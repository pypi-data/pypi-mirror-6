# coding: utf-8

""" Contains core imports required for the Spectroscopy Made Hard GUI """

__author__ = "Andy Casey <andy@astrowizici.st>"

import matplotlib
import wx

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.pyplot import Figure, subplot
from matplotlib.ticker import MaxNLocator, FuncFormatter

from pyface.api import confirm, GUI, FileDialog, OK, YES

from traitsui.api import \
    Handler, HSplit, HFlow, View, VSplit, ButtonEditor, EnumEditor, \
    Action, Label, Item, Group, HGroup, InstanceEditor, VGroup, Menu, \
    MenuBar, ImageEditor, FileEditor, TableEditor, TextEditor, Tabbed, \
    TabularEditor, ToolBar, TitleEditor, UItem, spring, VGrid

# Custom columns for the ArrayEditor
from traitsui.extras.checkbox_column import CheckboxColumn
from traitsui.table_column import ObjectColumn, NumericColumn

# Editor factories for matplotlib figures
from traitsui.wx.editor import Editor
from traitsui.wx.basic_editor_factory import BasicEditorFactory



class _MPLFigureEditor(Editor):
    """ Editor class for containing a matplotlib figure within a
    TraitsUI GUI window """

    scrollable  = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the matplotlib canvas """

        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        
        mpl_control = FigureCanvasWxAgg(panel, -1, self.value)
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar2Wx(mpl_control)
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((10,10))
        
        return panel


class MPLFigureEditor(BasicEditorFactory):
    """ Factory class for generating editors that contain matplotlib
    figures and can be placed within a TraitsUI GUI """
    klass = _MPLFigureEditor


def show_keyboard_shortcuts(figure, shortcuts, extent=[0.2, 0.2, 0.6, 0.6],
    two_columns=True, **kwargs):
    """ Shows a help dialogue of keyboard shortcuts for the present
    figure 

    Parameters
    ----------

    figure : `~matplotlib.pyplot.figure`
        The figure to display shortcuts for.

    shortcuts : dict
        A dictionary describing the short cut keys (as dictionary
        keys) and text describing each short cut as values.
    """

    axes = figure.add_axes(extent)
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    axes.set_axis_bgcolor("#eeeeee")
    axes.text(0.5, 0.9, "Keyboard Shortcuts", horizontalalignment="center",
        verticalalignment="center", weight="bold")

    spacing = {
        "x": 0.10, "y": 0.10,
        "top": 0.30,
        "left_col": 0.10,
        "right_col": 0.55
    }
    spacing.update(kwargs)

    s_shortcuts = sorted(shortcuts.keys())
    rs_shortcuts = []
    for shortcut in s_shortcuts:
        if len(shortcut) == 1: rs_shortcuts.append(shortcut)

    for shortcut in s_shortcuts:
        if len(shortcut) > 1: rs_shortcuts.append(shortcut)

    for i, shortcut in enumerate(rs_shortcuts):

        description = shortcuts[shortcut]
        if two_columns:
            x_pos = [spacing["left_col"], spacing["right_col"]][i % 2]
            y_pos = 1 - (spacing["top"] + int(i/2) * spacing["y"])
        else:
            x_pos = spacing["left_col"]
            y_pos = 1 - (spacing["top"] + i * spacing["y"])
        axes.text(x_pos, y_pos, shortcut, weight="bold", verticalalignment="top")
        axes.text(x_pos + spacing["x"], y_pos, description, verticalalignment="top")

    axes.text(spacing["left_col"], spacing["y"], "h", weight="bold")
    axes.text(spacing["left_col"] + spacing["x"], spacing["y"], "toggle this shortcut window")

    return axes
    