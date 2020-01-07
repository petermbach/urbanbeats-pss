"""
@file   md_urbdevelopguic.py
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
import os

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ublibs.ubdatatypes as ubdatatypes

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from .md_urbdevelopgui import Ui_Urbandev_Dialog
from .md_subgui_influence import Ui_InfluenceFunctionDialog


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
        # MUNICIPALITIES
        self.municipalmaps = self.get_dataref_array("spatial", "Boundaries", "Geopolitical")
        self.ui.input_lga_combo.clear()
        [self.ui.input_lga_combo.addItem(str(self.municipalmaps[0][i])) for i in range(len(self.municipalmaps[0]))]

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
        self.railmaps = self.get_dataref_array("spatial", "Built Infrastructure", "Rail Network")
        self.ui.access_rail_data.clear()    # Clear the combo box first before setting it up
        [self.ui.access_rail_data.addItem(str(self.railmaps[0][i])) for i in range(len(self.railmaps[0]))]

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
        self.localitymaps = self.get_dataref_array("spatial", "Locality Maps")  # Obtain the data ref array
        self.ui.access_poi_data.clear()  # Clear the combo box first before setting it up
        [self.ui.access_poi_data.addItem(str(self.localitymaps[0][i])) for i in range(len(self.localitymaps[0]))]

        # PUBLIC TRANSPORT HUBS
        self.localitymaps = self.get_dataref_array("spatial", "Locality Maps")  # Obtain the data ref array
        self.ui.access_pth_data.clear()  # Clear the combo box first before setting it up
        [self.ui.access_pth_data.addItem(str(self.localitymaps[0][i])) for i in range(len(self.localitymaps[0]))]

        # TAB 2 SUITABILITY - Elevation, Groundwater Depth, Soil Infiltration Rate, Custom Criteria
        # SLOPE
        self.elevmaps = self.get_dataref_array("spatial", "Elevation")
        self.ui.suit_slope_data.clear()
        [self.ui.suit_slope_data.addItem(str(self.elevmaps[0][i])) for i in range(len(self.elevmaps[0]))]
        self.ui.suit_aspect_data.clear()
        [self.ui.suit_aspect_data.addItem(str(self.elevmaps[0][i])) for i in range(len(self.elevmaps[0]))]

        self.soilmaps = self.get_dataref_array("spatial", "Soil")
        self.ui.suit_soil_data.clear()
        [self.ui.suit_soil_data.addItem(str(self.soilmaps[0][i])) for i in range(len(self.soilmaps[0]))]

        self.gwmaps = self.get_dataref_array("spatial", "Overlays", "Groundwater")
        self.ui.suit_gw_data.clear()
        [self.ui.suit_gw_data.addItem(str(self.gwmaps[0][i])) for i in range(len(self.gwmaps[0]))]

        self.overlaymaps = self.get_dataref_array("spatial", "Overlays")  # Obtain the data ref array
        self.ui.suit_custom_data.clear()
        [self.ui.suit_custom_data.addItem(str(self.overlaymaps[0][i])) for i in range(len(self.overlaymaps[0]))]

        # TAB 3 ZONING - Water bodies, residential zoning maps
        # GENERAL ZONING RULES FOR ACTIVE LAND USES
        self.ui.zoning_rules_rescombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_rescombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]
        self.ui.zoning_rules_comcombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_comcombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]
        self.ui.zoning_rules_indcombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_indcombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]
        self.ui.zoning_rules_officescombo.clear()  # Clear the combo box first before setting it up
        [self.ui.zoning_rules_officescombo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        # SPECIFIC PLANNING CONSTRAINTS
        self.ui.zoning_constraints_water_combo.clear()
        [self.ui.zoning_constraints_water_combo.addItem(str(self.lakemaps[0][i])) for i in range(len(self.lakemaps[0]))]

        self.ui.zoning_constraints_heritage_combo.clear()
        [self.ui.zoning_constraints_heritage_combo.addItem(str(self.overlaymaps[0][i]))
         for i in range(len(self.overlaymaps[0]))]

        self.ui.zoning_constraints_public_combo.clear()
        [self.ui.zoning_constraints_public_combo.addItem(str(self.overlaymaps[0][i]))
         for i in range(len(self.overlaymaps[0]))]

        self.ui.zoning_constraints_enviro_combo.clear()
        [self.ui.zoning_constraints_enviro_combo.addItem(str(self.overlaymaps[0][i]))
         for i in range(len(self.overlaymaps[0]))]

        self.ui.zoning_constraints_flood_combo.clear()
        [self.ui.zoning_constraints_flood_combo.addItem(str(self.overlaymaps[0][i]))
         for i in range(len(self.overlaymaps[0]))]

        self.ui.zoning_constraints_custom_combo.clear()
        [self.ui.zoning_constraints_custom_combo.addItem(str(self.overlaymaps[0][i]))
         for i in range(len(self.overlaymaps[0]))]

        # TAB 4 - NEIGHBOURHOOD INTERACTION
        self.setup_if_function_select_combo()
        self.ifo_selection = []

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        self.ui.year_combo.currentIndexChanged.connect(self.change_active_module)
        self.ui.autofillButton.clicked.connect(self.autofill_from_previous_year)
        self.ui.same_params.clicked.connect(self.same_parameters_check)
        # self.ui.reset_button.clicked.connect(self.reset_parameters_to_default)

        # GENERAL
        self.ui.input_lga_combo.currentIndexChanged.connect(self.enable_disable_general_tab_widgets)
        self.ui.input_luc_combo.currentIndexChanged.connect(self.enable_disable_general_tab_widgets)
        self.ui.input_pop_combo.currentIndexChanged.connect(self.enable_disable_general_tab_widgets)
        self.ui.zoning_move_to_constrained.clicked.connect(self.move_zone_to_constrained)
        self.ui.zoning_move_to_passive.clicked.connect(self.move_zone_to_passive)
        self.ui.employ_inputmap.clicked.connect(self.update_employment_stack)
        self.ui.employ_pop.clicked.connect(self.update_employment_stack)
        self.ui.employ_land.clicked.connect(self.update_employment_stack)

        # ACCESSIBILITY
        self.ui.access_general_summary.clicked.connect(self.display_accessibility_summary)
        self.ui.access_roads_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_rail_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_waterways_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_lakes_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_pos_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_poi_include.clicked.connect(self.enable_disable_accessibility_widgets)
        self.ui.access_pth_include.clicked.connect(self.enable_disable_accessibility_widgets)

        # SUITABILITY
        self.ui.suit_general_summary.clicked.connect(self.display_suitability_summary)
        self.ui.suit_slope_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_aspect_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_slope_data.currentIndexChanged.connect(self.sync_aspect_to_slope_combobox)
        self.ui.suit_aspect_data.currentIndexChanged.connect(self.sync_slope_to_aspect_combobox)
        self.ui.suit_gw_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_soil_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.suit_custom_check.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.slope_res_slider.valueChanged.connect(self.update_suitability_sliders_slope)
        self.ui.slope_com_slider.valueChanged.connect(self.update_suitability_sliders_slope)
        self.ui.slope_ind_slider.valueChanged.connect(self.update_suitability_sliders_slope)
        self.ui.slope_orc_slider.valueChanged.connect(self.update_suitability_sliders_slope)
        self.ui.gw_res_slider.valueChanged.connect(self.update_suitability_sliders_gw)
        self.ui.gw_com_slider.valueChanged.connect(self.update_suitability_sliders_gw)
        self.ui.gw_ind_slider.valueChanged.connect(self.update_suitability_sliders_gw)
        self.ui.gw_orc_slider.valueChanged.connect(self.update_suitability_sliders_gw)
        self.ui.slope_include_midpoints.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.gw_include_midpoints.clicked.connect(self.enable_disable_suitability_widgets)
        self.ui.custom_include_midpoints.clicked.connect(self.enable_disable_suitability_widgets)

        # ZONING
        self.ui.zoning_rules_resauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_comauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_indauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_officesauto.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_reslimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_comlimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_indlimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_rules_officeslimit.clicked.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_constraints_heritage_combo.currentIndexChanged.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_constraints_public_combo.currentIndexChanged.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_constraints_enviro_combo.currentIndexChanged.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_constraints_flood_combo.currentIndexChanged.connect(self.enable_disable_zoning_widgets)
        self.ui.zoning_constraints_custom_combo.currentIndexChanged.connect(self.enable_disable_zoning_widgets)

        # NEIGHBOURHOOD EFFECT
        self.ui.functionselection_add.clicked.connect(self.add_if_function_to_table)
        self.ui.functionselect_view.clicked.connect(lambda: self.view_selectedfunction("combo"))
        self.ui.nhd_create_button.clicked.connect(self.open_if_function_dialog)
        self.ui.nhd_view_button.clicked.connect(lambda: self.view_selectedfunction("table"))
        self.ui.nhd_remove_button.clicked.connect(self.remove_table_selection)
        self.ui.nhd_clear_button.clicked.connect(self.clear_if_table)

        # URBAN DYNAMICS
        self.ui.pop_method_function.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.pop_method_rate.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.employ_rate_ind_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.employ_rate_orc_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.res_maxdens_auto.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.com_maxdens_auto.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.ind_maxdens_auto.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.orc_maxdens_auto.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.pg_penalty_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.pg_provision_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.pg_provision_current_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.ref_penalty_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.ref_provision_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)
        self.ui.ref_provision_current_check.clicked.connect(self.enable_disable_dynamics_tab_widgets)

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

    def clear_if_table(self):
        """Clears the entire Influence Function Table. Does not update the module parameter yet."""
        self.ifo_selection = []
        self.ui.nhd_table.setRowCount(0)

    def setup_if_function_select_combo(self):
        """Sets up the if_functions combo box. Called also when the influence function creation dialog is closed, while
        editing module parameters."""
        self.if_functions = self.simulation.get_all_function_objects_of_type("IF")
        self.ui.functionselect_combo.clear()
        self.ui.functionselect_combo.addItem("(no function selected)")
        [self.ui.functionselect_combo.addItem(str(self.if_functions[i].get_function_name()))
         for i in range(len(self.if_functions))]
        self.ui.functionselect_combo.setCurrentIndex(0)

    def remove_table_selection(self):
        """Removes the current row in the table."""
        ifo_id = self.ui.nhd_table.item(self.ui.nhd_table.currentRow(), 0).text()
        self.ifo_selection.pop(self.ifo_selection.index(ifo_id))
        self.ui.nhd_table.removeRow(self.ui.nhd_table.currentRow())

    def add_if_function_to_table(self):
        """Adds the current IF function in the combo box to the table, writes the relevant details as well to table
        columns."""
        if self.ui.functionselect_combo.currentIndex() in [0, -1]:      # Check that we are actually adding a function
            return True # DO Nothing
        ifo = self.if_functions[self.ui.functionselect_combo.currentIndex()-1]
        if ifo.get_id() in self.ifo_selection:      # Check if the function already exists in the scenario.
            prompt_msg = "Influence Function already added!"
            QtWidgets.QMessageBox.warning(self, 'Error', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        luabbr = str(ifo.origin_landuse)+" -> "+str(ifo.target_landuse)
        metadata = [ifo.get_id(), ifo.get_function_name(), luabbr, str(ifo.get_x_range()), str(ifo.get_y_range())]
        print(metadata)
        self.ifo_selection.append(ifo.get_id())
        self.ui.nhd_table.insertRow(self.ui.nhd_table.rowCount())
        for m in range(len(metadata)):
            twi = QtWidgets.QTableWidgetItem()
            twi.setText(str(metadata[m]))
            self.ui.nhd_table.setItem(self.ui.nhd_table.rowCount()-1, m, twi)
        self.ui.nhd_table.resizeColumnsToContents()
        return True

    def open_if_function_dialog(self):
        """Opens the influence function dialog window so that the user can modify and add new functions. The difference
        with the version in the main GUI is that this function catches the 'accepted' and 'rejected' signals and
        updates the GUI accordingly."""
        print("Opening Dialog")
        if_dialog = InfluenceFunctionGUILaunch(self.simulation, self.log)
        if_dialog.accepted.connect(self.populate_if_table_from_module)
        if_dialog.accepted.connect(self.setup_if_function_select_combo)
        if_dialog.rejected.connect(self.populate_if_table_from_module)
        if_dialog.rejected.connect(self.setup_if_function_select_combo)
        if_dialog.exec_()

    def view_selectedfunction(self, source):
        """Opens the influence function dialog window for viewing of the selected function.

        :param source: either "combo" or "table" depending on which button was clicked. Allows the program to find
                        which function to actually show.
        """
        viewindex = None
        if self.ui.nhd_table.rowCount() == 0:
            return True     # If table is empty, do nothing.

        if source == "combo":       # Determine combo box index
            viewindex = self.ui.functionselect_combo.currentIndex()
        elif source == "table":
            fid = self.ui.nhd_table.item(self.ui.nhd_table.currentRow(), 0).text()
            print(fid)
            ifos = self.simulation.get_all_function_objects_of_type("IF")
            for i in range(len(ifos)):
                if ifos[i].get_id() == fid:
                    viewindex = i + 1
                    break
        if viewindex is None:
            return True
        if_dialog = InfluenceFunctionGUILaunch(self.simulation, self.log, viewmode=viewindex)
        if_dialog.exec_()

    def populate_if_table_from_module(self):
        """Populates the IF table from module parameters based on the available functions."""
        self.ui.nhd_table.setRowCount(0)
        if_ids = self.module.get_parameter("function_ids")
        for fid in if_ids:
            ifo = self.simulation.get_function_with_id(fid)
            if ifo is None:
                continue

            luabbr = str(ifo.origin_landuse) + " -> " + str(ifo.target_landuse)
            metadata = [ifo.get_id(), ifo.get_function_name(), luabbr, str(ifo.get_x_range()), str(ifo.get_y_range())]
            print(f"Loading {metadata}")
            self.ui.nhd_table.insertRow(self.ui.nhd_table.rowCount())
            for m in range(len(metadata)):
                twi = QtWidgets.QTableWidgetItem()
                twi.setText(str(metadata[m]))
                self.ui.nhd_table.setItem(self.ui.nhd_table.rowCount() - 1, m, twi)
        self.ui.nhd_table.resizeColumnsToContents()
        return True

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

    def sync_aspect_to_slope_combobox(self):
        """Synchronizes the current index of the aspect combo box to that of the slope. They both rely on the same
        data set."""
        self.ui.suit_aspect_data.setCurrentIndex(self.ui.suit_slope_data.currentIndex())

    def sync_slope_to_aspect_combobox(self):
        """Synchronizes the current index of the slope combo box to that of the aspect. They both rely on the same
        data set."""
        self.ui.suit_slope_data.setCurrentIndex(self.ui.suit_aspect_data.currentIndex())

    def enable_disable_dynamics_tab_widgets(self):
        """Scans the Urban Dynamics tab widgets and enables and disables accordingly."""
        self.ui.input_birthrate_spin.setEnabled(self.ui.pop_method_rate.isChecked())
        self.ui.input_deathrate_spin.setEnabled(self.ui.pop_method_rate.isChecked())
        self.ui.input_migration_spin.setEnabled(self.ui.pop_method_rate.isChecked())
        self.ui.input_birthrate_function.setEnabled(self.ui.pop_method_function.isChecked())
        self.ui.input_deathrate_function.setEnabled(self.ui.pop_method_function.isChecked())
        self.ui.input_migration_function.setEnabled(self.ui.pop_method_function.isChecked())
        self.ui.employ_rate_ind_spin.setEnabled(self.ui.employ_rate_ind_check.isChecked())
        self.ui.employ_rate_orc_spin.setEnabled(self.ui.employ_rate_orc_check.isChecked())

        self.ui.res_maxdens_spin.setEnabled(not(self.ui.res_maxdens_auto.isChecked()))
        self.ui.com_maxdens_spin.setEnabled(not(self.ui.com_maxdens_auto.isChecked()))
        self.ui.ind_maxdens_spin.setEnabled(not(self.ui.ind_maxdens_auto.isChecked()))
        self.ui.orc_maxdens_spin.setEnabled(not(self.ui.orc_maxdens_auto.isChecked()))

        self.ui.pg_penalty_inertia.setEnabled(self.ui.pg_penalty_check.isChecked())
        self.ui.pg_provision_spin.setEnabled(self.ui.pg_provision_check.isChecked() and
                                             not(self.ui.pg_provision_current_check.isChecked()))
        self.ui.pg_provision_current_check.setEnabled(self.ui.pg_provision_check.isChecked())

        self.ui.ref_penalty_inertia.setEnabled(self.ui.ref_penalty_check.isChecked())
        self.ui.ref_provision_spin.setEnabled(self.ui.ref_provision_check.isChecked() and
                                              not(self.ui.ref_provision_current_check.isChecked()))
        self.ui.ref_provision_current_check.setEnabled(self.ui.ref_provision_check.isChecked())
        return True

    def enable_disable_zoning_widgets(self):
        """Scans the zoning list and enables and disables the criteria list accordingly."""
        self.ui.zoning_rules_rescombo.setEnabled(not self.ui.zoning_rules_resauto.isChecked())  # RESIDENTIAL
        self.ui.zoning_rules_reslimit.setEnabled(self.ui.zoning_rules_resauto.isChecked())
        self.ui.zoning_rules_respassive.setEnabled(self.ui.zoning_rules_resauto.isChecked() and
                                                   self.ui.zoning_rules_reslimit.isChecked())

        self.ui.zoning_rules_comcombo.setEnabled(not self.ui.zoning_rules_comauto.isChecked())  # COMMERCIAL
        self.ui.zoning_rules_comlimit.setEnabled(self.ui.zoning_rules_comauto.isChecked())
        self.ui.zoning_rules_compassive.setEnabled(self.ui.zoning_rules_comauto.isChecked() and
                                                   self.ui.zoning_rules_comlimit.isChecked())

        self.ui.zoning_rules_indcombo.setEnabled(not self.ui.zoning_rules_indauto.isChecked())  # INDUSTRIAL
        self.ui.zoning_rules_indlimit.setEnabled(self.ui.zoning_rules_indauto.isChecked())
        self.ui.zoning_rules_indpassive.setEnabled(self.ui.zoning_rules_indauto.isChecked() and
                                                   self.ui.zoning_rules_indlimit.isChecked())

        self.ui.zoning_rules_officescombo.setEnabled(not self.ui.zoning_rules_officesauto.isChecked())  # OFFICES
        self.ui.zoning_rules_officeslimit.setEnabled(self.ui.zoning_rules_officesauto.isChecked())
        self.ui.zoning_rules_officespassive.setEnabled(self.ui.zoning_rules_officesauto.isChecked() and
                                                       self.ui.zoning_rules_officeslimit.isChecked())

        if self.ui.zoning_constraints_heritage_combo.currentIndex() == 0:
            self.ui.zoning_constraints_heritage_res.setEnabled(0)
            self.ui.zoning_constraints_heritage_com.setEnabled(0)
            self.ui.zoning_constraints_heritage_ind.setEnabled(0)
            self.ui.zoning_constraints_heritage_orc.setEnabled(0)
        else:
            self.ui.zoning_constraints_heritage_res.setEnabled(1)
            self.ui.zoning_constraints_heritage_com.setEnabled(1)
            self.ui.zoning_constraints_heritage_ind.setEnabled(1)
            self.ui.zoning_constraints_heritage_orc.setEnabled(1)

        if self.ui.zoning_constraints_public_combo.currentIndex() == 0:
            self.ui.zoning_constraints_public_res.setEnabled(0)
            self.ui.zoning_constraints_public_com.setEnabled(0)
            self.ui.zoning_constraints_public_ind.setEnabled(0)
            self.ui.zoning_constraints_public_orc.setEnabled(0)
        else:
            self.ui.zoning_constraints_public_res.setEnabled(1)
            self.ui.zoning_constraints_public_com.setEnabled(1)
            self.ui.zoning_constraints_public_ind.setEnabled(1)
            self.ui.zoning_constraints_public_orc.setEnabled(1)

        if self.ui.zoning_constraints_enviro_combo.currentIndex() == 0:
            self.ui.zoning_constraints_enviro_res.setEnabled(0)
            self.ui.zoning_constraints_enviro_com.setEnabled(0)
            self.ui.zoning_constraints_enviro_ind.setEnabled(0)
            self.ui.zoning_constraints_enviro_orc.setEnabled(0)
        else:
            self.ui.zoning_constraints_enviro_res.setEnabled(1)
            self.ui.zoning_constraints_enviro_com.setEnabled(1)
            self.ui.zoning_constraints_enviro_ind.setEnabled(1)
            self.ui.zoning_constraints_enviro_orc.setEnabled(1)

        if self.ui.zoning_constraints_flood_combo.currentIndex() == 0:
            self.ui.zoning_constraints_flood_res.setEnabled(0)
            self.ui.zoning_constraints_flood_com.setEnabled(0)
            self.ui.zoning_constraints_flood_ind.setEnabled(0)
            self.ui.zoning_constraints_flood_orc.setEnabled(0)
        else:
            self.ui.zoning_constraints_flood_res.setEnabled(1)
            self.ui.zoning_constraints_flood_com.setEnabled(1)
            self.ui.zoning_constraints_flood_ind.setEnabled(1)
            self.ui.zoning_constraints_flood_orc.setEnabled(1)

        if self.ui.zoning_constraints_custom_combo.currentIndex() == 0:
            self.ui.zoning_constraints_custom_res.setEnabled(0)
            self.ui.zoning_constraints_custom_com.setEnabled(0)
            self.ui.zoning_constraints_custom_ind.setEnabled(0)
            self.ui.zoning_constraints_custom_orc.setEnabled(0)
        else:
            self.ui.zoning_constraints_custom_res.setEnabled(1)
            self.ui.zoning_constraints_custom_com.setEnabled(1)
            self.ui.zoning_constraints_custom_ind.setEnabled(1)
            self.ui.zoning_constraints_custom_orc.setEnabled(1)
        return True

    def enable_disable_suitability_widgets(self):
        """Scans the suitability list and enables and disables the criteria list accordingly."""
        self.ui.suit_slope_data.setEnabled(self.ui.suit_slope_check.isChecked())        # Slope
        self.ui.suit_slope_weight.setEnabled(self.ui.suit_slope_check.isChecked())
        self.ui.slope_widget.setEnabled(self.ui.suit_slope_check.isChecked())

        self.ui.suit_aspect_data.setEnabled(self.ui.suit_aspect_check.isChecked())      # Aspect
        self.ui.suit_aspect_weight.setEnabled(self.ui.suit_aspect_check.isChecked())
        self.ui.aspect_widget.setEnabled(self.ui.suit_aspect_check.isChecked())

        self.ui.suit_gw_data.setEnabled(self.ui.suit_gw_check.isChecked())      # Groundwater
        self.ui.suit_gw_weight.setEnabled(self.ui.suit_gw_check.isChecked())
        self.ui.gw_widget.setEnabled(self.ui.suit_gw_check.isChecked())

        self.ui.suit_soil_data.setEnabled(self.ui.suit_soil_check.isChecked())      # Soil
        self.ui.suit_soil_weight.setEnabled(self.ui.suit_soil_check.isChecked())
        self.ui.soil_widget.setEnabled(self.ui.suit_soil_check.isChecked())

        self.ui.suit_custom_data.setEnabled(self.ui.suit_custom_check.isChecked())    # Custom
        self.ui.suit_custom_weight.setEnabled(self.ui.suit_custom_check.isChecked())
        self.ui.custom_widget.setEnabled(self.ui.suit_custom_check.isChecked())

        self.ui.slope_res_midpoint.setEnabled(self.ui.slope_include_midpoints.isChecked())
        self.ui.slope_com_midpoint.setEnabled(self.ui.slope_include_midpoints.isChecked())
        self.ui.slope_ind_midpoint.setEnabled(self.ui.slope_include_midpoints.isChecked())
        self.ui.slope_orc_midpoint.setEnabled(self.ui.slope_include_midpoints.isChecked())

        self.ui.gw_res_midpoint.setEnabled(self.ui.gw_include_midpoints.isChecked())
        self.ui.gw_com_midpoint.setEnabled(self.ui.gw_include_midpoints.isChecked())
        self.ui.gw_ind_midpoint.setEnabled(self.ui.gw_include_midpoints.isChecked())
        self.ui.gw_orc_midpoint.setEnabled(self.ui.gw_include_midpoints.isChecked())

        self.ui.custom_res_midpoint.setEnabled(self.ui.custom_include_midpoints.isChecked())
        self.ui.custom_com_midpoint.setEnabled(self.ui.custom_include_midpoints.isChecked())
        self.ui.custom_ind_midpoint.setEnabled(self.ui.custom_include_midpoints.isChecked())
        self.ui.custom_orc_midpoint.setEnabled(self.ui.custom_include_midpoints.isChecked())
        return True

    def update_suitability_sliders_slope(self):
        """Updates the value of the slider boxes for the slope sliders."""
        self.ui.slope_res_box.setText(str(round(float(self.ui.slope_res_slider.value() / 10), 1))+" %")
        self.ui.slope_com_box.setText(str(round(float(self.ui.slope_com_slider.value() / 10), 1))+" %")
        self.ui.slope_ind_box.setText(str(round(float(self.ui.slope_ind_slider.value() / 10), 1))+" %")
        self.ui.slope_orc_box.setText(str(round(float(self.ui.slope_orc_slider.value() / 10), 1))+" %")

    def update_suitability_sliders_gw(self):
        """Updates the value of the slider boxes for the groundwater sliders."""
        self.ui.gw_res_box.setText(str(round(float(self.ui.gw_res_slider.value()), 1))+" m")
        self.ui.gw_com_box.setText(str(round(float(self.ui.gw_com_slider.value()), 1))+" m")
        self.ui.gw_ind_box.setText(str(round(float(self.ui.gw_ind_slider.value()), 1))+" m")
        self.ui.gw_orc_box.setText(str(round(float(self.ui.gw_orc_slider.value()), 1))+" m")

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

        self.ui.access_pth_data.setEnabled(self.ui.access_pth_include.isChecked())  # Public Transport Hubs (PTH)
        self.ui.access_pth_weight.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_res.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_com.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_ind.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_offices.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_ares.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_acom.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_aind.setEnabled(self.ui.access_pth_include.isChecked())
        self.ui.access_pth_aoffices.setEnabled(self.ui.access_pth_include.isChecked())
        return True

    def enable_disable_general_tab_widgets(self):
        """Enables and disables all the widgets in the general Tab area depending on what is selected."""
        if self.ui.input_lga_combo.currentIndex() == 0:
            self.ui.input_lga_name.setEnabled(0)
        else:
            self.ui.input_lga_name.setEnabled(1)

        if self.ui.input_luc_combo.currentIndex() == 0:
            self.ui.input_aggreg_combo.setEnabled(0)
        else:
            self.ui.input_aggreg_combo.setEnabled(1)

        if self.ui.input_pop_combo.currentIndex() == 0:
            self.ui.dynamics_pop_widget.setEnabled(0)
        else:
            self.ui.dynamics_pop_widget.setEnabled(1)
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

        try:    # MUNICIPALITY COMBO - retrieve the dataID from module
            self.ui.input_lga_combo.setCurrentIndex(
                self.municipalmaps[1].index(self.module.get_parameter("lga_inputmap")))
        except ValueError:
            self.ui.input_lga_combo.setCurrentIndex(0)     # map doesn't exist or single municipality option chosen

        self.ui.input_lga_name.setText(str(self.module.get_parameter("lga_attribute")))

        try:    # LAND USE COMBO - retrieve the dataID from module
            self.ui.input_luc_combo.setCurrentIndex(self.lumaps[1].index(self.module.get_parameter("luc_inputmap")))
        except ValueError:
            self.ui.input_luc_combo.setCurrentIndex(0)     # else the map must've been removed, set combo to zero index

        self.ui.input_aggreg_combo.setCurrentIndex(self.aggregation_methods.index(
            self.module.get_parameter("luc_aggregation")))

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

        try:    # POPULATION COMBO - retrieve the dataID from module
            self.ui.input_pop_combo.setCurrentIndex(self.popmaps[1].index(self.module.get_parameter("pop_inputmap")))
        except ValueError:
            self.ui.input_pop_combo.setCurrentIndex(0)     # else the map must've been removed, set combo to zero index

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

        # --- employment STACK 2
        self.ui.employ_pop_com.setValue(float(self.module.get_parameter("employ_pop_comfactor")))
        self.ui.employ_pop_ind.setValue(float(self.module.get_parameter("employ_pop_indfactor")))
        self.ui.employ_pop_office.setValue(float(self.module.get_parameter("employ_pop_officefactor")))

        # --- employment STACK 3
        self.ui.employ_land_com.setValue(float(self.module.get_parameter("employ_land_comfactor")))
        self.ui.employ_land_ind.setValue(float(self.module.get_parameter("employ_land_indfactor")))
        self.ui.employ_land_office.setValue(float(self.module.get_parameter("employ_land_officefactor")))

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
        try:    # RAIL COMBO BOX
            self.ui.access_rail_data.setCurrentIndex(self.railmaps[1].index(
                self.module.get_parameter("access_rail_data")))
        except ValueError:
            self.ui.access_rail_data.setCurrentIndex(0)

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

        # Public Transport Hubs (PTHs)
        self.ui.access_pth_include.setChecked(int(self.module.get_parameter("access_pth_include")))
        self.ui.access_pth_weight.setValue(int(self.module.get_parameter("access_pth_weight")))
        self.ui.access_pth_res.setChecked(int(self.module.get_parameter("access_pth_res")))
        self.ui.access_pth_com.setChecked(int(self.module.get_parameter("access_pth_com")))
        self.ui.access_pth_ind.setChecked(int(self.module.get_parameter("access_pth_ind")))
        self.ui.access_pth_offices.setChecked(int(self.module.get_parameter("access_pth_offices")))
        self.ui.access_pth_ares.setText(str(self.module.get_parameter("access_pth_ares")))
        self.ui.access_pth_acom.setText(str(self.module.get_parameter("access_pth_acom")))
        self.ui.access_pth_aind.setText(str(self.module.get_parameter("access_pth_aind")))
        self.ui.access_pth_aoffices.setText(str(self.module.get_parameter("access_pth_aoffices")))
        try:  # PTH COMBO BOX
            self.ui.access_pth_data.setCurrentIndex(self.localitymaps[1].index(
                self.module.get_parameter("access_pth_data")))
        except ValueError:
            self.ui.access_pth_data.setCurrentIndex(0)

        self.enable_disable_accessibility_widgets()

        # TAB 2.2 - Suitability
        self.ui.suit_export_maps.setChecked(int(self.module.get_parameter("suit_export")))
        self.ui.suit_criteria_combo.setCurrentIndex(0)

        # CRITERION - SLOPE
        self.ui.suit_slope_check.setChecked(int(self.module.get_parameter("suit_slope_include")))
        self.ui.suit_slope_weight.setValue(int(self.module.get_parameter("suit_slope_weight")))
        try:    # SLOPE DATA COMBO
            self.ui.suit_slope_data.setCurrentIndex(self.elevmaps[1].index(
                self.module.get_parameter("suit_elevation_data")))
        except ValueError:
            self.ui.suit_slope_data.setCurrentIndex(0)
        self.ui.slope_res_slider.setValue(int(float(self.module.get_parameter("slope_res"))*10.0))
        self.ui.slope_com_slider.setValue(int(float(self.module.get_parameter("slope_com"))*10.0))
        self.ui.slope_ind_slider.setValue(int(float(self.module.get_parameter("slope_ind"))*10.0))
        self.ui.slope_orc_slider.setValue(int(float(self.module.get_parameter("slope_orc"))*10.0))
        self.ui.slope_trend_combo.setCurrentIndex(int(ubglobals.VALUE_SCALE_METHODS.index(
            self.module.get_parameter("slope_trend"))))
        self.ui.slope_include_midpoints.setChecked(int(self.module.get_parameter("slope_midpoint")))
        self.ui.slope_res_midpoint.setValue(float(self.module.get_parameter("slope_res_mid")))
        self.ui.slope_com_midpoint.setValue(float(self.module.get_parameter("slope_com_mid")))
        self.ui.slope_ind_midpoint.setValue(float(self.module.get_parameter("slope_ind_mid")))
        self.ui.slope_orc_midpoint.setValue(float(self.module.get_parameter("slope_orc_mid")))

        # CRITERION - ASPECT
        self.ui.suit_aspect_check.setChecked(int(self.module.get_parameter("suit_aspect_include")))
        self.ui.suit_aspect_weight.setValue(int(self.module.get_parameter("suit_aspect_weight")))
        try:  # ASPECT DATA COMBO
            self.ui.suit_aspect_data.setCurrentIndex(self.elevmaps[1].index(
                self.module.get_parameter("suit_elevation_data")))
        except ValueError:
            self.ui.suit_aspect_data.setCurrentIndex(0)
        self.ui.aspect_res_north.setValue(int(self.module.get_parameter("aspect_res_north")))
        self.ui.aspect_res_east.setValue(int(self.module.get_parameter("aspect_res_east")))
        self.ui.aspect_res_south.setValue(int(self.module.get_parameter("aspect_res_south")))
        self.ui.aspect_res_west.setValue(int(self.module.get_parameter("aspect_res_west")))

        self.ui.aspect_com_north.setValue(int(self.module.get_parameter("aspect_com_north")))
        self.ui.aspect_com_east.setValue(int(self.module.get_parameter("aspect_com_east")))
        self.ui.aspect_com_south.setValue(int(self.module.get_parameter("aspect_com_south")))
        self.ui.aspect_com_west.setValue(int(self.module.get_parameter("aspect_com_west")))

        self.ui.aspect_ind_north.setValue(int(self.module.get_parameter("aspect_ind_north")))
        self.ui.aspect_ind_east.setValue(int(self.module.get_parameter("aspect_ind_east")))
        self.ui.aspect_ind_south.setValue(int(self.module.get_parameter("aspect_ind_south")))
        self.ui.aspect_ind_west.setValue(int(self.module.get_parameter("aspect_ind_west")))

        self.ui.aspect_orc_north.setValue(int(self.module.get_parameter("aspect_orc_north")))
        self.ui.aspect_orc_east.setValue(int(self.module.get_parameter("aspect_orc_east")))
        self.ui.aspect_orc_south.setValue(int(self.module.get_parameter("aspect_orc_south")))
        self.ui.aspect_orc_west.setValue(int(self.module.get_parameter("aspect_orc_west")))

        # CRITERION - SOIL
        self.ui.suit_soil_check.setChecked(int(self.module.get_parameter("suit_soil_include")))
        self.ui.suit_soil_weight.setValue(int(self.module.get_parameter("suit_soil_weight")))
        try:  # SOIL DATA COMBO
            self.ui.suit_soil_data.setCurrentIndex(self.soilmaps[1].index(
                self.module.get_parameter("suit_soil_data")))
        except ValueError:
            self.ui.suit_soil_data.setCurrentIndex(0)
        self.ui.soil_res_sand.setValue(int(self.module.get_parameter("soil_res_sand")))
        self.ui.soil_res_sandclay.setValue(int(self.module.get_parameter("soil_res_sandclay")))
        self.ui.soil_res_medclay.setValue(int(self.module.get_parameter("soil_res_medclay")))
        self.ui.soil_res_heavyclay.setValue(int(self.module.get_parameter("soil_res_heavyclay")))

        self.ui.soil_com_sand.setValue(int(self.module.get_parameter("soil_com_sand")))
        self.ui.soil_com_sandclay.setValue(int(self.module.get_parameter("soil_com_sandclay")))
        self.ui.soil_com_medclay.setValue(int(self.module.get_parameter("soil_com_medclay")))
        self.ui.soil_com_heavyclay.setValue(int(self.module.get_parameter("soil_com_heavyclay")))

        self.ui.soil_ind_sand.setValue(int(self.module.get_parameter("soil_ind_sand")))
        self.ui.soil_ind_sandclay.setValue(int(self.module.get_parameter("soil_ind_sandclay")))
        self.ui.soil_ind_medclay.setValue(int(self.module.get_parameter("soil_ind_medclay")))
        self.ui.soil_ind_heavyclay.setValue(int(self.module.get_parameter("soil_ind_heavyclay")))

        self.ui.soil_orc_sand.setValue(int(self.module.get_parameter("soil_orc_sand")))
        self.ui.soil_orc_sandclay.setValue(int(self.module.get_parameter("soil_orc_sandclay")))
        self.ui.soil_orc_medclay.setValue(int(self.module.get_parameter("soil_orc_medclay")))
        self.ui.soil_orc_heavyclay.setValue(int(self.module.get_parameter("soil_orc_heavyclay")))

        # CRITERION - GROUNDWATER DEPTH [m]
        self.ui.suit_gw_check.setChecked(int(self.module.get_parameter("suit_gw_include")))
        self.ui.suit_gw_weight.setValue(int(self.module.get_parameter("suit_gw_weight")))
        try:  # GROUNDWATER DATA COMBO
            self.ui.suit_gw_data.setCurrentIndex(self.gwmaps[1].index(
                self.module.get_parameter("suit_gw_data")))
        except ValueError:
            self.ui.suit_gw_data.setCurrentIndex(0)
        self.ui.gw_res_slider.setValue(int(self.module.get_parameter("gw_res")))
        self.ui.gw_com_slider.setValue(int(self.module.get_parameter("gw_com")))
        self.ui.gw_ind_slider.setValue(int(self.module.get_parameter("gw_ind")))
        self.ui.gw_orc_slider.setValue(int(self.module.get_parameter("gw_orc")))
        self.ui.gw_trend_combo.setCurrentIndex(int(ubglobals.VALUE_SCALE_METHODS.index(
            self.module.get_parameter("gw_trend"))))
        self.ui.gw_include_midpoints.setChecked(int(self.module.get_parameter("gw_midpoint")))
        self.ui.gw_res_midpoint.setValue(float(self.module.get_parameter("gw_res_mid")))
        self.ui.gw_com_midpoint.setValue(float(self.module.get_parameter("gw_com_mid")))
        self.ui.gw_ind_midpoint.setValue(float(self.module.get_parameter("gw_ind_mid")))
        self.ui.gw_orc_midpoint.setValue(float(self.module.get_parameter("gw_orc_mid")))

        # CRITERION - CUSTOM
        self.ui.suit_custom_check.setChecked(int(self.module.get_parameter("suit_custom_include")))
        self.ui.suit_custom_weight.setValue(int(self.module.get_parameter("suit_custom_weight")))
        try:  # CUSTOM COMBO
            self.ui.suit_custom_data.setCurrentIndex(self.overlaymaps[1].index(
                self.module.get_parameter("suit_custom_data")))
        except ValueError:
            self.ui.suit_custom_data.setCurrentIndex(0)
        self.ui.custom_res_min.setText(str(self.module.get_parameter("custom_res_min")))
        self.ui.custom_res_max.setText(str(self.module.get_parameter("custom_res_max")))
        self.ui.custom_com_min.setText(str(self.module.get_parameter("custom_com_min")))
        self.ui.custom_com_max.setText(str(self.module.get_parameter("custom_com_max")))
        self.ui.custom_ind_min.setText(str(self.module.get_parameter("custom_ind_min")))
        self.ui.custom_ind_max.setText(str(self.module.get_parameter("custom_ind_max")))
        self.ui.custom_orc_min.setText(str(self.module.get_parameter("custom_orc_min")))
        self.ui.custom_orc_max.setText(str(self.module.get_parameter("custom_orc_max")))
        self.ui.custom_trend_combo.setCurrentIndex(int(ubglobals.VALUE_SCALE_METHODS.index(
            self.module.get_parameter("custom_trend"))))
        self.ui.custom_include_midpoints.setChecked(int(self.module.get_parameter("custom_midpoint")))
        self.ui.custom_res_midpoint.setText(str(float(self.module.get_parameter("custom_res_mid"))))
        self.ui.custom_com_midpoint.setText(str(float(self.module.get_parameter("custom_com_mid"))))
        self.ui.custom_ind_midpoint.setText(str(float(self.module.get_parameter("custom_ind_mid"))))
        self.ui.custom_orc_midpoint.setText(str(float(self.module.get_parameter("custom_orc_mid"))))

        self.enable_disable_suitability_widgets()
        self.update_suitability_sliders_slope()
        self.update_suitability_sliders_gw()
        self.ui.suit_threshold_stack.setCurrentIndex(int(self.ui.suit_criteria_combo.currentIndex()))

        # TAB 2.3 - Zoning
        self.ui.zoning_export.setChecked(int(self.module.get_parameter("zoning_export")))

        # GENERAL ZONING RULES FOR ACTIVE LAND USES
        try:    # ZONING RESIDENTIAL COMBO
            self.ui.zoning_rules_rescombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_resmap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_resauto.setChecked(self.module.get_parameter("zoning_rules_resauto"))
        self.ui.zoning_rules_reslimit.setChecked(self.module.get_parameter("zoning_rules_reslimit"))
        self.ui.zoning_rules_respassive.setChecked(self.module.get_parameter("zoning_rules_respassive"))

        try:    # ZONING COMMERCIAL COMBO
            self.ui.zoning_rules_comcombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_commap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_comauto.setChecked(self.module.get_parameter("zoning_rules_comauto"))
        self.ui.zoning_rules_comlimit.setChecked(self.module.get_parameter("zoning_rules_comlimit"))
        self.ui.zoning_rules_compassive.setChecked(self.module.get_parameter("zoning_rules_compassive"))

        try:    # ZONING INDUSTRIAL COMBO
            self.ui.zoning_rules_indcombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_indmap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_indauto.setChecked(self.module.get_parameter("zoning_rules_indauto"))
        self.ui.zoning_rules_indlimit.setChecked(self.module.get_parameter("zoning_rules_indlimit"))
        self.ui.zoning_rules_indpassive.setChecked(self.module.get_parameter("zoning_rules_indpassive"))

        try:    # ZONING OFFICES COMBO
            self.ui.zoning_rules_officescombo.setCurrentIndex(self.lumaps[1].index(
                self.module.get_parameter("zoning_rules_officesmap")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)
        self.ui.zoning_rules_officesauto.setChecked(self.module.get_parameter("zoning_rules_officesauto"))
        self.ui.zoning_rules_officeslimit.setChecked(self.module.get_parameter("zoning_rules_officeslimit"))
        self.ui.zoning_rules_officespassive.setChecked(self.module.get_parameter("zoning_rules_officespassive"))

        # SPECIFIC PLANNING CONSTRAINTS FOR ZONING
        try:    # ZONING WATER BODIES COMBO BOX
            self.ui.zoning_constraints_water_combo.setCurrentIndex(self.lakemaps[1].index(
                self.module.get_parameter("zoning_water")))
        except ValueError:
            self.ui.zoning_constraints_water_combo.setCurrentIndex(0)

        try:    # ZONING HERITAGE COMBO
            self.ui.zoning_constraints_heritage_combo.setCurrentIndex(self.overlaymaps[1].index(
                self.module.get_parameter("zoning_heritage")))
        except ValueError:
            self.ui.zoning_constraints_heritage_combo.setCurrentIndex(0)

        try:    # ZONING PUBLIC COMBO
            self.ui.zoning_constraints_public_combo.setCurrentIndex(self.overlaymaps[1].index(
                self.module.get_parameter("zoning_public")))
        except ValueError:
            self.ui.zoning_constraints_public_combo.setCurrentIndex(0)

        try:    # ZONING ENVIRONMENTAL SIGNIFICANCE COMBO
            self.ui.zoning_constraints_enviro_combo.setCurrentIndex(self.overlaymaps[1].index(
                self.module.get_parameter("zoning_enviro")))
        except ValueError:
            self.ui.zoning_constraints_enviro_combo.setCurrentIndex(0)

        try:  # ZONING LAND SUBJECT TO INUNDATION COMBO
            self.ui.zoning_constraints_flood_combo.setCurrentIndex(self.overlaymaps[1].index(
                self.module.get_parameter("zoning_flood")))
        except ValueError:
            self.ui.zoning_constraints_flood_combo.setCurrentIndex(0)

        try:  # ZONING CUSTOM COMBO
            self.ui.zoning_constraints_custom_combo.setCurrentIndex(self.overlaymaps[1].index(
                self.module.get_parameter("zoning_custom")))
        except ValueError:
            self.ui.zoning_constraints_custom_combo.setCurrentIndex(0)

        self.ui.zoning_constraints_heritage_res.setChecked(int(self.module.get_parameter("zoning_heritage_res")))
        self.ui.zoning_constraints_heritage_com.setChecked(int(self.module.get_parameter("zoning_heritage_com")))
        self.ui.zoning_constraints_heritage_ind.setChecked(int(self.module.get_parameter("zoning_heritage_ind")))
        self.ui.zoning_constraints_heritage_orc.setChecked(int(self.module.get_parameter("zoning_heritage_orc")))

        self.ui.zoning_constraints_public_res.setChecked(int(self.module.get_parameter("zoning_public_res")))
        self.ui.zoning_constraints_public_com.setChecked(int(self.module.get_parameter("zoning_public_com")))
        self.ui.zoning_constraints_public_ind.setChecked(int(self.module.get_parameter("zoning_public_ind")))
        self.ui.zoning_constraints_public_orc.setChecked(int(self.module.get_parameter("zoning_public_orc")))

        self.ui.zoning_constraints_enviro_res.setChecked(int(self.module.get_parameter("zoning_enviro_res")))
        self.ui.zoning_constraints_enviro_com.setChecked(int(self.module.get_parameter("zoning_enviro_com")))
        self.ui.zoning_constraints_enviro_ind.setChecked(int(self.module.get_parameter("zoning_enviro_ind")))
        self.ui.zoning_constraints_enviro_orc.setChecked(int(self.module.get_parameter("zoning_enviro_orc")))

        self.ui.zoning_constraints_flood_res.setChecked(int(self.module.get_parameter("zoning_flood_res")))
        self.ui.zoning_constraints_flood_com.setChecked(int(self.module.get_parameter("zoning_flood_com")))
        self.ui.zoning_constraints_flood_ind.setChecked(int(self.module.get_parameter("zoning_flood_ind")))
        self.ui.zoning_constraints_flood_orc.setChecked(int(self.module.get_parameter("zoning_flood_orc")))

        self.ui.zoning_constraints_custom_res.setChecked(int(self.module.get_parameter("zoning_custom_res")))
        self.ui.zoning_constraints_custom_com.setChecked(int(self.module.get_parameter("zoning_custom_com")))
        self.ui.zoning_constraints_custom_ind.setChecked(int(self.module.get_parameter("zoning_custom_ind")))
        self.ui.zoning_constraints_custom_orc.setChecked(int(self.module.get_parameter("zoning_custom_orc")))

        self.enable_disable_zoning_widgets()

        # TAB 2.4 - Neighbourhood Effect
        self.ifo_selection = self.module.get_parameter("function_ids")
        self.populate_if_table_from_module()
        if self.module.get_parameter("edge_effects_method") == "NA":
            self.ui.ee_noaccount.setChecked(1)
        elif self.module.get_parameter("edge_effects_method") == "AVG":
            self.ui.ee_averaging.setChecked(1)
        elif self.module.get_parameter("edge_effects_method") == "PP":
            self.ui.ee_proportioning.setChecked(1)
        else:
            self.ui.ee_ppavg.setChecked(1)

        # TAB 3 - URBAN DYNAMICS
        # TAB 3.1 - External Drivers
        # Population and Employment Rates fo Change
        if self.module.get_parameter("pop_growthmethod") == "C":
            self.ui.pop_method_rate.setChecked(1)
        else:
            self.ui.pop_method_function.setChecked(1)

        self.ui.input_birthrate_spin.setValue(float(self.module.get_parameter("pop_birthrate")))
        self.ui.input_deathrate_spin.setValue(float(self.module.get_parameter("pop_deathrate")))
        self.ui.input_migration_spin.setValue(float(self.module.get_parameter("pop_migration")))

        # self.ui.input_birthrate_function.setCurrentIndex(self.poptrends.index(
        #     self.module.get_parameter("pop_birthfunction")))
        # self.ui.input_deathrate_function.setCurrentIndex(self.poptrends.index(
        #     self.module.get_parameter("pop_deathfunction")))
        # self.ui.input_migration_function.setCurrentIndex(self.poptrends.index(
        #     self.module.get_parameter("pop_migrationfunction")))

        self.ui.employ_rate_spin.setValue(float(self.module.get_parameter("employ_com_roc")))
        self.ui.employ_rate_ind_check.setChecked(int(self.module.get_parameter("employ_ind_rocbool")))
        self.ui.employ_rate_ind_spin.setValue(float(self.module.get_parameter("employ_ind_roc")))
        self.ui.employ_rate_orc_check.setChecked(int(self.module.get_parameter("employ_orc_rocbool")))
        self.ui.employ_rate_orc_spin.setValue(float(self.module.get_parameter("employ_orc_roc")))

        # TAB 3.2 - Internal Drivers
        # Stochastic Perturbation
        self.ui.stoch_box.setValue(float(self.module.get_parameter("alpha")))

        # Recalculation Rules
        self.ui.dynamics_recalculate_nhd.setChecked(int(self.module.get_parameter("recalc_nhd")))
        self.ui.dynamics_recalculate_stoch.setChecked(int(self.module.get_parameter("recalc_stoch")))

        # Land use Potential and Allocation
        self.ui.dynamics_lpot_eqn_combo.setCurrentIndex(ubglobals.VPOT.index(self.module.get_parameter("vpot_eqn")))
        self.ui.dynamics_lpot_zeropot_check.setChecked(int(self.module.get_parameter("vpot_zeropot")))
        self.ui.dynamics_lpot_negativepot_check.setChecked(int(self.module.get_parameter("vpot_negpot")))

        # TAB 3.3 - Transition Rules
        # Inertia and Sensitivities
        self.ui.res_inertia_spin.setValue(self.module.get_parameter("res_inertia"))
        self.ui.res_sensitivity_delta_spin.setValue(self.module.get_parameter("res_delta"))
        self.ui.res_sensitivity_lambda_spin.setValue(self.module.get_parameter("res_lambda"))
        self.ui.res_maxdens_spin.setValue(float(self.module.get_parameter("res_maxdensity")))
        self.ui.res_maxdens_auto.setChecked(int(self.module.get_parameter("res_maxdens_auto")))
        self.ui.res_mindens_spin.setValue(float(self.module.get_parameter("res_mindensity")))

        self.ui.com_inertia_spin.setValue(self.module.get_parameter("com_inertia"))
        self.ui.com_sensitivity_delta_spin.setValue(self.module.get_parameter("com_delta"))
        self.ui.com_sensitivity_lambda_spin.setValue(self.module.get_parameter("com_lambda"))
        self.ui.com_maxdens_spin.setValue(float(self.module.get_parameter("com_maxdensity")))
        self.ui.com_maxdens_auto.setChecked(int(self.module.get_parameter("com_maxdens_auto")))
        self.ui.com_mindens_spin.setValue(float(self.module.get_parameter("com_mindensity")))

        self.ui.ind_inertia_spin.setValue(self.module.get_parameter("ind_inertia"))
        self.ui.ind_sensitivity_delta_spin.setValue(self.module.get_parameter("ind_delta"))
        self.ui.ind_sensitivity_lambda_spin.setValue(self.module.get_parameter("ind_lambda"))
        self.ui.ind_maxdens_spin.setValue(float(self.module.get_parameter("ind_maxdensity")))
        self.ui.ind_maxdens_auto.setChecked(int(self.module.get_parameter("ind_maxdens_auto")))
        self.ui.ind_mindens_spin.setValue(float(self.module.get_parameter("ind_mindensity")))

        self.ui.orc_inertia_spin.setValue(self.module.get_parameter("orc_inertia"))
        self.ui.orc_sensitivity_delta_spin.setValue(self.module.get_parameter("orc_delta"))
        self.ui.orc_sensitivity_lambda_spin.setValue(self.module.get_parameter("orc_lambda"))
        self.ui.orc_maxdens_spin.setValue(float(self.module.get_parameter("orc_maxdensity")))
        self.ui.orc_maxdens_auto.setChecked(int(self.module.get_parameter("orc_maxdens_auto")))
        self.ui.orc_mindens_spin.setValue(float(self.module.get_parameter("orc_mindensity")))

        # Open Space Transitions
        self.ui.pg_penalty_check.setChecked(int(self.module.get_parameter("pg_penalise")))
        self.ui.pg_penalty_inertia.setValue(float(self.module.get_parameter("pg_inertia")))
        self.ui.pg_provision_check.setChecked(int(self.module.get_parameter("pg_provision")))
        self.ui.pg_provision_spin.setValue(float(self.module.get_parameter("pg_proportion")))
        self.ui.pg_provision_current_check.setChecked(int(self.module.get_parameter("pg_current")))

        self.ui.ref_penalty_check.setChecked(int(self.module.get_parameter("ref_penalise")))
        self.ui.ref_penalty_inertia.setValue(float(self.module.get_parameter("ref_inertia")))
        self.ui.ref_provision_check.setChecked(int(self.module.get_parameter("ref_provision")))
        self.ui.ref_provision_spin.setValue(float(self.module.get_parameter("ref_proportion")))
        self.ui.ref_provision_current_check.setChecked(int(self.module.get_parameter("ref_current")))

        self.enable_disable_dynamics_tab_widgets()
        # END OF FILING IN GUI VALUES
        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        # TAB 1 - GENERAL
        self.module.set_parameter("cellsize", int(self.ui.basic_cellsize.value()))
        self.module.set_parameter("nhd_radius", float(self.ui.basic_nhd.value()))

        self.module.set_parameter("lga_inputmap", self.municipalmaps[1][self.ui.input_lga_combo.currentIndex()])
        self.module.set_parameter("lga_attribute", str(self.ui.input_lga_name.text()))

        self.module.set_parameter("luc_inputmap", self.lumaps[1][self.ui.input_luc_combo.currentIndex()])
        self.module.set_parameter("luc_aggregation",
                                  self.aggregation_methods[self.ui.input_aggreg_combo.currentIndex()])

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

        self.module.set_parameter("pop_inputmap", self.popmaps[1][self.ui.input_pop_combo.currentIndex()])

        if self.ui.employ_inputmap.isChecked():
            self.module.set_parameter("employ_datasource", "I")
        elif self.ui.employ_pop.isChecked():
            self.module.set_parameter("employ_datasource", "P")
        else:
            self.module.set_parameter("employ_datasource", "L")

        self.module.set_parameter("employ_inputmap", self.employmaps[1][self.ui.employ_inputmap_combo.currentIndex()])

        self.module.set_parameter("employ_pop_comfactor", float(self.ui.employ_pop_com.value()))
        self.module.set_parameter("employ_pop_indfactor", float(self.ui.employ_pop_ind.value()))
        self.module.set_parameter("employ_pop_officefactor", float(self.ui.employ_pop_office.value()))

        self.module.set_parameter("employ_land_comfactor", float(self.ui.employ_land_com.value()))
        self.module.set_parameter("employ_land_indfactor", float(self.ui.employ_land_ind.value()))
        self.module.set_parameter("employ_land_officefactor", float(self.ui.employ_land_office.value()))

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
        self.module.set_parameter("access_rail_data", self.railmaps[1][self.ui.access_rail_data.currentIndex()])
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

        # Accessibility to Public Transport Hubs (PTHs)
        self.module.set_parameter("access_pth_include", int(self.ui.access_pth_include.isChecked()))
        self.module.set_parameter("access_pth_data", self.localitymaps[1][self.ui.access_pth_data.currentIndex()])
        self.module.set_parameter("access_pth_weight", self.ui.access_pth_weight.value())
        self.module.set_parameter("access_pth_res", int(self.ui.access_pth_res.isChecked()))
        self.module.set_parameter("access_pth_com", int(self.ui.access_pth_com.isChecked()))
        self.module.set_parameter("access_pth_ind", int(self.ui.access_pth_ind.isChecked()))
        self.module.set_parameter("access_pth_offices", int(self.ui.access_pth_offices.isChecked()))
        self.module.set_parameter("access_pth_ares", float(self.ui.access_pth_ares.text()))
        self.module.set_parameter("access_pth_acom", float(self.ui.access_pth_acom.text()))
        self.module.set_parameter("access_pth_aind", float(self.ui.access_pth_aind.text()))
        self.module.set_parameter("access_pth_aoffices", float(self.ui.access_pth_aoffices.text()))

        # TAB 2 - 2.2 Suitability
        self.module.set_parameter("suit_export", int(self.ui.suit_export_maps.isChecked()))

        self.module.set_parameter("suit_elevation_data", self.elevmaps[1][self.ui.suit_slope_data.currentIndex()])

        # SLOPE
        self.module.set_parameter("suit_slope_include", int(self.ui.suit_slope_check.isChecked()))
        self.module.set_parameter("suit_slope_weight", int(self.ui.suit_slope_weight.value()))
        self.module.set_parameter("slope_trend",
                                  ubglobals.VALUE_SCALE_METHODS[self.ui.slope_trend_combo.currentIndex()])
        self.module.set_parameter("slope_midpoint", int(self.ui.slope_include_midpoints.isChecked()))
        self.module.set_parameter("slope_res", float(self.ui.slope_res_slider.value() / 10.0))
        self.module.set_parameter("slope_com", float(self.ui.slope_com_slider.value() / 10.0))
        self.module.set_parameter("slope_ind", float(self.ui.slope_ind_slider.value() / 10.0))
        self.module.set_parameter("slope_orc", float(self.ui.slope_orc_slider.value() / 10.0))
        self.module.set_parameter("slope_res_mid", float(self.ui.slope_res_midpoint.value()))
        self.module.set_parameter("slope_com_mid", float(self.ui.slope_com_midpoint.value()))
        self.module.set_parameter("slope_ind_mid", float(self.ui.slope_ind_midpoint.value()))
        self.module.set_parameter("slope_orc_mid", float(self.ui.slope_orc_midpoint.value()))

        # ASPECT
        self.module.set_parameter("suit_aspect_include", int(self.ui.suit_aspect_check.isChecked()))
        self.module.set_parameter("suit_aspect_weight", int(self.ui.suit_aspect_weight.value()))
        self.module.set_parameter("aspect_res_north", float(self.ui.aspect_res_north.value()))
        self.module.set_parameter("aspect_res_east", float(self.ui.aspect_res_east.value()))
        self.module.set_parameter("aspect_res_south", float(self.ui.aspect_res_south.value()))
        self.module.set_parameter("aspect_res_west", float(self.ui.aspect_res_west.value()))
        self.module.set_parameter("aspect_com_north", float(self.ui.aspect_com_north.value()))
        self.module.set_parameter("aspect_com_east", float(self.ui.aspect_com_east.value()))
        self.module.set_parameter("aspect_com_south", float(self.ui.aspect_com_south.value()))
        self.module.set_parameter("aspect_com_west", float(self.ui.aspect_com_west.value()))
        self.module.set_parameter("aspect_ind_north", float(self.ui.aspect_ind_north.value()))
        self.module.set_parameter("aspect_ind_east", float(self.ui.aspect_ind_east.value()))
        self.module.set_parameter("aspect_ind_south", float(self.ui.aspect_ind_south.value()))
        self.module.set_parameter("aspect_ind_west", float(self.ui.aspect_ind_west.value()))
        self.module.set_parameter("aspect_orc_north", float(self.ui.aspect_orc_north.value()))
        self.module.set_parameter("aspect_orc_east", float(self.ui.aspect_orc_east.value()))
        self.module.set_parameter("aspect_orc_south", float(self.ui.aspect_orc_south.value()))
        self.module.set_parameter("aspect_orc_west", float(self.ui.aspect_orc_west.value()))

        # GROUNDWATER
        self.module.set_parameter("suit_gw_include", int(self.ui.suit_gw_check.isChecked()))
        self.module.set_parameter("suit_gw_data", self.gwmaps[1][self.ui.suit_gw_data.currentIndex()])
        self.module.set_parameter("suit_gw_weight", int(self.ui.suit_gw_weight.value()))
        self.module.set_parameter("gw_trend",
                                  ubglobals.VALUE_SCALE_METHODS[self.ui.gw_trend_combo.currentIndex()])
        self.module.set_parameter("gw_midpoint", int(self.ui.gw_include_midpoints.isChecked()))
        self.module.set_parameter("gw_res", float(self.ui.gw_res_slider.value()))
        self.module.set_parameter("gw_com", float(self.ui.gw_com_slider.value()))
        self.module.set_parameter("gw_ind", float(self.ui.gw_ind_slider.value()))
        self.module.set_parameter("gw_orc", float(self.ui.gw_orc_slider.value()))
        self.module.set_parameter("gw_res_mid", float(self.ui.gw_res_midpoint.value()))
        self.module.set_parameter("gw_com_mid", float(self.ui.gw_com_midpoint.value()))
        self.module.set_parameter("gw_ind_mid", float(self.ui.gw_ind_midpoint.value()))
        self.module.set_parameter("gw_orc_mid", float(self.ui.gw_orc_midpoint.value()))

        # SOIL
        self.module.set_parameter("suit_soil_include", int(self.ui.suit_soil_check.isChecked()))
        self.module.set_parameter("suit_soil_data", self.soilmaps[1][self.ui.suit_soil_data.currentIndex()])
        self.module.set_parameter("suit_soil_weight", int(self.ui.suit_soil_weight.value()))
        self.module.set_parameter("soil_res_sand", float(self.ui.soil_res_sand.value()))
        self.module.set_parameter("soil_res_sandclay", float(self.ui.soil_res_sandclay.value()))
        self.module.set_parameter("soil_res_medclay", float(self.ui.soil_res_medclay.value()))
        self.module.set_parameter("soil_res_heavyclay", float(self.ui.soil_res_heavyclay.value()))
        self.module.set_parameter("soil_com_sand", float(self.ui.soil_com_sand.value()))
        self.module.set_parameter("soil_com_sandclay", float(self.ui.soil_com_sandclay.value()))
        self.module.set_parameter("soil_com_medclay", float(self.ui.soil_com_medclay.value()))
        self.module.set_parameter("soil_com_heavyclay", float(self.ui.soil_com_heavyclay.value()))
        self.module.set_parameter("soil_ind_sand", float(self.ui.soil_ind_sand.value()))
        self.module.set_parameter("soil_ind_sandclay", float(self.ui.soil_ind_sandclay.value()))
        self.module.set_parameter("soil_ind_medclay", float(self.ui.soil_ind_medclay.value()))
        self.module.set_parameter("soil_ind_heavyclay", float(self.ui.soil_ind_heavyclay.value()))
        self.module.set_parameter("soil_orc_sand", float(self.ui.soil_orc_sand.value()))
        self.module.set_parameter("soil_orc_sandclay", float(self.ui.soil_orc_sandclay.value()))
        self.module.set_parameter("soil_orc_medclay", float(self.ui.soil_orc_medclay.value()))
        self.module.set_parameter("soil_orc_heavyclay", float(self.ui.soil_orc_heavyclay.value()))

        # CUSTOM
        self.module.set_parameter("suit_custom_include", int(self.ui.suit_custom_check.isChecked()))
        self.module.set_parameter("suit_custom_data", self.ui.suit_custom_data.currentText())
        self.module.set_parameter("suit_custom_weight", int(self.ui.suit_custom_weight.value()))
        self.module.set_parameter("custom_trend",
                                  ubglobals.VALUE_SCALE_METHODS[self.ui.custom_trend_combo.currentIndex()])
        self.module.set_parameter("custom_midpoint", int(self.ui.custom_include_midpoints.isChecked()))
        self.module.set_parameter("custom_res_min", float(self.ui.custom_res_min.text()))
        self.module.set_parameter("custom_res_max", float(self.ui.custom_res_max.text()))
        self.module.set_parameter("custom_res_mid", float(self.ui.custom_res_midpoint.text()))
        self.module.set_parameter("custom_com_min", float(self.ui.custom_com_min.text()))
        self.module.set_parameter("custom_com_max", float(self.ui.custom_com_max.text()))
        self.module.set_parameter("custom_com_mid", float(self.ui.custom_com_midpoint.text()))
        self.module.set_parameter("custom_ind_min", float(self.ui.custom_ind_min.text()))
        self.module.set_parameter("custom_ind_max", float(self.ui.custom_ind_max.text()))
        self.module.set_parameter("custom_ind_mid", float(self.ui.custom_ind_midpoint.text()))
        self.module.set_parameter("custom_orc_min", float(self.ui.custom_orc_min.text()))
        self.module.set_parameter("custom_orc_max", float(self.ui.custom_orc_max.text()))
        self.module.set_parameter("custom_orc_mid", float(self.ui.custom_orc_midpoint.text()))

        # TAB 2 - 2.3 Zoning
        self.module.set_parameter("zoning_export", int(self.ui.zoning_export.isChecked()))
        self.module.set_parameter("zoning_water",
                                  self.lakemaps[1][self.ui.zoning_constraints_water_combo.currentIndex()])
        self.module.set_parameter("zoning_heritage",
                                  self.overlaymaps[1][self.ui.zoning_constraints_heritage_combo.currentIndex()])
        self.module.set_parameter("zoning_public",
                                  self.overlaymaps[1][self.ui.zoning_constraints_public_combo.currentIndex()])
        self.module.set_parameter("zoning_enviro",
                                  self.overlaymaps[1][self.ui.zoning_constraints_enviro_combo.currentIndex()])
        self.module.set_parameter("zoning_flood",
                                  self.overlaymaps[1][self.ui.zoning_constraints_flood_combo.currentIndex()])
        self.module.set_parameter("zoning_custom",
                                  self.overlaymaps[1][self.ui.zoning_constraints_custom_combo.currentIndex()])

        self.module.set_parameter("zoning_heritage_res", int(self.ui.zoning_constraints_heritage_res.isChecked()))
        self.module.set_parameter("zoning_heritage_com", int(self.ui.zoning_constraints_heritage_com.isChecked()))
        self.module.set_parameter("zoning_heritage_ind", int(self.ui.zoning_constraints_heritage_ind.isChecked()))
        self.module.set_parameter("zoning_heritage_orc", int(self.ui.zoning_constraints_heritage_orc.isChecked()))

        self.module.set_parameter("zoning_public_res", int(self.ui.zoning_constraints_public_res.isChecked()))
        self.module.set_parameter("zoning_public_com", int(self.ui.zoning_constraints_public_com.isChecked()))
        self.module.set_parameter("zoning_public_ind", int(self.ui.zoning_constraints_public_ind.isChecked()))
        self.module.set_parameter("zoning_public_orc", int(self.ui.zoning_constraints_public_orc.isChecked()))

        self.module.set_parameter("zoning_enviro_res", int(self.ui.zoning_constraints_enviro_res.isChecked()))
        self.module.set_parameter("zoning_enviro_com", int(self.ui.zoning_constraints_enviro_com.isChecked()))
        self.module.set_parameter("zoning_enviro_ind", int(self.ui.zoning_constraints_enviro_ind.isChecked()))
        self.module.set_parameter("zoning_enviro_orc", int(self.ui.zoning_constraints_enviro_orc.isChecked()))

        self.module.set_parameter("zoning_flood_res", int(self.ui.zoning_constraints_flood_res.isChecked()))
        self.module.set_parameter("zoning_flood_com", int(self.ui.zoning_constraints_flood_com.isChecked()))
        self.module.set_parameter("zoning_flood_ind", int(self.ui.zoning_constraints_flood_ind.isChecked()))
        self.module.set_parameter("zoning_flood_orc", int(self.ui.zoning_constraints_flood_orc.isChecked()))

        self.module.set_parameter("zoning_custom_res", int(self.ui.zoning_constraints_custom_res.isChecked()))
        self.module.set_parameter("zoning_custom_com", int(self.ui.zoning_constraints_custom_com.isChecked()))
        self.module.set_parameter("zoning_custom_ind", int(self.ui.zoning_constraints_custom_ind.isChecked()))
        self.module.set_parameter("zoning_custom_orc", int(self.ui.zoning_constraints_custom_orc.isChecked()))

        self.module.set_parameter("zoning_rules_resmap", self.lumaps[1][self.ui.zoning_rules_rescombo.currentIndex()])
        self.module.set_parameter("zoning_rules_resauto", int(self.ui.zoning_rules_resauto.isChecked()))
        self.module.set_parameter("zoning_rules_reslimit", int(self.ui.zoning_rules_reslimit.isChecked()))
        self.module.set_parameter("zoning_rules_respassive", int(self.ui.zoning_rules_respassive.isChecked()))

        self.module.set_parameter("zoning_rules_commap", self.lumaps[1][self.ui.zoning_rules_comcombo.currentIndex()])
        self.module.set_parameter("zoning_rules_comauto", int(self.ui.zoning_rules_comauto.isChecked()))
        self.module.set_parameter("zoning_rules_comlimit", int(self.ui.zoning_rules_comlimit.isChecked()))
        self.module.set_parameter("zoning_rules_compassive", int(self.ui.zoning_rules_compassive.isChecked()))

        self.module.set_parameter("zoning_rules_indmap", self.lumaps[1][self.ui.zoning_rules_indcombo.currentIndex()])
        self.module.set_parameter("zoning_rules_indauto", int(self.ui.zoning_rules_indauto.isChecked()))
        self.module.set_parameter("zoning_rules_indlimit", int(self.ui.zoning_rules_indlimit.isChecked()))
        self.module.set_parameter("zoning_rules_indpassive", int(self.ui.zoning_rules_indpassive.isChecked()))

        self.module.set_parameter("zoning_rules_officesmap",
                                  self.lumaps[1][self.ui.zoning_rules_officescombo.currentIndex()])
        self.module.set_parameter("zoning_rules_officesauto", int(self.ui.zoning_rules_officesauto.isChecked()))
        self.module.set_parameter("zoning_rules_officeslimit", int(self.ui.zoning_rules_officeslimit.isChecked()))
        self.module.set_parameter("zoning_rules_officespassive", int(self.ui.zoning_rules_officespassive.isChecked()))

        # NEIGHBOURHOOD EFFECT
        self.module.set_parameter("function_ids", self.ifo_selection)
        if self.ui.ee_noaccount.isChecked():
            self.module.set_parameter("edge_effects_method", "NA")
        elif self.ui.ee_averaging.isChecked():
            self.module.set_parameter("edge_effects_method", "AVG")
        elif self.ui.ee_proportioning.isChecked():
            self.module.set_parameter("edge_effects_method", "PP")
        else:
            self.module.set_parameter("edge_effects_method", "PPAVG")

        # TAB 3 - URBAN DYNAMICS
        # TAB 3.1 - External Drivers
        if self.ui.pop_method_rate.isChecked():
            self.module.set_parameter("pop_growthmethod", "C")
        else:
            self.module.set_parameter("pop_growthmethod", "F")

        self.module.set_parameter("pop_birthrate", float(self.ui.input_birthrate_spin.value()))
        # self.module.set_parameter("pop_birthfunction", self.poptrends[self.ui.input_birthrate_function.currentIndex()])
        self.module.set_parameter("pop_deathrate", float(self.ui.input_deathrate_spin.value()))
        # self.module.set_parameter("pop_deathfunction", self.poptrends[self.ui.input_deathrate_function.currentIndex()])
        self.module.set_parameter("pop_migration", float(self.ui.input_migration_spin.value()))
        # self.module.set_parameter("pop_migrationfunction", self.poptrends[self.ui.input_migration_function.currentIndex()])

        self.module.set_parameter("employ_com_roc", float(self.ui.employ_rate_spin.value()))
        self.module.set_parameter("employ_ind_rocbool", int(self.ui.employ_rate_ind_check.isChecked()))
        self.module.set_parameter("employ_ind_roc", float(self.ui.employ_rate_ind_spin.value()))
        self.module.set_parameter("employ_orc_rocbool", int(self.ui.employ_rate_orc_check.isChecked()))
        self.module.set_parameter("employ_orc_roc", float(self.ui.employ_rate_orc_spin.value()))

        # TAB 3.2 - Internal Drivers
        self.module.set_parameter("alpha", float(self.ui.stoch_box.value()))

        self.module.set_parameter("recalc_nhd", int(self.ui.dynamics_recalculate_nhd.isChecked()))
        self.module.set_parameter("recalc_stoch", int(self.ui.dynamics_recalculate_stoch.isChecked()))

        self.module.set_parameter("vpot_eqn", ubglobals.VPOT[int(self.ui.dynamics_lpot_eqn_combo.currentIndex())])
        self.module.set_parameter("vpot_zeropot", int(self.ui.dynamics_lpot_zeropot_check.isChecked()))
        self.module.set_parameter("vpot_negpot", int(self.ui.dynamics_lpot_negativepot_check.isChecked()))

        # TAB 3.3 - Transition Rules
        self.module.set_parameter("res_inertia", float(self.ui.res_inertia_spin.value()))
        self.module.set_parameter("res_delta", float(self.ui.res_sensitivity_delta_spin.value()))
        self.module.set_parameter("res_lambda", float(self.ui.res_sensitivity_lambda_spin.value()))
        self.module.set_parameter("res_maxdensity", float(self.ui.res_maxdens_spin.value()))
        self.module.set_parameter("res_maxdens_auto", int(self.ui.res_maxdens_auto.isChecked()))
        self.module.set_parameter("res_mindensity", float(self.ui.res_mindens_spin.value()))

        self.module.set_parameter("com_inertia", float(self.ui.com_inertia_spin.value()))
        self.module.set_parameter("com_delta", float(self.ui.com_sensitivity_delta_spin.value()))
        self.module.set_parameter("com_lambda", float(self.ui.com_sensitivity_lambda_spin.value()))
        self.module.set_parameter("com_maxdensity", float(self.ui.com_maxdens_spin.value()))
        self.module.set_parameter("com_maxdens_auto", int(self.ui.com_maxdens_auto.isChecked()))
        self.module.set_parameter("com_mindensity", float(self.ui.com_mindens_spin.value()))

        self.module.set_parameter("ind_inertia", float(self.ui.ind_inertia_spin.value()))
        self.module.set_parameter("ind_delta", float(self.ui.ind_sensitivity_delta_spin.value()))
        self.module.set_parameter("ind_lambda", float(self.ui.ind_sensitivity_lambda_spin.value()))
        self.module.set_parameter("ind_maxdensity", float(self.ui.ind_maxdens_spin.value()))
        self.module.set_parameter("ind_maxdens_auto", int(self.ui.ind_maxdens_auto.isChecked()))
        self.module.set_parameter("ind_mindensity", float(self.ui.ind_mindens_spin.value()))

        self.module.set_parameter("orc_inertia", float(self.ui.orc_inertia_spin.value()))
        self.module.set_parameter("orc_delta", float(self.ui.orc_sensitivity_delta_spin.value()))
        self.module.set_parameter("orc_lambda", float(self.ui.orc_sensitivity_lambda_spin.value()))
        self.module.set_parameter("orc_maxdensity", float(self.ui.orc_maxdens_spin.value()))
        self.module.set_parameter("orc_maxdens_auto", int(self.ui.orc_maxdens_auto.isChecked()))
        self.module.set_parameter("orc_mindensity", float(self.ui.orc_mindens_spin.value()))

        self.module.set_parameter("pg_penalise", int(self.ui.pg_penalty_check.isChecked()))
        self.module.set_parameter("pg_inertia", float(self.ui.pg_penalty_inertia.value()))
        self.module.set_parameter("pg_provision", int(self.ui.pg_provision_check.isChecked()))
        self.module.set_parameter("pg_proportion", float(self.ui.pg_provision_spin.value()))
        self.module.set_parameter("pg_current", int(self.ui.pg_provision_current_check.isChecked()))

        self.module.set_parameter("ref_penalise", int(self.ui.ref_penalty_check.isChecked()))
        self.module.set_parameter("ref_inertia", float(self.ui.ref_penalty_inertia.value()))
        self.module.set_parameter("ref_provision", int(self.ui.ref_provision_check.isChecked()))
        self.module.set_parameter("ref_proportion", float(self.ui.ref_provision_spin.value()))
        self.module.set_parameter("ref_current", int(self.ui.ref_provision_current_check.isChecked()))
        return True


class InfluenceFunctionGUILaunch(QtWidgets.QDialog):
    """The class definition for the sub-GUI for defining influence functions. This sub-gui launches if the add button
    or edit button is clicked in the Urban Development Module - Neighbourhood Effect dialog window."""
    def __init__(self, simulation, projectlog, viewmode=0, parent=None):
        """Initialization of the subGUI for defining influence functions. This sub-gui is launched and filled with
        the current influence function selected from the table unless a new function is launched.

        :param simulation: reference to the current UrbanBEATS Simulation active
        :param projectlog: reference to the active project log in the UrbanBEATS Simulation
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_InfluenceFunctionDialog()
        self.ui.setupUi(self)
        self.simulation = simulation
        self.projectlog = projectlog
        self.functionlist = []
        self.datainputmethods = ["none", "temp", "manual", "pattern", "existing"]
        self.update_function_combobox()
        self.current_active_ifobject = None

        self.ui.define_luc_combo.clear()
        [self.ui.define_luc_combo.addItem(str(ubglobals.ACTIVELANDUSENAMES[i]))
         for i in range(len(ubglobals.ACTIVELANDUSENAMES))]

        self.ui.influence_luc_combo.clear()
        [self.ui.influence_luc_combo.addItem(str(ubglobals.UM_LUCNAMES[i]))
         for i in range(len(ubglobals.UM_LUCNAMES))]

        # SIGNALS AND SLOTS
        self.ui.select_combo.currentIndexChanged.connect(self.update_if_gui)
        self.ui.datatable.itemChanged.connect(self.update_plot)
        self.ui.datainputmethod_combo.currentIndexChanged.connect(self.update_inputmethod)
        self.ui.datapoints_spin.valueChanged.connect(self.update_data_table_rows)
        self.ui.savefunction_button.clicked.connect(self.save_current_function)
        self.ui.exportfunction_button.clicked.connect(self.export_current_function)
        self.ui.deletefunction_button.clicked.connect(self.delete_current_function)
        self.ui.standardlib_combo.currentIndexChanged.connect(self.pre_fill_gui)

        # ACTIVATE THE CURRENT FUNCTION TO VIEW. THIS IS CALLED WHEN THE GUI IS BEING OPENED FOR VIEWING PURPOSES.
        if viewmode != 0:
            self.ui.select_combo.setCurrentIndex((viewmode))
            self.ui.select_combo.setEnabled(0)      # Disable the combo box!
            self.ui.deletefunction_button.setEnabled(0)     # Disable controls!
            self.ui.exportfunction_button.setEnabled(0)     # Disable controls!

    def update_function_combobox(self):
        """Updates the combo box with selection options for functions."""
        self.functionlist = self.simulation.get_all_function_objects_of_type("IF")
        self.ui.select_combo.clear()
        self.ui.select_combo.addItem("<no selection>")
        for i in range(len(self.functionlist)):
            self.ui.select_combo.addItem(str(self.functionlist[i].get_function_name()))
        self.ui.select_combo.addItem("<create new function>")
        self.ui.select_combo.setCurrentIndex(0)
        self.set_if_gui_to_init_state()

    def set_if_gui_to_init_state(self):
        """Updates the current GUI."""
        self.ui.functionname_box.clear()
        self.ui.datainputmethod_combo.setCurrentIndex(0)
        self.ui.define_luc_combo.setCurrentIndex(0)
        self.ui.influence_luc_combo.setCurrentIndex(0)
        self.ui.datatable.setRowCount(0)
        self.ui.datapoints_spin.setValue(2)
        self.ui.input_widget.setEnabled(0)
        self.ui.webView.setHtml("")
        self.ui.view_widget.setEnabled(0)

    def update_if_gui(self):
        """Updates the GUI based on the current index of the combo box."""
        self.functionlist = self.simulation.get_all_function_objects_of_type("IF")
        if self.ui.select_combo.currentIndex() in [-1, 0]:
            # CASE 1 - NO SELECTION - DISABLE EVERYTHING
            self.set_if_gui_to_init_state()
        elif self.ui.select_combo.currentIndex() == len(self.functionlist) + 1:
            # CASE 2 - CREATE A NEW FUNCTION
            self.set_if_gui_to_init_state()
            self.ui.input_widget.setEnabled(1)
            self.ui.webView.setHtml("")
            self.ui.view_widget.setEnabled(1)
            self.ui.savefunction_button.setEnabled(1)
            self.ui.deletefunction_button.setEnabled(0)
            self.ui.exportfunction_button.setEnabled(0)
        else:
            # CASE 3 - A FUNCTION WAS SELECTED, VIEW THE FUNCTION
            self.set_if_gui_to_init_state()
            self.ui.input_widget.setEnabled(0)
            self.ui.view_widget.setEnabled(1)
            self.ui.savefunction_button.setEnabled(0)
            self.ui.deletefunction_button.setEnabled(1)
            self.ui.exportfunction_button.setEnabled(1)
            self.update_ui_from_comboselect()

    def update_ui_from_comboselect(self):
        """Updates the UI based on the currently selected Influence Function."""
        self.current_active_ifobject = self.functionlist[self.ui.select_combo.currentIndex() - 1]
        self.update_gui_from_ifobject(self.current_active_ifobject)
        self.ui.datainputmethod_combo.setCurrentIndex(0)
        self.ui.standardlib_lbl.setText("Template")
        self.ui.standardlib_combo.setCurrentIndex(0)

    def update_inputmethod(self):
        """Updates the GUI based on the data input method."""
        datainputmethod = self.datainputmethods[self.ui.datainputmethod_combo.currentIndex()]
        if datainputmethod == "none":
            self.ui.standardlib_lbl.setText("Template")
            self.ui.standardlib_combo.setEnabled(0)
            self.ui.standardlib_combo.clear()
            self.ui.standardlib_combo.addItem("<none>")
            self.ui.standardlib_combo.setCurrentIndex(0)
            pass    # Do nothing
        elif datainputmethod == "temp":     # Open file dialog to browse for template
            self.ui.standardlib_lbl.setText("Template")
            self.ui.standardlib_combo.setEnabled(0)
            self.ui.standardlib_combo.clear()
            self.ui.standardlib_combo.addItem("<none>")
            self.ui.standardlib_combo.setCurrentIndex(0)
            datatype = "IF File (*.ubif)"
            message = "Browse for Influence Function..."
            datafile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir, datatype)
            if datafile:
                self.current_active_ifobject = ubdatatypes.NeighbourhoodInfluenceFunction(0)
                self.current_active_ifobject.create_from_ubif(datafile)
                self.update_gui_from_ifobject(self.current_active_ifobject)
            else:
                self.ui.datainputmethod_combo.setCurrentIndex(0)
        elif datainputmethod == "manual":
            self.ui.standardlib_lbl.setText("Template")
            self.ui.standardlib_combo.setEnabled(0)
            self.ui.standardlib_combo.clear()
            self.ui.standardlib_combo.addItem("<none>")
            self.ui.standardlib_combo.setCurrentIndex(0)
            self.current_active_ifobject = ubdatatypes.NeighbourhoodInfluenceFunction()
            self.update_gui_from_ifobject(self.current_active_ifobject)
        elif datainputmethod == "pattern":      # [TO DO] NEED TO FIGURE OUT PATTERNS
            self.ui.standardlib_lbl.setText("Select Standard Pattern")
            self.ui.standardlib_combo.setEnabled(1)
            self.ui.standardlib_combo.clear()
            self.ui.standardlib_combo.addItem("<none>")
            self.ui.standardlib_combo.setCurrentIndex(0)
            self.current_active_ifobject = ubdatatypes.NeighbourhoodInfluenceFunction()
            self.update_gui_from_ifobject(self.current_active_ifobject)
        elif datainputmethod == "existing":
            self.ui.standardlib_lbl.setText("Select Function")
            self.ui.standardlib_combo.setEnabled(1)
            self.ui.standardlib_combo.clear()
            self.ui.standardlib_combo.addItem("<none>")
            self.ui.standardlib_combo.setCurrentIndex(0)
            [self.ui.standardlib_combo.addItem(str(self.functionlist[i].get_function_name()))
             for i in range(len(self.functionlist))]
            self.current_active_ifobject = ubdatatypes.NeighbourhoodInfluenceFunction()
            self.update_gui_from_ifobject(self.current_active_ifobject)

    def pre_fill_gui(self):
        """Prefills the GUI with data from the function selected in the existing functions list."""
        datainputmethod = self.datainputmethods[self.ui.datainputmethod_combo.currentIndex()]
        if self.ui.standardlib_combo.currentIndex() in [-1, 0]:
            return True
        if datainputmethod == "existing":
            ifo = self.functionlist[self.ui.standardlib_combo.currentIndex() - 1]
            self.update_gui_from_ifobject(ifo)
            self.ui.functionname_box.setText("unnamed")
        elif datainputmethod == "patern":
            pass

    def update_gui_from_ifobject(self, ifo):
        """Updates the GUI elements with the current data available in the active if_object passed to the function."""
        self.ui.functionname_box.setText(str(ifo.get_function_name()))
        self.ui.define_luc_combo.setCurrentIndex(ubglobals.ACTIVELANDUSEABBR.index(ifo.origin_landuse))
        self.ui.influence_luc_combo.setCurrentIndex(ubglobals.UM_LUCABBRS.index(ifo.target_landuse))
        self.ui.datapoints_spin.setValue(ifo.datapoints)
        self.ui.datatable.setRowCount(0)
        while self.ui.datatable.rowCount() < ifo.datapoints:
            self.ui.datatable.insertRow(0)
        xy = ifo.get_xy_data()
        for i in range(ifo.datapoints):
            twiX = QtWidgets.QTableWidgetItem()
            twiX.setText(str(xy[0][i]))
            self.ui.datatable.setItem(i, 0, twiX)
            twiY = QtWidgets.QTableWidgetItem()
            twiY.setText(str(xy[1][i]))
            self.ui.datatable.setItem(i, 1, twiY)
        self.update_plot()
        return True

    def save_current_function(self):
        """Saves the current GUI settings, defined by the current active IF object to the project's database."""
        # Get Table Data first to determine whether to save the data or not, throw an error if not.
        xdata = []
        ydata = []
        error = False
        for i in range(self.ui.datatable.rowCount()):
            if self.ui.datatable.item(i, 0) is None or self.ui.datatable.item(i, 1) is None:
                error = True
                continue
            else:
                xdata.append(float(self.ui.datatable.item(i,0).text()))
                ydata.append(float(self.ui.datatable.item(i,1).text()))
        if error:
            prompt_msg = "Error: Cannot save influence function. Table data is incomplete!"
            QtWidgets.QMessageBox.warning(self, 'Incomplete Function Data', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        self.current_active_ifobject.set_function_name(self.ui.functionname_box.text())
        self.current_active_ifobject.origin_landuse = \
            ubglobals.ACTIVELANDUSEABBR[self.ui.define_luc_combo.currentIndex()]
        self.current_active_ifobject.target_landuse = \
            ubglobals.UM_LUCABBRS[self.ui.influence_luc_combo.currentIndex()]
        self.current_active_ifobject.assign_xy_data(xdata, ydata)
        if self.current_active_ifobject.get_id() == None:
            functions = self.simulation.get_all_function_objects_of_type("IF")
            self.current_active_ifobject.assign_id("fx_" + str(len(functions)))
            self.simulation.add_new_function_to_library(self.current_active_ifobject)
            self.ui.select_combo.setCurrentIndex(0)
            self.update_function_combobox()

    def update_data_table_rows(self):
        """Updates the data table rows to reflect the number in the spin button."""
        if int(self.ui.datapoints_spin.value()) > self.ui.datatable.rowCount():
            while int(self.ui.datapoints_spin.value()) > self.ui.datatable.rowCount():
                self.ui.datatable.insertRow(self.ui.datatable.rowCount())
        elif int(self.ui.datapoints_spin.value()) < self.ui.datatable.rowCount():
            while int(self.ui.datapoints_spin.value()) < self.ui.datatable.rowCount():
                self.ui.datatable.removeRow(self.ui.datatable.rowCount()-1)
        else:
            pass    # Rows are equal, do nothing

    def export_current_function(self):
        """Exports the current function to a .ubif file to be saved in the directory selected by the user."""
        if self.ui.select_combo.currentIndex() in [0, self.ui.select_combo.count()-1]:
            return True

        datatype = "IF File (*.ubif)"
        message = "Export to .ubif file, choose location..."
        datafile, _filter = QtWidgets.QFileDialog.getSaveFileName(self, message, os.curdir, datatype)
        if datafile and not self.current_active_ifobject is None:
            self.current_active_ifobject.export_function_to_ubif(datafile)
            prompt_msg = "Function successfully exported!"
            QtWidgets.QMessageBox.information(self, 'Export Complete', prompt_msg, QtWidgets.QMessageBox.Ok)

    def delete_current_function(self):
        """Deletes the current active selection, removes this selection from the project."""
        if self.ui.select_combo.currentIndex() in [0, self.ui.select_combo.count() - 1]:
            return True

        if not self.current_active_ifobject is None:
            fid = self.current_active_ifobject.get_id()
            self.simulation.remove_function_object_with_id(fid)
            self.ui.select_combo.setCurrentIndex(0)
            self.update_function_combobox()

    def update_plot(self):
        """Updates the plot in the viewer to reflect the changes in the data table. If the program cannot plot, it
        quits updating and leaves the existing plot showing."""
        # Get the X and Y data from the table
        plotdata = []
        for i in range(self.ui.datatable.rowCount()):
            xy = [self.ui.datatable.item(i, 0), self.ui.datatable.item(i, 1)]
            if None in xy or xy[0].text() == "" or xy[1].text() == "":
                return True
            else:
                plotdata.append([float(xy[0].text()), float(xy[1].text())])
        plotname = self.ui.functionname_box.text()

        html = """
        <!DOCTYPE HTML>
        <html>
	    <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>"""+plotname+"""</title>

		    <style type="text/css">
            #container {
                min-width: 100%;
                max-width: 100%;
                height: 100%;
                margin: 0 auto
            }
            </style>
        </head>
        <body>
        <script src="file:///C:\Users\peter\Documents\Coding Projects\UrbanBEATS-PSS\libs\highcharts\code\highcharts.js"></script>
        
        <div id="container"></div>
        
                <script type="text/javascript">
        Highcharts.chart('container', {
        
            title: {
                text: 'Influence Function'
            },
        
            yAxis: {
                title: {
                    text: 'Weight'
                }
            },
            
            xAxis: {
                title: {
                text: 'Distance [km]'
              }
            },
        
            series: [{
                name: '"""+str(plotname)+"""',
                data: """+str(plotdata)+"""
            }],
        
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    
                }]
            }
        
        });
                </script>
            </body>
        </html>
        """
        self.ui.webView.setHtml(html)

