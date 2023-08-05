# coding: utf-8

""" This module implements the session and settings class for the ApplicationMain. """

__author__ = "Andy Casey <andy@astrowizici.st>"

__all__ = ['Session']

# Standard libraries
import logging
import multiprocessing as mpi
import pickle
import shutil
import sys
import traceback

from functools import wraps
from commands import getstatusoutput
from time import time
from tempfile import mkdtemp
from itertools import product

# Third party
from scipy.io import readsav
from scipy.optimize import fmin_bfgs, leastsq, fmin, fmin_powell, fsolve
from scipy.interpolate import interp1d, griddata

# Module specific
import atmospheres
import moog
import nlte
import utils

from core import *
from profiles import measure_transition
from specutils import Spectrum, Spectrum1D, cross_correlate

logger = logging.getLogger(__name__)

class OptimizationSuccess(BaseException):
    pass

def _evaluate_stellar_parameter_permutation(i, permutation_twd, atmosphere_type, \
    equivalent_widths_filename, teff, vt, logg, feh, alpha_fe=0.4):
    """ Evaluate a stellar parameter permutation and return the parameters used
    to minimise during excitation and ionization equalibria """
    
    adjusted_abundances = {}
    for element, (abundance, uncertainty, meteroitic) in solar_abundances.iteritems():
        if element == "H": continue
        adjusted_abundances[element] = abundance + feh
    
    # Set up the atmospheric interpolator
    model_atmosphere_folder, model_atmosphere_parser = atmospheres.parsers[atmosphere_type]
    atmosphere_grid = atmospheres.AtmosphereInterpolator(model_atmosphere_folder, model_atmosphere_parser())

    # Interpolate to a model atmosphere
    moog_output_filename = os.path.join(permutation_twd, "moog.out")
    model_atmosphere_filename = os.path.join(permutation_twd, "stellar_atmosphere.model")

    try:
        atmosphere_grid.interpolate(model_atmosphere_filename,
            teff, logg, feh, alpha_fe, vt, solar_abundances=adjusted_abundances)

        abundances, moog_slopes = moog.abfind(moog_output_filename, equivalent_widths_filename,
            model_atmosphere_filename, twd=permutation_twd)
    except:
        etype, value, tb = sys.exc_info()
        logger.warn("Exception occurred in evaluating permutation function. Traceback (most recent call last):" +
            "\n{0}\n\t{1}: {2}".format("\n".join(traceback.format_tb(tb, 5)), etype, value))

        return (None, permutation_twd)

    # We will want to calculate our own slopes, since MOOG output precision is limited
    col_wl, col_transition, col_ep, col_loggf, col_ew, col_logrw, col_abund, col_del_avg = xrange(8)

    distributions, calculated_slopes = moog.calculate_trend_lines(abundances, 
        transition_col=col_transition, x_cols=(col_ep, col_logrw), y_col=col_abund)
   
    balance_transitions = sorted(np.unique(abundances[:, col_transition]))
    if len(balance_transitions) > 2:
        logger.warn("More than 2 unique transitions found in {0}. Taking {1} as balance transitions".format(
            equivalent_widths_filename, balance_transitions))

    idx_I = np.where(abundances[:, 1] == balance_transitions[0])
    idx_II = np.where(abundances[:, 1] == balance_transitions[1])

    permutation_results = [
        calculated_slopes[balance_transitions[0]][0][0],
        calculated_slopes[balance_transitions[0]][1][0],
        (0.1 * (np.mean(abundances[idx_I, col_abund]) - np.mean(abundances[idx_II, col_abund]))),
        (0.1 * (np.mean(abundances[idx_I, col_abund]) - (feh + solar_abundances["Fe"][0]))),
        ]

    full_result = [i] + [teff, vt, logg, feh] + permutation_results
    return (full_result, permutation_twd) 


def stellar_optimization(func):
    """ A decorator to wrap the stellar optimization function such
    that it finishes with the parameter tolerance we require and
    doesn't make unncessary (i.e., repeated) calls to MOOG """

    def _decorator(request, *args, **kwargs):

        previously_sampled_points, total_tolerance, individual_tolerances, outlier_rejection_total_tolerance, \
            outlier_limits, use_nlte_grid = args

        previously_sampled_points = np.array(previously_sampled_points)

        # Checking if this point is sampled already
        if len(previously_sampled_points) > 0:

            this_point = np.array(request)
            sampled_before = (previously_sampled_points[:, :4] == this_point).all(
                np.arange(previously_sampled_points[:, :4].ndim - this_point.ndim, previously_sampled_points[:, :4].ndim))

            if np.any(sampled_before):
                index = np.where(sampled_before)[0][0]
                logger.debug("Sampled these stellar parameters already, so we're just returning those values.")
                logger.debug(previously_sampled_points[index])

                return previously_sampled_points[index, 4:]

        # Perform the optimization
        response = func(request, *args, **kwargs)

        # Check for accepted tolerances, both total tolerance and individual tolerances if they are specified
        acquired_total_tolerance = np.sum(pow(response, 2))
        if total_tolerance >= acquired_total_tolerance and \
            (individual_tolerances is None or np.all(np.less_equal(np.abs(response), individual_tolerances))):

            message = "Optimization complete. Total tolerance of <{0:.1e} met: {1:.1e}".format(
                total_tolerance, acquired_total_tolerance)

            if individual_tolerances is not None:
                message += ", and individual tolerances of <[{0:.1e}, {1:.1e}, {2:.1e}, {3:.1e}] met: [{4:.1e}, {5:.1e}, {6:.1e}, {7:.1e}]".format(
                    *tuple(list(response) + list(individual_tolerances)))

            else:
                message += ", and no individual tolerances specified."

            raise OptimizationSuccess(message)


        return response
    return wraps(func)(_decorator)


class Session(HasTraits):
    """ A class to perform analysis of high-resolution stellar spectra """
    
    headers = Dict

    object_name = Str("No object")
    ra_repr = Str("None")
    dec_repr = Str("None")

    smh_version = Str("Unknown")

    correctly_handles_fwhm = Bool(True)
    
    # Normalisation tab
    normalisation_function = Enum('Spline', 'Polynomial')
    normalisation_order = Enum(range(1, 10))
    normalisation_max_iterations = Int(5)
    normalisation_sigma_low_clip = Float(5.0)
    normalisation_sigma_high_clip = Float(1.0)
    normalisation_knot_spacing = Float(20)

    normalisation_arguments = List(Dict)

    # Doppler Correction tab
    doppler_wlstart = Float
    doppler_wlend = Float
    doppler_template_filename = File
    
    v_rad = Float
    v_err = Float
    v_helio = Float
    v_tdr = Float
    v_correlation = Float
    v_apply_offset = Float
    v_applied_offset = Float(np.nan)
    
    # Equivalent width tab
    ew_local_continuum_fitting = Bool
    ew_detection_sigma = Float
    ew_continuum_order = Enum(*xrange(1, 5))
    ew_continuum_window = Float

    ew_initial_fwhm_guess = Float
    ew_max_fitting_iterations = Enum(*xrange(1, 10))
    ew_use_central_weighting = Bool
    ew_fitting_function = Enum("Gaussian", "Voigt", "Lorentzian")
    ew_initial_shape_guess = Float(0.)

    # [TODO] This should be renamed
    measurements = List(AtomicTransition)
    elemental_abundances = List(ElementalAbundance)

    # Stellar parameters tab
    stellar_teff = Int
    stellar_teff_uncertainty = Int
    stellar_phot_teff = Int
    stellar_logg = Float
    stellar_logg_uncertainty = Float
    stellar_vt = Float
    stellar_vt_uncertainty = Float
    stellar_alpha = Float
    stellar_feh = Float
    stellar_atmosphere_type = Enum(*atmospheres.parsers.keys())
    stellar_atmosphere_filename = Str
    stellar_reference_fe_h = Float(np.nan)
    stellar_feh_uncertainty = Float
    stellar_teff_text = Str

    model_atmosphere_folder = Str

    solar_abundances_filename = Str
    solar_abundances = Dict

    automatic_nlte_corrections = Dict
    
    initial_orders = List(Spectrum1D)
    continuum_orders = List(Spectrum1D)
    num_orders_per_filename = List(Int)

    normalised_spectrum = Instance(Spectrum1D)
    rest_spectrum = Instance(Spectrum1D)
    snr_spectrum = Instance(Spectrum1D)

    notes = Str

    def __init__(self, *args, **kwargs):
        HasTraits.__init__(self)

        self.add_trait("normalisation", Session.Normalisation(self))
        self.add_trait("doppler", Session.Doppler(self))

        # Add the synthesis setups as a list 
        self.add_trait("synthesis_setups", List(Session.Synthesis))

        # Load configuration
        configuration_dir = os.path.abspath(
            os.path.expanduser(os.path.join(os.path.dirname(__file__), "../config")))
        default_configuration = os.path.join(configuration_dir, "settings.json")
        local_configuration = os.path.join(configuration_dir, "local_settings.json")

        # Do we have a local copy of the default settings? If not, make one.
        if not os.path.exists(local_configuration):
            logger.info("Creating local copy of default configuration file ({0} to {1})"
                .format(default_configuration, local_configuration))
            shutil.copyfile(default_configuration, local_configuration)

        self.smh_version = utils.get_version()
        self.load_settings(local_configuration)

        # Should we load an existing session file? Or some spectra?
        if len(args) == 1 and args[0].endswith(".smh") and os.path.exists(args[0]):
            self.load(args[0])

        elif len(args) > 1:
            self.load_spectra(*args, **kwargs)


    def load_spectra(self, filenames, data_indices=None):
        """Loads un-normalised spectra into the current session file.

        Inputs
        ------

        filenames : list of strings
            The relative or absolute paths for spectrum filenames to load.

        data_indices : int
            The index to use to reference the data extension for each filename. This
            is only relevant for multi-extension FITS files. This should either be None,
            or have an explicit integer for every filename.
        """

        if data_indices is not None and len(filenames) != len(data_indices):
            raise TypeError("data indices should either be a list of integers the same length as the filenames provided, or None")

        spectra = []
        wl_start = []
        file_types = []
        path_information = []
        please_be_explicit = False
        all_carpy_files = True

        for i, path in enumerate(filenames):

            # dialog.paths
            try:
                spectrum = Spectrum1D.load(path)

            except:
                
                try:
                    spectrum = Spectrum.load_multispec(path)

                except:

                    logger.warn("Could not load the following file: '%s' -- is it a real spectrum?" % (path, ))
                    
                    if len(filenames) >= i + 1:
                        logger.info("Continuing to load other filenames...")

                    continue

            # Find out details about the filename
            a_fits_file = path.endswith('.fits')
            a_multi_fits_file = a_fits_file and len(spectrum.flux.shape) > 1
            extensions_required = a_fits_file and len(spectrum.flux.shape) > 2
            reduced_with_carpy = a_multi_fits_file and 1409561315 == hash(','.join([spectrum.headers[key] for key in spectrum.headers.keys() if key.startswith('BANDID')]))
            
            if extensions_required and not reduced_with_carpy \
            and data_indices is None:
                please_be_explicit = True

            # Human-readable file format
            data_index, snr_index = 'N/A', 'N/A'
            if not a_fits_file:
                file_type = 'ASCII'
            
            else:
                if a_multi_fits_file:
                    file_type = 'Multi-ext. FITS'
                    data_index = data_indices[i] if data_indices is not None else 0
                    if reduced_with_carpy:
                        file_type += ' (CarPy)'
                        data_index, snr_index = 1, 4

                else:
                    file_type = '1D FITS'

            # Store the information
            spectra.append(spectrum)
            file_types.append(file_type)

            path_information.append({
                'path'      : path,
                'file_type' : file_type,
                'data_index': str(data_index),
                'snr_index' : str(snr_index),
                'wl_range'  : (np.min(spectrum.disp), np.max(spectrum.disp)),
                })
            wl_start.append(np.min(spectrum.disp))
            if "CarPy" not in file_type: all_carpy_files = False

        if please_be_explicit:
            return (False, path_information)

        # Put a note in
        self.notes += "Initial filenames were:\n\t" + "\n\t".join([item['path'] for item in path_information]) + "\n\n"
        
        # Sort by starting wavelength
        sorted_index = np.argsort(wl_start)

        path_information_sorted = []
        spectra_sorted = []
        for index in sorted_index:
            spectra_sorted.append(spectra[index])
            path_information_sorted.append(path_information[index])

        del path_information, spectra
        spectra = spectra_sorted
        path_information = path_information_sorted

        # Update the session headers
        logger.info("Updating session headers with headers from the spectra from blue to red (reddest aperture will overwrite session headers)")

        updated_session_headers = {}
        updated_session_headers.update(self.headers)
        for spectrum in spectra:
            updated_session_headers.update(spectrum.headers)

        self.headers = updated_session_headers

        possible_object_keywords = ("OBJECT", "NAME")
        for possible_object_keyword in possible_object_keywords:
            if possible_object_keyword in self.headers:
                self.object_name = self.headers[possible_object_keyword]
                break
        else:
            self.object_name = "Unknown"

        if "RA" in self.headers:
            self.ra_repr = str(self.headers["RA"])

        if "DEC" in self.headers:
            self.dec_repr = str(self.headers["DEC"])

        initial_orders = []
        num_orders_per_filename = []
        for spectrum, information in zip(spectra, path_information):

            if not np.any(np.isfinite(spectrum.flux)) or np.all(spectrum.flux == 0): continue

            num_apertures = spectrum.disp.shape[0] if len(spectrum.disp.shape) > 1 else 1
            
            if num_apertures > 1:

                # Some multi-extension FITS files don't have multiple data formats
                if len(spectrum.flux.shape) > 2:
                    data_index = int(information['data_index'])

                    for i in xrange(num_apertures):
                        if not np.any(np.isfinite(spectrum.flux[data_index, i])) or np.all(spectrum.flux[data_index, i] == 0):
                            num_apertures -= 1
                            continue

                        initial_orders.append(Spectrum1D(disp=spectrum.disp[i], flux=spectrum.flux[data_index, i]))

                else:
                    # No extension required.
                    for i in xrange(num_apertures):
                        if not np.any(np.isfinite(spectrum.flux[i])) or np.all(spectrum.flux[i] == 0):
                            num_apertures -= 1
                            continue
                            
                        initial_orders.append(Spectrum1D(disp=spectrum.disp[i], flux=spectrum.flux[i]))

            else:
                initial_orders.append(spectrum)

            num_orders_per_filename.append(num_apertures)


        # Load into the session
        logger.info("Initial orders (%i): %s" % (len(initial_orders), initial_orders, ))
        logger.info("Re-setting continuum orders to []")
        logger.info("Orders per filename: %s" % (num_orders_per_filename, ))

        # Mr Sulu, take us to warp.
        # Engage.
        logger.info("Setting num orders and initial orders")
        self.num_orders_per_filename = num_orders_per_filename
        self.continuum_orders = []
        self.normalisation_arguments = []
        self.initial_orders = initial_orders

        # If all spectra were CarPy multi-extension FITS files, generate a snr spectrum
        if all_carpy_files and len(initial_orders) > 0:

            sample_rate, snr_data_index = 1, 3
            snr_spectra_to_stitch = []
            
            for spectrum in spectra:
                num_apertures = spectrum.disp.shape[0] if len(spectrum.disp.shape) > 1 else 1
                for i in xrange(num_apertures):
                    snr_spectrum = Spectrum1D(disp=spectrum.disp[i], flux=spectrum.flux[snr_data_index, i])
                    snr_spectra_to_stitch.append(snr_spectrum)

            wl_start, wl_end = snr_spectra_to_stitch[0].disp[0], snr_spectra_to_stitch[-1].disp[-1]

            wl_pixel_step = np.diff(snr_spectra_to_stitch[0].disp[:2])[0]
            wl_linear_step = wl_pixel_step / sample_rate
            linear_disp = np.arange(wl_start, wl_end + wl_linear_step, wl_linear_step)

            stacked_snr_flux = np.zeros(len(linear_disp))
            for i, aperture in enumerate(snr_spectra_to_stitch):
                is_finite = np.isfinite(aperture.flux)
                f_u = interp1d(aperture.disp[is_finite], aperture.flux[is_finite], bounds_error=False, fill_value=0.0)
                stacked_snr_flux += f_u(linear_disp)**2

            stacked_snr_flux = stacked_snr_flux**0.5

            # Divide stacked unnormalised spectra / stacked continuum function (on linear scale)
            self.snr_spectrum = Spectrum1D(disp=linear_disp, flux=stacked_snr_flux)

            

        return (True, path_information)


    def measure_equivalent_widths(self, species):
        """Measure equivalent widths for the species provided.

        Inputs
        ------

        species : list of floats, "all", or "acceptable"
            The species (as floats) to measure, or description of which atomic
            lines to measure.
        """

        atomic_transitions = []    
        if species == "all":
            atomic_transitions.extend(self.measurements)

        elif species == "acceptable":
            atomic_transitions.extend([measurement for measurement in self.measurements if measurement.is_acceptable])

        elif isinstance(species, (list, tuple, np.ndarray)):
            atomic_transitions.extend([measurement for measurement in self.measurements if measurement.transition in map(float, species)])

        else:
            try:
                species = float(species)
            except TypeError:
                raise TypeError("species provided to measure is not valid")
            else:
                species = [species]

            atomic_transitions.extend([measurement for measurement in self.measurements if measurement.transition in species])

        # Prepare arguments
        ew_arguments = {
            'local_continuum'       : self.ew_local_continuum_fitting,
            'detection_sigma'       : self.ew_detection_sigma,
            'order'                 : self.ew_continuum_order,
            'function'              : self.ew_fitting_function,
            'window'                : self.ew_continuum_window,
            'fwhm_guess'            : self.ew_initial_fwhm_guess,
            'max_iter'              : self.ew_max_fitting_iterations,
            'shape_guess'           : self.ew_initial_shape_guess,
            'use_central_weighting' : self.ew_use_central_weighting
        }

        aggregated_exclusion_ranges = []
        for transition in atomic_transitions:

            ew_measurement = measure_transition(self.rest_spectrum, transition.rest_wavelength, **ew_arguments)
                
            #p1 = [True/False, line_center, trough, fwhm, wl_start, wl_end, ew, chi_sq, ier, cont_x, cont_y, exclusion_regions]
            
            if ew_measurement[0]:

                transition.is_acceptable = True
                
                transition.measured_wavelength, transition.measured_trough, transition.measured_fwhm = ew_measurement[1:4]
                transition.measured_chi_sq, transition.measured_equivalent_width = ew_measurement[-5], ew_measurement[-6] * 1e3
                
                # Now we need the continuum information too
                transition.profile = np.vstack([ew_measurement[-3], ew_measurement[-2]])
                
                logger.info("Measured %s transition at %1.3f to have EW = %1.2f mA" \
                    % (transition.element, transition.rest_wavelength, transition.measured_equivalent_width, ))
                   
                exclusion_ranges = ew_measurement[-1]

                if exclusion_ranges is not None:
                    aggregated_exclusion_ranges.extend(exclusion_ranges)

                    ew_arguments['exclusion_ranges'] = aggregated_exclusion_ranges
                    ew_arguments['search_within_exclusion_ranges'] = False

            else:
                transition.is_acceptable = False
                transition.measured_wavelength, transition.measured_trough, transition.measured_fwhm, \
                    transition.measured_chi_sq, transition.measured_equivalent_width = [np.nan]*5

                logger.info("Failed to measure %s transition at %1.3f Angstroms: %s" \
                    % (transition.element, transition.rest_wavelength, ew_measurement[3], ))


    def _normalised_spectrum_changed(self, value):
        logger.info("Normalised spectrum updated. Ready for radial velocity measurement and correction.")

    def _rest_spectrum_changed(self, value):
        logger.info("Rest spectrum updated. Ready for equivalent width measurements.")
        
    def _stellar_reference_fe_h_changed(self, old_value, new_value):
        """ Updates the stellar reference [Fe/H] in all the elemental abundances
        in all of the synthesis setups """

        logger.info("The stellar reference log eps(Fe) (used for [X/Fe] calculations) has changed: log eps(Fe) = %1.2f" % (new_value, ))

        reference_fe_h_difference = new_value - old_value
        if not np.isfinite(reference_fe_h_difference): return

        logger.info("Synthesis has recognised the log eps(Fe) used for [X/Fe] calculations has changed by: %+1.2f" % (reference_fe_h_difference, ))

        for synthesis_setup in self.synthesis_setups:
            for element in synthesis_setup.elements_in_synthesis:
                element.X_on_Fe_minus_log_epsilon -= reference_fe_h_difference


    def summarise_abundances(self):

        unique_species = sorted(list(set([measurement.species for measurement in self.measurements])))

        elemental_abundances = []
        for species in unique_species:

            solar_abundance, solar_uncertainty, is_not_photospheric_abundance = solar_abundances[utils.species_to_element(species).split()[0]]

            # Get lines associated with this elemental abundance measurement            
            relevant_measurements = [measurement for measurement in self.measurements if measurement.species == species]

            elemental_abundance = ElementalAbundance(
                transition=species,
                solar_abundance=solar_abundance,
                solar_uncertainty=solar_uncertainty,
                stellar_reference_fe_h  = self.stellar_reference_fe_h,
                solar_fe_abundance      = solar_abundances["Fe"][0],
                line_measurements       = relevant_measurements)
            elemental_abundances.append(elemental_abundance)

        self.elemental_abundances = elemental_abundances

        return elemental_abundances


    def abundance_summary(self):
        """ Collates and returns an abundance summary for the current session,
        based on abundance measurements from equivalent widths and synthesis """

        if len(self.elemental_abundances) == 0:

            self.summarise_abundances()

        # Equivalent width measurements
        abundance_summary = {}
        for elemental_abundance in self.elemental_abundances:
            abundance_summary[elemental_abundance.transition] = (
                elemental_abundance.element,
                elemental_abundance.number_of_lines,
                elemental_abundance.solar_abundance,
                elemental_abundance.abundance_mean,
                elemental_abundance.nlte_abundance_mean,
                elemental_abundance.X_on_H,
                elemental_abundance.X_on_Fe,
                elemental_abundance.abundance_std,
                elemental_abundance.X_on_Fe_uncertainty
                )
            
        # Gather syntheses abundances
        synthesis_abundances = {}
        for synthesis_setup in self.synthesis_setups:
            if not synthesis_setup.is_acceptable or not np.isfinite(synthesis_setup.abundance): continue

            if synthesis_setup.element in synthesis_abundances:
                abundances, uncertainties = synthesis_abundances[synthesis_setup.element]
                abundances.append(synthesis_setup.abundance)
                uncertainties.append(synthesis_setup.uncertainty)

            else:
                abundances = [synthesis_setup.abundance]
                uncertainties = [synthesis_setup.uncertainty]

            synthesis_abundances[synthesis_setup.element] = (abundances, uncertainties)
            
        # Put the synthesis abundances into the abundance summary
        for element, setup in synthesis_abundances.iteritems():
            abundances, uncertainties = map(np.array, setup)

            number_of_lines = len(abundances)
            abundance_mean = np.mean(abundances)
            uncertainties[~np.isfinite(uncertainties)] = 0
            uncertainty = pow(np.sum(pow(uncertainties, 2)), 0.5)

            solar_abundance = solar_abundances[element][0]
            X_on_H = abundance_mean - solar_abundance
            X_on_Fe = X_on_H - (self.stellar_reference_fe_h - solar_abundances["Fe"][0])

            abundance_summary[utils.element_to_species(element) + 0.5] = (
                element + " (Syn.)",
                number_of_lines,
                solar_abundance,
                abundance_mean,
                np.nan, 
                X_on_H,
                X_on_Fe, 
                uncertainty,
                np.nan
                )

        sorted_abundance_keys = sorted(abundance_summary.keys())
        sorted_abundance_summary = []
        for key in sorted_abundance_keys:
            sorted_abundance_summary.append(abundance_summary[key])

        return sorted_abundance_summary


    def export_abundance_summary(self, filename, format="ascii", clobber=False):
        """ 
        Exports a summary of the elemental abundances for the current session.

        Parameters
        ----------

        filename : str
            The filename to save the abundance summary to.

        format : str, optional
            The format to save in: csv, ascii, tex

        clobber : bool
            Whether to clobber the file if it already exists.
        """

        if os.path.exists(filename) and not clobber:
            raise IOError("filename exists and we have been asked not to clobber it")

        format = format.lower()
        delimiters = {
            "csv": ",",
            "ascii": " \t",
            "tex": " & ",
        }
        nan_reprs = {
            "csv": "nan",
            "ascii": "nan",
            "tex": "\\nodata"
        }
        if format not in delimiters:
            raise ValueError("export format not recognised. Available inputs are: csv, tex, ascii")

        delimiter = delimiters[format]
        nan_repr = nan_reprs[format]

        sorted_abundance_summary = self.abundance_summary()

        formatted_lines = [["Element", "N", "Solar", "log(X)", "log(X_NLTE)", "[X/H]", "[X/Fe]", "[X/H]_err", "[X/Fe]_err"]]
        paddings = [map(len, formatted_lines[0])]
        for line in sorted_abundance_summary:

            element, number_of_lines, solar_abundance, abundance_mean, nlte_abundance_mean, X_on_H,\
                X_on_Fe, X_on_H_err, X_on_Fe_err = line

            formatted_line = [element, str(number_of_lines), "{:+.2f}".format(solar_abundance),
                "{:+.2f}".format(abundance_mean) if np.isfinite(abundance_mean) else nan_repr,
                "{:+.2f}".format(nlte_abundance_mean) if np.isfinite(nlte_abundance_mean) else nan_repr,
                "{:+.2f}".format(X_on_H) if np.isfinite(X_on_H) else nan_repr,
                "{:+.2f}".format(X_on_Fe) if np.isfinite(X_on_Fe) else nan_repr,
                "{:.2f}".format(X_on_H_err) if np.isfinite(X_on_H_err) and (number_of_lines > 1 or "(Syn.)" in element) else nan_repr,
                "{:.2f}".format(X_on_Fe_err) if np.isfinite(X_on_Fe_err) and (number_of_lines > 1 or "(Syn.)" in element) else nan_repr
                ]
            formatted_lines.append(formatted_line)

            paddings.append(map(len, formatted_line))

        summary_string = ""
        padded_lines = []
        paddings = np.max(np.array(paddings), axis=0)
        for formatted_line in formatted_lines:
            padded_line = [item.ljust(padding) for item, padding in zip(formatted_line, paddings)]
            summary_string += delimiter.join(padded_line) + ("\n" if format != "tex" else "  \\\\\n")

        logger.info("Abundances summary table:\n{0}".format(summary_string))

        with open(filename, "w") as fp:
            fp.write(summary_string)

        logger.info("Saved abundance summary table to {0}".format(filename))

        return summary_string



    def solve_stellar_parameters(self, initial_guess=None, max_attempts=5, total_tolerance=1e-4, 
        individual_tolerances=None, outlier_rejection_total_tolerance=None, outlier_limits=None,
        maxfev=30, use_nlte_grid=None):
        """
        Solves for the stellar parameters by performing excitation and ionization
        equilibria. Specifically, this function minimises four quantities by varying
        the effective temperature, microturbulence, surface gravity, and overall
        metallicity:

            - Slope of excitation potential and abundance for acceptable Fe I lines,
              known as d_A/d_chi

            - Slope of reduced equivalent width and abundance for acceptable Fe I lines,
              known as d_A/d_REW

            - The difference between the mean Fe I and Fe II abundances,
              known as delta_Fe

            - The difference between the mean Fe I abundance and overall metallicity,
              known as delta_M

        These quantities are minimised by a multi-variate Newton-Raphson conjugate-
        gradient algorithm with the Jacobian approximated from partial derivatives 
        measured in the Sun. An additional level of control decorates the optimization
        function such that (1) it will not re-sample previously sampled points, (2) will
        raise an exception when the precision of step sizes has reached negligible levels
        (even if the function tolerance and (3) will restart the optimization from a
        random point chosen uniformly distributed throughout the parameter space).

        Parameters
        ----------
        initial_guess : list of float objects, optional
            The initial temperature, microturbulence, surface gravity, metallicity to
            start solving from. If None is provided, these points will be randomly
            generated.

        max_attempts : int, optional
            The maximum number of times to re-try the optimization algorithm before
            giving up on a solution.

        total_tolerance : float, optional
            The maximum acceptable tolerance. The tolerance is calculated as the sum of
            the scaled squares of our parameters of interest:

            total_tolerance = (d_A/d_chi)^2 + (d_A/d_REW)^2 + (0.1 * delta_Fe)^2 +
                                + (0.1 * delta_M)^2

        individual_tolerances : list of four positive floats or None, optional
            The maximum absolute tolerance for each of the minimised parameters. If
            None is provided, then only the `total_tolerance` criterion will be
            used to evaluate convergence.

        outlier_rejection_total_tolerance : positive float or None, optional
            The tolerance required before performing a single rejection of outlier
            points. If None is provided, then no outliers will be removed. Outlier
            rejection occurs only the first time the `outlier_rejection_total_tolerance`
            is reached, and uses limits from `outlier_limits`.

        outlier_limits : dict or None, optional
            A dictionary with species (keys) and sigma values (values) that qualify
            for outlier rejection. Outlier rejection occurs *once*, *only* if the
            `outlier_rejection_total_tolerance` has been set. Once the tolerance
            specified in `outlier_rejection_total_tolerance` has been reached, any
            species (keys) provided to `outlier_limits` will be rejected if their
            abundance is outside of the sigma limit provided as a value.

        use_nlte_grid : str, optional
            A filename of pre-computed non-LTE corrections to use for the balance transitions.
            If `use_nlte_grid` is not None then non-LTE abundances will be used for
            performing excitation and ionization equalibria.

        Notes
        -----
        delta_Fe and delta_M are scaled by 0.10 in the calculation of total_tolerance as acceptable
        stellar parameters are generally found when |d_A/d_chi| ~ 0.001 dex/eV,
        |d_A/d_REW| ~ 0.001, |delta_Fe| ~ 0.01 dex, |delta_M| ~ 0.01 dex. Hence, delta_M
        and delta_Fe are scaled to be of order the same importance as d_A/d_chi and
        d_A/d_REW.
        """

        if not isinstance(max_attempts, int):
            raise TypeError("maximum number of attempts must be a positive integer-like type")

        if max_attempts < 1:
            raise ValueError("maximum number of attempts must be a positive integer")

        if total_tolerance < 0:
            raise ValueError("tolerance must be a positive value")

        if individual_tolerances is not None:
            if np.any(individual_tolerances < 0):
                raise ValueError("individual tolerances must either be a list of positive floats"+
                    " of length four, or None")

        if outlier_rejection_total_tolerance is not None:
            if outlier_rejection_total_tolerance < 0:
                raise ValueError("total tolerance for outlier rejection must be a positive float")

            if outlier_limits is None or len(outlier_limits) == 0:
                logger.warn("an outlier rejection limit was provided but no sigma limits were provided")

            for species, sigma_limit in outlier_limits.iteritems():
                if not isinstance(species, (float, int)):
                    raise ValueError("keys for outlier limits must be given as float-like species")

                if not isinstance(sigma_limit, (float, int)) or sigma_limit < 0:
                    raise ValueError("values for outlier limits must be given as positive float-like values")

        # TODO
        parameter_ranges = {
            "teff": (4000, 7000),
            "logg": (0, 5),
            "vt": (0.5, 2.5),
            "[Fe/H]": (-3, 0.5)
        }
        if initial_guess is None:
            initial_guess = [np.random.uniform(*parameter_ranges[parameter]) for parameter in ["teff", "vt", "logg", "[Fe/H]"]]

        # Create a temporary working directory if we don't have one already
        self.twd = self.twd if hasattr(self, 'twd') else mkdtemp()
        if isinstance(self.twd, (list, tuple)): self.twd = self.twd[1]
        
        # Create filenames (save the stellar atmosphere one)
        self.stellar_atmosphere_filename = os.path.join(self.twd, 'stellar_atmosphere.model')
        equivalent_widths_filename = os.path.join(self.twd, 'balance_ew.list')
        moog_output_prefix = os.path.join(self.twd, 'moog.out')

        # Set up the atmospheric interpolator
        model_atmosphere_folder, model_atmosphere_parser = atmospheres.parsers[self.stellar_atmosphere_type]
        atmosphere_grid = atmospheres.AtmosphereInterpolator(model_atmosphere_folder, model_atmosphere_parser())
        logger.info("Using {0} atmospheres: {1} located in {2}".format(
            self.stellar_atmosphere_type, model_atmosphere_parser, model_atmosphere_folder))
        logger.info("Leaving [alpha/Fe] = {0:.2f} during optimisation".format(self.stellar_alpha))

        # Create a mutable copy for the initial guess
        solver_guess = []
        solver_guess.extend(initial_guess)

        # We will want to calculate our own slopes, since MOOG output precision is limited
        col_wl, col_transition, col_ep, col_loggf, col_ew, col_logrw, col_lte_abund, col_del_avg, col_nlte_abund = xrange(9)
            
        # Pre-load the non-LTE grid
        if use_nlte_grid is not None:
            use_nlte_grid = readsav(use_nlte_grid)

        @stellar_optimization
        def minimisation_function(stellar_parameters, *args):
            """ The function we want to minimise (e.g., calculates the quadrature
                sum of all minimizable variables.)

                stellar_parameters : [teff, vt, logg, feh]

            """

            teff, vt, logg, feh = stellar_parameters
            all_sampled_points, total_tolerance, individual_tolerances, outlier_rejection_total_tolerance, \
                outlier_limits, use_nlte_grid = args

            # Skip over unphysical results
            if not (5 > vt > 0):
                return np.array([np.nan, np.nan, np.nan, np.nan])

            # We need to scale the abundance differences from MOOG's internal default solar
            # composition by Anders & Grevesse et al (1989), to the Asplund et al. (2009)
            # solar composition.

            adjusted_abundances = {}
            for element, (abundance, uncertainty, meteroitic) in solar_abundances.iteritems():
                if element == "H": continue
                adjusted_abundances[element] = abundance + self.stellar_feh

            # Write the equivalent widths to file
            balance_transitions = [measurement for measurement in self.measurements if measurement.transition in self.balance_transitions \
                and measurement.is_acceptable and measurement.measured_equivalent_width > 0]
            if "OUTLIER_INDICES" in outlier_limits:

                balance_transitions_to_measure = []
                for i, item in enumerate(balance_transitions):
                    if i not in outlier_limits["OUTLIER_INDICES"]:
                        balance_transitions_to_measure.append(item)

            else:
                balance_transitions_to_measure = balance_transitions

            moog.io.write_equivalent_widths(balance_transitions_to_measure, equivalent_widths_filename, clobber=True)
            
            try:
                # Interpolate to a model atmosphere
                atmosphere_grid.interpolate(self.stellar_atmosphere_filename, teff, logg, feh, self.stellar_alpha, vt,
                    solar_abundances=adjusted_abundances, clobber=True)

                # Run MOOG abfind routine
                abundances, moog_slopes = moog.abfind(moog_output_prefix, equivalent_widths_filename,
                    self.stellar_atmosphere_filename, twd=self.twd)


            except:
                etype, value, tb = sys.exc_info()
                logger.warn("Exception occurred in minimisation function. Traceback (most recent call last):\n{0}\n\t{1}: {2}".format( 
                    "\n".join(traceback.format_tb(tb, 5)), etype, value))
                all_sampled_points.append([teff, vt, logg, feh, np.nan, np.nan, np.nan, np.nan])
                return np.array([np.nan, np.nan, np.nan, np.nan])


            # Calculate non-LTE abundances if necessary
            if use_nlte_grid is not None:

                # Add column to array
                abundances = np.hstack((abundances, np.array([np.nan]*len(abundances)).reshape((len(abundances),1))))

                for i, abundance in enumerate(abundances):
                    if np.isfinite(abundance[col_lte_abund]):

                        try:
                            lte_abundance, nlte_abundance, correction = nlte.get_nlte_correction(use_nlte_grid,
                                abundance[col_wl], abundance[col_ew], teff, logg, feh, vt,
                                solar_fe_abundance=solar_abundances["Fe"][0])

                        except (ValueError, IndexError) as e:
                            logger.debug("non-LTE correction for {0:.1f} at {1:.1f} failed: {2}".format(
                                abundance[col_transition], abundance[col_wl], e.args[0]))

                        else:
                            logger.debug("non-LTE correction for {0:.1f} at {1:.1f} is {2:+.3f} dex (LTE: {3:+.3f}, n-LTE: {4:+.3f})".format(
                                abundance[col_transition], abundance[col_wl], correction, lte_abundance, nlte_abundance))

                            # Apply the correction to the measurement
                            abundances[i, col_nlte_abund] = abundance[col_lte_abund] + correction

                if np.all(~np.isfinite(abundances[:, col_nlte_abund])):
                    logger.info("Performing excitation and ionization equalibria with LTE abundance because non-LTE abundances were all invalid")
                    col_abund = col_lte_abund

                else:
                    logger.info("Performing excitation and ionization equalibria with non-LTE abundances")
                    col_abund = col_nlte_abund

            else:
                logger.info("Performing excitation and ionization equalibria with LTE abundances")
                col_abund = col_lte_abund

            
            finite_abundances = np.isfinite(abundances[:, col_abund])
            abundances = abundances[finite_abundances]

            # Update abundances with proper values of reduced equivalent widths
            abundances[:, col_logrw] = [item.reduced_equivalent_width for item in balance_transitions_to_measure]
            #print("A", [item.reduced_equivalent_width for item in balance_transitions_to_measure])
            distributions, calculated_slopes = moog.calculate_trend_lines(
                abundances,
                transition_col=col_transition,
                x_cols=(col_ep, col_logrw),
                y_col=col_abund)


            idx_I = np.where(abundances[:, col_transition] == self.balance_transitions[0])
            idx_II = np.where(abundances[:, col_transition] == self.balance_transitions[1])
            results = np.array([
                calculated_slopes[self.balance_transitions[0]][0][0],
                calculated_slopes[self.balance_transitions[0]][1][0],
                (0.1 * (np.mean(abundances[idx_I, col_abund]) - np.mean(abundances[idx_II, col_abund]))),
                (0.1 * (np.mean(abundances[idx_I, col_abund]) - (feh + solar_abundances['Fe'][0]))),
                ])

            # Have we reached the required tolerance to reject outliers? And have we not rejected any outliers yet?
            acquired_total_tolerance = np.sum(results**2)
            if outlier_rejection_total_tolerance >= acquired_total_tolerance and len(outlier_limits) > 0 \
                and "OUTLIER_INDICES" not in outlier_limits.keys():
            
                logger.info("Performing outlier rejection: {0}".format(outlier_limits))

                outlier_indices = []
                # We should remove outliers, then clear outlier_limits
                for species in outlier_limits.keys():

                    outlier_limit = outlier_limits[species]
                    species_indices = np.where(abundances[:, col_transition] == species)[0]

                    # Any abundances to work with?
                    if len(species_indices) == 0:
                        del outlier_limits[species]
                        continue 

                    species_abundances = abundances[species_indices, col_abund]
                    abundance_mean = np.mean(species_abundances)
                    abundance_std = np.std(species_abundances)

                    # Any outliers?
                    are_outliers = (abundances[:, col_transition] == species) & (np.abs(abundances[:, col_abund] - abundance_mean)/abundance_std >= outlier_limit)
                    if np.any(are_outliers):
                        wavelengths = abundances[are_outliers, col_wl]
                        logger.info("Identified {0:.0f} outliers of species {1:.1f} with (|sigma| > {2:.1f}) -- wavelengths: {3}".format(
                            np.sum(are_outliers), species, outlier_limit, wavelengths))
                
                        outlier_indices.extend(np.where(are_outliers)[0])
                        del outlier_limits[species]

                outlier_limits["OUTLIER_INDICES"] = np.array(outlier_indices)
                logger.info("There were {0:d} outliers that were removed in total.".format(len(outlier_indices)))


            point = [teff, vt, logg, feh] + list(results)
            all_sampled_points.append(point)

            logger.info("Atmosphere with Teff = {0:.0f} K, vt = {1:.2f} km/s, logg = {2:.2f}, [Fe/H] = {3:.2f}, [alpha/Fe] = {4:.2f}"
                " yields sum {5:.1e}:\n\t\t\t[{6:.1e}, {7:.1e}, {8:.1e}, {9:.1e}]".format(teff, vt, logg, feh, self.stellar_alpha,
                acquired_total_tolerance, *results))

            return results



        all_sampled_points = []

        outlier_limits_copy = {}
        if outlier_limits is not None:
            outlier_limits_copy.update(outlier_limits)

        # Solve
        ta = time()
        for i in xrange(1, 1 + max_attempts):
        
            sampled_points = []
            args = (sampled_points, total_tolerance, individual_tolerances, outlier_rejection_total_tolerance, outlier_limits_copy,
                use_nlte_grid)

            try:
                results = fsolve(minimisation_function, solver_guess, args=args, fprime=utils.approximate_stellar_jacobian,
                    col_deriv=1, epsfcn=0, xtol=1e-10, full_output=1, maxfev=maxfev)

            except:# OptimizationSuccess as e:
                # Optimization is complete and tolerances have been reached

                os.system('cp "{0}" /Users/andycasey/goo.model'.format(self.stellar_atmosphere_filename))
                print("COPIED TO GOO")
        

                t_elapsed = time() - ta
                logger.info("Successful after {0:.0f} seconds".format(t_elapsed))
                
                point_results = np.sum(np.array(sampled_points)[:, 4:]**2, axis=1)
                min_index = np.argmin(point_results)

                final_parameters = sampled_points[min_index][:4]
                final_parameters[0] = int(np.round(final_parameters[0])) # Effective temperature
                final_parameters_result = sampled_points[min_index][4:]
                num_moog_iterations = len(sampled_points)
                all_sampled_points.extend(sampled_points)

                acquired_total_tolerance = sum(pow(np.array(final_parameters_result), 2))

                outlier_indices = outlier_limits_copy["OUTLIER_INDICES"] if "OUTLIER_INDICES" in outlier_limits_copy else []
                return (True, initial_guess, num_moog_iterations, i, t_elapsed, final_parameters, final_parameters_result, np.array(all_sampled_points), outlier_indices)

                
            else:
                # The optimizer stopped on its own
                # accord
                t_elapsed = time() - ta
                logger.info("Optimizer has finished with: {0}".format(results[0]))
                ier, mesg = results[-2:]
                if ier != 1:
                    logger.info("Optimizer has returned with the message: {0}".format(mesg))

                # Do we have the requisite tolerance?
                final_parameters = results[0]
                final_parameters[0] = int(np.round(final_parameters[0])) # Effective temperature
                final_parameters_result = results[1]["fvec"]
                num_moog_iterations = len(sampled_points)
                all_sampled_points.extend(sampled_points)
                
                acquired_total_tolerance = sum(pow(np.array(final_parameters_result), 2))

                # Have we achieved tolerance?
                if total_tolerance >= acquired_total_tolerance and \
                    (individual_tolerances is None or np.all(np.less_equal(np.abs(final_parameters_result), individual_tolerances))):

                    outlier_indices = outlier_limits_copy["OUTLIER_INDICES"] if "OUTLIER_INDICES" in outlier_limits_copy else []
                    return (True, initial_guess, num_moog_iterations, i, t_elapsed, final_parameters, final_parameters_result, np.array(all_sampled_points), outlier_indices)

                else:

                    # This solution will fail. Try a new starting point
                    solver_guess = [np.random.uniform(*parameter_ranges[parameter]) for parameter in ["teff", "vt", "logg", "[Fe/H]"]]
                    
        t_elapsed = time() - ta
        logger.info("Took {0} minutes to finish.".format(t_elapsed/60.))

        # Have we achieved tolerance?
        if total_tolerance >= acquired_total_tolerance and \
            (individual_tolerances is None or np.all(np.less_equal(np.abs(final_parameters_result), individual_tolerances))):
            tolerance_achieved = True
            
        else:
            tolerance_achieved = False

        outlier_indices = outlier_limits_copy["OUTLIER_INDICES"] if "OUTLIER_INDICES" in outlier_limits_copy else []
        return (tolerance_achieved, initial_guess, num_moog_iterations, i, t_elapsed, final_parameters, final_parameters_result, np.array(all_sampled_points), outlier_indices)


    def _automatic_nlte_corrections_changed(self, value):
        """ Triggers an update of automatic non-LTE corrections """
        self.apply_automatic_nlte_corrections()


    def apply_automatic_nlte_corrections(self):
        """Applies any non-LTE corrections that we've been told to calculate automatically."""

        logger.info("Applying any automatic non-LTE corrections to session..")

        for element, grid_filename in self.automatic_nlte_corrections.iteritems():
            logger.info("Applying non-LTE corrections for {0} with grid in {1}".format(
                element, grid_filename))

            # Turn element into species
            species = int(utils.element_to_species(element))
            species = [species, species + 0.1]

            self.apply_nlte_corrections(grid_filename, species)

        return True


    def apply_nlte_corrections(self, grid_filename, species):
        """Calculates non-LTE corrections for a set of measured species
        from a grid of pre-computed non-LTE corrections.

        Parameters
        ----------

        grid_filename : str
            Filename of grid of pre-computed non-LTE corrections.

        species : list of floats
            List of species to compute corrections for.
        """

        grid = readsav(grid_filename)

        for measurement in self.measurements:
            if measurement.transition in species and measurement.is_acceptable \
            and measurement.measured_equivalent_width > 0 and np.isfinite(measurement.abundance):

                try:
                    lte_abundance, nlte_abundance, correction = nlte.get_nlte_correction(grid,
                        measurement.rest_wavelength, measurement.measured_equivalent_width,
                        self.stellar_teff, self.stellar_logg, self.stellar_feh, self.stellar_vt,
                        solar_fe_abundance=solar_abundances["Fe"][0])

                except (IndexError, ValueError) as e:
                    logger.debug("non-LTE correction for {0:5s} at {1:.1f} failed: {2}".format(
                        measurement.element, measurement.rest_wavelength, e.args[0]))

                else:
                    logger.debug("non-LTE correction for {0:5s} at {1:.1f} is {2:+.3f} dex (LTE: {3:+.3f}, n-LTE: {4:+.3f})".format(
                        measurement.element, measurement.rest_wavelength, correction, lte_abundance, nlte_abundance))

                    # Apply the correction to the measurement
                    measurement.nlte_abundance = measurement.abundance + correction

        return True


    def sample_stellar_parameters(self, threads=1):
        """ Sample all possible stellar parameters so that the Jacobian
        can be approximated for the current session. """

        # Create permutations
        alpha_fe = 0.4
        teffs = np.arange(4000, 8250, 250)
        vts = np.linspace(0.5, 3.5, 10)
        loggs = np.arange(0, 5 + 0.5, 0.5)
        fehs = np.arange(-3, 0.5 + 0.5, 0.5)
        
        permutations = product(*[teffs, vts, loggs, fehs])

        # Create a temporary working directory if we don't have one already
        twd = self.twd if hasattr(self, 'twd') else mkdtemp()
        if isinstance(twd, (list, tuple)): twd = twd[1]
        
        # Save to session
        self.twd = twd

        # Write equivalent widths to disk, as these won't change for each permutation
        equivalent_widths_filename = os.path.join(twd, "balance_ew.list")
        moog.io.write_equivalent_widths(
            [measurement for measurement in self.measurements if measurement.transition in self.balance_transitions \
                and measurement.is_acceptable and measurement.measured_equivalent_width > 0],
            equivalent_widths_filename, clobber=True)
        
        pool = mpi.Pool(threads)
        num_permutations = len(teffs)*len(loggs)*len(fehs)*len(vts)
        results_grid = np.zeros((num_permutations, 8))
        results_grid[:] = np.nan


        def permutation_callback(*args):
            """ Record the results from each permutation """
            result, permutation_twd = args[0]
            
            if result is not None:
                results_grid[result[0], :] = result[1:]
            shutil.rmtree(permutation_twd)


        for i, (teff, vt, logg, feh) in enumerate(permutations):
            results_grid[i, :4] = [teff, vt, logg, feh]
            
            permutation_twd = mkdtemp()
            args = (i, permutation_twd, self.stellar_atmosphere_type, equivalent_widths_filename, teff, vt, logg, feh)
            pool.apply_async(_evaluate_stellar_parameter_permutation, args=args, callback=permutation_callback)

        pool.close()
        pool.join()

        np.savetxt("sampled_stellar_parameters.data", results_grid)

        return results_grid


    def _solar_abundances_filename_changed(self, filename):
        """Loads in the solar abundances."""

        with open(filename, "r") as fp:
            solar_abundances = json.load(fp)

        self.solar_abundances = solar_abundances



    def _snr_spectrum_changed_(self, snr_spectrum):
        """ Calculates a minimum detectable equivalent width from the spectrum SNR
        and assigns that minimum detectable equivalent width to all the measurements
        in the session.

        Parameters
        ----------
        snr_spectrum : `specutils.Spectrum1D`
            A signal-to-noise spectrum.
        """

        logger.debug("Session.snr_spectrum = %s" % (snr_spectrum, ))

        num_updated = 0
        for measurement in self.measurements:
            if measurement.rest_wavelength < snr_spectrum.disp[0] \
            or measurement.rest_wavelength > snr_spectrum.disp[-1]:
                continue

            idx = np.searchsorted(snr_spectrum.disp, measurement.rest_wavelength)

            num_pixels = 8
            pixel_width = np.diff(snr_spectrum.disp)[idx]
            
            measurement.minimum_detectable_ew = (pixel_width * (num_pixels**0.5) / snr_spectrum.flux[idx]) * 1e3
            num_updated += 1

        logger.debug("Number of measurements updated with minimum detectable equivalent widths: %i" % (num_updated, ))


    def _twd_changed(self, twd):
        """ Logs the location of the temporary working directory """
        
        logger.info("Temporary working directory is located at:  %s" % (twd, ))
        

    def clean_up(self):
        """Cleans up the TWD if it exists."""

        if hasattr(self, 'twd'):
            logger.debug("Attempting to remove TWD at %s" % (self.twd, ))

            if os.path.exists(self.twd):
                shutil.rmtree(self.twd)

                logger.info("Temporary working directory removed.")
                return True

            else:
                logger.warn("Could not remove temporary working directory at '%s' -- has it been removed outside of SMH? Closing anyways.." % (self.twd, ))
                return False


    def extend_line_list(self, filename):
        """ Extend the existing line list with a new line list filename """

        additional_transition_data = np.loadtxt(filename)

        additional_transitions = []
        for transition in additional_transition_data:
            rest_wavelength, transition, excitation_potential, oscillator_strength = transition
            measurement = AtomicTransition(
                rest_wavelength     = rest_wavelength,
                transition          = transition,
                excitation_potential= excitation_potential,
                oscillator_strength = oscillator_strength)

            additional_transitions.append(measurement)

        all_transitions = []
        all_transitions.extend(info.object.session.measurements)
        all_transitions.extend(additional_transitions)

        self.measurements = all_transitions


    def load_line_list(self, filename):
        """ Loads in a line list.
        
        Parameters
        ----------
        filename : str
            Path to the line list filename.
            
        Returns
        ----
        result : bool
            Whether or not the line list was successfully loaded.
            
        Raises
        ----
        IOError
            If the `filename` provided cannot be found.
            
        Notes
        ----
            The status-quo (as set by MOOG) is to have the first line of the
            list be a "comment line". If the first line looks like any other,
            then the list will be loaded with the first line included. 

            If the first line of the file looks like a comment, it will be
            ignored. The `filename` provided is expected to be an ASCII
            formatted file with the following whitespace-separated columns (e.g.
             either tabs or spaces):
             
            Wavelength, Transition, Excitation Potential, Oscillator Strength,
            Van der Waals broadening constant
            
            Anything interpreted after the Van der Waals broadening constant is
            assumed to be a comment and is stored in `EquivalentWidths.comment`
            attribute.
        """
        
        if len(filename) is 0: return False
        
        if not os.path.exists(filename):
            raise IOError("Cannot load line list '%s', the path does not exist." \
                          % (filename, ))
        
        # We cannot use np.loadtxt because some lines may have Van der Waals
        # broadening and/or comments
        
        num_added = 0
        loaded_measurements = []
        
        with open(filename, 'r') as fp:
            
            lines = fp.readlines()
            
            for i, line in enumerate(lines):
                
                line = line.split()
                
                # Skip the first line in keeping with status quo
                try:
                    wavelength, transition, lep, loggf = map(float, line[:4])

                except:
                    if i == 0: continue

                    else:
                        raise ValueError("Improper line in line list at line #%i." \
                            % (i + 1, ))


                vdw, comment = None, None
                if len(line) > 4:
                    # Van der Waals broadening?
                    try:
                        vdw = float(line[4])
                        
                    except TypeError as e:
                        # No; must be a comment
                        comment = ' '.join(line[4:])
                    
                    else:
                        if len(line) > 5:
                            comment = ' '.join(line[5:])
                            
                kwargs = {
                    'rest_wavelength': wavelength,
                    'transition': transition,
                    'excitation_potential': lep,
                    'oscillator_strength': loggf,
                    'vanderwaal_broadening': vdw,
                    'comment': comment
                }
                
                if comment is None: del kwargs['comment']
                if vdw is None: del kwargs['vanderwaal_broadening']
                
                loaded_measurements.append(AtomicTransition(**kwargs))
                
                num_added += 1
        
        # Update the actual session
        self.measurements = loaded_measurements

    
   

    @on_trait_change('v_applied_offset,normalised_spectrum')
    def _place_normalised_spectrum_at_rest(self):
        """Places the normalised spectrum at rest"""

        if hasattr(self, 'v_applied_offset') and hasattr(self, 'normalised_spectrum') \
        and self.v_applied_offset is not None and self.normalised_spectrum is not None \
        and np.isfinite(self.v_applied_offset):
            self.rest_spectrum = self.normalised_spectrum.doppler_correct(self.v_applied_offset)


    def save_as(self, output_filename, clobber=True):
        """ Saves the `ApplicationMain` session to the `output_filename` provided.
        
        Parameters
        ----------
        output_filename : str
            The filename to save the session to.
          
        clobber : bool, optional
            Whether to overwrite the file if the `output_filename` already exists.
          
        Raises
        ------
        IOError
            If the `filename` already exists and `clobber` is not True.     
        """

        # Force output_filename to be a .smh file
        if not output_filename.endswith('.smh'):
            logger.debug("Forcing save filename to have .smh extension.")
            output_filename += '.smh'

        
        if os.path.exists(output_filename) and not clobber:
            raise IOError("Cannot write to disk. Filename '%s' already exists and we've been told not to clobber it." \
                          % (output_filename, ))
        
        # First let's create a temporary directory where all the files will be
        # saved to
        saved_session = self.__dict__.copy()
        twd = self.twd if saved_session.has_key('twd') else mkdtemp()
        assert os.path.exists(twd)

        ignore_keys = ('twd', 'save_as', 'load', 'automatic_nlte_corrections', 'load_settings', 'shifted_telluric_spectrum', 'normalisation', 'doppler', 'Doppler', "Synthesis", 'synthesis', 'Normalisation')
        for key in saved_session.keys():
            if key in ignore_keys or key.startswith('_'):
                del saved_session[key]

        logger.debug("Session dump:")
        logger.debug(saved_session)
        
        if (not saved_session.has_key('initial_orders') or len(saved_session['initial_orders']) == 0) \
        and (not saved_session.has_key('continuum_orders') or len(saved_session['continuum_orders']) == 0):
            logger.warn("There's no initial orders to save: have you done anything worth saving?")

        # Save initial spectra
        if saved_session.has_key('initial_orders'):

            for i, order in enumerate(saved_session['initial_orders']):
                order.save(os.path.join(twd, 'initial_order_%i.fits' % (i, )))

            # Remove this key from the saved session since we will just package the saved fits files
            # into the session tarball
            del saved_session['initial_orders']


        # Save continuum spectra
        if saved_session.has_key('continuum_orders'):
            for i, order in enumerate(saved_session['continuum_orders']):
                order.save(os.path.join(twd, 'continuum_order_%i.fits' % (i, )))

            # Remove this key from the saved session since we will just package the saved fits files
            # into the session tarball
            del saved_session['continuum_orders']


        # Save other relevant spectra
        spectrum_keywords = ('normalised_spectrum', 'telluric_spectrum', 'snr_spectrum')
        for spectrum_keyword in spectrum_keywords:
            
            if saved_session.has_key(spectrum_keyword) and saved_session[spectrum_keyword] is not None:
                saved_session[spectrum_keyword].save(os.path.join(twd, spectrum_keyword + '.fits'))
            
                # Remove this key from the saved session since we will just package the saved fits files
                # into the session tarball
                del saved_session[spectrum_keyword]
        

        # Save other relevant files
        filename_keywords = ('solar_abundances_filename', 'stellar_atmosphere_filename')

        for filename_keyword in filename_keywords:
            if filename_keyword not in saved_session: continue

            filename_to_save = saved_session[filename_keyword]
            if not os.path.exists(filename_to_save): 
                logger.warn("Expected filename '%s' (the %s) to save to session, but the file does not exist! This session file may be incomplete or corrupted." \
                    % (filename_to_save, filename_keyword.replace('_', ' '), ))

                continue
            
            twd_filename = os.path.join(twd, os.path.basename(filename_to_save))
            
            if filename_to_save != twd_filename:
                logger.debug("Copying '%s' to '%s'" % (filename_to_save, twd_filename, ))
                try:
                    shutil.copyfile(filename_to_save, twd_filename)

                except shutil.Error as reason:
                    logger.warn("Error when copying file '%s' to '%s': %s" % (filename_to_save, twd_filename, reason, ))

            # Update session key to only use the base name, which will be relative to
            # the temporary working directory
            saved_session[filename_keyword] = os.path.basename(filename_to_save)
        

        # Measurements
        json_ready_measurements = []
        for measurement in saved_session['measurements']:

            dictionary = measurement.__dict__.copy()
            
            # Remove listeners
            for key in dictionary.keys():
                if key.startswith('_'): del dictionary[key]

            if dictionary.has_key('profile'):
                dictionary['profile'] = dictionary['profile'].tolist()
            
            json_ready_measurements.append(dictionary)
        
        # JSON-ify the measurements
        if saved_session.has_key('measurements'):
            saved_session['measurements'] = json_ready_measurements

        # ElementalAbundances are created on-the-fly when the session is loaded.
        # Same with rest_spectrum
        on_the_fly_keys = ('rest_spectrum', 'elemental_abundances')
        for key in on_the_fly_keys:
            if key in saved_session.keys():
                del saved_session[key]
        
        # Synthesis setups
        json_ready_synthesis_setups = []
        if 'synthesis_setups' in saved_session:
            
            for i, synthesis_setup in enumerate(saved_session['synthesis_setups']):

                synthesis_setup = synthesis_setup.__dict__.copy()
                logger.debug("Getting ready to save: %s" % (synthesis_setup, ))

                # Line list
                if not os.path.exists(synthesis_setup['line_list_filename']):
                    logger.warn("Line list '%s' does not exist!" % (synthesis_setup['line_list_filename'], ))

                else:
                    current_line_list_filename = synthesis_setup['line_list_filename']
                    new_line_list_filename = os.path.join(twd, os.path.basename(current_line_list_filename))

                    if current_line_list_filename != new_line_list_filename:
                        # Copy the file to the new line list filename
                        logger.debug("Copying %s to %s" % (current_line_list_filename, new_line_list_filename, ))
                        try:
                            shutil.copyfile(current_line_list_filename, new_line_list_filename)

                        except shutil.Error as reason:
                            logger.warn("Error when copying file '%s' to '%s': %s" % (current_line_list_filename, new_line_list_filename, reason, ))
        
                    # Update the session name to use only the basename, because it will be within the TWD
                    synthesis_setup['line_list_filename'] = os.path.basename(current_line_list_filename)

                # Elements in synthesis
                if 'elements_in_synthesis' in synthesis_setup:

                    elements_in_synthesis = []

                    for j, element_in_synthesis in enumerate(synthesis_setup['elements_in_synthesis']):

                        element_in_synthesis = element_in_synthesis.__dict__
                        element_in_synthesis['atomic_number'] = int(element_in_synthesis['atomic_number'])
                        element_in_synthesis['highlight'] = bool(element_in_synthesis['highlight'])

                        for key in element_in_synthesis.keys():
                            if key.startswith('__'):
                                del element_in_synthesis[key]

                        elements_in_synthesis.append(element_in_synthesis)

                    synthesis_setup['elements_in_synthesis'] = elements_in_synthesis

                # Synthesised spectra
                if 'synthesised_spectra' in synthesis_setup:

                    synthesised_spectra_filenames = []

                    for j, spectrum in enumerate(synthesis_setup['synthesised_spectra']):

                        synthesised_spectrum_filename = os.path.join(twd, 'synth-%i-%i.fits' % (i, j, ))
                        
                        # Save the spectrum
                        spectrum.save(synthesised_spectrum_filename)

                        # Save the basename to the session, since it will be relate to the TWD
                        synthesised_spectra_filenames.append(os.path.basename(synthesised_spectrum_filename))

                    synthesis_setup['synthesised_spectra'] = synthesised_spectra_filenames

                # Elemental abundances and solar abundances should be initialised on load
                remove_keys = ('smoothed_spectra', 'difference_spectra', 'elemental_abundances', 'solar_abundances')
                for key in synthesis_setup.keys():
                    if key in remove_keys or key.startswith('__'):
                        del synthesis_setup[key]

                logger.debug("This synthesis setup is currently: %s" % (synthesis_setup, ))

                # Save this JSON-ready synthesis setup
                json_ready_synthesis_setups.append(synthesis_setup)

            logger.debug("Saving synthesis setups as %s" % (json_ready_synthesis_setups, ))
            saved_session['synthesis_setups'] = json_ready_synthesis_setups
        '''

        json_ready_synthesis_setups = []
        if saved_session.has_key('synthesis_setups'):
            
            synthesised_spectra_saved = 0
            for i, synthesis_setup in enumerate(saved_session['synthesis_setups']):
                dictionary = synthesis_setup.__dict__.copy()


                # Synthesized spectra
                if dictionary.has_key('synthesised_spectra'):
                    synthesised_spectra_filenames = []
                    for i, spectrum in enumerate(dictionary['synthesised_spectra']):
                        synthesised_filename = os.path.join(twd, 'synth_%i.fits' % (synthesised_spectra_saved, ))
                        
                        synthesised_spectra_filenames.append('synth_%i.fits' % (synthesised_spectra_saved, ))
                        spectrum.save(synthesised_filename)
                        synthesised_spectra_saved += 1

                    dictionary['synthesised_spectra'] = synthesised_spectra_filenames

                # Remove all __* keys and keys marked as removable
                remove_keys = ['smoothed_spectra', 'difference_spectra', 'elemental_abundances']
                
                for key in dictionary.keys():
                    if key.startswith('__') or key in remove_keys:
                        del dictionary[key]

                json_ready_synthesis_setups.append(dictionary)
            
            saved_session['synthesis_setups'] = json_ready_synthesis_setups
        
        ''' 
        # Configuration
        remove_corrupted = []

        try:
            session_repr = json.dumps(saved_session)
            
        except TypeError:
            logger.warn("Saved session was unpickleable! This is a serious error.")
            logger.warn("Attempting to locate source of problem..")
            
            for key, value in saved_session.iteritems():
                try:
                    json.dumps(value)
                
                except TypeError:
                    logger.info("\tFailed on session key '%s'..." % (key, ))
                    logger.info("\tValue is: %s" % (value, ))
                    
                    if isinstance(value, (dict, list, tuple)):

                        for sub_item in value:

                            # Get the actual value
                            sub_item_value = value[sub_item] if isinstance(value, dict) else sub_item

                            try:
                                json.dumps(sub_item_value)

                            except TypeError:
                                logger.warn("\t\tFailed on session sub-item '%s'..." % (sub_item, ))

                                if isinstance(sub_item_value, dict):
                                    for sub_key, sub_value in sub_item_value.iteritems():
                                        try:
                                            json.dumps(sub_value)
                                        except TypeError:
                                            logger.warn("\t\t\tFailed on session sub-sub-key '%s': %s (%s)" % (sub_key, sub_value, type(sub_value), ))

                    logger.info("\tRemoving entire '%s' key..." % (key, ))

                    remove_corrupted.append(key)
                    break

        if len(remove_corrupted) > 0:

            for key in remove_corrupted:
                del saved_session[key]

            try:
                session_repr = json.dumps(saved_session)

            except TypeError:
                raise

            else:
                logger.info("We were able to save part of the SMH file.")

                if os.path.exists(output_filename):
                    logger.info("Since the filename '%s' already exists, we will not overwrite it with a corrupted file. Saving to %s.partial instead" \
                        % (output_filename, output_filename, ))

                    output_filename += '.partial'

        # Save the pickled session
        session_filename = os.path.join(twd, 'session.json')
        with open(session_filename, 'w') as fp:
            fp.write(session_repr)
            
        # Gzip the temporary working directory and move it to the specified filename
        os.system('cd %s; tar -czvf archive.tar.gz *' % (twd, ))
        os.system('mv %s/archive.tar.gz %s' % (twd, output_filename, ))
        logger.info("Session saved to %s" % (output_filename, ))
        
        # Save the temporary working directory into the session
        self.twd = twd
        self.save_as_filename = output_filename
        
        return True


    def load_settings(self, filename):
        """Loads a JSON file containing settings for `ApplicationMain`.
        
        Inputs
        ----
        filename : str
            The filename containing the settings in a JSON representation.
            
        Raises
        ----
        IOError,
            If the filename specified cannot be found.
        """
        
        if not os.path.exists(filename):
            raise IOError("Filename '%s' does not exist." % (filename, ))
        
        filename = os.path.abspath(os.path.expanduser(filename))
        logger.info("Loading settings from {0} into session".format(filename))
        
        with open(filename, 'r') as fp:
            settings_repr = json.load(fp)
        
        if settings_repr.has_key('synthesis_setups'):
            synthesis_setups_repr = []
            
            for synthesis_setup in settings_repr['synthesis_setups']:
                # Check for blanks
                if len(synthesis_setup.keys()) == 0: continue
                # Check for isotopic ratios
                if "isotopic_ratios" in synthesis_setup:
                    isotopic_ratios = []
                    for isotopic_ratio in synthesis_setup['isotopic_ratios']:
                        isotopic_ratios.append(IsotopicRatio(**isotopic_ratio))

                    synthesis_setup['isotopic_ratios'] = isotopic_ratios

                synthesis_setups_repr.append(Session.Synthesis(self, **synthesis_setup))
            
            settings_repr['synthesis_setups'] = synthesis_setups_repr
        
        relative_keywords = ['model_atmosphere_folder', 'doppler_template_filename', 'solar_abundances_filename', 'line_list_filename']
        for key, value in settings_repr.iteritems():
            if key in relative_keywords:
                value = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', value))

            setattr(self, key, value)

            if key == "line_list_filename":
                self.load_line_list(value)

        
        return True
    
    
    def load(self, session_filename):
        """Loads a previously saved session file.
        
        Parameters
        ----------
        session_filename : str
            Filename to load the session from.
            
        Raises
        ------
        IOError,
            If the filename specified cannot be found.
        """
        
        if not os.path.exists(session_filename):
            raise IOError("filename '%s' does not exist." % (session_filename, ))
        
        logger.debug("Session.load(%s)" % (session_filename, ))
        
        # We need a twd to extract everything to
        twd = self.twd if self.__dict__.has_key('twd') else mkdtemp()
        assert os.path.exists(twd)

        # Copy the archive to a temporary directory and extract the files
        source, destination = (session_filename, "%s/archive.tar.gz" % (twd, ))
        
        if source != destination:
            try:
                shutil.copyfile(source, destination)

            except shutil.Error as reason:
                logger.warn("Error when copying file '%s' to '%s': %s" % (source, destination, reason, ))

        os.system('cd %s; tar -xzf archive.tar.gz' % (twd, ))
        
        # Load in settings
        session_json_filename = os.path.join(twd, 'session.json')

        if not os.path.exists(session_json_filename):
            logger.warn("No session file found in %s!" % (session_json_filename, ))

        with open(session_json_filename, 'r') as fp:
            session_json = json.loads("".join(fp.readlines()))


        # LEGACY NOTES START
        if 'stellar_atmosphere_type' in session_json and 'ODFNEW' in session_json['stellar_atmosphere_type']:
            session_json['stellar_atmosphere_type'] = atmospheres.parsers.keys()[0]

        if 'stellar_fe_abundance' in session_json and 'stellar_reference_fe_h' not in session_json:
            session_json['stellar_reference_fe_h'] = session_json['stellar_fe_abundance']
        # LEGACY NOTES END

        prefix_attribute_with_twd = ('solar_abundances_filename', 'stellar_atmosphere_filename')

        attribute_load_order = (
            'measurements', 'solar_abundances_filename', 'synthesis_setups'
            )

        # SMH-relative paths
        # TODO - not sure if we need this..
        attributes_with_relative_paths = ['model_atmosphere_folder', 'doppler_template_filename']

        for attribute in attributes_with_relative_paths:
            if hasattr(self, attribute):
                filename = getattr(self, attribute)

                if os.path.exists(filename): continue
                else:
                    setattr(self, attribute, os.path.abspath(os.path.join(os.path.dirname(__file__), '../', filename)))


        # Load all non-sequential attributes
        for attribute in session_json:
            if attribute not in attribute_load_order:
                attribute_value = session_json[attribute]

                if attribute in prefix_attribute_with_twd:
                    attribute_value = os.path.join(twd, attribute_value)

                setattr(self, attribute, attribute_value)

        # Load sequential attribute
        for attribute in attribute_load_order:
            
            # Check that we have this attribute
            if attribute not in session_json: continue

            # Get the attribute value
            attribute_value = session_json[attribute]

            # Prefix the attribute value with the TWD if necessary
            if attribute in prefix_attribute_with_twd:
                attribute_value = os.path.join(twd, attribute_value)

            # Load the measurements as AtomicTransition objects
            if attribute == 'measurements':
                loaded_measurements = []
            
                for measurement in attribute_value:
                    fred = AtomicTransition(**measurement)
                    if "abundance" in measurement:
                        fred.abundance = measurement["abundance"]
                    loaded_measurements.append(fred)
                
                self.measurements = loaded_measurements
            

            elif attribute == 'synthesis_setups':

                loaded_synthesis_setups = []
                
                for synthesis_setup in session_json['synthesis_setups']:

                    # Load in everything except the line list, elements_in_synthesis, synthesized_spectra
                    # Load as a SynthesisSetup and provide this session as a kwarg
                    # Set the line list for the SynthesisSetup
                    # Set the abundances for each element_in_synthesis
                    synthesis_setup_copy = synthesis_setup.copy()
                    if "line_list_filename" in synthesis_setup_copy:
                        synthesis_setup_copy["line_list_filename"] = os.path.join(twd, synthesis_setup["line_list_filename"])


                    #if 'line_list_filename' in synthesis_setup_copy: del synthesis_setup_copy['line_list_filename']
                    if 'synthesised_spectra' in synthesis_setup_copy: del synthesis_setup_copy['synthesised_spectra']
                    if 'elements_in_synthesis' in synthesis_setup_copy: 
                        synthesis_setup_copy['elements_in_synthesis'] = [ElementInSynthesisSetup(**kwargs) for kwargs in synthesis_setup_copy["elements_in_synthesis"] if kwargs["element_repr"] not in ['106', '606', '607', '107', '112']]

                    if 'isotopic_ratios' in synthesis_setup_copy:

                        if len(synthesis_setup_copy['isotopic_ratios']) == 0:
                            del synthesis_setup_copy['isotopic_ratios']

                        elif isinstance(synthesis_setup_copy["isotopic_ratios"][0], dict):
                            isotopic_ratios_as_str = ""
                            #[{u'isotopes': [], u'ratios_repr': u'41.24/15.19/12.73/8.92/1.39', u'species': 56, u'ratios': [], u'isotopes_repr': u'1134/1135/1136/1137/1138'}]
                            for isotopic_ratio in synthesis_setup_copy["isotopic_ratios"]:

                                species = isotopic_ratio["species"]
                                split_character = "/"

                                for isotope, ratio in zip(isotopic_ratio["isotopes_repr"].split(split_character), isotopic_ratio["ratios_repr"].split(split_character)):
                                    isotope, ratio = map(float, ['0.' + isotope, ratio])

                                    isotopic_ratios_as_str += str(species + isotope) + " " + " ".join(map(str, [ratio] * 5)) + "\n"

                            synthesis_setup_copy['isotopic_ratios'] = isotopic_ratios_as_str.rstrip("\n")


                    #logger.debug("synthesised abundances -C: %s " % (synthesis_setup['synthesised_abundances'], ))

                    #if 'isotopic_ratios' in synthesis_setup_copy:
                    #    synthesis_setup_copy['isotopic_ratios'] = ''
                        
                    synthesis_setup_repr = Session.Synthesis(self, **synthesis_setup_copy)
                    #logger.debug("synthesised abundances A: %s" % (synthesis_setup_repr.synthesised_abundances, ))
                    
                    #synthesis_setup_repr.line_list_filename = os.path.join(twd, synthesis_setup['line_list_filename'])

                    #logger.debug("synthesised abundances B: %s" % (synthesis_setup_repr.synthesised_abundances, ))


                    # Load the spectra
                    if 'synthesised_spectra' in synthesis_setup:
                        logger.debug("Loading synthesised spectra: %s" % (synthesis_setup['synthesised_spectra'], ))
                        synthesis_setup_repr.synthesised_spectra = [Spectrum1D.load(os.path.join(twd, filename)) for filename in synthesis_setup['synthesised_spectra']]
                    
                    # Load in the abundance to each element in synthesis
                    if False and 'elements_in_synthesis' in synthesis_setup:

                        print("ELEMENTS IN SYNTH", synthesis_setup["elements_in_synthesis"])
                        logger.debug("Loading elements in synthesis: %s" % (synthesis_setup['elements_in_synthesis'], ))

                        for element_in_synthesis_from in synthesis_setup['elements_in_synthesis']:

                            per_element_transferable_keys = ('log_epsilon', 'abundance_minus_offset', 'abundance_plus_offset')
                            for element_in_synthesis_to in synthesis_setup_repr.elements_in_synthesis:
                                if int(element_in_synthesis_from['atomic_number']) == int(element_in_synthesis_to.atomic_number):

                                    # Set the attributes we want transferred for each element in synthesis
                                    for key in per_element_transferable_keys:
                                        if key in element_in_synthesis_from:
                                            setattr(element_in_synthesis_to, key, element_in_synthesis_from[key])

                    loaded_synthesis_setups.append(synthesis_setup_repr)

                # Load the synthesis setups
                setattr(self, 'synthesis_setups', loaded_synthesis_setups)
        
        # Load in the spectra files
        # Continuum orders first otherwise you'll get weird behaviour
        c, continuum_orders = 0, []
        while True:
            filename = os.path.join(twd, 'continuum_order_%i.fits' % (c, ))

            if not os.path.exists(filename):
                setattr(self, 'continuum_orders', continuum_orders)
                break

            continuum_orders.append(Spectrum1D.load(filename))
            c += 1

        # Load the initial orders
        i, initial_orders = 0, []
        while True:
            filename = os.path.join(twd, 'initial_order_%i.fits' % (i, ))

            if not os.path.exists(filename):
                setattr(self, 'initial_orders', initial_orders)
                break

            initial_orders.append(Spectrum1D.load(filename))
            i += 1        

        logger.info("Found %i initial orders and %i continuum orders" % (i, c, ))

        # Load additional spectrum files
        spectrum_keywords = ('normalised_spectrum', 'telluric_spectrum', 'snr_spectrum')
        for spectrum_keyword in spectrum_keywords:
            spectrum_filename = os.path.join(twd, spectrum_keyword + '.fits')
            
            if os.path.exists(spectrum_filename):
                setattr(self, spectrum_keyword, Spectrum1D.load(spectrum_filename))


        # 
        possible_object_keywords = ("OBJECT", "NAME")
        for possible_object_keyword in possible_object_keywords:
            if possible_object_keyword in self.headers:
                self.object_name = self.headers[possible_object_keyword].upper()
                break
        else:
            self.object_name = "Unknown"

        if "RA" in self.headers:
            self.ra_repr = str(self.headers["RA"])

        if "DEC" in self.headers:
            self.dec_repr = str(self.headers["DEC"])


        # Add the TWD and session filename to the session.
        setattr(self, 'twd', twd)
        setattr(self, 'save_as_filename', session_filename)


        return True


    def calculate_atomic_abundances(self, species="all", full_output=False):
        """
        Calculates elements for all elements in the atomic line list that have acceptable
        equivalent width measurements

        Parameters
        ----------

        species : list of floats, optional
            A list containing the species (atomic number + ionisation state, e.g., 26.0 
            for neutrally ionized iron) to calculate abundances for
        """

        # Get all the relevant lines
        lines_to_measure_abundances_for = []
        measurement_rest_wavelengths = []
        for measurement in self.measurements:
            if measurement.is_acceptable and measurement.measured_equivalent_width > 0 \
            and (species == "all" or measurement.transition in species):
                lines_to_measure_abundances_for.append(measurement)
            
            # Keep a record of all the rest wavelengths so we can supply abundance
            # information back to the session
            measurement_rest_wavelengths.append(measurement.rest_wavelength)
        
        # Are there actually any lines we should be measuring?
        if len(lines_to_measure_abundances_for) == 0: 
            return False
        
        # Prepare MOOG files
        measurement_rest_wavelengths = np.array(measurement_rest_wavelengths)
        equivalent_widths_filename = os.path.join(self.twd, "elemental_abundances.ew")
        moog_output_prefix = os.path.join(self.twd, "moog_abundances.out")
        moog.io.write_equivalent_widths(lines_to_measure_abundances_for, equivalent_widths_filename, force_loggf=True, clobber=True)
        
        # Run MOOG abfind routine
        abundances, slopes = moog.abfind(moog_output_prefix, equivalent_widths_filename,
            self.stellar_atmosphere_filename, twd=self.twd)

        assert len(abundances) == len(lines_to_measure_abundances_for)
        
        # Set up some column index references
        col_wl, col_transition, col_ep, col_loggf, col_ew, col_logrw, col_abund, col_del_avg, col_idx_match = xrange(9)

        # Update abundances array to have real reduced equivalent widths
        #print("B", [item.reduced_equivalent_width for item in lines_to_measure_abundances_for])
        abundances[:, col_logrw] = [item.reduced_equivalent_width for item in lines_to_measure_abundances_for]
        distributions, slopes = moog.calculate_trend_lines(
            abundances,
            transition_col=col_transition,
            x_cols=(col_ep, col_logrw, col_wl),
            y_col=col_abund)
        
        # Append a column to abundances for index referencing
        abundances = np.append(abundances, -np.ones((len(abundances), 1)), 1)
        tolerance_match = 1e-2 # Angstroms
        for i, abundance in enumerate(abundances):
            
            dist = np.abs(abundance[col_wl] - measurement_rest_wavelengths)    
            idx, closeness = np.argmin(dist), np.min(dist)
            if closeness > tolerance_match:
                logger.warn("Wavelength tolerance constraint not met!")
                logger.warn("\t %3.3f %3.3f (%1.3e)" % (abundance[col_wl], measurement_rest_wavelengths[idx], closeness, ))
                
            # Update the abundances with the index of the session measurement
            abundances[i, col_idx_match] = idx
            self.measurements[idx].abundance = abundance[col_abund]
            
        # Check we didn"t miss any
        check = np.where(abundances[:, col_idx_match] == -1)[0]
        if len(check) > 0:
            logger.warn("Not all abundances from MOOG were matched to the session:")
            logger.warn(abundances[check])

        # Apply any automatic non-LTE abundance corrections
        self.apply_automatic_nlte_corrections()
        
        if full_output:
            return abundances, distributions, slopes

        return abundances

        
    class Normalisation(object):

        def __init__(self, session):
            self.__session__ = session

        def stitch_apertures(self):
            """Stitches together overlapping or separate apertures into a single
            one-dimensional linear spectrum. If the apertures have had continuum
            fitted to them, then a normalised, stitched spectrum will result.
            Otherwise, the apertures are assumed to be already normalised outside
            of SMH."""

            # Define the sub-pixel scale:
            # Sample rate
            sample_rate = 1

            wl_start = self.__session__.initial_orders[0].disp[0]
            wl_end = self.__session__.initial_orders[-1].disp[-1]

            wl_pixel_step = np.diff(self.__session__.initial_orders[0].disp[:2])[0]
            wl_linear_step = wl_pixel_step / sample_rate

            linear_disp = np.arange(wl_start, wl_end + wl_linear_step, wl_linear_step)

            if len(self.__session__.initial_orders) > len(self.__session__.continuum_orders):
                # Assume some apertures are already normalised.

                # Special case
                if len(self.__session__.initial_orders) == 1:
                    self.__session__.normalised_spectrum = self.__session__.initial_orders[0]
                    return self.__session__.initial_orders[0]

                num_to_extend = len(self.__session__.continuum_orders) - len(self.__session__.initial_orders)
                for aperture in self.__session__.initial_orders[-num_to_extend:]:
                    self.__session__.continuum_orders.append(Specrum1D(disp=aperture.disp, flux=np.ones(len(aperture.disp))))

            # Stack all the unnormalised spectra on top of each other
            # Stitch the stacked unnormalised spectra onto a linear scale

            # Stack all the continuum functions on top of each other
            # Stitch the stacked continuum function onto a linear scale

            # These need to be done in conjunction with one other so that
            # we only take the intersect of both their dispersion domains

            stacked_unnormalised_flux = np.zeros(len(linear_disp))
            stacked_continuum = np.zeros(len(linear_disp))

            for i, (unnormalised_order, continuum_order) in enumerate(zip(self.__session__.initial_orders, self.__session__.continuum_orders)):

                # Find the intersection of their dispersions
                
                min_disp = np.max([unnormalised_order.disp[0], continuum_order.disp[0]])
                max_disp = np.min([unnormalised_order.disp[-1], continuum_order.disp[-1]])

                u_idx_l = np.searchsorted(unnormalised_order.disp, min_disp, side='left')
                u_idx_r = np.searchsorted(unnormalised_order.disp, max_disp, side='right')

                c_idx_l = np.searchsorted(continuum_order.disp, min_disp, side='left')
                c_idx_r = np.searchsorted(continuum_order.disp, max_disp, side='right')

                f_u = interp1d(
                    unnormalised_order.disp[u_idx_l:u_idx_r],
                    unnormalised_order.flux[u_idx_l:u_idx_r],
                    bounds_error=False, fill_value=0.0)

                f_c = interp1d(
                    continuum_order.disp[c_idx_l:c_idx_r],
                    continuum_order.flux[c_idx_l:c_idx_r],
                    bounds_error=False, fill_value=0.0)

                stacked_unnormalised_flux += f_u(linear_disp)
                stacked_continuum += f_c(linear_disp)

            # Divide stacked unnormalised spectra / stacked continuum function (on linear scale)
            normalised_flux = stacked_unnormalised_flux / stacked_continuum
            normalised_spectrum = Spectrum1D(disp=linear_disp, flux=normalised_flux)

            self.__session__.normalised_spectrum = normalised_spectrum
            num_missing_aperture_args = len(self.__session__.initial_orders) - len(self.__session__.normalisation_arguments)
            self.__session__.normalisation_arguments = self.__session__.normalisation_arguments + [{"default_text": "Assumed to already be normalised"}] * num_missing_aperture_args
            return normalised_spectrum

        def normalise_apertures(self):
            raise NotImplementedError


    class Doppler(object):

        def __init__(self, session):
            self.__session__ = session

        def measure(self, template_filename, wl_start, wl_end):
            """Cross-correlates the session normalised spectrum against a template
            spectrum at rest to determine the stellar radial velocity. The stellar
            radial velocity and it's associated error is updated in the session."""

            v_rad, v_err = cross_correlate(
                self.__session__.normalised_spectrum,
                Spectrum1D.load(template_filename),
                [wl_start, wl_end])

            logger.info("Measured radial velocity is $V_r = %3.2f +/- %3.2f$\,km s$^{-1}$" % (v_rad, v_err, ))

            self.__session__.v_apply_offset = -v_rad
            self.__session__.v_rad, self.__session__.v_err = v_rad, v_err

            return (v_rad, v_err)


        def correct(self, v_rad):
            """Doppler corrects the rest specrum by the given velocity."""

            self.__session__.v_apply_offset = v_rad

            # Updating v_applied_offset will trigger the rest_spectrum to be updated
            self.__session__.v_applied_offset = v_rad

            return True

        def set_already_at_rest(self):
            """Sets the initial spectra to already be at rest."""
            self.correct(0)


    class Synthesis(HasTraits):
        """ A class containing all the information for a chemical synthesis setup """

        periodic_table = """                                                   He
                            Li Be                               B  C  N  O  F  Ne
                            Na Mg                               Al Si P  S  Cl Ar
                            K  Ca Sc Ti V  Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
                            Rb Sr Y  Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I  Xe
                            Cs Ba Lu Hf Ta W  Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn
                            Fr Ra Lr Rf Db Sg Bh Hs Mt Ds Rg Cn UUt"""
        
        lanthanoids    =   "La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb"
        actinoids      =   "Ac Th Pa U  Np Pu Am Cm Bk Cf Es Fm Md No"
        
        periodic_table = periodic_table.replace(' Ba ', ' Ba ' + lanthanoids + ' ').replace(' Ra ', ' Ra ' + actinoids + ' ').split()
        del actinoids, lanthanoids
        
        # These items need to be directly loaded from session. 
        #twd = DelegatesTo("session")
        #elemental_abundances = DelegatesTo("session")
        #stellar_feh = DelegatesTo("session")
        #stellar_reference_fe_h = DelegatesTo("session")
        #stellar_atmosphere_filename = DelegatesTo("session")

        is_acceptable = Bool(True)
        elements_in_synthesis = List(ElementInSynthesisSetup)

        representation = Str
        element = Enum(periodic_table)
        transition = Float
        line_list_filename = File
        comment = Str
        uncertainty = Float(0.10)
        
        #isotopes = Dict
        abundance = Float
        
        smoothing_kernel = Float(0.1)
        observed_smoothing_kernel = Float(0.0)
        continuum_adjust = Float(1.0)
        v_rad = Float

        plot_surrounding = Float(1.0)

        wavelength_regions = List(Float)

        
        # Spectra
        synthesised_abundances = List(Float)
        synthesised_spectra = List(Instance(Spectrum1D))
        smoothed_spectra = List(Instance(Spectrum1D))
        difference_spectra = List(Instance(Spectrum1D))

        chisq_regions = List


        # Isotopic ratio information
        isotopic_ratios = Str

        is_blank = Str('')
        label = Str(' ')

        def __init__(self, session, *args, **kwargs):
            HasTraits.__init__(self)

            # Weak reference to the session
            self.__session__ = session
            
            # Solar abundances can be loaded directly
            self.solar_abundances = solar_abundances

            # Set attributes, although we shouldn't have to..
            for key in kwargs:
                setattr(self, key, kwargs[key])

            if len(self.chisq_regions) == 0 and len(self.wavelength_regions) > 1:
                self.chisq_regions = [
                    self.wavelength_regions[0] - self.plot_surrounding,
                    self.wavelength_regions[1] + self.plot_surrounding
                ]

            self._update_solar_abundances()

        @on_trait_change('comment, element')
        def _update_representation(self):
            self.representation = '%s (%s)' % (self.element, self.comment, )

        def _synthesised_spectra_changed(self, synthesised_spectra):
            self._smooth_and_shift_spectra()

        def _smoothing_kernel_changed(self, smoothing_kernel):
            self._smooth_and_shift_spectra()


        def _smooth_and_shift_spectra(self):
            logger.debug("_smooth_and_shift_spectra()")
            self.smoothed_spectra = [spectrum.gaussian_smooth(self.smoothing_kernel) for spectrum in self.synthesised_spectra]


        def _update_solar_abundances(self):
            """Updates the reference stellar abundances for the current synthesis setup"""
            
            # Get reference [Fe/H]
            if np.isfinite(self.__session__.stellar_reference_fe_h): reference_fe_h = self.__session__.stellar_reference_fe_h
            else: reference_fe_h = solar_abundances["Fe"][0] + self.__session__.stellar_feh

            for synthesis_element in self.elements_in_synthesis:
                
                # Need to get the first element from solar_abundances, because it is structured as [abundance, uncertainty, flag]
                if utils.species_to_element(synthesis_element.atomic_number).split()[0] not in self.solar_abundances.keys():
                    logger.warn("Could not find solar abundance for %s" % (synthesis_element.atomic_number, ))
                    self.solar_abundance = np.nan

                else:
                    self.solar_abundance = solar_abundances[utils.species_to_element(synthesis_element.atomic_number).split()[0]][0]

                self.X_on_Fe_minus_log_epsilon = solar_abundances["Fe"][0] \
                    - self.solar_abundance - reference_fe_h


        def _element_changed(self, element):
            """Update all the elements in synthesis as to whether they should
            be highlighted or not."""
            logger.debug("_element_changed(%s)" % (element, ))

            transition = int(utils.element_to_species(element))

            elements_in_synthesis = []
            for synthesis_element in self.elements_in_synthesis:
                synthesis_element.highlight = int(synthesis_element.atomic_number) == transition
            
        
        def _line_list_filename_changed(self, line_list_filename):
            """Reads in the updated line list and determines the wavelength
            region and the elements in the line list."""

            if line_list_filename is None: return

            logger.debug("Loading line list for synthesis: %s" % (line_list_filename, ))
            line_list_filename = os.path.abspath(line_list_filename)

            try:
                # Try initially loading with the first line included
                wavelengths, species_in_line_list = np.loadtxt(line_list_filename, usecols=(0, 1, ), unpack=True)

            except (IndexError, ValueError) as exception:
                logger.debug("Couldn't load filename '%s' using the first line. Skipping the first row." % (line_list_filename, ))
                wavelengths, species_in_line_list = np.loadtxt(line_list_filename, usecols=(0, 1,), skiprows=1, unpack=True)

            # Deal with single species in line list
            if isinstance(species_in_line_list, (float, int)):
                species_in_line_list = [int(species_in_line_list)]
                wavelengths = [wavelengths]
            else:
                species_in_line_list = np.array(map(int, species_in_line_list))

            # Deal with molecules
            common_molecules = {
                606: [6],
                607: [6, 7],
                112: [12],
                106: [6],
                107: [7],
                122: [22]
            }
            relevant_species = []
            for species in species_in_line_list:
                if species in common_molecules.keys():
                    relevant_species.extend(common_molecules[species])

                else:
                    relevant_species.append(species)

            relevant_species = sorted(list(set(relevant_species)))
            
            # Set all wavelengths as positive to deal with lines with HFS
            wavelengths = np.abs(wavelengths)

            # Specify the wavelength regions
            self.wavelength_regions = [np.min(wavelengths), np.max(wavelengths)]

            if len(self.__session__.elemental_abundances) == 0:
                self.__session__.summarise_abundances()

            # Existing abundances
            existing_species_with_abundances = [int(elemental_abundance.transition) for elemental_abundance in self.__session__.elemental_abundances]

            # Get reference [Fe/H]
            if np.isfinite(self.__session__.stellar_reference_fe_h): reference_fe_h = self.__session__.stellar_reference_fe_h
            else: reference_fe_h = self.solar_abundances["Fe"][0] + self.__session__.stellar_feh

            # What's in the line list?
            elements_in_synthesis = []
            for species in relevant_species:

                # Get rest wavelengths for this element so we can highlight where it is
                species_wavelengths = list(wavelengths[np.where(species_in_line_list == species)[0]])
                if species in sum(common_molecules.values(), []):
                    for molecule, component_species in common_molecules.iteritems():
                        if species in component_species:
                            species_wavelengths += list(wavelengths[np.where(species_in_line_list == molecule)[0]])

                # Elemental abundance transition index
                if species in existing_species_with_abundances:
                    # We have an existing abundance for this species
                    elemental_abundance = self.__session__.elemental_abundances[existing_species_with_abundances.index(species)]
                    X_on_Fe_minus_log_epsilon = elemental_abundance.X_on_Fe - elemental_abundance.abundance_mean

                    if not np.isfinite(X_on_Fe_minus_log_epsilon):
                        X_on_Fe_minus_log_epsilon = self.solar_abundances["Fe"][0] \
                            - self.solar_abundances[utils.species_to_element(species).split()[0]][0] \
                            - reference_fe_h

                    element_in_synthesis = ElementInSynthesisSetup(
                        atomic_number=species, highlight=(species == int(utils.element_to_species(self.element))),
                        X_on_Fe_minus_log_epsilon=X_on_Fe_minus_log_epsilon, log_epsilon=elemental_abundance.abundance_mean,
                        rest_wavelengths=species_wavelengths)

                else:
                    try:
                        X_on_Fe_minus_log_epsilon = self.solar_abundances["Fe"][0] \
                            - self.solar_abundances[utils.species_to_element(species).split()[0]][0] \
                            - reference_fe_h
                    except KeyError: # We don't even have a solar abundance for this.
                        X_on_Fe_minus_log_epsilon = np.nan

                    element_in_synthesis = ElementInSynthesisSetup(
                        atomic_number=species, highlight=(species == int(utils.element_to_species(self.element))),
                        X_on_Fe_minus_log_epsilon=X_on_Fe_minus_log_epsilon, rest_wavelengths=species_wavelengths)

                elements_in_synthesis.append(element_in_synthesis)

            if len(self.chisq_regions) == 0:
                self.chisq_regions = [
                    self.wavelength_regions[0] - self.plot_surrounding,
                    self.wavelength_regions[1] + self.plot_surrounding
                ]

            self.elements_in_synthesis = elements_in_synthesis


        def solve(self, initial_abundance=None, initial_abundance_offset=None, initial_vrad=None,
            initial_continuum_adjust=None, initial_smoothing_kernel=None, abundance_tolerance=0.01,
            max_refinements=5):
            """ Solves the abundance, smoothing, radial velocity and continuum scaling factor
            for the current synthesis setup.
            """

            self.chisq_regions = self.chisq_regions if hasattr(self, "chisq_regions") and len(self.chisq_regions) > 0 else [
                self.wavelength_regions[0] - self.plot_surrounding,
                self.wavelength_regions[1] + self.plot_surrounding
            ]
            
            # Define likelihood function
            def synthesis_chi_sq(inputs, *args):
                """ Interpolates between the synthesised spectra and calculates
                the $\chi^2$ value between the observed spectra and the smoothed,
                scaled, doppler-shifted synthetic spectra. """
                if np.any(~np.isfinite(inputs)): return 999

                requested_abundances, synthesised_spectra = args
                abundance, v_rad, smoothing_kernel, continuum_adjust = inputs

                smoothing_kernel = abs(smoothing_kernel)
                continuum_adjust = abs(continuum_adjust)

                # Get interpolated flux from abundance
                interpolated_flux = griddata(requested_abundances,
                    np.array([spectrum.flux for spectrum in synthesised_spectra]), [abundance]).flatten()

                # Smooth the interpolated flux
                spectrum = Spectrum1D(disp=synthesised_spectra[0].disp, flux=interpolated_flux).gaussian_smooth(smoothing_kernel)
                
                # Interpolate convolved synthetic spectrum onto observed scale
                f = interp1d(spectrum.disp, spectrum.flux, bounds_error=False, fill_value=np.nan)

                all_chisq_regions = np.array(self.chisq_regions).flatten()
                print("ALL CHISQ REGIONS", all_chisq_regions, self.chisq_regions)
                edge_chisq_indices = np.searchsorted(self.__session__.rest_spectrum.disp, [np.min(all_chisq_regions), np.max(all_chisq_regions)])

                # Calculate chi^2 from regions internally, or +/- plot_surrounding?
                observed_segment = Spectrum1D(
                    disp=self.__session__.rest_spectrum.disp[edge_chisq_indices[0]:edge_chisq_indices[1]+1],
                    flux=self.__session__.rest_spectrum.flux[edge_chisq_indices[0]:edge_chisq_indices[1]+1] * continuum_adjust)
                observed_segment = observed_segment.doppler_correct(v_rad)

                # Find the indices of the doppler-corrected segment that correspond with our chisq_regions
                if len(self.chisq_regions) == 2 and isinstance(self.chisq_regions[0], float):
                    indices = (self.chisq_regions[1] >= observed_segment.disp) * (observed_segment.disp >= self.chisq_regions[0])

                else:
                    indices = np.zeros(len(observed_segment.flux))
                    for chisq_region in self.chisq_regions:
                        indices += (chisq_region[1] >= observed_segment.disp) * (observed_segment.disp >= chisq_region[0])
                    indices = np.array(indices, dtype=bool)

                squared_difference = (f(observed_segment.disp[indices]) - observed_segment.flux[indices])**2
                finite_squared_difference = squared_difference[np.isfinite(squared_difference)]
                result = finite_squared_difference

                return sum(result)


            if initial_smoothing_kernel is None:
                initial_smoothing_kernel = self.smoothing_kernel

            if initial_continuum_adjust is None:
                initial_continuum_adjust = self.continuum_adjust

            if initial_vrad is None:
                initial_vrad = self.v_rad

            # Set abundances in abundance table
            for element in self.elements_in_synthesis:
                if element.atomic_number == int(utils.element_to_species(self.element)):
                    if initial_abundance is not None:
                        element.X_on_Fe = initial_abundance

                    elif not np.isfinite(element.X_on_Fe):
                        element.X_on_Fe = 0
                    
                    if initial_abundance_offset is not None:
                        element.abundance_minus_offset = initial_abundance_offset
                        element.abundance_plus_offset =  initial_abundance_offset
                    else:
                        if not np.isfinite(element.abundance_minus_offset) or element.abundance_minus_offset == 0:
                            element.abundance_minus_offset = 1
                        if not np.isfinite(element.abundance_plus_offset) or element.abundance_plus_offset == 0:
                            element.abundance_plus_offset = 1

                    requested_abundances = np.array([
                        element.X_on_Fe - element.abundance_minus_offset,
                        element.X_on_Fe,
                        element.X_on_Fe + element.abundance_plus_offset
                    ])
                    break



            previous_abundance = None
            x0 = [requested_abundances[1], initial_vrad, initial_smoothing_kernel, initial_continuum_adjust]

            for refinement in xrange(max_refinements):
                logger.info("ITERATION {0} {1}".format(refinement, x0))

                # Synthesise and retrieve 3 spectra
                synthesised_abundances, synthesised_spectra = self.synthesize()

                # Check that we had a good first guess for abundances:
                for abundance, spectrum in zip(synthesised_abundances, synthesised_spectra):
                    if np.std(spectrum.flux) == 0 and np.mean(spectrum.flux) == 1:
                        # All we got back was unity flux
                        logger.warn("Initial synthesis abundance of log_eps({0}) = {1:.2f} returned only continuum!".format(
                            self.element, abundance))

                # Minimise by a weighted least squares method
                final_parameters = fmin(synthesis_chi_sq, x0, args=(requested_abundances, synthesised_spectra), ftol=1e-9, xtol=1e-9)

                # Ensure smoothing kernel and continuum adjust are positive parameters
                final_parameters[2:] = map(abs, final_parameters[2:])

                # Set the values back to the setup
                self.abundance, self.v_rad, self.smoothing_kernel, self.continuum_adjust = final_parameters
                for element in self.elements_in_synthesis:
                    if element.atomic_number == int(utils.element_to_species(self.element)):
                        element.X_on_Fe = self.abundance
                        element.abundance_minus_offset = 0.3
                        element.abundance_plus_offset = 0.3
                        requested_abundances = np.array([self.abundance - 0.3, self.abundance, 0.3 + self.abundance])
                        break

                # Did we reach the tolerance?
                if previous_abundance is not None and abundance_tolerance >= abs(previous_abundance - self.abundance):
                    break

                previous_abundance = self.abundance
                x0 = final_parameters


            self.synthesize()
            return final_parameters



        def synthesize(self):
            """ Calls MOOG, synthesises spectra for the current setup """
            
            # Prepare abundance table
            moog_abundance_table = []
            for i, element_in_synthesis in enumerate(self.elements_in_synthesis):
                print("DOING", i, element_in_synthesis, element_in_synthesis.X_on_Fe)
                if not np.isfinite(element_in_synthesis.X_on_Fe): continue

                # If it's an atomic transition, then we should put in both neutral and singly
                # ionized abundances
                neutral_species = float(element_in_synthesis.atomic_number)
                single_ionized_species = neutral_species + 0.1

                for species in (neutral_species, single_ionized_species):
                    abundance_line = [
                        species,
                        element_in_synthesis.X_on_Fe,
                        element_in_synthesis.abundance_minus_offset,
                        element_in_synthesis.abundance_plus_offset,
                    ]
                    # Add this line to the table
                    moog_abundance_table.append(abundance_line)

            moog_abundance_table = np.array(moog_abundance_table)
            print("Current table", moog_abundance_table)

            # Check to see that we actually need to do the offsets
            remove_columns = []
            unique_minus_offsets = np.unique(moog_abundance_table[:, 2])
            if len(unique_minus_offsets) == 1 and unique_minus_offsets[0] == 0:
                remove_columns.append(2)

            else:
                # values = [X/Fe] - offset
                moog_abundance_table[:, 2] = moog_abundance_table[:, 1] - moog_abundance_table[:, 2]

            unique_plus_offsets = np.unique(moog_abundance_table[:, 3])
            if len(unique_plus_offsets) == 1 and unique_plus_offsets[0] == 0:
                remove_columns.append(3)

            else:
                moog_abundance_table[:, 3] += moog_abundance_table[:, 1]

            # Remove any unnecessary columns
            moog_abundance_table = np.delete(moog_abundance_table, remove_columns, axis=1)

            # Give the offset difference from [X/Fe] to [X/M]
            if all(np.isfinite([self.__session__.stellar_feh, self.__session__.stellar_reference_fe_h])):
                moog_abundance_table[:, 1:] -= (self.solar_abundances["Fe"][0] + self.__session__.stellar_feh - self.__session__.stellar_reference_fe_h)
            #moog_abundance_table[:, 1:] -= (self.X_on_Fe_minus_log_epsilon + self.solar_abundances["Fe"][0]

            logger.debug("MOOG Abundance Table:")
            logger.debug(moog_abundance_table)

            # Prepare the isotopic ratios
            num_isotopic_lines = self.isotopic_ratios.strip().count("\n") + 1

            isotopic_ratios = np.fromstring(self.isotopic_ratios, sep=" ")
            formatted_isotope_ratios = isotopic_ratios.reshape((num_isotopic_lines, len(isotopic_ratios)/float(num_isotopic_lines), ))

            # Because the February 2013 version of MOOG is even MORE pedantic about this, we can
            # only specify the same number of isotopic ratios we're providing as input.
            formatted_isotope_ratios = formatted_isotope_ratios[:, :moog_abundance_table.shape[1]]
            logger.debug("Formatted isotopic ratios: %s" % (formatted_isotope_ratios, ))

            # Copy line list filename to twd
            if not self.line_list_filename.startswith(self.__session__.twd):
                line_list_filename = os.path.join(self.__session__.twd, os.path.basename(self.line_list_filename))
                os.system('cp "{0}" "{1}"'.format(self.line_list_filename, line_list_filename))

            else:
                line_list_filename = self.line_list_filename

            # Prepare the synthesis filename
            synth_in = moog.prepare_synth_file(moog_abundance_table,
                                               line_list_filename,
                                               self.__session__.stellar_atmosphere_filename,
                                               observed=None,
                                               twd = self.__session__.twd,
                                               isotope_ratios = formatted_isotope_ratios,
                                               synthesis_pm_range = self.plot_surrounding)
                                               
            # Run the synthesis and give us back the spectra
            self.synthesised_abundances, self.synthesised_spectra = moog.synth(synth_in, element=self.element)
            
            # Which columns were removed?
            if len(self.synthesised_abundances) == 1:
                self.abundance = self.synthesised_abundances[0]
                self.uncertainty = np.nan

            elif len(self.synthesised_abundances) == 2:

                if remove_columns == [3]:
                    self.abundance = self.synthesised_abundances[1]

                else:
                    self.abundance = self.synthesised_abundances[0]

                self.uncertainty = np.abs(np.diff(self.synthesised_abundances))[0]

            else:
                # We have a positive and negative uncertainty
                self.abundance = self.synthesised_abundances[1]
                self.uncertainty = np.max(np.abs(np.diff(self.synthesised_abundances)))

            return (self.synthesised_abundances, self.synthesised_spectra)


            
