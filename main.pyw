# -*- coding: utf-8 -*-
"""
@file   main.pyw
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2012  Peter M. Bach

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2012. Peter M. Bach"

# --- CODE STRUCTURE --- --- --- --- --- ---
#       1.) CORE LIBRARY IMPORTS
#       2.) URBANBEATS LIBRARY IMPORTS
#       3.) GUI IMPORTS
#       4.) MAIN GUI FUNCTION
#       5.) CONSOLE OBSERVER
#       6.) START SCREEN LAUNCH
# --- --- --- --- --- --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import sys
import os
import platform
import time
import random
import webbrowser
import subprocess
import xml.etree.ElementTree as ET

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.urbanbeatscore as ubcore
import ubeats_spatialhandling as ubspatial

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit
from urbanbeatsmaingui import Ui_MainWindow
from startscreen import Ui_StartDialog
import urbanbeatsdialogs as ubdialogs       # Contains code for all non-module and non-result dialog windows

# --- MAIN GUI FUNCTION ---
class MainWindow(QtWidgets.QMainWindow):
    """The class definition for the UrbanBEATS Main Window. The main window
    opens during the main runtime loop and manages the calls to all other GUIs. It
    links with the model core."""
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- INITIALIZATION ---
        self.setWindowTitle("UrbanBEATS Planning Support Tool")
        self.ui.OutputConsole.append("<b>=================================<b>")
        self.ui.OutputConsole.append("<b>UrbanBEATS OUTPUT CONSOLE<b>")
        self.ui.OutputConsole.append("<b>=================================<b>\n")
        self.consoleobserver = ConsoleObserver()

        # --- SIGNAL DEFINITIONS ---


        # --- WORKFLOW VARIABLES ---
        self.__current_project_name = ""
        self.__saveProjectState = True      # True = unsaved, False = saved - used to track changes in workflow
        self.__activeSimulationObject = None
        self.__activeprojectpath = "C:\\"

        self.__global_options = {}
        self.__dtype_names = []

        # --- GUI SIGNALS AND SLOTS ---
        # Function naming conventions: show_ = launching dialog windows,
        #                              get_ / set_ / update_ = modifying existing information
        #                              reset_ = resets variables to original state
        #                              run_ = executes some form of runtime function

        # FILE MENU
        self.ui.actionNew_Project.triggered.connect(self.create_new_project)
        # self.ui.actionOpen_Project.triggered.connect()
        # self.ui.actionSave.triggered.connect()
        # self.ui.actionSave_As.triggered.connect()
        # self.ui.actionImport_Project.triggered.connect()
        # self.ui.actionExport_Project.triggered.connect()
        # self.ui.actionQuit.triggered.connect() - implemented through QtDesigner
        #
        # # EDIT MENU
        self.ui.actionEdit_Project_Details.triggered.connect(lambda: self.show_new_project_dialog(1))
        self.ui.actionPreferences.triggered.connect(self.show_options)
        #
        # # PROJECT MENU
        self.ui.actionView_Project_Description.triggered.connect(lambda: self.show_new_project_dialog(2))
        self.ui.actionView_Full_Project_Log.triggered.connect(self.show_project_log)
        # self.ui.actionDefine_New_Scenario.triggered.connect()
        # self.ui.actionDelete_Scenario.triggered.connect()
        #
        # # DATA MENU
        self.ui.actionAdd_Data.triggered.connect(self.show_add_data_dialog)
        # self.ui.actionImport_Archive_File.triggered.connect()
        # self.ui.actionImport_Archive_from_Project.triggered.connect()
        # self.ui.actionExport_Data_Archive.triggered.connect()
        # self.ui.actionReset_Data_Library.triggered.connect()
        #
        # # SIMULATION MENU
        # # Do this much later once GUIs for modules have been defined.
        #
        # # ADVANCED MENU
        # self.ui.actionModel_Calibration_Viewer.triggered.connect()
        #
        # # WINDOW MENU
        # self.ui.actionMinimize.triggered.connect() - implemented through QtDesigner
        # self.ui.actionOpen_Project_Folder.triggered.connect()
        # self.ui.actionResults_Viewer.triggered.connect()
        #
        # # HELP MENU
        self.ui.actionAbout.triggered.connect(self.show_about_dialog)
        # self.ui.actionView_Documentation.triggered.connect()
        # self.ui.actionOnline_Help.triggered.connect()
        # self.ui.actionSubmit_a_Bug_Report.triggered.connect()
        # self.ui.actionLike_on_Facebook.triggered.connect()
        # self.ui.actionShare_on_Twiter.triggered.connect()

        # OBSERVER PATTERN - CONSOLE UPDATE
        self.consoleobserver.updateConsole[str].connect(self.printc)

        # MAIN INTERFACE BUTTONS
        # Project Data Library Interface

        # Scenario Browser Interface

        # Data View Interface

        #self.ui.DataView_extent.clicked.connect()
        #self.ui.DataView_meta.clicked.connect()
        self.ui.DataView_options.clicked.connect(lambda: self.show_options(2))

        # Scenario Narrative Interface

        # Modules Interface
        self.ui.ModuleDock_spatialsetup.clicked.connect(self.launch_spatialsetup_modulegui)
        self.ui.ModuleDock_climatesetup.clicked.connect(self.launch_climatesetup_modulegui)

        self.ui.ModuleDock_urbandev.clicked.connect(self.launch_urbandev_modulegui)
        self.ui.ModuleDock_urbanplan.clicked.connect(self.launch_urbanplan_modulegui)
        self.ui.ModuleDock_socioeconomic.clicked.connect(self.launch_socioeconomic_modulegui)

        self.ui.ModuleDock_spatialmap.clicked.connect(self.launch_spatialmap_modulegui)
        self.ui.ModuleDock_regulation.clicked.connect(self.launch_regulation_modulegui)
        self.ui.ModuleDock_infrastructure.clicked.connect(self.launch_infrastructure_modulegui)

        self.ui.ModuleDock_performance.clicked.connect(self.launch_performance_modulegui)
        self.ui.ModuleDock_impact.clicked.connect(self.launch_impact_modulegui)
        self.ui.ModuleDock_decisionanalysis.clicked.connect(self.launch_decisionanalysis_modulegui)

        # Control Panel Interface
        self.ui.SimDock_projectfolder.clicked.connect(self.open_project_folder)
        # self.ui.SimDock_mapoptions.clicked.connect(self.show_map_export_settings)
        # self.ui.SimDock_report.clicked.connect(self.show_reporting_settings)
        # self.ui.SimDock_resultsview.connect(self.show_results_viewer)
        # self.ui.SimDock_run.connect(self.call_run_simulation)

    # MAIN INTERFACE FUNCTIONALITY
    def printc(self, textmessage):
        """Print to console function, adds the textmessage to the console"""
        if "PROGRESSUPDATE" in str(textmessage):
            progress = textmessage.split('||')
            #self.updateProgressBar(int(progress[1]))
            pass
        else:
            self.ui.OutputConsole.append(str("<font color=\"#93cbc7\">"+time.asctime())+"</font> | "+str(textmessage))

    def open_project_folder(self):
        """Opens the proejct folder of the active simulation. The function is called differently
        depending on the operating system.

        :return: None, opens Explorer or Finder depending on Windows/Mac
        """
        simulation = self.get_active_simulation_object()
        if simulation:
            print self.__activeprojectpath
            self.printc("Opening Project Folder: "+str(self.__activeprojectpath))
            if platform.system() == "Windows":
                subprocess.Popen(r'explorer "'+self.__activeprojectpath+'"')
            else:
                subprocess.Popen(["open", self.__activeprojectpath])    # NOTE: untested!
        return

    # ABOUT AND OPTIONS DIALOG AND RELATED FUNCTIONS
    def show_about_dialog(self):
        """Shows the About Dialog with all model information, development team, etc."""
        aboutdialog = ubdialogs.AboutDialogLaunch()
        aboutdialog.exec_()

    def show_options(self, tabindex):
        """Launches the Options/Preferences Dialog window and updates its interface with the data from
        the variable self.__global_options. Upon closing the window, an accept() signal will call the
        update_options() method."""
        preferencedialog = ubdialogs.PreferenceDialogLaunch(self, tabindex)
        preferencedialog.exec_()

    def get_options(self):
        """Gets the complete list of global options.

        :return: dict - self.__global_options
        """
        return self.__global_options

    def get_option(self, att):
        """Returns a specific attribute from the list of global program options.

        :param: att - the attribute from the options list
        :return: property of att if it is the correct key, otherwise None"""
        try:
            return self.__global_options[att]
        except KeyError:
            return None

    def update_options(self, newoptions, reset=False):
        """Updates the config.cfg file with either the user-modified options saved in newoptions or
        the default values if the user is resetting options.

        :param newoptions: dictionary type in the same format as self.__global_options
        :param reset: boolean, if False, config.cfg if updated with values from newoptions, otherwise reset to default
        :return: None
        """
        if newoptions == 0 and reset:
            self.printc("Options have been reset!")
        elif reset == False:
            self.printc("Options have been successfully changed!")
            print self.__global_options

    def set_options_from_config(self):
        """Parses config.cfg file and saves all attributes into the self.__global_options dictionary

        :param filepath: str, full filepath to the .cfg file. Usually UBEATSROOT
        :return: None
        """
        options = ET.parse(UBEATSROOT+"/config.cfg")
        root = options.getroot()

        for section in root.find('options'):
            for child in section:
                self.__global_options[child.tag] = child.text
        print self.__global_options

    def write_new_options(self, newoptions):
        """Updates the config

        :return:
        """
        options = ET.parse(UBEATSROOT+"/config.cfg")
        root = options.getroot()
        for section in root.find('options'):
            for child in section:
                child.text = str(newoptions[child.tag])
        options.write(UBEATSROOT+"/config.cfg")
        self.update_gui_elements()

    def reset_default_options(self):
        print "RESETTING"


    def update_gui_elements(self):
        coordinates = ubglobals.COORDINATES[main_window.get_option("city")]
        tileserver = ubglobals.TILESERVERS[main_window.get_option("mapstyle")]
        leaflet_html = ubspatial.generate_initial_leaflet_map(coordinates, tileserver, UBEATSROOT)
        main_window.ui.DataView_web.setHtml(leaflet_html)

    # NEW PROJECT INSTANCE CREATION
    def create_new_project(self):
        newsimulation = ubcore.UrbanBeatsSim(UBEATSROOT, self.__global_options) #instantiate new simulation objective
        self.set_active_simulation_object(newsimulation)
        self.show_new_project_dialog(0)

    def show_new_project_dialog(self, viewmode):
        newprojectdialog = ubdialogs.NewProjectDialogLaunch(self.get_active_simulation_object(), viewmode)
        newprojectdialog.rejected.connect(self.cancel_new_project_creation)
        newprojectdialog.exec_()

    def cancel_new_project_creation(self):
        self.set_active_simulation_object(None)
        self.enable_disable_main_interface(0)

    def open_existing_project(self):
        self.printc("OPEN AN EXISTING PROJECT")
        pass

    def import_existing_project(self):
        self.printc("IMPORT PROJECT!")
        pass

    def enable_disable_main_interface(self, condition):
        pass

    # def create_new_project_instance(self):
    #     """Creates a new instance of an UrbanBEATS Core Program."""
    #     newsimulation = ubc.UrbanBeatsSim(UBEATSROOT)
    #     newsimulation.register_observer(self.consoleobserver)
    #     return newsimulation

    def set_active_simulation_object(self, simobjectfromcore):
        self.__activeSimulationObject = simobjectfromcore

    def get_active_simulation_object(self):
        return self.__activeSimulationObject

    def set_save_project_state(self, status):
        """Reverses the state of saveProjectState. Tracks changes made to project settings. Then, changes
         the Main Window title depending on the save state. If unsaved, appends *, if saved, removes *

        :param status: bool, True = all changes saved, False = changes made and project unsaved
        :return: None
        """
        self.__saveProjectState = status
        if self.__saveProjectState: # if saved
            self.setWindowTitle("UrbanBEATS Planning Support Tool -" + self.__current_project_name + "")
        else:
            self.setWindowTitle("UrbanBEATS Planning Support Tool -" + self.__current_project_name + "*")

    def save_project(self):
        """Saves the project's current state, overwriting the existing project."""
        self.set_save_project_state(True)

    def close_event(self, event):
        """Shows a message box before closing the program to confirm with the user about quitting.
        Checks the save project state before deciding to post the message or not."""
        if not self.__saveProjectState:
            quit_msg = "Would you like to save your work before quitting?"
            reply = QtWidgets.QMessageBox.question(self, 'Close Program?',
                                                   quit_msg, QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                self.saveProject()
                event.accept()
            elif reply == QtWidgets.QMessageBox.No:
                event.accept()
            else:
                event.ignore()

    def show_project_log(self):
        """Opens the project log window for the user to review the history of the modelling project."""
        # Get the active Log object
        logobject = None
        projectlog = ubdialogs.ProjectLogLaunch(logobject)

        projectlog.exec_()

    def show_add_data_dialog(self):
        """Opens the Add Data Dialog window when the user clicks on any function to add data to the project."""
        adddatadialog = ubdialogs.AddDataDialogLaunch()

        adddatadialog.exec_()

    # FUNCTIONS TO DO
    def checks_before_run(self):
        pass

    def raise_ub_error_message(self, message):
        pass

    def run_simulation(self):
        pass

    def run_simulation_perfonly(self):
        pass


# --- CONSOLE OBSERVER ---
class ConsoleObserver(QtCore.QObject):
    """Defines the observer class that will work with the console window in
    UrbanBEATS' main window."""

    updateConsole = QtCore.pyqtSignal(str, name="updateConsole")

    def update_observer(self, textmessage):
        """Emits <updateConsole> signal"""
        self.updateConsole.emit(textmessage)


# --- START SCREEN LAUNCH ---
class StartScreenLaunch(QtWidgets.QDialog):
    """Class definition for the Getting Started Screen that launches when
    UrbanBEATS starts up. The dialog has several options for the user to choose
    including New, Open, Import, Website/Online service + options, help and quit."""

    # DEFINITION OF SIGNALS
    startupNew = QtCore.pyqtSignal()
    startupOpen = QtCore.pyqtSignal()
    startupImport = QtCore.pyqtSignal()
    startupOptions = QtCore.pyqtSignal()

    def __init__(self, main, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_StartDialog()      # Assign an instance of the UI class to variable
        self.ui.setupUi(self)           # Call setup to set up the UI
        self.main = main

        # --- SIGNALS AND SLOTS ---
        self.ui.NewProject_button.clicked.connect(self.startup_new_project_window)
        self.ui.OpenProject_button.clicked.connect(self.startup_open_project)
        self.ui.ImportProject_button.clicked.connect(self.startup_import_project)
        self.ui.VisitWeb_button.clicked.connect(self.startup_web)
        self.ui.OptionsButton.clicked.connect(self.startup_options)
        self.ui.HelpButton.clicked.connect(self.startup_help)
        self.ui.QuitButton.clicked.connect(self.startup_quit)

    def startup_new_project_window(self):
        """Called when user clicks on Begin New Project, emits <startupNew> signal."""
        self.accept()   #closes dialog
        self.startupNew.emit()

    def startup_open_project(self):
        """Called when user clicks on Open Existing Project, emits <startupOpen> signal."""
        self.accept()   #closes dialog
        self.startupOpen.emit()

    def startup_import_project(self):
        """Called when user clicks on Import Existing Project, emits <startupImport> signal."""
        self.accept()   #closes dialog
        self.startupImport.emit()

    @staticmethod
    def startup_web(self):
        """Called when user clicks on visit Ubeatsmodel.com, emits <startupWeb> signal."""
        webbrowser.open("http://urbanbeatsmodel.com")

    def startup_options(self):
        """Called when Options button clicked, opens the options dialog box."""
        self.accept()
        self.startupOptions.emit()

    def startup_help(self):
        """Called when Help button clicked, opens documentation."""
        pass

    def startup_quit(self):
        """Called when Quit button clicked, quits the program."""
        self.accept()
        sys.exit()


# --- MAIN PROGRAM RUNTIME ---
if __name__ == "__main__":

    # --- OBTAIN AND STORE PATH DATA FOR PROGRAM ---
    UBEATSROOT = os.path.dirname(sys.argv[0])  # Obtains the program's root directory
    UBEATSROOT = UBEATSROOT.encode('string-escape')  # To avoid weird bugs e.g. if someone's folder path

    random.seed()   #Seed the random numbers

    # Someone is launching this directly
    # Create the QApplication
    app = QtWidgets.QApplication(sys.argv)

    # --- I18N Localization ---
    # To create a translation, follow these steps:
    #   (1) run the command: pylupdate5 <GUI file>.py -ts <translation_file>.ts
    #   (2) Open the file with QLinguist, set the language options and edit the file with translations.
    #       Save the .ts file
    #   (3) in the command prompt, run: lrelease <translation_file>.ts    <--- same path as translation file
    #       This creates a qmake file: .qm
    #   (4) In the program runtime, here is the following code to select the correct translation file and
    #       call the translator (continued below - search for tag i18n step 5)
    #   (5) Final step to translate UI is to call installTranslator(translator) on the app variable.
    # File Naming Convention: Needs to follow <lang>_<region>.ts convention
    #   <lang> = ISO 639-1 (see https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) and
    #   <region> = ISO3166-1 (see https://en.wikipedia.org/wiki/ISO_3166-1)
    translator = QtCore.QTranslator()
    translator.load("ubjapa")
    #app.installTranslator(translator)

    # --- SPLASH SCREEN ---
    splash_matrix = ["1", "2", "3", "4", "5"]
    splash_pix = QtGui.QPixmap("media/splashscreen" + splash_matrix[random.randint(0, 4)] + ".png")
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()

    app.processEvents()

    # Simulate something that takes time
    time.sleep(1)       # "Marvel at the beautiful splash screen!"

    # --- MAIN WINDOW AND APPLICATION LOOP ---
    # Setup Main Window
    main_window = MainWindow()
    main_window.showMaximized()
    splash.finish(main_window)  # remove splashscreen, follow by main window

    # Enter the main loop
    main_window.set_options_from_config()

    # Set the initial Leaflet map
    coordinates = ubglobals.COORDINATES[main_window.get_option("city")]
    tileserver = ubglobals.TILESERVERS[main_window.get_option("mapstyle")]
    leaflet_html = ubspatial.generate_initial_leaflet_map(coordinates, tileserver, UBEATSROOT)
    main_window.ui.DataView_web.setHtml(leaflet_html)

    time.sleep(1)

    start_screen = StartScreenLaunch(main_window)
    # Signals for the Main Window and Start Screen Connection
    start_screen.startupNew.connect(main_window.create_new_project)
    start_screen.startupOpen.connect(main_window.open_existing_project)
    start_screen.startupImport.connect(main_window.import_existing_project)
    start_screen.startupOptions.connect(lambda: main_window.show_options(0))

    start_screen.exec_()
    sys.exit(app.exec_())   # END OF MAIN WINDOW LOOP
