# coding: utf-8

""" Module to interface with MOOG and return Python objects """

__author__ = "Andy Casey <andy@astrowizici.st>"

# Standard library
import logging
import operator
import os
import re
import shutil

from random import choice
from signal import alarm, signal, SIGALRM, SIGKILL
from subprocess import PIPE, Popen
from textwrap import dedent

# Third party
import numpy as np
import scipy.stats as statistics
from scipy import delete

# Module specific
from specutils import Spectrum1D
from utils import element_to_species, species_to_element

acceptable_moog_return_codes = (0, )
MOOGSILENT = "MOOGSILENT"

# For Stromlo machines:
# (also check tempfile in core.py)
#acceptable_moog_return_codes = (0, -6)
#MOOGSILENT = "/home/acasey/moog2011-miner/MOOGSILENT"

logger = logging.getLogger(__name__)

class MOOGError(BaseException):
    pass

def run(input_filename, cwd=None, timeout=30, shell=False, env=None):
    """ Execute a MOOG input file with a timeout after which it will be forcibly killed. """

    logger.info("Executing MOOG input file: {0}".format(input_filename))

    class Alarm(Exception):
        pass

    def alarm_handler(signum, frame):
        raise Alarm

    if cwd is None:
        cwd = os.path.dirname(input_filename)
    
    if env is None and len(os.path.dirname(MOOGSILENT)) > 0:
        env = {"PATH": os.path.dirname(MOOGSILENT)}

    p = Popen([os.path.basename(MOOGSILENT)], shell=shell, bufsize=2056, cwd=cwd, stdin=PIPE, stdout=PIPE, 
        stderr=PIPE, env=env, close_fds=True)

    if timeout != -1:
        signal(SIGALRM, alarm_handler)
        alarm(timeout)
    try:
        # Stromlo clusters may need a "\n" prefixed to the input for p.communicate
        pipe_input = "\n" if -6 in acceptable_moog_return_codes else ""
        pipe_input += os.path.basename(input_filename) + "\n"*100

        stdout, stderr = p.communicate(input=pipe_input)
        if timeout != -1:
            alarm(0)
    except Alarm:

        # process might have died before getting to this line
        # so wrap to avoid OSError: no such process
        try:
            os.kill(p.pid, SIGKILL)
        except OSError:
            pass
        return (-9, '', '')

    return (p.returncode, stdout, stderr)


class io:
    
    @staticmethod    
    def write_equivalent_widths(measurements, filename, transitions='all',
                                force_loggf=True, comment=None, clobber=False):
        """Writes equivalent widths to an output file which is compatible for
        MOOG.
        
        Parameters
        ----
        measurements : list of `AtomicTransition` objects
            A list where each row contains the following:
        
        filename : str
            Output filename for the measured equivalent widths.
        
        transitions : list of float-types, optional
            A list of transitions to write to file. Default is to write "all"
            transitions to file.

        force_loggf : bool
            Should MOOG treat all the oscillator strengths as log(gf) values?
            If all lines in the list have positive oscillator strengths, using
            this option will force a fake line in the list with a negative
            oscillator strength.
            
        comment : str, optional
            A comment to place at the top of the output file.
        
        clobber : bool, optional
            Whether to over-write the `filename` if it already exists.
        """
        
        if os.path.exists(filename) and not clobber:
            raise IOError("Cannot overwrite existing filename '%s' because clobber is False" % (filename, ))
            
        if transitions != 'all' and not isinstance(transitions, list):
            raise TypeError("Transitions must be a list of float-types or 'all'")
        
        output_string = comment if comment is not None else ''
        output_string += "\n"
        
        measurements_arr = []
        for i, measurement in enumerate(measurements):

            if transitions != "all" and measurement.transition not in transitions: continue
            if not measurement.is_acceptable or 0 >= measurement.measured_equivalent_width: continue
            
            measurements_arr.append([measurement.rest_wavelength,
                                     measurement.transition,
                                     measurement.excitation_potential,
                                     measurement.oscillator_strength,
                                     measurement.measured_equivalent_width])

        measurements_arr = np.array(measurements_arr)

        if force_loggf and np.all(measurements_arr[:, 3] > 0):
            logger.info("Adding fake line to line list with a negative oscillator strength.")
            measurements_arr = np.insert(measurements_arr, 0, [9000., 89., 0.0, -9.999, 0.0], axis=0)
        
        # Sort all the lines first transition, then by wavelength
        measurements_arr = sorted(measurements_arr, key=operator.itemgetter(1, 0))
        
        for line in measurements_arr:
            output_string += "%10.3f %9.3f %8.2f %6.2f                             %5.1f\n" % (line[0], line[1], line[2], line[3], line[4], )
        
        with open(filename, 'w') as fp:
            fp.write(output_string)
        
        return True


def calculate_trend_lines(abundances, transition_col, x_cols, y_col):
    """Calculates the slope and offset for the given abundances from MOOG for
    the main plots."""
    
    if len(abundances) == 0: return

    unique_transitions = np.unique(abundances[:, transition_col])
    
    distributions = {}
    slopes = {}
    
    for transition in unique_transitions:
        
        idx = np.where(abundances[:, transition_col] == transition)[0]
        
        # Get the distribution information first
        N = len(idx)
        mean = np.mean(abundances[idx, y_col])
        std = np.std(abundances[idx, y_col])
        
        distributions[transition] = (N, mean, std)
        
        # slope, intercept, r-value, p-value, stderr
        slopes_arr = np.ones((len(x_cols), 5))
        
        # Calculate the slopes
        for i, x_col in enumerate(x_cols):
            slopes_arr[i, :] = statistics.linregress(x=abundances[idx, x_col], y=abundances[idx, y_col])
        
        slopes[transition] = slopes_arr
    
    return distributions, slopes




def synth(input_filename, transition=None, element=None, **kwargs):
    """Performs a subprocess call to MOOG to perform synthesis on a given input
    filename, and returns 
    
    Inputs
    ----
    input_filename : str
        MOOG-compatible input filename.
    
    Returns
    ----
    A dictionary containing keywords and `specutils.Spectrum1D` objects. The keys
    refer to either 'observed' for the observed spectrum, or the abundance of the
    element in question. For example:
    
        >> {
            'observed': <specutils.Spectrum1D object at 0x1e5083c0>,
            -9.0: <specutils.Spectrum1D object at 0x1e4043c0>,
            -0.50: <specutils.Spectrum1D object at 0x1e4283c0>,
            0.00: <specutils.Spectrum1D object at 0x1e4013c0>,
            0.50: <specutils.Spectrum1D object at 0x1e4023c0>
        }
    """

    if transition is None and element is None:
        raise ValueError("no transition or element provided")

    if transition is not None and element is not None:
        raise ValueError("both transition and element provided -- specify one.")
    
    if transition is not None:
        element = species_to_element(transition).split()[0]

    elif element is not None:
        transition = element_to_species(element)

    # Run MOOG
    moog_code, moog_stdout, moog_stderr = run(input_filename)

    if moog_code not in acceptable_moog_return_codes:
        logger.info("MOOG returned the following standard output:")
        logger.info(moog_stdout)
        logger.warn("MOOG returned the following errors (code: {0:d}):".format(moog_code))
        logger.warn(moog_stderr)

        raise MOOGError(moog_stderr)

    else:
        logger.info("MOOG executed {0} successfully".format(input_filename))
    
    # Extract the output filenames from the input file
    with open(input_filename, 'r') as fp:
        lines = fp.readlines()    
    
    in_abundances = False
    for i, line in enumerate(lines):
        if line.startswith('standard_out'):
            output_filename = ' '.join(line.split()[1:])[1:-1]
            
        if line.startswith('abundances'):
            in_abundances = True
            continue

        if in_abundances and line.lstrip().startswith('%i ' % (transition, )):
            print line
            requested_abundances = map(float, line.split()[1:])
            
            break

        if lines[i - 1].startswith('synlimits'):
            synthesis_step_size = float(line.split()[2])
    
    # Some assertions    
    assert output_filename
    assert requested_abundances
    assert len(requested_abundances) > 0

    '''    
    # Return the synthesized spectra from summary_out
    with open(output_filename, 'r') as fp:
        lines = fp.readlines()
    
    num_points_per_synthesis = int(lines[0].split()[-1])
    
    # Check file length
    #assert len(lines) == len(abundances) * (num_points_per_synthesis + 2)
    
    synthesized_spectra = {}
    for i, abundance in enumerate(abundances):
        
        # Get start and end line indices
        start = i * (num_points_per_synthesis + 2) + 2
        end = start + num_points_per_synthesis
        
        # Grab the lines that contain wavelengths and fluxes
        data = np.array([map(float, line.strip().split()) for line in lines[start:end]])
        
        # Convert to a Spectrum1D object and put into a dictionary
        spectrum = specutils.Spectrum1D(data[:, 0], data[:, 1])
        synthesized_spectra[abundance] = spectrum
    '''
    
    #logger.debug("Estimated synth step size for read out: %1.3f" % (synthesis_step_size, ))

    synthesis_step_size = 0.01 if not 'synthesis_step_size' in kwargs.keys() else kwargs['synthesis_step_size']
    
    logger.debug("actual synth step size used for read out: %1.3f" % (synthesis_step_size, ))

    in_spectrum = False
    with open(output_filename, 'r') as fp:
        lines = fp.readlines()
        
        k = 0
        synthesized_spectra = [None] * len(requested_abundances)
        
        spectrum_flux = []

        returned_abundances = []

        for i, line in enumerate(lines):
            '''
            if line.startswith('SPECTRUM DEPTHS'):
                in_spectrum = True
                spectrum_flux = []
                continue
            
            if in_spectrum and line.startswith('FINAL WAVELENGTH'):
                in_spectrum = False
                
                final_wl = float(line.split()[3])
                
                spectrum_flux = 1.0 - np.array(map(float, spectrum_flux))
                spectrum_disp = np.arange(final_wl - len(spectrum_flux) * synthesis_step_size, final_wl + synthesis_step_size, synthesis_step_size)[0:len(spectrum_flux)]
                
                logger.debug("spectrum disp")
                logger.debug(spectrum_disp)
                logger.debug(spectrum_flux)
                logger.debug(len(spectrum_disp))
                logger.debug(len(spectrum_flux))
                assert len(spectrum_flux) == len(spectrum_disp)
                
                
                synthesized_spectra[i] = Spectrum1D(spectrum_disp, spectrum_flux)
                i += 1
                continue
            
            if not in_spectrum: continue
            
            n_chars = 6
            flux_data = line[19:].rstrip()

            spectrum_flux.extend(
                [flux_data[j:j+n_chars] for j in xrange(0, len(flux_data), n_chars)]
            )
            '''

            if ':  abundance = ' in line \
            and ((len(element) == 1 and line.startswith('element %s :' % (element, ))) or line.startswith('element %s:' % (element, ))):
                returned_abundances.append(float(line.split()[-1]))

            # Dispersion
            if i > 0 and lines[i - 2].startswith('SYNTHETIC SPECTRUM PARAMETER'):

                # Get the dispersion info from the previous couple of lines
                wl_range_info = lines[i - 1].split()

                wl_start, wl_end = map(float, [wl_range_info[2], wl_range_info[5]])

                wl_step_size = float(line.split()[-1])

                spectrum_disp = np.arange(wl_start, wl_end, wl_step_size)

            # Flux
            if ': depths=' in line:
                n_chars = 6
                flux_data = line[19:].rstrip()

                spectrum_flux.extend(
                    [flux_data[j:j+n_chars] for j in xrange(0, len(flux_data), n_chars)]
                    )

            if line.startswith('FINAL WAVELENGTH'):

                spectrum_flux = 1. - np.array(map(float, spectrum_flux))

                if len(spectrum_disp) < len(spectrum_flux):
                    logger.warn("Looks like MOOG is trying to trick us. We won't be so easily fooled.")

                    wl_start = wl_end - wl_step_size * (len(spectrum_flux) - 2)

                    spectrum_disp = np.arange(wl_start, wl_end + wl_step_size, wl_step_size)

                logger.debug("lens: %i, %i" % (len(spectrum_flux), len(spectrum_disp), ))
                logger.debug("%3.1f %3.1f %3.3f" % (wl_start, wl_end, wl_step_size, ))

                if len(spectrum_flux) > len(spectrum_disp):
                    logger.warn("%i more flux points than dispersion points back from MOOG. MOOG, stahp!" % (len(spectrum_flux) - len(spectrum_disp), ))

                    spectrum_flux = spectrum_flux[:len(spectrum_disp)]

                elif len(spectrum_disp) > len(spectrum_flux):
                    logger.warn("%i more dispersion points than flux points back from MOOG. MOOG, stahp!" % (len(spectrum_disp) - len(spectrum_flux), ))

                    spectrum_disp = spectrum_disp[:len(spectrum_flux)]

                assert len(spectrum_flux) == len(spectrum_disp)

                synthesized_spectra[k] = Spectrum1D(disp=spectrum_disp, flux=spectrum_flux) 
                
                # Get ready for the next one
                k += 1
                spectrum_flux = []

    logger.debug("Abundance requested by MOOG in [%s/Fe] |  Abundance returned by MOOG in log(%s):" % (element, element, ))
    for requested, returned in zip(requested_abundances, returned_abundances):
        logger.debug("\t%1.2f\t\t\t\t%1.2f" % (requested, returned, ))

    assert len(returned_abundances) == len(requested_abundances)

    # Re-arrange spectra and abundances based on increasing abundance
    indices = np.argsort(returned_abundances)

    sorted_returned_abundances = []
    sorted_synthesized_spectra = []

    for index in indices:
        sorted_returned_abundances.append(returned_abundances[index])
        sorted_synthesized_spectra.append(synthesized_spectra[index])

    return (sorted_returned_abundances, sorted_synthesized_spectra)


def abfind(output, line_list, model_atmosphere, **kwargs):
    
    if not os.path.exists(line_list):
        raise IOError('Line list file "%s" does not exist.' % (line_list, ))
    
    if not os.path.exists(model_atmosphere):
        raise IOError('Model atmosphere file "%s" does not exist.' % (model_atmosphere, ))
        
    # prepare the files
    input_filename, standard_out, summary_out = prepare_abfind_file(line_list, model_atmosphere, **kwargs)
    
    # magic
    moog_code, moog_stdout, moog_stderr = run(input_filename)

    if moog_code not in acceptable_moog_return_codes:
        logger.info("MOOG returned the following standard output:")
        logger.info(moog_stdout)
        logger.warn("MOOG returned the following errors (code: {0:d}):".format(moog_code))
        logger.warn(moog_stderr)

        raise MOOGError(moog_stderr)

    else:
        logger.info("MOOG executed {0} successfully".format(input_filename))

    # Check the output
    with open(summary_out, "r") as fp:
        summary = fp.readlines()

    # Just load in all the abundance values, since everything else can be
    # calculated from them
    species = None
    abundances = []
    moog_slopes = {}
    
    # Map (characters are cheap)
    name_map = {
        'ep': 'excitation_potential',
        'rw': 'reduced_ew',
        'wav': 'wavelength'
    }
    
    for line in summary:
        if line.startswith('Abundance Results for Species'):
            
            species = element_to_species(line.split('Species')[1].split('(')[0].strip())
            moog_slopes[species] = {}
            
            if len(abundances) > 0:
                    
                # Check to see if we already have abundances for this species
                exists = np.where(np.array(abundances)[:, 1] == species)
                
                if len(exists[0]) > 0:
                    logger.debug("Detecting more than one iteration from MOOG")
                    abundances = list(delete(abundances, exists, axis=0))
            
        elif re.match("^   [0-9]", line):
            if species is None:
                raise IOError("Could not find the species!")
                
            line = map(float, line.split())
            # Insert transition
            line.insert(1, species)
            abundances.append(line)
        
        elif 'corr. coeff.' in line:
            line = line.split()
            moog_slopes[species][name_map[line[0].replace('.', '').lower()]] = map(float, [value.replace('D-', 'E-') for value in [line[4], line[7], line[11]]])
            
    
    abundances = np.array(abundances, dtype=np.float)
    calculated_distributions, calculated_slopes = calculate_trend_lines(abundances, transition_col=1, x_cols=(2, 5, 0, ), y_col=6)
    
    #logger.info("Calculated slopes: %s" % (calculated_slopes, ))
            
    return_slopes = {}
    for key, value in calculated_slopes.iteritems():
        return_slopes[key] = {
            'excitation_potential': value[0],
            'reduced_ew': value[1],
            'wavelength': value[2]
        }

    # Move the summary and stdout files to their appropriate locales
    os.system('mv %s %s' % (summary_out, output + '.summary', ))
    os.system('mv %s %s' % (standard_out, output + '.stdout', ))
    os.system('rm -f batch.par')
    
    return (abundances, return_slopes)
    
    
def prepare_synth_file(elemental_abundances, \
                       line_list, model_atmosphere, observed=None, isotope_ratios=None, twd=None, **kwargs):
    """Prepares a MOOG-compatible synthesis file.
    
    Inputs
    ----
    abundance_table : float, or list-type of floats
        Either a single abundance (X/Fe) to synthesize, or a list-type of
        abundances to synthesize.
    
    line_list : str
        Line list filename.
        
    model_atmosphere : str
        Model atmosphere filename.
        
    observed : `specutils.Spectrum1D`
        Observed spectrum.
    
    elemental_abundances : `np.array`
        Array containing the elemental abundances, i.e. [C/Fe]. This function
        will determine which elemental abundances are relevant for this synthesis
        and only use those elements. An example of the abundances array:
        
            >> np.array([
                [6,  -0.52],
                [21, -1.20]
            ])
        
        Shows that [C/Fe] = -0.52 and [Sc/Fe] = -1.20.
        
    
    output_prefix : str
        Prefix to apply to all the MOOG output files.
    
    Keyword Arguments
    ----
    Acceptable keyword recommendations are ones that MOOG accepts. For example:
    
    atmosphere, molecules, lines, flux/int, plot, isotopes, synlimits, plotpars
    
    These keywords will be passed directly into the MOOG input file. See
    WRITEMOOG.ps for more information on these keywords. By default the keyword
    inputs are as follows:
    
        >> atmosphere: 1
        >> molecules: 2
        >> lines: 1
        >> flux/int: 0
        >> plot: 2
        >> isotopic_ratios: np.array(
                [[106.00112,  1.25,  1.25,  1.25,  1.25],         
                 [106.00113,     5,     5,     5,     5],                      
                 [606.01212,  1.25,  1.25,  1.25,  1.25],         
                 [606.01213,     5,     5,     5,     5],                     
                 [607.01214,  1.25,  1.25,  1.25,  1.25],         
                 [607.01314,     5,     5,     5,     5],                     
                 [56.1134,   41.24, 41.24, 41.24, 41.24],
                 [56.1135,   15.19, 15.19, 15.19, 15.19],
                 [56.1136,   12.73, 12.73, 12.73, 12.73],
                 [56.1137,    8.92,  8.92,  8.92,  8.92],
                 [56.1138,    1.39,  1.39,  1.39,  1.39]]
             )
    
    Notes
    ----
    By default, synlimits will default to synthesising between the lower and
    upper limit of the wavelength points in the line list. The synthesis step
    size will be the minimum dispersion step in the observed spectrum portion.
    
    By default, plotpars will default to generating all spectra, and plotting
    them between the same limits as synlimits.
    
    Outputs
    ----
    filename : str
        The location of the MOOG-ready input file.
    """
    
    # Get the wavelength range in the line list. We will use this to determine
    # the synthesis regions
    
    if twd is None:
        twd = tempfile.mkstemp()[1]
    
    wlrange = np.abs(np.loadtxt(line_list, usecols=(0, ), skiprows=1, unpack=True, ndmin=1))
    
    if len(wlrange) == 0:
        wlrange = np.loadtxt(line_list, usecols=(0, ), skiprows=0, unpack=True, ndmin=1)
    
    # If there is only one line in the line list
    try:
        wlrange = float(wlrange)

    except TypeError:
        logger.debug("wavelength range looks good")

    else:
        wlrange = [wlrange]
    
    # Let's build the abundances table
    elemental_abundances = np.array(elemental_abundances)

        
    
    # Save observed spectrum portion
    #idx = np.searchsorted(observed.disp, [wlrange[0], wlrange[-1]])
    #data = observed.data[idx[0]:idx[1]]
    #np.savetxt('/tmp/observed', data)
     
    # Keywords which will overwrite
    necessary_kwargs = {
        'standard_out': os.path.join(twd, 'moog.synth.std.out'),
        'summary_out': os.path.join(twd, 'moog.synth.sum.out'),
        'smoothed_out': os.path.join(twd, 'moog.synth.spectra'),
        'model_in': model_atmosphere,
        'lines_in': line_list,
        'abundances': elemental_abundances
    }

    """
    if isotope_ratios is not None and len(isotope_ratios) > 0:

        logger.debug("ISOTOPE RATIOS IS %s" % (isotope_ratios, ))

        isotope_array = []
        for element_key, ratio in isotope_ratios.iteritems():
            if element_key == 'C':
                # C 12/13 ratio
                ratio_b = 1 - 1/ratio

                isotope_array.extend([
                    [106.00112, ratio_b, ratio_b, ratio_b, ratio_b],
                    [106.00113, ratio, ratio, ratio, ratio],
                    [606.01212, ratio_b, ratio_b, ratio_b, ratio_b],
                    [606.01213, ratio, ratio, ratio, ratio],
                    [607.01214, ratio_b, ratio_b, ratio_b, ratio_b],
                    [607.01314, ratio, ratio, ratio, ratio],
                    ])


        necessary_kwargs['isotopes'] = np.array(isotope_array)
    """

    if isotope_ratios is not None:
        logger.debug("Putting isotopes in kwargs")
        
        necessary_kwargs['isotopes'] = np.array(isotope_ratios)

    synthesis_step_size = 0.01 if not 'synthesis_step_size' in kwargs.keys() else kwargs['synthesis_step_size']
    synthesis_pm_range = 1.0 if not 'synthesis_pm_range' in kwargs.keys() else kwargs['synthesis_pm_range']

    logger.debug("synthesis step size is %1.3f" % (synthesis_step_size, ))
    logger.debug("synthesis pm range is %1.3f" % (synthesis_pm_range, ))

    # Default synthesis keywords
    synth_keywords = {
        'terminal':     'x11',
        'atmosphere':   1,
        'molecules':    2,
        'lines':        1,
        'flux/int':     0,
        'plot':         0,
        'synlimits': (np.min(wlrange) - synthesis_pm_range, np.max(wlrange) + synthesis_pm_range, synthesis_step_size, 1.00),
        'plotpars': (1, 
                    np.min(wlrange) - synthesis_pm_range, np.max(wlrange) + synthesis_pm_range, 0, 1.2,
                     0, 0, 0, 1.0,
                     'g', 0.0, 0, 0, 0, 0),
        'obspectrum': 0
    }

    """
    'isotopes':     np.array(
           [[106.00112,  1.05,  1.05,  1.05,  1.05],         
            [106.00113,    20,    20,    20,    20],                      
            [606.01212,  1.05,  1.05,  1.05,  1.05],         
            [606.01213,    20,    20,    20,    20],                     
            [607.01214,  1.05,  1.05,  1.05,  1.05],         
            [607.01314,    20,    20,    20,    20],                     
            [56.1134,   41.24, 41.24, 41.24, 41.24],
            [56.1135,   15.19, 15.19, 15.19, 15.19],
            [56.1136,   12.73, 12.73, 12.73, 12.73],
            [56.1137,    8.92,  8.92,  8.92,  8.92],
            [56.1138,    1.39,  1.39,  1.39,  1.39]]
        ),

    """

    # Update the synth_keywords with any that were explicitly passed through
    synth_keywords.update(kwargs)

    # Update the synth_keywords with necessary keywords
    synth_keywords.update(necessary_kwargs)
    
    # Order of keywords for the output file
    keyword_order = "terminal standard_out summary_out smoothed_out model_in lines_in observed_in atmosphere molecules lines flux/int plot isotopes abundances synlimits plotpars obspectrum".split()
    
    output_str = "synth\n"
    
    for keyword in keyword_order:
        if keyword not in synth_keywords:
            logger.warn("Wanted keyword %s but couldn't find it in synth_keywords" % (keyword, ))
            continue
        
        value = synth_keywords[keyword]
        sp = ' ' * (14 - len(keyword))
        
        # Special formatting
        if keyword in ('isotopes', 'abundances', ):

            logger.debug("value = %s, %s" % (type(value), value, ))
            # Skip to the next keyword if there's nothing here for us.
            if 1 > len(value): continue

            try:
                assert isinstance(value, np.ndarray)
            except AssertionError:
                print keyword
                print value

            shape = value.shape
            if len(shape) == 1:
                shape = (1, len(value))
                value = [value]
                
            # We want the second column to read N of different abundances, not
            # specifically the shape of the array
            value_str = "%s %i   %i\n" % (keyword + sp, shape[0], shape[1] - 1, )

            if keyword == 'abundances':
                # Replace nan's
                print "abundance values were ", value
                value[:, 1:][~np.isfinite(value[:, 1:])] = -9.0
                print "abundance values are ", value
                value_str += "\n".join(["       %i    %s" % (line[0], "    ".join(['%1.2f' % (v, ) for v in line[1:]]), ) for line in value])

            else:
                # Isotopes need more precision than abundances
                logger.debug("Isotope precision values")
                logger.debug(value)
                value_str += "\n".join(["       %1.5f    %s" % (line[0], "    ".join(map(str, line[1:])), ) for line in value])

        elif keyword == 'synlimits':
            assert isinstance(value, (tuple, list, np.ndarray))
            assert len(value) == 4

            # If we specified a +/- synthesis region, we probably want some precision:
            if 'synthesis_pm_range' in kwargs.keys():
                value_str = keyword + "\n %4.3f %4.3f %5.4f %5.2f" % tuple(value)
            
            else:
                value_str = keyword + "\n %4.1f  %4.1f %5.4f %5.2f" % tuple(value)

        
        elif keyword == 'plotpars':
            assert isinstance(value, (tuple, list, np.ndarray))
            assert len(value) == 15
            value_str = keyword + sp + " %i\n  %4.1f  %4.1f    %1.2f    %1.2f\n  %4.1f  %4.1f    %1.2f    %1.2f\n%s    %1.2f    %1.2f    %1.2f    %1.2f    %1.2f" % tuple(value)
        
        elif keyword in ('terminal', 'standard_out', 'summary_out', 'smoothed_out', 'model_in', 'lines_in'):
            value_str = "%s '%s'" % (keyword + sp, value, )
            
        else:
            value_str = "%s %s" % (keyword + sp, value, )
            
        output_str += "%s\n" % (value_str, )
    
    
    output_filename = os.path.join(twd, 'moog.synth.in')
    logger.debug("Input MOOG synth file is %s" % (output_filename, ))

    with open(output_filename, 'w') as fp:
        fp.write(output_str)
        
    return output_filename


def abundance_differences(composition_a, composition_b):
    """Returns a key containing the abundance differences for elements that are
    common to `composition_a` and `composition_b`. This is particularly handy
    when scaling from one Solar composition to another.

    Inputs
    ----
    composition_a : `dict`
        The initial composition where elements are represented as keys and the
        abundances are inputted as values. The keys are agnostic (strings, floats,
        ints), as long as they have the same structure as composition_b.

    composition_b : `dict`
        The second composition to compare to. This should have the same format
        as composition_a

    Returns
    ----
    scaled_composition : `dict`
        A scaled composition dictionary for elements that are common to both
        input compositions."""


    if not isinstance(composition_a, dict) or not isinstance(composition_b, dict):
        raise TypeError("Chemical compositions must be dictionary types")

    common_elements = set(composition_a.keys()).intersection(composition_b.keys())

    scaled_composition = {}
    for element in common_elements:
        if np.abs(composition_a[element] - composition_b[element]) >= 1e-2:
            scaled_composition[element] = composition_a[element] - composition_b[element]

    return scaled_composition




def prepare_abfind_file(line_list_filename, model_atmosphere_filename, twd=None,
                        atmosphere=1, molecules=2, lines=1, freeform=0, fluxint=0,
                        damping=1, plot=0):
    """Returns the location of a temporary file which has been prepared for
    MOOG to run abfind.
    
    Inputs
    ------
    
    line_list           : Location of the input line list with measured equivalent widths.
    model_atmosphere    : Location of the model atmosphere filename.
    atmosphere          : Refer to WRITEMOOG.ps
    model               : Refer to WRITEMOOG.ps
    lines               : Refer to WRITEMOOG.ps
    freeform            : Refer to WRITEMOOG.ps
    fluxint             : Refer to WRITEMOOG.ps
    damping             : Refer to WRITEMOOG.ps
    plot                : Refer to WRITEMOOG.ps
    
    Outputs
    -------
    
    moog_input_file     : Location of the prepared input file for MOOG.
    moog_standard_out   : Where MOOG will output the standard output (temporary filepath)
    moog_summary_out    : Where MOOG will output the summary output (temporary filepath)
    """
    
    if not os.path.exists(line_list_filename):
        raise IOError('Line list file "%s" does not exist.' % (line_list_filename, ))
        
    if not os.path.exists(model_atmosphere_filename):
        raise IOError('Model atmosphere file "%s" does not exist.' % (model_atmosphere_filename, ))
    
    if twd is None:
        twd = tempfile.mkstemp()[1]
    
    # MOOG has a maximum filename length that it can handle
    max_filename_length = 40
    
    # Copy files to twd if necessary
    if len(line_list_filename) > max_filename_length:
        line_list_filename_temp = os.path.join(twd, os.path.basename(line_list_filename))
        # TODO what if len(basename) > max_filename_length
        if line_list_filename != line_list_filename_temp:
            try:
                shutil.copyfile(line_list_filename, line_list_filename_temp)

            except shutil.Error as reason:
                logger.warn("Error when copying file '%s' to '%s': %s" % (line_list_filename, line_list_filename_temp, reason))
            
    else: line_list_filename_temp = line_list_filename
    
    if len(model_atmosphere_filename) > max_filename_length:
        model_atmosphere_filename_temp = os.path.join(twd, os.path.basename(model_atmosphere_filename))
        
        if model_atmosphere_filename != model_atmosphere_filename_temp:
            try:
                shutil.copyfile(model_atmosphere_filename, model_atmosphere_filename_temp)

            except shutil.Error as reason:
                logger.warn("Error when copying file '%s' to '%s': %s" % (line_list_filename, line_list_filename_temp, reason, ))
    
    else: model_atmosphere_filename_temp = model_atmosphere_filename
    
            
    # We need short, temporary files for MOOG
    moog_input_file = os.path.join(twd, 'moog.abfind.in')
    moog_standard_out = os.path.join(twd, 'moog.abfind.std.out')
    moog_summary_out = os.path.join(twd, 'moog.abfind.sum.out')
    
    moog_output = """
    abfind
    terminal 'x11'
    standard_out '%s'
    summary_out '%s'
    model_in '%s'
    lines_in '%s'
    atmosphere %i
    molecules %i
    lines %i
    freeform %i
    flux/int %i
    damping %i
    plot %i
    """ % (moog_standard_out, moog_summary_out, model_atmosphere_filename_temp, line_list_filename_temp, \
           atmosphere, molecules, lines, freeform, fluxint, damping, plot, )
    
    with open(moog_input_file, 'w') as fp:
        fp.write(dedent(moog_output).lstrip())
    
    return (moog_input_file, moog_standard_out, moog_summary_out, )
    
   
