# -*- coding: utf-8 -*-
"""
@file   md_urbplanbbguic.py
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
from md_urbdevelop import Ui_Urbandev_Dialog


# --- MAIN GUI FUNCTION ---
class UrbdevelopGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Urbandev_Dialog()
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
        # self.pixmap_ref = [":/images/images/md_urbplanbb_general.jpg",
        #                    ":/images/images/md_urbplanbb_residential.jpg",
        #                    ":/images/images/md_urbplanbb_nonres.jpg",
        #                    ":/images/images/md_urbplanbb_roads.jpg",
        #                    ":/images/images/md_urbplanbb_openspaces.jpg",
        #                    ":/images/images/md_urbplanbb_others.jpg"]
        # self.adjust_module_img()

        # --- SIMULATION YEAR SETTINGS ---
        simyears = self.active_scenario.get_simulation_years()  # gets the simulation years
        if len(simyears) > 1:
            self.ui.year_combo.setEnabled(1)  # if more than one year, enables the box for selection
            self.ui.autofillButton.setEnabled(1)
            self.ui.same_params.setEnabled(1)
            self.ui.year_combo.clear()
            for yr in simyears:
                self.ui.year_combo.addItem(str(yr))
        else:
            self.ui.autofillButton.setEnabled(0)  # if static or benchmark, then only one year is available
            self.ui.same_params.setEnabled(0)  # so all of the sidebar buttons get disabled.
            self.ui.year_combo.setEnabled(0)
            self.ui.year_combo.clear()
            self.ui.year_combo.addItem(str(simyears[0]))
        self.ui.year_combo.setCurrentIndex(0)  # Set to the first item on the list.

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        # TAB 1 - Land use, population, employment
        # LAND USE
        self.lumaps = self.get_dataref_array("spatial", "Land Use")  # Obtain the data ref array
        # self.lumaps is used later on in other combo boxes too.
        print self.lumaps
        self.ui.input_luc_combo.clear()  # Clear the combo box first before setting it up
        [self.ui.input_luc_combo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        # POPULATION
        self.popmaps = self.get_dataref_array("spatial", "Population")
        self.ui.input_pop_combo.clear()
        [self.ui.input_pop_combo.addItem(str(self.popmaps[0][i])) for i in range(len(self.popmaps[0]))]

        # EMPLOYMENT
        self.employmaps = self.get_dataref_array("spatial", "Employment")  # Obtain the data ref array
        self.ui.employ_inputmap_combo.clear()  # Clear the combo box first before setting it up
        [self.ui.employ_inputmap_combo.addItem(str(self.employmaps[0][i])) for i in range(len(self.employmaps[0]))]

        # TAB 2 ACCESSIBILITY - Roads, Rail, Waterways, Lakes, Public Open Spaces, Locality
        # ROADS
        self.roadmaps = self.get_dataref_array("spatial", "Built Infrastructure", "Road Network")
        self.ui.access_roads_data.clear()  # Clear the combo box first before setting it up
        [self.ui.access_roads_data.addItem(str(self.roadmaps[0][i])) for i in range(len(self.roadmaps[0]))]

        # RAIL

        # WATERWAYS
        self.rivermaps = self.get_dataref_array("spatial", "Water Bodies", "Rivers")
        self.ui.access_waterways_data.clear()
        [self.ui.access_waterways_data.addItem(str(self.rivermaps[0][i])) for i in range(len(self.rivermaps[0]))]

        # LAKES
        self.lakemaps = self.get_dataref_array("spatial", "Water Bodies", "Lakes")  # variable reused later
        self.ui.access_lakes_data.clear()
        [self.ui.access_lakes_data.addItem(str(self.lakemaps[0][i])) for i in range(len(self.lakemaps[0]))]

        # PUBLIC OPEN SPACES
        self.ui.access_pos_data.clear()  # Clear the combo box first before setting it up
        [self.ui.access_pos_data.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        # POINTS OF INTEREST
        self.localitymaps = self.get_dataref_array("spatial", "Employment")  # Obtain the data ref array
        self.ui.access_poi_data.clear()  # Clear the combo box first before setting it up
        [self.ui.access_poi_data.addItem(str(self.localitymaps[0][i])) for i in range(len(self.localitymaps[0]))]

        # TAB 2 SUITABILITY - Elevation, Groundwater Depth, Soil Infiltration Rate, Custom Criteria
        # SLOPE
        self.elevmaps = self.get_dataref_array("spatial", "Elevation")
        self.ui.suit_slope_data.clear()
        [self.ui.suit_slope_data.addItem(str(self.elevmaps[0][i])) for i in range(len(self.elevmaps[0]))]

        # DEPTH TO GROUNDWATER
        # SOIL INFILTRATION RATES
        # CUSTOM CRITERIA 1 - Uses ALL maps [TO DO]
        # CUSTOM CRITERIA 2 - Uses ALL maps [TO DO]

        # TAB 2 ZONING - Water bodies, residential zoning maps
        # WATER BODIES
        self.ui.zoning_constraints_water_combo.clear()
        [self.ui.zoning_constraints_water_combo.addItem(str(self.lakemaps[0][i])) for i in range(len(self.lakemaps[0]))]

        # LAND USE MAPS FOR RES, COM, IND, OFFICES
        self.ui.zoning_rules_rescombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_rescombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]
        self.ui.zoning_rules_comcombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_comcombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]
        self.ui.zoning_rules_indcombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_indcombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]
        self.ui.zoning_rules_officescombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_officescombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        # TAB 3 - COMING SOON
        # ---

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        self.ui.year_combo.currentIndexChanged.connect(self.change_active_module)
        self.ui.autofillButton.clicked.connect(self.autofill_from_previous_year)
        self.ui.same_params.clicked.connect(self.same_parameters_check)
        # self.ui.reset_button.clicked.connect(self.reset_parameters_to_default)

        # GENERAL
        self.ui.input_birthrate_custom.clicked.connect(self.call_birthrate_custom)
        self.ui.input_deathrate_custom.clicked.connect(self.call_deathrate_custom)
        self.ui.input_migration_custom.clicked.connect(self.call_migration_custom)
        self.ui.input_birthrate_trend.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.input_deathrate_trend.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.input_migration_trend.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.input_pop_summary.clicked.connect(self.display_population_summary)
        self.ui.employ_inputmap.clicked.connect(self.update_employment_stack)
        self.ui.employ_pop.clicked.connect(self.update_employment_stack)
        self.ui.employ_land.clicked.connect(self.update_employment_stack)
        self.ui.employ_pop_roc.clicked.connect(self.enable_disable_employment_stack_widgets)
        self.ui.employ_land_roc.clicked.connect(self.enable_disable_employment_stack_widgets)

        # ACCESSIBILITY
        self.ui.access_general_summary.clicked.connect(self.display_accessibility_summary)
        self.ui.access_roads_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_rail_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_waterways_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_lakes_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_pos_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_poi_include.clicked.connect(self.enable_disable_accessibility_widgets)

        # SUITABILITY
        self.ui.suit_slope_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_gw_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_soil_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_custom1_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_custom2_check.clicked.connect(self.enable_disable_suitability_widgets)

        # ZONING
        self.ui.zoning_move_to_constrained.clicked.connect(self.move_zone_to_constrained)
        self.ui.zoning_move_to_passive.clicked.connect(self.move_zone_to_passive)
        self.ui.zoning_rules_resauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_comauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_indauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_officesauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_reslimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_comlimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_indlimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_officeslimit.clicked.connect(self.enable_disable_zoning_widgets)

        # FOOTER
        self.ui.buttonBox.accepted.connect(self.save_values)

    def adjust_module_img(self):
        """Changes the module's image based on the currently selected tab in the GUI."""
        pass

    def get_dataref_array(self, dataclass, datatype, *args):
        """Retrieves a list of data files loaded into the current scenario for display in the GUI

        :param dataclass: the data class i.e. spatial, temporal, qualitative
        :param datatype: the name that goes with the data class e.g. landuse, population, etc.
        """
        dataref_array = [["(no map selected)"], [""]]  # index 0:filenames, index 1:object_reference
        for dref in self.active_scenario.get_data_reference(dataclass):
            if dref.get_metadata("parent") == datatype:
                if len(args) > 0 and datatype in ["Boundaries", "Water Bodies", "Built Infrastructure", "Overlays"]:
                    if dref.get_metadata("sub") != args[0]:
                        continue
                dataref_array[0].append(dref.get_metadata("filename"))
                dataref_array[1].append(dref.get_data_id())
        return dataref_array

    def pre_fill_parameters(self):
        """Pre-filling method, will set up the module with all values contained in the pre-loaded parameter file or
        settings. This method is called when the Combo box index is changed or a file has been browsed and entered into
        the text box on the GENERALS tab."""
        pass    # [TO DO]

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

    def display_population_summary(self):
        """Opens a summary widget displaying a summary of the population settings entered into the model."""
        pass    # [TO DO]

    def display_accessibility_summary(self):
        """Displays a summary of all the accessibility information entered into the model for the user to gain an
        overview. Opens a dialog window for this."""
        pass

    def update_employment_stack(self):
        """Updates the index of the employment input stack widget."""
        if self.ui.employ_inputmap.isChecked():
            self.ui.employ_stack.setCurrentIndex(0)
        elif self.ui.employ_pop.isChecked():
            self.ui.employ_stack.setCurrentIndex(1)
        else:
            self.ui.employ_stack.setCurrentIndex(2)

    def enable_disable_custom_buttons(self):
        """Enables and disables the custom buttons across the GUI."""
        pass

    def call_birthrate_custom(self):
        """Calls the custom window for filling out a dynamic birth-rate."""
        pass

    def call_deathrate_custom(self):
        """Calls the custom window for filling out a dynamic death-rate."""
        pass

    def call_migration_custom(self):
        """Calls the custom window for filling out a dynamic migration-rate."""
        pass

    def move_zone_to_constrained(self):
        pass

    def move_zone_to_passive(self):
        pass

    def enable_disable_zoning_widgets(self):
        """Scans the zoning list and enables and disables the criteria list accordingly."""
        self.ui.zoning_rules_rescombo.setEnabled(not self.ui.zoning_rules_resauto.isChecked())  # RESIDENTIAL
        self.ui.zoning_rules_reslimit.setEnabled(self.ui.zoning_rules_resauto.isChecked())
        self.ui.zoning_rules_respassive.setEnabled(self.ui.zoning_rules_resauto.isChecked() and
                                                   self.ui.zoning_rules_reslimit.isChecked())
        self.ui.zoning_rules_resundev.setEnabled(self.ui.zoning_rules_resauto.isChecked() and
                                                   self.ui.zoning_rules_reslimit.isChecked())

        self.ui.zoning_rules_comcombo.setEnabled(not self.ui.zoning_rules_comauto.isChecked())  # COMMERCIAL
        self.ui.zoning_rules_comlimit.setEnabled(self.ui.zoning_rules_comauto.isChecked())
        self.ui.zoning_rules_compassive.setEnabled(self.ui.zoning_rules_comauto.isChecked() and
                                                   self.ui.zoning_rules_comlimit.isChecked())
        self.ui.zoning_rules_comundev.setEnabled(self.ui.zoning_rules_comauto.isChecked() and
                                                 self.ui.zoning_rules_comlimit.isChecked())

        self.ui.zoning_rules_indcombo.setEnabled(not self.ui.zoning_rules_indauto.isChecked())  # INDUSTRIAL
        self.ui.zoning_rules_indlimit.setEnabled(self.ui.zoning_rules_indauto.isChecked())
        self.ui.zoning_rules_indpassive.setEnabled(self.ui.zoning_rules_indauto.isChecked() and
                                                   self.ui.zoning_rules_indlimit.isChecked())
        self.ui.zoning_rules_indundev.setEnabled(self.ui.zoning_rules_indauto.isChecked() and
                                                   self.ui.zoning_rules_indlimit.isChecked())

        self.ui.zoning_rules_officescombo.setEnabled(not self.ui.zoning_rules_officesauto.isChecked())  # OFFICES
        self.ui.zoning_rules_officeslimit.setEnabled(self.ui.zoning_rules_officesauto.isChecked())
        self.ui.zoning_rules_officespassive.setEnabled(self.ui.zoning_rules_officesauto.isChecked() and
                                                       self.ui.zoning_rules_officeslimit.isChecked())
        self.ui.zoning_rules_officesundev.setEnabled(self.ui.zoning_rules_officesauto.isChecked() and
                                                     self.ui.zoning_rules_officeslimit.isChecked())
        return True

    def enable_disable_suitability_widgets(self):
        """Scans the suitability list and enables and disables the criteria list accordingly."""
        self.ui.suit_slope_data.setEnabled(self.ui.suit_slope_check.isChecked())        # Slope
        self.ui.suit_slope_weight.setEnabled(self.ui.suit_slope_check.isChecked())
        self.ui.suit_slope_attract.setEnabled(self.ui.suit_slope_check.isChecked())

        self.ui.suit_gw_data.setEnabled(self.ui.suit_gw_check.isChecked())      # Groundwater
        self.ui.suit_gw_weight.setEnabled(self.ui.suit_gw_check.isChecked())
        self.ui.suit_gw_attract.setEnabled(self.ui.suit_gw_check.isChecked())

        self.ui.suit_soil_data.setEnabled(self.ui.suit_soil_check.isChecked())      # Soil
        self.ui.suit_soil_weight.setEnabled(self.ui.suit_soil_check.isChecked())
        self.ui.suit_soil_attract.setEnabled(self.ui.suit_soil_check.isChecked())

        self.ui.suit_custom1_data.setEnabled(self.ui.suit_custom1_check.isChecked())    # Custom1
        self.ui.suit_custom1_weight.setEnabled(self.ui.suit_custom1_check.isChecked())
        self.ui.suit_custom1_attract.setEnabled(self.ui.suit_custom1_check.isChecked())

        self.ui.suit_custom2_data.setEnabled(self.ui.suit_custom2_check.isChecked())    # Custom2
        self.ui.suit_custom2_weight.setEnabled(self.ui.suit_custom2_check.isChecked())
        self.ui.suit_custom2_attract.setEnabled(self.ui.suit_custom2_check.isChecked())
        return True

    def enable_disable_accessibility_widgets(self):
        """Scans the entire accessibility list and enables and disables all respective widgets accordingly."""
        self.ui.access_roads_data.setEnabled(self.ui.access_roads_include.isChecked())      # Roads
        self.ui.access_roads_weight.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_res.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_com.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_ind.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_offices.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_ares.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_acom.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_aind.setEnabled(self.ui.access_roads_include.isChecked())
        self.ui.access_roads_aoffices.setEnabled(self.ui.access_roads_include.isChecked())

        self.ui.access_rail_data.setEnabled(self.ui.access_rail_include.isChecked())        # Rail
        self.ui.access_rail_weight.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_res.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_com.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_ind.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_offices.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_ares.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_acom.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_aind.setEnabled(self.ui.access_rail_include.isChecked())
        self.ui.access_rail_aoffices.setEnabled(self.ui.access_rail_include.isChecked())

        self.ui.access_waterways_data.setEnabled(self.ui.access_waterways_include.isChecked())      # Waterways
        self.ui.access_waterways_weight.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_res.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_com.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_ind.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_offices.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_ares.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_acom.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_aind.setEnabled(self.ui.access_waterways_include.isChecked())
        self.ui.access_waterways_aoffices.setEnabled(self.ui.access_waterways_include.isChecked())

        self.ui.access_lakes_data.setEnabled(self.ui.access_lakes_include.isChecked())      # Lakes
        self.ui.access_lakes_weight.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_res.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_com.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_ind.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_offices.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_ares.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_acom.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_aind.setEnabled(self.ui.access_lakes_include.isChecked())
        self.ui.access_lakes_aoffices.setEnabled(self.ui.access_lakes_include.isChecked())

        self.ui.access_pos_data.setEnabled(self.ui.access_pos_include.isChecked())      # Public Open Space (POS)
        self.ui.access_pos_weight.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_res.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_com.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_ind.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_offices.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_ares.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_acom.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_aind.setEnabled(self.ui.access_pos_include.isChecked())
        self.ui.access_pos_aoffices.setEnabled(self.ui.access_pos_include.isChecked())

        self.ui.access_poi_data.setEnabled(self.ui.access_poi_include.isChecked())      # Points of Interest (POIs)
        self.ui.access_poi_weight.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_res.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_com.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_ind.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_offices.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_ares.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_acom.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_aind.setEnabled(self.ui.access_poi_include.isChecked())
        self.ui.access_poi_aoffices.setEnabled(self.ui.access_poi_include.isChecked())
        return True

    def enable_disable_employment_stack_widgets(self):
        """Enables and disables options in the employment stack widget, mainly the rate of change."""
        self.ui.employ_pop_roc_spin.setEnabled(self.ui.employ_pop_roc.isChecked())
        self.ui.employ_land_roc_spin.setEnabled(self.ui.employ_land_roc.isChecked())
        return True

    def change_active_module(self):
        """Searches for the active module based on the simulation year combo box and updates the GUI."""
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

        # Retrieve the Urbdevelop() Reference corresponding to the current year
        self.module = self.active_scenario.get_module_object("URBDEV", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()
        return True

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""

        self.ui.suit_threshold_stack.setCurrentIndex(int(self.ui.suit_threshold_luccombo.currentIndex()))


        # END OF FILING IN GUI VALUES

        # ENABLE DISABLE FUNCTIONS - GUI MODIFICATION FUNCTIONS
        self.enable_disable_custom_buttons()
        self.enable_disable_employment_stack_widgets()
        self.update_employment_stack()
        self.enable_disable_accessibility_widgets()
        self.enable_disable_suitability_widgets()
        self.enable_disable_zoning_widgets()
        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""

        return True
