"""
@file   md_delinblocksguic.py
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

# --- PYTHON LIBRARY IMPORTS ---

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from .md_delinblocksgui import Ui_Delinblocks_Dialog


# --- MAIN GUI FUNCTION ---
class DelinBlocksGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Delinblocks_Dialog()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.active_scenario = simulation.get_active_scenario()
        # The active scenario is already set when the GUI is launched because the user could only click it if
        # a scenario is active. This active scenario will inform the rest of the GUI.
        self.module = None  # Initialize the variable to hold the active module object

        # --- SIMULATION YEAR SETTINGS ---
        simyears = self.active_scenario.get_simulation_years()  # gets the simulation years
        if len(simyears) > 1:
            self.ui.year_combo.setEnabled(1)        # if more than one year, enables the box for selection
            self.ui.autofillButton.setEnabled(1)
            self.ui.same_params.setEnabled(1)
            self.ui.year_combo.clear()
            for yr in simyears:
                self.ui.year_combo.addItem(str(yr))
        else:
            self.ui.autofillButton.setEnabled(0)    # if static or benchmark, then only one year is available
            self.ui.same_params.setEnabled(0)       # so all of the sidebar buttons get disabled.
            self.ui.year_combo.setEnabled(0)
            self.ui.year_combo.clear()
            self.ui.year_combo.addItem(str(simyears[0]))
        self.ui.year_combo.setCurrentIndex(0)   # Set to the first item on the list.

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        self.lumaps = self.get_dataref_array("spatial", "Land Use")  # Obtain the data ref array
        self.ui.lu_combo.clear()  # Clear the combo box first before setting it up
        # Set up the combo box (note: this also includes the no map option)
        [self.ui.lu_combo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        self.popmaps = self.get_dataref_array("spatial", "Population")
        self.ui.pop_combo.clear()
        [self.ui.pop_combo.addItem(str(self.popmaps[0][i])) for i in range(len(self.popmaps[0]))]

        self.elevmaps = self.get_dataref_array("spatial", "Elevation")
        self.ui.elev_combo.clear()
        [self.ui.elev_combo.addItem(str(self.elevmaps[0][i])) for i in range(len(self.elevmaps[0]))]

        self.municipalmaps = self.get_dataref_array("spatial", "Boundaries", "Geopolitical")
        self.ui.geopolitical_combo.clear()
        [self.ui.geopolitical_combo.addItem(str(self.municipalmaps[0][i])) for i in range(len(self.municipalmaps[0]))]

        self.suburbmaps = self.get_dataref_array("spatial", "Boundaries", "Suburban")
        self.ui.suburb_combo.clear()
        [self.ui.suburb_combo.addItem(str(self.suburbmaps[0][i])) for i in range(len(self.suburbmaps[0]))]

        self.planzonemaps = self.get_dataref_array("spatial", "Boundaries", "Planning Zones")
        self.ui.planzone_combo.clear()
        [self.ui.planzone_combo.addItem(str(self.planzonemaps[0][i])) for i in range(len(self.planzonemaps[0]))]

        self.ui.city_combo.clear()
        self.citynames = ubglobals.COORDINATES.keys()
        self.citynames.sort()
        [self.ui.city_combo.addItem(str(n)) for n in self.citynames]

        self.rivermaps = self.get_dataref_array("spatial", "Water Bodies", "Rivers")
        self.ui.rivers_combo.clear()
        [self.ui.rivers_combo.addItem(str(self.rivermaps[0][i])) for i in range(len(self.rivermaps[0]))]

        self.lakemaps = self.get_dataref_array("spatial", "Water Bodies", "Lakes")
        self.ui.lakes_combo.clear()
        [self.ui.lakes_combo.addItem(str(self.lakemaps[0][i])) for i in range(len(self.lakemaps[0]))]

        self.builtwaterfeatures = self.get_dataref_array("spatial", "Built Infrastructure", "Water Network")
        self.ui.storm_combo.clear()
        [self.ui.storm_combo.addItem(str(self.builtwaterfeatures[0][i])) for i in range(len(self.builtwaterfeatures[0]))]

        # self.ui.supply_combo.clear()
        # [self.ui.supply_combo.addItem(str(self.builtwaterfeatures[0][i])) for i in range(len(self.builtwaterfeatures[0]))]
        #
        # self.ui.sewer_combo.clear()
        # [self.ui.sewer_combo.addItem(str(self.builtwaterfeatures[0][i])) for i in range(len(self.builtwaterfeatures[0]))]

        self.delin_methods = ["Dinf", "D8"]

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        self.ui.year_combo.currentIndexChanged.connect(self.change_active_module)
        self.ui.autofillButton.clicked.connect(self.autofill_from_previous_year)
        self.ui.same_params.clicked.connect(self.same_parameters_check)
        self.ui.reset_button.clicked.connect(self.reset_parameters_to_default)

        self.ui.lu_fromurbandev.clicked.connect(self.enable_disable_guis)
        self.ui.pop_fromurbandev.clicked.connect(self.enable_disable_guis)
        self.ui.geopolitical_check.clicked.connect(self.enable_disable_guis)
        self.ui.suburb_check.clicked.connect(self.enable_disable_guis)
        self.ui.planzone_check.clicked.connect(self.enable_disable_guis)
        self.ui.resolution_auto.clicked.connect(self.enable_disable_guis)
        self.ui.considergeo_check.clicked.connect(self.enable_disable_guis)
        self.ui.cbdknown_radio.clicked.connect(self.enable_disable_guis)
        self.ui.cbdmanual_radio.clicked.connect(self.enable_disable_guis)
        self.ui.rivers_check.clicked.connect(self.enable_disable_guis)
        self.ui.lakes_check.clicked.connect(self.enable_disable_guis)
        self.ui.storm_check.clicked.connect(self.enable_disable_guis)
        # self.ui.sewer_check.clicked.connect(self.enable_disable_guis)
        # self.ui.supply_check.clicked.connect(self.enable_disable_guis)
        self.ui.patchflow_delin.clicked.connect(self.enable_disable_guis)
        self.ui.patchflow_searchradius_auto.clicked.connect(self.enable_disable_guis)

        self.ui.buttonBox.accepted.connect(self.save_values)

    def same_parameters_check(self):    # TO DO
        """Checks if the 'same parameters' checkbox is checked, automatically disables GUI time combobox, takes
        current parameters in the GUI and saves to all modules when the GUI box is closed with accept() signal
        (i.e. OK button pressed)."""
        if self.ui.same_params.isChecked():
            pass    # Functions if checked
        else:
            pass    # Functions if unchecked

    def autofill_from_previous_year(self):  # TO DO
        """Autofills all GUI parameters from the previous year's class instance."""
        pass    # Figure out some automatic parameter filling function that can be called in the delinblocks module

    def reset_parameters_to_default(self):  # TO DO
        """Resets all parameters of the current module instance back to default values."""
        pass

    def change_active_module(self):
        """Searches for the active module based on the simulation year combo box and updates the GUI."""
        # Send message box to user to ask whether to save current parameters
        if self.gui_state == "ready":
            prompt_msg = "You are about to change the time period, do you wish to save changes made to your parameters " \
                         "for the current time step?"
            reply = QtWidgets.QMessageBox.question(self, "Changing Time Period", prompt_msg,
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                           QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                self.save_values()
            elif reply == QtWidgets.QMessageBox.No:
                pass
            else:
                return

        # Retrieve the DelinBlocks() Reference corresponding to the current year
        self.module = self.active_scenario.get_module_object("SPATIAL", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()
        return True

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # --- ESSENTIAL SPATIAL DATA SETS ---
        # Dynamic setup of data combo boxes
        try:    # LAND USE COMBO - retrieve the dataID from module
            self.ui.lu_combo.setCurrentIndex(self.lumaps[1].index(self.module.get_parameter("landuse_map")))
            # if dataID is available, set the combo box
        except ValueError:
            self.ui.lu_combo.setCurrentIndex(0) # else the map must've been removed, set combo to zero index

        try:    # POPULATION COMBO
            self.ui.pop_combo.setCurrentIndex(self.popmaps[1].index(self.module.get_parameter("population_map")))
        except ValueError:
            self.ui.pop_combo.setCurrentIndex(0)

        try:    # ELEVATION COMBO
            self.ui.elev_combo.setCurrentIndex(self.elevmaps[1].index(self.module.get_parameter("elevation_map")))
        except ValueError:
            self.ui.elev_combo.setCurrentIndex(0)

        self.ui.pop_fromurbandev.setChecked(int(self.module.get_parameter("population_fud")))
        self.ui.lu_fromurbandev.setChecked(int(self.module.get_parameter("landuse_fud")))

        # --- SPATIAL GEOMETRY ---
        spatial_ref = ["BLOCKS", "HEXAGONS"]
        self.ui.rep_combo.setCurrentIndex(spatial_ref.index(self.module.get_parameter("geometry_type")))
        self.ui.resolution_spin.setValue(self.module.get_parameter("blocksize"))
        self.ui.resolution_auto.setChecked(int(self.module.get_parameter("blocksize_auto")))
        if self.module.get_parameter("neighbourhood") == "M":
            self.ui.radio_moore.setChecked(1)
        else:
            self.ui.radio_vonNeu.setChecked(1)
        self.ui.spatialindices_check.setChecked(self.module.get_parameter("spatialmetrics"))
        self.ui.patchdelin_check.setChecked(self.module.get_parameter("patchdelin"))

        # --- JURISDICTIONAL AND SUBURBAN BOUNDARIES ---
        try:    # MUNICIPAL BOUNDARY MAP COMBO
            self.ui.geopolitical_combo.setCurrentIndex(self.municipalmaps[1].index(
                self.module.get_parameter("geopolitical_map")))
        except ValueError:
            self.ui.geopolitical_combo.setCurrentIndex(0)

        try:    # SUBURB BOUNDARY MAP COMBO
            self.ui.suburb_combo.setCurrentIndex(self.suburbmaps[1].index(self.module.get_parameter("suburban_map")))
        except ValueError:
            self.ui.suburb_combo.setCurrentIndex(0)

        try:    # PLANNING ZONES BOUNDARY MAP COMBO
            self.ui.planzone_combo.setCurrentIndex(self.planzonemaps[1].index(
                self.module.get_parameter("planzone_map")))
        except ValueError:
            self.ui.planzone_combo.setCurrentIndex(0)

        self.ui.geopolitical_check.setChecked(self.module.get_parameter("include_geopolitical"))
        self.ui.geopolitical_line.setText(self.module.get_parameter("geopolitical_attref"))
        self.ui.suburb_check.setChecked(self.module.get_parameter("include_suburb"))
        self.ui.suburb_line.setText(self.module.get_parameter("suburban_attref"))
        self.ui.planzone_check.setChecked(self.module.get_parameter("include_planzone"))
        self.ui.planzone_line.setText(self.module.get_parameter("planzone_attref"))

        # --- CENTRAL BUSINESS DISTRICT ---
        self.ui.considergeo_check.setChecked(self.module.get_parameter("considerCBD"))
        if self.module.get_parameter("locationOption") == "S":  # S = Selection, C = coordinates
            self.ui.cbdknown_radio.setChecked(1)
        else:
            self.ui.cbdmanual_radio.setChecked(1)

        project_city = self.simulation.get_project_parameter("city")
        self.ui.city_combo.setCurrentIndex(self.citynames.index(project_city))
        self.ui.cbdlong_box.setText(str(self.module.get_parameter("locationLong")))
        self.ui.cbdlat_box.setText(str(self.module.get_parameter("locationLat")))
        self.ui.cbdmark_check.setChecked(self.module.get_parameter("marklocation"))

        # --- OPEN SPACE NETWORK ---
        self.ui.osnet_accessibility_check.setChecked(self.module.get_parameter("osnet_accessibility"))
        self.ui.osnet_spacenet_check.setChecked(self.module.get_parameter("osnet_network"))

        # --- MAJOR WATER FEATURES ---
        try:    # RIVER COMBO
            self.ui.rivers_combo.setCurrentIndex(self.rivermaps[1].index(self.module.get_parameter("river_map")))
        except ValueError:
            self.ui.rivers_combo.setCurrentIndex(0)

        try:    # LAKES COMBO
            self.ui.lakes_combo.setCurrentIndex(self.lakemaps[1].index(self.module.get_parameter("lake_map")))
        except ValueError:
            self.ui.lakes_combo.setCurrentIndex(0)

        self.ui.rivers_check.setChecked(self.module.get_parameter("include_rivers"))
        self.ui.rivers_attname.setText(self.module.get_parameter("river_attname"))
        self.ui.lakes_check.setChecked(self.module.get_parameter("include_lakes"))
        self.ui.lakes_attname.setText(self.module.get_parameter("lake_attname"))
        self.ui.waterbody_distance_check.setChecked(self.module.get_parameter("calculate_wbdistance"))

        # --- BUILT WATER INFRASTRUCTURE ---
        self.ui.storm_check.setChecked(self.module.get_parameter("include_storm"))
        # self.ui.sewer_check.setChecked(self.module.get_parameter("include_sewer"))
        # self.ui.supply_check.setChecked(self.module.get_parameter("include_supply"))

        try:    # STORMWATER DRAINAGE FEATURES COMBO
            self.ui.storm_combo.setCurrentIndex(self.builtwaterfeatures[1].index(
                self.module.get_parameter("storm_map")))
        except ValueError:
            self.ui.storm_combo.setCurrentIndex(0)

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
        self.ui.flowpath_combo.setCurrentIndex(self.delin_methods.index(self.module.get_parameter("flowpath_method")))
        self.ui.demsmooth_check.setChecked(self.module.get_parameter("dem_smooth"))
        self.ui.demsmooth_spin.setValue(self.module.get_parameter("dem_passes"))
        self.ui.natfeature_check.setChecked(self.module.get_parameter("guide_natural"))
        self.ui.infrastructure_check.setChecked(self.module.get_parameter("guide_built"))
        self.ui.ignore_rivers_check.setChecked(self.module.get_parameter("ignore_rivers"))
        self.ui.ignore_lakes_check.setChecked(self.module.get_parameter("ignore_lakes"))

        self.ui.patchflow_delin.setChecked(int(self.module.get_parameter("patchflowpaths")))
        self.ui.patchflow_method_combo.setCurrentIndex(ubglobals.PATCHFLOWMETHODS.index(
            self.module.get_parameter("patchflowmethod")))
        self.ui.patchflow_searchradius_spin.setValue(float(self.module.get_parameter("patchsearchradius")))
        self.ui.patchflow_searchradius_auto.setChecked(int(self.module.get_parameter("patchsearchauto")))

        self.enable_disable_guis()

    def enable_disable_guis(self):
        """Enables and disabled the combox boxes based on the parameter values."""
        self.ui.lu_combo.setEnabled(not(self.ui.lu_fromurbandev.isChecked()))
        self.ui.pop_combo.setEnabled(not(self.ui.pop_fromurbandev.isChecked()))
        self.ui.geopolitical_combo.setEnabled(self.ui.geopolitical_check.isChecked())
        self.ui.suburb_combo.setEnabled(self.ui.suburb_check.isChecked())
        self.ui.planzone_combo.setEnabled(self.ui.planzone_check.isChecked())
        self.ui.geopolitical_line.setEnabled(self.ui.geopolitical_check.isChecked())
        self.ui.suburb_line.setEnabled(self.ui.suburb_check.isChecked())
        self.ui.planzone_line.setEnabled(self.ui.planzone_check.isChecked())

        self.ui.resolution_spin.setEnabled(not(self.ui.resolution_auto.isChecked()))
        self.ui.city_combo.setEnabled(self.ui.cbdknown_radio.isChecked())
        self.ui.cbdlong_box.setEnabled(self.ui.cbdmanual_radio.isChecked())
        self.ui.cbdlat_box.setEnabled(self.ui.cbdmanual_radio.isChecked())
        self.ui.cbdmark_check.setEnabled(self.ui.cbdmanual_radio.isChecked())
        self.ui.region_widget.setEnabled(self.ui.considergeo_check.isChecked())
        self.ui.rivers_combo.setEnabled(self.ui.rivers_check.isChecked())
        self.ui.rivers_attname.setEnabled(self.ui.rivers_check.isChecked())
        self.ui.lakes_combo.setEnabled(self.ui.lakes_check.isChecked())
        self.ui.lakes_attname.setEnabled(self.ui.lakes_check.isChecked())
        self.ui.waterbody_distance_check.setEnabled((self.ui.rivers_check.isChecked() or
                                                     self.ui.lakes_check.isChecked()))
        self.ui.natfeature_check.setEnabled((self.ui.rivers_check.isChecked() or
                                             self.ui.lakes_check.isChecked()))
        self.ui.storm_combo.setEnabled(self.ui.storm_check.isChecked())
        # self.ui.sewer_combo.setEnabled(self.ui.sewer_check.isChecked())
        # self.ui.supply_combo.setEnabled(self.ui.supply_check.isChecked())

        self.ui.ignore_rivers_check.setEnabled(self.ui.rivers_check.isChecked())
        self.ui.ignore_lakes_check.setEnabled(self.ui.lakes_check.isChecked())

        self.ui.patchflow_method_combo.setEnabled(self.ui.patchflow_delin.isChecked())
        self.ui.patchflow_searchradius_spin.setEnabled(self.ui.patchflow_delin.isChecked() and
                                                       not self.ui.patchflow_searchradius_auto.isChecked())
        self.ui.patchflow_searchradius_auto.setEnabled(self.ui.patchflow_delin.isChecked())


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
        # --- ESSENTIAL SPATIAL DATA SETS ---
        self.module.set_parameter("landuse_map", self.lumaps[1][self.ui.lu_combo.currentIndex()])
        self.module.set_parameter("population_map", self.popmaps[1][self.ui.pop_combo.currentIndex()])
        self.module.set_parameter("elevation_map", self.elevmaps[1][self.ui.elev_combo.currentIndex()])
        self.module.set_parameter("landuse_fud", int(self.ui.lu_fromurbandev.isChecked()))
        self.module.set_parameter("population_fud", int(self.ui.pop_fromurbandev.isChecked()))

        # --- SPATIAL GEOMETRY ---
        if self.ui.rep_combo.currentIndex() == 0:
            self.module.set_parameter("geometry_type", "BLOCKS")
        elif self.ui.rep_combo.currentIndex() == 1:
            self.module.set_parameter("geometry_type", "HEXAGONS")
        self.module.set_parameter("blocksize", self.ui.resolution_spin.value())
        self.module.set_parameter("blocksize_auto", int(self.ui.resolution_auto.isChecked()))
        if self.ui.radio_moore.isChecked():
            self.module.set_parameter("neighbourhood", "M")
        else:
            self.module.set_parameter("neighbourhood", "V")
        self.module.set_parameter("patchdelin", int(self.ui.patchdelin_check.isChecked()))
        self.module.set_parameter("spatialmetrics", int(self.ui.spatialindices_check.isChecked()))

        # --- JURISDICTIONAL AND SUBURBAN BOUNDARIES ---
        self.module.set_parameter("include_geopolitical", int(self.ui.geopolitical_check.isChecked()))
        self.module.set_parameter("geopolitical_map", self.municipalmaps[1][self.ui.geopolitical_combo.currentIndex()])
        self.module.set_parameter("geopolitical_attref", self.ui.geopolitical_line.text())
        self.module.set_parameter("include_suburb", int(self.ui.suburb_check.isChecked()))
        self.module.set_parameter("suburban_map", self.suburbmaps[1][self.ui.suburb_combo.currentIndex()])
        self.module.set_parameter("suburban_attref", self.ui.suburb_line.text())
        self.module.set_parameter("include_planzone", int(self.ui.planzone_check.isChecked()))
        self.module.set_parameter("planzone_map", self.planzonemaps[1][self.ui.planzone_combo.currentIndex()])
        self.module.set_parameter("planzone_attref", self.ui.planzone_line.text())

        # --- CENTRAL BUSINESS DISTRICT ---
        self.module.set_parameter("considerCBD", int(self.ui.considergeo_check.isChecked()))
        if self.ui.cbdknown_radio.isChecked():
            self.module.set_parameter("locationOption", "S")
        else:
            self.module.set_parameter("locationOption", "C")
        self.module.set_parameter("locationCity", self.citynames[self.ui.city_combo.currentIndex()])
        self.module.set_parameter("locationLong", float(self.ui.cbdlong_box.text()))
        self.module.set_parameter("locationLat", float(self.ui.cbdlat_box.text()))
        self.module.set_parameter("marklocation", int(self.ui.cbdmark_check.isChecked()))

        # --- OPEN SPACE NETWORK ---
        self.module.set_parameter("osnet_accessibility", int(self.ui.osnet_accessibility_check.isChecked()))
        self.module.set_parameter("osnet_network", int(self.ui.osnet_spacenet_check.isChecked()))

        # --- MAJOR WATER FEATURES ---
        self.module.set_parameter("include_rivers", int(self.ui.rivers_check.isChecked()))
        self.module.set_parameter("include_lakes", int(self.ui.lakes_check.isChecked()))
        self.module.set_parameter("calculate_wbdistance", int(self.ui.waterbody_distance_check.isChecked()))
        self.module.set_parameter("river_map", self.rivermaps[1][self.ui.rivers_combo.currentIndex()])
        self.module.set_parameter("lake_map", self.lakemaps[1][self.ui.lakes_combo.currentIndex()])
        self.module.set_parameter("river_attname", str(self.ui.rivers_attname.text()))
        self.module.set_parameter("lake_attname", str(self.ui.lakes_attname.text()))

        # --- BUILT WATER INFRASTRUCTURE ---
        self.module.set_parameter("include_storm", int(self.ui.storm_check.isChecked()))
        self.module.set_parameter("storm_map", self.builtwaterfeatures[1][self.ui.storm_combo.currentIndex()])
        print(f"{self.builtwaterfeatures}, {self.builtwaterfeatures[1][self.ui.storm_combo.currentIndex()]}")
        # self.module.set_parameter("include_sewer", int(self.ui.sewer_check.isChecked()))
        # self.module.set_parameter("sewer_map", self.builtwaterfeatures[1][self.ui.sewer_combo.currentIndex()])
        # self.module.set_parameter("include_supply", int(self.ui.supply_check.isChecked()))
        # self.module.set_parameter("supply_map", self.builtwaterfeatures[1][self.ui.supply_combo.currentIndex()])

        # --- FLOW PATH DELINEATION ---
        self.module.set_parameter("flowpath_method", self.delin_methods[self.ui.flowpath_combo.currentIndex()])
        self.module.set_parameter("dem_smooth", int(self.ui.demsmooth_check.isChecked()))
        self.module.set_parameter("dem_passes", int(self.ui.demsmooth_spin.value()))
        self.module.set_parameter("guide_natural", int(self.ui.natfeature_check.isChecked()))
        self.module.set_parameter("guide_built", int(self.ui.infrastructure_check.isChecked()))
        self.module.set_parameter("ignore_rivers", int(self.ui.ignore_rivers_check.isChecked()))
        self.module.set_parameter("ignore_lakes", int(self.ui.ignore_lakes_check.isChecked()))

        self.module.set_parameter("patchflowpaths", int(self.ui.patchflow_delin.isChecked()))
        self.module.set_parameter("patchflowmethod",
                                  ubglobals.PATCHFLOWMETHODS[int(self.ui.patchflow_method_combo.currentIndex())])
        self.module.set_parameter("patchsearchradius", float(self.ui.patchflow_searchradius_spin.value()))
        self.module.set_parameter("patchsearchauto", int(self.ui.patchflow_searchradius_auto.isChecked()))
