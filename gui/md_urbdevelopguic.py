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
from md_urbdevelopgui import Ui_Urbandev_Dialog


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
        if len(simyears) > 1:       # Note that the dt simulation or the Urban Development Module is annual
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
        self.aggregation_methods = ["S", "MS", "MA"]  # Land use aggregation methods
        self.poptrends = ["E", "L", "S", "P", "C"]  # Trend combo boxes for population rates

        # TAB 1 - Land use, population, employment
        # LAND USE
        self.lumaps = self.get_dataref_array("spatial", "Land Use")  # Obtain the data ref array
        # self.lumaps is used later on in other combo boxes too.
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
        self.ui.input_birthrate_trend.currentIndexChanged.connect(self.enable_disable_general_tab_widgets)
        self.ui.input_deathrate_trend.currentIndexChanged.connect(self.enable_disable_general_tab_widgets)
        self.ui.input_migration_trend.currentIndexChanged.connect(self.enable_disable_general_tab_widgets)
        self.ui.input_pop_summary.clicked.connect(self.display_population_summary)
        self.ui.employ_inputmap.clicked.connect(self.update_employment_stack)
        self.ui.employ_pop.clicked.connect(self.update_employment_stack)
        self.ui.employ_land.clicked.connect(self.update_employment_stack)
        self.ui.employ_pop_roc.clicked.connect(self.enable_disable_general_tab_widgets)
        self.ui.employ_land_roc.clicked.connect(self.enable_disable_general_tab_widgets)

        # ACCESSIBILITY
        self.ui.access_general_summary.clicked.connect(self.display_accessibility_summary)
        self.ui.access_roads_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_rail_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_waterways_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_lakes_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_pos_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_poi_include.clicked.connect(self.enable_disable_accessibility_widgets)

        # SUITABILITY
        self.ui.suit_general_summary.clicked.connect(self.display_suitability_summary)
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
        pass    # [TO DO] once I decide on having different images...

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
        pass    # [TO DO]

    def display_suitability_summary(self):
        """Displays a summary of all the suitability information entered into the model for the user to gain an
        overview. Opens a dialog window for this."""
        pass    # [TO DO]

    def update_employment_stack(self):
        """Updates the index of the employment input stack widget."""
        if self.ui.employ_inputmap.isChecked():
            self.ui.employ_stack.setCurrentIndex(0)
        elif self.ui.employ_pop.isChecked():
            self.ui.employ_stack.setCurrentIndex(1)
        else:
            self.ui.employ_stack.setCurrentIndex(2)

    def call_birthrate_custom(self):
        """Calls the custom window for filling out a dynamic birth-rate."""
        pass    # [TO DO]

    def call_deathrate_custom(self):
        """Calls the custom window for filling out a dynamic death-rate."""
        pass    # [TO DO]

    def call_migration_custom(self):
        """Calls the custom window for filling out a dynamic migration-rate."""
        pass    # [TO DO]

    def move_zone_to_constrained(self):
        """Moves a list-widget-item from the passive box to the constrained box, called when
        the arrow button is clicked and there is an active selection."""
        selection = self.ui.zoning_passive_box.selectedItems()
        if len(selection) == 0:
            return True
        for item in selection:
            self.ui.zoning_passive_box.takeItem(self.ui.zoning_passive_box.currentRow())
            self.ui.zoning_constrained_box.addItem(item)

    def move_zone_to_passive(self):
        """Moves a list-widget-item from the constrained box to the passive box, called when
        the arrow button is clicked and there is an active selection."""
        selection = self.ui.zoning_constrained_box.selectedItems()
        if len(selection) == 0:
            return True
        for item in selection:
            self.ui.zoning_constrained_box.takeItem(self.ui.zoning_constrained_box.currentRow())
            self.ui.zoning_passive_box.addItem(item)

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

    def enable_disable_general_tab_widgets(self):
        """Enables and disables all the widgets in the general Tab area depending on what is selected."""
        if self.ui.input_luc_combo.currentIndex() == 0:
            self.ui.input_aggreg_combo.setEnabled(0)
        else:
            self.ui.input_aggreg_combo.setEnabled(1)

        if self.ui.input_birthrate_trend.currentIndex() == 4:
            self.ui.input_birthrate_custom.setEnabled(1)
        else:
            self.ui.input_birthrate_custom.setEnabled(0)

        if self.ui.input_deathrate_trend.currentIndex() == 4:
            self.ui.input_deathrate_custom.setEnabled(1)
        else:
            self.ui.input_deathrate_custom.setEnabled(0)

        if self.ui.input_migration_trend.currentIndex() == 4:
            self.ui.input_migration_custom.setEnabled(1)
        else:
            self.ui.input_migration_custom.setEnabled(0)

        self.ui.employ_pop_roc_spin.setEnabled(int(self.ui.employ_pop_roc.isChecked()))
        self.ui.employ_land_roc_spin.setEnabled(int(self.ui.employ_land_roc.isChecked()))
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
        # TAB 1 - General Tab
        self.ui.basic_cellsize.setValue(int(self.module.get_parameter("cellsize")))
        self.ui.basic_baseyear.setText(str(self.active_scenario.get_metadata("startyear")))
        self.ui.basic_dt.setText(str(self.active_scenario.get_metadata("dt"))+" year(s)")
        self.ui.basic_nhd.setValue(float(self.module.get_parameter("nhd_radius")))
        self.ui.basic_stochastic.setText(str(self.module.get_parameter("alpha")))

        try:    # LAND USE COMBO - retrieve the dataID from module
            self.ui.input_luc_combo.setCurrentIndex(self.lumaps[1].index(self.module.get_parameter("luc_inputmap")))
        except ValueError:
            self.ui.input_luc_combo.setCurrentIndex(0)     # else the map must've been removed, set combo to zero index

        self.ui.input_aggreg_combo.setCurrentIndex(self.aggregation_methods.index(
            self.module.get_parameter("luc_aggregation")))

        try:    # POPULATION COMBO - retrieve the dataID from module
            self.ui.input_pop_combo.setCurrentIndex(self.popmaps[1].index(self.module.get_parameter("pop_inputmap")))
        except ValueError:
            self.ui.input_pop_combo.setCurrentIndex(0)     # else the map must've been removed, set combo to zero index

        self.ui.input_birthrate_spin.setValue(float(self.module.get_parameter("pop_birthrate")))
        self.ui.input_deathrate_spin.setValue(float(self.module.get_parameter("pop_deathrate")))
        self.ui.input_migration_spin.setValue(float(self.module.get_parameter("pop_migration")))

        self.ui.input_birthrate_trend.setCurrentIndex(self.poptrends.index(
            self.module.get_parameter("pop_birthtrend")))
        self.ui.input_deathrate_trend.setCurrentIndex(self.poptrends.index(
            self.module.get_parameter("pop_deathtrend")))
        self.ui.input_migration_trend.setCurrentIndex(self.poptrends.index(
            self.module.get_parameter("pop_migrationtrend")))

        if self.module.get_parameter("employ_datasource") == "I":
            self.ui.employ_inputmap.setChecked(1)
        elif self.module.get_parameter("employ_datasource") == "P":
            self.ui.employ_pop.setChecked(1)
        else:
            self.ui.employ_land.setChecked(1)

        # --- employment STACK 1
        try:    # EMPLOYMENT COMBO - retrieve the dataID from module
            self.ui.employ_inputmap_combo.setCurrentIndex(self.employmaps[1].index(
                self.module.get_parameter("employ_inputmap")))
        except ValueError:
            self.ui.employ_inputmap_combo.setCurrentIndex(0)
        self.ui.employ_inputmap_spin.setValue(float(self.module.get_parameter("employ_inputmaprate")))

        # --- employment STACK 2
        self.ui.employ_pop_com.setValue(float(self.module.get_parameter("employ_pop_comfactor")))
        self.ui.employ_pop_ind.setValue(float(self.module.get_parameter("employ_pop_indfactor")))
        self.ui.employ_pop_office.setValue(float(self.module.get_parameter("employ_pop_officefactor")))
        self.ui.employ_pop_roc.setChecked(int(self.module.get_parameter("employ_pop_rocbool")))
        self.ui.employ_pop_roc_spin.setValue(float(self.module.get_parameter("employ_pop_roc")))

        # --- employment STACK 3
        self.ui.employ_land_com.setValue(float(self.module.get_parameter("employ_land_comfactor")))
        self.ui.employ_land_ind.setValue(float(self.module.get_parameter("employ_land_indfactor")))
        self.ui.employ_land_office.setValue(float(self.module.get_parameter("employ_land_officefactor")))
        self.ui.employ_land_roc.setChecked(int(self.module.get_parameter("employ_land_rocbool")))
        self.ui.employ_land_roc_spin.setValue(float(self.module.get_parameter("employ_land_roc")))

        self.enable_disable_general_tab_widgets()
        self.update_employment_stack()

        # TAB 2 - Spatial Relationships
        # TAB 2.1 - Accessibility
        self.ui.access_export_combined.setChecked(int(self.module.get_parameter("access_export_combined")))
        self.ui.access_export_individual.setChecked(int(self.module.get_parameter("access_export_individual")))

        # Major Arterials and Highways
        self.ui.access_roads_include.setChecked(int(self.module.get_parameter("access_roads_include")))
        self.ui.access_roads_weight.setValue(int(self.module.get_parameter("access_roads_weight")))
        self.ui.access_roads_res.setChecked(int(self.module.get_parameter("access_roads_res")))
        self.ui.access_roads_com.setChecked(int(self.module.get_parameter("access_roads_com")))
        self.ui.access_roads_ind.setChecked(int(self.module.get_parameter("access_roads_ind")))
        self.ui.access_roads_offices.setChecked(int(self.module.get_parameter("access_roads_offices")))
        self.ui.access_roads_ares.setText(str(self.module.get_parameter("access_roads_ares")))
        self.ui.access_roads_acom.setText(str(self.module.get_parameter("access_roads_acom")))
        self.ui.access_roads_aind.setText(str(self.module.get_parameter("access_roads_aind")))
        self.ui.access_roads_aoffices.setText(str(self.module.get_parameter("access_roads_aoffices")))
        try:    # ROADS COMBO BOX
            self.ui.access_roads_data.setCurrentIndex(self.roadmaps[1].index(
                self.module.get_parameter("access_roads_data")))
        except ValueError:
            self.ui.access_roads_data.setCurrentIndex(0)

        # Rail Infrastructure
        self.ui.access_rail_include.setChecked(int(self.module.get_parameter("access_rail_include")))
        self.ui.access_rail_weight.setValue(int(self.module.get_parameter("access_rail_weight")))
        self.ui.access_rail_res.setChecked(int(self.module.get_parameter("access_rail_res")))
        self.ui.access_rail_com.setChecked(int(self.module.get_parameter("access_rail_com")))
        self.ui.access_rail_ind.setChecked(int(self.module.get_parameter("access_rail_ind")))
        self.ui.access_rail_offices.setChecked(int(self.module.get_parameter("access_rail_offices")))
        self.ui.access_rail_ares.setText(str(self.module.get_parameter("access_rail_ares")))
        self.ui.access_rail_acom.setText(str(self.module.get_parameter("access_rail_acom")))
        self.ui.access_rail_aind.setText(str(self.module.get_parameter("access_rail_aind")))
        self.ui.access_rail_aoffices.setText(str(self.module.get_parameter("access_rail_aoffices")))
        # try:  # RAIL COMBO BOX
        #     self.ui.access_rail_data.setCurrentIndex(self.railmaps[1].index(
        #         self.module.get_parameter("access_rail_data")))
        # except ValueError:
        #     self.ui.access_rail_data.setCurrentIndex(0)

        # Major Waterways
        self.ui.access_waterways_include.setChecked(int(self.module.get_parameter("access_waterways_include")))
        self.ui.access_waterways_weight.setValue(int(self.module.get_parameter("access_waterways_weight")))
        self.ui.access_waterways_res.setChecked(int(self.module.get_parameter("access_waterways_res")))
        self.ui.access_waterways_com.setChecked(int(self.module.get_parameter("access_waterways_com")))
        self.ui.access_waterways_ind.setChecked(int(self.module.get_parameter("access_waterways_ind")))
        self.ui.access_waterways_offices.setChecked(int(self.module.get_parameter("access_waterways_offices")))
        self.ui.access_waterways_ares.setText(str(self.module.get_parameter("access_waterways_ares")))
        self.ui.access_waterways_acom.setText(str(self.module.get_parameter("access_waterways_acom")))
        self.ui.access_waterways_aind.setText(str(self.module.get_parameter("access_waterways_aind")))
        self.ui.access_waterways_aoffices.setText(str(self.module.get_parameter("access_waterways_aoffices")))
        try:  # waterways COMBO BOX
            self.ui.access_waterways_data.setCurrentIndex(self.rivermaps[1].index(
                self.module.get_parameter("access_waterways_data")))
        except ValueError:
            self.ui.access_waterways_data.setCurrentIndex(0)

        # Major Water Bodies
        self.ui.access_lakes_include.setChecked(int(self.module.get_parameter("access_lakes_include")))
        self.ui.access_lakes_weight.setValue(int(self.module.get_parameter("access_lakes_weight")))
        self.ui.access_lakes_res.setChecked(int(self.module.get_parameter("access_lakes_res")))
        self.ui.access_lakes_com.setChecked(int(self.module.get_parameter("access_lakes_com")))
        self.ui.access_lakes_ind.setChecked(int(self.module.get_parameter("access_lakes_ind")))
        self.ui.access_lakes_offices.setChecked(int(self.module.get_parameter("access_lakes_offices")))
        self.ui.access_lakes_ares.setText(str(self.module.get_parameter("access_lakes_ares")))
        self.ui.access_lakes_acom.setText(str(self.module.get_parameter("access_lakes_acom")))
        self.ui.access_lakes_aind.setText(str(self.module.get_parameter("access_lakes_aind")))
        self.ui.access_lakes_aoffices.setText(str(self.module.get_parameter("access_lakes_aoffices")))
        try:  # lakes COMBO BOX
            self.ui.access_lakes_data.setCurrentIndex(self.lakemaps[1].index(
                self.module.get_parameter("access_lakes_data")))
        except ValueError:
            self.ui.access_lakes_data.setCurrentIndex(0)

        # Green and Open Spaces
        self.ui.access_pos_include.setChecked(int(self.module.get_parameter("access_pos_include")))
        self.ui.access_pos_weight.setValue(int(self.module.get_parameter("access_pos_weight")))
        self.ui.access_pos_res.setChecked(int(self.module.get_parameter("access_pos_res")))
        self.ui.access_pos_com.setChecked(int(self.module.get_parameter("access_pos_com")))
        self.ui.access_pos_ind.setChecked(int(self.module.get_parameter("access_pos_ind")))
        self.ui.access_pos_offices.setChecked(int(self.module.get_parameter("access_pos_offices")))
        self.ui.access_pos_ares.setText(str(self.module.get_parameter("access_pos_ares")))
        self.ui.access_pos_acom.setText(str(self.module.get_parameter("access_pos_acom")))
        self.ui.access_pos_aind.setText(str(self.module.get_parameter("access_pos_aind")))
        self.ui.access_pos_aoffices.setText(str(self.module.get_parameter("access_pos_aoffices")))
        try:  # pos COMBO BOX
            self.ui.access_pos_data.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("access_pos_data")))
        except ValueError:
            self.ui.access_pos_data.setCurrentIndex(0)

        # Points of Interest (POIs)
        self.ui.access_poi_include.setChecked(int(self.module.get_parameter("access_poi_include")))
        self.ui.access_poi_weight.setValue(int(self.module.get_parameter("access_poi_weight")))
        self.ui.access_poi_res.setChecked(int(self.module.get_parameter("access_poi_res")))
        self.ui.access_poi_com.setChecked(int(self.module.get_parameter("access_poi_com")))
        self.ui.access_poi_ind.setChecked(int(self.module.get_parameter("access_poi_ind")))
        self.ui.access_poi_offices.setChecked(int(self.module.get_parameter("access_poi_offices")))
        self.ui.access_poi_ares.setText(str(self.module.get_parameter("access_poi_ares")))
        self.ui.access_poi_acom.setText(str(self.module.get_parameter("access_poi_acom")))
        self.ui.access_poi_aind.setText(str(self.module.get_parameter("access_poi_aind")))
        self.ui.access_poi_aoffices.setText(str(self.module.get_parameter("access_poi_aoffices")))
        try:  # poi COMBO BOX
            self.ui.access_poi_data.setCurrentIndex(self.localitymaps[1].index(
                self.module.get_parameter("access_poi_data")))
        except ValueError:
            self.ui.access_poi_data.setCurrentIndex(0)

        self.enable_disable_accessibility_widgets()

        # TAB 2.2 - Suitability
        self.ui.suit_export_maps.setChecked(int(self.module.get_parameter("suit_export")))

        # Slope
        self.ui.suit_slope_check.setChecked(int(self.module.get_parameter("suit_slope_include")))
        self.ui.suit_slope_weight.setValue(int(self.module.get_parameter("suit_slope_weight")))
        self.ui.suit_slope_attract.setChecked(int(self.module.get_parameter("suit_slope_attract")))
        try:    # SLOPE COMBO
            self.ui.suit_slope_data.setCurrentIndex(self.elevmaps[1].index(
                self.module.get_parameter("suit_slope_data")))
        except ValueError:
            self.ui.suit_slope_data.setCurrentIndex(0)

        # Groundwater Depth
        self.ui.suit_gw_check.setChecked(int(self.module.get_parameter("suit_gw_include")))
        self.ui.suit_gw_weight.setValue(int(self.module.get_parameter("suit_gw_weight")))
        self.ui.suit_gw_attract.setChecked(int(self.module.get_parameter("suit_gw_attract")))
        # try:  # gw COMBO
        #     self.ui.suit_gw_data.setCurrentIndex(self.[1].index(
        #         self.module.get_parameter("suit_gw_data")))
        # except ValueError:
        #     self.ui.suit_gw_data.setCurrentIndex(0)

        # Soil
        self.ui.suit_soil_check.setChecked(int(self.module.get_parameter("suit_soil_include")))
        self.ui.suit_soil_weight.setValue(int(self.module.get_parameter("suit_soil_weight")))
        self.ui.suit_soil_attract.setChecked(int(self.module.get_parameter("suit_soil_attract")))
        # try:  # soil COMBO
        #     self.ui.suit_soil_data.setCurrentIndex(self.soilmaps[1].index(
        #         self.module.get_parameter("suit_soil_data")))
        # except ValueError:
        #     self.ui.suit_soil_data.setCurrentIndex(0)

        # Custom 1
        self.ui.suit_custom1_check.setChecked(int(self.module.get_parameter("suit_custom1_include")))
        self.ui.suit_custom1_weight.setValue(int(self.module.get_parameter("suit_custom1_weight")))
        self.ui.suit_custom1_attract.setChecked(int(self.module.get_parameter("suit_custom1_attract")))
        # try:  # custom1 COMBO
        #     self.ui.suit_custom1_data.setCurrentIndex(self.custommaps[1].index(
        #         self.module.get_parameter("suit_custom1_data")))
        # except ValueError:
        #     self.ui.suit_custom1_data.setCurrentIndex(0)

        # Custom 2
        self.ui.suit_custom2_check.setChecked(int(self.module.get_parameter("suit_custom2_include")))
        self.ui.suit_custom2_weight.setValue(int(self.module.get_parameter("suit_custom2_weight")))
        self.ui.suit_custom2_attract.setChecked(int(self.module.get_parameter("suit_custom2_attract")))
        # try:  # custom2 COMBO
        #     self.ui.suit_custom2_data.setCurrentIndex(self.custommaps[1].index(
        #         self.module.get_parameter("suit_custom2_data")))
        # except ValueError:
        #     self.ui.suit_custom2_data.setCurrentIndex(0)

        self.enable_disable_suitability_widgets()
        self.ui.suit_threshold_stack.setCurrentIndex(int(self.ui.suit_threshold_luccombo.currentIndex()))

        # TAB 2.3 - Zoning
        self.ui.zoning_export.setChecked(int(self.module.get_parameter("zoning_export")))

        try:    # ZONING WATER BODIES COMBO BOX
            self.ui.zoning_constraints_water_combo.setCurrentIndex(self.lakemaps[1].index(
                self.module.get_parameter("zoning_constraint_water")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)

        # Passive and Constrained Land Uses
        # Fill out the list widget
        lunames = ubglobals.LANDUSENAMES
        self.ui.zoning_passive_box.clear()
        for lu_id in self.module.get_parameter("zoning_passive_luc"):
            a = QtWidgets.QListWidgetItem()
            a.setText(lunames[int(lu_id)])
            self.ui.zoning_passive_box.addItem(a)
        self.ui.zoning_constrained_box.clear()
        for lu_id in self.module.get_parameter("zoning_constrained_luc"):
            a = QtWidgets.QListWidgetItem()
            a.setText(lunames[int(lu_id)])
            self.ui.zoning_constrained_box.addItem(a)

        try:    # ZONING RESIDENTIAL COMBO
            self.ui.zoning_rules_rescombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_resmap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_resauto.setChecked(self.module.get_parameter("zoning_rules_resauto"))
        self.ui.zoning_rules_reslimit.setChecked(self.module.get_parameter("zoning_rules_reslimit"))
        self.ui.zoning_rules_respassive.setChecked(self.module.get_parameter("zoning_rules_respassive"))
        self.ui.zoning_rules_resundev.setChecked(self.module.get_parameter("zoning_rules_resundev"))

        try:    # ZONING COMMERCIAL COMBO
            self.ui.zoning_rules_comcombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_commap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_comauto.setChecked(self.module.get_parameter("zoning_rules_comauto"))
        self.ui.zoning_rules_comlimit.setChecked(self.module.get_parameter("zoning_rules_comlimit"))
        self.ui.zoning_rules_compassive.setChecked(self.module.get_parameter("zoning_rules_compassive"))
        self.ui.zoning_rules_comundev.setChecked(self.module.get_parameter("zoning_rules_comundev"))

        try:    # ZONING INDUSTRIAL COMBO
            self.ui.zoning_rules_indcombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_indmap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_indauto.setChecked(self.module.get_parameter("zoning_rules_indauto"))
        self.ui.zoning_rules_indlimit.setChecked(self.module.get_parameter("zoning_rules_indlimit"))
        self.ui.zoning_rules_indpassive.setChecked(self.module.get_parameter("zoning_rules_indpassive"))
        self.ui.zoning_rules_indundev.setChecked(self.module.get_parameter("zoning_rules_indundev"))

        try:    # ZONING officesIDENTIAL COMBO
            self.ui.zoning_rules_officescombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_officesmap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_officesauto.setChecked(self.module.get_parameter("zoning_rules_officesauto"))
        self.ui.zoning_rules_officeslimit.setChecked(self.module.get_parameter("zoning_rules_officeslimit"))
        self.ui.zoning_rules_officespassive.setChecked(self.module.get_parameter("zoning_rules_officespassive"))
        self.ui.zoning_rules_officesundev.setChecked(self.module.get_parameter("zoning_rules_officesundev"))

        self.enable_disable_zoning_widgets()

        # TAB 3 - Neighbourhood Effect

        # END OF FILING IN GUI VALUES
        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        # TAB 1 - GENERAL
        self.module.set_parameter("cellsize", int(self.ui.basic_cellsize.value()))
        self.module.set_parameter("nhd_radius", float(self.ui.basic_nhd.value()))
        self.module.set_parameter("alpha", float(self.ui.basic_stochastic.text()))

        self.module.set_parameter("luc_inputmap", self.lumaps[1][self.ui.input_luc_combo.currentIndex()])
        self.module.set_parameter("luc_aggregation",
                                  self.aggregation_methods[self.ui.input_aggreg_combo.currentIndex()])
        self.module.set_parameter("pop_inputmap", self.popmaps[1][self.ui.input_pop_combo.currentIndex()])
        self.module.set_parameter("pop_birthrate", float(self.ui.input_birthrate_spin.value()))
        self.module.set_parameter("pop_birthtrend", self.poptrends[self.ui.input_birthrate_trend.currentIndex()])
        self.module.set_parameter("pop_deathrate", float(self.ui.input_deathrate_spin.value()))
        self.module.set_parameter("pop_deathtrend", self.poptrends[self.ui.input_deathrate_trend.currentIndex()])
        self.module.set_parameter("pop_migration", float(self.ui.input_migration_spin.value()))
        self.module.set_parameter("pop_migrationtrend", self.poptrends[self.ui.input_migration_trend.currentIndex()])

        if self.ui.employ_inputmap.isChecked():
            self.module.set_parameter("employ_datasource", "I")
        elif self.ui.employ_pop.isChecked():
            self.module.set_parameter("employ_datasource", "P")
        else:
            self.module.set_parameter("employ_datasource", "L")

        self.module.set_parameter("employ_inputmap", self.employmaps[1][self.ui.employ_inputmap_combo.currentIndex()])
        self.module.set_parameter("employ_inputmaprate", float(self.ui.employ_inputmap_spin.value()))

        self.module.set_parameter("employ_pop_comfactor", float(self.ui.employ_pop_com.value()))
        self.module.set_parameter("employ_pop_indfactor", float(self.ui.employ_pop_ind.value()))
        self.module.set_parameter("employ_pop_officefactor", float(self.ui.employ_pop_office.value()))
        self.module.set_parameter("employ_pop_rocbool", int(self.ui.employ_pop_roc.isChecked()))
        self.module.set_parameter("employ_pop_roc", float(self.ui.employ_pop_roc_spin.value()))

        self.module.set_parameter("employ_land_comfactor", float(self.ui.employ_pop_com.value()))
        self.module.set_parameter("employ_land_indfactor", float(self.ui.employ_pop_ind.value()))
        self.module.set_parameter("employ_land_officefactor", float(self.ui.employ_pop_office.value()))
        self.module.set_parameter("employ_land_rocbool", int(self.ui.employ_pop_roc.isChecked()))
        self.module.set_parameter("employ_land_roc", float(self.ui.employ_pop_roc_spin.value()))

        # TAB 2 - 2.1 - ACCESSIBILITY
        self.module.set_parameter("access_export_combined", int(self.ui.access_export_combined.isChecked()))
        self.module.set_parameter("access_export_individual", int(self.ui.access_export_individual.isChecked()))

        # Accessibility to Roads
        self.module.set_parameter("access_roads_include", int(self.ui.access_roads_include.isChecked()))
        self.module.set_parameter("access_roads_data", self.roadmaps[1][self.ui.access_roads_data.currentIndex()])
        self.module.set_parameter("access_roads_weight", self.ui.access_roads_weight.value())
        self.module.set_parameter("access_roads_res", int(self.ui.access_roads_res.isChecked()))
        self.module.set_parameter("access_roads_com", int(self.ui.access_roads_com.isChecked()))
        self.module.set_parameter("access_roads_ind", int(self.ui.access_roads_ind.isChecked()))
        self.module.set_parameter("access_roads_offices", int(self.ui.access_roads_offices.isChecked()))
        self.module.set_parameter("access_roads_ares", float(self.ui.access_roads_ares.text()))
        self.module.set_parameter("access_roads_acom", float(self.ui.access_roads_acom.text()))
        self.module.set_parameter("access_roads_aind", float(self.ui.access_roads_aind.text()))
        self.module.set_parameter("access_roads_aoffices", float(self.ui.access_roads_aoffices.text()))

        # Accessibility to Rail
        self.module.set_parameter("access_rail_include", int(self.ui.access_rail_include.isChecked()))
        # self.module.set_parameter("access_rail_data", self.ui.access_rail_data.currentText())
        self.module.set_parameter("access_rail_weight", self.ui.access_rail_weight.value())
        self.module.set_parameter("access_rail_res", int(self.ui.access_rail_res.isChecked()))
        self.module.set_parameter("access_rail_com", int(self.ui.access_rail_com.isChecked()))
        self.module.set_parameter("access_rail_ind", int(self.ui.access_rail_ind.isChecked()))
        self.module.set_parameter("access_rail_offices", int(self.ui.access_rail_offices.isChecked()))
        self.module.set_parameter("access_rail_ares", float(self.ui.access_rail_ares.text()))
        self.module.set_parameter("access_rail_acom", float(self.ui.access_rail_acom.text()))
        self.module.set_parameter("access_rail_aind", float(self.ui.access_rail_aind.text()))
        self.module.set_parameter("access_rail_aoffices", float(self.ui.access_rail_aoffices.text()))

        # Accessibility to Waterways
        self.module.set_parameter("access_waterways_include", int(self.ui.access_waterways_include.isChecked()))
        self.module.set_parameter("access_waterways_data",
                                  self.rivermaps[1][self.ui.access_waterways_data.currentIndex()])
        self.module.set_parameter("access_waterways_weight", self.ui.access_waterways_weight.value())
        self.module.set_parameter("access_waterways_res", int(self.ui.access_waterways_res.isChecked()))
        self.module.set_parameter("access_waterways_com", int(self.ui.access_waterways_com.isChecked()))
        self.module.set_parameter("access_waterways_ind", int(self.ui.access_waterways_ind.isChecked()))
        self.module.set_parameter("access_waterways_offices", int(self.ui.access_waterways_offices.isChecked()))
        self.module.set_parameter("access_waterways_ares", float(self.ui.access_waterways_ares.text()))
        self.module.set_parameter("access_waterways_acom", float(self.ui.access_waterways_acom.text()))
        self.module.set_parameter("access_waterways_aind", float(self.ui.access_waterways_aind.text()))
        self.module.set_parameter("access_waterways_aoffices", float(self.ui.access_waterways_aoffices.text()))

        # Accessibility to Lakes
        self.module.set_parameter("access_lakes_include", int(self.ui.access_lakes_include.isChecked()))
        self.module.set_parameter("access_lakes_data", self.lakemaps[1][self.ui.access_lakes_data.currentIndex()])
        self.module.set_parameter("access_lakes_weight", self.ui.access_lakes_weight.value())
        self.module.set_parameter("access_lakes_res", int(self.ui.access_lakes_res.isChecked()))
        self.module.set_parameter("access_lakes_com", int(self.ui.access_lakes_com.isChecked()))
        self.module.set_parameter("access_lakes_ind", int(self.ui.access_lakes_ind.isChecked()))
        self.module.set_parameter("access_lakes_offices", int(self.ui.access_lakes_offices.isChecked()))
        self.module.set_parameter("access_lakes_ares", float(self.ui.access_lakes_ares.text()))
        self.module.set_parameter("access_lakes_acom", float(self.ui.access_lakes_acom.text()))
        self.module.set_parameter("access_lakes_aind", float(self.ui.access_lakes_aind.text()))
        self.module.set_parameter("access_lakes_aoffices", float(self.ui.access_lakes_aoffices.text()))

        # Accessibility to Public Open Space (POS)
        self.module.set_parameter("access_pos_include", int(self.ui.access_pos_include.isChecked()))
        self.module.set_parameter("access_pos_data", self.lumaps[1][self.ui.access_pos_data.currentIndex()])
        self.module.set_parameter("access_pos_weight", self.ui.access_pos_weight.value())
        self.module.set_parameter("access_pos_res", int(self.ui.access_pos_res.isChecked()))
        self.module.set_parameter("access_pos_com", int(self.ui.access_pos_com.isChecked()))
        self.module.set_parameter("access_pos_ind", int(self.ui.access_pos_ind.isChecked()))
        self.module.set_parameter("access_pos_offices", int(self.ui.access_pos_offices.isChecked()))
        self.module.set_parameter("access_pos_ares", float(self.ui.access_pos_ares.text()))
        self.module.set_parameter("access_pos_acom", float(self.ui.access_pos_acom.text()))
        self.module.set_parameter("access_pos_aind", float(self.ui.access_pos_aind.text()))
        self.module.set_parameter("access_pos_aoffices", float(self.ui.access_pos_aoffices.text()))

        # Accessibility to Points of Interest (POIs)
        self.module.set_parameter("access_poi_include", int(self.ui.access_poi_include.isChecked()))
        self.module.set_parameter("access_poi_data", self.localitymaps[1][self.ui.access_poi_data.currentIndex()])
        self.module.set_parameter("access_poi_weight", self.ui.access_poi_weight.value())
        self.module.set_parameter("access_poi_res", int(self.ui.access_poi_res.isChecked()))
        self.module.set_parameter("access_poi_com", int(self.ui.access_poi_com.isChecked()))
        self.module.set_parameter("access_poi_ind", int(self.ui.access_poi_ind.isChecked()))
        self.module.set_parameter("access_poi_offices", int(self.ui.access_poi_offices.isChecked()))
        self.module.set_parameter("access_poi_ares", float(self.ui.access_poi_ares.text()))
        self.module.set_parameter("access_poi_acom", float(self.ui.access_poi_acom.text()))
        self.module.set_parameter("access_poi_aind", float(self.ui.access_poi_aind.text()))
        self.module.set_parameter("access_poi_aoffices", float(self.ui.access_poi_aoffices.text()))

        # TAB 2 - 2.2 Suitability
        self.module.set_parameter("suit_export", int(self.ui.suit_export_maps.isChecked()))

        self.module.set_parameter("suit_slope_include", int(self.ui.suit_slope_check.isChecked()))
        self.module.set_parameter("suit_slope_data", self.elevmaps[1][self.ui.suit_slope_data.currentIndex()])
        self.module.set_parameter("suit_slope_weight", int(self.ui.suit_slope_weight.value()))
        self.module.set_parameter("suit_slope_attract", int(self.ui.suit_slope_attract.isChecked()))

        self.module.set_parameter("suit_gw_include", int(self.ui.suit_gw_check.isChecked()))
        # self.module.set_parameter("suit_gw_data", self.ui.suit_gw_data.currentText())
        self.module.set_parameter("suit_gw_weight", int(self.ui.suit_gw_weight.value()))
        self.module.set_parameter("suit_gw_attract", int(self.ui.suit_gw_attract.isChecked()))

        self.module.set_parameter("suit_soil_include", int(self.ui.suit_soil_check.isChecked()))
        # self.module.set_parameter("suit_soil_data", self.ui.suit_soil_data.currentText())
        self.module.set_parameter("suit_soil_weight", int(self.ui.suit_soil_weight.value()))
        self.module.set_parameter("suit_soil_attract", int(self.ui.suit_soil_attract.isChecked()))

        self.module.set_parameter("suit_custom1_include", int(self.ui.suit_custom1_check.isChecked()))
        # self.module.set_parameter("suit_custom1_data", self.ui.suit_custom1_data.currentText())
        self.module.set_parameter("suit_custom1_weight", int(self.ui.suit_custom1_weight.value()))
        self.module.set_parameter("suit_custom1_attract", int(self.ui.suit_custom1_attract.isChecked()))

        self.module.set_parameter("suit_custom2_include", int(self.ui.suit_custom2_check.isChecked()))
        # self.module.set_parameter("suit_custom2_data", self.ui.suit_custom2_data.currentText())
        self.module.set_parameter("suit_custom2_weight", int(self.ui.suit_custom2_weight.value()))
        self.module.set_parameter("suit_custom2_attract", int(self.ui.suit_custom2_attract.isChecked()))

        # TAB 2 - 2.3 Zoning
        self.module.set_parameter("zoning_export", int(self.ui.zoning_export.isChecked()))
        self.module.set_parameter("zoning_constraint_water",
                                  self.lakemaps[1][self.ui.zoning_constraints_water_combo.currentIndex()])

        # Passive and Constrained uses
        lunames = ubglobals.LANDUSENAMES
        zoning_passive_luc = []
        for rows in range(self.ui.zoning_passive_box.count()):
            item = self.ui.zoning_passive_box.item(rows)
            zoning_passive_luc.append(lunames.index(item.text()))

        zoning_constrained_luc = []
        for rows in range(self.ui.zoning_constrained_box.count()):
            item = self.ui.zoning_constrained_box.item(rows)
            zoning_constrained_luc.append(lunames.index(item.text()))

        self.module.set_parameter("zoning_passive_luc", zoning_passive_luc)
        self.module.set_parameter("zoning_constrained_luc", zoning_constrained_luc)

        self.module.set_parameter("zoning_rules_resmap", self.lumaps[1][self.ui.zoning_rules_rescombo.currentIndex()])
        self.module.set_parameter("zoning_rules_resauto", int(self.ui.zoning_rules_resauto.isChecked()))
        self.module.set_parameter("zoning_rules_reslimit", int(self.ui.zoning_rules_reslimit.isChecked()))
        self.module.set_parameter("zoning_rules_respassive", int(self.ui.zoning_rules_respassive.isChecked()))
        self.module.set_parameter("zoning_rules_resundev", int(self.ui.zoning_rules_resundev.isChecked()))

        self.module.set_parameter("zoning_rules_commap", self.lumaps[1][self.ui.zoning_rules_comcombo.currentIndex()])
        self.module.set_parameter("zoning_rules_comauto", int(self.ui.zoning_rules_comauto.isChecked()))
        self.module.set_parameter("zoning_rules_comlimit", int(self.ui.zoning_rules_comlimit.isChecked()))
        self.module.set_parameter("zoning_rules_compassive", int(self.ui.zoning_rules_compassive.isChecked()))
        self.module.set_parameter("zoning_rules_comundev", int(self.ui.zoning_rules_comundev.isChecked()))

        self.module.set_parameter("zoning_rules_indmap", self.lumaps[1][self.ui.zoning_rules_indcombo.currentIndex()])
        self.module.set_parameter("zoning_rules_indauto", int(self.ui.zoning_rules_indauto.isChecked()))
        self.module.set_parameter("zoning_rules_indlimit", int(self.ui.zoning_rules_indlimit.isChecked()))
        self.module.set_parameter("zoning_rules_indpassive", int(self.ui.zoning_rules_indpassive.isChecked()))
        self.module.set_parameter("zoning_rules_indundev", int(self.ui.zoning_rules_indundev.isChecked()))

        self.module.set_parameter("zoning_rules_officesmap",
                                  self.lumaps[1][self.ui.zoning_rules_officescombo.currentIndex()])
        self.module.set_parameter("zoning_rules_officesauto", int(self.ui.zoning_rules_officesauto.isChecked()))
        self.module.set_parameter("zoning_rules_officeslimit", int(self.ui.zoning_rules_officeslimit.isChecked()))
        self.module.set_parameter("zoning_rules_officespassive", int(self.ui.zoning_rules_officespassive.isChecked()))
        self.module.set_parameter("zoning_rules_officesundev", int(self.ui.zoning_rules_officesundev.isChecked()))
        return True
