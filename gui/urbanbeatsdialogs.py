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

# --- CODE STRUCTURE ---
#       (1) Preferences Dialog
#       (2)
#
# --- --- --- --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import sys
import os
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ubdatalibrary as ubdatalibrary

from aboutdialog import Ui_AboutDialog      # About UrbanBEATS Dialog
from preferencesdialog import Ui_PreferencesDialog      # Preferences Dialog
from startnewprojectdialog import Ui_ProjectSetupDialog     # Start New Project Dialog
from logdialog import Ui_LogDialog         # Project Log Dialog
from adddatadialog import Ui_AddDataDialog      # Add Data Dialog
from newscenario import Ui_NewScenarioDialog    # Scenario Creation Dialog
from mapexportoptions import Ui_MapExportDialog
from reportoptions import Ui_ReportingDialog


# --- ABOUT DIALOG ---
class AboutDialogLaunch(QtWidgets.QDialog):
    """Class definition for the about dialog window. Connects the GUI
    Ui_AboutDialog() with the Main Window"""
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)


# --- ADD DATA DIALOG ---
class AddDataDialogLaunch(QtWidgets.QDialog):
    """Class definition for the add data dialog window for importing and managing data."""
    dataLibraryUpdated = QtCore.pyqtSignal()

    def __init__(self, main, simulation, datalibrary, parent=None):
        """Class constructor, references the data library object active in the simulation as well as the main
        runtime class.

        :param main: referring to the main GUI so that changes can be made in real-time to the main interface
        :param datalibrary: the data library object, which will be updated as data files are added to the project.
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_AddDataDialog()
        self.ui.setupUi(self)

        # --- INITIALIZE MAIN VARIABLES ---
        self.maingui = main    # the main runtime - for GUI changes
        self.simulation = simulation
        self.datalibrary = datalibrary      # the simulation object's data library
        self.currentDataType = "spatial"
        self.ui.spatial_radio.setChecked(1)

        # Update the category and sub-category combo boxes
        self.update_datacat_combo()
        self.update_datacatsub_combo()

        # --- SIGNALS AND SLOTS ---
        self.ui.adddatabrowse.clicked.connect(self.browse_for_data)
        self.ui.spatial_radio.clicked.connect(self.update_datacat_combo)
        self.ui.temporal_radio.clicked.connect(self.update_datacat_combo)
        self.ui.qualitative_radio.clicked.connect(self.update_datacat_combo)
        self.ui.datacat_combo.currentIndexChanged.connect(self.update_datacatsub_combo)

        self.ui.adddata_button.clicked.connect(self.add_data_to_project)
        self.ui.cleardata_button.clicked.connect(self.clear_interface)
        self.ui.done_button.clicked.connect(self.close)

    def browse_for_data(self):
        """Allows the user to select a data file to load into the model's data library."""
        if self.ui.spatial_radio.isChecked():
            datatype = "Spatial Formats (*.txt *shp)"
        elif self.ui.temporal_radio.isChecked():
            datatype = "Temporal Data (*.txt *.csv *.dat *.nc)"
        else:
            datatype = "Qualitative Data (*.txt *.csv *.dat)"

        message = "Browse for Input Data File..."
        datafile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir,datatype)
        if datafile:
            self.ui.databox.setText(datafile)

    def update_datacat_combo(self):
        """Updates the data category combo box depending on whether it should display spatial, temporal
        or qualitative data. The update is dependent on the checked radio button. The function also
        updates the main data browse box. If the user selected temporal data and then changed the
        format, then the selected file should no longer be valid and will disappear."""
        if self.ui.spatial_radio.isChecked():
            if self.currentDataType != "spatial":
                self.ui.databox.setText("<none>")
            self.ui.datacat_combo.setEnabled(1)
            self.ui.datacat_combo.clear()
            self.ui.datacat_combo.addItem("<undefined>")
            for i in ubglobals.SPATIALDATA:
                self.ui.datacat_combo.addItem(i)
        elif self.ui.temporal_radio.isChecked():
            if self.currentDataType != "temporal":
                self.ui.databox.setText("<none>")
            self.ui.datacat_combo.setEnabled(1)
            self.ui.datacat_combo.clear()
            self.ui.datacat_combo.addItem("<undefined>")
            for i in ubglobals.TEMPORALDATA:
                self.ui.datacat_combo.addItem(i)
        else:
            if self.currentDataType != "qualitative":
                self.ui.databox.setText("<none>")
            self.ui.datacat_combo.setEnabled(0)
            self.ui.datacat_combo.clear()
            self.ui.datacat_combo.addItem("<undefined>")
        self.ui.datacat_combo.setCurrentIndex(1)

    def update_datacatsub_combo(self):
        """Updates the sub-category combo box based on the required sub-classification of various
        data sets."""
        self.ui.datacatsub_combo.clear()
        self.ui.datacatsub_combo.addItem("<undefined>")
        try:
            subcategories = ubglobals.SUBDATASETS[str(self.ui.datacat_combo.currentText())]
        except KeyError:
            self.ui.datacatsub_combo.setEnabled(0)
            return
        self.ui.datacatsub_combo.setEnabled(1)
        for i in subcategories:
            self.ui.datacatsub_combo.addItem(i)
        self.ui.datacatsub_combo.setCurrentIndex(0)

    def clear_interface(self):
        """Clears the addData interface by removing the text in the browse box (setting it to <none>),
        checking one of the radio buttons and updating the combo boxes."""
        self.ui.databox.setText("<none>")
        self.ui.spatial_radio.setChecked(1)
        self.update_datacat_combo()
        self.update_datacatsub_combo()

    def add_data_to_project(self):
        """Adds the data to the project based on all the information provided. Checks for the validity
        of the data file."""
        datafile = self.ui.databox.text()
        if self.ui.spatial_radio.isChecked():
            self.currentDataType = "spatial"
        elif self.ui.temporal_radio.isChecked():
            self.currentDataType = "temporal"
        else:
            self.currentDataType = "qualitative"

        if os.path.isfile(datafile):
            if self.ui.datacat_combo.currentText() != "<undefined>":
                if self.ui.datacatsub_combo.isEnabled() == 0 \
                        or self.ui.datacatsub_combo.currentIndex() != 0:
                    datatype = []
                    datatype.append(self.currentDataType)   # index 0
                    datatype.append(self.ui.datacat_combo.currentText())    # index 1
                    datatype.append(self.ui.datacatsub_combo.currentText()) # index 2
                    datatype.append(os.path.splitext(datafile)[1])  # index 3
                    dataref = ubdatalibrary.\
                        UrbanBeatsDataReference(datatype, datafile,
                                                self.simulation.get_project_parameter("projectpath"),
                                                self.simulation.get_project_parameter("keepcopy"),
                                                self.ui.notes_box.toPlainText())
                    self.datalibrary.add_data_to_library(dataref)
                    self.dataLibraryUpdated.emit()
                    self.clear_interface()
                else:
                    prompt_msg = "Please select a valid classification"
                    QtWidgets.QMessageBox.warning(self, 'Invalid Classification', prompt_msg, QtWidgets.QMessageBox.Ok)
            else:
                prompt_msg = "Please select a valid classification"
                QtWidgets.QMessageBox.warning(self, 'Invalid Classification', prompt_msg, QtWidgets.QMessageBox.Ok)
        else:
            prompt_msg = "Invalid Data Set! Please select a valid file."
            QtWidgets.QMessageBox.warning(self, 'Invalid Data', prompt_msg, QtWidgets.QMessageBox.Ok)


# --- CREATE SCENARIO DIALOG ---
class CreateScenarioLaunch(QtWidgets.QDialog):
    """Class definition for the create scenario dialog window. Connects the GUI Ui_NewScenarioDialog()
    with the Main Window"""

    def __init__(self, main, simulation, datalibrary, viewmode, parent=None):
        """Class constructor, references the active runtime, active simulation and data library.

        :param main: active instance of the MainWindow() class
        :param simulation: active instance of the UrbanBeatsSimulation() class
        :param datalibrary: active instance of the data library in the main simulation
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_NewScenarioDialog()
        self.ui.setupUi(self)

        # --- INITIALIZE MAIN VARIABLES ---
        self.maingui = main
        self.simulation = simulation
        self.datalibrary = datalibrary
        self.scenario = simulation.get_active_scenario()

        self.ui.name_box.setText(self.scenario.get_metadata("name"))

        if self.scenario.get_metadata("type") == "STATIC":
            self.ui.static_radio.setChecked(1)
        elif self.scenario.get_metadata("type") == "BENCHMARK":
            self.ui.benchmark_radio.setChecked(1)
        else:
            self.ui.dynamic_radio.setChecked(1)

        self.ui.narrative_box.setPlainText(self.scenario.get_metadata("narrative"))

        self.ui.startyear_spin.setValue(int(self.scenario.get_metadata("startyear")))
        self.ui.endyear_spin.setValue(int(self.scenario.get_metadata("endyear")))
        self.ui.timestep_spin.setValue(int(self.scenario.get_metadata("dt")))
        self.ui.benchmark_spin.setValue(int(self.scenario.get_metadata("benchmarks")))

        self.ui.naming_line.setText(self.scenario.get_metadata("filename"))
        self.ui.naming_check.setChecked(self.scenario.get_metadata("usescenarioname"))

        # MODULE CHECKBOXES
        self.ui.citydevelopment.setChecked(self.scenario.check_is_module_active("URBDEV"))
        self.ui.urbanplanning.setChecked(self.scenario.check_is_module_active("URBPLAN"))
        self.ui.socioeconomic.setChecked(self.scenario.check_is_module_active("SOCIO"))
        self.ui.spatialmapping.setChecked(self.scenario.check_is_module_active("MAP"))
        self.ui.regulation.setChecked(self.scenario.check_is_module_active("REG"))
        self.ui.infrastructure.setChecked(self.scenario.check_is_module_active("INFRA"))
        self.ui.performance.setChecked(self.scenario.check_is_module_active("PERF"))
        self.ui.impact.setChecked(self.scenario.check_is_module_active("IMPACT"))
        self.ui.decisionanalysis.setChecked(self.scenario.check_is_module_active("DECISION"))

        self.enable_disable_module_checkboxes()
        self.enable_disable_settings_tab()
        self.enable_disable_naming_line()

        self.update_dialog_data_library()

        # --- SIGNALS AND SLOTS
        self.ui.benchmark_radio.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.static_radio.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.dynamic_radio.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.benchmark_radio.clicked.connect(self.enable_disable_settings_tab)
        self.ui.static_radio.clicked.connect(self.enable_disable_settings_tab)
        self.ui.dynamic_radio.clicked.connect(self.enable_disable_settings_tab)

        self.ui.urbanplanning.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.spatialmapping.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.regulation.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.infrastructure.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.performance.clicked.connect(self.enable_disable_module_checkboxes)
        self.ui.impact.clicked.connect(self.enable_disable_module_checkboxes)

        self.ui.naming_check.clicked.connect(self.enable_disable_naming_line)
        self.ui.create_button.clicked.connect(self.create_scenario)
        self.ui.clear_button.clicked.connect(self.reset_interface)

        self.ui.add_to_button.clicked.connect(self.add_datalibrary_to_scenariodata)
        self.ui.remove_from_button.clicked.connect(self.remove_scenariodata_entry)

        if viewmode == 1:
            self.enable_disable_guis_for_viewonly()

    def add_datalibrary_to_scenariodata(self):
        """Description"""
        pass

    def remove_scenariodata_entry(self):
        """Description"""
        pass

    def reset_scenario_tree_widgets(self):
        """Resets the scenario tree widgets back to original before populating it with data."""
        self.ui.scenariodata_tree.clear()
        self.ui.datalibrary_tree.clear()
        for datacat in ubglobals.DATACATEGORIES:
            dtwi = QtWidgets.QTreeWidgetItem()
            dtwi.setText(0, datacat)
            self.ui.datalibrary_tree.addTopLevelItem(dtwi)

            stwi = QtWidgets.QTreeWidgetItem()
            stwi.setText(0, datacat)
            self.ui.scenariodata_tree.addTopLevelItem(stwi)

        for spdata in ubglobals.SPATIALDATA:
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, spdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "<no data>")
            twi.addChild(twi_child)
            self.ui.datalibrary_tree.topLevelItem(0).addChild(twi)
        for tdata in ubglobals.TEMPORALDATA:
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, tdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "<no data>")
            twi.addChild(twi_child)
            self.ui.datalibrary_tree.topLevelItem(1).addChild(twi)

    def update_dialog_data_library(self):
        """Just like the main window, this method populates the dialog window's data library
        browser with the info from the project's data library."""
        self.reset_scenario_tree_widgets()  # Redo the data library
        datacol = self.datalibrary.get_all_data_of_class("spatial")  # Get the list of data
        cur_toplevelitem = self.ui.datalibrary_tree.topLevelItem(0)
        for dref in datacol:
            dtype = dref.get_metadata("parent")  # Returns overall type (e.g. Land Use, Rainfall, etc.)
            dtypeindex = ubglobals.SPATIALDATA.index(dtype)  # Get the index in the tree-widget
            if cur_toplevelitem.child(dtypeindex).child(0).text(0) == "<no data>":
                cur_toplevelitem.child(dtypeindex).takeChild(0)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, dref.get_metadata("filename"))
            twi.setToolTip(0, str(dref.get_dataID()) + " - " + str(dref.get_data_file_path()))
            cur_toplevelitem.child(dtypeindex).addChild(twi)

        # Update Temporal Data Sets
        datacol = self.datalibrary.get_all_data_of_class("temporal")
        cur_toplevelitem = self.ui.datalibrary_tree.topLevelItem(1)
        for dref in datacol:
            dtype = dref.get_metadata("parent")
            dtypeindex = ubglobals.TEMPORALDATA.index(dtype)
            if cur_toplevelitem.child(dtypeindex).child(0).text(0) == "<no data>":
                cur_toplevelitem.child(dtypeindex).takeChild(0)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, dref.get_metadata("filename"))
            twi.setToolTip(0, str(dref.get_dataID()) + " - " + str(dref.get_data_file_path()))
            cur_toplevelitem.child(dtypeindex).addChild(twi)

        # Update the Qualitative Data Set
        datacol = self.datalibrary.get_all_data_of_class("qualitative")
        for dref in datacol:
            if self.ui.datalibrary_tree.topLevelItem(2).child(0).text(0) == "<no data>":
                self.ui.datalibrary_tree.topLevelItem(2).takeChild(0)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, dref.get_metadata("filename"))
            twi.setToolTip(0, str(dref.get_dataID()) + " - " + str(dref.get_data_file_path()))
            self.ui.datalibrary_tree.topLevelItem(2).addChild(twi)

        self.ui.datalibrary_tree.expandAll()
        self.ui.scenariodata_tree.expandAll()

    def enable_disable_guis_for_viewonly(self):
        """Disables all items to prevent user interference once the scenario has been creatd. The edit scenario
        option is only meant for changes in file naming convention, narrative, data and name changes.

        :return:
        """
        self.ui.static_radio.setEnabled(0)
        self.ui.benchmark_radio.setEnabled(0)
        self.ui.dynamic_radio.setEnabled(0)
        self.ui.timestep_widget.setEnabled(0)
        self.ui.timestep_widget_2.setEnabled(0)
        self.enable_disable_module_checkboxes(special="ALL")

    def enable_disable_settings_tab(self):
        """Enables and disables the details tab widgets based on the simulation type selected. This determines
        what kinds of options are available to the user.

        :return: None (GUI changes)
        """
        if self.ui.dynamic_radio.isChecked():
            self.ui.benchmark_spin.setEnabled(0)
            self.ui.timestep_spin.setEnabled(1)
            self.ui.endyear_spin.setEnabled(1)
        elif self.ui.benchmark_radio.isChecked():
            self.ui.benchmark_spin.setEnabled(1)
            self.ui.timestep_spin.setEnabled(0)
            self.ui.endyear_spin.setEnabled(0)
        elif self.ui.static_radio.isChecked():
            self.ui.benchmark_spin.setEnabled(0)
            self.ui.timestep_spin.setEnabled(0)
            self.ui.endyear_spin.setEnabled(0)

    def enable_disable_module_checkboxes(self, **kwargs):
        """Enables and disables the module checkboxes based on various conditionals. This is a clusterfuck of
        if else statements! Good luck working out the logic!
        """
        boxes = [self.ui.spatialmapping, self.ui.regulation, self.ui.infrastructure,
                 self.ui.performance, self.ui.impact, self.ui.decisionanalysis]
        # LOGIC CHAIN 1 - URBAN DEVELOPMENT
        # Spatial setup and climate setup are ALWAYS active
        try:
            if kwargs["special"] == "ALL":
                mbool = [0, 0, 0, 0, 0, 0]
                [boxes[b].setEnabled(mbool[b]) for b in range(len(boxes))]
                self.ui.urbanplanning.setEnabled(0)
                self.ui.citydevelopment.setEnabled(0)
                self.ui.socioeconomic.setEnabled(0)
                return
        except KeyError:
            pass

        if self.ui.static_radio.isChecked() or self.ui.benchmark_radio.isChecked():
            self.ui.citydevelopment.setEnabled(0)  # no urban development if static or benchmark mode
        else:
            self.ui.citydevelopment.setEnabled(1)

        # Urban Planning Module Chain
        if self.ui.urbanplanning.isChecked():
            mbool = [1, 1, 1, 1, 1, 1]
            [boxes[b].setEnabled(mbool[b]) for b in range(len(boxes))]  # list comprehension a.k.a. one-line for loop
        else:
            mbool = [0, 0, 0, 0, 0, 0]
            [boxes[b].setEnabled(mbool[b]) for b in range(len(boxes))]
            return

        # Spatial Mapping Chain
        if self.ui.spatialmapping.isChecked():
            mbool = [1, 1, 1, 1, 1, 1]
            [boxes[b].setEnabled(mbool[b]) for b in range(len(boxes))]
        else:
            mbool = [1, 1, 0, 0, 0, 0]
            [boxes[b].setEnabled(mbool[b]) for b in range(len(boxes))]
            return

        # Conditions to enable infrastructure planning
        if self.ui.regulation.isChecked() and self.ui.spatialmapping.isChecked():
            self.ui.infrastructure.setEnabled(1)
        else:
            self.ui.infrastructure.setEnabled(0)

        if self.ui.spatialmapping.isChecked():
            self.ui.decisionanalysis.setEnabled(1)
        else:
            self.ui.decisionanalysis.setEnabled(0)

    def enable_disable_naming_line(self):
        """Enables or disables the naming convention lineEdit if the checkbox is unchecked/checked."""
        self.ui.naming_line.setEnabled(not self.ui.naming_check.isChecked())

    def uncheck_all_module_checkboxes(self):
        """Unchecks all module checkboxes as part of the resetting of the user interface. Then calls enable
        disable method."""
        self.ui.urbanplanning.setChecked(0)
        self.ui.citydevelopment.setChecked(0)
        self.ui.socioeconomic.setChecked(0)
        self.ui.spatialmapping.setChecked(0)
        self.ui.regulation.setChecked(0)
        self.ui.infrastructure.setChecked(0)
        self.ui.performance.setChecked(0)
        self.ui.impact.setChecked(0)
        self.ui.decisionanalysis.setChecked(0)
        self.enable_disable_module_checkboxes()

    def reset_interface(self):
        """Reverts entire interface back to default settings."""
        self.ui.setup_widget.setCurrentIndex(0)

        # Refresh narrative tab
        self.ui.name_box.setText("<enter scenario name>")
        self.ui.narrative_box.setPlainText("<enter scenario description")
        self.ui.static_radio.setChecked(1)
        self.ui.endyear_spin.setValue(2068)
        self.ui.startyear_spin.setValue(2018)
        self.ui.timestep_spin.setValue(1)

        # Refresh Modules
        self.uncheck_all_module_checkboxes()
        self.enable_disable_settings_tab()

        # Refresh Data TreeWidgets

        # Refresh Output tab
        self.ui.naming_line.setText("<enter a naming convention for outputs>")
        self.ui.naming_check.setChecked(0)

    def fill_data_library_from_project(self):
        """Fills out the data library treewidget with the data from the project."""
        pass

    def create_scenario(self):
        """Saves the newly created data to the scenario object and closes the window. Accept() signal
        calls core functions that then create the scenario."""
        self.scenario.set_metadata("name", str(self.ui.name_box.text()))
        self.scenario.set_metadata("narrative", str(self.ui.narrative_box.toPlainText()))

        if self.ui.static_radio.isChecked():
            self.scenario.set_metadata("type", "STATIC")
        elif self.ui.benchmark_radio.isChecked():
            self.scenario.set_metadata("type", "BENCHMARK")
        else:
            self.scenario.set_metadata("type", "DYNAMIC")

        self.scenario.set_metadata("startyear", int(self.ui.startyear_spin.value()))
        self.scenario.set_metadata("endyear", int(self.ui.endyear_spin.value()))
        self.scenario.set_metadata("dt", int(self.ui.timestep_spin.value()))
        self.scenario.set_metadata("benchmarks", int(self.ui.benchmark_spin.value()))

        # Activate the modules
        if self.ui.citydevelopment.isChecked():
            self.scenario.set_module_active("URBDEV")
        if self.ui.urbanplanning.isChecked():
            self.scenario.set_module_active("URBPLAN")
        if self.ui.socioeconomic.isChecked():
            self.scenario.set_module_active("SOCIO")
        if self.ui.spatialmapping.isChecked():
            self.scenario.set_module_active("MAP")
        if self.ui.regulation.isChecked():
            self.scenario.set_module_active("REG")
        if self.ui.infrastructure.isChecked():
            self.scenario.set_module_active("INFRA")
        if self.ui.performance.isChecked():
            self.scenario.set_module_active("PERF")
        if self.ui.impact.isChecked():
            self.scenario.set_module_active("IMPACT")
        if self.ui.decisionanalysis.isChecked():
            self.scenario.set_module_active("DECISION")

        # Data Sets

        # Outputs
        self.scenario.set_metadata("usescenarioname", self.ui.naming_check.isChecked())
        if self.ui.naming_check.isChecked():
            self.scenario.set_metadata("filename", self.ui.name_box.text().replace(" ", "_"))
        else:
            self.scenario.set_metadata("filename", self.ui.naming_line.text().replace(" ", "_"))

        self.accept()

    def done(self, r):
        """Checks if the scenario name already exists and if it does, tells the user to choose a different
        name."""
        scenario_name = self.ui.name_box.text()
        nochars = False
        for char in ubglobals.NOCHARS:
            if char in scenario_name:
                nochars = True
        if self.Accepted == r:
            if self.simulation.check_for_existing_scenario_by_name(scenario_name):
                prompt_msg = "Error, scenario name already exists, please choose a different name!"
                QtWidgets.QMessageBox.warning(self, 'Duplicate Scenario', prompt_msg, QtWidgets.QMessageBox.Ok)
            elif nochars:
                prompt_msg = "Please enter a valid name without special characters!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Name', prompt_msg, QtWidgets.QMessageBox.Ok)
            else:
                # OK all good.
                QtWidgets.QDialog.done(self, r)  # Call the parent's method instead of the override.
        else:
            # If cancel or close is called, ignore
            QtWidgets.QDialog.done(self, r)  # Call the parent's method instead of the override.

# --- MAP EXPORT DIALOG ---
class MapExportDialogLaunch(QtWidgets.QDialog):
    """Class definition for the export options for all spatial maps from UrbanBEATS. Connects the GUI
    Ui_MapExportDialog() with the Main Window."""
    def __init__(self, scenarios, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_MapExportDialog()
        self.ui.setupUi(self)

        self.ui.ok_button.clicked.connect(self.save_values)
        self.ui.cancel_button.clicked.connect(self.reject)

    def save_values(self):
        """Saves all values to the project's current scenario. This is relevant as the scenario's settings will
        determine what gets exported to files."""
        # Save stuff
        self.accept()


# --- REPORTING OPTIONS DIALOG ---
class ReportingDialogLaunch(QtWidgets.QDialog):
    """Class definition for the reporting dialog window Ui_ReportingDialog(), which connects to the main
    Window."""
    def __init__(self, simulation, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_ReportingDialog()
        self.ui.setupUi(self)

        self.ui.create_button.clicked.connect(self.create_report)
        self.ui.done_button.clicked.connect(self.save_values)

    def create_report(self):
        pass

    def save_values(self):
        self.close()


# --- SETUP NEW PROJECT DIALOG ---
class NewProjectDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the setup of a new project dialog window Ui_ProjectSetupDialog
    with the main window or startup dialog. This dialog helps the user set up a new project from
    scratch and includes the essential elements for creating the initial project folder."""
    def __init__(self, simulation, viewer, parent=None):
        """Initialization of class, takes two key parameters that differentiate the dialog window's
        use as a viewer or a setup dialog.

        :param main: the instance of the main runtime environment
        :param viewer: int, if 0, then the dialog is being opened for a new project, 1 to modify, 2 to view
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_ProjectSetupDialog()
        self.ui.setupUi(self)
        self.__viewer = viewer
        self.simulation = simulation

        # --- PRE-FILLING GUI SETUP ---
        if self.__viewer == 1:     # Edit Project Details
            self.disable_non_modifiable_parameters()
        if self.__viewer == 2:     # View Project Details
            self.disable_all_parameters()

        # --- GUI PARAMETERS ---
        self.ui.projname_line.setText(self.simulation.get_project_parameter("name"))
        self.ui.region_line.setText(self.simulation.get_project_parameter("region"))
        self.ui.location_combo.setCurrentIndex(ubglobals.CITIES.index(self.simulation.get_project_parameter("city")))
        self.ui.modellername_box.setText(self.simulation.get_project_parameter("modeller"))
        self.ui.affiliation_box.setText(self.simulation.get_project_parameter("affiliation"))
        self.ui.otherpersons_box.setPlainText(self.simulation.get_project_parameter("otherpersons"))
        self.ui.synopsis_box.setPlainText(self.simulation.get_project_parameter("synopsis"))
        self.ui.projectboundary_line.setText(self.simulation.get_project_parameter("boundaryshp"))

        if self.simulation.get_project_parameter("logstyle") == "comprehensive":
            self.ui.projectlog_compreh.setChecked(1)
        else:
            self.ui.projectlog_simple.setChecked(1)

        self.ui.projpath_line.setText(self.simulation.get_project_parameter("projectpath"))
        self.ui.keepcopy_check.setChecked(int(self.simulation.get_project_parameter("keepcopy")))

        # --- SIGNALS AND SLOTS ---
        self.ui.projectboundary_browse.clicked.connect(self.browse_boundary_file)
        self.ui.projpath_button.clicked.connect(self.browse_project_path)
        self.accepted.connect(self.run_setup_project)

    def browse_boundary_file(self):
        """Opens a file dialog, which requests a shapefile of the case study boundary. UrbanBEATS
        uses this to delineate data for the project and for visualisation purposes and other calculations."""
        message = "Browse for Project Boundary Shapefile..."
        boundaryfile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir, "Shapefile (*.shp)")
        if boundaryfile:
            self.ui.projectboundary_line.setText(boundaryfile)

    def browse_project_path(self):
        """Opens a file dialog, which requests for a folder path within which UrbanBEATS will
        create the project folders and move input maps if requested."""
        message = "Select the folder you wish to create the project in..."
        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
        if folderpath:
            self.ui.projpath_line.setText(str(folderpath))

    def disable_non_modifiable_parameters(self):
        """Disabled several key input parameters that cannot be modified if the project
        has already been created. The method is called if the GUI is being opened as a viewer
        rather than for the setup of a new proejct. Items disabled include the project name,
        the log settings, the path and whether to copy data into the project folder."""
        self.ui.projname_line.setEnabled(0)
        self.ui.projectlog_compreh.setEnabled(0)
        self.ui.projectlog_simple.setEnabled(0)
        self.ui.projpath_line.setEnabled(0)
        self.ui.projpath_button.setEnabled(0)
        self.ui.keepcopy_check.setEnabled(0)

    def disable_all_parameters(self):
        """Disables the whole interface as it was opened just for viewing the information."""
        self.ui.aboutproject_widget1.setEnabled(0)
        self.ui.aboutproject_widget2.setEnabled(0)
        self.ui.aboutuser_widget.setEnabled(0)
        self.ui.synopsis_box.setEnabled(0)
        self.ui.boundary_widget.setEnabled(0)
        self.ui.projectlog_widget.setEnabled(0)
        self.ui.path_widget.setEnabled(0)

    def run_setup_project(self):
        """Determines based on how the GUI was opened what needs to occur. If self.__viewer == 0 then
        new project signal is emitted with the dictionary of details. If self.__viewer == 1 then an update
        of project parameters is passed back to the main runtime. If self.__viewer == 2, then nothing
        happens and the dialog window just closes."""
        if self.__viewer == 0:
            # Do stuff
            self.save_values()
        elif self.__viewer == 1:
            self.save_values()
        else:
            pass    # Just viewing, just close the window.

    def done(self, r):
        """Overwriting the done() method so that checks can be made before closing the window,
        automatically gets called when the signals "accepted()" or "rejected()" are emitted.

        :param r: The signal type
        :return: Nothing if all conditions are fine, warning message box if not.
        """
        if self.Accepted == r:
            conditions_met = [1, 1]
            if os.path.isdir(self.ui.projpath_line.text()):
                pass
            else:
                prompt_msg = "Please select a valid project path!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Path', prompt_msg, QtWidgets.QMessageBox.Ok)
                conditions_met[0] = 0
            if os.path.isfile(self.ui.projectboundary_line.text()):
                pass
            else:
                prompt_msg = "Please select a valid boundary shapefile!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Boundary File', prompt_msg, QtWidgets.QMessageBox.Ok)
                conditions_met[1] = 0
            if sum(conditions_met) == len(conditions_met):
                self.save_values()
                QtWidgets.QDialog.done(self, r)
            else:
                return
        else:
            QtWidgets.QDialog.done(self, r) # Call the parent's method instead of the override.

    def save_values(self):
        """Saves all project parameters values and returns a dictionary for use to setup simulation."""
        self.simulation.set_project_parameter("name", self.ui.projname_line.text())
        self.simulation.set_project_parameter("region", self.ui.region_line.text())
        self.simulation.set_project_parameter("city", ubglobals.CITIES[self.ui.location_combo.currentIndex()])
        self.simulation.set_project_parameter("modeller", self.ui.modellername_box.text())
        self.simulation.set_project_parameter("affiliation", self.ui.affiliation_box.text())
        self.simulation.set_project_parameter("otherpersons", self.ui.otherpersons_box.toPlainText())
        self.simulation.set_project_parameter("synopsis", self.ui.synopsis_box.toPlainText())
        self.simulation.set_project_parameter("boundaryshp", self.ui.projectboundary_line.text())
        self.simulation.set_project_parameter("projectpath", self.ui.projpath_line.text())
        self.simulation.set_project_parameter("keepcopy", int(self.ui.keepcopy_check.isChecked()))

        if self.ui.projectlog_compreh.isChecked():
            self.simulation.set_project_parameter("logstyle", "comprehensive")
        else:
            self.simulation.set_project_parameter("logstyle", "simplfied")


# --- PREFERENCES DIALOG ---
class PreferenceDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the preferences dialog. Connects the GUI
    Ui_PreferenceDialog() with the Main Window. This dialog is primarily for adjusting
    global model options. These options are saved in the Main Window class (main.pyw) rather than
    model core."""
    def __init__(self, main, tabindex, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self.ui.options_tabs.setCurrentIndex(tabindex)

        self.module = main
        self.options = main.get_options()

        # --- FILL IN GUI ---
        # GENERAL TAB
        self.ui.modellername_line.setText(str(self.options["defaultmodeller"]))
        self.ui.modelleraffil_line.setText(str(self.options["defaultaffil"]))

        if self.options["projectlogstyle"] == "comprehensive":
            self.ui.projectlog_compreh.setChecked(1)
        else:
            self.ui.projectlog_simple.setChecked(0)

        self.ui.lang_combo.setCurrentIndex(ubglobals.LANGUAGECOMBO.index(self.options["language"]))

        self.ui.location_combo.setCurrentIndex(ubglobals.CITIES.index(self.options["city"]))
        self.ui_coords_line_enabledisable()

        self.ui.projpath_line.setText(str(self.options["defaultpath"]))
        self.ui.temppath_line.setText(str(self.options["tempdir"]))
        self.ui.temppath_check.setChecked(bool(self.options["tempdefault"]))
        self.ui_temppath_line_enabledisable()

        # Text Appearance

        # SIMULATION TAB
        self.ui.numiter_spin.setValue(int(self.options["maxiterations"]))
        self.ui.tolerance_spin.setValue(float(self.options["globaltolerance"]))

        self.ui.decision_combo.setCurrentIndex(ubglobals.DECISIONS.index(self.options["defaultdecision"]))

        # MAP SETTINGS TAB
        self.ui.mapstyle_combo.setCurrentIndex(ubglobals.MAPSTYLES.index(self.options["mapstyle"]))
        self.ui_setmapstyle_pixmap()

        self.ui.tileserver_line.setText(self.options["tileserverURL"])
        self.ui.cache_check.setChecked(bool(self.options["cachetiles"]))
        self.ui.offline_check.setChecked(bool(self.options["offline"]))

        self.ui.coords_combo.setCurrentIndex(ubglobals.COORDINATESYSTEMS.index(self.options["defaultcoordsys"]))
        self.ui.epsg_line.setText(self.options["customepsg"])
        self.ui_epsg_line_enabledisable()

        # EXTERNAL TAB
        self.ui.epanetpath_line.setText(self.options["epanetpath"])
        self.ui.swmmpath_line.setText(self.options["swmmpath"])
        self.ui.musicpath_line.setText(self.options["musicpath"])

        # ONLINE TAB
        # Coming Soon.

        # --- SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.reset_button.clicked.connect(self.reset_values)
        self.ui.location_combo.currentIndexChanged.connect(self.ui_coords_line_enabledisable)
        self.ui.temppath_check.clicked.connect(self.ui_temppath_line_enabledisable)
        self.ui.projpath_button.clicked.connect(lambda: self.get_path("P"))
        self.ui.temppath_button.clicked.connect(lambda: self.get_path("T"))
        self.ui.mapstyle_combo.currentIndexChanged.connect(self.ui_setmapstyle_pixmap)
        self.ui.coords_combo.currentIndexChanged.connect(self.ui_epsg_line_enabledisable)
        self.ui.epanetpath_button.clicked.connect(lambda: self.get_path("E"))
        self.ui.swmmpath_button.clicked.connect(lambda: self.get_path("S"))
        self.ui.musicpath_button.clicked.connect(lambda: self.get_path("M"))

    def get_path(self, path_type):
        """Opens a browse window in search for a folder path based on the input path_type. After user
        chooses the path, data is filled into the relevant GUI widget.

        :param path_type: type of path, "P" = project, "T" = temp, "E" = epanet, "S" = swmm, "M" = MUSIC
        :return: None
        """
        if path_type == "P":
            message = "Default Path for Projects"
        elif path_type == "T":
            message = "Default Path for Temp Directory"
        elif path_type == "E":
            message = "Installation Directory for EPANET2"
        elif path_type == "S":
            message = "Installation Directory for SWMM"
        elif path_type == "M":
            message = "Installation Directory for MUSIC"
        else:
            message = "How am I supposed to know what path I want!?"

        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
        if folderpath:
            if path_type == "P":
                self.ui.projpath_line.setText(folderpath)
            elif path_type == "T":
                self.ui.temppath_line.setText(folderpath)
            elif path_type == "E":
                self.ui.epanetpath_line.setText(folderpath)
            elif path_type == "S":
                self.ui.swmmpath_line.setText(folderpath)
            elif path_type == "M":
                self.ui.musicpath_line.setText(folderpath)

    def ui_setmapstyle_pixmap(self):
        """Dynamically changes the displayed minimap on the preference dialog Map Settings Tab to the appropriate
        map style."""
        mapstylepixmaps = ["mt_cartodb.png", "mt_esriworld.png", "mt_osm.png",
                           "mt_stamentoner.png", "mt_stamenterrain.png"]
        self.ui.mapstyle_pic.setPixmap(QtGui.QPixmap(":/media/map templates/" +
                                                     mapstylepixmaps[self.ui.mapstyle_combo.currentIndex()]))

    def ui_epsg_line_enabledisable(self):
        """Enables or disables the EPSG line edit depending on whether 'Other' coordinate system was selected."""
        if self.ui.coords_combo.currentIndex() == self.ui.coords_combo.count() - 1:
            self.ui.epsg_line.setEnabled(1)
        else:
            self.ui.epsg_line.setEnabled(0)

    def ui_temppath_line_enabledisable(self):
        """Enables/Disables the temppath_line widget and button based on the tempdir temppath checkbox."""
        if self.ui.temppath_check.isChecked():
            self.ui.temppath_line.setEnabled(0)
            self.ui.temppath_button.setEnabled(0)
        else:
            self.ui.temppath_line.setEnabled(1)
            self.ui.temppath_button.setEnabled(1)

    def ui_coords_line_enabledisable(self):
        """Enables/Disables the coordinates input box based on selected city"""
        if self.ui.location_combo.currentIndex() == self.ui.location_combo.count()-1:
            self.ui.coords_line.setEnabled(1)
        else:
            self.ui.coords_line.setEnabled(0)

    def reset_values(self):
        """Resets all option values and closes the options/preferences dialog window."""
        self.module.reset_default_options()
        self.reject()   # close the dialog window but do not update it

    def save_values(self):
        """Saves the updated options to the main window and calls the update function to modify the
        .cfg file with new options.

        :return: None
        """
        # GENERAL TAB
        self.options["defaultmodeller"] = str(self.ui.modellername_line.text())
        self.options["defaultaffil"] = str(self.ui.modelleraffil_line.text())
        if self.ui.projectlog_compreh.isChecked():
            self.options["projectlogstyle"] = "comprehensive"
        else:
            self.options["projectlogstyle"] = "simplified"

        self.options["language"] = str(ubglobals.LANGUAGECOMBO[self.ui.lang_combo.currentIndex()])
        self.options["city"] = str(ubglobals.CITIES[self.ui.location_combo.currentIndex()])

        self.options["coordinates"] = str(self.ui.coords_line.text())
        self.options["defaultpath"] = str(self.ui.projpath_line.text())
        self.options["tempdir"] = str(self.ui.temppath_line.text())
        self.options["tempdefault"] = int(self.ui.temppath_check.isChecked())

        # Text Appearance

        # SIMULATION TAB
        self.options["maxiterations"] = int(self.ui.numiter_spin.value())
        self.options["globaltolerance"] = float(self.ui.tolerance_spin.value())
        self.options["defaultdecision"] = str(ubglobals.DECISIONS[self.ui.decision_combo.currentIndex()])

        # MAP SETTINGS TAB
        self.options["mapstyle"] = str(ubglobals.MAPSTYLES[self.ui.mapstyle_combo.currentIndex()])
        self.options["tileserverURL"] = str(self.ui.tileserver_line.text())
        self.options["cachetiles"] = int(self.ui.cache_check.isChecked())
        self.options["offline"] = int(self.ui.offline_check.isChecked())
        self.options["defaultcoordsys"] = str(ubglobals.COORDINATESYSTEMS[self.ui.coords_combo.currentIndex()])
        self.options["customepsg"] = str(self.ui.epsg_line.text())

        # EXTERNAL TAB
        self.options["epanetpath"] = str(self.ui.epanetpath_line.text())
        self.options["swmmpath"] = str(self.ui.swmmpath_line.text())
        self.options["musicpath"] = str(self.ui.musicpath_line.text())

        #ONLINE TAB
        # Coming Soon

        #UPDATE THE CFG FILE BY EMITTING THE SIGNAL
        self.module.write_new_options(self.options)


# --- PROJECT LOG DIALOG ---
class ProjectLogLaunch(QtWidgets.QDialog):
    """Class instance for the project log window."""
    def __init__(self, logobject, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_LogDialog()
        self.ui.setupUi(self)
        self.__logobject = logobject

        # --- SIGNALS AND SLOTS ---
        self.ui.export_log.clicked.connect(self.export_log)
        self.ui.log_widget.currentChanged.connect(self.disable_clear_button)
        self.ui.done_button.clicked.connect(self.close)

    def disable_clear_button(self):
        if self.ui.log_widget.currentIndex() == 1:
            self.ui.clear_log.setEnabled(0)
        else:
            self.ui.clear_log.setEnabled(1)

    def export_log(self):
        pass


# --- VIEW METADATA DIALOG ---

# --- MAP EXPORT OPTIONS DIALOG ---

# --- REPORTING OPTIONS DIALOG ---