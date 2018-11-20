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
from md_urbplanbbgui import Ui_Urbplanbb_Dialog


# --- MAIN GUI FUNCTION ---
class UrbplanbbGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Urbplanbb_Dialog()
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
        self.pixmap_ref = [":/images/images/md_urbplanbb_general.jpg",
                           ":/images/images/md_urbplanbb_residential.jpg",
                           ":/images/images/md_urbplanbb_nonres.jpg",
                           ":/images/images/md_urbplanbb_roads.jpg",
                           ":/images/images/md_urbplanbb_openspaces.jpg",
                           ":/images/images/md_urbplanbb_others.jpg"]
        self.adjust_module_img()

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
        self.employmaps = self.get_dataref_array("spatial", "Employment")  # Obtain the data ref array
        self.ui.employment_combo.clear()  # Clear the combo box first before setting it up
        # Set up the combo box (note: this also includes the no map option)
        [self.ui.employment_combo.addItem(str(self.employmaps[0][i])) for i in range(len(self.employmaps[0]))]

        self.localitymaps = self.get_dataref_array("spatial", "Employment")  # Obtain the data ref array
        self.ui.locality_combo.clear()  # Clear the combo box first before setting it up
        # Set up the combo box (note: this also includes the no map option)
        [self.ui.locality_combo.addItem(str(self.localitymaps[0][i])) for i in range(len(self.localitymaps[0]))]

        self.roadmaps = self.get_dataref_array("spatial", "Built Infrastructure", "Road Network")
        self.ui.roadnet_combo.clear()   # Clear the combo box first before setting it up
        # Set up the combo box (note: this also includes the 'no map' option)
        [self.ui.roadnet_combo.addItem(str(self.roadmaps[0][i])) for i in range(len(self.roadmaps[0]))]

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        self.ui.parameters.currentChanged.connect(self.adjust_module_img)   # Changes the module's image

        # Tab 1 - General
        self.ui.plan_params_preload.clicked.connect(self.enable_disable_devchecks)
        self.ui.plan_params_predef.clicked.connect(self.enable_disable_devchecks)
        self.ui.plan_params_citycombo.currentIndexChanged.connect(self.pre_fill_parameters)
        self.ui.plan_params_filebox.textChanged.connect(self.pre_fill_parameters)
        self.ui.lucredevelop_check.clicked.connect(self.enable_disable_devchecks)
        self.ui.popredevelop_check.clicked.connect(self.enable_disable_devchecks)
        self.ui.noredevelop_check.clicked.connect(self.enable_disable_devchecks)
        self.ui.emp_fud.clicked.connect(self.enable_disable_devchecks)

        # Tab 2 - Residential
        self.ui.allot_depth_check.clicked.connect(self.enable_disable_residential)
        self.ui.drainage_rule_check.clicked.connect(self.enable_disable_residential)
        self.ui.roof_connected_radiodirect.clicked.connect(self.enable_disable_residential)
        self.ui.roof_connected_radiodisc.clicked.connect(self.enable_disable_residential)
        self.ui.roof_connected_radiovary.clicked.connect(self.enable_disable_residential)

        # Tab 3 - Non-Residential
        self.ui.jobs_direct_radio.clicked.connect(self.adjust_employment_stack)
        self.ui.jobs_dist_radio.clicked.connect(self.adjust_employment_stack)
        self.ui.jobs_total_radio.clicked.connect(self.adjust_employment_stack)
        self.ui.nres_setback_auto.clicked.connect(self.enable_disable_nonres)
        self.ui.nres_maxfloors_nolimit.clicked.connect(self.enable_disable_nonres)
        self.ui.plotratio_ind_slider.valueChanged.connect(self.set_nonres_plotratio_boxupdate)
        self.ui.plotratio_com_slider.valueChanged.connect(self.set_nonres_plotratio_boxupdate)
        self.ui.civ_consider_check.clicked.connect(self.enable_disable_civic)
        self.ui.civ_customise.clicked.connect(self.launch_civ_customisation_gui)

        # Tab 4 - Roads and Transport
        self.ui.ma_buffer_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.ma_fpath_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.ma_nstrip_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.ma_sidestreet_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.ma_bicycle_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.ma_travellane_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.ma_centralbuffer_check.clicked.connect(self.enable_disable_majorarterials)
        self.ui.pt_centralbuffer.clicked.connect(self.enable_disable_majorarterials)
        self.ui.hwy_different_check.clicked.connect(self.enable_disable_highways)
        self.ui.hwy_verge_check.clicked.connect(self.enable_disable_highways)
        self.ui.hwy_service_check.clicked.connect(self.enable_disable_highways)
        self.ui.hwy_travellane_check.clicked.connect(self.enable_disable_highways)
        self.ui.hwy_centralbuffer_check.clicked.connect(self.enable_disable_highways)
        self.ui.consider_transport.clicked.connect(self.enable_disable_transport)
        self.ui.trans_customise.clicked.connect(self.launch_civ_customisation_gui)

        # Tab 5 - Open Spaces
        self.ui.pg_ggratio_slide.valueChanged.connect(self.set_greengreyratio_boxupdate)
        self.ui.svu_slider.valueChanged.connect(self.set_svu_waternonwater_boxupdate)
        self.ui.ref_usable_check.clicked.connect(self.enable_disable_openspaces)
        self.ui.svu_supply_check.clicked.connect(self.enable_disable_openspaces)
        self.ui.svu_waste_check.clicked.connect(self.enable_disable_openspaces)
        self.ui.svu_storm_check.clicked.connect(self.enable_disable_openspaces)

        # Tab 6 - Other Uses
        self.ui.unc_merge_check.clicked.connect(self.enable_disable_others)
        self.ui.unc_merge2pg_check.clicked.connect(self.enable_disable_others)
        self.ui.unc_merge2ref_check.clicked.connect(self.enable_disable_others)
        self.ui.unc_merge2trans_check.clicked.connect(self.enable_disable_others)
        self.ui.unc_custom_check.clicked.connect(self.enable_disable_others)
        self.ui.und_statemanual_radio.clicked.connect(self.enable_disable_others)
        self.ui.und_stateauto_radio.clicked.connect(self.enable_disable_others)

        # Others
        self.ui.buttonBox.accepted.connect(self.save_values)

    def adjust_module_img(self):
        """Changes the module's image based on the currently selected tab in the GUI."""
        self.ui.module_img.setPixmap(QtGui.QPixmap(self.pixmap_ref[self.ui.parameters.currentIndex()]))

    def launch_civ_customisation_gui(self):
        """Launches the advanced options for customising Civic Facilities in UrbanBEATS."""
        pass    # [TO DO]

    def enable_disable_residential(self):
        """Enables and disables respective GUI elements depending on what the user clicks."""
        if self.ui.allot_depth_check.isChecked():
            self.ui.allot_depth_box.setText("40.0")
            self.ui.allot_depth_box.setEnabled(0)
        else:
            self.ui.allot_depth_box.setEnabled(1)

        if self.ui.drainage_rule_check.isChecked():
            self.ui.roof_connected_radiodirect.setEnabled(1)
            self.ui.roof_connected_radiodisc.setEnabled(1)
            self.ui.roof_connected_radiovary.setEnabled(1)
            self.ui.avg_imp_dced_spin.setEnabled(1)
            self.ui.roofdced_vary_spin.setEnabled(self.ui.roof_connected_radiovary.isChecked())
        else:
            self.ui.roof_connected_radiodirect.setEnabled(0)
            self.ui.roof_connected_radiodisc.setEnabled(0)
            self.ui.roof_connected_radiovary.setEnabled(0)
            self.ui.avg_imp_dced_spin.setEnabled(0)
            self.ui.roofdced_vary_spin.setEnabled(0)

    def enable_disable_devchecks(self):
        """Enables or disables the Block redevelopment features based on the state of the checkboxes. General Tab."""
        self.ui.plan_params_filebox.setEnabled(self.ui.plan_params_preload.isChecked())
        self.ui.plan_params_filebrowse.setEnabled(self.ui.plan_params_preload.isChecked())
        self.ui.plan_params_citycombo.setEnabled(self.ui.plan_params_predef.isChecked())
        self.ui.employment_combo.setEnabled(int(not self.ui.emp_fud.isChecked()))
        if self.ui.noredevelop_check.isChecked():
            self.ui.lucredevelop_check.setEnabled(0)
            self.ui.popredevelop_check.setEnabled(0)
            self.ui.lucredevelop_spin.setEnabled(0)
            self.ui.popredevelop_spin.setEnabled(0)
        else:
            self.ui.lucredevelop_check.setEnabled(1)
            self.ui.popredevelop_check.setEnabled(1)
            self.ui.lucredevelop_spin.setEnabled(self.ui.lucredevelop_check.isChecked())
            self.ui.popredevelop_spin.setEnabled(self.ui.popredevelop_check.isChecked())
        return True

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

    def pre_fill_parameters(self):
        """Pre-filling method, will set up the module with all values contained in the pre-loaded parameter file or
        settings. This method is called when the Combo box index is changed or a file has been browsed and entered into
        the text box on the GENERALS tab."""
        pass    # [TO DO]

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

        # Retrieve the Urbplanbb() Reference corresponding to the current year
        self.module = self.active_scenario.get_module_object("URBPLAN", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()
        return True

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""
        # TAB 1 - GENERAL PARAMETERS
        self.ui.plan_typology_combo.setCurrentIndex(ubglobals.PLANTYPES.index(self.module.get_parameter("plan_type")))

        if self.module.get_parameter("plan_template") == "PREDEF":
            self.ui.plan_params_predef.setChecked(1)
        else:
            self.ui.plan_params_preload.setChecked(1)

        self.ui.plan_params_citycombo.setCurrentIndex(ubglobals.PLANPARAMSET.index(
            self.module.get_parameter("plan_paramset")))

        self.ui.plan_params_filebox.setText(str(self.module.get_parameter("plan_paramfile")))

        try:    # EMPLOYMENT COMBO - retrieve the dataID from module
            self.ui.employment_combo.setCurrentIndex(self.employmaps[1].index(self.module.get_parameter("emp_map")))
        except ValueError:
            self.ui.employment_combo.setCurrentIndex(0)     # else the map must've been removed, set combo to zero index

        try:    # LOCALITY COMBO - retrieve the dataID from module
            self.ui.locality_combo.setCurrentIndex(self.localitymaps[1].index(self.module.get_parameter("local_map")))
        except ValueError:
            self.ui.locality_combo.setCurrentIndex(0)   # else the map must've been removed, set combo to zero index

        try:    # ROADMAP COMBO - retrieve the dataID from module
            self.ui.roadnet_combo.setCurrentIndex(self.roadmaps[1].index(self.module.get_parameter("roadnet_map")))
        except ValueError:
            self.ui.roadnet_combo.setCurrentIndex(0)

        self.ui.emp_fud.setChecked(int(self.module.get_parameter("emp_fud")))
        self.ui.locality_attref.setText(str(self.module.get_parameter("local_attref")))
        self.ui.roadnet_attref.setText(str(self.module.get_parameter("roadnet_attref")))

        if self.module.get_parameter("cityarchetype") == "MC":
            self.ui.citymono_radio.setChecked(1)
        else:
            self.ui.citypoly_radio.setChecked(1)

        self.ui.citysprawl_spin.setValue(float(self.module.get_parameter("citysprawl")))

        # --> Decision Variables for Block Dynamics
        self.ui.lucredevelop_check.setChecked(int(self.module.get_parameter("lucredev")))
        self.ui.popredevelop_check.setChecked(int(self.module.get_parameter("popredev")))
        self.ui.noredevelop_check.setChecked(int(self.module.get_parameter("noredev")))
        self.ui.lucredevelop_spin.setValue(int(self.module.get_parameter("lucredev_thresh")))
        self.ui.popredevelop_spin.setValue(int(self.module.get_parameter("popredev_thresh")))
        self.enable_disable_devchecks()

        # TAB 2 - RESIDENTIAL PLANNING PARAMETERS
        self.ui.occup_avg_box.setText(str(self.module.get_parameter("occup_avg")))
        self.ui.occup_max_box.setText(str(self.module.get_parameter("occup_max")))
        self.ui.person_space_box.setText(str(self.module.get_parameter("person_space")))
        self.ui.extra_comm_area_box.setText(str(self.module.get_parameter("extra_comm_area")))
        self.ui.allot_depth_box.setText(str(self.module.get_parameter("avg_allot_depth")))
        self.ui.allot_depth_check.setChecked(int(self.module.get_parameter("allot_depth_default")))
        self.ui.house_floors.setValue(int(self.module.get_parameter("floor_num_max")))
        self.ui.patio_area_max_box.setText(str(self.module.get_parameter("patio_area_max")))
        self.ui.patio_covered_box.setChecked(bool(int(self.module.get_parameter("patio_covered"))))
        self.ui.carports_max_box.setText(str(self.module.get_parameter("carports_max")))
        self.ui.garage_incl_box.setChecked(int(self.module.get_parameter("garage_incl")))
        self.ui.w_driveway_min_box.setText(str(self.module.get_parameter("w_driveway_min")))

        self.ui.setback_f_min_box.setText(str(self.module.get_parameter("setback_f_min")))
        self.ui.setback_f_max_box.setText(str(self.module.get_parameter("setback_f_max")))
        self.ui.setback_s_min_box.setText(str(self.module.get_parameter("setback_s_min")))
        self.ui.setback_s_max_box.setText(str(self.module.get_parameter("setback_s_max")))
        self.ui.fsetbackmed_check.setChecked(bool(int(self.module.get_parameter("setback_f_med"))))
        self.ui.ssetbackmed_check.setChecked(bool(int(self.module.get_parameter("setback_s_med"))))

        self.ui.occup_flat_avg_box.setText(str(self.module.get_parameter("occup_flat_avg")))
        self.ui.flat_area_max_box.setText(str(self.module.get_parameter("flat_area_max")))
        self.ui.indoor_com_spin.setValue(int(self.module.get_parameter("commspace_indoor")))
        self.ui.outdoor_com_spin.setValue(int(self.module.get_parameter("commspace_outdoor")))
        self.ui.aptbldg_floors.setValue(int(self.module.get_parameter("floor_num_HDRmax")))
        self.ui.setback_HDR_avg_box.setText(str(self.module.get_parameter("setback_HDR_avg")))

        if self.module.get_parameter("parking_HDR") == "On":
            self.ui.parking_on.setChecked(1)
        elif self.module.get_parameter("parking_HDR") == "Off":
            self.ui.parking_off.setChecked(1)
        elif self.module.get_parameter("parking_HDR") == "Var":
            self.ui.parking_vary.setChecked(1)
        elif self.module.get_parameter("parking_HDR") == "NA":
            self.ui.parking_none.setChecked(1)

        self.ui.OSR_parks_include.setChecked(int(self.module.get_parameter("park_OSR")))

        self.ui.w_resfootpath_min_box.setText(str(self.module.get_parameter("res_fpwmin")))
        self.ui.w_resfootpath_max_box.setText(str(self.module.get_parameter("res_fpwmax")))
        self.ui.w_resnaturestrip_min_box.setText(str(self.module.get_parameter("res_nswmin")))
        self.ui.w_resnaturestrip_max_box.setText(str(self.module.get_parameter("res_nswmax")))
        self.ui.w_resfootpath_med_check.setChecked(bool(int(self.module.get_parameter("res_fpmed"))))
        self.ui.w_resnaturestrip_med_check.setChecked(bool(int(self.module.get_parameter("res_nsmed"))))
        self.ui.w_reslane_min_box.setText(str(self.module.get_parameter("res_lanemin")))
        self.ui.w_reslane_max_box.setText(str(self.module.get_parameter("res_lanemax")))
        self.ui.w_reslane_med_check.setChecked(bool(int(self.module.get_parameter("res_lanemed"))))

        self.ui.drainage_rule_check.setChecked(int(self.module.get_parameter("define_drainage_rule")))

        if self.module.get_parameter("roof_connected") == "Direct":
            self.ui.roof_connected_radiodirect.setChecked(1)
        elif self.module.get_parameter("roof_connected") == "Disconnect":
            self.ui.roof_connected_radiodisc.setChecked(1)
        elif self.module.get_parameter("roof_connected") == "Vary":
            self.ui.roof_connected_radiovary.setChecked(1)

        self.ui.roofdced_vary_spin.setValue(int(self.module.get_parameter("roof_dced_p")))
        self.ui.avg_imp_dced_spin.setValue(int(self.module.get_parameter("imperv_prop_dced")))
        self.enable_disable_residential()

        # TAB 3 - NON-RESIDENTIAL PLANNING PARAMETERS
        if self.module.get_parameter("employment_mode") == "I":
            self.ui.jobs_direct_radio.setChecked(1)
        elif self.module.get_parameter("employment_mode") == "D":
            self.ui.jobs_dist_radio.setChecked(1)
        elif self.module.get_parameter("employment_mode") == "S":
            self.ui.jobs_total_radio.setChecked(1)
        self.adjust_employment_stack()

        self.ui.dist_ind_spin.setValue(int(self.module.get_parameter("ind_edist")))
        self.ui.dist_com_spin.setValue(int(self.module.get_parameter("com_edist")))
        self.ui.dist_orc_spin.setValue(int(self.module.get_parameter("orc_edist")))
        self.ui.totjobs_box.setText(str(self.module.get_parameter("employment_total")))

        self.ui.ind_subd_min.setText(str(self.module.get_parameter("ind_subd_min")))
        self.ui.ind_subd_max.setText(str(self.module.get_parameter("ind_subd_max")))
        self.ui.com_subd_min.setText(str(self.module.get_parameter("com_subd_min")))
        self.ui.com_subd_max.setText(str(self.module.get_parameter("com_subd_max")))

        self.ui.nres_setback_box.setText(str(self.module.get_parameter("nres_minfsetback")))
        self.ui.nres_setback_auto.setChecked(int(self.module.get_parameter("nres_setback_auto")))

        self.ui.plotratio_ind_slider.setValue(int(self.module.get_parameter("maxplotratio_ind")))
        self.ui.plotratio_com_slider.setValue(int(self.module.get_parameter("maxplotratio_com")))
        self.ui.nres_maxfloors_spin.setValue(int(self.module.get_parameter("nres_maxfloors")))
        self.ui.nres_maxfloors_nolimit.setChecked(int(self.module.get_parameter("nres_nolimit_floors")))

        self.ui.carpark_dimW_box.setText(str(self.module.get_parameter("carpark_Wmin")))
        self.ui.carpark_dimD_box.setText(str(self.module.get_parameter("carpark_Dmin")))
        self.ui.carpark_imp_spin.setValue(int(self.module.get_parameter("carpark_imp")))
        self.ui.carpark_ind_box.setText(str(self.module.get_parameter("carpark_ind")))
        self.ui.carpark_com_box.setText(str(self.module.get_parameter("carpark_com")))
        self.ui.loadingbay_box.setText(str(self.module.get_parameter("loadingbay_A")))

        self.ui.lscape_hsbalance_slide.setValue(int(self.module.get_parameter("lscape_hsbalance")))
        self.ui.lscape_impdced_spin.setValue(int(self.module.get_parameter("lscape_impdced")))

        self.ui.w_nresfootpath_min_box.setText(str(self.module.get_parameter("nres_fpwmin")))
        self.ui.w_nresfootpath_max_box.setText(str(self.module.get_parameter("nres_fpwmax")))
        self.ui.w_nresnaturestrip_min_box.setText(str(self.module.get_parameter("nres_nswmin")))
        self.ui.w_nresnaturestrip_max_box.setText(str(self.module.get_parameter("nres_nswmax")))
        self.ui.w_nresfootpath_med_check.setChecked(bool(int(self.module.get_parameter("nres_fpmed"))))
        self.ui.w_nresnaturestrip_med_check.setChecked(bool(int(self.module.get_parameter("nres_nsmed"))))
        self.ui.w_nreslane_min_box.setText(str(self.module.get_parameter("nres_lanemin")))
        self.ui.w_nreslane_max_box.setText(str(self.module.get_parameter("nres_lanemax")))
        self.ui.w_nreslane_med_check.setChecked(bool(int(self.module.get_parameter("nres_lanemed"))))

        # --> Municipal Facilities
        self.ui.civ_consider_check.setChecked(bool(int(self.module.get_parameter("civic_explicit"))))
        self.ui.civ_school.setChecked(bool(int(self.module.get_parameter("civ_school"))))
        self.ui.civ_university.setChecked(bool(int(self.module.get_parameter("civ_uni"))))
        self.ui.civ_library.setChecked(bool(int(self.module.get_parameter("civ_lib"))))
        self.ui.civ_hospital.setChecked(bool(int(self.module.get_parameter("civ_hospital"))))
        self.ui.civ_clinic.setChecked(bool(int(self.module.get_parameter("civ_clinic"))))
        self.ui.civ_police.setChecked(bool(int(self.module.get_parameter("civ_police"))))
        self.ui.civ_fire.setChecked(bool(int(self.module.get_parameter("civ_fire"))))
        self.ui.civ_jail.setChecked(bool(int(self.module.get_parameter("civ_jail"))))
        self.ui.civ_worship.setChecked(bool(int(self.module.get_parameter("civ_worship"))))
        self.ui.civ_leisure.setChecked(bool(int(self.module.get_parameter("civ_leisure"))))
        self.ui.civ_museum.setChecked(bool(int(self.module.get_parameter("civ_museum"))))
        self.ui.civ_zoo.setChecked(bool(int(self.module.get_parameter("civ_zoo"))))
        self.ui.civ_stadium.setChecked(bool(int(self.module.get_parameter("civ_stadium"))))
        self.ui.civ_racing.setChecked(bool(int(self.module.get_parameter("civ_racing"))))
        self.ui.civ_cemetery.setChecked(bool(int(self.module.get_parameter("civ_cemetery"))))
        self.ui.civ_cityhall.setChecked(bool(int(self.module.get_parameter("civ_cityhall"))))

        self.enable_disable_nonres()
        self.enable_disable_civic()
        self.set_nonres_plotratio_boxupdate()

        # Advanced Parameters
        self.nonres_far = {}
        self.nonres_far["LI"] = 70.0
        self.nonres_far["HI"] = 150.0
        self.nonres_far["COM"] = 220.0
        self.nonres_far["ORC"] = 110.0

        # TAB 4 - TRANSPORT PLANNING PARAMETERS
        self.ui.ma_buffer_check.setChecked(int(self.module.get_parameter("ma_buffer")))
        self.ui.ma_fpath_check.setChecked(int(self.module.get_parameter("ma_fpath")))
        self.ui.ma_nstrip_check.setChecked(int(self.module.get_parameter("ma_nstrip")))
        self.ui.ma_sidestreet_check.setChecked(int(self.module.get_parameter("ma_sidestreet")))
        self.ui.ma_bicycle_check.setChecked(int(self.module.get_parameter("ma_bicycle")))
        self.ui.ma_travellane_check.setChecked(int(self.module.get_parameter("ma_travellane")))
        self.ui.ma_centralbuffer_check.setChecked(int(self.module.get_parameter("ma_centralbuffer")))

        self.ui.ma_buffer_wmin.setText(str(self.module.get_parameter("ma_buffer_wmin")))
        self.ui.ma_buffer_wmax.setText(str(self.module.get_parameter("ma_buffer_wmax")))
        self.ui.ma_fpath_wmin.setText(str(self.module.get_parameter("ma_fpath_wmin")))
        self.ui.ma_fpath_wmax.setText(str(self.module.get_parameter("ma_fpath_wmax")))
        self.ui.ma_nstrip_wmin.setText(str(self.module.get_parameter("ma_nstrip_wmin")))
        self.ui.ma_nstrip_wmax.setText(str(self.module.get_parameter("ma_nstrip_wmax")))
        self.ui.ma_sidestreet_wmin.setText(str(self.module.get_parameter("ma_sidestreet_wmin")))
        self.ui.ma_sidestreet_wmax.setText(str(self.module.get_parameter("ma_sidestreet_wmax")))
        self.ui.ma_bicycle_wmin.setText(str(self.module.get_parameter("ma_bicycle_wmin")))
        self.ui.ma_bicycle_wmax.setText(str(self.module.get_parameter("ma_bicycle_wmax")))
        self.ui.ma_travellane_wmin.setText(str(self.module.get_parameter("ma_travellane_wmin")))
        self.ui.ma_travellane_wmax.setText(str(self.module.get_parameter("ma_travellane_wmax")))
        self.ui.ma_centralbuffer_wmin.setText(str(self.module.get_parameter("ma_centralbuffer_wmin")))
        self.ui.ma_centralbuffer_wmax.setText(str(self.module.get_parameter("ma_centralbuffer_wmax")))

        self.ui.ma_buffer_median.setChecked(int(self.module.get_parameter("ma_buffer_median")))
        self.ui.ma_fpath_median.setChecked(int(self.module.get_parameter("ma_fpath_median")))
        self.ui.ma_nstrip_median.setChecked(int(self.module.get_parameter("ma_nstrip_median")))
        self.ui.ma_sidestreet_median.setChecked(int(self.module.get_parameter("ma_sidestreet_median")))
        self.ui.ma_bicycle_median.setChecked(int(self.module.get_parameter("ma_bicycle_median")))
        self.ui.ma_travellane_median.setChecked(int(self.module.get_parameter("ma_travellane_median")))
        self.ui.ma_centralbuffer_median.setChecked(int(self.module.get_parameter("ma_centralbuffer_median")))

        self.ui.ma_sidestreet_lanes.setValue(int(self.module.get_parameter("ma_sidestreet_lanes")))
        self.ui.ma_bicycle_lanes.setValue(int(self.module.get_parameter("ma_bicycle_lanes")))
        self.ui.ma_bicycle_shared.setChecked(int(self.module.get_parameter("ma_bicycle_shared")))
        self.ui.ma_travellane_lanes.setValue(int(self.module.get_parameter("ma_travellane_lanes")))

        self.ui.pt_centralbuffer.setChecked(int(self.module.get_parameter("pt_centralbuffer")))
        self.ui.pt_impervious.setValue(int(self.module.get_parameter("pt_impervious")))
        self.ui.ma_median_reserved.setChecked(int(self.module.get_parameter("ma_median_reserved")))
        self.ui.ma_openspacebuffer.setChecked(int(self.module.get_parameter("ma_openspacebuffer")))

        self.ui.hwy_different_check.setChecked(int(self.module.get_parameter("hwy_different_check")))
        self.ui.hwy_verge_check.setChecked(int(self.module.get_parameter("hwy_verge_check")))
        self.ui.hwy_service_check.setChecked(int(self.module.get_parameter("hwy_service_check")))
        self.ui.hwy_travellane_check.setChecked(int(self.module.get_parameter("hwy_travellane_check")))
        self.ui.hwy_centralbuffer_check.setChecked(int(self.module.get_parameter("hwy_centralbuffer_check")))

        self.ui.hwy_verge_wmin.setText(str(self.module.get_parameter("hwy_verge_wmin")))
        self.ui.hwy_verge_wmax.setText(str(self.module.get_parameter("hwy_verge_wmax")))
        self.ui.hwy_service_wmin.setText(str(self.module.get_parameter("hwy_service_wmin")))
        self.ui.hwy_service_wmax.setText(str(self.module.get_parameter("hwy_service_wmax")))
        self.ui.hwy_travellane_wmin.setText(str(self.module.get_parameter("hwy_travellane_wmin")))
        self.ui.hwy_travellane_wmax.setText(str(self.module.get_parameter("hwy_travellane_wmax")))
        self.ui.hwy_centralbuffer_wmin.setText(str(self.module.get_parameter("hwy_centralbuffer_wmin")))
        self.ui.hwy_centralbuffer_wmax.setText(str(self.module.get_parameter("hwy_centralbuffer_wmax")))

        self.ui.hwy_verge_median.setChecked(int(self.module.get_parameter("hwy_verge_median")))
        self.ui.hwy_service_median.setChecked(int(self.module.get_parameter("hwy_service_median")))
        self.ui.hwy_travellane_median.setChecked(int(self.module.get_parameter("hwy_travellane_median")))
        self.ui.hwy_centralbuffer_median.setChecked(int(self.module.get_parameter("hwy_centralbuffer_median")))

        self.ui.hwy_service_lanes.setValue(int(self.module.get_parameter("hwy_service_lanes")))
        self.ui.hwy_travellane_lanes.setValue(int(self.module.get_parameter("hwy_travellane_lanes")))
        self.ui.hwy_median_reserved.setChecked(int(self.module.get_parameter("hwy_median_reserved")))
        self.ui.hwy_openspacebuffer.setChecked(int(self.module.get_parameter("hwy_openspacebuffer")))

        self.ui.consider_transport.setChecked(int(self.module.get_parameter("consider_transport")))
        self.ui.trans_airport.setChecked(int(self.module.get_parameter("trans_airport")))
        self.ui.trans_seaport.setChecked(int(self.module.get_parameter("trans_seaport")))
        self.ui.trans_busdepot.setChecked(int(self.module.get_parameter("trans_busdepot")))
        self.ui.trans_railterminal.setChecked(int(self.module.get_parameter("trans_railterminal")))

        self.enable_disable_majorarterials()
        self.enable_disable_highways()
        self.enable_disable_transport()

        # TAB 5 - OPEN SPACES PLANNING PARAMETERS
        self.ui.pg_ggratio_slide.setValue(int(self.module.get_parameter("pg_greengrey_ratio")))
        self.ui.pg_usable_spin.setValue(int(self.module.get_parameter("pg_nonrec_space")))
        self.ui.pg_fac_restaurant.setChecked(int(self.module.get_parameter("pg_fac_restaurant")))
        self.ui.pg_fac_fitness.setChecked(int(self.module.get_parameter("pg_fac_fitness")))
        self.ui.pg_fac_bbq.setChecked(int(self.module.get_parameter("pg_fac_bbq")))
        self.ui.pg_fac_sports.setChecked(int(self.module.get_parameter("pg_fac_sports")))

        self.ui.ref_usable_check.setChecked(int(self.module.get_parameter("ref_usable")))
        self.ui.ref_usable_spin.setValue(int(self.module.get_parameter("ref_usable_percent")))

        self.ui.svu_slider.setValue(int(self.module.get_parameter("svu_water")))
        self.ui.svu_supply_check.setChecked(self.module.get_parameter("svu4supply"))
        self.ui.svu_waste_check.setChecked(self.module.get_parameter("svu4waste"))
        self.ui.svu_storm_check.setChecked(self.module.get_parameter("svu4storm"))

        self.ui.svu_supply_spin.setValue(int(self.module.get_parameter("svu4supply_prop")))
        self.ui.svu_waste_spin.setValue(int(self.module.get_parameter("svu4waste_prop")))
        self.ui.svu_storm_spin.setValue(int(self.module.get_parameter("svu4storm_prop")))

        self.set_greengreyratio_boxupdate()
        self.set_svu_waternonwater_boxupdate()
        self.enable_disable_openspaces()

        # TAB 6 - OTHER LAND USES
        self.ui.unc_merge_check.setChecked(int(self.module.get_parameter("unc_merge")))
        self.ui.unc_merge2pg_check.setChecked(int(self.module.get_parameter("unc_pgmerge")))
        self.ui.unc_merge2ref_check.setChecked(int(self.module.get_parameter("unc_refmerge")))
        self.ui.unc_merge2trans_check.setChecked(int(self.module.get_parameter("unc_rdmerge")))
        self.ui.unc_merge2ref_spin.setValue(float(self.module.get_parameter("unc_refmerge_w")))
        self.ui.unc_merge2pg_spin.setValue(float(self.module.get_parameter("unc_pgmerge_w")))
        self.ui.unc_merge2trans_spin.setValue(float(self.module.get_parameter("unc_rdmerge_w")))
        self.ui.unc_custom_check.setChecked(self.module.get_parameter("unc_custom"))
        self.ui.unc_areathresh_spin.setValue(float(self.module.get_parameter("unc_customthresh")))
        self.ui.unc_customimp_spin.setValue(float(self.module.get_parameter("unc_customimp")))
        self.ui.unc_customirrigate_check.setChecked(int(self.module.get_parameter("unc_landirrigate")))

        if self.module.get_parameter("und_state") == "M":
            self.ui.und_statemanual_radio.setChecked(1)
        else:
            self.ui.und_stateauto_radio.setChecked(1)

        undev_type = self.module.get_parameter("und_type_manual")
        undevindex = ubglobals.UNDEVSTATES.index(undev_type)
        self.ui.und_statemanual_combo.setCurrentIndex(int(undevindex))
        self.ui.und_allowdev_check.setChecked(int(self.module.get_parameter("und_allowdev")))
        self.enable_disable_others()
        # END OF FILING IN GUI VALUES
        return True

    def enable_disable_majorarterials(self):
        """Enables and disables GUI elements for all items under the MAJOR ARTERIALS category set of parameters."""
        self.ui.ma_fpath_wmin.setEnabled(self.ui.ma_fpath_check.isChecked())
        self.ui.ma_fpath_wmax.setEnabled(self.ui.ma_fpath_check.isChecked())
        self.ui.ma_fpath_median.setEnabled(self.ui.ma_fpath_check.isChecked())

        self.ui.ma_nstrip_wmin.setEnabled(self.ui.ma_nstrip_check.isChecked())
        self.ui.ma_nstrip_wmax.setEnabled(self.ui.ma_nstrip_check.isChecked())
        self.ui.ma_nstrip_median.setEnabled(self.ui.ma_nstrip_check.isChecked())

        self.ui.ma_sidestreet_wmin.setEnabled(self.ui.ma_sidestreet_check.isChecked())
        self.ui.ma_sidestreet_wmax.setEnabled(self.ui.ma_sidestreet_check.isChecked())
        self.ui.ma_sidestreet_median.setEnabled(self.ui.ma_sidestreet_check.isChecked())
        self.ui.ma_sidestreet_lanes.setEnabled(self.ui.ma_sidestreet_check.isChecked())

        self.ui.ma_bicycle_wmin.setEnabled(self.ui.ma_bicycle_check.isChecked())
        self.ui.ma_bicycle_wmax.setEnabled(self.ui.ma_bicycle_check.isChecked())
        self.ui.ma_bicycle_median.setEnabled(self.ui.ma_bicycle_check.isChecked())
        self.ui.ma_bicycle_lanes.setEnabled(self.ui.ma_bicycle_check.isChecked())
        self.ui.ma_bicycle_shared.setEnabled(self.ui.ma_bicycle_check.isChecked())

        self.ui.ma_travellane_wmin.setEnabled(self.ui.ma_travellane_check.isChecked())
        self.ui.ma_travellane_wmax.setEnabled(self.ui.ma_travellane_check.isChecked())
        self.ui.ma_travellane_median.setEnabled(self.ui.ma_travellane_check.isChecked())
        self.ui.ma_travellane_lanes.setEnabled(self.ui.ma_travellane_check.isChecked())

        self.ui.ma_centralbuffer_wmin.setEnabled(self.ui.ma_centralbuffer_check.isChecked())
        self.ui.ma_centralbuffer_wmax.setEnabled(self.ui.ma_centralbuffer_check.isChecked())
        self.ui.ma_centralbuffer_median.setEnabled(self.ui.ma_centralbuffer_check.isChecked())
        self.ui.ma_median_reserved.setEnabled(self.ui.ma_centralbuffer_check.isChecked())
        if self.ui.ma_centralbuffer_check.isChecked():
            self.ui.pt_centralbuffer.setEnabled(1)
            self.ui.pt_impervious.setEnabled(self.ui.pt_centralbuffer.isChecked())
        else:
            self.ui.pt_centralbuffer.setEnabled(0)
            self.ui.pt_impervious.setEnabled(0)
        return True

    def enable_disable_highways(self):
        """Enables and disables GUI elements under the HIGHWAYS Options based on user actions."""
        if self.ui.hwy_different_check.isChecked():
            self.ui.hwy_verge_check.setEnabled(1)
            self.ui.hwy_verge_wmin.setEnabled(self.ui.hwy_verge_check.isChecked())
            self.ui.hwy_verge_wmax.setEnabled(self.ui.hwy_verge_check.isChecked())
            self.ui.hwy_verge_median.setEnabled(self.ui.hwy_verge_check.isChecked())
            self.ui.hwy_service_check.setEnabled(1)
            self.ui.hwy_service_wmin.setEnabled(self.ui.hwy_service_check.isChecked())
            self.ui.hwy_service_wmax.setEnabled(self.ui.hwy_service_check.isChecked())
            self.ui.hwy_service_lanes.setEnabled(self.ui.hwy_service_check.isChecked())
            self.ui.hwy_service_median.setEnabled(self.ui.hwy_service_check.isChecked())
            self.ui.hwy_travellane_check.setEnabled(1)
            self.ui.hwy_travellane_wmin.setEnabled(self.ui.hwy_travellane_check.isChecked())
            self.ui.hwy_travellane_wmax.setEnabled(self.ui.hwy_travellane_check.isChecked())
            self.ui.hwy_travellane_lanes.setEnabled(self.ui.hwy_travellane_check.isChecked())
            self.ui.hwy_travellane_median.setEnabled(self.ui.hwy_travellane_check.isChecked())
            self.ui.hwy_centralbuffer_check.setEnabled(1)
            self.ui.hwy_centralbuffer_wmin.setEnabled(self.ui.hwy_centralbuffer_check.isChecked())
            self.ui.hwy_centralbuffer_wmax.setEnabled(self.ui.hwy_centralbuffer_check.isChecked())
            self.ui.hwy_centralbuffer_median.setEnabled(self.ui.hwy_centralbuffer_check.isChecked())
            self.ui.hwy_median_reserved.setEnabled(self.ui.hwy_centralbuffer_check.isChecked())
        else:
            self.ui.hwy_verge_check.setEnabled(0)
            self.ui.hwy_verge_wmin.setEnabled(0)
            self.ui.hwy_verge_wmax.setEnabled(0)
            self.ui.hwy_verge_median.setEnabled(0)
            self.ui.hwy_service_check.setEnabled(0)
            self.ui.hwy_service_wmin.setEnabled(0)
            self.ui.hwy_service_wmax.setEnabled(0)
            self.ui.hwy_service_lanes.setEnabled(0)
            self.ui.hwy_service_median.setEnabled(0)
            self.ui.hwy_travellane_check.setEnabled(0)
            self.ui.hwy_travellane_wmin.setEnabled(0)
            self.ui.hwy_travellane_wmax.setEnabled(0)
            self.ui.hwy_travellane_lanes.setEnabled(0)
            self.ui.hwy_travellane_median.setEnabled(0)
            self.ui.hwy_centralbuffer_check.setEnabled(0)
            self.ui.hwy_centralbuffer_wmin.setEnabled(0)
            self.ui.hwy_centralbuffer_wmax.setEnabled(0)
            self.ui.hwy_centralbuffer_median.setEnabled(0)
            self.ui.hwy_median_reserved.setEnabled(0)
        return True

    def enable_disable_transport(self):
        """Enables and disables the check boxes under TRANSPORTATION FACILITIES SUB-CATEGORY."""
        self.ui.trans_airport.setEnabled(self.ui.consider_transport.isChecked())
        self.ui.trans_seaport.setEnabled(self.ui.consider_transport.isChecked())
        self.ui.trans_busdepot.setEnabled(self.ui.consider_transport.isChecked())
        self.ui.trans_railterminal.setEnabled(self.ui.consider_transport.isChecked())
        self.ui.trans_customise.setEnabled(self.ui.consider_transport.isChecked())
        return True

    def enable_disable_others(self):
        """Enables and disables the 'Others' land use tab GUI items."""
        self.ui.und_statemanual_combo.setEnabled(self.ui.und_statemanual_radio.isChecked())
        if self.ui.unc_merge_check.isChecked():
            self.ui.unc_merge2ref_check.setEnabled(1)
            self.ui.unc_merge2pg_check.setEnabled(1)
            self.ui.unc_merge2trans_check.setEnabled(1)
            self.ui.unc_merge2ref_spin.setEnabled(self.ui.unc_merge2ref_check.isChecked())
            self.ui.unc_merge2pg_spin.setEnabled(self.ui.unc_merge2pg_check.isChecked())
            self.ui.unc_merge2trans_spin.setEnabled(self.ui.unc_merge2trans_check.isChecked())
        else:
            self.ui.unc_merge2ref_check.setEnabled(0)
            self.ui.unc_merge2pg_check.setEnabled(0)
            self.ui.unc_merge2trans_check.setEnabled(0)
            self.ui.unc_merge2ref_spin.setEnabled(0)
            self.ui.unc_merge2pg_spin.setEnabled(0)
            self.ui.unc_merge2trans_spin.setEnabled(0)

        if self.ui.unc_custom_check.isChecked():
            self.ui.unc_areathresh_spin.setEnabled(1)
            self.ui.unc_customimp_spin.setEnabled(1)
            self.ui.unc_customirrigate_check.setEnabled(1)
        else:
            self.ui.unc_areathresh_spin.setEnabled(0)
            self.ui.unc_customimp_spin.setEnabled(0)
            self.ui.unc_customirrigate_check.setEnabled(0)

    def enable_disable_openspaces(self):
        """Enables and disables the open spaces GUI elements based on conditions defined by the user parameters."""
        self.ui.ref_usable_spin.setEnabled(self.ui.ref_usable_check.isChecked())
        self.ui.svu_supply_spin.setEnabled(self.ui.svu_supply_check.isChecked())
        self.ui.svu_waste_spin.setEnabled(self.ui.svu_waste_check.isChecked())
        self.ui.svu_storm_spin.setEnabled(self.ui.svu_storm_check.isChecked())

    def set_svu_waternonwater_boxupdate(self):
        """Updates the two text boxes on either side of the services and utility slider widget."""
        svu_water = int(self.ui.svu_slider.value())
        svu_nonwater = 100 - svu_water
        self.ui.svu_wat_box.setText(str(svu_water))
        self.ui.svu_nonwat_box.setText(str(svu_nonwater))

    def set_greengreyratio_boxupdate(self):
        """Updates the text box for green grey ratio based on the slider value."""
        self.ui.pg_ggratio_box.setText(str(self.ui.pg_ggratio_slide.value()))

    def set_nonres_plotratio_boxupdate(self):
        """Sets the values of the plot ratio boxes depending on the plot ratio """
        self.ui.plotratio_ind_box.setText(str(float(self.ui.plotratio_ind_slider.value()) / 100.0))
        self.ui.plotratio_com_box.setText(str(float(self.ui.plotratio_com_slider.value()) / 100.0))

    def enable_disable_nonres(self):
        """Enables and disables non-residential GUI elements based on user-defined options and actions."""
        self.ui.nres_setback_box.setEnabled(not self.ui.nres_setback_auto.isChecked())
        self.ui.nres_maxfloors_spin.setEnabled(not self.ui.nres_maxfloors_nolimit.isChecked())

    def enable_disable_civic(self):
        """Enables and disables the civic facilities features in the GUI based on whether the user wants to consider
        these explicitly in the modelling."""
        self.ui.civ_cemetery.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_cityhall.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_clinic.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_customise.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_fire.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_hospital.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_jail.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_leisure.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_library.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_museum.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_police.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_racing.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_school.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_stadium.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_university.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_worship.setEnabled(self.ui.civ_consider_check.isChecked())
        self.ui.civ_zoo.setEnabled(self.ui.civ_consider_check.isChecked())
        return True

    def adjust_employment_stack(self):
        """Changes the current index of the employment stack widget based on the selected radio button."""
        if self.ui.jobs_direct_radio.isChecked():
            self.ui.jobs_define_stack.setCurrentIndex(0)
        elif self.ui.jobs_dist_radio.isChecked():
            self.ui.jobs_define_stack.setCurrentIndex(1)
        else:
            self.ui.jobs_define_stack.setCurrentIndex(2)

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        # TAB 1 - GENERAL PARAMETERS
        print "Debug String: GENERAL PARAMETERS"
        self.module.set_parameter("plan_type", ubglobals.PLANTYPES[self.ui.plan_typology_combo.currentIndex()])
        if self.ui.plan_params_predef.isChecked():
            self.module.set_parameter("plan_template", "PREDEF")
        else:
            self.module.set_parameter("plan_template", "PRELOAD")

        self.module.set_parameter("plan_paramset", ubglobals.PLANPARAMSET[self.ui.plan_params_citycombo.currentIndex()])
        self.module.set_parameter("plan_paramfile", self.ui.plan_params_filebox.text())

        self.module.set_parameter("emp_map", self.ui.employment_combo.currentText())
        self.module.set_parameter("local_map", self.ui.locality_combo.currentText())
        self.module.set_parameter("roadnet_map", self.ui.roadnet_combo.currentText())
        self.module.set_parameter("emp_fud", int(self.ui.emp_fud.isChecked()))
        self.module.set_parameter("local_attref", str(self.ui.locality_attref.text()))
        self.module.set_parameter("roadnet_attref", str(self.ui.roadnet_attref.text()))

        if self.ui.citymono_radio.isChecked():
            self.module.set_parameter("cityarchetype", "MC")
        else:
            self.module.set_parameter("cityarchetype", "PC")

        self.module.set_parameter("citysprawl", float(self.ui.citysprawl_spin.value()))

        # --> Decision Variables for Block Dynamics
        self.module.set_parameter("lucredev", int(self.ui.lucredevelop_check.isChecked()))
        self.module.set_parameter("popredev", int(self.ui.popredevelop_check.isChecked()))
        self.module.set_parameter("noredev", int(self.ui.noredevelop_check.isChecked()))
        self.module.set_parameter("lucredev_thresh", int(self.ui.lucredevelop_spin.value()))
        self.module.set_parameter("popredev_thresh", int(self.ui.popredevelop_spin.value()))

        # TAB 2 - Residential
        print "Debug String: RESIDENTIAL PARAMETERS"
        self.module.set_parameter("occup_avg", float(self.ui.occup_avg_box.text()))
        self.module.set_parameter("occup_max", float(self.ui.occup_max_box.text()))
        self.module.set_parameter("person_space", float(self.ui.person_space_box.text()))
        self.module.set_parameter("extra_comm_area", float(self.ui.extra_comm_area_box.text()))
        self.module.set_parameter("avg_allot_depth", float(self.ui.allot_depth_box.text()))
        self.module.set_parameter("allot_depth_default", int(self.ui.allot_depth_check.isChecked()))
        self.module.set_parameter("floor_num_max", int(self.ui.house_floors.value()))
        self.module.set_parameter("patio_area_max", float(self.ui.patio_area_max_box.text()))
        self.module.set_parameter("patio_covered", int(self.ui.patio_covered_box.isChecked()))
        self.module.set_parameter("carports_max", int(self.ui.carports_max_box.text()))
        self.module.set_parameter("garage_incl", int(self.ui.garage_incl_box.isChecked()))
        self.module.set_parameter("w_driveway_min", float(self.ui.w_driveway_min_box.text()))

        self.module.set_parameter("setback_f_min", float(self.ui.setback_f_min_box.text()))
        self.module.set_parameter("setback_f_max", float(self.ui.setback_f_max_box.text()))
        self.module.set_parameter("setback_s_min", float(self.ui.setback_s_min_box.text()))
        self.module.set_parameter("setback_s_max", float(self.ui.setback_s_max_box.text()))
        self.module.set_parameter("setback_f_med", int(self.ui.fsetbackmed_check.isChecked()))
        self.module.set_parameter("setback_s_med", int(self.ui.ssetbackmed_check.isChecked()))

        self.module.set_parameter("occup_flat_avg", float(self.ui.occup_flat_avg_box.text()))
        self.module.set_parameter("flat_area_max", float(self.ui.flat_area_max_box.text()))
        self.module.set_parameter("commspace_indoor", float(self.ui.indoor_com_spin.value()))
        self.module.set_parameter("commspace_outdoor", float(self.ui.outdoor_com_spin.value()))
        self.module.set_parameter("floor_num_HDRmax", int(self.ui.aptbldg_floors.value()))
        self.module.set_parameter("setback_HDR_avg", float(self.ui.setback_HDR_avg_box.text()))

        if self.ui.parking_on.isChecked():
            self.module.set_parameter("parking_HDR", "On")
        elif self.ui.parking_off.isChecked():
            self.module.set_parameter("parking_HDR", "Off")
        elif self.ui.parking_vary.isChecked():
            self.module.set_parameter("parking_HDR", "Var")
        else:
            self.module.set_parameter("parking_HDR", "NA")

        self.module.set_parameter("park_OSR", int(self.ui.OSR_parks_include.isCheckable()))

        self.module.set_parameter("res_fpwmin", float(self.ui.w_resfootpath_min_box.text()))
        self.module.set_parameter("res_fpwmax", float(self.ui.w_resfootpath_max_box.text()))
        self.module.set_parameter("res_nswmin", float(self.ui.w_resnaturestrip_min_box.text()))
        self.module.set_parameter("res_nswmax", float(self.ui.w_resnaturestrip_max_box.text()))
        self.module.set_parameter("res_fpmed", int(self.ui.w_resfootpath_med_check.isChecked()))
        self.module.set_parameter("res_nsmed",  int(self.ui.w_resnaturestrip_med_check.isChecked()))
        self.module.set_parameter("res_lanemin", float(self.ui.w_reslane_min_box.text()))
        self.module.set_parameter("res_lanemax", float(self.ui.w_reslane_max_box.text()))
        self.module.set_parameter("res_lanemed", int(self.ui.w_reslane_med_check.isChecked()))

        self.module.set_parameter("define_drainage_rule", int(self.ui.drainage_rule_check.isChecked()))

        if self.ui.roof_connected_radiodirect.isChecked():
            self.module.set_parameter("roof_connected", "Direct")
        elif self.ui.roof_connected_radiodisc.isChecked():
            self.module.set_parameter("roof_connected", "Disconnect")
        else:
            self.module.set_parameter("roof_connected", "Vary")

        self.module.set_parameter("roof_dced_p", int(self.ui.roofdced_vary_spin.value()))
        self.module.set_parameter("imperv_prop_dced", int(self.ui.avg_imp_dced_spin.value()))

        # TAB 3 - Non-Residential
        print "Debug String: NON-RESIDENTIAL PARAMETERS"
        if self.ui.jobs_direct_radio.isChecked():
            self.module.set_parameter("employment_mode", "I")
        elif self.ui.jobs_dist_radio.isChecked():
            self.module.set_parameter("employment_mode", "D")
        else:
            self.module.set_parameter("employment_mode", "S")

        self.module.set_parameter("ind_edist", int(self.ui.dist_ind_spin.value()))
        self.module.set_parameter("com_edist", int(self.ui.dist_com_spin.value()))
        self.module.set_parameter("orc_edist", int(self.ui.dist_orc_spin.value()))
        self.module.set_parameter("employment_total", float(self.ui.totjobs_box.text()))

        self.module.set_parameter("ind_subd_min", float(self.ui.ind_subd_min.text()))
        self.module.set_parameter("ind_subd_max", float(self.ui.ind_subd_max.text()))
        self.module.set_parameter("com_subd_min", float(self.ui.com_subd_min.text()))
        self.module.set_parameter("com_subd_max", float(self.ui.com_subd_max.text()))

        self.module.set_parameter("nres_minfsetback", float(self.ui.nres_setback_box.text()))
        self.module.set_parameter("nres_setback_auto", int(self.ui.nres_setback_auto.isChecked()))

        self.module.set_parameter("maxplotratio_ind", int(self.ui.plotratio_ind_slider.value()))
        self.module.set_parameter("maxplotratio_com", int(self.ui.plotratio_com_slider.value()))
        self.module.set_parameter("nres_maxfloors", int(self.ui.nres_maxfloors_spin.value()))
        self.module.set_parameter("nres_nolimit_floors", int(self.ui.nres_maxfloors_nolimit.isChecked()))

        self.module.set_parameter("carpark_Wmin", float(self.ui.carpark_dimW_box.text()))
        self.module.set_parameter("carpark_Dmin", float(self.ui.carpark_dimD_box.text()))
        self.module.set_parameter("carpark_imp", float(self.ui.carpark_imp_spin.value()))
        self.module.set_parameter("carpark_ind", float(self.ui.carpark_ind_box.text()))
        self.module.set_parameter("carpark_com", float(self.ui.carpark_com_box.text()))
        self.module.set_parameter("loadingbay_A", float(self.ui.loadingbay_box.text()))

        self.module.set_parameter("lscape_hsbalance", int(self.ui.lscape_hsbalance_slide.value()))
        self.module.set_parameter("lscape_impdced", int(self.ui.lscape_impdced_spin.value()))

        self.module.set_parameter("nres_fpwmin", float(self.ui.w_nresfootpath_min_box.text()))
        self.module.set_parameter("nres_fpwmax", float(self.ui.w_nresfootpath_max_box.text()))
        self.module.set_parameter("nres_nswmin", float(self.ui.w_nresnaturestrip_min_box.text()))
        self.module.set_parameter("nres_nswmax", float(self.ui.w_nresnaturestrip_max_box.text()))
        self.module.set_parameter("nres_fpmed", int(self.ui.w_nresfootpath_med_check.isChecked()))
        self.module.set_parameter("nres_nsmed", int(self.ui.w_nresnaturestrip_med_check.isChecked()))
        self.module.set_parameter("nres_lanemin", float(self.ui.w_nreslane_min_box.text()))
        self.module.set_parameter("nres_lanemax", float(self.ui.w_nreslane_max_box.text()))
        self.module.set_parameter("nres_lanemed", int(self.ui.w_nreslane_med_check.isChecked()))

        # --> Municipal Facilities
        self.module.set_parameter("civic_explicit", int(self.ui.civ_consider_check.isChecked()))
        self.module.set_parameter("civ_school", int(self.ui.civ_school.isChecked()))
        self.module.set_parameter("civ_uni", int(self.ui.civ_university.isChecked()))
        self.module.set_parameter("civ_lib", int(self.ui.civ_library.isChecked()))
        self.module.set_parameter("civ_hospital", int(self.ui.civ_hospital.isChecked()))
        self.module.set_parameter("civ_clinic", int(self.ui.civ_clinic.isChecked()))
        self.module.set_parameter("civ_police", int(self.ui.civ_police.isChecked()))
        self.module.set_parameter("civ_fire", int(self.ui.civ_fire.isChecked()))
        self.module.set_parameter("civ_jail", int(self.ui.civ_jail.isChecked()))
        self.module.set_parameter("civ_worship",  int(self.ui.civ_worship.isChecked()))
        self.module.set_parameter("civ_leisure", int(self.ui.civ_leisure.isChecked()))
        self.module.set_parameter("civ_museum", int(self.ui.civ_museum.isChecked()))
        self.module.set_parameter("civ_zoo", int(self.ui.civ_zoo.isChecked()))
        self.module.set_parameter("civ_stadium", int(self.ui.civ_stadium.isChecked()))
        self.module.set_parameter("civ_racing", int(self.ui.civ_racing.isChecked()))
        self.module.set_parameter("civ_cemetery", int(self.ui.civ_cemetery.isChecked()))
        self.module.set_parameter("civ_cityhall", int(self.ui.civ_cityhall.isChecked()))

        # TAB 4 - Transport and Roads
        print "Debug String: TRANSPORT PARAMETERS"
        self.module.set_parameter("ma_buffer", int(self.ui.ma_buffer_check.isChecked()))
        self.module.set_parameter("ma_fpath", int(self.ui.ma_fpath_check.isChecked()))
        self.module.set_parameter("ma_nstrip", int(self.ui.ma_nstrip_check.isChecked()))
        self.module.set_parameter("ma_sidestreet", int(self.ui.ma_sidestreet_check.isChecked()))
        self.module.set_parameter("ma_bicycle", int(self.ui.ma_bicycle_check.isChecked()))
        self.module.set_parameter("ma_travellane", int(self.ui.ma_travellane_check.isChecked()))
        self.module.set_parameter("ma_centralbuffer", int(self.ui.ma_centralbuffer_check.isChecked()))

        self.module.set_parameter("ma_buffer_wmin", float(self.ui.ma_buffer_wmin.text()))
        self.module.set_parameter("ma_buffer_wmax", float(self.ui.ma_buffer_wmax.text()))
        self.module.set_parameter("ma_fpath_wmin", float(self.ui.ma_fpath_wmin.text()))
        self.module.set_parameter("ma_fpath_wmax", float(self.ui.ma_fpath_wmax.text()))
        self.module.set_parameter("ma_nstrip_wmin", float(self.ui.ma_nstrip_wmin.text()))
        self.module.set_parameter("ma_nstrip_wmax", float(self.ui.ma_nstrip_wmax.text()))
        self.module.set_parameter("ma_sidestreet_wmin", float(self.ui.ma_sidestreet_wmin.text()))
        self.module.set_parameter("ma_sidestreet_wmax", float(self.ui.ma_sidestreet_wmax.text()))
        self.module.set_parameter("ma_bicycle_wmin", float(self.ui.ma_bicycle_wmin.text()))
        self.module.set_parameter("ma_bicycle_wmax", float(self.ui.ma_bicycle_wmax.text()))
        self.module.set_parameter("ma_travellane_wmin", float(self.ui.ma_travellane_wmin.text()))
        self.module.set_parameter("ma_travellane_wmax", float(self.ui.ma_travellane_wmax.text()))
        self.module.set_parameter("ma_centralbuffer_wmin", float(self.ui.ma_centralbuffer_wmin.text()))
        self.module.set_parameter("ma_centralbuffer_wmax", float(self.ui.ma_centralbuffer_wmax.text()))

        self.module.set_parameter("ma_buffer_median", int(self.ui.ma_buffer_median.isChecked()))
        self.module.set_parameter("ma_fpath_median", int(self.ui.ma_fpath_median.isChecked()))
        self.module.set_parameter("ma_nstrip_median", int(self.ui.ma_nstrip_median.isChecked()))
        self.module.set_parameter("ma_sidestreet_median", int(self.ui.ma_sidestreet_median.isChecked()))
        self.module.set_parameter("ma_bicycle_median", int(self.ui.ma_bicycle_median.isChecked()))
        self.module.set_parameter("ma_travellane_median", int(self.ui.ma_travellane_median.isChecked()))
        self.module.set_parameter("ma_centralbuffer_median", int(self.ui.ma_centralbuffer_median.isChecked()))

        self.module.set_parameter("ma_sidestreet_lanes", int(self.ui.ma_sidestreet_lanes.value()))
        self.module.set_parameter("ma_bicycle_lanes", int(self.ui.ma_bicycle_lanes.value()))
        self.module.set_parameter("ma_bicycle_shared", int(self.ui.ma_bicycle_shared.isChecked()))
        self.module.set_parameter("ma_travellane_lanes", int(self.ui.ma_travellane_lanes.value()))

        self.module.set_parameter("pt_centralbuffer", int(self.ui.pt_centralbuffer.isChecked()))
        self.module.set_parameter("pt_impervious", int(self.ui.pt_impervious.value()))
        self.module.set_parameter("ma_median_reserved", int(self.ui.ma_median_reserved.isChecked()))
        self.module.set_parameter("ma_openspacebuffer", int(self.ui.ma_openspacebuffer.isChecked()))

        self.module.set_parameter("hwy_different_check", int(self.ui.hwy_different_check.isChecked()))
        self.module.set_parameter("hwy_verge_check", int(self.ui.hwy_verge_check.isChecked()))
        self.module.set_parameter("hwy_service_check", int(self.ui.hwy_service_check.isChecked()))
        self.module.set_parameter("hwy_travellane_check", int(self.ui.hwy_travellane_check.isChecked()))
        self.module.set_parameter("hwy_centralbuffer_check", int(self.ui.hwy_centralbuffer_check.isChecked()))

        self.module.set_parameter("hwy_verge_wmin", float(self.ui.hwy_verge_wmin.text()))
        self.module.set_parameter("hwy_verge_wmax", float(self.ui.hwy_verge_wmax.text()))
        self.module.set_parameter("hwy_service_wmin", float(self.ui.hwy_service_wmin.text()))
        self.module.set_parameter("hwy_service_wmax", float(self.ui.hwy_service_wmax.text()))
        self.module.set_parameter("hwy_travellane_wmin", float(self.ui.hwy_travellane_wmin.text()))
        self.module.set_parameter("hwy_travellane_wmax", float(self.ui.hwy_travellane_wmax.text()))
        self.module.set_parameter("hwy_centralbuffer_wmin", float(self.ui.hwy_centralbuffer_wmin.text()))
        self.module.set_parameter("hwy_centralbuffer_wmax", float(self.ui.hwy_centralbuffer_wmax.text()))

        self.module.set_parameter("hwy_verge_median", int(self.ui.hwy_verge_median.isChecked()))
        self.module.set_parameter("hwy_service_median", int(self.ui.hwy_service_median.isChecked()))
        self.module.set_parameter("hwy_travellane_median", int(self.ui.hwy_travellane_median.isChecked()))
        self.module.set_parameter("hwy_centralbuffer_median", int(self.ui.hwy_centralbuffer_median.isChecked()))

        self.module.set_parameter("hwy_service_lanes", int(self.ui.hwy_service_lanes.value()))
        self.module.set_parameter("hwy_travellane_lanes", int(self.ui.hwy_travellane_lanes.value()))
        self.module.set_parameter("hwy_median_reserved", int(self.ui.hwy_median_reserved.isChecked()))
        self.module.set_parameter("hwy_openspacebuffer", int(self.ui.hwy_openspacebuffer.isChecked()))

        self.module.set_parameter("consider_transport", int(self.ui.consider_transport.isChecked()))
        self.module.set_parameter("trans_airport",int( self.ui.trans_airport.isChecked()))
        self.module.set_parameter("trans_seaport", int(self.ui.trans_seaport.isChecked()))
        self.module.set_parameter("trans_busdepot", int(self.ui.trans_busdepot.isChecked()))
        self.module.set_parameter("trans_railterminal", int(self.ui.trans_railterminal.isChecked()))

        # TAB 5 - Open Spaces
        print "Debug String: OPEN SPACE PARAMETERS"
        self.module.set_parameter("pg_greengrey_ratio", int(self.ui.pg_ggratio_slide.value()))
        self.module.set_parameter("pg_nonrec_space", int(self.ui.pg_usable_spin.value()))
        self.module.set_parameter("pg_fac_restaurant", int(self.ui.pg_fac_restaurant.isChecked()))
        self.module.set_parameter("pg_fac_fitness", int(self.ui.pg_fac_fitness.isChecked()))
        self.module.set_parameter("pg_fac_bbq", int(self.ui.pg_fac_bbq.isChecked()))
        self.module.set_parameter("pg_fac_sports", int(self.ui.pg_fac_sports.isChecked()))

        self.module.set_parameter("ref_usable", int(self.ui.ref_usable_check.isChecked()))
        self.module.set_parameter("ref_usable_percent", int(self.ui.ref_usable_spin.value()))

        self.module.set_parameter("svu_water", int(self.ui.svu_slider.value()))
        self.module.set_parameter("svu4supply", int(self.ui.svu_supply_check.isChecked()))
        self.module.set_parameter("svu4waste", int(self.ui.svu_waste_check.isChecked()))
        self.module.set_parameter("svu4storm", int(self.ui.svu_storm_check.isChecked()))

        self.module.set_parameter("svu4supply_prop", int(self.ui.svu_supply_spin.value()))
        self.module.set_parameter("svu4waste_prop", int(self.ui.svu_waste_spin.value()))
        self.module.set_parameter("svu4storm_prop", int(self.ui.svu_storm_spin.value()))

        # TAB 6 - Other Uses
        print "Debug String: OTHER PARAMETERS"
        self.module.set_parameter("unc_merge", int(self.ui.unc_merge_check.isChecked()))
        self.module.set_parameter("unc_pgmerge", int(self.ui.unc_merge2pg_check.isChecked()))
        self.module.set_parameter("unc_refmerge", int(self.ui.unc_merge2ref_check.isChecked()))
        self.module.set_parameter("unc_rdmerge", int(self.ui.unc_merge2trans_check.isChecked()))
        self.module.set_parameter("unc_refmerge_w", float(self.ui.unc_merge2ref_spin.value()))
        self.module.set_parameter("unc_pgmerge_w", float(self.ui.unc_merge2pg_spin.value()))
        self.module.set_parameter("unc_rdmerge_w", float(self.ui.unc_merge2trans_spin.value()))
        self.module.set_parameter("unc_custom", int(self.ui.unc_custom_check.isChecked()))
        self.module.set_parameter("unc_customthresh", float(self.ui.unc_areathresh_spin.value()))
        self.module.set_parameter("unc_customimp", float(self.ui.unc_customimp_spin.value()))
        self.module.set_parameter("unc_landirrigate", int(self.ui.unc_customirrigate_check.isChecked()))

        if self.ui.und_statemanual_radio.isChecked():
            self.module.set_parameter("und_state", "M")
        else:
            self.module.set_parameter("und_state", "A")

        self.module.set_parameter("und_type_manual", ubglobals.UNDEVSTATES[self.ui.und_statemanual_combo.currenIndex()])
        self.module.set_parameter("und_allowdev", int(self.ui.und_allowdev_check.isChecked()))
        return True
