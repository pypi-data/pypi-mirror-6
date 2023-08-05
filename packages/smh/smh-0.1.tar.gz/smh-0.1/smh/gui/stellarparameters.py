# coding: utf-8

""" Contains code required for the stellar parameters tab in Spectroscopy Made Hard GUI """

__author__ = "Andy Casey <andy@astrowizici.st>"

__all__ = ["StellarParametersTab"]

from tempfile import mkdtemp

# Third party
from scipy.optimize import fmin

# Module specific
from ..core import *
from ..session import Session
from ..utils import extend_limits, species_to_element
from .. import atmospheres, moog

# GUI module specific
from gui_core import *

class ExcitationIonizationEqualibriaHandler(Handler):
    """ Handler to deal with the Excitation & Ionization Equalibria
    dialog """

    def perform_equalibria(self, info):
        """ Trigger the excitation and ionization equilibria """

        if info.object.initial_point == "Current point":
            p0 = [
                info.object.session.stellar_teff,
                info.object.session.stellar_vt,
                info.object.session.stellar_logg,
                info.object.session.stellar_feh
            ]

        else:
            p0 = None

        outlier_limits = {}
        if np.isfinite(info.object.fe_I_outlier_sigma):
            outlier_limits[26.0] = info.object.fe_I_outlier_sigma

        if np.isfinite(info.object.fe_II_outlier_sigma):
            outlier_limits[26.1] = info.object.fe_II_outlier_sigma


        results = info.object.session.solve_stellar_parameters(initial_guess=p0,
            total_tolerance=info.object.tolerance, max_attempts=info.object.max_attempts,
            individual_tolerances=info.object.individual_tolerances, outlier_rejection_total_tolerance=info.object.outlier_rejection_total_tolerance,
            outlier_limits=outlier_limits)
       
        logger.debug("Results from automatic excitation and ionization equalibria are as follows:")
        logger.debug(results)

        if results[0]:
            logger.info("Automatic excitation and ionization equalibria completed successfully. Previous stellar"
                " parameters:\n\tTeff = {0:.0f}, vt = {1:.2f}, logg = {2:.2f}, [Fe/H] = {3:.2f}".format(
                    info.object.session.stellar_teff, info.object.session.stellar_vt, info.object.session.stellar_logg,
                    info.object.session.stellar_feh))

            info.object.session.stellar_teff = int(results[5][0])
            info.object.session.stellar_vt, info.object.session.stellar_logg, info.object.session.stellar_feh = map(float, results[5][1:])

            logger.info("New stellar parameters:\n\tTeff = {0:.0f}, vt = {1:.2f}, logg = {2:.2f}, [Fe/H] = {3:.2f}"
                .format(info.object.session.stellar_teff, info.object.session.stellar_vt, info.object.session.stellar_logg,
                    info.object.session.stellar_feh))

            # Trigger an abundance fire to ensure everything is up to date
            info.object.successful_callback(None)

        else:
            logger.warn("Automatic excitation and ionization equalibria did not reach required tolerance!")
        info.ui.owner.close()

    def cancel(self, info):
        info.ui.owner.close()


class ExcitationIonizationEqualibriaDialog(HasTraits):
    """ A configurable GUI to control the settings for performing
    excitation and ionization equilibria """

    initial_point = Enum("Current point", "Random point")
    tolerance = Float(4e-6)
    max_attempts = Int(5)

    doing_things = Bool(False)

    individual_tolerances = List([1e-3, 1e-3, 1e-3, 1e-3])
    outlier_rejection_total_tolerance = Float(1e-4)
    fe_I_outlier_sigma = Float(2)
    fe_II_outlier_sigma = Float(np.nan)

    outlier_rejection_title = Str("Outlier rejection options")
    individual_tolerances_title = Str("Individual Tolerances")
    perform = Button("Perform equilibria")

    blank = Str(" ")
    view = View(
        VGroup(
            HGroup(
                Item("blank", label="Initial stellar parameters", style="readonly", padding=5),
                spring,
                Item("initial_point", show_label=False, padding=5, enabled_when="not doing_things")),
            HGroup(
                Item("blank", label="Acceptable total tolerance", style="readonly", padding=5),
                spring,
                Item("tolerance", show_label=False, format_str="%1.1e", enabled_when="not doing_things", width=-60, padding=5)),
            HGroup(
                Item("blank", label="Maximum number of attempts", style="readonly", padding=5),
                spring,
                Item("max_attempts", show_label=False, format_str="%1.0f", width=-30, enabled_when="not doing_things", padding=5)),
            HGroup(
                Item("individual_tolerances_title",
                     show_label = False,
                     springy    = True,
                     editor     = TitleEditor(),
                     padding    = 0
                    )),
            HGroup(
                Item("individual_tolerances", label="Tolerances (dA/dChi, dA/dREW, <Fe I> - <Fe II>, <Fe I> - [M/H])", padding=5),
                spring,
                ),
            HGroup(
                Item("outlier_rejection_title", show_label=False, springy=True, editor=TitleEditor(), padding=0)),
            HGroup(
                Item("outlier_rejection_total_tolerance", label="Acceptable tolerance for outlier rejection", padding=5),
                spring
                ),
            HGroup(
                Item("fe_I_outlier_sigma", label="Fe I clip", padding=5),
                Item("fe_II_outlier_sigma", label="Fe II clip", padding=5)
                )
            ),
        width=400,
        handler = ExcitationIonizationEqualibriaHandler(),
        buttons = [
            Action(name="Perform excitation-ionization equalibria", action="perform_equalibria", enabled_when="not doing_things"),
            Action(name="Cancel", action="cancel", enabled_when="not doing_things")
            ],
        title="Perform Excitation and Ionization Equalibria"
        )

    def __init__(self, session, successful_callback):
        self.session = session
        self.successful_callback = successful_callback


def calculate_stellar_slope(parameter_value, parameter_name, equivalent_widths_filename, session):
    logger.debug("Calculating slope for %s = %s" % (parameter_name, parameter_value, ))

    # Generate a model atmosphere    
    moog_output_prefix = os.path.join(session.twd, 'stellar_uncertainty.out')
    temporary_model_atmosphere_filename = os.path.join(session.twd, "temp_stellar_atmosphere.model")
    model_atmosphere_folder, model_atmosphere_parser = atmospheres.parsers[session.stellar_atmosphere_type]

    # We need to scale the abundance differences from MOOG's internal default solar
    # composition by Anders & Grevesse et al (1989), to the Asplund et al. (2009)
    # solar composition.

    formatted_abundances = {}
    for element, (abundance, uncertainty, meteroitic) in solar_abundances.iteritems():
        if element == "H": continue
        formatted_abundances[element] = abundance + session.stellar_feh

    interpolator = atmospheres.AtmosphereInterpolator(model_atmosphere_folder, model_atmosphere_parser())
    interpolator_inputs = {
        "filename"    : temporary_model_atmosphere_filename,
        "teff"      : session.stellar_teff,
        "logg"      : session.stellar_logg,
        "fe_h"     : session.stellar_feh,
        "alpha_fe" : session.stellar_alpha,
        "xi"        : session.stellar_vt,
        "solar_abundances": formatted_abundances,
        "clobber": True
    }

    # Update interpolator inputs with whatever this one is
    interpolator_inputs[parameter_name] = parameter_value[0]

    # Interpolate with these parameters
    interpolator.interpolate(**interpolator_inputs)
    
    # Run MOOG abfind routine
    abundances, moog_slopes = moog.abfind(moog_output_prefix, os.path.join(session.twd, equivalent_widths_filename),
        temporary_model_atmosphere_filename, twd=session.twd)

    # We will want to calculate our own slopes, since MOOG output precision is limited
    col_wl, col_transition, col_ep, col_loggf, col_ew, col_logrw, col_abund, col_del_avg = xrange(8)
    distributions, calculated_slopes = moog.calculate_trend_lines(abundances, 
        transition_col=col_transition, x_cols=(col_ep, col_logrw), y_col=col_abund)

    logger.debug("For %s = %s returning %s" % (parameter_name, parameter_value, calculated_slopes, ))
    logger.debug("{0} = {1}: {2}".format(parameter_name, parameter_value, calculated_slopes[np.min(calculated_slopes.keys())][0][0]))
    
    return calculated_slopes


def calculate_mean_differences(parameter_value, parameter_name, equivalent_widths_filename, session):
    logger.debug("Calculating mean differences for %s = %s" % (parameter_name, parameter_value, ))
    moog_output_prefix = os.path.join(session.twd, 'stellar_uncertainty.out')

    # Generate a model atmosphere    
    model_atmosphere_folder, model_atmosphere_parser = atmospheres.parsers[session.stellar_atmosphere_type]
    #output, teff, logg, feh, alpha, vt, solar_abundances=None, molecules=None
    # Model atmosphere folder is relative to SMH
    
    # We need to scale the abundance differences from MOOG's internal default solar
    # composition by Anders & Grevesse et al (1989), to the Asplund et al. (2009)
    # solar composition.

    formatted_abundances = {}
    for element, (abundance, uncertainty, meteroitic) in solar_abundances.iteritems():
        if element == "H": continue
        formatted_abundances[element] = abundance + session.stellar_feh

    interpolator = atmospheres.AtmosphereInterpolator(model_atmosphere_folder, model_atmosphere_parser())
    interpolator_inputs = {
        "filename"    : moog_output_prefix,
        "teff"      : session.stellar_teff,
        "logg"      : session.stellar_logg,
        "fe_h"       : session.stellar_feh,
        "alpha_fe"     : session.stellar_alpha,
        "xi"        : session.stellar_vt,
        "solar_abundances": formatted_abundances,
        "clobber": True
    }

    # Update interpolator inputs with whatever this one is
    interpolator_inputs[parameter_name] = parameter_value[0]

    # Interpolate with these parameters
    interpolator.interpolate(**interpolator_inputs)
    
    # Run MOOG abfind routine
    abundances, slopes = moog.abfind(moog_output_prefix, equivalent_widths_filename,
        session.stellar_atmosphere_filename, twd=session.twd)

    # Calculate the mean abundances then get a difference
    col_wl, col_transition, col_ep, col_loggf, col_ew, col_logrw, col_abund, col_del_avg, col_idx_match = xrange(9)

    # Make sure we only have two transitions here!
    unique_transitions = np.unique(abundances[:, col_transition])
    assert len(unique_transitions) == 2

    idx_1 = np.where(abundances[:, col_transition] == unique_transitions[0])[0]
    idx_2 = np.where(abundances[:, col_transition] == unique_transitions[1])[0]

    mean_abundance_1 = np.mean(abundances[idx_1, col_abund])
    mean_abundance_2 = np.mean(abundances[idx_2, col_abund])

    logger.debug("Mean abundances are %1.2f and %1.2f" % (mean_abundance_1, mean_abundance_2, ))

    mean_difference = mean_abundance_1 - mean_abundance_2

    logger.debug("For %s = %s returning %s" % (parameter_name, parameter_value, mean_difference))

    return mean_difference


class StellarParametersTab(HasTraits):
    """This class contains the model and view information for the determination
    of stellar parameters."""

    # Initiate session
    session = Instance(Session)
    
    title = Str('Determine Stellar Parameters')

    update_measurements = Bool(True)
    measurement_filter = Property

    line_measurements_editor = TableEditor(
        columns = [
            ObjectColumn(name='is_blank', label=' ', width=20),
            CheckboxColumn(name='is_acceptable', label=' ', width=20),
            NumericColumn(name='rest_wavelength', label='Wavelength',
                editable=False, format='%4.3f'),
            ObjectColumn(name='element', label='Species',
                editable=False),  
            NumericColumn(name='excitation_potential', label='EP',
                editable=False, format='%1.3f'),
            NumericColumn(name='reduced_equivalent_width', label='REW',
                editable=False, format='%1.2f'),
            NumericColumn(name='abundance', label=u'logε(X)',
                editable=False, format='%1.2f'),
            NumericColumn(name='delta_abundance', label=u'∂(logε(X))',
                          editable=False, format='%+1.2f'),    
        ],
        other_columns = [
            NumericColumn(name='measured_equivalent_width', label='EW',
                editable=False, format='%1.2f'),
        ],
        edit_view_width=400,
        auto_size = False,
        auto_add = False,
        editable = False,
        sortable = True,
        configurable = True,
        orientation = 'vertical',
        selected = 'selected',
        selection_mode = 'rows',
        show_column_labels = True,
        show_toolbar = True,
        reorderable = False,
        filter_name = 'measurement_filter'
        )


    selected = List(AtomicTransition)

    # Delegates to session
    twd = DelegatesTo("session")
    measurements = DelegatesTo('session')
    stellar_teff = DelegatesTo('session')
    stellar_teff_uncertainty = DelegatesTo('session')
    stellar_logg = DelegatesTo('session')
    stellar_logg_uncertainty = DelegatesTo('session')
    stellar_feh = DelegatesTo('session')
    stellar_feh_uncertainty = DelegatesTo('session')
    stellar_alpha = DelegatesTo('session')
    stellar_vt = DelegatesTo('session')
    stellar_vt_uncertainty = DelegatesTo('session')
    stellar_reference_fe_h = DelegatesTo('session')

    stellar_teff_text = DelegatesTo('session')
    
    stellar_atmosphere_type = DelegatesTo('session')
    stellar_atmosphere_filename = DelegatesTo('session')

    using_imported_atmosphere = DelegatesTo('session')



    # Plot displays
    display_trends = Instance(Figure)
    
    rest_spectrum = DelegatesTo('session')

    teff_units = Str('K')
    vt_units = Str('km/s')
    logg_units = Str('dex')
    feh_units = Str('dex')

    # Buttons
    blank = Str(' ')
    abfind = Button("Measure Abundances")
    uncertainty_analysis = Button("Calculate Uncertainties")
    solve_stellar = Button("Perform Equalibria..")
    
    traits_view = View(
        HGroup(
            VGroup(
                Item('title',
                    show_label = False,
                    springy    = True,
                    editor     = TitleEditor()
                    ),
                HGroup(
                    Item('blank', style='readonly', label='Stellar atmosphere models'),
                    spring,
                    Item('stellar_atmosphere_type', show_label=False)
                    ),
                HGroup(
                    Item('blank', style='readonly', label='Temperature, Teff'),
                    spring,
                    Item('stellar_teff', width=-45, padding=5, show_label=False, format_str='%i', enabled_when='not using_imported_atmosphere'),
                    Item('stellar_teff_uncertainty', width=45, style='readonly', format_str=u'± %i', show_label=False, visible_when='stellar_teff_uncertainty > 0 or stellar_vt_uncertainty > 0'),
                    Item('teff_units', width=40, padding=5, style='readonly', show_label=False),
                    
                    ),
                HGroup(
                    Item('blank', style='readonly', label=u'Microturbulence, ξ'),
                    spring,
                    Item('stellar_vt', width=-45, padding=5, show_label=False, format_str='%1.2f', enabled_when='not using_imported_atmosphere'),
                    Item('stellar_vt_uncertainty', width=45, style='readonly', format_str=u'± %1.2f', show_label=False, visible_when='stellar_teff_uncertainty > 0 or stellar_vt_uncertainty > 0'),
                    Item('vt_units', width=40, padding=5, style='readonly', show_label=False),
                    
                ),
                HGroup(
                    Item('blank', style='readonly', label='Surface gravity, log(g)'),
                    spring,
                    Item('stellar_logg', width=-45, padding=5, show_label=False, format_str='%1.2f', enabled_when='not using_imported_atmosphere'),
                    Item('stellar_logg_uncertainty', width=45, style='readonly', format_str=u'± %1.2f', show_label=False, visible_when='stellar_teff_uncertainty > 0 or stellar_vt_uncertainty > 0'),
                    Item('logg_units', width=40, padding=5, style='readonly', show_label=False),
                    
                ),
                HGroup(
                    Item('blank', style='readonly', label='Metallicity, [M/H]'),
                    spring,
                    Item('stellar_feh', width=-45, padding=5, show_label=False, format_str='%1.2f', enabled_when='not using_imported_atmosphere'),
                    Item('stellar_feh_uncertainty', width=45, style='readonly', format_str=u'± %1.2f', show_label=False, visible_when='stellar_teff_uncertainty > 0 or stellar_vt_uncertainty > 0'),
                    Item('feh_units', width=40, padding=5, style='readonly', show_label=False),
                    ),
                HGroup(
                    Item('blank', style='readonly', label='Alpha enhancement, [alpha/Fe]'),
                    spring,
                    Item('stellar_alpha', width=-45, padding=5,  show_label=False, enabled_when='not using_imported_atmosphere'),
                    Item('feh_units', width=40, padding=5, style='readonly', show_label=False),
                    Item('blank', width=35, padding=5, style='readonly', show_label=False, visible_when='stellar_teff_uncertainty > 0 or stellar_vt_uncertainty > 0'), 
                    
                    ),
                HGroup(
                    Item('solve_stellar', show_label=False, padding=5, enabled_when="rest_spectrum"),
                    Item('abfind', show_label=False, padding=5, enabled_when='rest_spectrum'),
                    spring,
                    Item('uncertainty_analysis', show_label=False, padding=5, enabled_when='rest_spectrum and stellar_atmosphere_filename'),
                    ),
                Group(Item('measurements', show_label=False, editor=line_measurements_editor)),
            ),
            Item('display_trends', padding=5, editor=MPLFigureEditor(), show_label=False)
        )
    )

    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)
        self.session = session
        
        self._display_text = []
        self._shift_select = False
        self.show_shortcuts = False

    def _solve_stellar_fired(self):
        """ Opens the Excitation & Ionization Equalibria Dialog """

        dialog = ExcitationIonizationEqualibriaDialog(self.session, self._abfind_fired)
        dialog.configure_traits(kind="modal")
    
    @property_depends_on("update_measurements")
    def _get_measurement_filter(self):
        """ Filter whether measurements are acceptable and if they should be
        used in the excitation and ionization balance """

        return lambda x: True if x.is_acceptable and x.transition in self.session.balance_transitions else False
    
    
    def _selected_changed(self, selections):
        """ When a row from the table is selected, this highlights the point on
        the display trend graphs """
        
        if len(selections) == 0: return

        x_values = np.zeros((len(selections), 3))
        y_values = np.zeros(len(selections))
        colors = np.zeros(len(selections), dtype=str)

        # If this is a good measurement
        num_good_measurements = 0
        for i, selected in enumerate(selections):

            if np.isfinite(selected.abundance):
                colors[num_good_measurements] = "g" if selected.is_acceptable else "r"
                
                x_values[num_good_measurements, :] = [
                    selected.excitation_potential,
                    selected.reduced_equivalent_width,
                    selected.rest_wavelength
                ]
                
                y_values[num_good_measurements] = selected.abundance
                num_good_measurements += 1

        if hasattr(self, "_display_selected_points"):
            for i, ax in enumerate(self.display_trends.axes):
                self._display_selected_points[i].set_offsets(np.array([x_values[:num_good_measurements, i], y_values[:num_good_measurements]]).T)
                self._display_selected_points[i].set_edgecolor(colors[:num_good_measurements])

        else:

            self._display_selected_points = []
            for i, ax in enumerate(self.display_trends.axes):

                self._display_selected_points.append(
                    ax.scatter(x_values[:num_good_measurements, i], y_values[:num_good_measurements], facecolor=colors[:num_good_measurements], alpha=0.5, s=50, edgecolor=colors[:num_good_measurements])
                    )
                
        # Update the canvas
        wx.CallAfter(self.display_trends.canvas.draw)


    def _clean_display(self):
        """ Restores display trends figure to its original state. """

        # Init text
        [text.set_visible(True) for text in self._init_text]

        if hasattr(self, "_display_points"):
            [item.set_offsets([]) for item in self._display_points]

        if hasattr(self, "_display_text"):
            [item.set_text("") for item in self._display_text]

        if hasattr(self, "_display_trend_lines"):
            [item[0].set_data([], []) for item in self._display_trend_lines]

        if hasattr(self, "_display_mean_lines"):
            [item[0].set_data([], []) for item in self._display_mean_lines]

        axes = self.display_trends.axes
        for ax in axes:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        wx.CallAfter(self.display_trends.canvas.draw)


    # Display defaults
    def _display_trends_default(self):
        """ Initializes the StellarParameters spectrum display. """
        
        figure = Figure()
        figure.subplots_adjust(left=0.10, bottom=0.10, right=0.90, top=0.95, wspace=0.30, hspace=0.30)
        
        labels = [
            "Excitation Potential, $\chi$ (eV)",
            "Reduced Equivalent Width",
            u"Wavelength, $\lambda$ (Å)"
        ]

        self._init_text = []
        for i, label in zip(xrange(1, 4), labels):
            ax = figure.add_subplot(3, 1, i)
            ax.set_xlabel(label)
            ax.set_ylabel("log$\epsilon$(X)")
            self._init_text.append(
                ax.text(
                    0.5, 0.5,
                    "Measure {0} equivalent widths before determining stellar parameters."
                        .format(", ".join([species_to_element(transition) for transition in self.session.balance_transitions]), ),
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=11,
                    transform=ax.transAxes))
        
        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor("w")
        
        return figure

    
    def _abfind_fired(self, value):
        """ Calls MOOG and calculates abundances for all balance transitions """
        
        # Generate a new model atmosphere!
        model_atmosphere_folder, model_atmosphere_parser = atmospheres.parsers[self.session.stellar_atmosphere_type]

        # We need to scale the abundance differences from MOOG's internal default solar
        # composition by Anders & Grevesse et al (1989), to the Asplund et al. (2009)
        # solar composition.

        formatted_abundances = {}
        for element, (abundance, uncertainty, meteroitic) in solar_abundances.iteritems():
            if element == "H": continue
            formatted_abundances[element] = abundance + self.session.stellar_feh

        # Interpolate with these parameters
        # Create a temporary working directory if we don't have one already
        self.twd = self.twd if hasattr(self, 'twd') else mkdtemp()
        if isinstance(self.twd, (list, tuple)): self.twd = self.twd[1]
        
        # Create filenames (save the stellar atmosphere one)
        self.stellar_atmosphere_filename = os.path.join(self.twd, 'stellar_atmosphere.model')

        interpolator = atmospheres.AtmosphereInterpolator(model_atmosphere_folder, model_atmosphere_parser())
        interpolator.interpolate(self.session.stellar_atmosphere_filename, self.session.stellar_teff,
            self.session.stellar_logg, self.session.stellar_feh, self.session.stellar_alpha,
            self.session.stellar_vt, solar_abundances=formatted_abundances, clobber=True)

        # Update the measurements
        self.update_measurements = not self.update_measurements
        results = self.session.calculate_atomic_abundances(species=self.session.balance_transitions, full_output=True)
        if results:
            self.abundances, self.distributions, self.slopes = results

            col_transition, col_abundance = 1, 6
            fe_index = np.where(self.abundances[:, col_transition] == 26.0)[0]
            if len(fe_index) > 0:
                is_finite = np.isfinite(self.abundances[:, col_abundance])
                self.session.stellar_reference_fe_h = np.mean(self.abundances[is_finite, col_abundance])

        else:
            logger.warn("No equivalent widths measured.")        

        # Update the trends plot
        self._update_display_trends()


    def _update_display_trends(self, force=False):
        """ Updates the display trends in the stellar parameters tab. """

        logger.debug("StellarParameters._update_display_trends(%s)" % (force, ))
        
        if not hasattr(self, 'rest_spectrum') or self.rest_spectrum is None: return
        
        if hasattr(self, '_init_text'):
            [text.set_visible(False) for text in self._init_text]

        # Some helpful column index identifiers
        col_wl, col_transition, col_ep, col_loggf, col_ew, col_logrw, col_abund, col_del_avg, col_idx_match = xrange(9)
        
        # This may be called from the main.py or session.py so we should check that
        # self.abundances exists as we want it.
        logger.debug("Continuing to update display trends..")

        if not hasattr(self, 'abundances') or force:
            
            logger.warn("No self.abundances found in Stellar Parameters tab. Initializing..")
            
            abundances = []
            for i, measurement in enumerate(self.session.measurements):
                if  measurement.is_acceptable \
                and measurement.transition in self.session.balance_transitions \
                and measurement.measured_equivalent_width > 0 \
                and measurement.abundance > 0:
                    abundances.append([
                        measurement.rest_wavelength,
                        measurement.transition,
                        measurement.excitation_potential,
                        measurement.oscillator_strength,
                        measurement.measured_equivalent_width,
                        measurement.reduced_equivalent_width,
                        measurement.abundance,
                        measurement.delta_abundance,
                        i
                    ])
            self.abundances = np.array(abundances)
            
            if len(self.abundances) == 0:
                return None

            # Calculate slopes
            self.distributions, self.slopes = moog.calculate_trend_lines(self.abundances,
                transition_col=1, x_cols=(col_ep, col_logrw, col_wl,), y_col=col_abund)

            # Update the session Fe I abundance
            idx = np.where(self.abundances[:, col_transition] == 26.0)[0]
            infinite_abundances = ~np.isfinite(self.abundances[idx, col_abund])
            idx = np.delete(idx, np.where(~np.isfinite(self.abundances[idx, col_abund]))[0])
            
            if len(idx) is 0:
                logger.warn("We don't know what the Fe I abundance is because it appears not to be a balance transition...")
    
            self.session.stellar_reference_fe_h = np.mean(self.abundances[idx, col_abund])
            
        assert len(self.abundances) > 0
        


        fig = self.display_trends 
        
        # Remove text at the top of the plots
        for text in self._display_text:
            text.set_visible(False)
            
        del self._display_text
        self._display_text = []
        
        # Some plotting variables
        colors, markers = 'kbrg', '+xosd'
        text_rhs, text_space = 0.90, 0.33
        mc_text_top, mc_text_space = 0.95, 0.13
        
        display_points_exists = hasattr(self, '_display_points')

        if display_points_exists:

            # Hide old selected points
            if hasattr(self, '_display_selected_points'):
                for i in xrange(len(fig.axes)):
                    self._display_selected_points[i].set_offsets([])

        else:
            self._display_points = []
            self._display_trend_lines = []
            self._display_mean_lines = []


        # Plot each balance transition with a different colour
        for i, (color, marker, transition) in enumerate(zip(colors, markers, self.session.balance_transitions)):
            
            # Get indices
            idx = np.where(self.abundances[:, col_transition] == transition)[0]
            
            # Remove NaN's or Inf's
            infinite_abundances = ~np.isfinite(self.abundances[idx, col_abund])
            idx = np.delete(idx, np.where(~np.isfinite(self.abundances[idx, col_abund]))[0])

            if len(idx) is 0:
                logger.warn("Couldn't find any finite values of balance transition %2.1f to plot" % (transition, ))
                continue
            
            # Get properties of the distribution
            N, mean, std = self.distributions[transition]
            
            # Get the element name
            element = species_to_element(transition)

            # Plot the information about this transition in the top right of the figure
            self._display_text.append(
                fig.text(text_rhs - (len(self.session.balance_transitions) - i - 1) * text_space,
                     0.95, u"[%s/H] = %1.2f $\pm$ %1.2f (N: %i)%s" \
                     % (element,
                        mean - self.session.solar_abundances[element.split()[0]][0],
                        std,
                        N,
                        "," if i + 1 != len(self.session.balance_transitions) else ""),
                    ha='right', va='bottom', color=color, fontsize=10, fontweight='bold'))
            

            
            xlim_indices = (col_ep, col_logrw, col_wl, )

            for j, (ax, xlim_index) in enumerate(zip(fig.axes, xlim_indices)):

                # Get the trend information
                m, c, r_value, p_value, std_err = self.slopes[transition][j]

                # Write display text
                text_to_display = [
                    "{slope:+1.3f}$\pm${std_err:1.3f} dex eV$^{{-1}}$",
                    "{slope:+1.3f}$\pm${std_err:1.3f} dex",
                    u"{slope:+1.3e}$\pm${std_err:1.3e} dex Å$^{{-1}}$", #$\AA{{}}^{{-1}}$ <-- no boldface.
                ]

                # Append the statistics
                text_to_display = [(item + " (r={r_value:+1.3f}, p={p_value:1.3f})") for item in text_to_display]
                
                self._display_text.append(
                    ax.text(0.99,
                        mc_text_top - mc_text_space * i,
                        text_to_display[j].format(slope=m, std_err=std_err, r_value=r_value, p_value=p_value),
                        ha='right', va='top', color=color, fontsize=10, fontweight='bold', transform=ax.transAxes)
                    )

                # Get the x limits of the data
                x_data = self.abundances[:, xlim_index]
                x_limits = np.array([np.min(x_data), np.max(x_data)])

                # Double it!
                x_limits = np.array([
                    np.mean(x_limits) - np.ptp(x_limits),
                    np.mean(x_limits) + np.ptp(x_limits)
                    ])


                if display_points_exists:
                    # Draw mean line
                    self._display_mean_lines[3 * i + j][0].set_data(x_limits, [mean] * 2)

                    # Draw trend line                
                    self._display_trend_lines[3 * i + j][0].set_data(x_limits, (m * x_limits) + c)

                else:
                    # Mean line
                    self._display_mean_lines.append(
                        ax.plot(x_limits, [mean, mean], '-.', c=color, zorder=-2)
                    )

                    # Trend line
                    self._display_trend_lines.append(
                        ax.plot(x_limits, (m * x_limits) + c, color + '-', lw=1, zorder=-2)
                    )
                
                

            if display_points_exists:
                
                # Excitation Potential axes
                ax = fig.axes[0]
                self._display_points[3 * i].set_offsets(np.vstack([
                    self.abundances[idx, col_ep],
                    self.abundances[idx, col_abund]
                    ]).T)

                # Reduced Equivalent Width axes
                ax = fig.axes[1]
                self._display_points[3 * i + 1].set_offsets(np.vstack([
                    self.abundances[idx, col_logrw],
                    self.abundances[idx, col_abund]
                    ]).T)
                
                # Wavelength axes
                ax = fig.axes[2]
                self._display_points[3 * i + 2].set_offsets(np.vstack([
                    self.abundances[idx, col_wl],
                    self.abundances[idx, col_abund]
                    ]).T)
                
                

            else:

                # Excitation Potential axes
                ax = fig.axes[0]
                self._display_points.append(
                    ax.scatter(self.abundances[idx, col_ep], self.abundances[idx, col_abund], s=30, edgecolor=color, marker=marker, facecolor='none')
                    )

                # Reduced Equivalent Width axes
                ax = fig.axes[1]
                self._display_points.append(
                    ax.scatter(self.abundances[idx, col_logrw], self.abundances[idx, col_abund], s=30, edgecolor=color, marker=marker, facecolor='none')
                    )

                # Wavelength
                ax = fig.axes[2]
                self._display_points.append(
                    ax.scatter(self.abundances[idx, col_wl], self.abundances[idx, col_abund], s=30, edgecolor=color, marker=marker, facecolor='none')
                )

                

        y_data = self.abundances[:, col_abund]
        y_limits = extend_limits([np.min(y_data), np.max(y_data)], fraction=0.20)

        for i, ax in enumerate(fig.axes):
            x_data = self.abundances[:, xlim_indices[i]]
            
            x_limits = np.array([np.min(x_data), np.max(x_data)])

            ax.set_xlim(extend_limits(x_limits))
            ax.set_ylim(extend_limits(y_limits))

        if not hasattr(self, 'mpl_button_event'):
            self.mpl_button_event = fig.canvas.mpl_connect('button_press_event', self._select_point_on_plot)
            self.mpl_keypress_event = fig.canvas.mpl_connect('key_press_event', self._on_keypress)
            self.mpl_keyrelease_event = fig.canvas.mpl_connect('key_release_event', self._on_keyrelease)
            self.mpl_figureleave_event = fig.canvas.mpl_connect('figure_leave_event', self._on_figureleave)
            
        # Update the canvas
        wx.CallAfter(fig.canvas.draw)
    

    def _on_keypress(self, event):
        """ Handles for when either the shift, u, or a key is pressed when the
        figure has focus. """

        if event.key == 'shift':
            self._shift_select = True

        elif event.key == 'u':
            for selection in self.selected:
                selection.is_acceptable = False

            self._selected_changed(self.selected)

        elif event.key == 'a':
            for selection in self.selected:
                selection.is_acceptable = True

            self._selected_changed(self.selected)

        elif event.key == "h":
            self.show_shortcuts = not self.show_shortcuts
            if self.show_shortcuts:
                if not hasattr(self, "shortcut_display"):
                    self.shortcut_display = show_keyboard_shortcuts(self.display_trends, {
                        "a": "mark selected measurements as acceptable",
                        "u": "mark selected measurements as unacceptable",
                        "shift": "select multiple measurements"
                        }, extent=[0.15, 0.15, 0.7, 0.7], two_columns=False)
                else:
                    self.shortcut_display.set_visible(True)
            else:
                self.shortcut_display.set_visible(False)
            wx.CallAfter(self.display_trends.canvas.draw)

    def _on_keyrelease(self, event):
        """ Triggers the end of shift clicking points """
        if event.key == 'shift': self._shift_select = False


    def _on_figureleave(self, event):
        """ Disables shift select when the cursor leaves the figure. """

        self._shift_select = False


    def _select_point_on_plot(self, event):
        """Fires when the mouse was used to select a point on one of the stellar
        parameter plots."""
        
        if not hasattr(self, 'abundances'):
            return False
       
        # Find out which axes was clicked on
        ax = event.inaxes
        axes_idx = self.display_trends.axes.index(event.inaxes)
        
        # We need to map the axes to which value from abundances that we want
        axes_xcol_mapping = {
            0: 2, # Excitation balance for top axes
            1: 5, # Reduced equivalent width for middle axes
            2: 0  # Wavelength for bottom axes
            }
        
        # Which columns of self.abundances should we be using for each axes?
        xcol = axes_xcol_mapping[axes_idx]
        ycol = 6
        
        # Get the limits so we can truly see what the closest point is in pixel space
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        
        # Scale the values and calculate a distance
        dist = pow(((event.xdata - self.abundances[:, xcol])/np.ptp(xlims)), 2) + pow(((event.ydata - self.abundances[:, ycol])/np.ptp(ylims)), 2)
        
        nearest_point = self.abundances[np.argmin(dist)]
        logger.debug("Nearest point is at %1.2f, %1.2f at session index %i" % (nearest_point[xcol], nearest_point[ycol], nearest_point[-1], ))
        
        # Update the selected items
        if not self._shift_select:
            logger.debug("Setting selected without shift")
            self.selected = [self.session.measurements[int(nearest_point[-1])]]

        else:
            logger.debug("Setting selected with shift")
            currently_selected = []
            currently_selected.extend(self.selected)
            currently_selected.append(self.session.measurements[int(nearest_point[-1])])

            self.selected = currently_selected
        
        return True    


    def _uncertainty_analysis_fired(self, value):
        """Performs an uncertainty analysis on the effective temperature."""

        # Try temperatures until you get a slope of m + std_err

        # Build up the list of just excitation balance items and write it to file
        excitation_balance_index, microturbulence = (0, 1, )

        balance_species = self.session.balance_transitions[0] # 26.0 is default
        moog.io.write_equivalent_widths(self.session.measurements, os.path.join(self.twd, "stellar_uncertainty.ew"), transitions=[balance_species], clobber=True)
        
        try:
            # Get the statistical information for the first balance transition (excitation)
            m, c, r_value, p_value, std_err = self.slopes[balance_species][excitation_balance_index]

            # Specify the minimisation function
            excitation_uncertainty = lambda teff, m_target: pow(m_target - calculate_stellar_slope(teff, "teff", "stellar_uncertainty.ew", self.session)[balance_species][0][0], 2)

            # Do the 1-sigma minimizations on one side for Teff (it seems fairly symmetrical)
            print("err", m, std_err)
            teff_positive_uncertainty = self.stellar_teff - fmin(excitation_uncertainty, [self.stellar_teff], args=(m + std_err, ), xtol=0.1, ftol=0.00001)[0]
            #teff_negative_uncertainty = fmin(excitation_uncertainty, [self.stellar_teff], args=(m - std_err, ), xtol=0.1, ftol=0.001)[0] - self.stellar_teff
            teff_maximum_uncertainty = teff_positive_uncertainty
            #teff_maximum_uncertainty = np.max(np.abs([teff_positive_uncertainty, teff_negative_uncertainty]))

            print("TEFF", teff_positive_uncertainty, teff_maximum_uncertainty)
        except:
            logger.warn("Critical error while trying to calculate uncertainties in effective temperature!")
            raise

        else:
            self.session.stellar_teff_uncertainty = int(teff_maximum_uncertainty)
        

        try:
            # Get the statistical information for the first balance transition (excitation)
            m, c, r_value, p_value, std_err = self.slopes[balance_species][microturbulence]
            
            # Specify the minimisation function
            microturbulence_uncertainty = lambda vt, m_target: pow(m_target - calculate_stellar_slope(vt, "xi", os.path.join(self.twd, "stellar_uncertainty.ew"), self.session)[balance_species][0][1], 2)

            # Do the 1-sigma minimizations either side for microturbulence
            vt_positive_uncertainty = self.stellar_vt - fmin(microturbulence_uncertainty, [self.stellar_vt], args=(m + std_err, ), xtol=0.1, ftol=0.001)[0]
            vt_negative_uncertainty = fmin(microturbulence_uncertainty, [self.stellar_vt], args=(m - std_err, ), xtol=0.1, ftol=0.00001)[0] - self.stellar_vt

            vt_maximum_uncertainty = np.max(np.abs([vt_negative_uncertainty, vt_positive_uncertainty]))
            print("VT", vt_positive_uncertainty, vt_negative_uncertainty, vt_maximum_uncertainty)
        
        except:
            logger.warn("Critical error while trying to calculate uncertainties in microturbulence")

        else:
            self.session.stellar_vt_uncertainty = vt_maximum_uncertainty
        

        try:
            # Do the 1-sigma minimisation for logg.
            # Get STD dev in the two balance species and adjust logg until their mean difference is that amount
            N_1, mean_1, std_1 = self.distributions[self.session.balance_transitions[0]]
            N_2, mean_2, std_2 = self.distributions[self.session.balance_transitions[1]]

            # Add the standard error of the mean in both measurements
            SEM_quadrature = pow(pow(std_1/np.sqrt(N_1), 2) + pow(std_2/np.sqrt(N_2), 2), 0.5)
            logger.info("SEM quadrature is: %1.2f" % (SEM_quadrature, ))

            # We need to write both balance species to the EW list.
            moog.io.write_equivalent_widths(self.session.measurements, os.path.join(self.twd, "stellar_uncertainty.ew"), transitions=self.session.balance_transitions, clobber=True)
            
            # Adjust logg until the difference in mean abundances matches this SEM_quadrature
            # Specify the minimisation function
            logg_uncertainty = lambda logg, logeps_difference_target: pow(logeps_difference_target - calculate_mean_differences(logg, "logg", os.path.join(self.twd, "stellar_uncertainty.ew"), self.session), 2)

            logg_positive_uncertainty = fmin(logg_uncertainty, [self.stellar_logg], args=(-SEM_quadrature, ), xtol=0.1, ftol=0.001)[0] - self.stellar_logg
            logg_negative_uncertainty = fmin(logg_uncertainty, [self.stellar_logg], args=(+SEM_quadrature, ), xtol=0.1, ftol=0.001)[0] - self.stellar_logg

            logg_maximum_uncertainty = np.max(np.abs([logg_positive_uncertainty, logg_negative_uncertainty]))
            print("LOGG", logg_positive_uncertainty, logg_negative_uncertainty, logg_maximum_uncertainty)

        except:
            logger.warn("Critical error while trying to calculate uncertainties in surface gravity")

        else:
            self.session.stellar_logg_uncertainty = logg_maximum_uncertainty

        # Metallicity uncertainty - quote standard deviation of Fe I if it exists
        if 26.0 in self.session.balance_transitions:
            N, mean, std = self.distributions[26.0]
            self.session.stellar_feh_uncertainty = std



        

