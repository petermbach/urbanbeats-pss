r"""
@file   mod_landuse_import_gui.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2017-2022  Peter M. Bach

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
__copyright__ = "Copyright 2017-2022. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
import pickle

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ublibs.ubspatial as ubspatial
import model.mods_master.mod_landuse_import as mod_landuse_import

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_landuse_import_gui import Ui_Map_Landuse

# --- MAIN GUI FUNCTION ---
class MapLanduseLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 3
    longname = "Map Land Use"
    icon = ":/icons/region.png"

    def __init__(self, main, simulation, datalibrary, simlog, mode, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param mode: 0 = generic, 1 = scenario
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Map_Landuse()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None
        self.active_lufile = None

        # --- PROGRESSBAR OBSERVER ---
        # In the GUIc, we instantiate an observer instance of the types we want and write their corresponding GUI
        # response signals and slots.
        self.ui.progressbar.setValue(0)  # Set the bar to zero
        self.progressbarobserver = ProgressBarObserver()  # For single runtime only

        # Usage mode: with a scenario or not with a scenario (determines GUI settings)
        if mode == 1:
            self.active_scenario = simulation.get_active_scenario()
            self.active_scenario_name = self.active_scenario.get_metadata("name")
            self.module = None
            self.ui.ok_button.setEnabled(1)
            self.ui.run_button.setEnabled(0)
            self.ui.progressbar.setEnabled(0)
        else:
            self.active_scenario = None
            self.active_scenario_name = None
            self.module = self.simulation.get_module_instance(self.longname)
            self.ui.ok_button.setEnabled(0)
            self.ui.run_button.setEnabled(1)
            self.ui.progressbar.setEnabled(1)

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        self.ui.assetcol_combo.clear()
        self.ui.assetcol_combo.addItem("(select asset collection)")
        simgrids = self.simulation.get_global_asset_collection()
        for n in simgrids.keys():
            if mode != 1:   # If we are running standalone mode
                if simgrids[n].get_container_type() == "Standalone":
                    self.ui.assetcol_combo.addItem(str(n))
                self.ui.assetcol_combo.setEnabled(1)
            else:
                self.ui.assetcol_combo.addItem(
                    self.active_scenario.get_asset_collection_container().get_container_name())
                self.ui.assetcol_combo.setEnabled(0)
        self.update_asset_col_metadata()

        # Land use combo box
        self.ui.lu_combo.clear()
        self.lumaps = self.datalibrary.get_dataref_array("spatial", ["Land Use/Cover"], subtypes="Land Use",
                                                         scenario=self.active_scenario_name)
        if len(self.lumaps) == 0:
            self.ui.lu_combo.addItem(str("(no land use maps in project)"))
        else:
            self.ui.lu_combo.addItem("(select land use map)")
            [self.ui.lu_combo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        # --- SIGNALS AND SLOTS ---
        self.ui.lu_combo.currentIndexChanged.connect(self.update_land_use_attributes)
        self.ui.lureclass_check.clicked.connect(self.refresh_lu_reclassification_widgets)
        self.ui.lureclass_save_button.clicked.connect(self.save_current_reclassification)
        self.ui.lureclass_load_button.clicked.connect(self.load_reclassification)
        self.ui.lureclass_reset_button.clicked.connect(self.reset_reclassification)
        self.ui.single_landuse_check.clicked.connect(self.enable_disable_guis)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.ui.lureclass_table.setRowCount(0)
        self.setup_gui_with_parameters()
        self.enable_disable_guis()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def update_land_use_attributes(self):
        """Updates the land use classification attributes combo with info."""
        self.ui.luattr_combo.clear()
        if ".shp" in self.ui.lu_combo.currentText():
            print(self.lumaps)
            dataref = self.datalibrary.get_data_with_id(self.lumaps[1][self.ui.lu_combo.currentIndex()-1])
            self.active_lufile = dataref.get_data_file_path() + self.ui.lu_combo.currentText()
            fileprops = ubspatial.load_shapefile_details(self.active_lufile)
            self.ui.luattr_combo.addItem("(attribute name)")
            for i in fileprops[8]:
                self.ui.luattr_combo.addItem(i)
            self.ui.luattr_combo.setCurrentIndex(0)
            self.ui.luattr_combo.setEnabled(1)
            self.ui.rastermapping_mask_radio.setEnabled(0)
            self.ui.rastermapping_polygon_radio.setEnabled(0)
        else:
            self.active_lufile = None
            self.ui.luattr_combo.addItem("(not a shapefile)")
            self.ui.luattr_combo.setCurrentIndex(0)
            self.ui.luattr_combo.setEnabled(0)
            self.ui.lureclass_check.setChecked(0)
            self.ui.rastermapping_mask_radio.setEnabled(1)
            self.ui.rastermapping_polygon_radio.setEnabled(1)
            self.reset_reclassification()
            self.enable_disable_guis()

    def refresh_lu_reclassification_widgets(self):
        """Activates the reclassification widget, populates the left column, gives the right column options."""
        if ".shp" not in self.ui.lu_combo.currentText():
            prompt_msg = "Reclassification only possible on shapefiles. Select a shapefile and attribute to reclassify."
            QtWidgets.QMessageBox.warning(self, "Only .shp files", prompt_msg, QtWidgets.QMessageBox.Ok)
            self.ui.lureclass_check.setChecked(0)
            self.enable_disable_guis()

        if self.ui.luattr_combo.currentIndex() == 0:    # If there is a valid shapefile
            prompt_msg = "Reclassification requires reference to an attribute in the data file"
            QtWidgets.QMessageBox.warning(self, "No attribute to reclassify", prompt_msg, QtWidgets.QMessageBox.Ok)
            self.ui.lureclass_check.setChecked(0)
            self.enable_disable_guis()
            return True

        # Prevent the attributes combo from being modified during reclassification
        if self.ui.lureclass_check.isChecked():
            self.ui.luattr_combo.setEnabled(0)
        else:
            self.ui.luattr_combo.setEnabled(1)
        self.enable_disable_guis()

        # Update Table
        self.ui.lureclass_table.setRowCount(0)
        categories = ubspatial.get_uniques_from_shapefile_attribute(self.active_lufile,
                                                                    self.ui.luattr_combo.currentText())
        for cat in categories:
            self.ui.lureclass_table.insertRow(self.ui.lureclass_table.rowCount())
            twi = QtWidgets.QTableWidgetItem()
            twi.setText(str(cat))
            self.ui.lureclass_table.setItem(self.ui.lureclass_table.rowCount()-1, 0, twi)
            combo = QtWidgets.QComboBox()
            combo.addItem("(select class)")
            for lu in mod_landuse_import.UBLANDUSENAMES:
                combo.addItem(str(lu))
            self.ui.lureclass_table.setCellWidget(self.ui.lureclass_table.rowCount()-1, 1, combo)
        self.ui.lureclass_table.resizeColumnsToContents()

    def save_current_reclassification(self):
        """Saves the current state of the reclassification table to a .ublcl file."""
        dir = self.simulation.get_project_path()
        message = "Save Reclassification Scheme"
        filename, fmt = QtWidgets.QFileDialog.getSaveFileName(self, message, dir, "UB Reclass (*.ublcl)")
        if filename:
            reclass = self.generate_reclassification_dict()
            f = open(filename, 'wb')
            pickle.dump(reclass, f)
            f.close()
            prompt_msg = "Reclassification file saved successfully!"
            QtWidgets.QMessageBox.information(self, "Reclassification saved", prompt_msg, QtWidgets.QMessageBox.Ok)
        else:
            prompt_msg = "No valid filename specified, reclassification not saved!"
            QtWidgets.QMessageBox.warning(self, "Reclassification not saved", prompt_msg, QtWidgets.QMessageBox.Ok)

    def generate_reclassification_dict(self):
        """Generates a dictionary object of the reclassification scheme."""
        reclass = {}  # of dictionary key pairs
        for i in range(self.ui.lureclass_table.rowCount()):
            class_raw = self.ui.lureclass_table.item(i, 0).text()
            reclass[class_raw] = self.ui.lureclass_table.cellWidget(i, 1).currentText()
        return reclass

    def load_reclassification(self):
        """Loads a .ublcl file and attempts to apply the reclassification as best to the table."""
        dir = self.simulation.get_project_path()
        message = "Load existing Reclassification Scheme"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB Reclass (*.ublcl)")
        if filename:
            f = open(filename, 'rb')
            reclass = pickle.load(f)
            self.classify_table(reclass)
        return True

    def reset_reclassification(self):
        if self.ui.lureclass_check.isChecked():
            prompt_msg = "Do you wish to reset the current reclassification?"
            answer = QtWidgets.QMessageBox.question(self, "Reset Reclassification?", prompt_msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if answer == QtWidgets.QMessageBox.Yes:
                self.ui.lureclass_table.setRowCount(0)
                self.refresh_lu_reclassification_widgets()
        return True

    def classify_table(self, reclass):
        """Fills in data from the reclass dictionary into the classification table based on current info."""
        for i in range(self.ui.lureclass_table.rowCount()):
            try:
                ubclass = reclass[self.ui.lureclass_table.item(i, 0).text()]
                if ubclass == "(select class)":
                    ubclassindex = 0
                else:
                    ubclassindex = mod_landuse_import.UBLANDUSENAMES.index(ubclass) + 1
                self.ui.lureclass_table.cellWidget(i, 1).setCurrentIndex(ubclassindex)
            except KeyError:
                self.ui.lureclass_table.cellWidget(i, 1).setCurrentIndex(0)
        return True

    def enable_disable_guis(self):
        self.ui.lureclass_table.setEnabled(self.ui.lureclass_check.isChecked())
        self.ui.lureclass_widget.setEnabled(self.ui.lureclass_check.isChecked())
        self.ui.spatialmetrics_check.setEnabled(not self.ui.single_landuse_check.isChecked())

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # Combo Boxes
        try:
            self.ui.lu_combo.setCurrentIndex(
                self.lumaps[1].index(self.module.get_parameter("landusemapid")))
        except:
            self.ui.lu_combo.setCurrentIndex(0)

        self.ui.luattr_combo.setCurrentIndex(0)
        if self.ui.lu_combo.currentIndex() != 0:
            attname = self.module.get_parameter("landuseattr")
            for i in range(self.ui.luattr_combo.count()):
                if self.ui.luattr_combo.itemText(i) == attname:
                    self.ui.luattr_combo.setCurrentIndex(i)
        else:
            self.ui.lureclass_table.setRowCount(0)

        if self.module.get_parameter("rastermaptech") == "MASK":
            self.ui.rastermapping_mask_radio.setChecked(1)
        else:
            self.ui.rastermapping_polygon_radio.setChecked(1)

        # Reclassification Table
        self.ui.lureclass_check.setChecked(self.module.get_parameter("lureclass"))
        if self.ui.lureclass_check.isChecked() and self.ui.luattr_combo.currentIndex() != 0:
            # Populate Table with reclassification system...
            self.refresh_lu_reclassification_widgets()
            reclass = self.module.get_parameter("lureclasssystem")
            self.classify_table(reclass)

        self.ui.single_landuse_check.setChecked(self.module.get_parameter("singlelu"))
        self.ui.spatialmetrics_check.setChecked(self.module.get_parameter("spatialmetrics"))

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())
        self.module.set_parameter("landusemapid", self.lumaps[1][self.ui.lu_combo.currentIndex()-1])
        self.module.set_parameter("landuseattr", self.ui.luattr_combo.currentText())

        self.module.set_parameter("lureclass", int(self.ui.lureclass_check.isChecked()))

        if self.ui.rastermapping_mask_radio.isChecked():
            self.module.set_parameter("rastermaptech", "MASK")
        else:
            self.module.set_parameter("rastermaptech", "POLY")

        # Reclassification scheme
        if self.ui.lureclass_check.isChecked():
            self.module.set_parameter("lureclasssystem", self.generate_reclassification_dict())
        else:
            self.module.set_parameter("lureclasssystem", {})

        self.module.set_parameter("singlelu", int(self.ui.single_landuse_check.isChecked()))
        self.module.set_parameter("spatialmetrics", int(self.ui.spatialmetrics_check.isChecked()))

    def update_progress_bar_value(self, value):
        """Updates the progress bar of the Main GUI when the simulation is started/stopped/reset. Also disables the
        close button if in 'ad-hoc' mode."""
        self.ui.progressbar.setValue(int(value))
        if self.ui.progressbar.value() not in [0, 100]:
            self.ui.close_button.setEnabled(0)
        else:
            self.ui.close_button.setEnabled(1)

    def run_module_in_runtime(self):
        self.save_values()
        if self.checks_before_runtime():
            self.simulation.execute_runtime(self.module, self.progressbarobserver)

    def checks_before_runtime(self):
        """Enter all GUI checks to do before the module is run."""
        # (1) Is an asset collection selected?
        if self.ui.assetcol_combo.currentIndex() == 0:
            prompt_msg = "Please select an Asset Collection to use for this simulation!"
            QtWidgets.QMessageBox.warning(self, "No Asset Collection selected", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        # (2) Check that a land use map has been selected
        if self.ui.lu_combo.currentIndex() == 0:
            prompt_msg = "Please select a valid land use map to use in the simulation."
            QtWidgets.QMessageBox.warning(self, "No Land Use Map selected", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        # (3) Check reclassification boxes
        if self.ui.lureclass_check.isChecked() and self.module.get_parameter("lureclasssystem") == {}:
            prompt_msg = "No reclassification system defined, please define a reclassification or load a " \
                         "pre-classified land use map into the simulation."
            QtWidgets.QMessageBox.warning(self, "No reclassification system defined", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False
        return True
