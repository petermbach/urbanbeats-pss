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
    catcode = 1
    longname = "Create Simulation Grid"
    icon = ":/icons/Data-Grid-icon.png"
    prerequisites = []

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
        if self.mode == 1:      # Scenario Mode
            self.active_scenario = simulation.get_active_scenario()
            self.active_scenario_name = self.active_scenario.get_metadata("name")
            self.module = None  # Initialize the variable to hold the active module object
            self.ui.ok_button.setEnabled(1)     # Disables the run, enables the OK
            self.ui.run_button.setEnabled(0)
            self.ui.progressbar.setEnabled(0)
            self.ui.asset_col_line.setEnabled(0)        # Asset collection
            self.ui.asset_col_line.setText(self.active_scenario.get_metadata("name"))   # Set scenario's name
            self.ui.asset_col_new_radio.setEnabled(0)   # Do not use radio buttons
            self.ui.asset_col_existing_radio.setEnabled(0)
            self.ui.asset_col_existing_radio.setChecked(1)      # Using existing asset collection from scenario
        else:                    # Standalone Mode
            self.active_scenario = None
            self.active_scenario_name = None
            self.module = self.simulation.get_module_instance(self.longname)
            self.ui.asset_col_line.setEnabled(1)
            self.ui.ok_button.setEnabled(0)     # Enables the run, disables the OK
            self.ui.run_button.setEnabled(1)
            self.ui.progressbar.setEnabled(1)
            self.ui.asset_col_new_radio.setEnabled(1)   # Asset collection
            self.ui.asset_col_new_radio.setChecked(1)   # By default, offer a new asset collection
            self.ui.asset_col_line.setEnabled(1)        # enable the line for the name
            self.ui.asset_col_existing_radio.setEnabled(1)      # Enable radio buttons

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        # Boundary combo box
        self.ui.boundary_combo.clear()
        self.ui.boundary_combo.addItem("(select simulation boundary)")
        boundarynames = self.simulation.get_project_boundary_names()
        for n in boundarynames:
            self.ui.boundary_combo.addItem(str(n))
        if self.mode == 1:      # SCENARIO MODE
            scenario_boundaryname = self.active_scenario.get_metadata("boundary")
            if scenario_boundaryname == "(select simulation boundary)":
                self.ui.boundary_combo.setCurrentIndex(0)
            else:
                self.ui.boundary_combo.setCurrentIndex(list(boundarynames).index(scenario_boundaryname)+1)
            self.ui.boundary_combo.setEnabled(0)
        else:       # STANDALONE MODE
            self.ui.boundary_combo.setEnabled(1)

        # Asset collection combo box
        if self.mode == 1:      # SCENARIO MODE
            self.ui.asset_col_combo.clear()
            self.ui.asset_col_combo.addItem(self.active_scenario.get_asset_collection_container().get_container_name())
            self.ui.asset_col_combo.setEnabled(0)
        else:
            self.ui.asset_col_combo.clear()
            self.ui.asset_col_combo.addItem("(select asset collection)")
            gac = self.simulation.get_global_asset_collection()
            for a in gac.keys():
                if gac[a].get_container_type() in ["Scenario", "Other"]:
                    pass    # Do not include scenario or "Other" collections
                else:
                    self.ui.asset_col_combo.addItem(gac[a].get_container_name())

        # Patch delineation land use combo
        self.ui.patch_data_zoneombo.clear()
        self.ui.patch_data_zoneombo.addItem("(select map for patch-delineation)")   # Add the default option
        self.combomaps = self.datalibrary.get_dataref_array("spatial", ["Boundaries", "Land Use", "Land Cover"],
                                                            subtypes=None, scenario=self.active_scenario_name)
        [self.ui.patch_data_zoneombo.addItem(str(self.combomaps[0][i])) for i in range(len(self.combomaps[0]))]

        self.ui.discret_combo.clear()
        self.ui.discret_combo.addItem("(select boundaries to guide discretization)")
        self.discretmaps = self.datalibrary.get_dataref_array("spatial", ["Boundaries"], subtypes=None,
                                                              scenario=self.active_scenario_name)
        [self.ui.discret_combo.addItem(str(self.discretmaps[0][i])) for i in range(len(self.discretmaps[0]))]

        self.ui.parcel_combo.clear()
        self.ui.parcel_combo.addItem("(select map for parcel delineation)")
        self.parcelmaps = self.datalibrary.get_dataref_array("spatial", ["Miscellaneous"])
        [self.ui.parcel_combo.addItem(str(self.parcelmaps[0][i])) for i in range(len(self.parcelmaps[0]))]

        # --- SIGNALS AND SLOTS ---
        self.ui.asset_col_new_radio.clicked.connect(self.enable_disable_guis)
        self.ui.asset_col_existing_radio.clicked.connect(self.enable_disable_guis)
        self.ui.blocksize_auto.clicked.connect(self.enable_disable_guis)
        self.ui.hexsize_auto.clicked.connect(self.enable_disable_guis)
        self.ui.patch_discretize_grid_radio.clicked.connect(self.enable_disable_guis)
        self.ui.patch_discretize_boundary_radio.clicked.connect(self.enable_disable_guis)
        self.ui.patch_discretize_none_radio.clicked.connect(self.enable_disable_guis)
        self.ui.patch_discretize_grid_auto.clicked.connect(self.enable_disable_guis)
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.enable_disable_guis()
        self.setup_gui_with_parameters()

    def enable_disable_guis(self):
        """Enables and disables items in the GUI based on conditions."""
        if self.ui.asset_col_new_radio.isChecked():
            self.ui.asset_col_line.setEnabled(1)
            self.ui.asset_col_combo.setEnabled(0)
        else:
            self.ui.asset_col_line.setEnabled(0)
            self.ui.asset_col_combo.setEnabled(1)
        self.ui.blocksize_spin.setEnabled(not self.ui.blocksize_auto.isChecked())
        self.ui.hexsize_spin.setEnabled(not self.ui.hexsize_auto.isChecked())
        self.ui.patch_discretize_grid_spin.setEnabled(self.ui.patch_discretize_grid_radio.isChecked())
        self.ui.patch_discretize_grid_auto.setEnabled(self.ui.patch_discretize_grid_radio.isChecked())
        self.ui.patch_discretize_grid_spin.setEnabled(not self.ui.patch_discretize_grid_auto.isChecked())
        self.ui.discret_combo.setEnabled(self.ui.patch_discretize_boundary_radio.isChecked())
        if self.ui.patch_discretize_none_radio.isChecked():
            self.ui.patch_discretize_grid_spin.setEnabled(0)
            self.ui.patch_discretize_grid_auto.setEnabled(0)
            self.ui.patch_discretize_grid_spin.setEnabled(0)
            self.ui.discret_combo.setEnabled(0)

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
                self.combomaps[1].index(self.module.get_parameter("patchzonemap"))+1)
            # if dataID is available, set the combo box
        except ValueError:
            self.ui.patch_data_zoneombo.setCurrentIndex(0) # else the map must've been removed, set combo to zero index

        if self.module.get_parameter("disgrid_type") == "GRID":
            self.ui.patch_discretize_grid_radio.setChecked(1)
        elif self.module.get_parameter("disgrid_type") == "BOUND":
            self.ui.patch_discretize_boundary_radio.setChecked(1)
        else:
            self.ui.patch_discretize_none_radio.setChecked(1)

        self.ui.patch_discretize_grid_spin.setValue(self.module.get_parameter("disgrid_length"))
        self.ui.patch_discretize_grid_auto.setChecked(int(self.module.get_parameter("disgrid_auto")))

        try:    # PATCH DISCRETIZATION BOUNDARY MAP COMBO
            self.ui.discret_combo.setCurrentIndex(
                self.discretmaps[1].index(self.module.get_parameter("disgrid_map"))+1)
        except ValueError:
            self.ui.discret_combo.setCurrentIndex(0)

        # RASTER REPRESENTATION
        self.ui.raster_resolution_spin.setValue(self.module.get_parameter("rastersize"))
        self.ui.raster_nodata_line.setText(str(self.module.get_parameter("nodatavalue")))
        self.ui.raster_generatefishnet_check.setChecked(int(self.module.get_parameter("generate_fishnet")))

        # GEOHASH GRID REPRESENTATION
        self.ui.gh_res_spin.setValue(int(self.module.get_parameter("geohash_lvl")))

        # PARCEL MAP
        try:
            self.ui.parcel_combo.setCurrentIndex(
                self.parcelmaps[1].index(self.module.get_parameter("parcel_map"))+1)
        except ValueError:
            self.ui.parcel_combo.setCurrentIndex(0)

    # ---- MARKED FOR DELETION
    # def get_dataref_array(self, dataclass, datatype, *args):
    #     """Retrieves a list of data files loaded into the current scenario for display in the GUI
    #
    #     :param dataclass: the data class i.e. spatial, temporal, qualitative
    #     :param datatype: the name that goes with the data class e.g. landuse, population, etc.
    #     """
    #     dataref_array = [["(no map selected)"], [""]]    # index 0:filenames, index 1:object_reference
    #     if self.mode == 1:
    #         data_lib = self.active_scenario.get_data_reference(dataclass)       # Limit to scenario's data
    #     else:
    #         data_lib = self.datalibrary.get_all_data_of_class(dataclass)        # Use entire library
    #
    #     for dref in data_lib:
    #         if dref.get_metadata("parent") == datatype:
    #             if len(args) > 0 and datatype in ["Boundaries", "Water Bodies", "Built Infrastructure", "Overlays"]:
    #                 if dref.get_metadata("sub") != args[0]:
    #                     continue
    #             dataref_array[0].append(dref.get_metadata("filename"))
    #             dataref_array[1].append(dref.get_data_id())
    #     return dataref_array
    # ---- MARKED FOR DELETION

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core. Only called in scenario mode."""
        # --- ASSET COLLECTION AND BOUNDARY ---
        if self.ui.asset_col_new_radio.isChecked():
            self.module.set_parameter("gridname", self.ui.asset_col_line.text())
        else:
            self.module.set_parameter("gridname", self.ui.asset_col_combo.currentText())

        self.module.set_parameter("boundaryname", self.ui.boundary_combo.currentText())

        # --- SPATIAL GEOMETRY ---
        if self.ui.geometry_combo.currentIndex() == 0:
            self.module.set_parameter("geometry_type", "SQUARES")
        elif self.ui.geometry_combo.currentIndex() == 1:
            self.module.set_parameter("geometry_type", "HEXAGONS")
        elif self.ui.geometry_combo.currentIndex() == 2:
            self.module.set_parameter("geometry_type", "VECTORPATCH")
        elif self.ui.geometry_combo.currentIndex() == 3:
            self.module.set_parameter("geometry_type", "RASTER")
        elif self.ui.geometry_combo.currentIndex() == 4:
            self.module.set_parameter("geometry_type", "GEOHASH")
        else:
            self.module.set_parameter("geometry_type", "PARCEL")

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
        self.module.set_parameter("patchzonemap", self.combomaps[1][self.ui.patch_data_zoneombo.currentIndex()-1])

        if self.ui.patch_discretize_grid_radio.isChecked():
            self.module.set_parameter("disgrid_type", "GRID")
        elif self.ui.patch_discretize_boundary_radio.isChecked():
            self.module.set_parameter("disgrid_type", "BOUND")
        else:
            self.module.set_parameter("disgrid_type", "NONE")

        self.module.set_parameter("disgrid_length", self.ui.patch_discretize_grid_spin.value())
        self.module.set_parameter("disgrid_auto", int(self.ui.patch_discretize_grid_auto.isChecked()))
        self.module.set_parameter("disgrid_map", self.discretmaps[1][self.ui.discret_combo.currentIndex()-1])

        # RASTER REPRESENTATION
        self.module.set_parameter("rastersize", self.ui.raster_resolution_spin.value())
        self.module.set_parameter("nodatavalue", int(self.ui.raster_nodata_line.text()))
        self.module.set_parameter("generate_fishnet", int(self.ui.raster_generatefishnet_check.isChecked()))

        # GEOHASH GRID REPRESENTATION
        self.module.set_parameter("geohash_lvl", int(self.ui.gh_res_spin.value()))

        # PARCEL REPRESENTATION
        self.module.set_parameter("parcel_map", self.parcelmaps[1][self.ui.parcel_combo.currentIndex()-1])

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
        # (1) Do we have a correct asset name or selected asset? (Radio Buttons)
        if self.ui.asset_col_new_radio.isChecked():
            for char in ubglobals.NOCHARS:
                if char in self.ui.asset_col_line.text():
                    nochars = True
                else:
                    nochars = False
            if nochars:
                prompt_msg = "Please enter a valid name for the Asset Collection!"
                QtWidgets.QMessageBox.warning(self, "Invalid Asset Collection Name", prompt_msg,
                                              QtWidgets.QMessageBox.Ok)
                return False
        else:
            if self.ui.asset_col_combo.currentIndex() == 0:
                prompt_msg = "Please select a valid Asset Collection for the simulation!"
                QtWidgets.QMessageBox.warning(self, "No Asset Collection selected", prompt_msg,
                                              QtWidgets.QMessageBox.Ok)
                return False

        # (2) Is there a valid boundary?
        if self.ui.boundary_combo.currentIndex() == 0:
            prompt_msg = "Please select a valid simulation boundary to use!"
            QtWidgets.QMessageBox.warning(self, "No valid boundary selected", prompt_msg,
                                          QtWidgets.QMessageBox.Ok)
            return False

        return True
