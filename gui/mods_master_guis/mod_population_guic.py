r"""
@file   mod_population.py
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
from .mod_population import Ui_Map_Population


# --- MAIN GUI FUNCTION ---
class PopulationLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 4
    longname = "Map Population"
    icon = ":/icons/demographics.png"

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
        self.ui = Ui_Map_Population()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog

        # Usage mode: with a scenario or not with a scenario (determines GUI settings)
        if mode == 1:
            self.active_scenario = simulation.get_active_scenario()
            # The active scenario is already set when the GUI is launched because the user could only click it if
            # a scenario is active. This active scenario will inform the rest of the GUI.
        else:
            self.active_scenario = None
        self.module = None  # Initialize the variable to hold the active module object

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        # Boundary combo box
        # self.ui.boundary_combo.clear()
        # self.ui.boundary_combo.addItem("(select simulation boundary)")
        # boundarynames = self.simulation.get_project_boundary_names()
        # for n in boundarynames:
        #     self.ui.boundary_combo.addItem(str(n))
        # if mode == 1:
        #     scenario_boundaryname = self.active_scenario.get_metadata("boundary")
        #     if scenario_boundaryname == "(select simulation boundary)":
        #         self.ui.boundary_combo.setCurrentIndex(0)
        #     else:
        #         self.ui.boundary_combo.setCurrentIndex(list(boundarynames).index(scenario_boundaryname)+1)
        #     self.ui.boundary_combo.setEnabled(0)
        # else:
        #     self.ui.boundary_combo.setEnabled(1)




        # self.gui_state = "initial"
        # self.change_active_module()
        # self.gui_state = "ready"
        #
        # self.ui.rep_stack.setCurrentIndex(self.ui.rep_combo.currentIndex())
        #
        # # --- SIGNALS AND SLOTS ---
        # self.ui.year_combo.currentIndexChanged.connect(self.change_active_module)
        # self.ui.autofillButton.clicked.connect(self.autofill_from_previous_year)
        # self.ui.same_params.clicked.connect(self.same_parameters_check)
        # self.ui.reset_button.clicked.connect(self.reset_parameters_to_default)
        #
        # self.ui.lu_fromurbandev.clicked.connect(self.enable_disable_guis)
        # self.ui.pop_fromurbandev.clicked.connect(self.enable_disable_guis)
        # self.ui.pop_correct_check.clicked.connect(self.enable_disable_guis)
        # self.ui.pop_correct_auto.clicked.connect(self.enable_disable_guis)
        # self.ui.resolution_sq_auto.clicked.connect(self.enable_disable_guis)
        # self.ui.edgelength_auto.clicked.connect(self.enable_disable_guis)
        # self.ui.hexsize_auto.clicked.connect(self.enable_disable_guis)
        # self.ui.vectorgrid_auto.clicked.connect(self.enable_disable_guis)
        #
        # self.ui.geopolitical_check.clicked.connect(self.enable_disable_guis)
        # self.ui.suburb_check.clicked.connect(self.enable_disable_guis)
        # self.ui.planzone_check.clicked.connect(self.enable_disable_guis)
        # self.ui.considergeo_check.clicked.connect(self.enable_disable_guis)
        # self.ui.cbdknown_radio.clicked.connect(self.enable_disable_guis)
        # self.ui.cbdmanual_radio.clicked.connect(self.enable_disable_guis)
        #
        # self.ui.rivers_check.clicked.connect(self.enable_disable_guis)
        # self.ui.lakes_check.clicked.connect(self.enable_disable_guis)
        # self.ui.storm_check.clicked.connect(self.enable_disable_guis)
        # # self.ui.sewer_check.clicked.connect(self.enable_disable_guis)
        # # self.ui.supply_check.clicked.connect(self.enable_disable_guis)
        #
        # self.ui.flowpath_check.clicked.connect(self.enable_disable_guis)
        #
        # # Advanced / Experimental
        # self.ui.patchflow_delin.clicked.connect(self.enable_disable_guis)
        # self.ui.patchflow_searchradius_auto.clicked.connect(self.enable_disable_guis)
        #
        # self.ui.buttonBox.accepted.connect(self.save_values)

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        pass
        # --- ESSENTIAL SPATIAL DATA SETS ---
        # Dynamic setup of data combo boxes
        # try:    # LAND USE COMBO - retrieve the dataID from module
        #     self.ui.lu_combo.setCurrentIndex(self.lumaps[1].index(self.module.get_parameter("landuse_map")))
        #     # if dataID is available, set the combo box
        # except ValueError:
        #     self.ui.lu_combo.setCurrentIndex(0) # else the map must've been removed, set combo to zero index
        #
        # try:    # POPULATION COMBO
        #     self.ui.pop_combo.setCurrentIndex(self.popmaps[1].index(self.module.get_parameter("population_map")))
        # except ValueError:
        #     self.ui.pop_combo.setCurrentIndex(0)
        #
        # try:    # ELEVATION COMBO
        #     self.ui.elev_combo.setCurrentIndex(self.elevmaps[1].index(self.module.get_parameter("elevation_map")))
        # except ValueError:
        #     self.ui.elev_combo.setCurrentIndex(0)
        #
        # self.ui.pop_fromurbandev.setChecked(int(self.module.get_parameter("population_fud")))
        # self.ui.lu_fromurbandev.setChecked(int(self.module.get_parameter("landuse_fud")))
        #
        # self.ui.pop_correct_check.setChecked(int(self.module.get_parameter("population_corr")))
        # self.ui.pop_correct_spin.setValue(self.module.get_parameter("population_scale"))
        # self.ui.pop_correct_auto.setChecked(int(self.module.get_parameter("population_scale_auto")))
        # self.ui.demsmooth_check.setChecked(self.module.get_parameter("dem_smooth"))
        # self.ui.demsmooth_spin.setValue(self.module.get_parameter("dem_passes"))
        #
        # # --- SPATIAL GEOMETRY ---
        # spatial_ref = ["SQUARES", "HEXAGONS", "VECTORPATCH"]
        # self.ui.rep_combo.setCurrentIndex(spatial_ref.index(self.module.get_parameter("geometry_type")))
        #
        # # BLOCKS GEOMETRY
        # self.ui.resolution_spin.setValue(self.module.get_parameter("blocksize"))
        # self.ui.resolution_sq_auto.setChecked(int(self.module.get_parameter("blocksize_auto")))
        # self.ui.spatialmetrics_sq_check.setChecked(int(self.module.get_parameter("spatialmetrics_sq")))
        # self.ui.patchdelin_sq_check.setChecked(int(self.module.get_parameter("patchdelin_sq")))
        #
        # if self.module.get_parameter("neighbourhood") == "M":
        #     self.ui.radio_moore.setChecked(1)
        # else:
        #     self.ui.radio_vonNeu.setChecked(1)
        #
        # self.ui.edgelength_spin.setValue(self.module.get_parameter("min_edge_length"))
        # self.ui.edgelength_auto.setChecked(int(self.module.get_parameter("min_edge_auto")))
        #
        # # HEXAGON GEOMETRY
        # self.ui.hexsize_spin.setValue(self.module.get_parameter("hexsize"))
        # self.ui.hexsize_auto.setChecked(int(self.module.get_parameter("hexsize_auto")))
        # if self.module.get_parameter("hex_orientation") == "NS":
        #     self.ui.radio_hexoNS.setChecked(1)
        # else:
        #     self.ui.radio_hexoEW.setChecked(1)
        #
        # self.ui.spatialmetrics_hex_check.setChecked(int(self.module.get_parameter("spatialmetrics_hex")))
        # self.ui.patchdelin_hex_check.setChecked(int(self.module.get_parameter("patchdelin_hex")))
        #
        # # VECTORPATCHES
        # disgrid = ["SQ", "HNS", "HEW"]
        # self.ui.disgrid_combo.setCurrentIndex(disgrid.index(self.module.get_parameter("disgrid_shape")))
        # self.ui.vectorgrid_spin.setValue(self.module.get_parameter("disgrid"))
        # self.ui.vectorgrid_auto.setChecked(int(self.module.get_parameter("disgrid_auto")))
        #
        # # --- JURISDICTIONAL AND SUBURBAN BOUNDARIES ---
        # try:    # MUNICIPAL BOUNDARY MAP COMBO
        #     self.ui.geopolitical_combo.setCurrentIndex(self.municipalmaps[1].index(
        #         self.module.get_parameter("geopolitical_map")))
        # except ValueError:
        #     self.ui.geopolitical_combo.setCurrentIndex(0)
        #
        # try:    # SUBURB BOUNDARY MAP COMBO
        #     self.ui.suburb_combo.setCurrentIndex(self.suburbmaps[1].index(self.module.get_parameter("suburban_map")))
        # except ValueError:
        #     self.ui.suburb_combo.setCurrentIndex(0)
        #
        # try:    # PLANNING ZONES BOUNDARY MAP COMBO
        #     self.ui.planzone_combo.setCurrentIndex(self.planzonemaps[1].index(
        #         self.module.get_parameter("planzone_map")))
        # except ValueError:
        #     self.ui.planzone_combo.setCurrentIndex(0)
        #
        # self.ui.geopolitical_check.setChecked(self.module.get_parameter("include_geopolitical"))
        # self.ui.geopolitical_line.setText(self.module.get_parameter("geopolitical_attref"))
        # self.ui.suburb_check.setChecked(self.module.get_parameter("include_suburb"))
        # self.ui.suburb_line.setText(self.module.get_parameter("suburban_attref"))
        # self.ui.planzone_check.setChecked(self.module.get_parameter("include_planzone"))
        # self.ui.planzone_line.setText(self.module.get_parameter("planzone_attref"))
        #
        # # --- CENTRAL BUSINESS DISTRICT ---
        # self.ui.considergeo_check.setChecked(self.module.get_parameter("considerCBD"))
        # if self.module.get_parameter("locationOption") == "S":  # S = Selection, C = coordinates
        #     self.ui.cbdknown_radio.setChecked(1)
        # else:
        #     self.ui.cbdmanual_radio.setChecked(1)
        #
        # self.ui.cbdlong_box.setText(str(self.module.get_parameter("locationLong")))
        # self.ui.cbdlat_box.setText(str(self.module.get_parameter("locationLat")))
        # self.ui.cbdmark_check.setChecked(self.module.get_parameter("marklocation"))
        #
        # # --- MAJOR WATER FEATURES ---
        # try:    # RIVER COMBO
        #     self.ui.rivers_combo.setCurrentIndex(self.rivermaps[1].index(self.module.get_parameter("river_map")))
        # except ValueError:
        #     self.ui.rivers_combo.setCurrentIndex(0)
        #
        # try:    # LAKES COMBO
        #     self.ui.lakes_combo.setCurrentIndex(self.lakemaps[1].index(self.module.get_parameter("lake_map")))
        # except ValueError:
        #     self.ui.lakes_combo.setCurrentIndex(0)
        #
        # self.ui.rivers_check.setChecked(self.module.get_parameter("include_rivers"))
        # self.ui.rivers_attname.setText(self.module.get_parameter("river_attname"))
        # self.ui.lakes_check.setChecked(self.module.get_parameter("include_lakes"))
        # self.ui.lakes_attname.setText(self.module.get_parameter("lake_attname"))
        # self.ui.waterbody_distance_check.setChecked(self.module.get_parameter("calculate_wbdistance"))
        #
        # # --- BUILT WATER INFRASTRUCTURE ---
        # self.ui.storm_check.setChecked(self.module.get_parameter("include_storm"))
        # # self.ui.sewer_check.setChecked(self.module.get_parameter("include_sewer"))
        # # self.ui.supply_check.setChecked(self.module.get_parameter("include_supply"))
        #
        # try:    # STORMWATER DRAINAGE FEATURES COMBO
        #     self.ui.storm_combo.setCurrentIndex(self.builtwaterfeatures[1].index(
        #         self.module.get_parameter("storm_map")))
        # except ValueError:
        #     self.ui.storm_combo.setCurrentIndex(0)

        # try:    # SEWER SYSTEM FEATURES COMBO
        #     self.ui.sewer_combo.setCurrentIndex(self.builtwaterfeatures[1].index(
        #         self.module.get_parameter("sewer_map")))
        # except ValueError:
        #     self.ui.storm_combo.setCurrentIndex(0)
        #
        # try:    # SUPPLY FEATURES COMBO
        #     self.ui.supply_combo.setCurrentIndex(self.builtwaterfeatures[1].index(
        #         self.module.get_parameter("supply_map")))
        # except ValueError:
        #     self.ui.supply_combo.setCurrentIndex(0)

        # --- FLOWPATH DELINEATION ---
        # self.ui.flowpath_check.setChecked(int(self.module.get_parameter("flowpaths")))
        # self.ui.flowpath_combo.setCurrentIndex(self.delin_methods.index(self.module.get_parameter("flowpath_method")))
        # self.ui.natfeature_check.setChecked(self.module.get_parameter("guide_natural"))
        # self.ui.infrastructure_check.setChecked(self.module.get_parameter("guide_built"))
        # self.ui.ignore_rivers_check.setChecked(self.module.get_parameter("ignore_rivers"))
        # self.ui.ignore_lakes_check.setChecked(self.module.get_parameter("ignore_lakes"))
        #
        # # --- ADVANCED / EXPERIMENTAL PARAMETERS ---
        # # Patch Flow Paths
        # self.ui.patchflow_delin.setChecked(int(self.module.get_parameter("patchflowpaths")))
        # self.ui.patchflow_method_combo.setCurrentIndex(ubglobals.PATCHFLOWMETHODS.index(
        #     self.module.get_parameter("patchflowmethod")))
        # self.ui.patchflow_searchradius_spin.setValue(float(self.module.get_parameter("patchsearchradius")))
        # self.ui.patchflow_searchradius_auto.setChecked(int(self.module.get_parameter("patchsearchauto")))
        #
        # # Hexagon Neighbourhood GUIs
        # if self.module.get_parameter("hex_neighbourhood") == "ISO":
        #     self.ui.radio_hexnISO.setChecked(1)
        # elif self.module.get_parameter("hex_neighbourhood") == "YINV":
        #     self.ui.radio_hexnYINV.setChecked(1)
        # elif self.module.get_parameter("hex_neighbourhood") == "YNOR":
        #     self.ui.radio_hexnYNOR.setChecked(1)
        # else:
        #     self.ui.radio_hexnNOR.setChecked(1)
        #
        # # Open Space Network GUIs
        # self.ui.osnet_accessibility_check.setChecked(self.module.get_parameter("osnet_accessibility"))
        # self.ui.osnet_spacenet_check.setChecked(self.module.get_parameter("osnet_network"))
        #
        # self.enable_disable_guis()

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
        pass
        # # --- ESSENTIAL SPATIAL DATA SETS ---
        # self.module.set_parameter("landuse_map", self.lumaps[1][self.ui.lu_combo.currentIndex()])
        # self.module.set_parameter("population_map", self.popmaps[1][self.ui.pop_combo.currentIndex()])
        # self.module.set_parameter("elevation_map", self.elevmaps[1][self.ui.elev_combo.currentIndex()])
        # self.module.set_parameter("landuse_fud", int(self.ui.lu_fromurbandev.isChecked()))
        # self.module.set_parameter("population_fud", int(self.ui.pop_fromurbandev.isChecked()))
        #
        # self.module.set_parameter("population_corr", int(self.ui.pop_correct_check.isChecked()))
        # self.module.set_parameter("population_scale", float(self.ui.pop_correct_spin.value()))
        # self.module.set_parameter("population_scale_auto", int(self.ui.pop_correct_auto.isChecked()))
        # self.module.set_parameter("dem_smooth", int(self.ui.demsmooth_check.isChecked()))
        # self.module.set_parameter("dem_passes", int(self.ui.demsmooth_spin.value()))
        #
        # # --- SPATIAL GEOMETRY ---
        # if self.ui.rep_combo.currentIndex() == 0:
        #     self.module.set_parameter("geometry_type", "SQUARES")
        # elif self.ui.rep_combo.currentIndex() == 1:
        #     self.module.set_parameter("geometry_type", "HEXAGONS")
        # elif self.ui.rep_combo.currentIndex() == 2:
        #     self.module.set_parameter("geometry_type", "VECTORPATCH")
        #
        # # SQUARE GRIDS
        # self.module.set_parameter("blocksize", self.ui.resolution_spin.value())
        # self.module.set_parameter("blocksize_auto", int(self.ui.resolution_sq_auto.isChecked()))
        # self.module.set_parameter("patchdelin_sq", int(self.ui.patchdelin_sq_check.isChecked()))
        # self.module.set_parameter("spatialmetrics_sq", int(self.ui.spatialmetrics_sq_check.isChecked()))
        # self.module.set_parameter("min_edge_length", self.ui.edgelength_spin.value())
        # self.module.set_parameter("min_edge_auto", int(self.ui.edgelength_auto.isChecked()))
        #
        # if self.ui.radio_moore.isChecked():
        #     self.module.set_parameter("neighbourhood", "M")
        # else:
        #     self.module.set_parameter("neighbourhood", "V")
        #
        # # HEX GRIDS
        # self.module.set_parameter("hexsize", self.ui.hexsize_spin.value())
        # self.module.set_parameter("hexsize_auto", int(self.ui.hexsize_auto.isChecked()))
        # if self.ui.radio_hexoNS.isChecked():
        #     self.module.set_parameter("hex_orientation", "NS")
        # else:
        #     self.module.set_parameter("hex_orientation", "EW")
        # self.module.set_parameter("patchdelin_hex", int(self.ui.patchdelin_hex_check.isChecked()))
        # self.module.set_parameter("spatialmetrics_hex", int(self.ui.spatialmetrics_hex_check.isChecked()))
        #
        # # VECTORPATCH GRID
        # if self.ui.disgrid_combo.currentIndex() == 0:
        #     self.module.set_parameter("disgrid_shape", "SQ")
        # elif self.ui.rep_combo.currentIndex() == 1:
        #     self.module.set_parameter("disgrid_shape", "HNS")
        # elif self.ui.rep_combo.currentIndex() == 2:
        #     self.module.set_parameter("disgrid_shape", "HEW")
        # self.module.set_parameter("disgrid", self.ui.vectorgrid_spin.value())
        # self.module.set_parameter("disgrid_auto", int(self.ui.vectorgrid_auto.isChecked()))
        #
        # # --- JURISDICTIONAL AND SUBURBAN BOUNDARIES ---
        # self.module.set_parameter("include_geopolitical", int(self.ui.geopolitical_check.isChecked()))
        # self.module.set_parameter("geopolitical_map", self.municipalmaps[1][self.ui.geopolitical_combo.currentIndex()])
        # self.module.set_parameter("geopolitical_attref", self.ui.geopolitical_line.text())
        # self.module.set_parameter("include_suburb", int(self.ui.suburb_check.isChecked()))
        # self.module.set_parameter("suburban_map", self.suburbmaps[1][self.ui.suburb_combo.currentIndex()])
        # self.module.set_parameter("suburban_attref", self.ui.suburb_line.text())
        # self.module.set_parameter("include_planzone", int(self.ui.planzone_check.isChecked()))
        # self.module.set_parameter("planzone_map", self.planzonemaps[1][self.ui.planzone_combo.currentIndex()])
        # self.module.set_parameter("planzone_attref", self.ui.planzone_line.text())
        #
        # # --- CENTRAL BUSINESS DISTRICT ---
        # self.module.set_parameter("considerCBD", int(self.ui.considergeo_check.isChecked()))
        # if self.ui.cbdknown_radio.isChecked():
        #     self.module.set_parameter("locationOption", "S")
        # else:
        #     self.module.set_parameter("locationOption", "C")
        # self.module.set_parameter("locationLong", float(self.ui.cbdlong_box.text()))
        # self.module.set_parameter("locationLat", float(self.ui.cbdlat_box.text()))
        # self.module.set_parameter("marklocation", int(self.ui.cbdmark_check.isChecked()))
        #
        # # --- MAJOR WATER FEATURES ---
        # self.module.set_parameter("include_rivers", int(self.ui.rivers_check.isChecked()))
        # self.module.set_parameter("include_lakes", int(self.ui.lakes_check.isChecked()))
        # self.module.set_parameter("calculate_wbdistance", int(self.ui.waterbody_distance_check.isChecked()))
        # self.module.set_parameter("river_map", self.rivermaps[1][self.ui.rivers_combo.currentIndex()])
        # self.module.set_parameter("lake_map", self.lakemaps[1][self.ui.lakes_combo.currentIndex()])
        # self.module.set_parameter("river_attname", str(self.ui.rivers_attname.text()))
        # self.module.set_parameter("lake_attname", str(self.ui.lakes_attname.text()))
        #
        # # --- BUILT WATER INFRASTRUCTURE ---
        # self.module.set_parameter("include_storm", int(self.ui.storm_check.isChecked()))
        # self.module.set_parameter("storm_map", self.builtwaterfeatures[1][self.ui.storm_combo.currentIndex()])
        # # self.module.set_parameter("include_sewer", int(self.ui.sewer_check.isChecked()))
        # # self.module.set_parameter("sewer_map", self.builtwaterfeatures[1][self.ui.sewer_combo.currentIndex()])
        # # self.module.set_parameter("include_supply", int(self.ui.supply_check.isChecked()))
        # # self.module.set_parameter("supply_map", self.builtwaterfeatures[1][self.ui.supply_combo.currentIndex()])
        #
        # # DEBUG
        # # print(f"{self.builtwaterfeatures}, {self.builtwaterfeatures[1][self.ui.storm_combo.currentIndex()]}")
        #
        # # --- FLOW PATH DELINEATION ---
        # self.module.set_parameter("flowpaths", int(self.ui.flowpath_check.isChecked()))
        # self.module.set_parameter("flowpath_method", self.delin_methods[self.ui.flowpath_combo.currentIndex()])
        # self.module.set_parameter("guide_natural", int(self.ui.natfeature_check.isChecked()))
        # self.module.set_parameter("guide_built", int(self.ui.infrastructure_check.isChecked()))
        # self.module.set_parameter("ignore_rivers", int(self.ui.ignore_rivers_check.isChecked()))
        # self.module.set_parameter("ignore_lakes", int(self.ui.ignore_lakes_check.isChecked()))
        #
        # # --- ADVANCED / EXPERIMENTAL PARAMETERS -----------------------------------------------------------------------
        # # Patch Flowpaths
        # self.module.set_parameter("patchflowpaths", int(self.ui.patchflow_delin.isChecked()))
        # self.module.set_parameter("patchflowmethod",
        #                           ubglobals.PATCHFLOWMETHODS[int(self.ui.patchflow_method_combo.currentIndex())])
        # self.module.set_parameter("patchsearchradius", float(self.ui.patchflow_searchradius_spin.value()))
        # self.module.set_parameter("patchsearchauto", int(self.ui.patchflow_searchradius_auto.isChecked()))
        #
        # # Hexagon Neighbourhoods
        # if self.ui.radio_hexnISO.isChecked():
        #     self.module.set_parameter("hex_neighbourhood", "ISO")
        # elif self.ui.radio_hexnYINV.isChecked():
        #     self.module.set_parameter("hex_neighbourhood", "YINV")
        # elif self.ui.radio_hexnYNOR.isChecked():
        #     self.module.set_parameter("hex_neighbourhood", "YNOR")
        # else:
        #     self.module.set_parameter("hex_neighbourhood", "NOR")
        #
        # # Open Space Networks
        # self.module.set_parameter("osnet_accessibility", int(self.ui.osnet_accessibility_check.isChecked()))
        # self.module.set_parameter("osnet_network", int(self.ui.osnet_spacenet_check.isChecked()))
        # # --------------------------------------------------------------------------------------------------------------