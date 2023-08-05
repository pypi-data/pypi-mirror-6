# coding: utf-8

""" Contains code for the quality control GUIs in SMH """

__author__ = "Andy Casey <andy@astrowizici.st>"
__all__ = ["MeasurementQualityConstraints"]

from ..core import *
from gui_core import *

class MeasurementQualityConstraintsDialog(HasTraits):
    """ GUI class to display the number of line transitions that have been
    marked unnacceptable """

    num_affected = Int
    view = View(
        VGroup(
            spring,
            HGroup(
                spring,
                Item("num_affected", show_label=False, format_str="%i rows marked as unacceptable.", style="readonly"),
                spring),
            spring),
        width=250,
        height=100,
        buttons=["OK"],
        title="Information"
        )


class MeasurementQualityConstraintsHandler(Handler):
    """ Handler class for the `MeasurementQualityConstraints` GUI """

    def save_as_default(self, info):
        """ Saves the current measurement quality constraints as local default
        settings for the future """

        info.object.item_changed = False

        keys = "rew_constraint rew_min rew_max fwhm_constraint fwhm_min fwhm_max vrad_constraint vrad_min vrad_max wl_constraint wl_min wl_max sigma_constraint detect_sigma_min".split()
                    
        defaults = {}
        for key in keys:
            defaults[key] = getattr(info.object, key)

        with open(info.object.default_filename, "w") as fp:
            fp.write(json.dumps(defaults))

        logger.info("Default quality constraints saved to {0}".format(info.object.default_filename))


    def setattr(self, info, object, name, value):
        if name != "item_changed":
            object.item_changed = True

        setattr(object, name, value)


    def apply(self, info):
        """ Applies the current measurement quality constraints to the current
        session and marks lines with poor quality as unacceptable """

        if not info.initialized: return None

        logger.debug("Applying filters to %i measurements..." % (len(info.object.measurements), ))

        ta = time()
        num_affected = 0
        for measurement in info.object.measurements:
            if not measurement.is_acceptable \
            or not measurement.measured_equivalent_width > 0: continue

            if (info.object.rew_constraint and (info.object.rew_min > measurement.reduced_equivalent_width or measurement.reduced_equivalent_width > info.object.rew_max)) \
            or (info.object.fwhm_constraint and (info.object.fwhm_min > measurement.measured_fwhm or measurement.measured_fwhm > info.object.fwhm_max)) \
            or (info.object.wl_constraint and (info.object.wl_min > measurement.rest_wavelength or measurement.rest_wavelength > info.object.wl_max)) \
            or (info.object.sigma_constraint and (info.object.sigma_constraint > measurement.detection_sigma)) \
            or (info.object.vrad_constraint and (info.object.vrad_min > measurement.measured_line_velocity or measurement.measured_line_velocity > info.object.vrad_max)): \
                
                # Does not meet quality constraints
                measurement.is_acceptable = False

                num_affected += 1

        # Display the number of rows affected
        information = MeasurementQualityConstraintsDialog()
        information.num_affected = num_affected
        information.configure_traits(kind="modal")

        info.ui.owner.close()


class MeasurementQualityConstraints(HasTraits):
    """ Measurement quality GUI used to quickly mark poor quality lines as
    unnacceptable """

    item_changed = Bool(False)

    # The following defaults are not "hard-coded" in. If a default configuration
    # file exists then it will be loaded when the GUI is initiated

    # Reduced equivalent width constraints
    rew_constraint = Bool(True)
    rew_min = Float(-9.0)
    rew_max = Float(-4.5)

    # Full width half maximum constraints
    fwhm_constraint = Bool(True)
    fwhm_min = Float(0.08)
    fwhm_max = Float(0.16)

    # Radial velocity constraints
    vrad_constraint = Bool(False)
    vrad_min = Float(-4.0)
    vrad_max = Float(4.0)

    # Wavelength constraints
    wl_constraint = Bool(True)
    wl_min = Float(3500.0)
    wl_max = Float(9400.0)

    # Detection sigma constraints
    sigma_constraint = Bool(False)
    detect_sigma_min = Float(2.5)

    default_filename = Str(os.path.join(os.path.dirname(__file__), "../config/quality_constraints.json"))

    view = View(
        VGroup(
            HGroup(
                VGroup(
                    Label("Quality Constraints"),
                    HGroup(
                        "5",
                        Item("rew_constraint", show_label=False),
                        Label(" Reduced equivalent width")
                        ),
                    HGroup(
                        "5",
                        Item("fwhm_constraint", show_label=False),
                        Label(u" FWHM between, (Å)")
                        ),
                    HGroup(
                        "5",
                        Item("vrad_constraint", show_label=False),
                        Label(" Residual line velocity, (km/s)"),
                        ),
                    HGroup(
                        "5",
                        Item("wl_constraint", show_label=False),
                        Label(u" Wavelength, (Å)")
                        ),
                    HGroup(
                        "5",
                        Item("sigma_constraint", show_label=False),
                        Label(" Minimum detection significance")
                        ),
                    ),
                "170",
                spring,
                VGroup(
                    HGroup(
                        spring,
                        Label("Min"),
                        spring),
                    Item("rew_min", width=-50, show_label=False, enabled_when="rew_constraint"),
                    Item("fwhm_min", width=-50, show_label=False, enabled_when="fwhm_constraint"),
                    Item("vrad_min", width=-50, show_label=False, enabled_when="vrad_constraint"),
                    Item("wl_min", width=-50, show_label=False, format_str="%i", enabled_when="wl_constraint"),
                    Item("detect_sigma_min", width=-50, show_label=False, enabled_when="sigma_constraint")
                    ),
                "10",
                VGroup(
                    HGroup(
                        spring,
                        Label("Max"),
                        spring),
                    Item("rew_max", width=-50, show_label=False, enabled_when="rew_constraint"),
                    Item("fwhm_max", width=-50, show_label=False, enabled_when="fwhm_constraint"),
                    Item("vrad_max", width=-50, show_label=False, enabled_when="vrad_constraint"),
                    Item("wl_max", width=-50, show_label=False, format_str="%i", enabled_when="wl_constraint"),
                    )
                ),
            "5",
            HGroup(
                spring,
                Label("Measurements that don\'t meet quality constraints will be marked as unacceptable."),
                spring),
            "5"
            ),
        handler = MeasurementQualityConstraintsHandler(),
        buttons = [Action(name="Apply", action="apply"), Action(name="Save as default", action="save_as_default", enabled_when="item_changed"), "Cancel"],
        title = "Measurement Quality Constraints"
        )

    
    def __init__(self, *args, **kwargs):
       
        if os.path.exists(self.default_filename):
            with open(self.default_filename, "r") as fp:
                try:
                    quality_constraints = json.loads("".join(fp.readlines()))

                except:
                    logger.info("Tried to load default quality constraints from %s but the JSON was malformed." % (self.default_filename, ))

                else:
                    logger.info("Loading quality contraints defaults from %s" % (self.default_filename, ))
                    
                    keys = """rew_constraint rew_min rew_max fwhm_constraint fwhm_min fwhm_max 
                            vrad_constraint vrad_min vrad_max wl_constraint wl_min wl_max sigma_constraint
                            detect_sigma_min""".split()

                    for key in keys:
                        if quality_constraints.has_key(key):
                            setattr(self, key, quality_constraints[key])
