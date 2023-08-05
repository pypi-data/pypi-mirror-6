# coding: utf-8

# Contains code for the doppler corrections tab in the main SMH GUI 
from gui_core import *

# Module specific imports
from ..core import *
from ..session import Session
from ..specutils import Spectrum1D

__all__ = ["DopplerCorrectTab"]

class DopplerCorrectTab(HasTraits):
    """ Class for the doppler corrections tab """
    
    # Initiate the session
    session = Instance(Session)
    
    template_title = Str("Template")
    measure_title = Str("Measurement")
    correct_title = Str("Correction")

    # Traits delegating from session
    doppler_template_filename = DelegatesTo("session")
    doppler_wlstart = DelegatesTo("session")
    doppler_wlend = DelegatesTo("session")
    
    normalised_spectrum = DelegatesTo("session")
    rest_spectrum = DelegatesTo("session")
    
    v_rad = DelegatesTo("session")
    v_helio = DelegatesTo("session")
    v_err = DelegatesTo("session")

    v_apply_offset = DelegatesTo("session")
    v_applied_offset = DelegatesTo("session")
    
    # Buttons
    measure_v_rad = Button("Calculate velocity")
    inspect_v_rad = Button("Show template")
    zoom_out = Button("Original view")
    
    mark_at_rest = Button("Spectrum already at rest")
    apply_offset = Button("Place spectrum at rest")
    
    # Plot items
    display_spectrum = Instance(Figure)

    # View
    view = View(
        HGroup(
            VGroup(
                Item("template_title",
                    show_label=False,
                    springy=True,
                    editor=TitleEditor()
                    ),
                HGroup(
                    Item("doppler_template_filename", style="simple", springy=True, label="Template", padding=5),
                    ),
                "10",
                Label(u"Wavelength region, (Å):"),
                HGroup(
                    Item("doppler_wlstart", width=-60, padding=5, label="Start"),
                    "20",
                    Item("doppler_wlend", width=-60, padding=5, label="End"),
                    ),
                HGroup(
                    Item("inspect_v_rad", show_label=False, padding=5, enabled_when="doppler_template_filename"),
                    spring,
                    Item("zoom_out", show_label=False, padding=5, enabled_when="normalised_spectrum")
                    ),
                "30",
                Item("measure_title",
                    show_label=False,
                    springy=True,
                    editor=TitleEditor()
                    ),
                "10",
                HGroup(
                    spring,
                    Label("V_rad = "),
                    Item("v_rad", show_label=False, format_str="%5.1f ", style="readonly"),
                    Label(" +/- "),
                    Item("v_err", show_label=False, format_str="%5.1f", style="readonly"),
                    Label("km/s"),
                    spring
                    ),
                HGroup(
                    spring,
                    Label("V_helio = "),
                    Item("v_helio", show_label=False, format_str="%5.1f", style="readonly"),
                    Label(" +/- "),
                    Item("v_err", show_label=False, format_str="%5.1f", style="readonly"),
                    Label("km/s"),
                    spring
                    ),
                "10",
                HGroup(
                    spring,
                    Item("measure_v_rad", show_label=False, padding=5, enabled_when="doppler_wlstart and doppler_wlend and doppler_template_filename and normalised_spectrum"),
                    spring
                    ),
                "30",
                Item("correct_title",
                    show_label=False,
                    springy=True,
                    editor=TitleEditor()
                    ),
                HGroup(
                    Item("v_apply_offset", padding=5, format_str="%1.1f", label="Velocity shift, (km/s)"),
                    spring
                    ),
                HGroup(
                    Item("v_applied_offset", padding=5, label="Applied offset, (km/s)", format_str="%1.1f", style="readonly"),
                    spring
                    ),
                "10",
                HGroup(
                    "14",
                    Item("apply_offset", show_label=False, padding=15, width=-220, enabled_when="abs(v_apply_offset) > 0 and normalised_spectrum"),
                    "14"
                ),
                HGroup(
                    "14",
                    Item("mark_at_rest", show_label=False, padding=15, width=-220, enabled_when="v_apply == 0 and normalised_spectrum"),
                    "14",
                )
            ),
            Item("display_spectrum", show_label=False, editor=MPLFigureEditor())
        )
    )
                    
    
    
    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)
        self.session = session


    def _display_spectrum_default(self):
        """ Initialising function for the spectrum display plot. """
        
        figure = Figure()
        ax = figure.add_axes([0.1, 0.1, 0.85, 0.85])

        ax.set_xlabel("Wavelength, $\lambda$ (${\AA}$)")
        
        ax.set_ylabel("Flux, $F_\lambda$")
        
        ax.set_ylim(0, 1.2)
        
        self._init_text = ax.text(0.5, 0.5, "No normalised spectrum found.",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes)
        
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))

        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor("w")
            
        return figure


    def _clean_display(self):
        """Restores the display to its original form."""

        self._init_text.set_visible(True)

        if hasattr(self, "_display_normalised_spectrum"):
            self._display_normalised_spectrum[0].set_data([], [])

        if hasattr(self, "_display_template_spectrum"):
            self._display_template_spectrum[0].set_data([], [])

        self.display_spectrum.axes[0].set_xlim(0, 1)
        self.display_spectrum.axes[0].set_ylim(0, 1.2)

        wx.CallAfter(self.display_spectrum.canvas.draw)
    
    
    def _update_observed_spectrum(self, spectrum):
        """ Updates the display with the observed spectrum. """

        if spectrum is None: return

        # Remove any initialisation text if it exists
        if hasattr(self, "_init_text"):
            self._init_text.set_visible(False)

        ax = self.display_spectrum.axes[0]  

        if hasattr(self, "_display_normalised_spectrum"):
            self._display_normalised_spectrum[0].set_data(spectrum.disp, spectrum.flux)

        else:
            self._display_normalised_spectrum = ax.plot(spectrum.disp, spectrum.flux, c="k", label="Observed frame")

        ax.set_xlim(spectrum.disp[0], spectrum.disp[-1])
        wx.CallAfter(self.display_spectrum.canvas.draw)
        

    def _normalised_spectrum_changed(self, spectrum):
        self._update_observed_spectrum(spectrum)


    def _rest_spectrum_changed(self, spectrum):
        self._update_observed_spectrum(spectrum)


    def _mark_at_rest_fired(self, value):
        """ The normalised spectrum is considered to already be at rest. """
        self.session.doppler.correct(0)


    def _measure_v_rad_fired(self, value):
        """Measures the radial velocity of the provided spectrum against a given
        template and updates the session with the measured radial velocity. """

        self.session.doppler.measure(
            self.session.doppler_template_filename,
            self.session.doppler_wlstart,
            self.session.doppler_wlend)


    def _apply_offset_fired(self, value):
        """ Applies a radial velocity offset to the normalised spectrum and plots
        the rest-frame spectrum in green in the Doppler Correct tab. """
        self.session.doppler.correct(self.v_apply_offset)


    def _zoom_out_fired(self, value):
        """ Restores the original zoom view """

        ax = self.display_spectrum.axes[0]
        ax.set_xlim(self.normalised_spectrum.disp[0], self.normalised_spectrum.disp[-1])
        ax.set_ylim(0, 1.2)

        wx.CallAfter(self.display_spectrum.canvas.draw)


    def _inspect_v_rad_fired(self, value):
        """ Inspect the wavelength region specified for doppler measurement, and
        the rest-frame spectrum, the template spectrum, and the original spectrum. """
        
        # Load the template spectrum
        template_spectrum = Spectrum1D.load(self.doppler_template_filename)

        # Norm the y-values
        median = np.median(template_spectrum.flux)
        if median > 2:
            template_spectrum.flux /= median
        
        ax = self.display_spectrum.axes[0]
        
        # Plot the template to the same normed-y values
        if hasattr(self, "_display_template_spectrum"):
            self._display_template_spectrum[0].set_data(template_spectrum.disp, template_spectrum.flux)
        
        else:
            self._display_template_spectrum = ax.plot(template_spectrum.disp, template_spectrum.flux, c="b", zorder=-2, label="Template")
        
        # Set the limits
        ax.set_xlim(self.doppler_wlstart, self.doppler_wlend)
        ax.set_ylim(0, 1.2)
        wx.CallAfter(self.display_spectrum.canvas.draw)
        
        
