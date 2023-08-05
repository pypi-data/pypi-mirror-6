# coding: utf-8

""" Tab for chemical abundances in the Spectroscopy Made Hard GUI """

__author__ = "Andy Casey <andy@astrowizici.st>"
__all__ = ["ChemicalAbundancesTab"]

# Module imports
from ..core import *
from ..utils import species_to_element, extend_limits
from ..session import Session

from ..profiles import measure_transition_with_continuum_points

# GUI module specific imports
from gui_core import *
from uncertainties import ChemicalAbundanceUncertainties

class ChemicalAbundancesTab(HasTraits):
   
    title = Str("Elemental Abundances")
    sub_title = Str("Individual Line Abundances")
   
    session = Instance(Session)    
    
    filter_current_element = Property
    
    selected_element = Instance(ElementalAbundance)
    selected_measurements = List(AtomicTransition)

    elemental_abundances = DelegatesTo("session")
    
    # Parameter inputs
    stellar_teff = DelegatesTo("session")
    stellar_logg = DelegatesTo("session")
    stellar_feh = DelegatesTo("session")
    stellar_alpha = DelegatesTo("session")
    stellar_vt = DelegatesTo("session")
    stellar_atmosphere_filename = DelegatesTo("session")
    stellar_reference_fe_h = DelegatesTo("session")
    
    show_only_acceptable_measurements = Bool(False)
    
    # Rest spectrum for plotting
    rest_spectrum = DelegatesTo("session")
    ew_initial_fwhm_guess = DelegatesTo("session")
    
    # Calculate abundances
    calculate_abundances = Button("Calculate Abundances")
    calculate_uncertainties = Button("Uncertainty analysis..")
    
    elemental_abundances_editor = TableEditor(
        columns = [
            ObjectColumn(name="element", label="Element", editable=False,
                         format="%s", width=-50),
            NumericColumn(name="transition", label="Transition",
                          editable=False, format="%2.1f", width=-50),
            NumericColumn(name="number_of_lines", label="N", editable=False,
                          format="%i", width=30),
            NumericColumn(name="abundance_mean", label="A(X)", editable=False,
                          format="%1.2f", width=-30),
            NumericColumn(name="abundance_std", label=u"σ(X)", editable=False,
                          format="%1.2f", width=-30),
            NumericColumn(name="solar_abundance", label=u"A(Xօ)",
                          editable=False, format="%1.2f", width=-30),
            NumericColumn(name="X_on_H", label="[X/H]", editable=False,
                          format="%1.2f", width=-30),
            NumericColumn(name="X_on_Fe", label="[X/Fe]", editable=False,
                          format="%1.2f", width=-30)
        ],
        other_columns = [
            NumericColumn(name="nlte_number_of_lines", label="N (n-LTE)",
                editable=False, format="%i"),
            NumericColumn(name="nlte_abundance_mean", label="A(X) (n-LTE)",
                editable=False, format="%+1.2f"),
            NumericColumn(name="nlte_abundance_std", label=u"σ(X) (n-LTE)",
                editable=False, format="%1.2f"),
        ],
        auto_size = False,
        auto_add = False,
        editable = False,
        sortable = True,
        sort_model = True,
        show_lines = True,
        configurable = True,
        orientation = "vertical",
        selected = "selected_element",
        selection_mode = "row",
        show_column_labels = True,
        show_toolbar = True,
        reorderable = False
    )

    blank = Str(" ")
    measurements = DelegatesTo("session")
    measurements_editor = TableEditor(
        columns = [
            ObjectColumn(name="is_blank", label=" ", editable=False, width=20),
            CheckboxColumn(name="is_acceptable", label="    ", width=20, ),
            NumericColumn(name="rest_wavelength", label="Wavelength",
                          editable=False, format="%4.3f"),
            NumericColumn(name="measured_fwhm", label="FWHM",
                          editable=False, format="%1.2f"),
            NumericColumn(name="oscillator_strength", label="log gf",
                          editable=False, format="%+1.3f"),
            NumericColumn(name="measured_equivalent_width", label="EW",
                          editable=False, format="%1.2f"),
            NumericColumn(name="reduced_equivalent_width", label="REW",
                          editable=False, format="%1.2f"),
            NumericColumn(name="abundance", label="A(X)", editable=False,
                          format="%+1.2f"),
            NumericColumn(name="delta_abundance", label="d_A(X)",
                          editable=False, format="%+1.2f"),            
        ],
        other_columns = [
            NumericColumn(name="transition", label="Transition",
                editable=False, format="%2.1f"),
            NumericColumn(name="nlte_abundance", label="A(X) (n-LTE)",
                editable=False, format="%+1.2f"),
            NumericColumn(name="excitation_potential", label="EP",
                editable=False, format="%1.3f"),
        ],
        edit_view_width=350,
        edit_view_height = 300,
        auto_size = False,
        auto_add = False,
        editable = False,
        sortable = True,
        sort_model = True,
        show_lines = True,
        configurable = True,
        orientation = "vertical",
        selected = "selected_measurements",
        selection_mode = "rows",
        show_column_labels = True,
        show_toolbar = True,
        reorderable = True,
        filter_name = "filter_current_element",
        row_factory = AtomicTransition
        )
    
    # Figures
    display_trends = Instance(Figure)
    
    view = View(
        
        HGroup(
            VGroup(
                HGroup(
                        Item("title",
                        show_label = False,
                        editor     = TitleEditor(),
                        springy = True,
                        ),
                    ),
                HGroup(
                    Item("calculate_abundances", show_label=False, padding=5, enabled_when="stellar_atmosphere_filename"),
                    spring,
                    Item("calculate_uncertainties", show_label=False, padding=5, enabled_when="stellar_atmosphere_filename and len(elemental_abundances) > 0"),
                ),
                Group(
                    Item("elemental_abundances", editor=elemental_abundances_editor, show_label=False, enabled_when="stellar_atmosphere_filename"),
                    ),
                HGroup(
                    Item("sub_title",
                         show_label=False,
                         editor = TitleEditor(),
                         springy = True,
                         )
                    ),
                Group(
                    Item("measurements", editor=measurements_editor, show_label=False, enabled_when="stellar_atmosphere_filename")
                    ),
                HGroup(
                    Item("show_only_acceptable_measurements", show_label=False),
                    Label("Show only acceptable measurements"),
                    spring
                    )
            ),
            Group(
                Item("display_trends", editor=MPLFigureEditor(), show_label=False),
                )
        )
    )
    
    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)
        self.session = session

        self.shift_key_held = False
        self.show_shortcuts = False
        self.selected_continuum_points = []
        

    def _clean_display(self):
        logger.warn("NotImplementedError")
        #raise NotImplementedError
    

    def _calculate_uncertainties_fired(self):
        """ Open the GUI window to calculate the uncertainties in abundance ratios due to atmospheric parameters """

        # Create a dictionary with the present information.
        initial_abundances = {}

        for element in self.elemental_abundances:
            initial_abundances[element.transition] = {
                "mean"  : element.abundance_mean,
                # Let"s specify a minimum standard deviation of 0.1 dex.
                "SEM"   : np.max([element.abundance_std, 0.1])/np.sqrt(element.number_of_lines), # Standard error about the mean
                }

        # Load the window
        uncertainty_analysis_window = ChemicalAbundanceUncertainties()
        uncertainty_analysis_window.session = self.session
        uncertainty_analysis_window.initial_abundances = initial_abundances

        # Do we have any uncertainties in this session?
        if self.session.stellar_teff_uncertainty > 0: uncertainty_analysis_window.teff_offset = self.session.stellar_teff_uncertainty
        if self.session.stellar_vt_uncertainty > 0: uncertainty_analysis_window.vt_offset = self.session.stellar_vt_uncertainty
        if self.session.stellar_logg_uncertainty > 0: uncertainty_analysis_window.logg_offset = self.session.stellar_logg_uncertainty

        # Open the GUI
        uncertainty_analysis_window.configure_traits()


    # Initialise trends plot
    def _display_trends_default(self):
        """ Initialises the trends display """
        
        figure = Figure()
        figure.subplots_adjust(left=0.10, bottom=0.10, right=0.70, top=0.95, wspace=0.40, hspace=0.45)
        
        ax = figure.add_subplot(3, 1, 1)
        ax.set_xlabel("Excitation Potential (eV)")
        ax.set_ylabel("Abundance")
        ax.xaxis.set_major_locator(MaxNLocator(6))
        ax.yaxis.set_major_locator(MaxNLocator(6))

        self._init_text = [ax.text(0.5, 0.5, "Determine stellar parameters before\ncalculating elemental abundances.",
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=11,
                transform=ax.transAxes)]
        
        ax = figure.add_subplot(3, 1, 2, sharey=ax)
        ax.set_xlabel("Reduced Equivalent Width")
        ax.set_ylabel("Abundance")
        ax.xaxis.set_major_locator(MaxNLocator(6))
        ax.yaxis.set_major_locator(MaxNLocator(6))

        self._init_text.append(ax.text(0.5, 0.5, "Determine stellar parameters before\ncalculating elemental abundances.",
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=11,
                transform=ax.transAxes))
        
        ax = figure.add_subplot(3, 1, 3)
        ax.set_xlabel("Wavelength, $\lambda$ (${\AA}$)")
        ax.set_ylabel("Flux, $F_\lambda$")
        ax.xaxis.set_major_locator(MaxNLocator(6))
        ax.yaxis.set_major_locator(MaxNLocator(6))

        self._init_text.append(ax.text(0.5, 0.5, "Determine stellar parameters before\ncalculating elemental abundances.",
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=11,
                transform=ax.transAxes))
        ax.set_ylim(0, 1.2)

        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor("w")
        
        return figure


    # This is used to largely initialize the elemental abundances table
    def _measurements_changed(self, value):
        logger.debug("ChemicalAbundances.measurements = %s" % (value, ))

        # Find out which transitions we should be listing in the abundance table
        
        available_transitions = []
        for measurement in self.measurements:
            available_transitions.append(measurement.transition)

        # Sort the unique transitions to display by their transition + ionization 
        self.transitions_to_display = np.sort(np.unique(available_transitions))
        
        # Take care of reference Fe first
        if np.any(self.transitions_to_display == 26.0):
            
            abundances = [measurement.abundance for measurement in self.measurements if measurement.transition == 26.0 and measurement.is_acceptable]

            logger.debug("Setting stellar reference as [Fe/H] = %1.2f (from measurements: %s)" % (np.mean(abundances), abundances, ))
            self.stellar_reference_fe_h = np.mean(abundances)

        # Create the elemental abundances
        elemental_abundances = []
        for transition in self.transitions_to_display:
            solar_abundance, solar_uncertainty, is_not_photospheric_abundance = self.session.solar_abundances[species_to_element(transition).split()[0]]

            # Get lines associated with this elemental abundance measurement            
            lines = [measurement for measurement in self.measurements if measurement.transition == transition]

            elemental_abundance = ElementalAbundance(
                transition=transition,
                solar_abundance=solar_abundance,
                solar_uncertainty=solar_uncertainty,
                stellar_reference_fe_h  = self.stellar_reference_fe_h,
                solar_fe_abundance      = self.session.solar_abundances["Fe"][0],
                line_measurements       = lines)

            elemental_abundances.append(elemental_abundance)
        
        self.elemental_abundances = elemental_abundances

        if not hasattr(self, "button_press_event"):
            # Set up the connect event
            self.button_press_event = self.display_trends.canvas.mpl_connect("button_press_event", self._select_point_on_plot)
            self.mpl_key_press_event = self.display_trends.canvas.mpl_connect("key_press_event", self._on_key_press)
            self.mpl_key_release_event = self.display_trends.canvas.mpl_connect("key_release_event", self._on_key_release) 


    # The stellar Fe I abundance must be propagated through to each elemental abundance manually
    @on_trait_change("stellar_reference_fe_h")
    def _update_x_on_fe_values(self):
        """ Delegates the updated stellar information to each chemical abundance class """

        if np.isfinite(self.stellar_reference_fe_h):
            for element in self.elemental_abundances:
                element.stellar_reference_fe_h = self.stellar_reference_fe_h


    def _rest_spectrum_changed(self, spectrum):
        """ Updates when the rest spectrum has been updated """
        
        if spectrum is None: return
        if hasattr(self, "_display_trends_spectrum"):
            self._display_trends_spectrum[0].set_data(spectrum.disp, spectrum.flux)

        else:
            self._display_trends_spectrum = self.display_trends.axes[2].plot(spectrum.disp, spectrum.flux, "k")

        # Remove init text
        if hasattr(self, "_init_text") and len(self._init_text) == 3:
            self._init_text[2].set_text("")
            del self._init_text[2]

        self.display_trends.axes[2].set_xlim(spectrum.disp[0], spectrum.disp[-1])   
     
        wx.CallAfter(self.display_trends.canvas.draw)


    # Calculate abundances
    def _calculate_abundances_fired(self, value):
        """ Calculates abundances for all elements in the atomic line list """

        # If we have no elemental abundances listed in the table we may
        # need to update our table first
        if len(self.elemental_abundances) == 0:
            self._measurements_changed(self.measurements)

        self.session.calculate_atomic_abundances()

        # Update plots and things
        self._update_scatter_displays()
        self._update_selected_points()
        self._update_trend_lines()
        self._update_axes_limits()

        # Draw the canvas
        wx.CallAfter(self.display_trends.canvas.draw)
        
    
    # Highlighting items in elemental abundances table
    def _selected_element_changed(self, selected):
        """ Changes the selected element in the GUI """

        if selected is None: return None
        self.sub_title = "%s line abundances" % (selected.element, )
        
        # Update the displays with the new scatter plots
        self._update_scatter_displays()

        # Update the displays with the new trend line and mean
        self._update_trend_lines()
        
        # Update the displays with the new profile plot
        self._update_fitted_profile()

        # Update selected points
        self._update_selected_points()

        # Update the limits
        self._update_axes_limits()

        # Draw the updates
        wx.CallAfter(self.display_trends.canvas.draw)


    def _update_scatter_displays(self):
        """ Update the excitation potential and reduced equivalent width
        scatter displays """

        # Remove initial text
        if hasattr(self, "_init_text"):
            [text.set_text("") for text in self._init_text]
            del self._init_text

        # Find data to display
        self.display_data = []
        for i, measurement in enumerate(self.selected_element.line_measurements):
            # Ignore measurements with non-finite abundances, regardless of whether
            # they are acceptable or not because they won't be displayed and will
            # just screw everything up
            if not np.isfinite(measurement.abundance) \
            or (self.show_only_acceptable_measurements and not measurement.is_acceptable): continue

            self.display_data.append([
                int(measurement.is_acceptable),
                measurement.excitation_potential,
                measurement.reduced_equivalent_width,
                measurement.abundance,
                i
                ])
            
        if len(self.display_data) == 0:
            if hasattr(self, "_display_trends_scatter_ep"):
                self._display_trends_scatter_ep.set_offsets([])

            if hasattr(self, "_display_trends_scatter_rew"):
                self._display_trends_scatter_rew.set_offsets([])

            return None

        self.display_data = np.array(self.display_data)
        col_is_acceptable, col_ep, col_rew, col_abund = xrange(4)

        possible_colors = ["r", "k"]
        colors = [possible_colors[int(is_acceptable)] for is_acceptable in self.display_data[:, col_is_acceptable]]
        
        # Excitation potential plot
        if hasattr(self, "_display_trends_scatter_ep"):
            self._display_trends_scatter_ep.set_offsets(
                np.vstack([
                    self.display_data[:, col_ep],
                    self.display_data[:, col_abund]
                ]).T)
            self._display_trends_scatter_ep.set_edgecolor(colors)
            
        else:
            self._display_trends_scatter_ep = self.display_trends.axes[0].scatter(
                self.display_data[:, col_ep],
                self.display_data[:, col_abund],
                marker="x", edgecolor=colors)

        # Reduced equivalent width plot
        if hasattr(self, "_display_trends_scatter_rew"):
            self._display_trends_scatter_rew.set_offsets(
                np.vstack([
                    self.display_data[:, col_rew],
                    self.display_data[:, col_abund]
                ]).T)
            self._display_trends_scatter_rew.set_edgecolor(colors)

        else:
            self._display_trends_scatter_rew = self.display_trends.axes[1].scatter(
                self.display_data[:, col_rew],
                self.display_data[:, col_abund],
                marker="x", edgecolor=colors)

        return True    


    def _update_axes_limits(self):
        """ Update the axes limits """

        if not hasattr(self, "display_data") or len(self.display_data) == 0: return 

        # Set limits
        col_is_acceptable, col_ep, col_rew, col_abund = xrange(4)
        x_ep_limits = extend_limits(self.display_data[:, col_ep], fraction=0.10)
        x_rew_limits = extend_limits(self.display_data[:, col_rew], fraction=0.10)
        both_y_limits = extend_limits(self.display_data[:, col_abund], fraction=0.10)

        self.display_trends.axes[0].set_xlim(x_ep_limits)
        self.display_trends.axes[1].set_xlim(x_rew_limits)
        # The y-axes are linked so we don't need to explicitly specify them for each axes
        self.display_trends.axes[0].set_ylim(both_y_limits)

        return True


    def _update_trend_lines(self):
        """ Update the trend lines for the excitation potential and reduced equivalent width
        scatter plots """

        if not hasattr(self, "display_data"): return
        if len(self.display_data) == 0:
            if hasattr(self, "_display_trends_scatter_ep_trendline"):
                self._display_trends_scatter_ep_trendline[0].set_data([], [])
                self._display_trends_scatter_ep_mean[0].set_data([], [])

            if hasattr(self, "_display_trends_scatter_rew_trendline"):
                self._display_trends_scatter_rew_trendline[0].set_data([], [])
                self._display_trends_scatter_rew_mean[0].set_data([], [])

            return

        col_is_acceptable, col_ep, col_rew, col_abund = xrange(4)

        # Calculate trend lines for excitation potential
        # Use only finite abundance indices AND acceptable measurements
        finite_abund_indices = np.array(np.isfinite(self.display_data[:, col_abund]) * self.display_data[:, col_is_acceptable], dtype=bool)

        x = extend_limits(self.display_data[:, col_ep], fraction=0.10)        
        A = np.vstack([self.display_data[finite_abund_indices, col_ep], np.ones(np.sum(finite_abund_indices))]).T
        m, c = np.linalg.lstsq(A, self.display_data[finite_abund_indices, col_abund])[0]
        y = m * x + c
        
        ax = self.display_trends.axes[0]
        if hasattr(self, "_display_trends_scatter_ep_trendline"):
            if np.sum(finite_abund_indices) >= 2:
                self._display_trends_scatter_ep_trendline[0].set_data(x, y)
            else:
                self._display_trends_scatter_ep_trendline[0].set_data([], [])

            self._display_trends_scatter_ep_mean[0].set_data(x, [np.mean(self.display_data[finite_abund_indices, col_abund])] * 2)
            
        else:
            if np.sum(finite_abund_indices) >= 2:
                self._display_trends_scatter_ep_trendline = ax.plot(x, y, "k--")
            else:
                self._display_trends_scatter_ep_trendline = ax.plot([], [], "k--")

            self._display_trends_scatter_ep_mean = ax.plot(x, [np.mean(self.display_data[finite_abund_indices, col_abund])] * 2, "k-")

        # Calculate trend lines for reduced equivalent widths
        ax = self.display_trends.axes[1]
        x = extend_limits(self.display_data[:, col_rew], fraction=0.10)
        A = np.vstack([self.display_data[finite_abund_indices, col_rew], np.ones(np.sum(finite_abund_indices))]).T
        m, c = np.linalg.lstsq(A, self.display_data[finite_abund_indices, col_abund])[0]
        y = m * x + c

        if hasattr(self, "_display_trends_scatter_rew_trendline"):
            if np.sum(finite_abund_indices) >= 2:
                self._display_trends_scatter_rew_trendline[0].set_data(x, y)
            else:
                self._display_trends_scatter_rew_trendline[0].set_data([], [])
            self._display_trends_scatter_rew_mean[0].set_data(x, [np.mean(self.display_data[finite_abund_indices, col_abund])] * 2)
        
        else:
            if np.sum(finite_abund_indices) >= 2:
                self._display_trends_scatter_rew_trendline = ax.plot(x, y, "k--")
            else:
                self._display_trends_scatter_rew_trendline = ax.plot([], [], "k--")
            self._display_trends_scatter_rew_mean = ax.plot(x, [np.mean(self.display_data[finite_abund_indices, col_abund])] * 2, "k-")

        return True



    def _on_key_press(self, event):
        """ Handles the keyboard button being pressed """

        if event.key == "shift":
            self.shift_key_held = True

        elif event.key == "a":
            # All selected items are acceptable
            if self.selected_measurements is not None:
                for point in self.selected_measurements:
                    point.is_acceptable = True

                self._update_scatter_displays()
                self._update_selected_points()

                # Update the canvas
                wx.CallAfter(self.display_trends.canvas.draw)

                # Update the measurements filter
                raise NotImplementedError

                
        elif event.key == "u":
            # All selected items are unacceptable
            if self.selected_measurements is not None:
                for point in self.selected_measurements:
                    point.is_acceptable = False

                self._update_scatter_displays()
                self._update_selected_points()

                # Update the canvas
                wx.CallAfter(self.display_trends.canvas.draw)

                # Update the measurements filter
                raise NotImplementedError

        elif event.key == "h":
            self.show_shortcuts = not self.show_shortcuts
            if self.show_shortcuts:
                if not hasattr(self, "shortcut_display"):
                    self.shortcut_display = show_keyboard_shortcuts(self.display_trends, {
                        "a": "mark selected measurements as acceptable",
                        "u": "mark selected measurements as unacceptable",
                        "shift": "select multiple points (upper/middle panel)\nor select two continuum points (lower panel)\nto measure equivalent width"
                        }, extent=[0.05, 0.15, 0.6, 0.7], two_columns=False)
                else:
                    self.shortcut_display.set_visible(True)
            else:
                self.shortcut_display.set_visible(False)
            wx.CallAfter(self.display_trends.canvas.draw)

    def _on_key_release(self, event):
        """ Handles the keyboard buttons being released """

        if event.key != "shift": return
        self.shift_key_held = False
        self.selected_continuum_points = []



    def _select_point_on_plot(self, event):
        """ Fires when the mouse was used to select a point on one of the trend line plots """
        
        if not hasattr(self, "display_data") \
        or len(self.display_data) == 0 \
        or event.inaxes is None:
            return False
        
        # Find out which axes was clicked on
        axes_idx = self.display_trends.axes.index(event.inaxes)

        if axes_idx > 1:

            if len(self.selected_measurements) == 0 or not self.shift_key_held: return

            # Measuring equivalent width
            print("in ew region", len(self.selected_continuum_points))
            if len(self.selected_continuum_points) > 0:
                print("We can measure an equivalent width!")

                # Hide any points
                self.selected_continuum_points.append([event.xdata, event.ydata])

                first_selected = self.selected_measurements[0]

                # Measure the EW
                profile = measure_transition_with_continuum_points(
                    self.rest_spectrum,
                    first_selected.rest_wavelength,
                    self.ew_initial_fwhm_guess,
                    *self.selected_continuum_points)

                if not profile[0]:
                    logger.warn("Interactive EW measurement failed: %s. Try re-placing the continuum." % (profile[3], ))
                    
                else:
                    # Add the profile values to this determined measurement
                    self.selected_measurements[0].is_acceptable = True
                    self.selected_measurements[0].measured_wavelength = profile[1]
                    self.selected_measurements[0].measured_trough = profile[2]
                    self.selected_measurements[0].measured_fwhm = profile[3]
                    self.selected_measurements[0].measured_equivalent_width = profile[6] * 1e3 # Convert to mA
                    self.selected_measurements[0].abundance = np.nan
                    self.selected_measurements[0].measured_chi_sq = profile[7]
                    self.selected_measurements[0].profile = np.vstack([profile[9], profile[10]])

                # Update the plots
                self._display_continuum_points.set_offsets([])

                self._update_fitted_profile()
                self._update_scatter_displays()
                self._update_selected_points()
                self._update_trend_lines()

                self.selected_continuum_points = []

            else:
                print("adding point")
                if hasattr(self, "_display_continuum_points"):
                    self._display_continuum_points.set_offsets(np.array([event.xdata, event.ydata]).T)

                else:
                    self._display_continuum_points = self.display_trends.axes[2].scatter(
                        [event.xdata], [event.ydata],
                        marker="o", s=60, facecolor="none", edgecolor="m", zorder=2)

                self.selected_continuum_points.append([event.xdata, event.ydata])
            
            wx.CallAfter(self.display_trends.canvas.draw) 

            return
                

        # Get the limits so we can truly see what the closest point is in pixel space
        axes = self.display_trends.axes[axes_idx]
        xlims, ylims = axes.get_xlim(), axes.get_ylim()
        col_is_acceptable, col_ep, col_rew, col_abund, col_reference_index = xrange(5)
        
        col_x = [col_ep, col_rew][axes_idx]

        # Scale the values and calculate a distance
        #finite_values = np.isfinite(self.display_data[:, col_x]) * np.isfinite(self.display_data[:, col_abund])
        dist = pow(((event.xdata - self.display_data[:, col_x])/np.ptp(xlims)), 2) + pow(((event.ydata - self.display_data[:, col_abund])/np.ptp(ylims)), 2)
        
        logger.debug("Nearest point on axes %i is at %s" % (axes_idx, self.display_data[int(np.argmin(dist))], ))
        
        nearest_point_index = int(self.display_data[int(np.argmin(dist)), col_reference_index])
        nearest_measurement = self.selected_element.line_measurements[nearest_point_index]

        # Select the transition
        if self.shift_key_held:
            # No double-ups, thanks
            if nearest_measurement in self.selected_measurements:
                return

            currently_selected = []
            currently_selected.extend(self.selected_measurements)
            currently_selected.append(nearest_measurement)

        else:
            currently_selected = [nearest_measurement]

        self.selected_measurements = currently_selected

        return True   


    # For when an individual line measurement has been selected
    def _selected_measurements_changed(self, selected_measurements):
        """ An individual selected measurement has been changed """

        if self.selected_measurements is None or len(self.selected_measurements) == 0:
            return None

        # Update the scatter display since this may have triggered a measurement being
        # marked acceptable or unacceptable
        self._update_scatter_displays()

        # Update the selected points on the scatter plot
        self._update_selected_points()

        # Update the spectrum plot
        self._update_fitted_profile()

        # Draw the canvas
        wx.CallAfter(self.display_trends.canvas.draw)


    def _update_selected_points(self):
        """ Updates the selected points """
        
        # Update the trends
        selected_data = []
        for i, selected_measurement in enumerate(self.selected_measurements):
            if self.show_only_acceptable_measurements and not selected_measurement.is_acceptable: continue

            selected_data.append([
                int(selected_measurement.is_acceptable),
                selected_measurement.excitation_potential,
                selected_measurement.reduced_equivalent_width,
                selected_measurement.abundance
                ])

        if len(selected_data) == 0:
            if hasattr(self, "_display_trends_ep_selected"):
                self._display_trends_ep_selected.set_offsets([])

            if hasattr(self, "_display_trends_rew_selected"):
                self._display_trends_rew_selected.set_offsets([])

            return True

        possible_colors = ["r", "k"]
        selected_data = np.array(selected_data)
        col_is_acceptable, col_ep, col_rew, col_abund = xrange(4)
        colors = [possible_colors[int(is_acceptable)] for is_acceptable in selected_data[:, col_is_acceptable]]
        
        # Highlight the point in excitation potential
        if hasattr(self, "_display_trends_ep_selected"):
            self._display_trends_ep_selected.set_offsets(np.array([
                selected_data[:, col_ep],
                selected_data[:, col_abund]
                ]).T)
            self._display_trends_ep_selected.set_edgecolor(colors)

        else:
            self._display_trends_ep_selected = self.display_trends.axes[0].scatter(
                selected_data[:, col_ep], selected_data[:, col_abund],
                marker="o", facecolor="none", edgecolor=colors, s=60, zorder=2)

        # Highlight the point in reduced equivalent width
        if hasattr(self, "_display_trends_rew_selected"):
            self._display_trends_rew_selected.set_offsets(np.array([
                selected_data[:, col_rew],
                selected_data[:, col_abund],
                ]).T)
            self._display_trends_rew_selected.set_edgecolor(colors)

        else:
            self._display_trends_rew_selected = self.display_trends.axes[1].scatter(
                selected_data[:, col_rew], selected_data[:, col_abund],
                marker="o", facecolor="none", edgecolor=colors, s=60, zorder=2)

        return True


    def _update_fitted_profile(self):
        """ Updates the spectrum plot to display the first selected measurements'
        fitted profile """

        if len(self.selected_measurements) == 0 \
        or (not self.selected_measurements[0].is_acceptable and self.show_only_acceptable_measurements):

            if hasattr(self, "_display_trends_selected"):
                self._display_trends_selected[0].set_data([], [])

            if hasattr(self, "_display_trends_selected_rest_line"):
                self._display_trends_selected_rest_line[0].set_data([], [])

            if hasattr(self, "_display_trends_selected_measured_line"):
                self._display_trends_selected_measured_line[0].set_data([], [])

            # This is costly...
            if hasattr(self, "rest_spectrum") and self.rest_spectrum is not None:
                self.display_trends.axes[2].set_xlim(self.rest_spectrum.disp[0], self.rest_spectrum.disp[-1])
        
            return True

        possible_colors = ["r", "g"]
        first_selected = self.selected_measurements[0]
        if len(first_selected.profile) > 0:
            if hasattr(self, "_display_trends_selected"):
                self._display_trends_selected[0].set_data(first_selected.profile[0], first_selected.profile[1])
                self._display_trends_selected[0].set_color(possible_colors[int(first_selected.is_acceptable)])

            else:
                self._display_trends_selected = self.display_trends.axes[2].plot(
                    first_selected.profile[0],
                    first_selected.profile[1],
                    color=possible_colors[int(first_selected.is_acceptable)], zorder=3)

        # Measured line
        if hasattr(self, "_display_trends_selected_rest_line"):
            self._display_trends_selected_rest_line[0].set_data([first_selected.rest_wavelength, first_selected.rest_wavelength], [0, 1.2])

        else:
            self._display_trends_selected_rest_line = self.display_trends.axes[2].plot(
                [first_selected.rest_wavelength, first_selected.rest_wavelength], [0, 1.2], ":", c="#666666", zorder=2)

        if first_selected.measured_wavelength > 0:
            if hasattr(self, "_display_trends_selected_measured_line"):
                self._display_trends_selected_measured_line[0].set_data([first_selected.measured_wavelength, first_selected.measured_wavelength], [0., 1.2])
            
            else:            
                self._display_trends_selected_measured_line = self.display_trends.axes[2].plot(
                    [first_selected.measured_wavelength, first_selected.measured_wavelength], [0, 1.2], "-", c="#666666", zorder=2)

        # Update the profile xlims
        self.display_trends.axes[2].set_xlim(first_selected.rest_wavelength - 5, first_selected.rest_wavelength + 5)

        return True


    def _show_only_acceptable_measurements_changed(self, show_only_acceptable_measurements):
        """ Triggers whether to display only acceptable measurements or not """

        # If there's no data, there's nothing to do
        if len(self.display_data) == 0:
            return

        # Okay, update the scatter displays
        self._update_scatter_displays()

        # Update the selected points because some of the selected ones might have been changed
        # to unacceptable
        self._update_selected_points()

        # Update the profile because we might have had an unacceptable measurement selected first
        self._update_fitted_profile()

        # Update the limits
        self._update_axes_limits()

        # Update the canvas
        wx.CallAfter(self.display_trends.canvas.draw)


    # Filters
    @property_depends_on("selected_element,show_only_acceptable_measurements")
    def _get_filter_current_element(self):
        if self.show_only_acceptable_measurements:
            return self._get_filter_current_acceptable_element()
    
        else:
            return lambda x: True if self.selected_element is not None and x.transition == self.selected_element.transition else False

    def _get_filter_current_acceptable_element(self):
        return lambda x: True if x.is_acceptable and self.selected_element is not None and x.transition == self.selected_element.transition else False



        