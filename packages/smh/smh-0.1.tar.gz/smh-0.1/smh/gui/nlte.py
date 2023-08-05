# coding: utf-8

""" Automatic non-LTE corrections dialog for Spectroscopy Made Hard """

__author__ = "Andy Casey <andy@astrowizici.st>"

__all__ = ["AutomaticNonLTECorrections"]

# Package imports
from ..core import *
from ..session import Session
from gui_core import *


class NonLTECorrectionSetup(HasTraits):

    periodic_table = """H                                                  He
                        Li Be                               B  C  N  O  F  Ne
                        Na Mg                               Al Si P  S  Cl Ar
                        K  Ca Sc Ti V  Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
                        Rb Sr Y  Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I  Xe
                        Cs Ba Lu Hf Ta W  Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn
                        Fr Ra Lr Rf Db Sg Bh Hs Mt Ds Rg Cn UUt"""
    
    lanthanoids    =   "La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb"
    actinoids      =   "Ac Th Pa U  Np Pu Am Cm Bk Cf Es Fm Md No"
    
    periodic_table = periodic_table.replace(" Ba ", " Ba " + lanthanoids + " ") \
        .replace(" Ra ", " Ra " + actinoids + " ").split()
    del actinoids, lanthanoids

    element = Enum("Fe", values="periodic_table")
    grid_filename = File(filter=["*.sav"], exists=True)


class MessageDialog(HasTraits):
    """ A basic message dialog """

    message = Str
    view = View(
        VGroup(
            spring,
            HGroup(spring, Item("message", style="readonly", springy=True, show_label=False), spring),
            spring,
            ),
        buttons=["OK"],
        title="Error in non-LTE Correction Setups",
        width=200,
        height=150
        )


def show_message(message):
    return MessageDialog(message=message).configure_traits(kind="modal")


class AutomaticNonLTECorrectionsHandler(Handler):
    """ Handler for the AutomaticNonLTECorrections class """

    def apply_setups(self, info):
        """ Checks and applies the edited setups to the current session """

        # Check the setups
        setups = {}
        for correction_setup in info.object.corrections:
            element, grid_filename = correction_setup.element, correction_setup.grid_filename

            if element in setups:
                show_message("Multiple entries for {0}!".format(element))
                return True

            if grid_filename is None or len(grid_filename) == 0:
                show_message("No grid filename provided for {0}!".format(element))
                return True

            if not os.path.exists(grid_filename):
                show_message("Grid filename for {0} does not exist:\n{1}".format(element, grid_filename))
                return True

            if not grid_filename.endswith(".sav"):
                show_message("Grid filename for {0} is not valid.".format(element))
                return True 

            setups[element] = grid_filename

        # Apply the settings to the session
        info.object.session.automatic_nlte_corrections = setups
        
        try:    info.ui.owner.close()
        except: None
        

class AutomaticNonLTECorrections(HasTraits):
    """ A class for editing the automatic non-LTE corrections to apply
    for this current session. """

    corrections = List(NonLTECorrectionSetup)
    corrections_editor = TableEditor(
        columns = [
            ObjectColumn(name="element", label="Element", editable=True, width=80),
            ObjectColumn(name="grid_filename", label="Pre-Computed Grid of non-LTE Corrections", editable=True)
        ],
        edit_view_width = 400,
        edit_view_height = 200,
        auto_size = False,
        auto_add = False,
        deletable = True,
        sortable = False,
        configurable = False,
        orientation = "vertical",
        show_column_labels = True,
        show_toolbar = True,
        reorderable = True,
        row_factory = NonLTECorrectionSetup
        )

    view = View(
        VGroup(
            Item("corrections", editor=corrections_editor, show_label=False)
            ),
        handler=AutomaticNonLTECorrectionsHandler(),
        buttons=[Action(name=" Apply ", action="apply_setups"), "Cancel"],
        title="Automatic non-LTE Corrections for Current Session",
        width=400,
        height=200
        )

    def __init__(self, session):
        HasTraits.__init__(self)

        # Load in the dict to something viewable

        corrections = []
        for element, grid_filename in session.automatic_nlte_corrections.iteritems():
            corrections.append(NonLTECorrectionSetup(element=element, grid_filename=grid_filename))

        self.session = session
        self.corrections = corrections
