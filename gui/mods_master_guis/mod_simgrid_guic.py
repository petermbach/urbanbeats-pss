r"""
@file   mod_simgrid_guic.py
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
from .mod_simgrid_gui import Ui_Create_SimGrid


# --- MAIN GUI FUNCTION ---
class CreateSimGridLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 1
    longname = "Create Simulation Grid"
    icon = ":/icons/Data-Grid-icon.png"

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
        self.ui = Ui_Create_SimGrid()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.mode = mode

        # --- PROGRESSBAR  OBSERVER ---
        # In the GUIc, we instantiate an observer instance of the types we want and write their corresponding GUI
        # response signals and slots.
        self.ui.progressbar.setValue(0)     # Set the bar to zero
        self.progressbarobserver = ProgressBarObserver()        # For single runtime only

        # Usage mode: with a scenario or not with a scenario (determines GUI settings and module connection)
        if self.mode == 1:
            self.active_scenario = simulation.get_active_scenario()
            self.module = None  # Initialize the variable to hold the active module object
            self.ui.gridname_line.setText(self.active_scenario.get_metadata("name"))
            self.ui.gridname_line.setEnabled(0)
            self.ui.ok_button.setEnabled(1)     # Disables the run, enables the OK
            self.ui.run_button.setEnabled(0)
            self.ui.progressbar.setEnabled(0)
        else:
            self.active_scenario = None
            self.module = self.simulation.get_module_instance(self.longname)
            self.ui.gridname_line.setEnabled(1)
            self.ui.ok_button.setEnabled(0)     # Enables the run, disables the OK
            self.ui.run_button.setEnabled(1)
            self.ui.progressbar.setEnabled(1)

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        # Boundary combo box
        self.ui.boundary_combo.clear()
        self.ui.boundary_combo.addItem("(select simulation boundary)")
        boundarynames = self.simulation.get_project_boundary_names()
        for n in boundarynames:
            self.ui.boundary_combo.addItem(str(n))
        if self.mode == 1:
            scenario_boundaryname = self.active_scenario.get_metadata("boundary")
            if scenario_boundaryname == "(select simulation boundary)":
                self.ui.boundary_combo.setCurrentIndex(0)
            else:
                self.ui.boundary_combo.setCurrentIndex(list(boundarynames).index(scenario_boundaryname)+1)
            self.ui.boundary_combo.setEnabled(0)
        else:
            self.ui.boundary_combo.setEnabled(1)

        # Patch delineation land use combo
        lumaps = self.get_dataref_array("spatial", "Land Use")  # Obtain the data ref array
        boundarymaps = self.get_dataref_array("spatial", "Boundaries")
        self.patchmaps = lumaps + boundarymaps
        [self.ui.patch_data_zoneombo.addItem(str(self.patchmaps[0][i])) for i in range(len(self.patchmaps[0]))]

        # --- SIGNALS AND SLOTS ---
        self.ui.blocksize_auto.clicked.connect(self.enable_disable_guis)
        self.ui.hexsize_auto.clicked.connect(self.enable_disable_guis)
        self.ui.patch_discretize_grid_check.clicked.connect(self.enable_disable_guis)
        self.ui.patch_discretize_grid_auto.clicked.connect(self.enable_disable_guis)
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.setup_gui_with_parameters()

    def enable_disable_guis(self):
        """Enables and disables items in the GUI based on conditions."""
        self.ui.blocksize_spin.setEnabled(not self.ui.blocksize_auto.isChecked())
        self.ui.hexsize_spin.setEnabled(not self.ui.hexsize_auto.isChecked())
        self.ui.patch_discretize_grid_spin.setEnabled(self.ui.patch_discretize_grid_check.isChecked())
        self.ui.patch_discretize_grid_auto.setEnabled(self.ui.patch_discretize_grid_check.isChecked())
        self.ui.patch_discretize_grid_spin.setEnabled(not self.ui.patch_discretize_grid_auto.isChecked())

    def setup_gui_with_parameters(self):
        """If using as a scenario module - sets up parameters based on the scenario."""
        spatial_ref = ["SQUARES", "HEXAGONS", "VECTORPATCH", "RASTER"]
        self.ui.geometry_combo.setCurrentIndex(spatial_ref.index(self.module.get_parameter("geometry_type")))

        # SQUARE BLOCKS
        self.ui.blocksize_spin.setValue(self.module.get_parameter("blocksize"))
        self.ui.blocksize_auto.setChecked(int(self.module.get_parameter("blocksize_auto")))

        # HEXAGONS BLOCKS
        self.ui.hexsize_spin.setValue(self.module.get_parameter("hexsize"))
        self.ui.hexsize_auto.setChecked(int(self.module.get_parameter("hexsize_auto")))
        if self.module.get_parameter("hex_orientation") == "NS":
            self.ui.radio_hexoNS.setChecked(1)
        else:
            self.ui.radio_hexoEW.setChecked(1)

        # PATCH REPRESENTATION
        try:    # LAND USE COMBO - retrieve the dataID from module
            self.ui.patch_data_zoneombo.setCurrentIndex(
                self.patchmaps[1].index(self.module.get_parameter("patchzonemap")))
            # if dataID is available, set the combo box
        except ValueError:
            self.ui.patch_data_zoneombo.setCurrentIndex(0) # else the map must've been removed, set combo to zero index

        self.ui.patch_discretize_grid_check.setChecked(int(self.module.get_parameter("disgrid_use")))
        self.ui.patch_discretize_grid_spin.setValue(self.module.get_parameter("disgrid_length"))
        self.ui.patch_discretize_grid_auto.setChecked(int(self.module.get_parameter("disgrid_auto")))

        # RASTER REPRESENTATION
        self.ui.raster_resolution_spin.setValue(self.module.get_parameter("rastersize"))
        self.ui.raster_nodata_line.setText(str(self.module.get_parameter("nodatavalue")))
        self.ui.raster_generatefishnet_check.setChecked(int(self.module.get_parameter("generate_fishnet")))

    def get_dataref_array(self, dataclass, datatype, *args):
        """Retrieves a list of data files loaded into the current scenario for display in the GUI

        :param dataclass: the data class i.e. spatial, temporal, qualitative
        :param datatype: the name that goes with the data class e.g. landuse, population, etc.
        """
        dataref_array = [["(no map selected)"], [""]]    # index 0:filenames, index 1:object_reference
        if self.mode == 1:
            data_lib = self.active_scenario.get_data_reference(dataclass)       # Limit to scenario's data
        else:
            data_lib = self.datalibrary.get_all_data_of_class(dataclass)        # Use entire library

        for dref in data_lib:
            if dref.get_metadata("parent") == datatype:
                if len(args) > 0 and datatype in ["Boundaries", "Water Bodies", "Built Infrastructure", "Overlays"]:
                    if dref.get_metadata("sub") != args[0]:
                        continue
                dataref_array[0].append(dref.get_metadata("filename"))
                dataref_array[1].append(dref.get_data_id())
        return dataref_array

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core. Only called in scenario mode."""
        # --- SPATIAL GEOMETRY ---
        if self.ui.geometry_combo.currentIndex() == 0:
            self.module.set_parameter("geometry_type", "SQUARES")
        elif self.ui.geometry_combo.currentIndex() == 1:
            self.module.set_parameter("geometry_type", "HEXAGONS")
        elif self.ui.geometry_combo.currentIndex() == 2:
            self.module.set_parameter("geometry_type", "VECTORPATCH")
        elif self.ui.geometry_combo.currentIndex() == 3:
            self.module.set_parameter("geometry_type", "RASTER")

        # SQUARE BLOCKS
        self.module.set_parameter("blocksize", self.ui.blocksize_spin.value())
        self.module.set_parameter("blocksize_auto", int(self.ui.blocksize_auto.isChecked()))

        # HEXAGONS BLOCKS
        self.module.set_parameter("hexsize", self.ui.hexsize_spin.value())
        self.module.set_parameter("hexsize_auto", int(self.ui.hexsize_auto.isChecked()))
        if self.ui.radio_hexoNS.isChecked():
            self.module.set_parameter("hex_orientation", "NS")
        else:
            self.module.set_parameter("hex_orientation", "EW")

        # PATCH REPRESENTATION
        self.module.set_parameter("patchzonemap", self.patchmaps[1][self.ui.patch_data_zoneombo.currentIndex()])
        self.module.set_parameter("disgrid_use", int(self.ui.patch_discretize_grid_check.isChecked()))
        self.module.set_parameter("disgrid", self.ui.patch_discretize_grid_spin.value())
        self.module.set_parameter("disgrid_auto", int(self.ui.patch_discretize_grid_auto.isChecked()))

        # RASTER REPRESENTATION
        self.module.set_parameter("rastersize", self.ui.raster_resolution_spin.value())
        self.module.set_parameter("nodatavalue", int(self.ui.raster_nodata_line.text()))
        self.module.set_parameter("generate_fishnet", int(self.ui.raster_generatefishnet_check.isChecked()))

    def update_progress_bar_value(self, value):
        """Updates the progress bar of the Main GUI when the simulation is started/stopped/reset."""
        self.ui.progressbar.setValue(int(value))
        if self.ui.progressbar.value() not in [0, 100]:
            self.ui.close_button.setEnabled(0)
        else:
            self.ui.close_button.setEnabled(1)

    def run_module_in_runtime(self):
        self.simulation.execute_runtime(self.module, self.progressbarobserver)