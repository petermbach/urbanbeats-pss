r"""
@file   mod_catchmentdelin_guic.py
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
from .mod_catchmentdelin_gui import Ui_CatchmentDelinGui

# --- MAIN GUI FUNCTION ---
class CatchmentDelineationLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Hydrology"
    catorder = 2
    longname = "Flow Paths & Sub-catchments"
    icon = ":/icons/river_flow.png"

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
        self.ui = Ui_CatchmentDelinGui()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None
        self.geomtype = None    # The active asset collection's geometry type

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
        # Asset Collection
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

        # Built Infrastructure Combo Box
        self.ui.storm_combo.clear()
        self.stormmaps = self.datalibrary.get_dataref_array("spatial", ["Built Environment"],
                                                            subtypes="Water Infrastructure",
                                                            scenario=self.active_scenario_name)
        if len(self.stormmaps[0]) == 0:
            self.ui.storm_combo.addItem(str("(no infrastructure maps in project"))
        else:
            self.ui.storm_combo.addItem(str("(select infrastructure map)"))
            [self.ui.storm_combo.addItem(str(self.stormmaps[0][i])) for i in range(len(self.stormmaps[0]))]

        # --- SIGNALS AND SLOTS ---
        self.ui.assetcol_combo.currentIndexChanged.connect(self.update_method_combo)
        self.ui.infrastructure_check.clicked.connect(self.enable_disable_guis)
        self.ui.natfeature_check.clicked.connect(self.enable_disable_guis)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.setup_gui_with_parameters()
        self.enable_disable_guis()

    def update_method_combo(self):
        if self.ui.assetcol_combo.currentIndex() == 0:      # If there is no active asset collection...
            self.geomtype = None
            self.update_asset_col_metadata()
            self.ui.flowpath_combo.setCurrentIndex(0)
            return True
        else:
            self.update_asset_col_metadata()
            if self.metadata is None:
                self.ui.flowpath_combo.setCurrentIndex(0)
            else:
                self.geomtype = self.metadata.get_attribute("AssetIdent")
                if self.geomtype in ["BlockID", "HexID", "GeohashID"]:
                    self.ui.flowpath_combo.setCurrentIndex(1)
                elif self.geomtype in ["PatchID", "ParcelID"]:
                    self.ui.flowpath_combo.setCurrentIndex(2)
                else:
                    self.ui.flowpath_combo.setCurrentIndex(3)
            return True

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def enable_disable_guis(self):
        self.ui.storm_combo.setEnabled(self.ui.infrastructure_check.isChecked())
        self.ui.ignore_lakes_check.setEnabled(self.ui.natfeature_check.isChecked())
        self.ui.ignore_lakes_check.setEnabled(self.ui.natfeature_check.isChecked())

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # Check boxes
        self.ui.natfeature_check.setChecked(int(self.module.get_parameter("guide_natural")))
        self.ui.infrastructure_check.setChecked(int(self.module.get_parameter("guide_built")))

        # Built-infrastructure combo box
        try:
            self.ui.storm_combo.setCurrentIndex(self.stormmaps[1].index(self.module.get_parameter("built_map")))
        except:
            self.ui.storm_combo.setCurrentIndex(0)

        self.ui.ignore_rivers_check.setChecked(int(self.module.get_parameter("ignore_rivers")))
        self.ui.ignore_lakes_check.setChecked(int(self.module.get_parameter("ignore_lakes")))

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("guide_natural", int(self.ui.natfeature_check.isChecked()))
        self.module.set_parameter("guide_built", int(self.ui.infrastructure_check.isChecked()))
        self.module.set_parameter("built_map", self.stormmaps[1][self.ui.storm_combo.currentIndex() - 1])
        self.module.set_parameter("ignore_rivers", int(self.ui.ignore_rivers_check.isChecked()))
        self.module.set_parameter("ignore_lakes", int(self.ui.ignore_lakes_check.isChecked()))

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

        # (2) If a drainage network is to be used as guidance, has one been selected or not?
        if self.ui.infrastructure_check.isChecked() and self.ui.storm_combo.currentIndex() == 0:
            prompt_msg = "You opted to use a drainage layer to aid delineation, but none has been selected! Please" \
                         "select a valid drainage map!"
            QtWidgets.QMessageBox.warning(self, "No Drainage layer selected", prompt_msg, QtWidgets.QMessageBox.Ok)
        return True
