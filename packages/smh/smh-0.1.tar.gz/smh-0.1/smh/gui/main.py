# coding: utf-8

""" Main application GUI for Spectroscopy Made Hard """

__author__ = "Andy Casey <andy@astrowizici.st>"
__all__ = ["application"]

# Package imports
from ..core import *
from ..utils import get_version, find_common_start
from ..session import Session

from gui_core import *
import plotting
from tabs import SummaryTab, NormalisationTab, DopplerCorrectTab,     \
    EquivalentWidthsTab, StellarParametersTab, ChemicalAbundancesTab, \
    SynthesisTab

from summary import SummaryAbundancesDialog
from nlte import AutomaticNonLTECorrections

class NewSessionFile(HasTraits):
    """A tabular item to represent a selected filename that may
    have some ambiguity to it. In essence, we don't *exactly*
    know how to open all the files without some explicit direction."""
    
    path = Str
    basename = Str
    dirname = Str
    file_type = Str
    data_index = Str
    snr_index = Str

    def _path_changed(self, path):
        self.basename = os.path.basename(path)
        self.dirname = os.path.dirname(path)

    def _extension_range_changed(self, extension_range):
        self.extension_range_values = range(extension_range)

    def _data_index_changed(self, data_index):
        if not self.file_type.startswith("Multi-ext.") and data_index != "N/A":
            self.data_index = "N/A"

    def _snr_index_changed(self, snr_index):
        if not self.file_type.startswith("Multi-ext.") and snr_index != "N/A":
            self.snr_index = "N/A"


class NewSessionFileHandler(Handler):

    def continue_to_load(self, info):
        """ Closes the `NewSessionFileLoader` dialog """
        info.object.continue_load_check = True
        info.ui.owner.close()


class NewSessionFileLoader(HasTraits):
    """ Class to deal with ambiguity when loading spectra """

    files = List(NewSessionFile)
    continue_load_check = Bool(False)

    files_editor = TableEditor(

        columns = [
            ObjectColumn(name="basename", label="Filename", editable=False),
            ObjectColumn(name="file_type", label="Type", editable=False),
            ObjectColumn(name="data_index", label="Data Ext.", editable=True),
            ObjectColumn(name="snr_index", label="SNR Ext.", editable=True),
            ObjectColumn(name="dirname", label="Folder", width=0.20, editable=False),
        ],
        auto_size           = True,
        deletable           = False,
        configurable        = False,
        orientation         = "vertical",
        selection_mode      = "row",
        show_column_labels  = True,
        show_toolbar        = False,
        reorderable         = False,
        )

    view = View(
        Item("files", editor=files_editor, show_label=False),
        handler   = NewSessionFileHandler(),
        buttons   = [Action(name="Continue to load spectra", action="continue_to_load"), "Cancel"],
        width     = 500,
        height    = 250,
        title     = "Verify adopted data extensions",
        resizable = True,
        kind      = "livemodal")

    def __init__(self, path_information, **kwargs):
        HasTraits.__init__(self)

        files_list = []
        for path_info in path_information:
            files_list.append(NewSessionFile(**path_info))

        self.files = files_list


class ApplicationMainHandler(Handler):
    """ GUI handler for the `ApplicationMain` class """

    def on_help_call(self, info):
        logger.info("Email Andy (andy@astrowizici.st) for help.")

    def object_title_str_changed(self, info):
        info.ui.title = info.object.title_str

    def new_session(self, info):
        """ Initiates a new session """
        
        if not info.initialized: return
        
        # Find me some spectra!
        wildcard = FileDialog.create_wildcard("Any spectrum files", ["*.fits", "*.txt", "*.csv", "*.data"])
        dialog = FileDialog(action="open", wildcard=wildcard, title="Select spectra for new session")
        dialog.open()

        # Are you OK?
        if dialog.return_code != OK: return

        # Check the current state of the session
        existing_apertures = hasattr(info.object.session, "initial_orders") and len(info.object.session.initial_orders) > 0

        # Create a new session!
        fresh_session = Session()
        
        # Load the spectra into the new session
        any_ambiguity, path_information = fresh_session.load_spectra(dialog.paths)
        
        if len(path_information) == 0:
            logger.warn("No files loaded!")
            return False

        # If the result is False, then that means there was some ambiguity about how to load the spectra,
        # and we will need to load the NewSessionFileLoader() GUI class.
        if not any_ambiguity:

            explicit_dialog = NewSessionFileLoader(path_information)
            explicit_dialog.configure_traits(kind="livemodal")

            # Ensure the "Continue to load spectra" button was pushed
            if not hasattr(explicit_dialog, "continue_load_check") or not explicit_dialog.continue_load_check:
                return

            for load_file in explicit_dialog.files:
                for i, path_info in enumerate(path_information):
                    if path_info["path"] == load_file.path and load_file.file_type.startswith("Multi-ext."):
                        
                        # Update path_information with the data and SNR index.
                        path_information[i]["data_index"] = load_file.data_index
                        path_information[i]["snr_index"] = load_file.snr_index

            # At this stage we are only continuing if the "Continue load check" button was clicked in the
            # explicit dialog

            filenames_to_load = [item["path"] for item in path_information]
            data_indices = [int(item["data_index"]) for item in path_information]

            any_ambiguity_again, path_information = fresh_session.load_spectra(filenames_to_load, data_indices)

            if not any_ambiguity_again:
                logger.warn("I can't help you - I tried twice. You should email Andy about this.")
                
                raise TypeError

        # It looks like we will replace the session with the new_session...

        logger.info("Loaded spectra with the following information:")
        for path_info in path_information:
            logger.info(path_info)


        # Update the plots, post-normalisation
        tabs = ("normalisation", "doppler_correct", "equivalent_widths", "stellar_parameters", "abundances")
        for tab in tabs:
            getattr(info.object, tab)._clean_display()
        
        # Let"s get a common base name from the path information
        basenames = [os.path.basename(item["path"]).lower() for item in path_information]
        common_basename = find_common_start(basenames)
        common_basename = common_basename if len(common_basename) > 0 else "Untitled"

        # Set the title
        info.ui.title = "Spectroscopy Made Hard - %s" % (common_basename, )

        # Did the old session have a TWD? If so, clean it up.
        #info.object.session.clean_up()

        # Set the current session as the fresh session
        
        # Transfer of traits to new session.
        ignore_keys = ("normalisation_arguments", "initial_orders", )
        delete_keys = []
        for key in info.object.session.__dict__:

            if key in ignore_keys: continue

            if key.startswith("__"):
                logger.warn("Ignoring %s" % (key, ))

            if key in fresh_session.__dict__:
                new_value = getattr(fresh_session, key)

                logger.info("Applying %s to new session..." % (key, ))
                setattr(info.object.session, key, new_value)

            else:
                delete_keys.append(key)

        for key in delete_keys:
            delattr(info.object.session, key)        

        # End with initial orders!
        setattr(info.object.session, "initial_orders", getattr(fresh_session, "initial_orders"))
    

    def open_session(self, info):
        """ Opens a file select dialog to open an existing session file """

        if not info.initialized: return
        
        dialog = FileDialog(action="open", wildcard="*.smh", title="Open session")
        dialog.open()
        
        if dialog.return_code == OK:

            filename = os.path.join(dialog.directory, dialog.filename)
            info.object.session.load(filename)
            
            # Set the title
            info.ui.title = "Spectroscopy Made Hard - %s" % (os.path.basename(filename), )

            # Update some plots
            # TODO - we shouldn"t have to do this here.
            info.object.stellar_parameters._update_display_trends(force=True)


    def save_session(self, info):
        """ Saves the session either to the existing session file, or to a
        new filename. """

        if not info.initialized: return
        
        ta = time()

        # Have we saved this session already?
        if hasattr(info.object.session, "save_as_filename"):
            logger.info("Saving to %s" % (info.object.session.save_as_filename, ))
            info.object.session.save_as(info.object.session.save_as_filename, True)
            
        else:
            self.save_as_session(info)


    def save_as_session(self, info):
        """ Save current session to a new filename. """
        
        if not info.initialized: return
        
        dialog = FileDialog(action="save as", wildcard='*.smh', title='Save session as..')
        dialog.open()

        if dialog.return_code == OK:
            filename = os.path.join(dialog.directory, dialog.filename)
            info.object.session.save_as(filename)
            info.ui.title = "Spectroscopy Made Hard - %s" % (os.path.basename(filename), )

            return True
    

    def quit_session(self, info):
        """ Re-directs to close. """
        self.close(info, None)


    def close(self, info, is_ok):
        """ Confirms whether the user wants to quit the program, and if so, exits """
        
        if not info.initialized: return
        
        # Are you sure?
        response = confirm(info.ui.control, "Are you sure you want to quit?")
        if response == YES:
            self.cleanup(info)
            info.ui.owner.close()
    
    
    def cleanup(self, info):
        """ Cleans up the session before closing """
        info.object.session.clean_up()


    def automatic_nlte_corrections(self, info):
        """ Loads the GUI for automatic non-LTE corrections """

        automatic_corrections = AutomaticNonLTECorrections(info.object.session)
        automatic_corrections.configure_traits(kind="modal")


    def introduce_literature_line_list(self, info):
        """ Allows you to introduce a line list with measured 
        equivalent widths from an external source. """

        # TODO this should go into the session

        if not info.initialized: return
        
        dialog = FileDialog(action="open", wildcard="*", title="Introduce literature line list")
        dialog.open()

        if dialog.return_code == OK:

            filename = os.path.join(dialog.directory, dialog.filename)
            
            if not os.path.exists(filename):
                raise IOError("Cannot load line list %s, the path does not exist." \
                              % (filename, ))
        
            # We cannot use np.loadtxt because some lines may have Van der Waals
            # broadening and/or comments
            
            num_added = 0
            measurements = []
            with open(filename, 'r') as fp:
                
                lines = fp.readlines()
                
                for i, line in enumerate(lines):
                    
                    line = line.split()
                    
                    # Skip the first line in keeping with status quo
                    try:
                        wavelength, transition, lep, loggf = map(float, line[:4])

                    except:
                        if i == 0: continue

                        else:
                            raise ValueError("Improper line in line list at line #%i." \
                                % (i + 1, ))


                    vdw, comment = None, None
                    if len(line) > 4:
                        # Van der Waals broadening?
                        try:
                            vdw = float(line[4])
                            
                        except TypeError as e:
                            # No; must be a comment
                            comment = ' '.join(line[4:])
                        
                        else:
                            if len(line) > 5:
                                comment = ' '.join(line[5:])
                                
                    kwargs = {
                        'rest_wavelength': wavelength,
                        'transition': transition,
                        'excitation_potential': lep,
                        'oscillator_strength': loggf,
                        'vanderwaal_broadening': vdw,
                        'comment': comment
                    }
                    
                    if comment is None: del kwargs['comment']
                    if vdw is None: del kwargs['vanderwaal_broadening']
                    
                    measurements.append(AtomicTransition(**kwargs))
                    
                    num_added += 1
            
            info.object.session.measurements = measurements


    # Plotting functions
    def plot_emp_summary_page(self, info):
        """ Shows the summary page plot """

        if not info.initialized \
        or info.object.session.rest_spectrum is None: return
        dialog = plotting.EMPSummaryDialog(info.object.session)
        dialog.configure_traits(kind="modal")


    def plot_measurements(self, info):
        """ Loads the measurement scatter plot GUI. """

        if not info.initialized \
        or len(info.object.session.measurements) == 0: return
        dialog = plotting.MeasurementsPlotDialog(info.object.measurements)
        dialog.configure_traits(kind="modal")


    def plot_snr_spectrum(self, info):
        """ Shows a dialog displaying the S/N spectrum """

        if not info.initialized \
        or info.object.session.snr_spectrum is None: return

        print("SNR SPECTRUM IS", info.object.session.snr_spectrum)
        print(info.object.session.snr_spectrum.flux)
        dialog = plotting.SNRSpectrumDialog(info.object.session.snr_spectrum)
        dialog.configure_traits(kind="modal")


    def export_to_database(self, info):
        """ Loads the GUI for exporting results to a database """

        if not info.initialized: return
        dialog = DatabaseConnectionGUI(info.object.session)
        dialog.configure_traits(kind="modal")


    def select_line_list(self, info):
        """ Opens dialog to select a new line list to load """

        if not info.initialized: return
        dialog = FileDialog(action="open", wildcard="*", title="Select line list")
        dialog.open()

        if dialog.return_code == OK:
            filename = os.path.join(dialog.directory, dialog.filename)
            info.object.session.load_line_list(filename)


    def extend_line_list(self, info):
        """ Opens a dialog for selecting a line list to extend the current list """
        
        if not info.initialized: return
        dialog = FileDialog(action="open", wildcard="*", title="Extend line list")
        dialog.open()

        if dialog.return_code == OK:
            filename = os.path.join(dialog.directory, dialog.filename)
            info.object.session.extend_line_list(filename)


    def export_normalised_spectrum(self, info):
        """ Saves the normalised spectrum to a selected filename """

        if not info.initialized \
        or info.object.session.normalised_spectrum is None: return
        dialog = FileDialog(action="save as", wildcard="*.fits", title="Save normalised spectrum")
        dialog.open()

        if dialog.return_code == OK:
            filename = os.path.join(dialog.directory, dialog.filename)
            info.object.session.normalised_spectrum.save(filename)
            logger.info("Normalised spectrum saved to %s" % (filename, ))
            

    def export_model_atmosphere(self, info):
        """ Saves the model atmosphere to a selected filename """

        if not info.initialized \
        or not os.path.exists(info.object.session.stellar_atmosphere_filename): return
        dialog = FileDialog(action="save as", wildcard="*.model", title="Save atmosphere model")
        dialog.open()

        if dialog.return_code == OK:
            filename = os.path.join(dialog.directory, dialog.filename)

            try:
                shutil.copyfile(info.object.session.stellar_atmosphere_filename, filename)
            except shutil.Error as reason:
                logger.warn("Error when copying file %s to %s: %s" % (info.object.session.stellar_atmosphere_filename, filename, ))
            else:
                logger.info("Model atmosphere saved to %s" % (filename, ))


    def export_rest_spectrum(self, info):
        """ Saves the rest spectrum to a selected filename """

        if not info.initialized \
        or info.object.session.rest_spectrum is None: return
        dialog = FileDialog(action="save as", wildcard="*.fits", title="Save rest spectrum")
        dialog.open()

        if dialog.return_code == OK:
            filename = os.path.join(dialog.directory, dialog.filename)

            info.object.session.rest_spectrum.save(filename)
            logger.info("Rest spectrum saved to %s" % (filename, ))


    def export_measured_properties(self, info):
        """ Loads the GUI for exporting measured properties """

        dialog = export.PropertiesTable()
        dialog.configure_traits(kind="modal")


    def export_equivalent_widths(self, info):
        """ Loads the GUI for exporting equivalent width measurements """

        dialog = export.EquivalentWidthTable(info.object.session)
        dialog.configure_traits(kind='modal')


    def export_chemical_abundances(self, info):
        """ Export a table of chemical abundance ratios """

        dialog = SummaryAbundancesDialog(info.object.session)
        dialog.configure_traits(kind="modal")

        return None
        # TODO this should go to session in a ChemicalAbundances attribute for __repr__ or something
        dialog = FileDialog(action="save as", wildcard='*', title='Export chemical abundances')
        dialog.open()
        
        if dialog.return_code != OK: return False

        output_filename = os.path.join(dialog.directory, dialog.filename)
        
        with open(output_filename, 'w') as fp:

            fp.write("# Element        Num.  log(X)    sigma(X)  [X/H]     [X/Fe]    Uncertainty\n")
            for element in info.object.session.elemental_abundances:

                element_str = element.element.split()
                element_str[1] = '\\textsc{%s}' % (element_str[1], )
                element_str = ' '.join(element_str)

                log_X = '\\nodata' if element.number_of_lines == 0 else ('%1.2f' % (element.abundance_mean, )).replace('nan', '\\nodata')
                sigma_X = '\\nodata' if element.number_of_lines == 0 else ('%1.2f' % (element.abundance_std, )).replace('nan', '\\nodata')
                x_on_H = '\\nodata' if element.number_of_lines == 0 else ('%1.2f' % (element.X_on_H, )).replace('-', '$-$').replace('nan', '\\nodata')
                x_on_Fe = '\\nodata' if element.number_of_lines == 0 else ('%1.2f' % (element.X_on_Fe, )).replace('-', '$-$').replace('nan', '\\nodata')
                uncertainty = '\\nodata' if element.number_of_lines == 0 else ('%1.2f' % (element.X_on_Fe_uncertainty, )).replace('nan', '\\nodata')

                row = "%15s & %3s & %7s & %7s & %7s & %7s & %7s \\\\\n" % \
                (element_str, element.number_of_lines, log_X, sigma_X, x_on_H, x_on_Fe, uncertainty, )

                fp.write(row)


            '''
            fp.write("# Element Number log(X) sigma(X) logSolar(X) [X/H] [X/Fe] Uncertainty\n")
            for element in self.session.elemental_abundances:
                row = "%s %2.1f %i %1.2f %1.2f %1.2f %1.2f %1.2f %1.2f\n" % \
                (element.element, element.transition, element.number_of_lines, element.abundance_mean, element.abundance_std,
                    element.solar_abundance, element.X_on_H, element.X_on_Fe, element.X_on_Fe_uncertainty, )

                fp.write(row)

            '''

        print "Exported chemical abundances to %s" % (output_filename, )

        

class ApplicationMain(HasTraits):
    """ Main application GUI for Spectroscopy Made Hard """
    
    # Initialise the session
    session = Instance(Session)

    # Session delegates
    spectrum_filenames = DelegatesTo("session")
    snr_spectrum = DelegatesTo("session")
    normalised_spectrum = DelegatesTo("session")
    rest_spectrum = DelegatesTo("session")
    measurements = DelegatesTo("session")
    stellar_atmosphere_filename = DelegatesTo("session")

    # Action items for File menu
    new_action = Action(name="&New session", accelerator="Ctrl+N", action="new_session",
        tooltip="New (Ctrl+N)")
    open_action = Action(name="&Open session..", accelerator="Ctrl+O",
                         action="open_session", tooltip="Open (Ctrl+O)")
    save_action = Action(name="&Save session", accelerator="Ctrl+S",
                         action="save_session", tooltip="Save (Ctrl+S)")
    save_as_action = Action(name="Save session &as..", accelerator="Shift+Ctrl+S",
                            action="save_as_session", tooltip="Save As (Shift+Ctrl+S)")
    quit_action = Action(name="&Quit..", accelerator="Ctrl+Q",
                         action="quit_session", tooltip="Quit (Ctrl+Q)")
    
    # Action items for Edit menu
    # Action items for Edit->Line list menu
    select_line_list = Action(name="Select line list..", action="select_line_list")
    extend_line_list = Action(name="Extend line list..", action="extend_line_list")
    introduce_literature_line_list = Action(name="Introduce literature line list..", action="introduce_literature_line_list")
    
    # Action items for tools menu
    automatic_nlte_corrections = Action(name="Automatic non-LTE corrections..", action="automatic_nlte_corrections")

    # Action items for plotting menu
    plot_emp_summary_page = Action(name="EMP star summary page", action="plot_emp_summary_page", enabled_when="rest_spectrum")
    plot_measurements = Action(name="Measurements", action="plot_measurements")
    plot_snr_spectrum = Action(name="S/N spectrum", action="plot_snr_spectrum", enabled_when="snr_spectrum")

    # Action items for export menu
    export_to_database = Action(name="Export to database", action="export_to_database", enabled_when="spectrum_filenames")
    export_measured_properties = Action(name="All properties", action="export_measured_properties", enabled_when="spectrum_filenames")
    export_equivalent_widths = Action(name="Line measurements", action="export_equivalent_widths", enabled_when="rest_spectrum")
    export_chemical_abundances = Action(name="Chemical abundances", action="export_chemical_abundances", enabled_when="stellar_atmosphere_filename")

    export_normalised_spectrum = Action(name="Stitched, normalised spectrum", action="export_normalised_spectrum", enabled_when="normalised_spectrum")
    export_rest_spectrum = Action(name="Rest spectrum", action="export_rest_spectrum", enabled_when="rest_spectrum")
    export_model_atmosphere = Action(name="Model atmosphere", action="export_model_atmosphere", enabled_when="stellar_atmosphere_filename")

    # File menu
    file_menu = Menu(
        "|",
        new_action,
        open_action,
        "_",
        save_action,
        save_as_action,
        "_",
        quit_action,
        name="&File"
    )

    undo_action = Action(name="Undo", action="_on_undo", defined_when="ui.history is not None",
        enabled_when="ui.history.can_undo", accelerator="Ctrl+Z", tooltip="Undo (Ctrl+Z)")
    redo_action = Action(name="Redo", action="_on_redo", defined_when="ui.history is not None",
        enabled_when="ui.history.can_undo", accelerator="Ctrl+Shift+Z", tooltip="Redo (Ctrl+Shift+Z)")

    line_list_submenu = Menu("|",
        select_line_list,
        extend_line_list,
        introduce_literature_line_list,
        name="Line list")

    # Edit menu
    edit_menu = Menu("|",
        undo_action,
        redo_action,
        "_",
        line_list_submenu,
        name="&Edit"
        )

    # Tools menu
    tools_menu = Menu("|",
        automatic_nlte_corrections,
        name="&Tools")

    # Plot menu
    plots_menu = Menu("|",
        plot_snr_spectrum,
        plot_emp_summary_page,
        plot_measurements,
        name="Plot")

    # Export spectra sub-menu
    export_spectra_submenu = Menu("|",
        export_normalised_spectrum,
        export_rest_spectrum,
        name="Spectra")

    # Export tables sub-menu
    export_tables_submenu = Menu("|",
        export_measured_properties,
        export_equivalent_widths,
        export_chemical_abundances,
        name="Tables")

    # Export menu
    export_menu = Menu("|",
        export_to_database,
        export_model_atmosphere,
        export_tables_submenu,
        export_spectra_submenu,
        name="Export")
    
    # Create instances of all the tabs
    summary = Instance(SummaryTab, ())
    normalisation = Instance(NormalisationTab, ())
    doppler_correct = Instance(DopplerCorrectTab, ())
    equivalent_widths = Instance(EquivalentWidthsTab, ())
    stellar_parameters = Instance(StellarParametersTab, ())
    abundances = Instance(ChemicalAbundancesTab, ())
    synthesis = Instance(SynthesisTab, ())

    title_str = Str("Spectroscopy Made Hard")

    # Generate the view
    view = View(
        Tabbed(
            Item("summary", style="custom", show_label=False),
            Item("normalisation", style="custom", show_label=False),
            Item("doppler_correct", style="custom", show_label=False),
            Item("equivalent_widths", style="custom", show_label=False),
            Item("stellar_parameters", style="custom", show_label=False),
            Item("abundances", style="custom", show_label=False),
            Item("synthesis", style="custom", show_label=False), 
        ),
        handler = ApplicationMainHandler(),
        menubar = MenuBar(
            file_menu,
            edit_menu,
            tools_menu,
            plots_menu,
            export_menu
        ),
        width     = 1280,
        height    = 700,
        resizable = True,
        title     = "Spectroscopy Made Hard"
    )

    
    def __init__(self):
        HasTraits.__init__(self)
        logger.warn("SMH may cause you to be scientifically productive. If symptoms persist, please visit www.reddit.com")

    # Initialize all the tabs by sending a copy of the session as a weak reference
    def _session_default(self):
        return Session()
        
    def _summary_default(self):
        return SummaryTab(self.session)

    def _normalisation_default(self):
        return NormalisationTab(self.session)    

    def _doppler_correct_default(self):
        return DopplerCorrectTab(self.session)
    
    def _equivalent_widths_default(self):
        return EquivalentWidthsTab(self.session)

    def _stellar_parameters_default(self):
        return StellarParametersTab(self.session)
    
    def _abundances_default(self):
        return ChemicalAbundancesTab(self.session)

    def _synthesis_default(self):
        return SynthesisTab(self.session)


def application(input_files=None):
    """
    Opens the Spectroscopy Made Hard GUI application.

    Inputs
    ------
    input_files : list or str
        Individual spectra filenames to initialise a new session or a
        SMH session file to load into SMH.
    """

    logger.info("Spectroscopy Made Hard(er) version {0}".format(get_version()))

    gui = ApplicationMain()
    
    if input_files is not None:

        # Do any input files have .smh extensions?
        has_smh_extension = [filename.endswith(".smh") for filename in input_files]
        if not any(has_smh_extension):
            logger.warn("This feature is not implemented yet.")

            # No SMH extensions identified, let's assume they are all spectra
            logger.info("Initialising GUI with input spectra after loading: {0}".format(", ".join(input_files)))

            # Let's get a common base name from the filenames we have been provided
            basenames = [os.path.basename(filename).lower() for filename in input_files]
            common_basename = find_common_start(basenames)
            common_basename = common_basename if len(common_basename) > 0 else "Untitled"

            def update_session_input_files():
                gui.session.load_spectra(input_files)
                gui.title_str = "Spectroscopy Made Hard - {0}".format(common_basename)

            wx.CallAfter(update_session_input_files)

        else:

            session_filename = input_files[has_smh_extension.index(True)]
            
            if len(input_files) > 1:
                logger.warn("SMH session file provided with other input files. Ignoring other input files.")

            if sum(has_smh_extension) > 1:
                logger.warn("More than one SMH session file provided. Loading the first session only: {0}".format(session_filename))

            logger.info("Initialising GUI with previous session: {0}".format(session_filename))

            def update_session_input_files():
                gui.session.load(session_filename)
                gui.title_str = "Spectroscopy Made Hard - {0}".format(os.path.basename(session_filename))

                # Update some plots
                # TODO - we shouldn"t have to do this here.
                #gui.info.object.stellar_parameters._update_display_trends(force=True)

            wx.CallAfter(update_session_input_files)

    gui.configure_traits()

