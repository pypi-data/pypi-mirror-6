# coding: utf-8

""" Contains code for the synthesis tab in the main SMH GUI. """

__author__ = "Andy Casey <andy@astrowizici.st>"

__all__ = ["SynthesisTab"]

# Third-party imports
from scipy.optimize import fmin

# Module-specific imports
from ..core import *
from ..utils import species_to_element
from ..session import Session
from ..specutils import Spectrum1D, cross_correlate

from gui_core import *

class CustomColumn(ObjectColumn):
    """ Custom column colouring for the element of interest in synthesis """

    def get_cell_color(self, row):
        return "#35a3d1" if row.highlight else "#FFFFFF"


def add_new_synthesis(*args, **kwargs):
    """ Loads a new synthesis traits GUI and checks to make sure it's
    valid before adding it in """

    view = View(
        VGroup(
            HGroup(
                Item('label', label='Element of interest', style='readonly', padding=5),
                spring,
                Item('element', show_label=False, padding=5)
                ),
            HGroup(
                Item('label', label='Spectral region', style='readonly', padding=5),
                spring,
                Item('comment', show_label=False, width=-60, padding=5)
                ),
            HGroup(
                Item('label', label='Line list', style='readonly', padding=5),
                spring,
                Item('line_list_filename', show_label=False, width=200, padding=5),
                ),
            VGroup(
                HGroup(Item('label', label='Isotopic ratios', style='readonly', padding=5)),
                HGroup(Item('isotopic_ratios', show_label=False, style='custom', height=200, width=350, padding=5)),
                ),
            ),
        width   = 350,
        height  = 200,
        buttons = [Action(name='OK', action='ok', enabled_when='len(comment) > 0 and os.path.exists(line_list_filename)'), 'Cancel'],
        title   = 'Edit Synthesis',
        resizable=True,
        )

    new_synthesis = Session.Synthesis(*args, **kwargs)
    new_synthesis.configure_traits(kind="modal", view=view)

    # Check the line list and comment.
    if not os.path.exists(new_synthesis.line_list_filename) \
    or new_synthesis.comment is None:
        return None

    return new_synthesis


class SynthesisTab(HasTraits):
    """ Container for the Chemical Synthesis panel of the GUI """
    
    # Initiate session
    session = Instance(Session)    
    
    # Synthesis setups
    synthesis_setups = DelegatesTo("session")

    # Elemental abundances
    elemental_abundances = DelegatesTo("session")
    stellar_reference_fe_h = DelegatesTo("session")
    stellar_feh = DelegatesTo("session")
    solar_abundances = DelegatesTo("session")
    twd = DelegatesTo("session")

    current_title = Str("Current Setup")
    
    # Controls for the current synthesi Float(0.50)
    v_rad = Float
    observed_smoothing_kernel = Float(0.0)
    smoothing_kernel = Float(0.1)
    continuum_adjust = Float(1.0)
    
    # Solve button items
    solve_button_text = Str("Solve")
    currently_solving = Bool(False)
    show_selected_element_wavelengths = Bool(True)
    
    # Events
    solve = Event
    edit_selected_synthesis = Event
    
    plot_surrounding = Float(1.5)
    stellar_atmosphere_filename = DelegatesTo("session")
    
    synthesis_setups_list = TableEditor(
        columns = [
            ObjectColumn(name="is_blank", label=" ", editable=False, width=20),
            CheckboxColumn(name="is_acceptable", label="    ", width=20),
            ObjectColumn(name="representation", label="Element (Spectral Region)", editable=False, format=" %s"),
            NumericColumn(name="abundance", label=u"logε(X)", editable=False, width=85, format="%+1.2f"),
            NumericColumn(name="uncertainty", label=u"σ(logε(X))", editable=False, width=85, format=u"±%1.2f")
        ],
        other_columns = [
        ],
        auto_size = False,
        auto_add = False,
        editable = True,
        sortable = True,
        sort_model = True,
        deletable = True,
        configurable = True,
        orientation = "vertical",
        selected = "current_synthesis",
        selection_mode = "row",
        show_column_labels = True,
        show_toolbar = True,
        reorderable = True,
        row_factory = add_new_synthesis,
        row_factory_kw = {},                # This is updated in __init__ after the session has been passed.
        dclick = "edit_selected_synthesis",
        rows = 20
        )

    rest_spectrum = DelegatesTo("session")
    
    # Buttons for adding/removing synthesis setups
    load_multiple_synthesis_setups = Button("Import..")

    synthesize = Button("Synthesize")
    plot_line_style = Enum("Line", "Dots", "Line and dots")

    update_synthesis_abundances = Button("Update Abundances from EWs")
    #save_spectra = Button("Save spectra")
    
    # Figures
    spectrum_display = Instance(Figure)
    
    selected_element_in_synthesis = Instance(ElementInSynthesisSetup)
    current_synthesis = Instance(Session.Synthesis)
    current_synthesis_setup_relevant_transitions = List(ElementInSynthesisSetup)
    current_synthesis_setup_relevant_transitions_editor = TableEditor(
        columns = [
            CustomColumn(name="element_repr", label="Element", editable=False, format="%s"),
            CustomColumn(name="log_epsilon", label=u"logε(X)", width=75, editable=True, format="%1.2f"),
            CustomColumn(name="X_on_Fe", label="[X/Fe]", width=75, editable=True, format="%1.2f"),
            CustomColumn(name="abundance_minus_offset", label=u"+Δlogε(X)", width=75, editable=True, format="%1.2f"),
            CustomColumn(name="abundance_plus_offset", label=u"-Δlogε(X)", width=75, editable=True, format="%1.2f")
            ],
            edit_view_width=100,
            edit_view_height=200,
            auto_size = False,
            auto_add = False,
            editable = True,
            sortable = False,
            configurable = False,
            orientation = "vertical",
            selection_mode = "row",
            selected = "selected_element_in_synthesis",
            show_column_labels = True,
            show_toolbar = True,
            reorderable = False
        )
    
    transition = Float
    element = Str
    X_on_Fe = Float

    blank = Str("")
    velocity_units = Str("km/s")

    traits_view = View(
        HSplit(
            VGroup(
                Group(
                    Item("synthesis_setups", editor=synthesis_setups_list, height=-150, show_label=False),
                    ),
                HGroup(
                    Item("load_multiple_synthesis_setups", show_label=False, padding=5),
                    spring
                    ),
                HGroup(
                    Item("current_title",
                        show_label = False,
                        springy = True,
                        editor = TitleEditor()
                        ),
                    ),
                VGroup(
                    HGroup(
                        Item("blank", style="readonly", label="Radial velocity"),
                        spring,
                        Item("v_rad", show_label=False, format_str="%+1.2f", width=-50,
                            enabled_when="stellar_atmosphere_filename and current_synthesis is not None and not currently_solving"), "5",
                        Item("velocity_units", show_label=False, width=40, style="readonly"), "5",
                        ),
                    HGroup(
                        Item("blank", style="readonly", label="Continuum adjustment"),
                        spring,
                        Item("continuum_adjust", show_label=False, format_str="%1.3f", width=-50, 
                            enabled_when="stellar_atmosphere_filename and current_synthesis is not None and not currently_solving"), "52",
                        ),
                    HGroup(
                        Item("blank", style="readonly", label="Synthetic smoothing FWHM"),
                        spring,
                        Item("smoothing_kernel", show_label=False, enabled_when="stellar_atmosphere_filename and current_synthesis is not None and not currently_solving",
                            format_str="%1.3f", width=-50), "5",
                        Item("velocity_units", show_label=False, width=40, style="readonly"), "5",
                        ),
                    HGroup(
                        Item("blank", style="readonly", label="Observed smoothing FWHM"),
                        spring,
                        Item("observed_smoothing_kernel", show_label=False, enabled_when="stellar_atmosphere_filename and current_synthesis is not None and not currently_solving", 
                            format_str="%1.3f", width=-50), "5",
                        Item("velocity_units", show_label=False, width=40, style="readonly"), "5"
                        ),
                    ),
                HGroup(
                    Item("update_synthesis_abundances", show_label=False, padding=5, enabled_when="stellar_atmosphere_filename and current_synthesis is not None and not currently_solving"),
                    spring,
                    #Item("save_spectra", show_label=False, padding=5),
                    ),
                Group(
                    Item("current_synthesis_setup_relevant_transitions", width=360, height=100, show_label=False, editor=current_synthesis_setup_relevant_transitions_editor),
                    ),
                HGroup(    
                    Item("synthesize", show_label=False, padding=5, enabled_when="stellar_atmosphere_filename and current_synthesis is not None and not currently_solving"),
                    spring,
                    Item("solve", editor=ButtonEditor(label_value="solve_button_text"), enabled_when="stellar_atmosphere_filename and current_synthesis is not None", show_label=False, padding=5)
                )
            ),
            
            VGroup(
                Group(
                    Item("spectrum_display", editor=MPLFigureEditor(), show_label=False),
                ),
                HGroup(
                    Item("plot_surrounding", padding=5, width=-40, label=u"Plot surrounding region, (Å)"),
                    spring,
                    Item("blank", style="readonly", label="Mark selected transitions"),
                    Item("show_selected_element_wavelengths", padding=5, show_label=False),
                    spring,
                    Item("plot_line_style", padding=5, label="Plotting style")
                    ),
                ),
        ),
        resizable = True
    )

    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)
        
        self.session = session
        self.synthesis_setups_list.row_factory_kw = { "session": session }


    def _spectrum_display_default(self):
        """ Initialises the spectrum display """
        
        figure = Figure()
        figure.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.95, hspace=0.0)
        
        ax = figure.add_subplot(2, 1, 1)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_major_locator(MaxNLocator(6))
        ax.set_ylabel("Observed - Synthetic Flux")
        
        self._init_text = []
        self._init_text.append(ax.text(0.5, 0.5, "Place spectrum at rest frame before synthesizing regions.",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes))

        ax = figure.add_subplot(2, 1, 2, sharex=ax)
        ax.set_xlabel(u"Wavelength, $\lambda$ (Å)")
        ax.set_ylabel("Flux, $F_\lambda$")
        ax.set_ylim(0, 1.2)

        self._init_text.append(ax.text(0.5, 0.5, "Place spectrum at rest frame before synthesizing regions.",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes))
        
        ax.xaxis.set_major_locator(MaxNLocator(8))
        ax.yaxis.set_major_locator(MaxNLocator(6))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: "{0:.0f}".format(x) if x.is_integer() else "{0:.1f}".format(x)))

        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor("w")
        self._display_synthesized_spectrum = []

        return figure


    def _rest_spectrum_changed(self, rest_spectrum):
        """ Updates the rest spectrum displayed in the synthesis plot """

        # Remove the text display
        if hasattr(self, "_init_text"):
            [text.set_text("") for text in self._init_text]
            del self._init_text

        self.update_spectrum_display()


    # Plotting updates
    def _plot_line_style_changed(self, plot_line_style):
        """ Updates the plotting style of the observed spectrum """

        if hasattr(self, "_display_observed_spectrum"):
            line = self._display_observed_spectrum[0]

            if plot_line_style == "Dots":
                line.set_marker("o")
                line.set_linestyle("none")

            elif plot_line_style == "Line":
                line.set_marker("None")
                line.set_linestyle("-")

            elif plot_line_style == "Line and dots":
                line.set_marker("o")
                line.set_linestyle("-")

            wx.CallAfter(self.spectrum_display.canvas.draw)


    def _show_selected_element_wavelengths_changed(self, show_selected_element_wavelengths):
        """ Toggles whether to show the rest wavelength locations for the currently selected
        element. Hides any existing markers if they exist """

        if not show_selected_element_wavelengths and hasattr(self, "_display_selected_element_wavelengths"):
            self._display_selected_element_wavelengths.set_offsets([])
            wx.CallAfter(self.spectrum_display.canvas.draw)

        if show_selected_element_wavelengths:
            # Show the markers for the selected element in the current synthesis
            self._selected_element_in_synthesis_changed(self.selected_element_in_synthesis)


    def _selected_element_in_synthesis_changed(self, selected_element_in_synthesis):
        """ Highlights the location of rest wavelength transitions when the selected
        element in the current synthesis changed """

        if selected_element_in_synthesis is None or not self.show_selected_element_wavelengths: return

        # Get the data we need to display
        x_points = selected_element_in_synthesis.rest_wavelengths
        y_points = 1.1 * np.ones(len(x_points))

        if not hasattr(self, "_display_selected_element_wavelengths"):
            self._display_selected_element_wavelengths = self.spectrum_display.axes[1].scatter(x_points, y_points, marker="|", s=150)

        else:
            self._display_selected_element_wavelengths.set_offsets(np.vstack([x_points, y_points]).T)

        wx.CallAfter(self.spectrum_display.canvas.draw)


    def _edit_selected_synthesis_fired(self):
        """ Open a traits GUI to edit the current selected synthesis setup """

        synth_view = View(
            VGroup(
                HGroup(
                    Item('label', label='Element of interest', style='readonly', padding=5),
                    spring,
                    Item('element', show_label=False, padding=5)
                    ),
                HGroup(
                    Item('label', label='Spectral region', style='readonly', padding=5),
                    spring,
                    Item('comment', show_label=False, width=-60, padding=5)
                    ),
                HGroup(
                    Item('label', label='Line list', style='readonly', padding=5),
                    spring,
                    Item('line_list_filename', show_label=False, width=200, padding=5),
                    ),
                VGroup(
                    HGroup(Item('label', label='Isotopic ratios', style='readonly', padding=5)),
                    HGroup(Item('isotopic_ratios', show_label=False, style='custom', height=200, width=350, padding=5)),
                    ),
                ),
            width   = 350,
            height  = 200,
            buttons = [Action(name='OK', action='ok', enabled_when='len(comment) > 0 and os.path.exists(line_list_filename)'), 'Cancel'],
            title   = 'Edit Synthesis',
            resizable=True,
            )
        self.current_synthesis.configure_traits(kind="modal", view=synth_view)
        #self._current_synthesis_changed(self.current_synthesis)


    def _load_multiple_synthesis_setups_fired(self):
        """Import multiple synthesis setups from a single JSON file."""

        dialog = FileDialog(action="open", wildcard="*.json", title="Select syntheses file")
        dialog.open()
        
        if dialog.return_code == OK:

            filename = os.path.join(dialog.directory, dialog.filename)
            assert os.path.exists(filename)

            with open(filename, "r") as fp:
                syntheses_jsonified = json.load(fp)

            if not isinstance(syntheses_jsonified, (list, tuple)):
                raise TypeError("loaded JSON from filename %s but the syntheses are not in a list-type")

            # Load the syntheses
            syntheses = []
            for setup_jsonified in syntheses_jsonified:

                if not os.path.exists(setup_jsonified["line_list_filename"]):
                    setup_jsonified["line_list_filename"] = os.path.join(dialog.directory, setup_jsonified["line_list_filename"])

                synthesis = Session.Synthesis(self.session, **setup_jsonified)
                syntheses.append(synthesis)

            # Add them in to the session
            self.synthesis_setups.extend(syntheses)


    def _current_synthesis_changed(self, synthesis):
        """ Updates the GUI once the currently selected synthesis has changed """

        if synthesis is None: return False
        
        # Update current items
        self.current_title = synthesis.representation
        self.smoothing_kernel = synthesis.smoothing_kernel
        self.continuum_adjust = synthesis.continuum_adjust
        self.observed_smoothing_kernel = synthesis.observed_smoothing_kernel
        self.v_rad = synthesis.v_rad
        self.plot_surrounding = synthesis.plot_surrounding

        # Update the synthesis relevant transitions 
        self.current_synthesis_setup_relevant_transitions = synthesis.elements_in_synthesis
        self.selected_element_in_synthesis = synthesis.elements_in_synthesis[0]

        # Draw the new spectra
        self.update_spectrum_display()


    @on_trait_change("plot_surrounding,smoothing_kernel,observed_smoothing_kernel,continuum_adjust,v_rad")
    def _current_synthesis_attribute_changed(self, attr, value):
        """ Applies an updated value to the currently selected synthesis setup """
        
        if self.current_synthesis is not None:
            setattr(self.current_synthesis, attr, value)


    # For some changes, don't re-scale
    @on_trait_change("observed_smoothing_kernel,continuum_adjust,v_rad,current_synthesis.smoothed_spectra")
    def update_spectrum_display_without_rescale(self):
        self.update_spectrum_display(force_rescale=False)

    
    @on_trait_change("current_synthesis,plot_surrounding")
    def update_spectrum_display(self, **kwargs):

        if self.current_synthesis is None \
        or self.currently_solving \
        or not self.rest_spectrum \
        or not hasattr(self.current_synthesis, "wavelength_regions") \
        or len(self.current_synthesis.wavelength_regions) == 0: return False
        
        logger.debug("Synthesis.update_spectrum_display(%s, %s, %s, %s)" % (self.current_synthesis, self.currently_solving, self.rest_spectrum, self.current_synthesis.wavelength_regions, ))
        
        # Update the markings
        self._selected_element_in_synthesis_changed(self.selected_element_in_synthesis)

        plot_regions = [
            self.current_synthesis.wavelength_regions[0] - self.plot_surrounding,
            self.current_synthesis.wavelength_regions[1] + self.plot_surrounding
        ]

        # Plot the observed
        idx_l = np.searchsorted(self.rest_spectrum.disp, plot_regions[0], side="left")
        idx_r = np.searchsorted(self.rest_spectrum.disp, plot_regions[1], side="right")

        if hasattr(self, "_display_chisq_regions"):
            [item.set_visible(False) for item in self._display_chisq_regions]
            del self._display_chisq_regions

        if hasattr(self.current_synthesis, "chisq_regions") and len(self.current_synthesis.chisq_regions) > 0:

            if len(self.current_synthesis.chisq_regions) == 2 and isinstance(self.current_synthesis.chisq_regions[0], float):
                self._display_chisq_regions = [self.spectrum_display.axes[1].axvspan(
                    self.current_synthesis.chisq_regions[0],
                    self.current_synthesis.chisq_regions[1],
                    ymin=0, ymax=1.2, facecolor="#2ecc71", alpha=0.2)]

            else:
                self._display_chisq_regions = []
                for chisq_region in self.current_synthesis.chisq_regions:
                    self._display_chisq_regions.append(self.spectrum_display.axes[1].axvspan(
                        chisq_region[0], chisq_region[1], ymin=0, ymax=1.2, facecolor="#2ecc71", alpha=0.2))

        # Plot a zero line
        if hasattr(self, "_display_diff_zero_line"):
            self._display_diff_zero_line[0].set_data(plot_regions, [0, 0])
        
        else:
            self._display_diff_zero_line = self.spectrum_display.axes[0].plot(plot_regions, [0, 0], "k", lw=2)

        # Get the observed spectrum
        observed_spectrum = Spectrum1D(
            disp=self.rest_spectrum.disp[idx_l:idx_r],
            flux=self.rest_spectrum.flux[idx_l:idx_r])

        # Apply smoothing, radial velocities and continuum adjustments where necessary
        if self.observed_smoothing_kernel > 0.:
            observed_spectrum = observed_spectrum.gaussian_smooth(self.observed_smoothing_kernel)

        if np.isfinite(self.v_rad):
            observed_spectrum = observed_spectrum.doppler_correct(self.v_rad, interpolate=False)

        # Display the observed spectrum
        if hasattr(self, "_display_observed_spectrum"):
            self._display_observed_spectrum[0].set_data(observed_spectrum.disp, self.continuum_adjust * observed_spectrum.flux)
            
        else:
            self._display_observed_spectrum = self.spectrum_display.axes[1].plot(observed_spectrum.disp, self.continuum_adjust * observed_spectrum.flux, "k")

        spectra = self.current_synthesis.smoothed_spectra        
        abundances = self.current_synthesis.synthesised_abundances

        if len(spectra) == 0:
            self.spectrum_display.axes[0].set_xlim(plot_regions)

            # Set x-axis ticks
            ax = self.spectrum_display.axes[1]

            # Remove synthetic spectra plotted from other synthesis setups
            if hasattr(self, "_display_synthesized_spectrum"):
                [line[0].set_data([], []) for line in self._display_synthesized_spectrum]
                legend = ax.get_legend()
                if legend is not None:
                    legend.set_visible(False)

            if hasattr(self, "_display_diff_spectra"):
                [line[0].set_data([], []) for line in self._display_diff_spectra]

            wx.CallAfter(self.spectrum_display.canvas.draw)
            return True
        
        # Plot the difference now
        colors = ["#CF5200", "#642448", "#002178"]
        ax = self.spectrum_display.axes[0]
        xlim = ax.get_xlim()
        
        num_already_plotted = len(self._display_diff_spectra) if hasattr(self, "_display_diff_spectra") else 0
        if num_already_plotted == 0:
            self._display_diff_spectra = []

        logger.debug("abundances: %s" % (abundances, ))
        logger.debug("spectra: %s" % (spectra, ))

        for i, (abundance, spectrum) in enumerate(zip(abundances, spectra)):
            # Calculate the difference and plot it
            diff_flux = self.continuum_adjust * observed_spectrum.flux \
                        - spectrum.interpolate(observed_spectrum.disp).flux
            
            if i >= num_already_plotted:
                self._display_diff_spectra.append(ax.plot(observed_spectrum.disp, diff_flux, colors[i]))

            else:
                self._display_diff_spectra[i][0].set_data(observed_spectrum.disp, diff_flux)
                self._display_diff_spectra[i][0].set_color(colors[i])

        # Hide any extra lines
        if len(abundances) > 0 and num_already_plotted > i:
            for item in self._display_diff_spectra[i + 1:]:
                item[0].set_data([], [])

        # Set y limits to have the same absolute value
        ylim = np.max(np.abs(ax.get_ylim()))
        ax.set_ylim((-ylim, ylim))
        
        ax = self.spectrum_display.axes[1]
        ylim = ax.get_ylim()

        if hasattr(self, "_display_zero_abundance"):
            self._display_zero_abundance[0].set_data([observed_spectrum.disp[0], observed_spectrum.disp[-1]], [1.0, 1.0])

        else:
            self._display_zero_abundance = ax.plot([observed_spectrum.disp[0], observed_spectrum.disp[-1]], [1.0, 1.0], "k:", zorder=-1)
        

        if num_already_plotted == 0:
            self._display_synthesized_spectrum = []

        for i, (abundance, spectrum, ) in enumerate(zip(abundances, spectra)):
            if i >= num_already_plotted:
                self._display_synthesized_spectrum.append(ax.plot(spectrum.disp, spectrum.flux, colors[i], label="log$\epsilon$(%s) = %1.2f" % (self.current_synthesis.element, abundance, )))

            else:
                self._display_synthesized_spectrum[i][0].set_data(spectrum.disp, spectrum.flux)
                self._display_synthesized_spectrum[i][0].set_color(colors[i])
                self._display_synthesized_spectrum[i][0].set_label(u"log$\epsilon$(%s) = %1.2f" % (self.current_synthesis.element, abundance, ))

        # Hide any extra lines
        if len(abundances) > 0 and num_already_plotted > i:
            for item in self._display_synthesized_spectrum[i + 1:]:
                item[0].set_data([], [])
                item[0].set_label(None)

        # Is the original xlim overlapping with our spectrum dispersion?
        if (plot_regions[-1] >= xlim[0] and xlim[0] >= plot_regions[0]) \
        or (plot_regions[-1] >= xlim[1] and xlim[1] >= plot_regions[0]):

            # Did we just increase the surrounding region to plot?
            if "force_rescale" in kwargs.keys() and not kwargs["force_rescale"]:
                ax.set_xlim(xlim)

            else:
                ax.set_xlim(plot_regions)

            ax.set_ylim(ylim)

        
        else:
            ax.set_xlim(plot_regions)
            ax.set_ylim(0, 1.2)
        
        ax.legend(loc=4, prop={"size":11})
        wx.CallAfter(self.spectrum_display.canvas.draw)
    

    def _update_synthesis_abundances_fired(self, value):
        """Updates the elemental abundances for the current synthesis setup"""
        
        logger.debug("Synthesis.update_synthesis_abundances fired")

        if self.current_synthesis is None: return False

        for synthesis_element in self.current_synthesis.elements_in_synthesis:
            
            # Update the solar, stellar and solar Fe abundance for this synthesis setup - regardless of whether
            # we have an abundance for this element from equivalent widths 

            # Need to get the first element from solar_abundances, because it is structured as [abundance, uncertainty, flag]
            if species_to_element(synthesis_element.atomic_number).split()[0] not in self.solar_abundances.keys():
                logger.warn("Could not find solar abundance for %s" % (synthesis_element.atomic_number, ))
                synthesis_element.solar_abundance = np.nan

            else:
                synthesis_element.solar_abundance = self.solar_abundances[species_to_element(synthesis_element.atomic_number).split()[0]][0]
            
            print("UPDATING WITH ", self.stellar_reference_fe_h, self.stellar_feh)
            
            #synthesis_element.stellar_fe_abundance = self.stellar_reference_fe_h
            #synthesis_element.stellar_model_abundance = self.stellar_feh
            #synthesis_element.solar_fe_abundance = self.solar_abundances["Fe"][0]

            synthesis_element.X_on_Fe_minus_log_epsilon = self.solar_abundances["Fe"][0] \
                - self.solar_abundances[utils.species_to_element(synthesis_element.atomic_number).split()[0]][0] \
                - self.stellar_reference_fe_h

            # Get the abundance for this element, if we have it
            abundances_for_this_synthesis_element = []
            number_of_lines_for_this_synthesis_element = []


            for abundance_element in self.elemental_abundances:
                # Just check on element, not transition
                print("  CHECK ", abundance_element.transition, synthesis_element.atomic_number)
                if int(abundance_element.transition) == synthesis_element.atomic_number:
                    abundances_for_this_synthesis_element.append(abundance_element.abundance_mean)
                    number_of_lines_for_this_synthesis_element.append(abundance_element.number_of_lines)
                    

            if len(abundances_for_this_synthesis_element) > 0:
                idx = np.argmax(number_of_lines_for_this_synthesis_element)
                log_epsilon = abundances_for_this_synthesis_element[idx]

                # Matched by element (not transition)
                synthesis_element.log_epsilon = log_epsilon
                print("  MATCHED", log_epsilon)
                


    def _synthesize_fired(self, value):
        """ Synthesises spectra for the current setup and loads it back into SMH """

        # Remove init text if it exists
        if hasattr(self, "_init_text"):
            [text.set_text("") for text in self._init_text]
            del self._init_text

        self.current_synthesis.synthesize()
        self.update_spectrum_display()


    def _solve_fired(self, value):
        """ Solves the abundance, radial velocity, continuum adjustment and smoothing
        kernel for the current setup """

        self.current_synthesis.solve()
        self._current_synthesis_changed(self.current_synthesis) # Force an update
        
        

