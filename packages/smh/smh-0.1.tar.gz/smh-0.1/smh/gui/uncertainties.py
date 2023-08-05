# coding: utf-8

""" Uncertainty analysis for stellar parameters and chemical abundances """

__author__ = "Andy Casey <acasey@mso.anu.edu.au>"

__all__ = ["ChemicalAbundanceUncertainties"]

# Module imports
from ..core import *
from .. import atmospheres

# GUI module specific imports
from gui_core import *

class AbundanceRatioUncertainty(HasTraits):
    
    species = Float
    element = Property(depends_on="species")
    X_on_H = Float

    uncertainty_from_teff = Float(0.0)
    uncertainty_from_logg = Float(0.0)
    uncertainty_from_vt = Float(0.0)
    uncertainty_from_feh = Float(0.0)
    SEM = Float(0.0) # Standard error about the mean

    total_uncertainty = Property(depends_on=[
        "uncertainty_from_teff",
        "uncertainty_from_logg",
        "uncertainty_from_vt",
        "uncertainty_from_feh",
        "SEM"
        ])

    def _get_element(self):
        """ Update the element based on the species. """
        return species_to_element(self.species)
        
    def _get_total_uncertainty(self):
        """ Update the total uncertainty by adding all uncertainties in quadrature. """

        uncertainties = np.array([
            self.uncertainty_from_teff,
            self.uncertainty_from_logg,
            self.uncertainty_from_vt,
            self.uncertainty_from_feh,
            self.SEM
        ])
        finite_uncertainties = np.isfinite(uncertainties)

        return np.sum(uncertainties[finite_uncertainties]**2)**0.5


class ChemicalAbundanceUncertaintiesHandler(Handler):

    def export(self, info):
        """Export the chemical abundance uncertainties to an external file."""

        dialog = FileDialog(action="save as", wildcard='*.csv', title='Export Uncertainties Table')
        dialog.open()

        if dialog.return_code == OK:

            # TODO - This should all go somehwere else and the GUI should just be calling some method.

            filename = os.path.join(dialog.directory, dialog.filename)
            if not filename.endswith('.csv'): filename += '.csv'

            logger.debug("Exporting abundance uncertainties table to %s.." % (filename, ))

            all_contents = "\n"
            with open(filename, 'w') as fp:

                # Write the header
                header = "# Element, Delta(Teff=%+i), Delta(logg=%+1.2f), Delta(vt=%+1.2f), Delta([M/H]=%+1.2f), S.E.M., Total\n" \
                    % (info.object.teff_offset, info.object.logg_offset, info.object.vt_offset, info.object.m_h_offset, )
                
                all_contents += header
                for abundance in info.object.abundance_uncertainties:
                    element = "[%s/H]" % (abundance.element, )
                    line = "%9s,%+17.2f,%+18.2f,%+16.2f,%+19.2f,%7.2f,%6.2f\n" \
                        % (element, abundance.uncertainty_from_teff, abundance.uncertainty_from_logg, abundance.uncertainty_from_vt, abundance.uncertainty_from_feh, abundance.SEM, abundance.total_uncertainty, )
                    all_contents += line
                
                all_contents = all_contents.rstrip("\n")
                fp.write(all_contents)

            logger.info(all_contents)
            logger.info("Saved abundance uncertainties table above to %s" % (filename, ))


    def save_to_session(self, info):
        """Save the current uncertainties in abundance ratios due to atmospheric
        parameters into the session file."""

        logger.warn("This feature isn't implemented yet. Sorry about that. But, you can export the uncertainties to a table instead.")
        raise NotImplementedError


    def close_gui(self, info):
        info.ui.owner.close()


class ChemicalAbundanceUncertainties(HasTraits):
    """ GUI dialog for displaying the uncertainties in chemical abundance ratios """

    teff_offset = Float(150)
    logg_offset = Float(0.3)
    vt_offset = Float(0.2)
    m_h_offset = Float(0.2)

    labels = Str(" ")
    teff_unit = Str("K")
    logg_unit = Str("dex")
    vt_unit = Str("km/s")
    m_h_unit = Str("dex")

    inputs_match_output = Bool(True)
    calculate_abundance_uncertainties = Button("Calculate Abundance Uncertainties")

    abundance_uncertainties = List(AbundanceRatioUncertainty)

    abundance_uncertainties_editor = TableEditor(
        columns = [
            ObjectColumn(name="element", label="Species", editable=False, format="[%s/H]", width=-80),
            NumericColumn(name="uncertainty_from_teff", label=u"ΔTeff", editable=False, format="%+1.2f", width=-40),
            NumericColumn(name="uncertainty_from_logg", label=u"Δlog(g)", editable=False, format="%+1.2f", width=-40),
            NumericColumn(name="uncertainty_from_vt", label=u"Δξ", editable=False, format="%+1.2f", width=-40),
            NumericColumn(name="uncertainty_from_feh", label=u"Δ[M/H]", editable=False, format="%+1.2f", width=-40),
            NumericColumn(name="SEM", label=u"σ/(√n)", editable=False, format="%1.2f", width=-40),
            NumericColumn(name="total_uncertainty", label="Total", editable=False, format="%1.2f", width=-40)
        ],
        auto_size          = False,
        sortable           = True,
        sort_model         = True,
        show_lines         = True,        
        orientation        = "vertical",
        show_column_labels = True,        
    )

    view = View(
        [
            HGroup(
                Item("labels", style="readonly", label=u"Temperature uncertainty, ΔTeff:", padding=5),
                spring,
                Item("teff_offset", width=-50, show_label=False, padding=5, format_str="%+i"),
                Item("teff_unit", style="readonly", show_label=False, width=-40)
            ),
            HGroup(
                Item("labels", style="readonly", label=u"Surface gravity uncertainty, Δlog(g):", padding=5),
                spring,
                Item("logg_offset", width=-50, show_label=False, padding=5, format_str="%+1.2f"),
                Item("logg_unit", style="readonly", show_label=False, width=-40)
            ),
            HGroup(
                Item("labels", style="readonly", label=u"Microturbulence uncertainty, Δξ:", padding=5),
                spring,
                Item("vt_offset", width=-50, show_label=False, padding=5, format_str="%+1.2f"),
                Item("vt_unit", style="readonly", show_label=False, width=-40)
            ),
            HGroup(
                Item("labels", style="readonly", label=u"Metallicity uncertainty, Δ[M/H]:", padding=5),
                spring,
                Item("m_h_offset", width=-50, show_label=False, padding=5, format_str="%+1.2f"),
                Item("m_h_unit", style="readonly", show_label=False, width=-40)
            ),
            HGroup(
                spring,
                Item("calculate_abundance_uncertainties", show_label=False),
                spring,
                ),
            "5",
            Group(Item("abundance_uncertainties", id="abundance_uncertainties", editor=abundance_uncertainties_editor, show_label=False)),
        ],
        title="Abundance Uncertainties Due to Atmospheric Parameters",
        handler=ChemicalAbundanceUncertaintiesHandler(),
        buttons=[
            Action(name="Export..", action="export", enabled_when="len(abundance_uncertainties) > 0 and inputs_match_output"),
            Action(name="Save to session", action="save_to_session", enabled_when="False and len(abundance_uncertainties) > 0 and inputs_match_output"),
            Action(name="Close", action="close_gui")
            ],
        dock="horizontal",
        width=600,
        height=700,
        resizable=True,

    )

    @on_trait_change("teff_offset,logg_offset,vt_offset,m_h_offset")
    def _forbid_export_without_remoog(self):
        """ The input parameters have changed, but some abundance table is there. """
        self.inputs_match_output = False


    def _calculate_abundance_uncertainties_fired(self):
        """Calculate the abundance uncertainties by varying the stellar parameters
        to the level requested and seeing how the final abundances change."""

        logger.info("Calculating abundance uncertainties due to atmospheric parameters")

        # TODO this functionality should go into session.uncertainties.chemical_abundances()

        # TODO check to see if any of these offsets have changed? 
        parameters_to_vary = {
            "stellar_teff" : self.teff_offset,
            "stellar_logg" : self.logg_offset,
            "stellar_vt"   : self.vt_offset,
            "stellar_feh"  : self.m_h_offset
        }

        # Check for non-zero values 
        for parameter in parameters_to_vary.keys():
            if parameters_to_vary[parameter] == 0:
                del parameters_to_vary[parameter]

        logger.info("Independently varying these parameters:")
        logger.info(parameters_to_vary)

        # Fill up the table with empty values so that we can fill up as we go?

        # Check to see what lines we should be measuring
        unique_species = []
        lines_to_measure_abundances_for = []
        for measurement in self.session.measurements:  
            if measurement.transition in self.initial_abundances.keys() \
            and measurement.is_acceptable and measurement.measured_equivalent_width > 0:
                lines_to_measure_abundances_for.append(measurement)
                unique_species.append(measurement.transition) # TODO -> should really switch "transition" to 'species' in core.py

        # Remove duplicate elements
        unique_species = list(set(unique_species))

        # Are there actually any lines we should be measuring?
        if len(lines_to_measure_abundances_for) is 0: 
            logger.warn("No uncertainty analysis has been performed because no acceptable measurements were found with positive equivalent widths.")
            return False

        if len(parameters_to_vary) > 0:

            # Prepare MOOG files
            equivalent_widths_filename = os.path.join(self.session.twd, 'atmosphere_uncertainties.ew')
            moog_output_prefix = os.path.join(self.session.twd, 'moog_uncertainties.out')    
            moog.io.write_equivalent_widths(lines_to_measure_abundances_for, equivalent_widths_filename, force_loggf=True, clobber=True)
        
            # Prepare model atmosphere interpolator
            model_atmosphere_for_uncertainties_filename = self.session.stellar_atmosphere_filename + '_uncertainty'
            model_atmosphere_folder, model_atmosphere_parser = atmospheres.parsers[self.session.stellar_atmosphere_type]
        
            # Model atmosphere folder is relative to SMH
            logger.info("Using %s atmospheres: %s in '%s'" % (self.session.stellar_atmosphere_type, model_atmosphere_parser, model_atmosphere_folder, ))
            logger.info("Model atmosphere filename for uncertainties will be %s" % (model_atmosphere_for_uncertainties_filename, ))

            # Load the solar composition
            solar_abundances = json.load(open(os.path.join(os.path.dirname(__file__), '../config/solar_abundances.json'), 'r'))
            
            # Initiate the interpolator
            interpolator = atmospheres.AtmosphereInterpolator(model_atmosphere_folder, model_atmosphere_parser())
            
            # Remember the model atmosphere parameters
            original_parameters = {
                "stellar_teff"  : self.session.stellar_teff,
                "stellar_logg"  : self.session.stellar_logg,
                "stellar_feh"   : self.session.stellar_feh,
                "stellar_vt"    : self.session.stellar_vt,
                "stellar_alpha" : self.session.stellar_alpha
            }

        # Prepare the results dictionary
        #resultant_uncertainties[26.0]["uncertainty_from_teff"]
        resultant_uncertainties = {}
        for unique_species in unique_species:
            resultant_uncertainties[unique_species] = {}

        # Start varying the model atmosphere parameters
        for parameter, parameter_uncertainty in parameters_to_vary.iteritems():

            original_value = original_parameters[parameter]

            logger.debug(u"Varying %s from %1.2f to %1.2f (Δ%s = %1.2f)" \
                % (parameter, original_value, original_value + parameter_uncertainty, parameter.split('_')[1], parameter_uncertainty))

            # We need to scale the abundance differences from MOOG's internal default solar
            # composition by Anders & Grevesse et al (1989), to the Asplund et al. (2009)
            # solar composition.
            formatted_abundances = {}
            for element, (abundance, uncertainty, meteroitic) in solar_abundances.iteritems():
                if element == "H": continue
                formatted_abundances[element] = abundance + self.session.stellar_feh

                if parameter == "stellar_feh":
                    formatted_abundances[element] += parameter_uncertainty

            # Copy the original model atmosphere
            current_parameters = original_parameters.copy()

            # Vary the parameter
            current_parameters[parameter] += parameter_uncertainty
            logger.info("Current model atmosphere for uncertainty analysis: %s" % (current_parameters))

            # Create a model atmosphere
            interpolator.interpolate(model_atmosphere_for_uncertainties_filename,
                current_parameters["stellar_teff"], current_parameters["stellar_logg"],
                current_parameters["stellar_feh"], current_parameters["stellar_alpha"],
                current_parameters["stellar_vt"], solar_abundances=formatted_abundances)

            # Run MOOG abfind routine
            atomic_transitions, slopes = moog.abfind(moog_output_prefix,
                                                     equivalent_widths_filename,
                                                     model_atmosphere_for_uncertainties_filename,
                                                     twd=self.session.twd)
        
            assert len(atomic_transitions) == len(lines_to_measure_abundances_for)
            
            # Set up some column index references
            col_wl, col_species, col_ep, col_loggf, col_ew, col_logrw, col_abund, col_del_avg, col_idx_match = xrange(9)
            
            # Go through each line abundance
            abundances_in_each_species = {}
            for i, atomic_transition in enumerate(atomic_transitions):

                rest_wavelength, species, abundance = atomic_transition[[col_wl, col_species, col_abund]]
                
                if not np.isfinite(abundance):
                    logger.warn("Skipping over species %s at wavelength %1.2f because the abundance returned was non-finite." \
                        % (abundance, rest_wavelength, ))

                # If we haven't seen this species before, create a list
                if species not in abundances_in_each_species.keys():
                    abundances_in_each_species[species] = []

                # Add this abundance to the rest for this species
                abundances_in_each_species[species].append(abundance)

            # Calculate mean abundances and save their results
            short_parameter_name = parameter[8:]    # This just converts "stellar_logg" -> "logg" for resultant_uncertainties

            for species, abundances in abundances_in_each_species.iteritems():
                resultant_uncertainties[species]["uncertainty_from_"+short_parameter_name] = np.mean(abundances) - self.initial_abundances[species]["mean"]

        # Use resultant_uncertainties dictionary to build the table
        logger.debug("Building uncertainty table...")

        # Sort elements by atomic number first.
        sorted_species = resultant_uncertainties.keys()
        sorted_species.sort()

        results = []
        for species in sorted_species:
            uncertainties = resultant_uncertainties[species]

            abundance_uncertainty = AbundanceRatioUncertainty(
                species=species,
                SEM=self.initial_abundances[species]["SEM"],
                **uncertainties)
            results.append(abundance_uncertainty)

        # Now update the GUI.
        self.inputs_match_output = True
        self.abundance_uncertainties = results
        logger.debug("Abundance uncertainties GUI")
            

