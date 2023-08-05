# coding: utf-8

""" Contains code for the normalisation tab in the main SMH GUI. """

__author__ = "Andy Casey <acasey@mso.anu.edu.au>"

# Third party
from scipy.interpolate import interp1d, griddata, bisplrep, bisplev

from gui_core import *

# Module specific imports
from ..core import *

from ..session import Session
from ..specutils import Spectrum, Spectrum1D, stitch

__all__ = ["NormalisationTab"]

class NormalisationTab(HasTraits):
    """ This class contains the model and view information for the normalisation
    tab in the `ApplicationMain` GUI """
    
    session = Instance(Session)
    
    initial_orders = DelegatesTo("session")
    continuum_orders = DelegatesTo("session")
    num_orders_per_filename = DelegatesTo("session")

    blank = Str(" ")
    normalisation_title = Str("Normalisation")
    smoothing_title = Str("Smoothing")
    stitching_title = Str("Stitch separate orders")

    # Normalisation options delegating to session
    # TODO
    normalisation_function = Enum("Spline", "Polynomial")
    normalisation_order = Enum(range(1, 10))
    normalisation_max_iterations = Enum(range(1,10))
    normalisation_sigma_low_clip = Float(5.0, tooltip="test", help="test")
    normalisation_sigma_high_clip = Float(1.0)
    normalisation_knot_spacing = Float(20)
    additional_point_weight = Float(10)

    normalisation_arguments = DelegatesTo("session")
    current_order_index = Int(-1)
    
    surface_fit_allowed = Bool(False)
    perform_surface_fit = Event
    surface_kx = Enum(3, range(1, 6))
    surface_ky = Enum(2, range(1, 6))

    # Should these be session delegates? #TODO
    
    display_spectrum = Instance(Figure)

    normalised_spectrum = DelegatesTo("session")   

    stitch_apertures = Event
    stitch_apertures_label = Str("Stitch Normalized Spectra")

    view = View(
            HGroup(
                VGroup(
                    Item("normalisation_title",
                      show_label = False,
                      springy    = False,
                      editor     = TitleEditor()
                    ),
                    VGroup(
                        HGroup(
                            Item("blank", style="readonly", label="Function"),
                            spring,
                            Item("normalisation_function", show_label=False, padding=5)
                            ),
                        HGroup(
                            Item("blank", style="readonly", label="Order"),
                            spring,
                            Item("normalisation_order", width=-50, show_label=False, padding=5)
                            ),
                        HGroup(
                            Item("blank", style="readonly", label="Maximum iterations"),
                            spring,
                            Item("normalisation_max_iterations", width=-50, show_label=False, padding=5)
                            ),
                        HGroup(
                            Item("blank", style="readonly", label="Low sigma clip"),
                            spring,
                            Item("normalisation_sigma_low_clip", width=-40, show_label=False, padding=5)
                            ),
                        HGroup(
                            Item("blank", style="readonly", label="High sigma clip"),
                            spring,
                            Item("normalisation_sigma_high_clip", width=-40, show_label=False, padding=5)
                            ),
                        HGroup(
                            Item("blank", style="readonly", label=u"Knot spacing, (Å)"),
                            spring,
                            Item("normalisation_knot_spacing", width=-40, show_label=False, padding=5, enabled_when="normalisation_function == 'Spline'")
                            ),
                        HGroup(
                            Item("blank", style="readonly", label="Additional point weight"),
                            spring,
                            Item("additional_point_weight", width=-40, show_label=False, padding=5)
                            ),
                        "20",
                        HGroup(
                            spring,
                            "9",
                            Item("stitch_apertures", editor=ButtonEditor(label_value="stitch_apertures_label"), show_label=False, padding=15, width=-220, enabled_when="(len(continuum_orders) > 0 and len(continuum_orders) == len(initial_orders))"),
                            "9",
                            spring
                            )
                        ),
                ),
                VGroup(
                    Item("display_spectrum", editor=MPLFigureEditor(), show_label=False),
                    HGroup(
                        Item("surface_kx", label="Order (x)", padding=5, visible_when="surface_fit_allowed"),
                        Item("surface_ky", label="Order (y)", padding=5, visible_when="surface_fit_allowed"),
                        Item("perform_surface_fit", editor=ButtonEditor(label="Fit Surface and Interpolate"), padding=5, show_label=False, visible_when="surface_fit_allowed"),
                        spring
                        )
                    ),
            ),
        resizable = False
    )
    

    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)
        
        self.session = session
        
        # Some normalisation defaults        
        self.show_shortcuts = False
        self.normalisation_order = 3#self.session.normalisation_order
        self.normalisation_max_iterations = 5#self.session.normalisation_max_iterations

        
        # Interactivity properties
        self.mpl_waiting_for_clicks = False
        self.mpl_highlight_region = False
        

    def _clean_display(self):
        """ Restores the spectrum display to its near-original format. """

        self._init_text.set_visible(True)
        if hasattr(self, "_plot_unnormalised_order") and len(self._plot_unnormalised_order) > 0:
            self._plot_unnormalised_order[0].set_visible(False)
            del self._plot_unnormalised_order

        if hasattr(self, "_plot_normalised_order") and len(self._plot_normalised_order) > 0:
            self._plot_normalised_order[0].set_visible(False)
            del self._plot_normalised_order
        
        if hasattr(self, "_plot_preview_order") and len(self._plot_preview_order) > 0:
            self._plot_preview_order[0].set_visible(False)
            del self._plot_preview_order

        self._normalisation_args_text.set_text("")

        ax = self.display_spectrum.axes[0]
        ax.set_title("")
        ax.set_ylim(0, 1.2)
        ax.set_xlim(0, 1)

        # Other things
        self._normalisation_weights.set_offsets([])

        if hasattr(self, "_show_highlighted_region"):
            self._show_highlighted_region.set_visible(False)
            del self._show_highlighted_region

        [item.set_visible(False) for item in self._show_excluded_regions]
        
        preview_ax = self.display_spectrum.axes[1]
        preview_ax.set_ylim(0.6, 1.4)
        preview_ax.set_yticks([0.8, 1.0, 1.2])

        wx.CallAfter(self.display_spectrum.canvas.draw)
    

    def _display_spectrum_default(self):
        """ Initialises the spectrum display """
        
        figure = Figure()
        
        ax = figure.add_axes([0.1, 0.25, 0.85, 0.70])

        ax.set_ylabel("Flux, $F_\lambda$")

        self._init_text = ax.text(0.5, 0.5, "No apertures found.",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes)

        self._normalisation_args_text = ax.text(0.05, 0.925, "", horizontalalignment="left",
            verticalalignment="top", transform=ax.transAxes)

        self._normalisation_weights = ax.scatter([], [], facecolor="m", edgecolor="k")
        self._show_excluded_regions = []

        preview_ax = figure.add_axes([0.1, 0.1, 0.85, 0.15], sharex=ax)
        preview_ax.set_xlabel("Wavelength, $\lambda$ (${\AA}$)")


        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor("w")

        ax.xaxis.set_visible(False)
        ax.set_ylim(0, 1)

        preview_ax.set_ylim(0.6, 1.4)
        preview_ax.set_yticks([0.8, 1.0, 1.2])
        preview_ax.axhline(y=1.0, c="k", linestyle=":")
        preview_ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        return figure


    def _stitch_apertures_fired(self, value):
        """ Stitches all apertures into a single one-dimensional spectrum. """
        self.session.normalisation.stitch_apertures()


    def _initial_orders_changed(self, spectra):
        """ The initial (unnormalised/normalised) spectra has changed. """

        if hasattr(self, "_init_text"):
            self._init_text.set_visible(False)

        # Link the key press event if it doesn"t exist already
        if not hasattr(self, "mpl_key_press_event"):
            self.mpl_key_press_event = self.display_spectrum.canvas.mpl_connect("key_press_event", self._on_key_press_event)
            self.mpl_button_press_event = self.display_spectrum.canvas.mpl_connect("button_press_event", self._on_button_press_event)

        # Draw the very first order in the spectrum window
        if hasattr(self, "current_order_index") and self.current_order_index == 0:

            # Force a draw update.
            self._current_order_index_changed(0)

        else:
            self.current_order_index = 0

    
    def _on_button_press_event(self, event):
        """ Handles clicks in the normalisation plots. """

        if not self.mpl_waiting_for_clicks: return None

        self.mpl_clicks.append((event.xdata, event.ydata))
        logger.debug("Current MPL clicks (len = {0}): {1}".format(len(self.mpl_clicks), self.mpl_clicks)) 

        if self.mpl_highlight_region and not hasattr(self, "mpl_motion_notify_event"):
            self.mpl_motion_notify_event = self.display_spectrum.canvas.mpl_connect("motion_notify_event", self._motion_notify_event)

        # Clean up?
        if len(self.mpl_clicks) >= self.mpl_num_clicks_required:
            self.mpl_clicks_callback()

            # Reset everything
            self.mpl_clicks = []
            self.mpl_waiting_for_clicks = False
            self._show_highlighted_region.set_visible(False)
            del self._show_highlighted_region

            if hasattr(self, "mpl_motion_notify_event"):
                self.display_spectrum.canvas.mpl_disconnect(self.mpl_motion_notify_event)
                del self.mpl_motion_notify_event

        

    def _motion_notify_event(self, event):
        """ Updates the drawn excluded region if one point has been selected
        while we are waiting for a second point """

        if len(self.mpl_clicks) == 0: return

        if hasattr(self, "_show_highlighted_region"):
            
            x_i, x_f = self.mpl_clicks[0][0], event.xdata
            self._show_highlighted_region.set_visible(True)
            self._show_highlighted_region.set_xy([[x_i, 0], [x_i, 1], [x_f, 1], [x_f, 0], [1, 0]])

        else:
            self._show_highlighted_region = self.display_spectrum.axes[0].axvspan(self.mpl_clicks[0][0], event.xdata, color="#e69d8a", edgecolor="none")
        
        wx.CallAfter(self.display_spectrum.canvas.draw)
    

    def _on_key_press_event(self, event):
        """ Handles mouse clicks on the normalisation plot """

        logger.debug("Current aperture index: %s, normalisation arguments: %s" % (self.current_order_index, self.normalisation_arguments, ))

        normalisation_args = self.normalisation_arguments[self.current_order_index].copy()

        if event.key == "right":
            new_index = self.current_order_index + 1
            self.current_order_index = np.min([len(self.initial_orders) - 1, new_index])
            return None

        elif event.key == "left":
            new_index = self.current_order_index - 1
            self.current_order_index = np.max([0, new_index])
            return None


        if event.key == "up":
            if "default_text" in normalisation_args and "surface" in normalisation_args["default_text"]:
                self.continuum_orders[self.current_order_index].flux *= (normalisation_args["scale"] + 0.005)/normalisation_args["scale"]
                normalisation_args["scale"] = normalisation_args["scale"] + 0.005

                normalisation_args["default_text"] = normalisation_args["default_text"].split("\n\n")[0] + "\n\nScale: {0:+.2f}%".format((normalisation_args["scale"] - 1) * 100)
                
                self.normalisation_arguments[self.current_order_index] = normalisation_args
                self._redraw_continuum_fit()
                return None

            normalisation_args["scale"] = normalisation_args["scale"] + 0.005
            
            
        elif event.key == "down":
            if "default_text" in normalisation_args and "surface" in normalisation_args["default_text"]:
                self.continuum_orders[self.current_order_index].flux *= (normalisation_args["scale"] - 0.005)/normalisation_args["scale"]
                normalisation_args["scale"] = normalisation_args["scale"] - 0.005     
                normalisation_args["default_text"] = normalisation_args["default_text"].split("\n\n")[0] + "\n\nScale: {0:+.2f}%".format((normalisation_args["scale"] - 1) * 100)
            
                self.normalisation_arguments[self.current_order_index] = normalisation_args
                self._redraw_continuum_fit()
                return None

            normalisation_args["scale"] = normalisation_args["scale"] - 0.005
     
        elif event.key == "a":
            # Add new point with a weight

            # Not valid for surface fits
            if "default_text" in normalisation_args and "surface" in normalisation_args["default_text"]:
                return 

            if not "additional_points" in normalisation_args.keys():
                normalisation_args["additional_points"] = [(event.xdata, event.ydata, self.additional_point_weight)]

                # Fit the continuum and update the text
                normalisation_args["scale"] = 1.0
                normalisation_args["exclude"] = []
                del normalisation_args["default_text"]

            else:
                normalisation_args["additional_points"].append((event.xdata, event.ydata, self.additional_point_weight))
            
        elif event.key == "c":
            # Clear exclude regions and additional points
            normalisation_args["scale"] = 1.0
            normalisation_args["additional_points"] = []
            normalisation_args["exclude"] = []
            if "default_text" in normalisation_args:
                del normalisation_args["default_text"]
            
        elif event.key == "d":
            # Don"t normalise this spectrum.
            logger.info("Forcing no continuum normalisation for this order.")

            disp = self.initial_orders[self.current_order_index].disp
            self.continuum_orders[self.current_order_index] = Spectrum1D(disp=disp, flux=[1.0] * len(disp))
            
            self.normalisation_arguments[self.current_order_index] = {
                "default_text"  : "No continuum normalisation"
            }

            self._redraw_continuum_fit()

            return None

        elif event.key == "e":
            # Exclude a region

            # THis is not valid for surface fits
            if "default_text" in normalisation_args and "surface" in normalisation_args["default_text"]:
                logger.debug("Not excluding region because the normalisation arguments contain 'surface' in the default text")
                return 

            # We need to initialise an event to wait for a mouse click
            self.mpl_waiting_for_clicks = True
            self.mpl_highlight_region = True
            self.mpl_clicks = []
            self.mpl_num_clicks_required = 2
            self.mpl_clicks_callback = self._set_exclude_region
            return None

        elif event.key == "h":
            self.show_shortcuts = not self.show_shortcuts
            if self.show_shortcuts:
                if not hasattr(self, "shortcut_display"):
                    self.shortcut_display = show_keyboard_shortcuts(self.display_spectrum, {
                        "a": "add a weighted continuum point",
                        "e": "select specral region to exclude",
                        "c": "clear exclusion regions and points",
                        "s": "interpolate surface fit",
                        "left": "show bluer aperture",
                        "right": "show redder aperture",
                        "up": "scale continuum fit up by 0.5%",
                        "down": "scale continuum fit down by 0.5%",
                        "d": "don't normalise this aperture",
                        }, extent=[0.15, 0.15, 0.7, 0.7])
                else:
                    self.shortcut_display.set_visible(True)
            else:
                self.shortcut_display.set_visible(False)

            wx.CallAfter(self.display_spectrum.canvas.draw)

        else: return None

        self.normalisation_arguments[self.current_order_index] = normalisation_args
        self._update_continuum_fit()


    def _set_exclude_region(self):
        """ Add an exclusion region. """

        # Each click has (x, y)
        self.normalisation_arguments[self.current_order_index]["exclude"].append(sorted([self.mpl_clicks[0][0], self.mpl_clicks[1][0]]))

        # Update our fit
        self._update_continuum_fit()

   
    def _perform_surface_fit_fired(self):
        """ Performs a surface fit and interpolates the surface to normalise
        the current aperture """

        index = self.current_order_index
        if not (len(self.continuum_orders) >= index + 3 and index > 1):
            logger.warn("Surface fit is not possible: adjacent regions do not exist")
            return False

        # Get dispersion for current order
        interpolated_disp = self.initial_orders[index].disp

        # Build up arrays
        x = np.arange(len(interpolated_disp))
        y = np.array([0, 1, 3, 4])

        Y = np.array([[_]*len(x) for _ in y])
        X = np.array([x for _ in y])
        Z = np.zeros((4, len(x)))

        # Build up flux 
        Z[0, :len(self.continuum_orders[index - 2].flux)] = self.continuum_orders[index - 2].flux
        Z[1, :len(self.continuum_orders[index - 1].flux)] = self.continuum_orders[index - 1].flux
        Z[2, :len(self.continuum_orders[index + 1].flux)] = self.continuum_orders[index + 1].flux
        Z[3, :len(self.continuum_orders[index + 2].flux)] = self.continuum_orders[index + 2].flux

        tck = bisplrep(X, Y, Z, kx=self.surface_kx, ky=self.surface_ky)
        interpolated_flux = bisplev(x, 2, tck).flatten()

        self.normalisation_arguments[index] = {
            "default_text": "Normalised by interpolated surface fit\nof four neighbouring apertures\nwith $k_x\,=\,{0:.0f}$, $k_y\,=\,{1:.0f}$\n\nOnly up/down scaling permitted.".format(
                self.surface_kx, self.surface_ky),
            "scale": 1.0
            }
        self.continuum_orders[index] = Spectrum1D(disp=interpolated_disp, flux=interpolated_flux)
        self._redraw_continuum_fit()


    def _current_order_index_changed(self, index):
        """ Handles the redrawing of a new order. """

        if index < 0 or index - 1 > len(self.initial_orders): return None
        
        axes = self.display_spectrum.axes[0]
        order = self.initial_orders[index]

        # Plot the unnormalised spectra
        if hasattr(self, "_plot_unnormalised_order"):
            self._plot_unnormalised_order[0].set_data(order.disp, order.flux)

        else:
            self._plot_unnormalised_order = axes.plot(order.disp, order.flux, "k")

        # Hide any residual highlighted region
        if hasattr(self, "_show_highlighted_region"):
            self._show_highlighted_region.set_visible(False)
            del self._show_highlighted_region


        # Set limits
        limiting_indices = np.isfinite(order.flux)
        axes.set_xlim(order.disp[np.where(limiting_indices)[0][0]] - 2, 2 + order.disp[np.where(limiting_indices)[0][-1]])
        axes.set_ylim(0, 1.1 * np.max(order.flux[limiting_indices]))
        
        # Which file is current?
        total_num = 0
        for file_num, num in enumerate(self.num_orders_per_filename):
            total_num += num
            if total_num > index:
                break

        # Do we need to do the normalisation?
        if index > len(self.continuum_orders) - 1:

            # We should try a first pass at the continuum fitting
            # Is the mean flux < 2? If so it"s probably already normalised
            if np.mean(order.flux) < 2:
                logger.info("This aperture (number %i of %i) has a mean flux less than 2.0. We are assuming it is already normalised. To fit the continuum, push 'c'. Use 'd' to revert back to no continuum fitting." \
                    % (index + 1, len(self.initial_orders), ))

                continuum = Spectrum1D(disp=order.disp, flux=np.ones(len(order.disp)))
                normalisation_argument = {
                    "default_text": "Order is already normalised (push 'c' to fit continuum)"
                }

            else:

                # Let"s try a first pass normalisation
                normalisation_argument = {
                    "function"          : self.normalisation_function.lower(),
                    "sigma_clip"        : (self.normalisation_sigma_low_clip, self.normalisation_sigma_high_clip),
                    "max_iterations"    : self.normalisation_max_iterations,
                    "order"             : self.normalisation_order,
                    "knot_spacing"      : self.normalisation_knot_spacing,
                    "scale"             : 1.0,
                    "exclude"           : [],
                    "additional_points" : []
                }
                continuum = order.fit_continuum(**normalisation_argument)
            
            self.normalisation_arguments.append(normalisation_argument)
            self.continuum_orders.append(continuum)

        axes.set_title("File: %i / %i, Aperture: %i / %i (%i apertures have continuum fits)" \
        % (file_num + 1, len(self.num_orders_per_filename), index + 1, len(self.initial_orders), len(self.continuum_orders), ))

        # Should we be allowing a surface fit?
        # We need two apertures fitted on either side of the current one
        self.surface_fit_allowed = True if len(self.continuum_orders) >= index + 3 and index > 1 else False

        # Draw the continuum, and all the information related to that (points, excluded regions, etc)
        self._redraw_continuum_fit()


    @on_trait_change("normalisation_function,normalisation_low_sigma_clip,normalisation_sigma_high_clip,normalisation_max_iterations,normalisation_order,normalisation_knot_spacing")
    def _update_continuum_fit(self):
        """ Updates the continuum fitting and plotting """

        if not hasattr(self, "initial_orders") or self.initial_orders is None or len(self.initial_orders) == 0: return

        # Get the current normalisation arguments
        normalisation_arguments = self.normalisation_arguments[self.current_order_index].copy()
        current_normalisation_arguments = {
            "sigma_clip"        : (self.normalisation_sigma_low_clip, self.normalisation_sigma_high_clip),
            "max_iterations"    : self.normalisation_max_iterations,
            "order"             : self.normalisation_order,
            "knot_spacing"      : self.normalisation_knot_spacing,
            "function"          : self.normalisation_function.lower()
            }

        # Update with the controllable values
        for key, value in current_normalisation_arguments.iteritems():
            normalisation_arguments[key] = value

        logger.debug("Updating continuum fit with: %s" % (normalisation_arguments, ))

        # Save this fit
        order = self.initial_orders[self.current_order_index]
        try:
            self.continuum_orders[self.current_order_index] = order.fit_continuum(**normalisation_arguments)
        
        except:
            logger.warn("Could not update continuum with new fit. Re-raising error..")
            raise

        else:
            self.normalisation_arguments[self.current_order_index] = normalisation_arguments

            # Re-draw it
            self._redraw_continuum_fit()


    def _redraw_continuum_fit(self):
        """Re-draws the current order"s continuum fit."""

        logger.debug("Re-drawing continuum fit: %i %s %s" % (self.current_order_index, self.continuum_orders, self.normalisation_arguments, ))

        continuum = self.continuum_orders[self.current_order_index]
        print("CONTINUUM IS ", continuum, len(continuum.disp))
        normalisation_arguments = self.normalisation_arguments[self.current_order_index]
        
        # Update normalisation arguments text
        if "default_text" in normalisation_arguments.keys():
            self._normalisation_args_text.set_text(normalisation_arguments["default_text"])

        else:
            self._normalisation_args_text.set_text("%s (order %i)\n%sSigma clipping: (%1.1f, %1.1f)\n%i iterations\nScale: %1.3f" % (
                normalisation_arguments["function"].replace("poly", "polynomial"),
                normalisation_arguments["order"],
                "%s ${\AA}$ knot spacing\n" % normalisation_arguments["knot_spacing"] if normalisation_arguments["function"] == "spline" else "",
                normalisation_arguments["sigma_clip"][0],
                normalisation_arguments["sigma_clip"][1],
                normalisation_arguments["max_iterations"],
                normalisation_arguments["scale"]
            ))

        # Update weight points
        if "additional_points" in normalisation_arguments.keys() and len(normalisation_arguments["additional_points"]) > 0:
            points = np.array(normalisation_arguments["additional_points"])

            self._normalisation_weights.set_offsets(points[:, :2])

            # This is a hack because MPL doesn"t have set_sizes() for PathCollections
            sizes = self._normalisation_weights.get_sizes()
            sizes = points[:, 2]
            self._normalisation_weights._sizes = sizes

        else:
            self._normalisation_weights.set_offsets([])

        # Update exclusion regions
        if "exclude" in normalisation_arguments.keys() and len(normalisation_arguments["exclude"]) > 0:
            
            for i, region in enumerate(normalisation_arguments["exclude"]):

                start, end = region
                
                if hasattr(self, "_show_excluded_regions") and len(self._show_excluded_regions) > i:
                    self._show_excluded_regions[i].set_xy([[start, 0], [start, 1], [end, 1], [end, 0], [1, 0]])
                    self._show_excluded_regions[i].set_visible(True)

                else:
                    self._show_excluded_regions.append(
                        self.display_spectrum.axes[0].axvspan(start, end, color="#e69d8a", edgecolor="none")
                    )

            # Hide any extra items
            [item.set_visible(False) for item in self._show_excluded_regions[i+1:]]

        elif hasattr(self, "_show_excluded_regions"):
            [item.set_visible(False) for item in self._show_excluded_regions]

        
        # Get the colour for the continuum
        if len(self.num_orders_per_filename) == 2:
            colors = ["blue", "red"]
            color_index = int(self.current_order_index >= self.num_orders_per_filename[0])

            color = colors[color_index]

        else:
            color = "g"

        # Draw the continuum
        if hasattr(self, "_plot_normalised_order"):
            self._plot_normalised_order[0].set_data(continuum.disp, continuum.flux)
            self._plot_normalised_order[0].set_color(color)

        else:
            self._plot_normalised_order = self.display_spectrum.axes[0].plot(continuum.disp, continuum.flux, c=color, lw=2)

        # Create a function for the continuum so we can divide by the normal flux
        f = interp1d(continuum.disp, continuum.flux, fill_value=np.nan, bounds_error=False)

        # Do the preview
        if hasattr(self, "_plot_preview_order"):
            self._plot_preview_order[0].set_data(
                self.initial_orders[self.current_order_index].disp,
                self.initial_orders[self.current_order_index].flux / f(self.initial_orders[self.current_order_index].disp)
                )

        else:
            self._plot_preview_order = self.display_spectrum.axes[1].plot(
                self.initial_orders[self.current_order_index].disp,
                self.initial_orders[self.current_order_index].flux / f(self.initial_orders[self.current_order_index].disp),
                c="#bababa"
                )

        logger.debug("Finished re-drawing continuum fit: %i %s %s" % (self.current_order_index, self.continuum_orders, self.normalisation_arguments, ))

        wx.CallAfter(self.display_spectrum.canvas.draw)


    def _normalised_spectrum_changed(self, spectrum):
        """ Sets the "Normalize and stitch" button label """

        if len(self.initial_orders) == 0 and spectrum is not None:
            self._init_text.set_text("No apertures found, but a full normalised spectrum exists.")
            self._init_text.set_visible(True)
            wx.CallAfter(self.display_spectrum.canvas.draw)

        self.stitch_apertures_label = "Re-Stitch Normalized Spectra"
