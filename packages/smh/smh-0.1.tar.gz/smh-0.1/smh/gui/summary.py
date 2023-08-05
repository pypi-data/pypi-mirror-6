# coding: utf-8

""" Contains code for the summary tab in the main SMH GUI. """

__author__ = "Andy Casey <andy@astrowizici.st>"

__all__ = ["SummaryTab", "SummaryAbundancesDialog"]

# Module specific imports
from ..core import *
from ..session import Session
from ..isochrones import load as load_isochrone
from ..utils import extend_limits

from gui_core import *
from traitsui.wx.text_editor import ReadonlyEditor
from traitsui.editors.text_editor import ToolkitEditorFactory


class _MyTextEditor(ReadonlyEditor):
    def init(self, parent):
        ReadonlyEditor.init(self, parent)
        font = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.control.SetFont(font)

class MyTextEditor(ToolkitEditorFactory):
    klass = _MyTextEditor
    def _get_custom_editor_class(self):
        return _MyTextEditor
    def _get_simple_editor_class(self):
        return _MyTextEditor


class _ObjectEditor(ReadonlyEditor):
    def init(self, parent):
        ReadonlyEditor.init(self, parent)
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.control.SetFont(font)

class ObjectEditor(ToolkitEditorFactory):
    klass = _ObjectEditor
    def _get_custom_editor_class(self):
        return _ObjectEditor
    def _get_simple_editor_class(self):
        return _ObjectEditor


class AbundanceMeasurement(HasTraits):
    representation = Str
    num_measurements = Int
    solar_abundance = Float
    log_eps = Float
    nlte_log_eps = Float
    X_on_H = Float
    X_on_Fe = Float
    X_on_H_err = Float
    X_on_Fe_err = Float

class SummaryAbundancesDialogHandler(Handler):
    """ A handler for the SummaryAbundancesDialog class """

    def export(self, info):
        """ Export the summary abundance table to disk """

        ext = ".{0}".format(info.object.format.lower()) if info.object.format.lower() != "ascii" else ""
        dialog = FileDialog(action="save as", wildcard="*" + ext, title="Save abundance summary")
        dialog.open()

        if dialog.return_code != OK: return False

        output_filename = os.path.join(dialog.directory, dialog.filename)

        if not output_filename.endswith(ext): output_filename += ext
        info.object.session.export_abundance_summary(output_filename, format=info.object.format)

    def close(self, info, is_ok=True):
        """ Close the dialog """
        info.ui.owner.close()


class SummaryAbundancesDialog(HasTraits):
    """ Class for viewing a summary of all abundances and exporting them to disk """

    title = Str("Abundances Summary")
    abundances = List(AbundanceMeasurement)
    show_measurement_type = Enum("All measurements", "Equivalent widths only", "Syntheses only")
    format = Enum("TeX", "ASCII", "CSV")

    abundances_editor = TableEditor(
        columns=[
            ObjectColumn(name="representation", label="Element", editable=False),
            NumericColumn(name="num_measurements", label="N", editable=False),
            NumericColumn(name="solar_abundance", label="Solar", editable=False, format="%+1.2f"),
            NumericColumn(name="log_eps", label="log(X)", editable=False, format="%+1.2f"),
            NumericColumn(name="nlte_log_eps", label="log(X) (n-LTE)", editable=False, format="%+1.2f"),
            NumericColumn(name="X_on_H", label="[X/H]", editable=False, format="%+1.2f"),
            NumericColumn(name="X_on_Fe", label="[X/Fe]", editable=False, format="%+1.2f"),
            NumericColumn(name="X_on_H_err", label="[X/H]_err", editable=False, format="%1.2f"),
            NumericColumn(name="X_on_Fe_err", label="[X/Fe]_err", editable=False, format="%1.2f"),
            ],
            auto_size = False,
            auto_add = False,
            deletable = False,
            sortable = False,
            configurable = False,
            orientation = "vertical",
            show_column_labels = True,
            reorderable = False,
        )

    view = View(
        VGroup(
            HGroup(Item("title",
                show_label=False,
                springy=True,
                editor=TitleEditor()
                )),
            Item("abundances", editor=abundances_editor, show_label=False, padding=5),
            HGroup(
                spring,
                Item("format", label="Export format", padding=5)
                )
            ),
        title="Abundances Summary",
        buttons=[
            Action(name="Save to file..", action="export"),
            Action(name="Done", action="close")
            ],
        handler=SummaryAbundancesDialogHandler(),
        width=600,
        height=700,
        resizable=True
        )

    def __init__(self, session):
        HasTraits.__init__(self)
        self.session = session

        abundances = []
        for element, number_of_lines, solar_abundance, abundance_mean, nlte_abundance_mean, X_on_H, \
            X_on_Fe, X_on_H_err, X_on_Fe_err in session.abundance_summary():
            abundances.append(AbundanceMeasurement(
                representation=element, num_measurements=number_of_lines, solar_abundance=solar_abundance,
                log_eps=abundance_mean, nlte_log_eps=nlte_abundance_mean, X_on_H=X_on_H, X_on_Fe=X_on_Fe,
                X_on_H_err=X_on_H_err, X_on_Fe_err=X_on_Fe_err
                ))

        self.abundances = abundances






class SummaryTab(HasTraits):
    """ Class for the Summary tab view of the SMH GUI """
    
    session = Instance(Session)    

    object_name = DelegatesTo("session")
    ra_repr = DelegatesTo("session")
    dec_repr = DelegatesTo("session")

    ra_label =  Str("Right ascension:  ")
    dec_label = Str("Declination:      ")

    figure = Instance(Figure)

    stellar_teff = DelegatesTo("session")
    stellar_logg = DelegatesTo("session")
    stellar_vt = DelegatesTo("session")

    stellar_teff_uncertainty = DelegatesTo("session")
    stellar_logg_uncertainty = DelegatesTo("session")
    stellar_vt_uncertainty = DelegatesTo("session")
    stellar_atmosphere_filename = DelegatesTo("session")

    title = Str("Notes")
    notes = DelegatesTo("session")
    
    traits_view = View(
        HGroup(
            VGroup(
                HGroup(
                    Item("object_name", show_label=False, padding=5, editor=ObjectEditor()),
                    spring,
                    ),
                HGroup(
                    Item("ra_label", show_label=False, padding=5, editor=MyTextEditor()),
                    Item("ra_repr", show_label=False, padding=5, editor=MyTextEditor()),
                    spring
                    ),
                HGroup(
                    Item("dec_label", show_label=False, padding=5, editor=MyTextEditor()),
                    Item("dec_repr", show_label=False, padding=5, editor=MyTextEditor()),
                    spring
                    ),
                Group(Item("title",
                    show_label = False,
                    springy    = True,
                    editor     = TitleEditor()
                )),
                Item("notes", style="custom", width=800, editor=TextEditor(multi_line=True, auto_set=True), show_label=False),
                ),
            Group(Item("figure", editor=MPLFigureEditor(), show_label=False))
        ),
    )
    

    def __init__(self, session, *args, **kwargs):
        HasTraits.__init__(self)    
        self.session = session


    def update_hr_point(self):
        """ Updates the point on the stellar parameters tab """

        # Do nothing if we haven't done a model atmosphere yet
        if self.stellar_atmosphere_filename is None: return

        if hasattr(self, "_show_star"):
            for child in self._show_star.get_children():
                child.set_visible(False)
            del self._show_star

        self._init_text[0].set_visible(False)
        teff_err = [self.stellar_teff_uncertainty] if hasattr(self, "stellar_teff_uncertainty") \
            and self.stellar_teff_uncertainty is not None else None
        logg_err = [self.stellar_logg_uncertainty] if hasattr(self, "stellar_logg_uncertainty") \
            and self.stellar_logg_uncertainty is not None else None
        self._show_star = self.figure.axes[0].errorbar([self.stellar_teff], [self.stellar_logg], 
            marker="o", xerr=teff_err, yerr=logg_err, color="k", ecolor="k")
        

    def update_vt_point(self):
        """ Updates the point on the microturbulence/surface gravity plot """

        if self.stellar_atmosphere_filename is None: return
        
        if hasattr(self, "_show_star_on_vt"):
            for child in self._show_star_on_vt.get_children():
                child.set_visible(False)
            del self._show_star_on_vt

        self._init_text[1].set_visible(False)
        vt_err = [self.stellar_vt_uncertainty] if hasattr(self, "stellar_vt_uncertainty") \
            and self.stellar_vt_uncertainty is not None else None        
        logg_err = [self.stellar_logg_uncertainty] if hasattr(self, "stellar_logg_uncertainty") \
            and self.stellar_logg_uncertainty is not None else None
        self._show_star_on_vt = self.figure.axes[1].errorbar([self.stellar_logg], [self.stellar_vt],
            marker="o", xerr=logg_err, yerr=vt_err, color="k", ecolor="k")
        

    def _stellar_teff_changed(self, stellar_teff):
        self.update_hr_point()
        wx.CallAfter(self.figure.canvas.draw)

    def _stellar_logg_changed(self, stellar_logg):
        self.update_hr_point()
        self.update_vt_point()
        wx.CallAfter(self.figure.canvas.draw)

    def _stellar_vt_changed(self, stellar_vt):
        self.update_vt_point()
        wx.CallAfter(self.figure.canvas.draw)

    def _stellar_teff_uncertainty_changed(self, stellar_teff_uncertainty):
        self.update_hr_point()
        wx.CallAfter(self.figure.canvas.draw)

    def _stellar_logg_uncertainty_changed(self, stellar_logg_uncertainty):
        self.update_hr_point()
        self.update_vt_point()
        wx.CallAfter(self.figure.canvas.draw)

    def _stellar_vt_uncertainty_changed(self, stellar_vt_uncertainty):
        self.update_vt_point()
        wx.CallAfter(self.figure.canvas.draw)
        
    
    def _figure_default(self):
        """ Initialises the stellar parameter diagnostic plots """
        
        figure = Figure()
        figure.subplots_adjust(left=0.10, bottom=0.10, right=0.52, top=0.95, wspace=0.20, hspace=0.20)
        
        ax = figure.add_subplot(2, 1, 1)
        ax.set_xlabel("Effective temperature, $T_{\\rm eff}$ (K)")
        ax.set_ylabel("Surface gravity, $\log{g}$ (cm s$^{-2}$)")
        ax.xaxis.set_major_locator(MaxNLocator(6))
        ax.yaxis.set_major_locator(MaxNLocator(6))

        self._show_star = ax.errorbar([], [])

        # Astronomers are nuts
        ax.invert_xaxis()
        ax.invert_yaxis()

        self._init_text = [ax.text(0.5, 0.5, "No stellar parameters sampled.",
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=11,
                transform=ax.transAxes)]
        
        ax = figure.add_subplot(2, 1, 2, sharey=ax)
        ax.set_xlabel("Surface gravity, $\log{g}$ (cm s$^{-2}$)")
        ax.set_ylabel("Microturbulence, $v_{t}$ (km s$^{-1}$)")
        ax.xaxis.set_major_locator(MaxNLocator(6))
        ax.yaxis.set_major_locator(MaxNLocator(6))

        self._init_text.append(ax.text(0.5, 0.5, "No stellar parameters sampled.",
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=11,
                transform=ax.transAxes))
        
        # Set matplotlib canvas colour to be white
        rect = figure.patch
        rect.set_facecolor("w")

        # If we have a isochrone in the settings, load it.
        # (The isochrone is not a trait)
        if hasattr(self.session, "show_isochrone"):
            # It should be relative to the main SMH directory
            isochrone_filename = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "../../",
                self.session.show_isochrone))

            if os.path.exists(isochrone_filename):
                isochrone_data, isochrone_metadata = load_isochrone(isochrone_filename)[-1]

                self._init_text[0].set_visible(False)
                teffs, loggs = 10**isochrone_data["LogTeff"], isochrone_data["LogG"]

                teff_limits = extend_limits(teffs)
                logg_limits = extend_limits(loggs)

                axes = figure.axes[0]
                axes.plot(teffs, loggs, c="k")
                axes.set_xlim(teff_limits[::-1])
                axes.set_ylim(logg_limits[::-1])
                title = "{source} {age:.1f} Gyr isochrone with [Fe/H] = ${feh:.1f}$".format(
                    source=isochrone_metadata["SOURCE"], age=isochrone_metadata["AGE"], feh=isochrone_metadata["[Fe/H]"])
                axes.set_title(title, fontsize=11)
                
            else:
                logger.warn("Could not find isochrone at {0}".format(isochrone_filename))
        else:
            figure.axes[0].set_xlim(8000, 4000)
            figure.axes[0].set_ylim(5, 0)

        return figure

        
