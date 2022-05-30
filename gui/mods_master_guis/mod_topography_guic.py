r"""
@file   mod_topography_guic.py
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

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_topography import Ui_Map_Topography


# --- MAIN GUI FUNCTION ---
class MapTopographyLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 5
    longname = "Map Topography"
    icon = ":/icons/topography.png"

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
        self.ui = Ui_Map_Topography()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None

        # --- PROGRESSBAR  OBSERVER ---
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
        # Boundary combo box
        self.ui.assetcol_combo.clear()
        self.ui.assetcol_combo.addItem("(select simulation grid)")
        simgrids = self.simulation.get_global_asset_collection()
        for n in simgrids.keys():
            if mode != 1:       # If we are running standalone mode
                if simgrids[n].get_container_type() == "Standalone":
                    self.ui.assetcol_combo.addItem(str(n))
                self.ui.assetcol_combo.setEnabled(1)
            else:
                self.ui.assetcol_combo.addItem(
                    self.active_scenario.get_asset_collection_container().get_container_name())
                self.ui.assetcol_combo.setEnabled(0)
        self.update_asset_col_metadata()

        # Elevation Combo Box
        self.ui.elev_combo.clear()
        self.elevmaps = self.datalibrary.get_dataref_array("spatial", ["Topography"],
                                                           subtypes=None, scenario=self.active_scenario_name)
        if len(self.elevmaps) == 0:
            self.ui.elev_combo.addItem(str("(no elevation maps in project)"))
        else:
            [self.ui.elev_combo.addItem(str(self.elevmaps[0][i])) for i in range(len(self.elevmaps[0]))]

        # --- SIGNALS AND SLOTS ---
        self.ui.assetcol_combo.currentIndexChanged.connect(self.update_asset_col_metadata)
        self.ui.demsmooth_check.clicked.connect(self.enable_disable_guis)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.enable_disable_guis()
        self.setup_gui_with_parameters()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def enable_disable_guis(self):
        """Enables and disables items in the GUI based on conditions."""
        self.ui.demsmooth_spin.setEnabled(self.ui.demsmooth_check.isChecked())

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        self.ui.demsmooth_check.setChecked(int(self.module.get_parameter("demsmooth")))
        self.ui.demsmooth_spin.setValue(int(self.module.get_parameter("dempasses")))

        self.ui.topo_stats_check.setChecked(int(self.module.get_parameter("demstats")))
        self.ui.topo_lowest_check.setChecked(int(self.module.get_parameter("demminmax")))
        self.ui.slope_check.setChecked(int(self.module.get_parameter("slope")))
        self.ui.aspect_check.setChecked(int(self.module.get_parameter("aspect")))

    def get_dataref_array(self, dataclass, datatype, *args):
        """Retrieves a list of data files loaded into the current scenario for display in the GUI

        :param dataclass: the data class i.e. spatial, temporal, qualitative
        :param datatype: the name that goes with the data class e.g. landuse, population, etc.
        """
        dataref_array = [["(no map selected)"], [""]]    # index 0:filenames, index 1:object_reference
        for dref in self.active_scenario.get_data_reference(dataclass):
            if dref.get_metadata("parent") == datatype:
                if len(args) > 0 and datatype in ["Boundaries", "Water Bodies", "Built Infrastructure", "Overlays"]:
                    if dref.get_metadata("sub") != args[0]:
                        continue
                dataref_array[0].append(dref.get_metadata("filename"))
                dataref_array[1].append(dref.get_data_id())
        return dataref_array

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())
        self.module.set_parameter("elevmapname", self.ui.elev_combo.currentText())
        self.module.set_parameter("demsmooth", int(self.ui.demsmooth_check.isChecked()))
        self.module.set_parameter("dempasses", float(self.ui.demsmooth_spin.value()))
        self.module.set_parameter("demstats", int(self.ui.topo_stats_check.isChecked()))
        self.module.set_parameter("demminmax", int(self.ui.topo_lowest_check.isChecked()))
        self.module.set_parameter("slope", int(self.ui.slope_check.isChecked()))
        self.module.set_parameter("aspect", int(self.ui.aspect_check.isChecked()))

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

        # (2) Elevation map not selected
        if self.ui.elev_combo.currentText() == "(no elevation maps in project)":
            prompt_msg = "Please load an elevation map into the project to be mapped!"
            QtWidgets.QMessageBox.warning(self, "Missing Elevation Map", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        return True
