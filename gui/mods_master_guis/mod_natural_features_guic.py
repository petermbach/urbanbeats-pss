r"""
@file   mod_natural_features_guic.py
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

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_natural_features_gui import Ui_Map_NaturalFeatures

# --- MAIN GUI FUNCTION ---
class MapNaturalFeaturesLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 6
    longname = "Map Natural Features"
    icon = ":/icons/nature_lake.png"

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
        self.ui = Ui_Map_NaturalFeatures()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None

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

        # River Combo Box
        self.ui.riverdata_combo.clear()
        self.rivermaps = self.datalibrary.get_dataref_array("spatial", ["Natural Features"], subtypes="Rivers",
                                                            scenario=self.active_scenario_name)
        self.ui.riverdata_combo.addItem("(select river/waterways map)")
        if len(self.rivermaps[0]) == 0:
            pass
        else:
            [self.ui.riverdata_combo.addItem(str(self.rivermaps[0][i])) for i in range(len(self.rivermaps[0]))]

        self.ui.riverattr_combo.clear()
        self.ui.riverattr_combo.addItem("(select attribute for identifier)")

        # Lakes Combo Box
        self.ui.lakedata_combo.clear()
        self.lakemaps = self.datalibrary.get_dataref_array("spatial", ["Natural Features"], subtypes="Lakes",
                                                           scenario=self.active_scenario_name)
        self.ui.lakedata_combo.addItem("(select lake/water body map)")
        if len(self.lakemaps[0]) == 0:
            pass
        else:
            [self.ui.lakedata_combo.addItem(str(self.lakemaps[0][i])) for i in range(len(self.lakemaps[0]))]

        self.ui.lakeattr_combo.clear()
        self.ui.lakeattr_combo.addItem("(select attribute for identifier)")

        # --- SIGNALS AND SLOTS ---
        self.ui.riverdata_combo.currentIndexChanged.connect(self.update_river_attributes)
        self.ui.lakedata_combo.currentIndexChanged.connect(self.update_lake_attributes)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.setup_gui_with_parameters()
        self.enable_disable_guis()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def update_river_attributes(self):
        self.ui.riverattr_combo.clear()
        self.ui.riverattr_combo.addItem("(select attribute for identifier)")

        dataref = self.datalibrary.get_data_with_id(self.rivermaps[1][self.ui.riverdata_combo.currentIndex()-1])
        filepath = dataref.get_data_file_path() + self.ui.riverdata_combo.currentText()
        fileprops = ubspatial.load_shapefile_details(filepath)
        for i in fileprops[8]:
            self.ui.riverattr_combo.addItem(i)
        self.enable_disable_guis()

    def update_lake_attributes(self):
        self.ui.lakeattr_combo.clear()
        self.ui.lakeattr_combo.addItem("(select attribute for identifier)")

        dataref = self.datalibrary.get_data_with_id(self.lakemaps[1][self.ui.lakedata_combo.currentIndex()-1])
        filepath = dataref.get_data_file_path() + self.ui.lakedata_combo.currentText()
        fileprops = ubspatial.load_shapefile_details(filepath)
        for i in fileprops[8]:
            self.ui.lakeattr_combo.addItem(i)
        self.enable_disable_guis()

    def enable_disable_guis(self):
        if self.ui.riverdata_combo.currentIndex() == 0:
            self.ui.riverattr_combo.setEnabled(0)
            self.ui.riverattr_ignore_check.setEnabled(0)
        else:
            self.ui.riverattr_combo.setEnabled(1)
            self.ui.riverattr_ignore_check.setEnabled(1)
        if self.ui.lakedata_combo.currentIndex() == 0:
            self.ui.lakeattr_combo.setEnabled(0)
            self.ui.lakeattr_ignore_check.setEnabled(0)
        else:
            self.ui.lakeattr_combo.setEnabled(1)
            self.ui.lakeattr_ignore_check.setEnabled(1)

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # Combo boxes
        try:
            self.ui.riverdata_combo.setCurrentIndex(self.rivermaps[1].index(
                self.module.get_parameter("rivermapdataid"))+1)
        except:
            self.ui.riverdata_combo.setCurrentIndex(0)

        # Attribute Combos

        try:
            self.ui.lakedata_combo.setCurrentIndex(self.lakemaps[1].index(
                self.module.get_parameter("lakemapdataid"))+1)
        except:
            self.ui.lakedata_combo.setCurrentIndex(0)

        # Attribute Combos

        # Check boxes
        self.ui.riverattr_ignore_check.setChecked(self.module.get_parameter("riverignorenoname"))
        self.ui.lakeattr_ignore_check.setChecked(self.module.get_parameter("lakeignorenoname"))

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        # RIVERS
        if self.ui.riverdata_combo.currentIndex() == 0:
            self.module.set_parameter("rivermapdataid", "")
        else:
            self.module.set_parameter("rivermapdataid", self.rivermaps[1][self.ui.riverdata_combo.currentIndex()-1])

        self.module.set_parameter("rivermapattr", self.ui.riverattr_combo.currentText())
        self.module.set_parameter("riverignorenoname", int(self.ui.riverattr_ignore_check.isChecked()))

        # LAKES
        if self.ui.lakedata_combo.currentIndex() == 0:
            self.module.set_parameter("lakemapdataid", "")
        else:
            self.module.set_parameter("lakemapdataid", self.lakemaps[1][self.ui.lakedata_combo.currentIndex()-1])

        self.module.set_parameter("lakemapattr", self.ui.lakeattr_combo.currentText())
        self.module.set_parameter("lakeignorenoname", int(self.ui.lakeattr_ignore_check.isChecked()))

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

        # (2) If a river map is selected but attribute combo box is still index 0, need to select attribute
        if self.ui.riverdata_combo.currentIndex() > 0 and self.ui.riverattr_combo.currentIndex() == 0:
            prompt_msg = "Please select which attribute to use as an identifier for mapped river locations in the" \
                         "simulation grid."
            QtWidgets.QMessageBox.warning(self, "No river map attribute selected", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        # (3) If a lake map is selected but attribute combo box is still index 0, need to select attribute
        if self.ui.lakedata_combo.currentIndex() > 0 and self.ui.lakeattr_combo.currentIndex() == 0:
            prompt_msg = "Please select which attribute to use as an identifier for mapped lake locations in the" \
                         "simulation grid."
            QtWidgets.QMessageBox.warning(self, "No lake map attribute selected", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        return True
