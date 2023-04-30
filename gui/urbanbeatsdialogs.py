r"""
@file   urbanbeatsdialogs.py
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

# --- CODE STRUCTURE ---
#       (1) Preferences Dialog
#       (2)
#
# --- --- --- --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import os
import datetime
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ubdatalibrary as ubdatalibrary
import model.ublibs.ubspatial as ubspatial

from .aboutdialog import Ui_AboutDialog      # About UrbanBEATS Dialog
from .preferencesdialog import Ui_PreferencesDialog      # Preferences Dialog
from .startnewprojectdialog import Ui_ProjectSetupDialog     # Start New Project Dialog
from .openprojectdialog import Ui_OpenProjectDialog      # Open Existing Project Dialog
from .logdialog import Ui_LogDialog         # Project Log Dialog
from .adddatadialog import Ui_AddDataDialog      # Add Data Dialog
from .newscenario import Ui_NewScenarioDialog    # Scenario Creation Dialog
from .metadatadialog import Ui_MetadataDialog   # Metadata dialogue for asset collection query
from .mapexportoptions import Ui_MapExportDialog
from .reportoptions import Ui_ReportingDialog


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

        self.shortcutpath = None
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
        if self.shortcutpath is None:
            dir = os.curdir
        else:
            dir = self.shortcutpath

        if self.ui.spatial_radio.isChecked():
            datatype = "Spatial Formats (*.txt *.shp *.tif *.asc)"
        elif self.ui.temporal_radio.isChecked():
            datatype = "Temporal Data (*.txt *.csv *.dat *.nc)"
        else:
            datatype = "Qualitative Data (*.txt *.csv *.dat)"

        message = "Browse for Input Data File..."
        datafile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, datatype)
        if datafile:
            self.ui.databox.setText(datafile)
        self.shortcutpath = os.path.dirname(datafile)

    def update_datacat_combo(self):
        """Updates the data category combo box depending on whether it should display spatial, temporal
        or qualitative data. The update is dependent on the checked radio button. The function also
        updates the main data browse box. If the user selected temporal data and then changed the
        format, then the selected file should no longer be valid and will disappear."""
        if self.ui.spatial_radio.isChecked():
            if self.currentDataType != "spatial":
                self.ui.databox.setText("(none)")
            self.ui.datacat_combo.setEnabled(1)
            self.ui.datacat_combo.clear()
            self.ui.datacat_combo.addItem("(undefined)")
            for i in ubdatalibrary.SPATIALDATA_DEFN.keys():
                self.ui.datacat_combo.addItem(i)
        elif self.ui.temporal_radio.isChecked():
            if self.currentDataType != "temporal":
                self.ui.databox.setText("(none)")
            self.ui.datacat_combo.setEnabled(1)
            self.ui.datacat_combo.clear()
            self.ui.datacat_combo.addItem("(undefined)")
            for i in ubdatalibrary.TEMPORALDATA_DEFN.keys():
                self.ui.datacat_combo.addItem(i)
        else:
            if self.currentDataType != "qualitative":
                self.ui.databox.setText("(none)")
            self.ui.datacat_combo.setEnabled(1)
            self.ui.datacat_combo.clear()
            self.ui.datacat_combo.addItem("(undefined)")
            for i in ubdatalibrary.QUALDATA_DEFN.keys():
                self.ui.datacat_combo.addItem(i)
        self.ui.datacat_combo.setCurrentIndex(1)

    def update_datacatsub_combo(self):
        """Updates the sub-category combo box based on the required sub-classification of various
        data sets."""
        self.ui.datacatsub_combo.clear()
        self.ui.datacatsub_combo.addItem("(undefined)")
        if self.ui.spatial_radio.isChecked():       # SPATIAL DATA
            try:
                subcategories = ubdatalibrary.SPATIALDATA_DEFN[str(self.ui.datacat_combo.currentText())]
            except KeyError:
                self.ui.datacatsub_combo.setCurrentIndex(0)
                return True
        elif self.ui.temporal_radio.isChecked():    # TEMPORAL DATA
            try:
                subcategories = ubdatalibrary.TEMPORALDATA_DEFN[str(self.ui.datacat_combo.currentText())]
            except KeyError:
                self.ui.datacatsub_combo.setCurrentIndex(0)
                return True
        else:       # QUALITATIVE DATA
            try:
                subcategories = ubdatalibrary.QUALDATA_DEFN[str(self.ui.datacat_combo.currentText())]
            except KeyError:
                self.ui.datacatsub_combo.setCurrentIndex(0)
                return True

        if len(subcategories) == 0:
            self.ui.datacatsub_combo.setEnabled(0)
            return
        else:
            self.ui.datacatsub_combo.setEnabled(1)
        for i in subcategories:
            self.ui.datacatsub_combo.addItem(i)
        self.ui.datacatsub_combo.setCurrentIndex(0)
        return

    def clear_interface(self):
        """Clears the addData interface by removing the text in the browse box (setting it to (none)),
        checking one of the radio buttons and updating the combo boxes."""
        self.ui.databox.setText("(none)")
        self.ui.spatial_radio.setChecked(1)
        self.update_datacat_combo()
        self.update_datacatsub_combo()
        self.ui.notes_box.setPlainText("none")

    def add_data_to_project(self):
        """Adds the data to the project based on all the information provided. Checks for the validity
        of the data file. Function collects the essential infos for the dataref class constructor:
        datatype, fullfillpath, projectpath, keepcopy, notes_text. Datatype comprises several aspects:
        [dataclass, type, subtype, format, file_extension]"""
        datafile = self.ui.databox.text()
        if self.ui.spatial_radio.isChecked():       # datatype[0]
            self.currentDataType = "spatial"
        elif self.ui.temporal_radio.isChecked():
            self.currentDataType = "temporal"
        else:
            self.currentDataType = "qualitative"

        if os.path.isfile(datafile):    # If the file exists
            if self.ui.datacat_combo.currentText() != "(undefined)":    # If the current Text is NOT (undefined)
                if not self.ui.datacatsub_combo.isEnabled() or self.ui.datacatsub_combo.currentIndex() != 0:    # If sub-categorisation is enabled
                    datatype = []
                    datatype.append(self.currentDataType)   # index 0
                    datatype.append(self.ui.datacat_combo.currentText())    # index 1
                    datatype.append(self.ui.datacatsub_combo.currentText()) # index 2
                    datatype.append(os.path.splitext(datafile)[1])  # index 3
                    print("File_ext:", datatype[3])     # index 4
                    # Determine data format...
                    if datatype[0] == "temporal":
                        datatype.append("TIMESERIES")
                    elif datatype[0] == "qualitative":
                        datatype.append("QUALITATIVE")
                    elif datatype[3] == ".shp":
                        datatype.append("VECTOR")
                    else:
                        datatype.append("RASTER")


                    # Create the Data Reference Object
                    projectpath = self.simulation.get_project_parameter("projectpath") + "/" +\
                                  self.simulation.get_project_parameter("name")
                    keepcopy = self.simulation.get_project_parameter("keepcopy")
                    notes = self.ui.notes_box.toPlainText()
                    dataref = ubdatalibrary.UrbanBeatsDataReference(datatype, datafile, projectpath, keepcopy, notes)
                    self.datalibrary.add_data_to_library(dataref, True)
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
        self.viewmode = viewmode

        self.ui.name_box.setText(self.scenario.get_metadata("name"))

        self.ui.boundary_combo.clear()
        self.ui.boundary_combo.addItem("(select simulation boundary)")
        boundarynames = self.simulation.get_project_boundary_names()
        for n in boundarynames:
            self.ui.boundary_combo.addItem(str(n))
        scenario_boundaryname = self.scenario.get_metadata("boundary")
        if scenario_boundaryname == "(select simulation boundary)":
            self.ui.boundary_combo.setCurrentIndex(0)
        else:
            self.ui.boundary_combo.setCurrentIndex(list(boundarynames).index(scenario_boundaryname)+1)

        self.ui.narrative_box.setPlainText(self.scenario.get_metadata("narrative"))

        self.ui.startyear_spin.setValue(int(self.scenario.get_metadata("startyear")))
        self.ui.naming_line.setText(self.scenario.get_metadata("filename"))
        self.ui.naming_check.setChecked(self.scenario.get_metadata("usescenarioname"))

        self.enable_disable_naming_line()
        self.update_dialog_data_library()

        # --- SIGNALS AND SLOTS
        self.ui.naming_check.clicked.connect(self.enable_disable_naming_line)
        self.ui.create_button.clicked.connect(self.create_scenario)
        self.ui.clear_button.clicked.connect(self.reset_interface)
        self.ui.add_to_button.clicked.connect(self.add_datalibrary_to_scenariodata)
        self.ui.remove_from_button.clicked.connect(self.remove_scenariodata_entry)

        if self.viewmode == 1:
            self.enable_disable_guis_for_editonly()

            dataclass = ["spatial", "temporal", "qualitative"]
            for i in range(len(dataclass)):
                datarefs = self.scenario.get_data_reference(dataclass[i])
                self.ui.scenariodata_tree.topLevelItem(i).takeChildren()
                for dref in datarefs:
                    twi = QtWidgets.QTreeWidgetItem()
                    twi.setText(0, dref.get_metadata("filename"))
                    twi.setToolTip(0, str(dref.get_data_id())+" :: "+str(dref.get_data_file_path()))
                    self.ui.scenariodata_tree.topLevelItem(i).addChild(twi)

    def enable_disable_guis_for_editonly(self):
        """Disables certain features of the interface for editing mode."""
        self.ui.name_box.setEnabled(0)
        # self.ui.startyear_spin.setEnabled(0)
        # self.ui.naming_line.setEnabled(0)
        # self.ui.naming_check.setEnabled(0)
        self.ui.create_button.setText("Update...")
        self.ui.clear_button.setEnabled(0)

    def add_datalibrary_to_scenariodata(self):
        """Adds an entry in the data library to the scenario data tree widget."""
        selection = self.ui.datalibrary_tree.currentItem()
        if selection.childCount() == 0 and selection.text(0) != "(no data)":
            # Then we have a data set
            dataID, filepath = selection.toolTip(0).split(" :: ")
            filename = selection.text(0)
            dataref = self.datalibrary.get_data_with_id(dataID)
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, filename)
            twi.setToolTip(0, str(dataID + " :: " + filepath))
            if dataref.get_metadata("class") == "spatial":
                self.ui.scenariodata_tree.topLevelItem(0).addChild(twi)
            elif dataref.get_metadata("class") == "temporal":
                self.ui.scenariodata_tree.topLevelItem(1).addChild(twi)
            else:
                self.ui.scenariodata_tree.topLevelItem(2).addChild(twi)

    def remove_scenariodata_entry(self):
        """Description"""
        selection = self.ui.scenariodata_tree.currentItem()
        if selection.text(0) not in ["Spatial Data", "Temporal Data", "Qualitative Data"]:
            # filename = selection.text(0)
            # dataID, filepath = selection.toolTip(0).split(" :: ")
            parent = selection.parent()
            parent.removeChild(selection)

    def reset_scenario_tree_widgets(self):
        """Resets the scenario tree widgets back to original before populating it with data."""
        self.ui.scenariodata_tree.clear()
        self.ui.datalibrary_tree.clear()
        for datacat in ubdatalibrary.DATACATEGORIES:
            dtwi = QtWidgets.QTreeWidgetItem()
            dtwi.setText(0, datacat)
            self.ui.datalibrary_tree.addTopLevelItem(dtwi)
            stwi = QtWidgets.QTreeWidgetItem()
            stwi.setText(0, datacat)
            self.ui.scenariodata_tree.addTopLevelItem(stwi)
        for spdata in ubdatalibrary.SPATIALDATA_DEFN.keys():
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, spdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "(no data)")
            twi.addChild(twi_child)
            self.ui.datalibrary_tree.topLevelItem(0).addChild(twi)
        for tdata in ubdatalibrary.TEMPORALDATA_DEFN.keys():
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, tdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "(no data)")
            twi.addChild(twi_child)
            self.ui.datalibrary_tree.topLevelItem(1).addChild(twi)
        for qdata in ubdatalibrary.QUALDATA_DEFN.keys():
            twi = QtWidgets.QTreeWidgetItem()
            twi.setText(0, qdata)
            twi_child = QtWidgets.QTreeWidgetItem()
            twi_child.setText(0, "(no data)")
            twi.addChild(twi_child)
            self.ui.datalibrary_tree.topLevelItem(2).addChild(twi)

    def update_dialog_data_library(self):
        """Just like the main window, this method populates the dialog window's data library
        browser with the info from the project's data library."""
        self.reset_scenario_tree_widgets()  # Redo the data library
        datacol_classes = ["spatial", "temporal", "qualitative"]
        datalib_refs = [list(ubdatalibrary.SPATIALDATA_DEFN.keys()),
                          list(ubdatalibrary.TEMPORALDATA_DEFN.keys()),
                          list(ubdatalibrary.QUALDATA_DEFN.keys())]    # TO DO  - update for qualitative
        for i in range(len(datacol_classes)):
            datacol = self.datalibrary.get_all_data_of_class(datacol_classes[i])    # Get the list of data
            cur_toplevelitem = self.ui.datalibrary_tree.topLevelItem(i)
            for dref in datacol:
                dtype = dref.get_metadata("type")
                dtypeindex = datalib_refs[i].index(dtype)
                if cur_toplevelitem.child(dtypeindex).child(0).text(0) == "(no data)":
                    cur_toplevelitem.child(dtypeindex).takeChild(0)
                twi = QtWidgets.QTreeWidgetItem()
                twi.setText(0, dref.get_metadata("filename"))
                twi.setToolTip(0, str(dref.get_data_id()) + " :: " + str(dref.get_data_file_path()))
                cur_toplevelitem.child(dtypeindex).addChild(twi)

        self.ui.datalibrary_tree.expandAll()
        self.ui.scenariodata_tree.expandAll()

    def enable_disable_naming_line(self):
        """Enables or disables the naming convention lineEdit if the checkbox is unchecked/checked."""
        self.ui.naming_line.setEnabled(not self.ui.naming_check.isChecked())

    def reset_interface(self):
        """Reverts entire interface back to default settings."""
        self.ui.setup_widget.setCurrentIndex(0)

        # Refresh narrative tab
        self.ui.name_box.setText("(enter scenario name)")
        self.ui.narrative_box.setPlainText("(enter scenario description)")
        self.ui.startyear_spin.setValue(2018)

        # Refresh Output tab
        self.ui.naming_line.setText("(enter a naming convention for outputs)")
        self.ui.naming_check.setChecked(0)

    def update_scenario_edit(self):
        """Called when the 'create' button is pressed during 'edit mode'. Note that the
        create button will display the words 'Update...' during the edit scenario mode.
        Things that can be updated include the narrative and the data used."""
        self.scenario.set_metadata("narrative", str(self.ui.narrative_box.toPlainText()))
        self.scenario.set_metadata("filename", str(self.ui.naming_line.text()))
        self.scenario.set_metadata("usescenarioname", int(self.ui.naming_check.isChecked()))
        self.update_scenario_datasets()

    def update_scenario_datasets(self):
        """Updates the scenario's data sets with the newly added or removed data maps."""
        olddatasets = self.scenario.get_data_reference("spatial")
        newdatasets = []
        for i in range(self.ui.scenariodata_tree.topLevelItem(0).childCount()):
            dataID, filepath = self.ui.scenariodata_tree.topLevelItem(0).child(i).toolTip(0).split(" :: ")
            filename = self.ui.scenariodata_tree.topLevelItem(0).child(i).text(0)
            dref = self.datalibrary.get_data_with_id(dataID)
            if self.scenario.has_dataref(dataID):
                pass  # if the scenario already has the data in it, ignore
            else:
                self.scenario.add_data_reference(dref)
                dref.assign_scenario(self.scenario.get_metadata("name"))
            newdatasets.append(dref)

        # print(f"Old Data Set Length {len(olddatasets)}")
        # print(f"New Data Set Length {len(newdatasets)}")
        data_to_remove = []
        for dref in olddatasets:
            if dref not in newdatasets:
                data_to_remove.append(dref)
        for dref in data_to_remove:
            self.scenario.remove_data_reference(dref.get_data_id())
            dref.remove_from_scenario(self.scenario.get_metadata("name"))

        # Temporal Data
        olddatasets = self.scenario.get_data_reference("temporal")
        newdatasets = []
        for i in range(self.ui.scenariodata_tree.topLevelItem(1).childCount()):
            dataID, filepath = self.ui.scenariodata_tree.topLevelItem(1).child(i).toolTip(0).split(" :: ")
            filename = self.ui.scenariodata_tree.topLevelItem(1).child(i).text(0)
            dref = self.datalibrary.get_data_with_id(dataID)
            if self.scenario.has_dataref(dataID):
                pass  # if the scenario already has the data in it, ignore
            else:
                self.scenario.add_data_reference(dref)
                dref.assign_scenario(self.scenario.get_metadata("name"))
            newdatasets.append(dref)
        data_to_remove = []
        for dref in olddatasets:
            if dref not in newdatasets:
                data_to_remove.append(dref)
        for dref in data_to_remove:
            self.scenario.remove_data_reference(dref.get_data_id())
            dref.remove_from_scenario(self.scenario.get_metadata("name"))

        # Qualitative Data
        olddatasets = self.scenario.get_data_reference("qualitative")
        newdatasets = []
        for i in range(self.ui.scenariodata_tree.topLevelItem(2).childCount()):
            dataID, filepath = self.ui.scenariodata_tree.topLevelItem(2).child(i).toolTip(0).split(" :: ")
            filename = self.ui.scenariodata_tree.topLevelItem(2).child(i).text(0)
            dref = self.datalibrary.get_data_with_id(dataID)
            if self.scenario.has_dataref(dataID):
                pass  # if the scenario already has the data in it, ignore
            else:
                self.scenario.add_data_reference(dref)
                dref.assign_scenario(self.scenario.get_metadata("name"))
            newdatasets.append(dref)
        data_to_remove = []
        for dref in olddatasets:
            if dref not in newdatasets:
                data_to_remove.append(dref)
        for dref in data_to_remove:
            self.scenario.remove_data_reference(dref.get_data_id())
            dref.remove_from_scenario(self.scenario.get_metadata("name"))

    def create_scenario(self):
        """Saves the newly created data to the scenario object and closes the window. Accept() signal
        calls core functions that then create the scenario."""
        if self.viewmode == 1:
            self.update_scenario_edit()

        self.scenario.set_metadata("name", str(self.ui.name_box.text()))
        self.scenario.set_metadata("boundary", str(self.ui.boundary_combo.currentText()))
        self.scenario.set_metadata("narrative", str(self.ui.narrative_box.toPlainText()))
        self.scenario.set_metadata("startyear", int(self.ui.startyear_spin.value()))

        self.update_scenario_datasets()

        # Outputs
        self.scenario.set_metadata("usescenarioname", int(self.ui.naming_check.isChecked()))
        if self.ui.naming_check.isChecked():
            self.scenario.set_metadata("filename", self.ui.name_box.text().replace(" ", "_"))
        else:
            self.scenario.set_metadata("filename", self.ui.naming_line.text().replace(" ", "_"))

        self.accept()

    def done(self, r):
        """Checks if the scenario name already exists and if it does, tells the user to choose a different
        name."""
        if self.viewmode == 1:
            QtWidgets.QDialog.done(self, r)  # Call the parent's method instead of the override.
            return
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


class ShowMetadataDialogLaunch(QtWidgets.QDialog):
    """Class definition for the metadata dialogue to view asset collection information in UrbanBEATS."""
    def __init__(self, main, simulation, assetname, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_MetadataDialog()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main
        self.simulation = simulation
        self.asset_col = simulation.get_global_asset_collection()
        self.export_path = self.simulation.get_project_path()+"/output/"
        self.meta = None
        self.assets = None

        # --- SETUP DYNAMIC COMBO BOX ---
        self.ui.assetcol_combo.clear()
        self.ui.assetcol_combo.addItem("(select asset collection)")
        [self.ui.assetcol_combo.addItem(str(asset_name)) for asset_name in self.asset_col.keys()]
        if assetname == 0:
            self.ui.assetcol_combo.setCurrentIndex(0)
        else:
            pass    # Then we need to locate the correct asset collection

        # SIGNALS AND SLOTS
        self.ui.assetcol_combo.currentIndexChanged.connect(self.update_metadatadialog_with_assetcol_data)
        self.ui.assetcol_assettypes_combo.currentIndexChanged.connect(self.update_attributes_table)
        self.ui.export_button.clicked.connect(self.export_assetcol_report)

    def update_metadatadialog_with_assetcol_data(self):
        # Clear all GUI elements
        self.ui.module_list.clear()
        self.ui.assetcol_assettypes_combo.clear()
        self.ui.attributes_list.clear()

        # Grab asset collection information and start populating
        if self.ui.assetcol_combo.currentText() not in self.asset_col.keys():
            return True
        else:
            self.assets = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
            if self.assets is None:
                return True
        self.meta = self.assets.get_asset_with_name("meta")

        # Population Asset Type Combo
        asset_types = self.assets.get_asset_types()
        self.ui.assetcol_assettypes_combo.addItem("(select an asset type to view data)")
        for key in asset_types.keys():
            self.ui.assetcol_assettypes_combo.addItem(str(key))

        # Update Modules Table
        for att in self.meta.get_all_attributes():
            if "mod_" in att:
                twi = QtWidgets.QTreeWidgetItem()
                twi.setText(0, str(att.split("mod_")[1]))
                twi.setText(1, "Today")
                self.ui.module_list.addTopLevelItem(twi)
        self.ui.module_list.resizeColumnToContents(0)
        return True

    def update_attributes_table(self):
        self.ui.attributes_list.clear()
        if self.ui.assetcol_assettypes_combo.currentText() == "Metadata":
            metadata = self.meta.get_all_attributes()
            self.ui.attributes_list.headerItem().setText(2, "Value")
            for att in metadata:
                if "mod_" in att:
                    continue
                twi = QtWidgets.QTreeWidgetItem()
                twi.setText(0, str(att))
                twi.setText(1, "-")
                twi.setText(2, str(metadata[att]))
                self.ui.attributes_list.addTopLevelItem(twi)
            # Do the population based on self.meta
            pass
        else:   # Not the metadata
            self.ui.attributes_list.headerItem().setText(2, "Description")
            pass
        self.ui.attributes_list.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.ui.attributes_list.resizeColumnToContents(0)
        return True

    def export_assetcol_report(self):
        print("Exporting Asset Collection report")
        pass


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


# --- OPEN PROJECT DIALOG ---
class OpenProjectDialogLaunch(QtWidgets.QDialog):
    """Class definition for the open existing project dialog window Ui_OpenProjectDialog with the
    main window or startup dialog. This dialog helps the user select from an existing list of recent
    projects or browse or a project location on the system."""
    def __init__(self, simulation, viewer=3, recent_projects=[], parent=None):
        """Initialization of class, takes several key parameters that allows the program to infill
        information into the dialog window.

        :param simulation: the simulation object
        :param viewer: a viewmode, like with the New Project Launch dialog, its default value is set to 3 as this is
        :param recent_projects: a list of recent projects containing 3 attributes: [name, modeller, path]
        always going to be called in relation to opening a project.
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_OpenProjectDialog()
        self.ui.setupUi(self)
        self.__viewer = viewer
        self.simulation = simulation
        self.__recent = recent_projects

        # --- POPULATE RECENT PROJECTS TABLE ---
        # The table is only populated if the user has pressed 'saved' during the project. This updates
        # UrbanBEATS' config file with recent projects.
        self.ui.project_table.setRowCount(0)
        self.populate_table()
        self.enable_disable_buttons()

        # --- SIGNALS & SLOTS ---
        self.ui.projpath_button.clicked.connect(self.browse_project_path)
        self.ui.project_table.itemSelectionChanged.connect(self.table_selection_to_path_box)
        self.ui.project_table.itemSelectionChanged.connect(self.enable_disable_buttons)

        # --- BUTTONS ---
        self.ui.info_button.clicked.connect(self.info_button_activate)
        self.ui.clear_button.clicked.connect(self.clear_button_activate)
        self.ui.delete_button.clicked.connect(self.delete_button_activate)
        self.ui.import_button.clicked.connect(self.import_button_activate)
        self.ui.export_button.clicked.connect(self.export_button_activate)
        self.ui.project_table.itemDoubleClicked.connect(self.accept)

    def enable_disable_buttons(self):
        """Enables and disables the buttons based on what has been clicked on the project table."""
        if self.ui.project_table.rowCount() == 0:       # Check if the table has rows
            self.ui.info_button.setEnabled(0)
            self.ui.export_button.setEnabled(0)
            self.ui.clear_button.setEnabled(0)
            self.ui.delete_button.setEnabled(0)
        if len(self.ui.project_table.selectedItems()) == 0:     # If something has NOT been selected in the table
            self.ui.info_button.setEnabled(0)
            self.ui.export_button.setEnabled(0)
            self.ui.delete_button.setEnabled(0)
        elif len(self.ui.project_table.selectedItems()) > 0:    # Otherwise something has been selected!
            self.ui.info_button.setEnabled(1)
            self.ui.export_button.setEnabled(1)
            self.ui.delete_button.setEnabled(1)

    def info_button_activate(self):
        """Called when the info button has been clicked."""
        print("Info Button")
        pass

    def clear_button_activate(self):
        """Called when the clear button has been clicked."""
        print("Clear Button")
        pass

    def delete_button_activate(self):
        """Called when the delete button has been clicked."""
        print("Delete Button")
        pass

    def import_button_activate(self):
        """Called when the import button has been clicked."""
        print("Import Button")
        pass

    def export_button_activate(self):
        """Called when the export button has been clicked."""
        print("Export Button")
        pass

    def table_selection_to_path_box(self):
        """Called when an item in the QTableWidget is clicked or unselected. The path box is altered with the path
        of the selected project."""
        tselection = self.ui.project_table.selectedItems()
        if len(tselection) == 3:
            self.ui.projpath_line.setText(str(tselection[2].text()))
        else:
            self.ui.projpath_line.setText("(none)")

    def browse_project_path(self):
        """Opens a file dialog, which requests for a folder path of the project folder. """
        self.ui.project_table.clearSelection()
        message = "Browse for Project Folder Location..."
        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
        if folderpath:
            self.ui.projpath_line.setText(str(folderpath))

    def populate_table(self):
        """ Populates the recent projects table with recent projects undertaken by teh user. """
        rowindex = 0
        for row in range(len(self.__recent)):
            if os.path.isdir(self.__recent[row][2]):
                self.ui.project_table.insertRow(rowindex)
                for col in range(len(self.__recent[row])):
                    twi = QtWidgets.QTableWidgetItem(str(self.__recent[row][col]))
                    self.ui.project_table.setItem(rowindex, col, twi)
                rowindex += 1
            else:
                continue
        self.ui.project_table.resizeColumnsToContents()

    def done(self, r):
        """ Loads the project folder location's info file and other files to help set up the simulation
        object self.simulation before exiting the GUI."""

        # Check whether the project selected is valid.
        if self.Accepted == r:      # Accepting to open the project
            conditions_met = [1]
            if os.path.isfile(self.ui.projpath_line.text()+"/info.ubdata"):    # Does the 'info.ubdata' file exist?
                pass    # Yes, there is a valid UrbanBEATS file
            else:
                prompt_msg = "Please select a valid project path!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Path', prompt_msg, QtWidgets.QMessageBox.Ok)
                conditions_met[0] = 0
            if sum(conditions_met) == len(conditions_met):
                self.load_project_info()        # Loads info.ubdata file and populates self.simulation with info
                QtWidgets.QDialog.done(self, r)
            else:
                return
        else:
            QtWidgets.QDialog.done(self, r)  # Call the parent's method instead of the override.

    def load_project_info(self):
        """ Loads the info.ubdata file in the project folder and writes the basic information """
        self.simulation.load_project_info_datafile(self.ui.projpath_line.text())


# --- SETUP NEW PROJECT DIALOG ---
class NewProjectDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the setup of a new project dialog window Ui_ProjectSetupDialog
    with the main window or startup dialog. This dialog helps the user set up a new project from
    scratch and includes the essential elements for creating the initial project folder."""
    def __init__(self, main, simulation, viewer, parent=None):
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
        self.epsg_dict = main.epsg_dict     # [REVAMP]
        self.cities_dict = main.cities_dict

        # --- PRE-FILLING GUI SETUP ---
        if self.__viewer == 1:     # Edit Project Details
            self.disable_non_modifiable_parameters()
        if self.__viewer == 2:     # View Project Details
            self.disable_all_parameters()

        # --- GUI PARAMETERS ---
        self.ui.projname_line.setText(self.simulation.get_project_parameter("name"))
        self.ui.date_spin.setDate(self.simulation.get_project_parameter("date"))
        self.ui.region_line.setText(self.simulation.get_project_parameter("region"))        # [REVAMP] - city library
        self.ui.modellername_box.setText(self.simulation.get_project_parameter("modeller"))
        self.ui.affiliation_box.setText(self.simulation.get_project_parameter("affiliation"))
        self.ui.otherpersons_box.setPlainText(self.simulation.get_project_parameter("otherpersons"))

        self.ui.projpath_line.setText(self.simulation.get_project_parameter("projectpath"))
        self.ui.keepcopy_check.setChecked(int(self.simulation.get_project_parameter("keepcopy")))

        self.ui.synopsis_box.setPlainText(self.simulation.get_project_parameter("synopsis"))

        if self.simulation.get_project_parameter("logstyle") == "comprehensive":
            self.ui.projectlog_compreh.setChecked(1)
        else:
            self.ui.projectlog_simple.setChecked(1)

        # Country combo box
        self.update_country_combo()
        countryname = self.simulation.get_project_parameter("country")
        countrynames = list(self.cities_dict.keys())
        if countryname == "(select country)":
            self.ui.country_combo.setCurrentIndex(0)
        elif countryname == "Multiple":
            self.ui.country_combo.setCurrentIndex(len(countrynames)+2)
        else:
            self.ui.country_combo.setCurrentIndex(list(self.cities_dict.keys()).index(countryname)+1)

        # City combo box
        self.update_city_combo()
        cityname = self.simulation.get_project_parameter("city")
        citynames = list(self.cities_dict[countryname].keys())
        citynames.sort()
        if cityname == "(select city)" or countryname == "(select country)":
            self.ui.location_combo.setCurrentIndex(0)
        elif cityname == "Multiple":
            self.ui.location_combo.setCurrentIndex(len(citynames)+2)
        else:
            self.ui.location_combo.setCurrentIndex(citynames.index(cityname)+1)

        self.update_coord_combo()
        self.ui.epsg_line.setText(str(self.simulation.get_project_parameter("project_epsg")))
        self.update_combo_from_epsg()

        # Enable Pop-up completion for the coordinate system combo box. Note that the combo box has to be editable!
        self.ui.coords_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # --- SIGNALS AND SLOTS ---
        self.ui.projpath_button.clicked.connect(self.browse_project_path)
        self.accepted.connect(self.run_setup_project)

        # - SIGNALS AND SLOTS FOR COORDINATE SYSTEMS
        self.timer_linedit = QtCore.QTimer()
        self.timer_linedit.setSingleShot(True)
        self.timer_linedit.setInterval(300)
        self.timer_linedit.timeout.connect(self.update_combo_from_epsg)
        self.ui.epsg_line.textEdited.connect(lambda: self.timer_linedit.start())
        self.ui.coords_combo.currentIndexChanged.connect(self.update_epsg_from_combo)
        self.ui.country_combo.currentIndexChanged.connect(self.update_city_combo)

    def update_city_combo(self):
        """Updates the closest city combo box based on the current value of country in the country combo box."""
        self.ui.location_combo.clear()
        self.ui.location_combo.addItem("(select city)")
        countryname = self.ui.country_combo.currentText()
        if countryname == "(select country)":
            self.ui.location_combo.setCurrentIndex(0)
            return
        citynames = list(self.cities_dict[countryname].keys())
        citynames.sort()
        for i in citynames:
            self.ui.location_combo.addItem(i)
        self.ui.location_combo.addItem("Multiple")
        self.ui.location_combo.setCurrentIndex(0)

    def update_country_combo(self):
        """Fills in the list of countries into the combo box."""
        self.ui.country_combo.clear()
        self.ui.country_combo.addItem("(select country)")
        names = list(self.cities_dict.keys())
        for i in names:
            self.ui.country_combo.addItem(i)
        self.ui.country_combo.addItem("Multiple")
        self.ui.country_combo.setCurrentIndex(0)

    def update_coord_combo(self):
        """Updates the coordinate system's combobox and the UI elements associated with it."""
        self.ui.coords_combo.clear()
        self.ui.coords_combo.addItem("(select coordinate system)")
        names = list(self.epsg_dict.keys())
        names.sort()
        for i in names:
            self.ui.coords_combo.addItem(i)
        self.ui.coords_combo.addItem("Other...")
        self.ui.coords_combo.setCurrentIndex(0)

    def update_combo_from_epsg(self):
        """Updates the coordinate system combo box based on the EPSG code entered in the text box, if the EPSG
        does not exist in the dictionary, the combo box displays "Other...". """
        names = list(self.epsg_dict.keys())
        names.sort()
        try:
            for name, epsg in self.epsg_dict.items():
                if int(epsg) == int(self.ui.epsg_line.text()):
                    curindex = names.index(name) + 1  # +1 to account for Index 0 < > text
                    self.ui.coords_combo.setCurrentIndex(curindex)
                    return True
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'
        except ValueError:
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'

    def update_epsg_from_combo(self):
        """Updates the EPSG text box based on the selected coordinate system in the combo box. If < >, index 0
        or "Other ..." are selected, the EPSG box remains blank."""
        try:
            self.ui.epsg_line.setText(self.epsg_dict[self.ui.coords_combo.currentText()])
        except KeyError:
            pass

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
        self.ui.coords_widget.setEnabled(0)

    def disable_all_parameters(self):
        """Disables the whole interface as it was opened just for viewing the information."""
        self.ui.aboutproject_widget1.setEnabled(0)
        self.ui.aboutproject_widget2.setEnabled(0)
        self.ui.aboutuser_widget.setEnabled(0)
        self.ui.synopsis_box.setEnabled(0)
        self.ui.projectlog_widget.setEnabled(0)
        self.ui.path_widget.setEnabled(0)
        self.ui.coords_widget.setEnabled(0)

    def run_setup_project(self):
        """Determines based on how the GUI was opened what needs to occur. If self.__viewer == 0 then
        new project signal is emitted with the dictionary of details. If self.__viewer == 1 then an update
        of project parameters is passed back to the main runtime. If self.__viewer == 2, then nothing
        happens and the dialog window just closes."""
        if self.__viewer == 0:
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
            condition_met = True

            # CONDITIONS FOR A VALID PROJECT PATH - conditions_met[0]
            if os.path.isdir(self.ui.projpath_line.text()):
                pass
            else:
                prompt_msg = "Please select a valid project path!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Path', prompt_msg, QtWidgets.QMessageBox.Ok)
                condition_met = False

            if condition_met:
                self.save_values()
                QtWidgets.QDialog.done(self, r)
        else:
            QtWidgets.QDialog.done(self, r)     # Call the parent's method instead of the override.

    def save_values(self):
        """Saves all project parameters values and returns a dictionary for use to setup simulation."""
        self.simulation.set_project_parameter("name", self.ui.projname_line.text())
        self.simulation.set_project_parameter("date", self.ui.date_spin.date().toPyDate())
        self.simulation.set_project_parameter("region", self.ui.region_line.text())
        self.simulation.set_project_parameter("country", self.ui.country_combo.currentText())
        self.simulation.set_project_parameter("city", self.ui.location_combo.currentText())
        self.simulation.set_project_parameter("modeller", self.ui.modellername_box.text())
        self.simulation.set_project_parameter("affiliation", self.ui.affiliation_box.text())
        self.simulation.set_project_parameter("otherpersons", self.ui.otherpersons_box.toPlainText())
        self.simulation.set_project_parameter("projectpath", self.ui.projpath_line.text())
        self.simulation.set_project_parameter("keepcopy", int(self.ui.keepcopy_check.isChecked()))
        self.simulation.set_project_parameter("synopsis", self.ui.synopsis_box.toPlainText())
        self.simulation.set_project_parameter("project_coord_sys", self.ui.coords_combo.currentText())
        self.simulation.set_project_parameter("project_epsg", int(self.ui.epsg_line.text()))
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
        self.epsg_dict = main.epsg_dict
        self.cities_dict = main.cities_dict

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

        # Country combo box
        self.update_country_combo()
        countryname = self.options["country"]
        countrynames = list(self.cities_dict.keys())
        if countryname == "(select country)":
            self.ui.country_combo.setCurrentIndex(0)
        elif countryname == "Multiple":
            self.ui.country_combo.setCurrentIndex(len(countrynames) + 2)
        else:
            self.ui.country_combo.setCurrentIndex(list(self.cities_dict.keys()).index(countryname) + 1)

        # City combo box
        self.update_city_combo()
        cityname = self.options["city"]
        citynames = list(self.cities_dict[countryname].keys())
        citynames.sort()
        if cityname == "(select city)" or countryname == "(select country)":
            self.ui.location_combo.setCurrentIndex(0)
        elif cityname == "Multiple":
            self.ui.location_combo.setCurrentIndex(len(citynames) + 2)
        else:
            self.ui.location_combo.setCurrentIndex(citynames.index(cityname) + 1)

        self.ui.projpath_line.setText(str(self.options["defaultpath"]))
        self.ui.temppath_line.setText(str(self.options["tempdir"]))
        self.ui.temppath_check.setChecked(bool(self.options["tempdefault"]))
        self.ui_temppath_line_enabledisable()

        self.ui.simboundary_featcount_spin.setValue(int(self.options["featcountwarning"]))

        # Text Appearance

        # SIMULATION TAB
        self.ui.numiter_spin.setValue(int(self.options["maxiterations"]))
        self.ui.tolerance_spin.setValue(float(self.options["globaltolerance"]))

        self.ui.decision_combo.setCurrentIndex(ubglobals.DECISIONS.index(self.options["defaultdecision"]))

        # MAP SETTINGS TAB
        self.ui.mapstyle_combo.setCurrentIndex(ubglobals.MAPSTYLES.index(self.options["mapstyle"]))
        self.ui_setmapstyle_pixmap()

        self.ui.tileserver_line.setText(self.options["tileserverURL"])
        self.ui.offline_check.setChecked(bool(self.options["offline"]))

        # DEFAULT COORDINATE SYSTEM
        self.update_coord_combo()
        self.ui.epsg_line.setText(self.options["customepsg"])
        self.update_combo_from_epsg()
        self.ui.coords_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        self.timer_linedit = QtCore.QTimer()
        self.timer_linedit.setSingleShot(True)
        self.timer_linedit.setInterval(300)
        self.timer_linedit.timeout.connect(self.update_combo_from_epsg)

        self.ui.epsg_line.textEdited.connect(lambda: self.timer_linedit.start())
        self.ui.coords_combo.currentIndexChanged.connect(self.update_epsg_from_combo)

        # EXTERNAL TAB
        self.ui.epanetpath_line.setText(self.options["epanetpath"])
        self.ui.swmmpath_line.setText(self.options["swmmpath"])
        self.ui.musicpath_line.setText(self.options["musicpath"])

        # ONLINE TAB
        # Coming Soon.

        # --- SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.reset_button.clicked.connect(self.reset_values)
        self.ui.country_combo.currentIndexChanged.connect(self.update_city_combo)
        self.ui.temppath_check.clicked.connect(self.ui_temppath_line_enabledisable)
        self.ui.projpath_button.clicked.connect(lambda: self.get_path("P"))
        self.ui.temppath_button.clicked.connect(lambda: self.get_path("T"))
        self.ui.mapstyle_combo.currentIndexChanged.connect(self.ui_setmapstyle_pixmap)
        self.ui.epanetpath_button.clicked.connect(lambda: self.get_path("E"))
        self.ui.swmmpath_button.clicked.connect(lambda: self.get_path("S"))
        self.ui.musicpath_button.clicked.connect(lambda: self.get_path("M"))

    def update_city_combo(self):
        """Updates the closest city combo box based on the current value of country in the country combo box."""
        self.ui.location_combo.clear()
        self.ui.location_combo.addItem("(select city)")
        countryname = self.ui.country_combo.currentText()
        if countryname == "(select country)":
            self.ui.location_combo.setCurrentIndex(0)
            return
        citynames = list(self.cities_dict[countryname].keys())
        citynames.sort()
        for i in citynames:
            self.ui.location_combo.addItem(i)
        self.ui.location_combo.addItem("Multiple")
        self.ui.location_combo.setCurrentIndex(0)

    def update_country_combo(self):
        """Fills in the list of countries into the combo box."""
        self.ui.country_combo.clear()
        self.ui.country_combo.addItem("(select country)")
        names = list(self.cities_dict.keys())
        for i in names:
            self.ui.country_combo.addItem(i)
        self.ui.country_combo.addItem("Multiple")
        self.ui.country_combo.setCurrentIndex(0)

    def update_coord_combo(self):
        """Updates the coordinate system's combobox and the UI elements associated with it."""
        self.ui.coords_combo.clear()
        self.ui.coords_combo.addItem("(select coordinate system)")
        names = list(self.epsg_dict.keys())
        names.sort()
        for i in names:
            self.ui.coords_combo.addItem(i)
        self.ui.coords_combo.addItem("Other...")
        self.ui.coords_combo.setCurrentIndex(0)

    def update_combo_from_epsg(self):
        """Updates the coordinate system combo box based on the EPSG code entered in the text box, if the EPSG
        does not exist in the dictionary, the combo box displays "Other...". """
        names = list(self.epsg_dict.keys())
        names.sort()
        try:
            for name, epsg in self.epsg_dict.items():
                if int(epsg) == int(self.ui.epsg_line.text()):
                    curindex = names.index(name) + 1    # +1 to account for Index 0 < > text
                    self.ui.coords_combo.setCurrentIndex(curindex)
                    return True
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'
        except ValueError:
            self.ui.coords_combo.setCurrentIndex(len(names)+1)   # Set to 'Other'

    def update_epsg_from_combo(self):
        """Updates the EPSG text box based on the selected coordinate system in the combo box. If < >, index 0
        or "Other ..." are selected, the EPSG box remains blank."""
        try:
            self.ui.epsg_line.setText(self.epsg_dict[self.ui.coords_combo.currentText()])
        except KeyError:
            pass

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
        mapstylepixmaps = ["mt_cartodbpositron.png","mt_cartodbdarkmatter.png","mt_esriworldimagery.png",
                           "mt_opentopomap.png","mt_stamentoner.png", "mt_stamenterrain.png", "mt_stamenwatercolor.png"]

        self.ui.mapstyle_pic.setPixmap(QtGui.QPixmap(":/media/map templates/gui/" +
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

        self.options["country"] = str(self.ui.country_combo.currentText())
        self.options["city"] = str(self.ui.location_combo.currentText())

        self.options["defaultpath"] = str(self.ui.projpath_line.text())
        self.options["tempdir"] = str(self.ui.temppath_line.text())
        self.options["tempdefault"] = int(self.ui.temppath_check.isChecked())

        self.options["featcountwarning"] = int(self.ui.simboundary_featcount_spin.value())

        # Text Appearance

        # SIMULATION TAB
        self.options["maxiterations"] = int(self.ui.numiter_spin.value())
        self.options["globaltolerance"] = float(self.ui.tolerance_spin.value())
        self.options["defaultdecision"] = str(ubglobals.DECISIONS[self.ui.decision_combo.currentIndex()])

        # MAP SETTINGS TAB
        self.options["mapstyle"] = str(ubglobals.MAPSTYLES[self.ui.mapstyle_combo.currentIndex()])
        self.options["tileserverURL"] = str(self.ui.tileserver_line.text())
        self.options["offline"] = int(self.ui.offline_check.isChecked())
        self.options["defaultcoordsys"] = str(self.ui.coords_combo.currentText())
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