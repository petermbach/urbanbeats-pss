r"""
@file   main.pyw
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2018  Peter M. Bach

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
__copyright__ = "Copyright 2018. Peter M. Bach"

# 8th JANUARY 2020 - URBANBEATS HAS BEEN CONVERTED TO PYTHON 3.7

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
import webbrowser
import subprocess
import random
import xml.etree.ElementTree as ET
import shutil
import tempfile

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.urbanbeatscore as ubcore

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.urbanbeatsmaingui import Ui_MainWindow
from gui.startscreen import Ui_StartDialog
from gui import urbanbeatsdialogs as ubdialogs
from gui import addboundarydialogc as gui_addboundary
from gui.urbanbeatsresultsguic import LaunchResultsExplorer
from gui.urbanbeatscalibrationguic import LaunchCalibrationViewer
import gui.ubgui_spatialhandling as gui_ubspatial
import gui.ubgui_reporting as ubreport
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubconfigfiles as ubconfigfiles

from gui.md_delinblocksguic import DelinBlocksGuiLaunch
from gui.md_urbplanbbguic import UrbplanbbGuiLaunch
from gui.md_urbdevelopguic import UrbdevelopGuiLaunch, InfluenceFunctionGUILaunch
from gui.md_spatialmappingguic import SpatialMappingGuiLaunch
from gui.md_infrastructureguic import InfrastructureGuiLaunch
from gui.md_bgsplanningguic import BlueGreenGuiLaunch
from gui import ssanto_dialogs as ssanto_dialogs
from gui import mapping_leaflet as mapping_leaflet

# --- MAIN GUI FUNCTION ---
class MainWindow(QtWidgets.QMainWindow):
    """The class definition for the UrbanBEATS Main Window. The main window
    opens during the main runtime loop and manages the calls to all other GUIs. It
    links with the model core."""
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__gui_state = "idle"   # GUI States, allows changing of functionality during runtime
        # The GUI state is introduced such that changes can be made when displaying different GUI elements during

        # --- INITIALIZATION ---
        self.setWindowTitle("UrbanBEATS Planning Support Tool")
        self.ui.stepwise_tree.setColumnWidth(0, 250)
        self.ui.stepwise_tree.expandAll()
        # self.setWindowTitle("规划模型")       #Chinese Translation - automate!
        self.initialize_output_console()
        self.consoleobserver = ConsoleObserver()
        self.progressbarobserver = ProgressBarObserver()
        self.rootfolder = UBEATSROOT
        self.app_tempdir = UBEATSTEMP       # The temp directory defined by tempfile

        # --- GLOBAL OPTIONS ---
        self.__global_options = {}
        self.epsg_dict = ubspatial.get_epsg_all(UBEATSROOT)
        self.set_options_from_config()

        # --- WORKFLOW VARIABLES ---
        self.__current_project_name = ""    # Name of the current project
        self.__saveProjectState = True      # True = unsaved, False = saved - used to track changes in workflow
        self.__activeSimulationObject = None    # The active simulation class instance: urbanbeatscore.UrbanBeatsSim()
        self.__activeScenario = None            # The active scenario
        self.__activeDataLibrary = None         # The active simulation's data library
        self.__activeProjectLog = None          # The active simulation's log file
        self.__dataview_displaystate = "default"    # The display state of the Leaflet data view, allows tracking

        self.__datalibraryexpanded = 0      # STATE: is the data library browser fully expanded?
        self.__current_location = self.get_option("city")   # STATE: the current location

        # --- GUI SIGNALS AND SLOTS ---
        # Function naming conventions: show_ = launching dialog windows,
        #                              get_ / set_ / update_ = modifying existing information
        #                              reset_ = resets variables to original state
        #                              run_ = executes some form of runtime function
        #                              launch_ = for working with larger module dialog windows

        # FILE MENU
        # actionQuit has been implemented through QtDesigner
        self.ui.actionNew_Project.triggered.connect(self.create_new_project)
        self.ui.actionOpen_Project.triggered.connect(self.open_existing_project)
        self.ui.actionSave.triggered.connect(self.save_project)
        self.ui.actionSave_As.triggered.connect(self.save_as_project)
        self.ui.actionImport_Project.triggered.connect(self.import_existing_project)
        self.ui.actionExport_Project.triggered.connect(self.export_existing_project)
        self.ui.actionClose_Project.triggered.connect(self.close_project)

        # EDIT MENU
        self.ui.actionEdit_Project_Details.triggered.connect(lambda: self.show_new_project_dialog(1))
        self.ui.actionPreferences.triggered.connect(self.show_options)

        # PROJECT MENU
        self.ui.actionAdd_Simulation_Boundary.triggered.connect(self.show_add_simulation_boundary_dialog)
        self.ui.actionView_Project_Description.triggered.connect(lambda: self.show_new_project_dialog(2))
        self.ui.actionView_Full_Project_Log.triggered.connect(self.show_project_log)
        # Scenario Submenu ---
        self.ui.actionDefine_New_Scenario.triggered.connect(lambda: self.show_scenario_dialog(0))
        self.ui.actionEdit_Scenario.triggered.connect(lambda: self.show_scenario_dialog(1))
        self.ui.actionDelete_Scenario.triggered.connect(self.delete_current_scenario)
        # --- //
        self.ui.actionReporting_Options.triggered.connect(self.show_reporting_settings)
        self.ui.actionMap_Export_Options.triggered.connect(self.show_map_export_settings)

        # DATA MENU
        self.ui.actionAdd_Data.triggered.connect(self.show_add_data_dialog)
        # self.ui.actionImport_Archive_File.triggered.connect()
        # self.ui.actionImport_Archive_from_Project.triggered.connect()
        # self.ui.actionExport_Data_Archive.triggered.connect()
        self.ui.actionReset_Data_Library.triggered.connect(self.reset_project_data_library)

        # SIMULATION MENU
        # Do this much later once GUIs for modules have been defined.
        self.ui.actionRun.triggered.connect(self.call_run_simulation)
        self.ui.actionDefine_IF.triggered.connect(self.launch_influencefunction_gui)
        # Variant for calling only the performance assessment

        #
        # ADVANCED MENU
        self.ui.actionModel_Calibration_Viewer.triggered.connect(self.show_calibration_viewer)

        # PLUGINS
        self.ui.actionSSANTO.triggered.connect(self.launch_SSANTO)

        #
        # WINDOW MENU
        # actionMinimize has been implemented through QtDesigner
        self.ui.actionOpen_Project_Folder.triggered.connect(self.open_project_folder)
        self.ui.actionResults_Viewer.triggered.connect(self.show_results_viewer)

        # HELP MENU
        self.ui.actionAbout.triggered.connect(self.show_about_dialog)
        # self.ui.actionView_Documentation.triggered.connect()
        # self.ui.actionOnline_Help.triggered.connect()
        # self.ui.actionSubmit_a_Bug_Report.triggered.connect()
        # self.ui.actionLike_on_Facebook.triggered.connect()
        # self.ui.actionShare_on_Twitter.triggered.connect()

        # --- END OF ACTIONS ---

        # OBSERVER PATTERN - CONSOLE UPDATE
        self.consoleobserver.updateConsole[str].connect(self.printc)
        self.progressbarobserver.updateProgressBar[int].connect(self.update_progress_bar_value)

        # --- MAIN INTERFACE BUTTONS ---
        # Project Data Library Interface
        self.ui.addData.clicked.connect(self.show_add_data_dialog)
        self.ui.removeData.clicked.connect(self.remove_data_from_library)
        self.ui.infoData.clicked.connect(self.show_metadata_dialog)
        self.ui.previewData.clicked.connect(self.update_preview_data)
        self.ui.expcolData.clicked.connect(self.expand_collapse_data_library)

        # Scenario Browser Interface
        self.ui.newScenario.clicked.connect(lambda: self.show_scenario_dialog(0))
        self.ui.editScenario.clicked.connect(lambda: self.show_scenario_dialog(1))
        self.ui.deleteScenario.clicked.connect(self.delete_current_scenario)
        self.ui.ScenarioDock_Combo.currentIndexChanged.connect(self.update_scenario_gui)
        self.ui.ScenarioDock_View.itemClicked.connect(self.change_narrative_gui_tab)

        # Data View Interface
        self.ui.DataView_extent.clicked.connect(self.update_map_display)
        self.ui.DataView_meta.clicked.connect(self.show_metadata_dialog)
        self.ui.DataView_options.clicked.connect(lambda: self.show_options(2))

        # Scenario Narrative Interface
        self.ui.ScenarioView_Widget.currentChanged.connect(self.adjust_context_stack)
        # clicking a data set on the table

        # Modules Interface
        self.ui.ModuleDock_spatialsetup.clicked.connect(self.launch_spatialsetup_modulegui)
        self.ui.ModuleDock_climatesetup.clicked.connect(self.launch_climatesetup_modulegui)

        self.ui.ModuleDock_urbandev.clicked.connect(self.launch_urbandev_modulegui)
        self.ui.ModuleDock_urbandynamics.clicked.connect(self.launch_urbandynamics_modulegui)

        self.ui.ModuleDock_urbanplan.clicked.connect(self.launch_urbanplan_modulegui)
        self.ui.ModuleDock_spatialmap.clicked.connect(self.launch_spatialmap_modulegui)

        self.ui.ModuleDock_infrastructure.clicked.connect(self.launch_infrastructure_modulegui)
        self.ui.ModuleDock_bluegreen.clicked.connect(self.launch_bluegreen_modulegui)

        self.ui.ModuleDock_watercycle.clicked.connect(self.launch_watercycle_modulegui)
        self.ui.ModuleDock_microclimate.clicked.connect(self.launch_microclimate_modulegui)
        self.ui.ModuleDock_flood.clicked.connect(self.launch_flood_modulegui)
        self.ui.ModuleDock_economics.clicked.connect(self.launch_economics_modulegui)

        # Control Panel Interface
        self.ui.SimDock_projectfolder.clicked.connect(self.open_project_folder)
        self.ui.SimDock_mapoptions.clicked.connect(self.show_map_export_settings)
        self.ui.SimDock_report.clicked.connect(self.show_reporting_settings)
        self.ui.SimDock_resultsview.clicked.connect(self.show_results_viewer)
        self.ui.SimDock_run.clicked.connect(self.call_run_simulation)

    # SSANTO
    def launch_SSANTO(self):
        """Launches the SSANTO Plugin using the current project's information."""
        ssantomain = ssanto_dialogs.SSANTOMainLaunch(self.get_active_simulation_object())
        ssantomain.exec_()


    # SCENARIO CREATION AND MANAGEMENT FUNCTIONALITY
    def show_scenario_dialog(self, viewmode):
        """Launches the scenario dialog window, which the user can use to customize and set up a simulation scenario.

        :param viewmode: 0 = new scenario, 1 = edit scenario
        """
        if viewmode == 0:       # Create New Scenario
            # Instantiate the scenario first, then make sure it is the active one
            self.get_active_simulation_object().create_new_scenario()
            newscenariodialog = ubdialogs.CreateScenarioLaunch(self, self.get_active_simulation_object(),
                                                               self.get_active_data_library(), viewmode)
            newscenariodialog.accepted.connect(self.setup_scenario)
            newscenariodialog.exec_()
        elif viewmode == 1:     # Edit Scenario
            if self.ui.ScenarioDock_Combo.currentIndex() == 0:
                return
            newscenariodialog = ubdialogs.CreateScenarioLaunch(self, self.get_active_simulation_object(),
                                                               self.get_active_data_library(), viewmode)
            newscenariodialog.accepted.connect(self.update_scenario_gui)
            newscenariodialog.exec_()

    def show_results_viewer(self):
        """Launches the results viewer dialog, passes the active simulation information to the viewer."""
        resultsexplorerdialog = LaunchResultsExplorer(self, self.get_active_simulation_object(),
                                                      self.get_active_data_library())
        resultsexplorerdialog.exec_()

    def show_calibration_viewer(self):
        """Launches the calibration viewer, passes the active simulation information for the user to undertake
        the calibration."""
        activesim = self.get_active_simulation_object()
        activescenario = activesim.get_active_scenario()
        calibrationviewer = LaunchCalibrationViewer(self, activesim, activescenario)
        calibrationviewer.exec_()

    def change_narrative_gui_tab(self):
        """Changes the current tab in the Scenario Narrative based on what is clicked in the Scenario Description
        tree view widget. Only updates if a top level item has been clicked."""
        # print(self.ui.ScenarioDock_View.selectedItems()[0].text(0))
        if self.ui.ScenarioDock_View.selectedItems()[0].text(0) == "Narrative":
            self.ui.ScenarioView_Widget.setCurrentIndex(1)
        elif self.ui.ScenarioDock_View.selectedItems()[0].text(0) == "Simulation Details":
            self.ui.ScenarioView_Widget.setCurrentIndex(2)
        elif self.ui.ScenarioDock_View.selectedItems()[0].text(0) == "Using Spatial Data Sets":
            self.ui.ScenarioView_Widget.setCurrentIndex(3)
        elif self.ui.ScenarioDock_View.selectedItems()[0].text(0) == "Modules":
            self.ui.ScenarioView_Widget.setCurrentIndex(2)
        elif self.ui.ScenarioDock_View.selectedItems()[0].text(0) == "Export Details":
            self.ui.ScenarioView_Widget.setCurrentIndex(2)
        else:
            pass

    def adjust_context_stack(self):
        """Changes the Main context view depending on the tab selected in the Scenario Information Tab Widget."""
        if self.ui.ScenarioView_Widget.currentIndex() in [0, 1]:
            self.ui.MainView_stack.setCurrentIndex(0)
        elif self.ui.ScenarioView_Widget.currentIndex() == 2:
            self.ui.MainView_stack.setCurrentIndex(1)
        elif self.ui.ScenarioView_Widget.currentIndex() == 3:
            self.ui.MainView_stack.setCurrentIndex(2)
        elif self.ui.ScenarioView_Widget.currentIndex() == 4:
            self.ui.MainView_stack.setCurrentIndex(3)
        else:
            pass

    def setup_scenario(self):
        """Called when the scenario setup dialog box has successfully closed. i.e. signal accepted()"""
        active_scenario = self.get_active_simulation_object().get_active_scenario()
        active_scenario.setup_scenario()
        self.get_active_simulation_object().add_new_scenario(active_scenario)
        self.ui.ScenarioDock_Combo.addItem(active_scenario.get_metadata("name"))
        self.ui.ScenarioDock_Combo.setCurrentIndex(int(self.ui.ScenarioDock_Combo.count() - 1))

    def delete_current_scenario(self):
        """Deletes the active scenario based on the scenario combobox. This includes removing it from the active
        simulation as well. The scenario interface is then reset to the default <select scenario> setting."""
        # Algorithm: (1) Get current scenario data, (2) Reset scenario narrative interface by clearing it
        # (3) Reset module buttons and control panel buttons, (4) Change current index of scenario combo
        # (5) Update the scenario description information, (6) Remove the scenario from the combo box,
        # (7) Remove the scenario from the simulation, (8) Delete the scenario folder from the project
        if self.ui.ScenarioDock_Combo.currentIndex() == 0:
            return  # Do nothing if no scenario selected.
        active_scenario = self.get_active_simulation_object().get_active_scenario()    # (1)
        self.get_active_simulation_object().delete_scenario(active_scenario.get_metadata("name"))   # (7), (8)
        self.ui.ScenarioDock_Combo.removeItem(self.ui.ScenarioDock_Combo.currentIndex())
        self.ui.ScenarioDock_Combo.setCurrentIndex(0)  # (2), (3), (4), (5), (6)

    def scenario_change_ui_setup(self):
        """Modifies the current Main Window Interface to suit the selected scenario. This includes enabling and
        disabling the module buttons, the control panel and updating the Scenario Narrative Section of the GUI
        with information on the current scenario. It also includes printing out details into the output console."""
        if self.ui.ScenarioDock_Combo.currentIndex() == 0:
            # <Select Scenario> Case - disables everything
            self.scenario_view_reset()
            self.ui.ModuleDock.setEnabled(0)
            self.ui.SimDock.setEnabled(0)
        else:
            self.update_scenario_gui()
            self.ui.SimDock.setEnabled(1)
        pass # [TO DO]

    def update_scenario_gui(self):
        """Updates the scenario GUI and narrative section with the current scenario's details."""
        if self.ui.ScenarioDock_Combo.count() == 0:
            return
        if self.ui.ScenarioDock_Combo.currentIndex() == 0:
            self.get_active_simulation_object().set_active_scenario(None)
            self.get_active_simulation_object().set_active_boundary(None)
            self.scenario_view_reset()
            return
        active_scenario_name = self.ui.ScenarioDock_Combo.currentText()
        self.get_active_simulation_object().set_active_scenario(active_scenario_name)
        self.__activeScenario = self.get_active_simulation_object().get_active_scenario()
        self.get_active_simulation_object().set_active_boundary(self.__activeScenario.get_metadata("boundary"))

        # Tree Widget Info:
        twi = QtWidgets.QTreeWidgetItem()
        twi.setText(0, str(self.__activeScenario.get_metadata("narrative")[:100]+"..."))
        twi.setToolTip(0, str(self.__activeScenario.get_metadata("narrative")[:100] + "..."))

        # Narrative
        self.ui.Narrative.setPlainText(self.__activeScenario.get_metadata("narrative"))

        self.ui.ScenarioDock_View.topLevelItem(0).takeChildren()
        self.ui.ScenarioDock_View.topLevelItem(0).addChild(twi)
        self.ui.ScenarioDock_View.topLevelItem(1).child(0).setText(0, "Type: "+self.__activeScenario.get_metadata("type"))
        self.ui.ScenarioDock_View.topLevelItem(1).child(1).setText(0, "Boundary: "+self.__activeScenario.get_metadata("boundary"))
        self.ui.ScenarioDock_View.topLevelItem(1).child(2).setText(0, "Status: "+"not simulated")
        if self.__activeScenario.get_metadata("type") == "DYNAMIC":
            yeartext = str(self.__activeScenario.get_metadata("startyear")) + " - " + str(self.__activeScenario.get_metadata("endyear"))
            dttext = str(self.__activeScenario.get_metadata("dt")) + " year(s)"
            benchtext = "N/A"
        elif self.__activeScenario.get_metadata("type") == "BENCHMARK":
            yeartext = str(self.__activeScenario.get_metadata("startyear"))
            dttext = "N/A"
            benchtext = str(self.__activeScenario.get_metadata("benchmarks"))
        else:
            yeartext = str(self.__activeScenario.get_metadata("startyear"))
            dttext = "N/A"
            benchtext = "N/A"
        self.ui.ScenarioDock_View.topLevelItem(1).child(3).setText(0, "Simulation Year(s): " + yeartext)
        self.ui.ScenarioDock_View.topLevelItem(1).child(4).setText(0, "Simulation Time Step: " + dttext)
        self.ui.ScenarioDock_View.topLevelItem(1).child(5).setText(0, "Benchmark Iterations: " + benchtext)
        self.ui.ScenarioDock_View.topLevelItem(4).\
            child(0).setText(0, "File Naming: "+self.__activeScenario.get_metadata("filename"))
        project_path = self.get_active_simulation_object().get_project_path()
        self.ui.ScenarioDock_View.topLevelItem(4).child(1).setText(0, "Path: " + str(os.path.normpath(project_path)))
        self.ui.ScenarioDock_View.topLevelItem(4).child(1).setToolTip(0, str(os.path.normpath(project_path)))

        # LIST OF DATA SETS
        datalist = self.__activeScenario.create_dataset_file_list()
        self.ui.DataSummary.setRowCount(0)
        self.ui.ScenarioDock_View.topLevelItem(2).takeChildren()
        self.ui.DataSummary.setRowCount(0)
        for entry in datalist:
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, entry[1])
            twi.setToolTip(0, entry[0]+" - "+entry[2])
            self.ui.ScenarioDock_View.topLevelItem(2).addChild(twi)

            # Update the Data Table Widget.
            rowposition = self.ui.DataSummary.rowCount()
            self.ui.DataSummary.insertRow(rowposition)
            self.ui.DataSummary.setItem(rowposition, 0, QtWidgets.QTableWidgetItem(entry[1]))
            self.ui.DataSummary.setItem(rowposition, 1, QtWidgets.QTableWidgetItem(entry[3]))
            self.ui.DataSummary.setItem(rowposition, 2, QtWidgets.QTableWidgetItem(entry[4]))
            self.ui.DataSummary.resizeColumnsToContents()

        # MODULES
        modulebools = []    # Holds 1 and 0 booleans that represent different modules in the module dock
        for i in range(len(ubglobals.MODULENAMES)):
            mbool = self.__activeScenario.check_is_module_active(ubglobals.MODULENAMES[i])
            if mbool:
                self.ui.ScenarioDock_View.topLevelItem(3).child(i).setDisabled(0)
                self.ui.ScenarioDock_View.topLevelItem(3).child(i).setCheckState(0, 2)
            else:
                self.ui.ScenarioDock_View.topLevelItem(3).child(i).setDisabled(1)
                self.ui.ScenarioDock_View.topLevelItem(3).child(i).setCheckState(0, 0)
            modulebools.append(int(mbool))
        self.enable_disable_module_icons(modulebools)   # enables corresponding module buttons

    def scenario_view_reset(self):
        """Resets the scenario view to the default """
        self.ui.ScenarioDock_View.topLevelItem(0).takeChildren()
        self.ui.ScenarioDock_View.topLevelItem(1).child(0).setText(0, "Type: <N/A>")
        self.ui.ScenarioDock_View.topLevelItem(1).child(1).setText(0, "Boundary: <N/A>")
        self.ui.ScenarioDock_View.topLevelItem(1).child(2).setText(0, "Status: <none>")
        self.ui.ScenarioDock_View.topLevelItem(1).child(3).setText(0, "Simulation Year(s): <year>")
        self.ui.ScenarioDock_View.topLevelItem(1).child(4).setText(0, "Simulation Time Step: N/A")
        self.ui.ScenarioDock_View.topLevelItem(1).child(5).setText(0, "Benchmark Iterations: N/A")
        self.ui.ScenarioDock_View.topLevelItem(2).takeChildren()
        for i in range(11):
            self.ui.ScenarioDock_View.topLevelItem(3).child(i).setCheckState(0, 0)
            self.ui.ScenarioDock_View.topLevelItem(3).child(i).setDisabled(1)
        self.ui.ScenarioDock_View.topLevelItem(4).child(0).setText(0, "File Naming: <name>")
        self.ui.ScenarioDock_View.topLevelItem(4).child(1).setText(0, "Path: <path>")

        self.ui.Narrative.clear()
        self.ui.DataSummary.setRowCount(0)
        self.enable_disable_module_icons([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    # MAIN INTERFACE FUNCTIONALITY
    def printc(self, textmessage):
        """Print to console function, adds the textmessage to the console"""
        if "PROGRESSUPDATE" in str(textmessage):
            progress = textmessage.split('||')
            # self.updateProgressBar(int(progress[1]))
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
            projectpath = os.path.normpath(simulation.get_project_path())
            self.printc("Opening Project Folder: "+str(projectpath))
            if platform.system() == "Windows":
                subprocess.Popen('explorer "%s"' %projectpath)
            else:
                subprocess.Popen(["open", projectpath])    # NOTE: untested!
        else:
            pass    # If no active project then the button will be disabled
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

    def set_options_from_config(self):
        """Parses config.cfg file and saves all attributes into the self.__global_options dictionary

        :param filepath: str, full filepath to the .cfg file. Usually UBEATSROOT
        :return: None
        """
        if not os.path.isfile(UBEATSROOT+"/config.cfg"):
            print("Creating Default Config File")
            ubconfigfiles.create_default_config_cfg(UBEATSROOT)     # if config.cfg does not exist, will create default

        options = ET.parse(UBEATSROOT+"/config.cfg")
        root = options.getroot()

        for section in root.find('options'):
            for child in section:
                self.__global_options[child.tag] = child.text

    def write_new_options(self, newoptions):
        """Updates the config.cfg file with the new option values set in the Options dialog."""
        options = ET.parse(UBEATSROOT+"/config.cfg")
        root = options.getroot()
        for section in root.find('options'):
            for child in section:
                child.text = str(newoptions[child.tag])
        options.write(UBEATSROOT+"/config.cfg")
        self.update_gui_elements()

    def reset_default_options(self):
        """Completely restores the default options based on the .cfg's default attribute for each option type.
        Also closes the options window."""
        print("RESETTING")       #[TO DO]
        ubconfigfiles.create_default_config_cfg(UBEATSROOT)
        self.set_options_from_config()      # Reset everything, update it
        self.update_gui_elements()
        return True

    def update_gui_elements(self):
        """Updates elements on the main window GUI depending on what has changed in the options menu. This
        includes the map viewer as well as others."""
        self.update_map_display()

    def update_map_display(self):
        """Updates the leaflet map display depending on the display-state, this is called either when options
        are changed or when the extent button is clicked."""
        if self.__dataview_displaystate == "default":       # Uses the display state to call correct function
            self.reset_data_view_to_default()
        elif self.__dataview_displaystate == "boundary":
            self.update_data_view("boundary")
        else:
            pass
            # Do nothing

    # NEW PROJECT INSTANCE CREATION
    def create_new_project(self):
        """Sets up the main user interface and calls the new project dialog"""
        self.setup_main_gui()
        self.show_new_project_dialog(0)

    def reset_data_view_to_default(self):
        """Resets the leaflet map view to the default location and default style based on when the program was
        opened"""
        if self.get_active_simulation_object() == None:
            coordinates = ubglobals.COORDINATES[self.get_option("city")]
        else:
            coordinates = ubglobals.COORDINATES[self.__current_location]

        tileserver = ubglobals.TILESERVERS[self.get_option("mapstyle")]

        leaflet_html = mapping_leaflet.generate_initial_leaflet_map(coordinates, tileserver, UBEATSROOT)
        f = open(self.app_tempdir+"/default.html", 'w')
        f.write(leaflet_html)
        f.close()
        self.ui.DataView_web.load(QtCore.QUrl.fromLocalFile(self.app_tempdir+"/default.html"))
        self.__dataview_displaystate = "default"

    def update_data_view(self, maptype):    # [REVAMP]
        """Updates the current leaflet map view to show base map and plot new data.

        :param newdata: The input data map, if the data map is of type SHP or .txt, leaflet will attempt to plot it.
        :return:
        """
        # Data to create map!
        tileserver = ubglobals.TILESERVERS[self.get_option("mapstyle")]
        projectdata = self.get_active_simulation_object().get_all_project_info()
        projectboundaries = self.get_active_simulation_object().get_project_boundaries()
        activeboundary = self.get_active_simulation_object().get_active_boundary()

        print(projectboundaries)
        print(activeboundary)
        print(projectdata)

        if maptype == "boundary":
            self.__dataview_displaystate = "boundary"

        if len(projectboundaries.keys()) == 0:
            return True

        temp_map_file = self.app_tempdir+"/boundary.html"
        mapping_leaflet.generate_leaflet_boundaries(temp_map_file, projectboundaries, activeboundary, projectdata,
                                                        self.get_active_simulation_object().get_global_centroid(),
                                                        self.get_active_simulation_object().get_project_epsg(),
                                                        tileserver, UBEATSROOT)
        self.ui.DataView_web.load(QtCore.QUrl.fromLocalFile(temp_map_file))


        #     projboundarymap = self.get_active_simulation_object().get_project_parameter("boundaryshp")
        #     coordinates, mapstats = ubspatial.get_bounding_polygons(projboundarymap, "leaflet", UBEATSROOT)
        #     leaflet_html = gui_ubspatial.generate_leaflet_boundary_map(coordinates, mapstats, projectdata, tileserver, UBEATSROOT)

        pass

    def initialize_output_console(self):
        """Resets the Output Console by first clearing its contents and then reprinting the three starting lines"""
        self.ui.OutputConsole.clear()
        self.ui.OutputConsole.append("<b>=================================<b>")
        self.ui.OutputConsole.append("<b>UrbanBEATS OUTPUT CONSOLE<b>")
        # self.ui.OutputConsole.append("<b>输出控制台<b>")   #CHINESE TRANSLATION - AUTOMATE!
        self.ui.OutputConsole.append("<b>=================================<b>\n")

    def setup_narrative_widget(self, condition):
        """Sets up the narrative widget based on the condition. If condition == "cler", method resets the scenario
        narrative widgets. If condition is based on scenario, then information from the scenario object is used
        to fill in the narrative scenario."""
        if condition == "clear":
            self.initialize_output_console()
            scenviewtext = "<html><head/><body><p><span style=\" font-weight:600;\">Scenario Narrative" \
                           "</span></p></body></html>"
            self.ui.ScenarioView_lbl.setText(scenviewtext)
            self.ui.Project.clear()
            self.ui.Narrative.clear()
            self.ui.Log.clear()
            self.ui.DataSummary.setRowCount(0)
        elif condition == "scenario":
            pass    #[TO DO]

    def show_add_simulation_boundary_dialog(self):
        """Launches the add simulation boundary dialog."""
        addsimboundarydialog = gui_addboundary.AddBoundaryDialogLaunch(self, self.get_active_simulation_object())
        addsimboundarydialog.accepted.connect(self.update_simulation_boundary_collection)
        addsimboundarydialog.exec_()

    def update_simulation_boundary_collection(self):
        self.get_active_simulation_object().import_simulation_boundaries()
        self.update_data_view("boundary")

    def show_new_project_dialog(self, viewmode):
        """Launches the New Project Dialog. Called either when starting new project, editing project info or
        viewing project information.

        :param viewmode: integer value that determins how GUI behaves, 0=newproject, 1=edit, 2=view
        """
        newprojectdialog = ubdialogs.NewProjectDialogLaunch(self, self.get_active_simulation_object(), viewmode)
        newprojectdialog.rejected.connect(lambda: self.cancel_new_project_creation(viewmode))
        newprojectdialog.accepted.connect(lambda: self.initialize_new_project(viewmode))
        newprojectdialog.exec_()

    def close_project(self):
        """Closes the current project and resets the main gui to startup state."""
        # First check save state
        if not self.get_save_project_state():
            quit_msg = "Would you like to save your work before closing the project?"
            reply = QtWidgets.QMessageBox.question(self, 'Close Project?',
                                                   quit_msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                                   QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                self.save_project()
            elif reply == QtWidgets.QMessageBox.No:
                pass
            else:
                return

        # Close project and prepare GUI and core for next project if the user wishes.
        self.set_active_simulation_object(None)
        self.set_active_data_library(None)
        self.set_active_project_log(None)
        self.set_current_project_name("")
        self.set_active_scenario(None)
        self.set_save_project_state(True)
        self.reset_project_data_library_view()

        self.setWindowTitle("UrbanBEATS Planning Support Tool")
        self.__datalibraryexpanded = True
        self.expand_collapse_data_library()  # Collapses the entire data library window
        self.ui.ScenarioDock_View.collapseAll()  # Collapse the scenario viewer

        self.ui.ScenarioDock_Combo.clear()  # Clear the scenario browser's combo
        self.ui.ScenarioDock_Combo.addItem("<Select Scenario>")
        self.ui.ScenarioDock_Combo.setCurrentIndex(0)

        self.setup_narrative_widget("clear")  # Clear the narrative widget's information
        self.reset_data_view_to_default()  # Restore the default Leaflet view
        self.scenario_change_ui_setup()
        self.enable_disable_main_interface("startup")

    def setup_main_gui(self):
        """Runs through the essential methods in order to prepare the GUI and simulation core for creating a new
        project. This includes: creating a new simulation object

        :return: None
        """
        self.ui.ProgressBar.setValue(0)
        self.set_active_simulation_object(None)  # Remove any existing active simulation
        self.reset_data_view_to_default()  # Restore the default Leaflet view
        newsimulation = ubcore.UrbanBeatsSim(UBEATSROOT, self.__global_options, self)  # instantiate new simulation objective
        newsimulation.register_observer(self.consoleobserver)   # Add the observer
        newsimulation.register_progressbar(self.progressbarobserver)    # Add the progress bar
        self.set_active_simulation_object(newsimulation)
        self.reset_project_data_library_view()

        # GUI calls
        self.setWindowTitle("UrbanBEATS Planning Support Tool")
        self.__datalibraryexpanded = True
        self.expand_collapse_data_library()  # Collapses the entire data library window

        self.ui.ScenarioDock_View.collapseAll()  # Collapse the scenario viewer

        self.ui.ScenarioDock_Combo.clear()  # Clear the scenario combo's items.
        self.ui.ScenarioDock_Combo.addItem("<Select Scenario>")
        self.ui.ScenarioDock_Combo.setCurrentIndex(0)

        self.setup_narrative_widget("clear")  # Clear the narrative widget's information
        self.enable_disable_main_interface("new")  # Enable and disable elements of the GUI for starting new project

    def cancel_new_project_creation(self, viewmode):
        """Called when the rejected() signal is emitted from the new project dialog. It reverts the active
        simulation object to None and disables interface elements back to the "startup" condition. """
        if viewmode == 0:   #ONLY IF CREATING NEW PROJECT
            self.set_active_simulation_object(None)
            self.enable_disable_main_interface("startup")

    def initialize_new_project(self, viewmode):
        """Calls core methods for the active simulation object and prepares the scenario and data library tree
        widgets."""
        if viewmode == 2:
            return
        self.set_save_project_state(False)  # Reverses the boolean on save project state
        if viewmode == 1:
            return

        activesimulation = self.get_active_simulation_object()
        if viewmode == 0:
            self.printc("New Project Initialized")
            activesimulation.initialize_simulation("new")
        else:
            self.printc("Loading Project " + activesimulation.get_project_parameter("name"))
            activesimulation.initialize_simulation("open")

        self.set_current_project_name(activesimulation.get_project_parameter("name"))
        self.set_active_data_library(activesimulation.get_data_library())
        self.set_active_project_log(activesimulation.get_project_log())
        self.__current_location = activesimulation.get_project_parameter("city")

        self.update_data_view("boundary")

        self.ui.Project.setHtml(ubreport.generate_project_overview_html(self.get_options(),
                                                                        activesimulation.get_all_project_info(),
                                                                        activesimulation.get_scenario_boundary_info("all"),
                                                                        activesimulation.get_num_scenarios(),
                                                                        activesimulation.get_num_datasets()))
        self.ui.ScenarioDock_View.expandAll()
        self.update_data_library_view()

        # Scenario View - UNCHECK and DISABLE ALL MODULES
        if viewmode == 0:
            moduleTree = self.ui.ScenarioDock_View.topLevelItem(3)
            moduleCount = moduleTree.childCount()
            for twi_module in range(moduleCount):
                moduleTree.child(twi_module).setDisabled(1)
                moduleTree.child(twi_module).setCheckState(0, False)
        else:
            # Prepare Scenario View by simply adding the names based on the active simulation's scenario names
            scenarionames = activesimulation.get_scenario_names()
            for n in scenarionames:
                self.ui.ScenarioDock_Combo.addItem(n)   # Adds the names to the Dock
                self.ui.ScenarioDock_Combo.setCurrentIndex(0)
                activesimulation.set_active_scenario(None)

        # Update Main Window Title
        self.setWindowTitle("UrbanBEATS Planning Support Tool - "+str(self.get_current_project_name()))

    def open_existing_project(self):
        """Opens an existing project folder and sets up the interface based on its information."""
        self.printc("OPEN AN EXISTING PROJECT")
        self.setup_main_gui()

        # Open Project Dialog
        recent_projects = self.load_recent_cfg()
        openprojectdialog = ubdialogs.OpenProjectDialogLaunch(self.get_active_simulation_object(), 3, recent_projects)
        openprojectdialog.rejected.connect(lambda: self.cancel_new_project_creation(0))     # Use viewmode 0
        openprojectdialog.accepted.connect(lambda: self.initialize_new_project(3))
        openprojectdialog.exec_()

    def import_existing_project(self):
        """Imports an UrbanBEATS Project File into the workspace, unpacks the file and sets up the folder
        structure of the project including scenarios and data."""
        self.printc("IMPORT PROJECT!")
        pass    #[TO DO]

    def export_existing_project(self):
        """Exports the existing project folder structure to a portable file."""
        self.printc("EXPORTING")

    def save_project(self):
        """Saves the project's current state, overwriting the existing project. This is a semi-save
        operation as UrbanBEATS tracks the status of the project throughout the workflow."""

        # Save the active data library
        self.printc("Consolidating Data Library...")
        if self.__activeDataLibrary is not None:
            self.__activeDataLibrary.consolidate_library()
        self.printc("Saving Active Scenario...")

        if self.__activeScenario is not None:
            self.__activeScenario.consolidate_scenario()

        # Consolidate the functions list
        self.printc("Consolidating Project Functions List")
        if self.__activeSimulationObject is not None:
            self.__activeSimulationObject.consolidate_functions_list()

        # Add project to the recent.cfg file
        self.update_recent_cfg(self.__activeSimulationObject.get_project_parameter("name"),
                               self.__activeSimulationObject.get_project_parameter("modeller"),
                               self.__activeSimulationObject.get_project_path())

        self.set_save_project_state(True)   #[TO DO]
        self.printc("Project Save State Updated!")

    def update_recent_cfg(self, project_name, modeller, project_path):
        """Updates the recent.cfg file with new project information."""
        projects = self.load_recent_cfg()
        if [str(project_name), str(modeller), str(project_path)] not in projects:
            projects.append([str(project_name), str(modeller), str(project_path)])
        self.save_recent_cfg(projects)

    def save_recent_cfg(self, projects):
        """Saves a new recent.cfg file with the updated information from projects array.

        :param projects: an array of projects, each element is [project_name, modeller, path]
        """
        f = open(UBEATSROOT+"/recent.cfg", 'w')
        f.write('<URBANBEATSRECENT creator="Peter M. Bach" version="1.0">\n')
        f.write('\t<recentprojects>\n')
        for p in projects:
            if os.path.isdir(str(p[2])):
                f.write('\t\t<project>\n')
                f.write('\t\t\t<name>'+str(p[0])+'</name>\n')
                f.write('\t\t\t<modeller>'+str(p[1])+'</modeller>\n')
                f.write('\t\t\t<path>'+str(p[2])+'</path>\n')
                f.write('\t\t</project>\n')
        f.write('\t</recentprojects>\n')
        f.write('</URBANBEATSRECENT>')
        f.close()
        return True

    def load_recent_cfg(self):
        """Loads the information from the recent.cfg file and returns an array of project info
        with the following structure: [project_name, modeller, path]."""
        recent_projects = []
        if not os.path.isfile(UBEATSROOT+"/recent.cfg"):
            print("Creating Blank Recent File")
            ubconfigfiles.create_default_recent_cfg(UBEATSROOT)

        recent_cfg = ET.parse(UBEATSROOT+"/recent.cfg")
        root = recent_cfg.getroot()
        projects = root.find("recentprojects")
        for child in projects:
            projectdata = []
            for att in child:
                projectdata.append(att.text)
            recent_projects.append(projectdata)
        return recent_projects

    def save_as_project(self):
        """Saves the project's current state to a completely different location. Also modifies its info with
        the new path information."""
        self.printc("SAVING AS")    #[TO DO]

    def closeEvent(self, event):
        """Shows a message box before closing the program to confirm with the user about quitting.
        Checks the save project state before deciding to post the message or not."""
        if not self.get_save_project_state():
            quit_msg = "Would you like to save your work before quitting?"
            reply = QtWidgets.QMessageBox.question(self, 'Close Program?',
                                                   quit_msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                                   QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                self.save_project()
            elif reply == QtWidgets.QMessageBox.No:
                pass
            else:
                event.ignore()

        shutil.rmtree(UBEATSTEMP)       # Clean up the temporary directory

    # OUTPUT OPTION GUIS - MAP EXPORT AND REPORT CREATION DIALOGS
    def show_map_export_settings(self):
        """Launches the map export options dialog window for the current scenario, where the user can customize
        the export format and types of spatial data required as output files from the model."""
        mapexportdialog = ubdialogs.MapExportDialogLaunch(self.get_active_simulation_object().get_active_scenario())

        mapexportdialog.exec_()

    def show_reporting_settings(self):
        """Launches the report creation dialog window, where the user can select and create reporting options. The
        settings are saved to the project's options for later use."""
        reportingdialog = ubdialogs.ReportingDialogLaunch(self.get_active_simulation_object())

        reportingdialog.exec_()

    # PROJECT LOG
    def show_project_log(self):
        """Opens the project log window for the user to review the history of the modelling project."""
        # Get the active Log object
        logobject = self.get_active_project_log()
        projectlog = ubdialogs.ProjectLogLaunch(logobject)

        projectlog.exec_()

    # DATA LIBRARY METHODS
    def show_add_data_dialog(self):
        """Opens the Add Data Dialog window when the user clicks on any function to add data to
        the project."""
        adddatadialog = ubdialogs.AddDataDialogLaunch(self, self.get_active_simulation_object(),
                                                      self.get_active_data_library())
        adddatadialog.dataLibraryUpdated.connect(self.update_data_library_view)
        adddatadialog.exec_()

    def reset_project_data_library(self):
        """RESETS THE ENTIRE PROJECT'S DATA LIBRARY including that in the simulation core."""
        self.get_active_data_library().reset_library()
        self.reset_project_data_library_view()

        # Go through all scenarios and remove all files
        pass    # [TO DO]

    def reset_project_data_library_view(self):
        """ONLY AFFECTS THE DATA LIBRARY VIEWER
        Removes all entries and recreates the base tree. Also retains the expanded and collapsed subitems.
        """
        expandcol_tli = []
        expandcol_twi = [[], []]
        for i in range(self.ui.DataDock_View.topLevelItemCount()):
            tli = self.ui.DataDock_View.topLevelItem(i)
            expandcol_tli.append(tli.isExpanded())
            if i == 2:  # Qualitative data has no children
                continue
            for j in range(tli.childCount()):
                expandcol_twi[i].append(tli.child(j).isExpanded())

        self.ui.DataDock_View.clear()
        for datacat in ubglobals.DATACATEGORIES:
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, datacat)
            self.ui.DataDock_View.addTopLevelItem(twi)
        for spdata in ubglobals.SPATIALDATA:
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, spdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "<no data>")
            twi.addChild(twi_child)
            self.ui.DataDock_View.topLevelItem(0).addChild(twi)
        for tdata in ubglobals.TEMPORALDATA:
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, tdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "<no data>")
            twi.addChild(twi_child)
            self.ui.DataDock_View.topLevelItem(1).addChild(twi)
        twi = QtWidgets.QTreeWidgetItem()
        twi.setText(0, "<no data>")
        self.ui.DataDock_View.topLevelItem(2).addChild(twi)

        # Now reorganise the expanded and contracted menus.
        for i in range(self.ui.DataDock_View.topLevelItemCount()):
            tli = self.ui.DataDock_View.topLevelItem(i)
            tli.setExpanded(expandcol_tli[i])
            if i == 2:  # Qualitative data has no children
                continue
            for j in range(tli.childCount()):
                tli.child(j).setExpanded(expandcol_twi[i][j])

        # Adjust the pixmap on the expand/col button
        if sum(expandcol_tli) == len(expandcol_tli) \
            and sum([len(i) for i in expandcol_twi]) == sum([sum(i) for i in expandcol_twi]):
            # If true: then tree widget fully expanded
            self.set_expand_collapse_button_icon("expanded")
        else:
            # If not fully expanded, then can still be expanded so set the button to the collapsed state.
            self.set_expand_collapse_button_icon("collapsed")

    def remove_data_from_library(self):
        """Removes the current selected data set from the data library and the data library view."""
        selection = self.ui.DataDock_View.selectedItems()[0]
        if selection.childCount() == 0 and selection.text(0) != "<no data>":
            dataID = selection.toolTip(0).split(" - ")[0]
            dataref = self.get_active_data_library().get_data_with_id(dataID)
            scenario_list = dataref.get_scenario_list()
            for scen in scenario_list:
                scenario = self.get_active_simulation_object().get_scenario_by_name(scen)
                scenario.remove_data_reference(dataID)
            self.get_active_data_library().delete_data(dataID)

            parent = selection.parent()
            parent.removeChild(selection)
            if parent.childCount() == 0:
                twi = QtWidgets.QTreeWidgetItem()
                twi.setText(0, "<no data>")
                parent.addChild(twi)

            self.update_scenario_gui()
        else:
            return

    def update_data_library_view(self):
        """Called then changes are made to the data library object either through the addition or
        removal of data from the data library. The program goes through the data library and updates
        the tree widget."""
        self.reset_project_data_library_view()  # Redo the data library
        datalib = self.get_active_data_library()
        # Update Spatial Data Sets
        datacol = datalib.get_all_data_of_class("spatial")  # Get the list of data
        cur_toplevelitem = self.ui.DataDock_View.topLevelItem(0)
        for dref in datacol:
            dtype = dref.get_metadata("parent")  # Returns overall type (e.g. Land Use, Rainfall, etc.)
            dtypeindex = ubglobals.SPATIALDATA.index(dtype)    # Get the index in the tree-widget
            if cur_toplevelitem.child(dtypeindex).child(0).text(0) == "<no data>":
                cur_toplevelitem.child(dtypeindex).takeChild(0)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, dref.get_metadata("filename"))
            twi.setToolTip(0, str(dref.get_data_id()) + " - " + str(dref.get_data_file_path()))
            cur_toplevelitem.child(dtypeindex).addChild(twi)

        # Update Temporal Data Sets
        datacol = datalib.get_all_data_of_class("temporal")
        cur_toplevelitem = self.ui.DataDock_View.topLevelItem(1)
        for dref in datacol:
            dtype = dref.get_metadata("parent")
            dtypeindex = ubglobals.TEMPORALDATA.index(dtype)
            if cur_toplevelitem.child(dtypeindex).child(0).text(0) == "<no data>":
                cur_toplevelitem.child(dtypeindex).takeChild(0)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, dref.get_metadata("filename"))
            twi.setToolTip(0, str(dref.get_data_id()) + " - " + str(dref.get_data_file_path()))
            cur_toplevelitem.child(dtypeindex).addChild(twi)

        # Update the Qualitative Data Set
        datacol = datalib.get_all_data_of_class("qualitative")
        for dref in datacol:
            if self.ui.DataDock_View.topLevelItem(2).child(0).text(0) == "<no data>":
                self.ui.DataDock_View.topLevelItem(2).takeChild(0)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, dref.get_metadata("filename"))
            twi.setToolTip(0, str(dref.get_data_id()) + " - " + str(dref.get_data_file_path()))
            self.ui.DataDock_View.topLevelItem(2).addChild(twi)

    def show_metadata_dialog(self):
        pass

    def update_preview_data(self):
        pass

    def expand_collapse_data_library(self):
        """Expands or collapses the data library features based on the state of the data library. Also
        changes the expand/collapse button by calling the set_expand_collapse_button_icon() method.
        """
        if self.__datalibraryexpanded:
            self.ui.DataDock_View.collapseAll()
            self.set_expand_collapse_button_icon("collapsed")
            self.__datalibraryexpanded = False
        else:
            self.ui.DataDock_View.expandAll()
            self.set_expand_collapse_button_icon("expanded")
            self.__datalibraryexpanded = True

    def set_expand_collapse_button_icon(self, condition):
        """Changes the icon pixmap on the expanded and collapse button in the Project Data Library
        Dock Window depending on the condition provdied.

        :param condition: one of two values, 'collapsed' or 'expanded'."""
        if condition == "collapsed":
            icon14 = QtGui.QIcon()
            icon14.addPixmap(QtGui.QPixmap(":/icons/arrowright.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.expcolData.setIcon(icon14)
            self.ui.expcolData.setIconSize(QtCore.QSize(20, 20))
        elif condition == "expanded":
            icon14 = QtGui.QIcon()
            icon14.addPixmap(QtGui.QPixmap(":/icons/arrowdown.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.expcolData.setIcon(icon14)
            self.ui.expcolData.setIconSize(QtCore.QSize(20, 20))
        else:
            print("Something Wrong")

    # GETTERS and SETTERS
    def set_active_simulation_object(self, simobjectfromcore):
        self.__activeSimulationObject = simobjectfromcore

    def set_active_data_library(self, libraryfromcore):
        self.__activeDataLibrary = libraryfromcore

    def set_active_project_log(self, logfromcore):
        self.__activeProjectLog = logfromcore

    def get_active_simulation_object(self):
        return self.__activeSimulationObject

    def get_active_data_library(self):
        return self.__activeDataLibrary

    def get_active_project_log(self):
        return self.__activeProjectLog

    def set_save_project_state(self, status):
        """Reverses the state of saveProjectState. Tracks changes made to project settings. Then, changes
         the Main Window title depending on the save state. If unsaved, appends *, if saved, removes *

        :param status: bool, True = all changes saved, False = changes made and project unsaved
        :return: None
        """
        self.__saveProjectState = status
        if self.__saveProjectState:  # if saved
            self.setWindowTitle("UrbanBEATS Planning Support Tool - " + self.__current_project_name + "")
        else:
            self.setWindowTitle("UrbanBEATS Planning Support Tool - " + self.__current_project_name + "*")

    def get_save_project_state(self):
        return self.__saveProjectState

    def set_current_project_name(self, pname):
        self.__current_project_name = pname

    def get_current_project_name(self):
        return self.__current_project_name

    # MODULE BAR - LAUNCHING ALL MODULES
    def launch_influencefunction_gui(self):
        """Launches the influence function creator GUI, for creating and saving influence functions in the project."""
        ifunctiongui = InfluenceFunctionGUILaunch(self.get_active_simulation_object(),
                                                  self.get_active_project_log())
        ifunctiongui.exec_()

    def launch_spatialsetup_modulegui(self):
        """Launches the spatial setup module's user interface and fills in relevant parameters."""
        delinblocksgui = DelinBlocksGuiLaunch(self, self.get_active_simulation_object(),
                                              self.get_active_data_library(), self.get_active_project_log())
        delinblocksgui.exec_()

    def launch_climatesetup_modulegui(self):
        """Launches the climate setup module's user interface and fills in relevant parameters."""
        pass    # [TO DO]

    def launch_urbandev_modulegui(self):
        """Launches the urban development module's user interface and filles in relevant parameters."""
        urbandevgui = UrbdevelopGuiLaunch(self, self.get_active_simulation_object(),
                                          self.get_active_data_library(), self.get_active_project_log())
        urbandevgui.exec_()

    def launch_urbandynamics_modulegui(self):
        """Launches the urban dynamics setup module's user interface and fills in relevant parameters."""
        pass    # [TO DO]

    def launch_urbanplan_modulegui(self):
        """Launches the urban planning modules user interface and pre-fills all relevant parameters."""
        urbplanbbgui = UrbplanbbGuiLaunch(self, self.get_active_simulation_object(),
                                          self.get_active_data_library(), self.get_active_project_log())
        urbplanbbgui.exec_()

    def launch_spatialmap_modulegui(self):
        """Launches the spatial mapping module's user interface and fills in relevant parameters."""
        spatialmappinggui = SpatialMappingGuiLaunch(self, self.get_active_simulation_object(),
                                                    self.get_active_data_library(), self.get_active_project_log())
        spatialmappinggui.exec_()

    def launch_infrastructure_modulegui(self):
        """Launches the infrastructure module's user interface and fills in relevant parameters."""
        infrastructuregui = InfrastructureGuiLaunch(self, self.get_active_simulation_object(),
                                                    self.get_active_data_library(), self.get_active_project_log())
        infrastructuregui.exec_()

    def launch_bluegreen_modulegui(self):
        """Launches the Regulation module's user interface and fills in relevant parameters."""
        bluegreengui = BlueGreenGuiLaunch(self, self.get_active_simulation_object(),
                                          self.get_active_data_library(), self.get_active_project_log())

        bluegreengui.exec_()

    def launch_watercycle_modulegui(self):
        """Launches the Performance Assessment's user interface and fills in relevant parameters."""
        pass

    def launch_microclimate_modulegui(self):
        """"""
        pass

    def launch_flood_modulegui(self):
        """"""
        pass

    def launch_economics_modulegui(self):
        """"""
        pass

    # FUNCTIONS TO DO
    def checks_before_run(self):
        pass

    def raise_ub_error_message(self, message):
        pass

    def update_progress_bar_value(self, value):
        """Updates the progress bar of the Main GUI when the simulation is started/stopped/reset."""
        self.ui.ProgressBar.setValue(int(value))

    def call_run_simulation(self):
        """Executes the run function for the current scenario that is active in the Scenario Browser."""
        self.get_active_simulation_object().run()

    def enable_disable_run_controls(self, state):
        """Enabels or Disables the run button controls depending on run state."""
        self.ui.actionRun.setEnabled(state)
        self.ui.SimDock_run.setEnabled(state)

    def call_run_simulation_perfonly(self):
        pass

    #ENABLERS and DISABLERS
    def enable_disable_main_interface(self, condition):
        """Enables and disables certain components of the main interface depending on the condition
        specified. Note that this is somewhat different from self.__gui_state as that tracks general
        behaviour throughout the program. The condition here is just what idle state the GUI should be in.

        :param condition: "startup", "new" or "scenario" will determine which buttons are enabled
        """
        if condition == "startup":
            self.ui.DataDock.setEnabled(0)
            self.ui.ScenarioDock.setEnabled(0)
            self.ui.SimDock.setEnabled(0)
            self.ui.ScenarioView_Widget.setEnabled(0)
            self.ui.DataView_extent.setEnabled(0)
            self.ui.DataView_meta.setEnabled(0)
            self.ui.actionView_Full_Project_Log.setEnabled(0)
            self.ui.actionView_Project_Description.setEnabled(0)
            self.enable_disable_module_icons([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        elif condition == "new":
            self.ui.ModuleDock.setEnabled(1)
            self.ui.DataDock.setEnabled(1)
            self.ui.ScenarioDock.setEnabled(1)
            self.ui.SimDock.setEnabled(1)
            self.ui.ScenarioView_Widget.setEnabled(1)
            self.ui.DataView_extent.setEnabled(1)
            self.ui.DataView_meta.setEnabled(1)
            self.ui.actionView_Full_Project_Log.setEnabled(1)
            self.ui.actionView_Project_Description.setEnabled(1)
            self.enable_disable_module_icons([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        else:
            pass

    def enable_disable_module_icons(self, condition):
        """Enables and disables the module icons based on the conditions given. The input
        passed to this method is a list of booleans in the order of module buttons on the
        main interface. Note that this is somewhat different from self.__gui_state as that
        tracks general behaviour throughout the program. The condition here is just what
        idle state the GUI should be in.

        :param condition: [ ] list of booleans in order of module buttons on main window
        """
        self.ui.ModuleDock_spatialsetup.setEnabled(condition[0])
        self.ui.ModuleDock_climatesetup.setEnabled(condition[1])
        self.ui.ModuleDock_urbandev.setEnabled(condition[2])
        self.ui.ModuleDock_urbandynamics.setEnabled(condition[3])
        self.ui.ModuleDock_urbanplan.setEnabled(condition[4])
        self.ui.ModuleDock_spatialmap.setEnabled(condition[5])
        self.ui.ModuleDock_infrastructure.setEnabled(condition[6])
        self.ui.ModuleDock_bluegreen.setEnabled(condition[7])
        self.ui.ModuleDock_watercycle.setEnabled(condition[8])
        self.ui.ModuleDock_microclimate.setEnabled(condition[9])
        self.ui.ModuleDock_flood.setEnabled(condition[10])
        self.ui.ModuleDock_economics.setEnabled(condition[11])

# --- OBSERVERS ---
class ConsoleObserver(QtCore.QObject):
    """Defines the observer class that will work with the console window in
    UrbanBEATS' main window."""

    updateConsole = QtCore.pyqtSignal(str, name="updateConsole")

    def update_observer(self, textmessage):
        """Emits <updateConsole> signal"""
        self.updateConsole.emit(textmessage)


class ProgressBarObserver(QtCore.QObject):
    """Defines the observer class that will work with the progress bar in the
    UrbanBEATS Main Window."""

    updateProgress = QtCore.pyqtSignal(int, name="updateProgressBar")

    def update_progress(self, value):
        """Emits <updateProgress> signal"""
        self.updateProgress.emit(value)


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


sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

sys.excepthook = exception_hook

# --- MAIN PROGRAM RUNTIME ---
if __name__ == "__main__":

    # --- OBTAIN AND STORE PATH DATA FOR PROGRAM ---
    UBEATSROOT = os.path.dirname(sys.argv[0])  # Obtains the program's root directory
    UBEATSROOT = UBEATSROOT.encode('unicode-escape').decode('utf-8')  # To avoid weird bugs e.g. if someone's folder path

    UBEATSTEMP = tempfile.mkdtemp()

    random.seed()

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
    # translator = QtCore.QTranslator()
    # translator.load("i18n\\zh_CN")
    # app.installTranslator(translator)

    # --- SPLASH SCREEN ---
    splash_matrix = ["innsbruck", "sydney", "melbourne", "ticino", "quebec", "montreal", "singapore",
                     "sanfran", "zurich", "delft"]
    splash_pix = QtGui.QPixmap("media/splash_" + splash_matrix[random.randint(0, len(splash_matrix)-1)] + ".png")
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

    # Set the initial Leaflet map
    main_window.reset_data_view_to_default()
    main_window.enable_disable_main_interface("startup")

    time.sleep(1)

    start_screen = StartScreenLaunch(main_window)       # Begin the Start Screen Loop
    # Signals for the Main Window and Start Screen Connection
    start_screen.startupNew.connect(main_window.create_new_project)
    start_screen.startupOpen.connect(main_window.open_existing_project)
    start_screen.startupImport.connect(main_window.import_existing_project)
    start_screen.startupOptions.connect(lambda: main_window.show_options(0))

    start_screen.exec_()    # End the Start Screen Loop

    sys.exit(app.exec_())   # END OF MAIN WINDOW LOOP
