r"""
@file   md_infrastructureguic.py
@author Peter M Bach <peterbach@gmail.com>, Natalia Duque <natalia.duquevillarreal@eawag.ch>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2019  Peter M. Bach, Natalia Duque

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
from .md_bgsplanninggui import Ui_BlueGreenDialog


# --- MAIN GUI FUNCTION ---
class BlueGreenGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Spatial Mapping GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_BlueGreenDialog()
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

        self.planning_algorithms = ["Bach2020", "Patch"]    # Variables specific to the GUI

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

        # --- MODULE INITIAL VIEW SETUP ---
        self.ui.bgs_listwidget.setCurrentRow(1)

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        self.asset_datasets = self.get_dataref_array("spatial", "Built Infrastructure", "WSUD")
        self.ui.assets_combo.clear()  # Clear the combo box first before setting it up
        [self.ui.assets_combo.addItem(str(self.asset_datasets[0][i])) for i in range(len(self.asset_datasets[0]))]

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        self.ui.bgs_listwidget.currentRowChanged.connect(self.change_stack_index)

        # Planning Objectives Section and Spatial Planning Restrictions
        self.ui.runoff_check.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.pollute_check.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.recycle_check.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.amenity_check.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.ecology_check.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.runoff_redundancy_ignore.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.pollute_redundancy_ignore.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.recycle_redundancy_ignore.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.amenity_redundancy_ignore.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.ecology_redundancy_ignore.clicked.connect(self.enable_disable_objectives_gui)
        self.ui.restrictions_pgusable.clicked.connect(self.enable_disable_objectives_gui)

        # Simulation Settings
        self.ui.planscales_lot_check.clicked.connect(self.enable_disable_simulation_settings_gui)
        self.ui.planscales_street_check.clicked.connect(self.enable_disable_simulation_settings_gui)
        self.ui.planscales_region_check.clicked.connect(self.enable_disable_simulation_settings_gui)
        self.ui.scalepref_check.clicked.connect(self.enable_disable_simulation_settings_gui)
        self.ui.planscales_lot_rigour.valueChanged.connect(self.simulation_settings_slider_boxes)
        self.ui.planscales_street_rigour.valueChanged.connect(self.simulation_settings_slider_boxes)
        self.ui.planscales_region_rigour.valueChanged.connect(self.simulation_settings_slider_boxes)

        # Life Cycle Costing
        self.ui.lcc_check.clicked.connect(self.enable_disable_lcc_gui)
        self.ui.lcc_capital_check.clicked.connect(self.enable_disable_lcc_gui)
        self.ui.lcc_prefill_button.clicked.connect(self.prefill_life_cycle_costs)
        self.ui.lcc_currency_combo.currentIndexChanged.connect(self.sync_lcc_combo_boxes)
        self.ui.lcc_currency_convert_check.clicked.connect(self.enable_disable_lcc_gui)

        # Technologies Menus
        self.ui.biof.clicked.connect(self.enable_disable_technology_guis)
        self.ui.wsur.clicked.connect(self.enable_disable_technology_guis)
        self.ui.pond.clicked.connect(self.enable_disable_technology_guis)
        self.ui.evap.clicked.connect(self.enable_disable_technology_guis)
        self.ui.roof.clicked.connect(self.enable_disable_technology_guis)
        self.ui.wall.clicked.connect(self.enable_disable_technology_guis)
        self.ui.pave.clicked.connect(self.enable_disable_technology_guis)
        self.ui.tank.clicked.connect(self.enable_disable_technology_guis)
        self.ui.infs.clicked.connect(self.enable_disable_technology_guis)
        self.ui.filt.clicked.connect(self.enable_disable_technology_guis)
        self.ui.swal.clicked.connect(self.enable_disable_technology_guis)
        self.ui.basn.clicked.connect(self.enable_disable_technology_guis)
        self.ui.disc.clicked.connect(self.enable_disable_technology_guis)
        self.ui.bank.clicked.connect(self.enable_disable_technology_guis)

        # OTHERS
        self.ui.buttonBox.accepted.connect(self.save_values)

        # CALL ENABLERS/DISABLERS
        self.enable_disable_objectives_gui()
        self.enable_disable_simulation_settings_gui()
        self.simulation_settings_slider_boxes()
        self.enable_disable_lcc_gui()

    def enable_disable_objectives_gui(self):
        """Enables/disables features of the objectives GUI."""
        self.ui.runoff_config.setEnabled(self.ui.runoff_check.isChecked())
        self.ui.pollute_config.setEnabled(self.ui.pollute_check.isChecked())
        self.ui.recycle_config.setEnabled(self.ui.recycle_check.isChecked())
        self.ui.amenity_config.setEnabled(self.ui.amenity_check.isChecked())
        self.ui.ecology_config.setEnabled(self.ui.ecology_check.isChecked())
        self.ui.runoff_redundancy_spin.setEnabled(not(self.ui.runoff_redundancy_ignore.isChecked()))
        self.ui.pollute_redundancy_spin.setEnabled(not(self.ui.pollute_redundancy_ignore.isChecked()))
        self.ui.recycle_redundancy_spin.setEnabled(not(self.ui.recycle_redundancy_ignore.isChecked()))
        self.ui.amenity_redundancy_spin.setEnabled(not(self.ui.amenity_redundancy_ignore.isChecked()))
        self.ui.ecology_redundancy_spin.setEnabled(not(self.ui.ecology_redundancy_ignore.isChecked()))
        self.ui.restrictions_pgusable_spin.setEnabled(self.ui.restrictions_pgusable.isChecked())
        return True

    def enable_disable_simulation_settings_gui(self):
        """Enables/disables elements of the Simulation Settings page in the GUI."""
        self.ui.planscales_lot_rigour.setEnabled(self.ui.planscales_lot_check.isChecked())
        self.ui.planscales_lot_box.setEnabled(self.ui.planscales_lot_check.isChecked())
        self.ui.planscales_street_rigour.setEnabled(self.ui.planscales_street_check.isChecked())
        self.ui.planscales_street_box.setEnabled(self.ui.planscales_street_check.isChecked())
        self.ui.planscales_region_rigour.setEnabled(self.ui.planscales_region_check.isChecked())
        self.ui.planscales_region_box.setEnabled(self.ui.planscales_region_check.isChecked())
        self.ui.scalepref_slider.setEnabled(self.ui.scalepref_check.isChecked())
        return True

    def simulation_settings_slider_boxes(self):
        """Writes the slider value into their respective boxes."""
        self.ui.planscales_lot_box.setText(str(self.ui.planscales_lot_rigour.value()))
        self.ui.planscales_street_box.setText(str(self.ui.planscales_street_rigour.value()))
        self.ui.planscales_region_box.setText(str(self.ui.planscales_region_rigour.value()))
        return True

    def enable_disable_lcc_gui(self):
        """Adjusts the LCC GUI based on inputs and signals and slots."""
        if self.ui.lcc_check.isChecked():
            self.ui.lcc_widget1.setEnabled(1)
            self.ui.lcc_widget2.setEnabled(1)
            self.ui.lcc_widget3.setEnabled(1)
            self.ui.lcc_widget4.setEnabled(1)
            self.ui.lcc_widget5.setEnabled(1)
            self.ui.lcc_widget6.setEnabled(1)
        else:
            self.ui.lcc_widget1.setEnabled(0)
            self.ui.lcc_widget2.setEnabled(0)
            self.ui.lcc_widget3.setEnabled(0)
            self.ui.lcc_widget4.setEnabled(0)
            self.ui.lcc_widget5.setEnabled(0)
            self.ui.lcc_widget6.setEnabled(0)

        if self.ui.lcc_capital_check.isChecked():
            self.ui.lcc_years_spin.setEnabled(0)
            self.ui.lcc_decom_at_end.setEnabled(0)
            self.ui.lcc_maintain_also.setEnabled(0)
            self.ui.lcc_ignore_lifespan.setEnabled(0)
        else:
            self.ui.lcc_years_spin.setEnabled(1)
            self.ui.lcc_decom_at_end.setEnabled(1)
            self.ui.lcc_maintain_also.setEnabled(1)
            self.ui.lcc_ignore_lifespan.setEnabled(1)

        self.ui.lcc_currency_rate.setEnabled(self.ui.lcc_currency_convert_check.isChecked())

    def prefill_life_cycle_costs(self):
        """Pre-fills the life cycle cost GUI with the corresponding template."""
        pass
        return True

    def sync_lcc_combo_boxes(self):
        """Synchronises the two currency combo boxes with each other."""
        self.ui.lcc_currency_combo2.setCurrentIndex(self.ui.lcc_currency_combo.currentIndex())
        return True

    def enable_disable_technology_guis(self):
        """Enables and disables respective technology menus based on the selection screen options."""
        self.ui.biof_scrollarea.setEnabled(self.ui.biof.isChecked())
        self.ui.wsur_scrollarea.setEnabled(self.ui.wsur.isChecked())
        self.ui.evap_scrollarea.setEnabled(self.ui.evap.isChecked())
        self.ui.pond_scrollarea.setEnabled(self.ui.pond.isChecked())
        self.ui.roof_scrollarea.setEnabled(self.ui.roof.isChecked())
        self.ui.wall_scrollarea.setEnabled(self.ui.wall.isChecked())
        self.ui.pave_scrollarea.setEnabled(self.ui.pave.isChecked())
        self.ui.tank_scrollarea.setEnabled(self.ui.tank.isChecked())
        self.ui.infs_scrollarea.setEnabled(self.ui.infs.isChecked())
        self.ui.filt_scrollarea.setEnabled(self.ui.filt.isChecked())
        self.ui.basn_scrollarea.setEnabled(self.ui.basn.isChecked())
        self.ui.swal_scrollarea.setEnabled(self.ui.swal.isChecked())

        # self.ui.disc_scrollarea.setEnabled(self.ui.disc.isChecked())
        # self.ui.bank_scrollarea.setEnabled(self.ui.bank.isChecked())

    def enable_disable_technology_widgets(self):
        """Enables/Disables elements of the technology GUIs widgets."""


    def enable_disable_entire_gui(self):
        """Enables and disables respective GUI elements depending on what the user clicks."""
        pass

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
        self.module = self.active_scenario.get_module_object("BGS", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()
        return True

    def change_stack_index(self):
        """Changes the current stack index to the index of the selected items in the list widget."""
        indexlookup = ["N", -1, -1, -1, -1, -1, -1, -1,
                       "N", -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2,
                       "N", -3, -3]
        i = indexlookup[int(self.ui.bgs_listwidget.currentRow())]
        if i == "N":
            return True
        else:
            self.ui.bgs_stack.setCurrentIndex(int(self.ui.bgs_listwidget.currentRow()) + i)

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""
        # --- PLANNING OBJECTIVES FOR BGS ---
        self.ui.runoff_check.setChecked(int(self.module.get_parameter("obj_run")))
        self.ui.runoff_pri_combo.setCurrentIndex(int(self.module.get_parameter("obj_run_priority"))-1)
        self.ui.runoff_target_spin.setValue(self.module.get_parameter("obj_run_target"))
        self.ui.runoff_service_spin.setValue(self.module.get_parameter("obj_run_service"))
        self.ui.runoff_redundancy_spin.setValue(self.module.get_parameter("obj_run_redund"))
        self.ui.runoff_redundancy_ignore.setChecked(int(self.module.get_parameter("obj_run_reignore")))

        self.ui.pollute_check.setChecked(int(self.module.get_parameter("obj_wq")))
        self.ui.pollute_pri_combo.setCurrentIndex(int(self.module.get_parameter("obj_wq_priority")) - 1)
        self.ui.pollute_tss_spin.setValue(self.module.get_parameter("obj_wq_target_tss"))
        self.ui.pollute_tn_spin.setValue(self.module.get_parameter("obj_wq_target_tn"))
        self.ui.pollute_tp_spin.setValue(self.module.get_parameter("obj_wq_target_tp"))
        self.ui.pollute_service_spin.setValue(self.module.get_parameter("obj_wq_service"))
        self.ui.pollute_redundancy_spin.setValue(self.module.get_parameter("obj_wq_redund"))
        self.ui.pollute_redundancy_ignore.setChecked(int(self.module.get_parameter("obj_wq_reignore")))

        self.ui.recycle_check.setChecked(int(self.module.get_parameter("obj_rec")))
        self.ui.recycle_pri_combo.setCurrentIndex(int(self.module.get_parameter("obj_rec_priority")) - 1)
        self.ui.recycle_target_spin.setValue(self.module.get_parameter("obj_rec_target"))
        self.ui.recycle_service_spin.setValue(self.module.get_parameter("obj_rec_service"))
        self.ui.recycle_redundancy_spin.setValue(self.module.get_parameter("obj_rec_redund"))
        self.ui.recycle_redundancy_ignore.setChecked(int(self.module.get_parameter("obj_rec_reignore")))

        self.ui.amenity_check.setChecked(int(self.module.get_parameter("obj_amen")))
        self.ui.amenity_pri_combo.setCurrentIndex(int(self.module.get_parameter("obj_amen_priority")) - 1)
        self.ui.amenity_green_spin.setValue(self.module.get_parameter("obj_amen_target_green"))
        self.ui.amenity_blue_spin.setValue(self.module.get_parameter("obj_amen_target_blue"))
        self.ui.amenity_target_andor.setCurrentIndex(int(self.module.get_parameter("obj_amen_target_andor")))
        self.ui.amenity_service_spin.setValue(self.module.get_parameter("obj_amen_service"))
        self.ui.amenity_redundancy_spin.setValue(self.module.get_parameter("obj_amen_redund"))
        self.ui.amenity_redundancy_ignore.setChecked(int(self.module.get_parameter("obj_amen_reignore")))

        # Ecological objective - COMING SOON [TO DO]

        # --- SPATIAL PLANNING RULES ---
        self.ui.service_res.setChecked(int(self.module.get_parameter("service_res")))
        self.ui.service_hdr.setChecked(int(self.module.get_parameter("service_hdr")))
        self.ui.service_com.setChecked(int(self.module.get_parameter("service_com")))
        self.ui.service_li.setChecked(int(self.module.get_parameter("service_li")))
        self.ui.service_hi.setChecked(int(self.module.get_parameter("service_hi")))
        self.ui.overlays_check.setChecked(int(self.module.get_parameter("overlays")))
        self.ui.restrictions_pgusable.setChecked(int(self.module.get_parameter("limit_pg_use")))
        self.ui.restrictions_pgusable_spin.setValue(self.module.get_parameter("limit_pg"))
        self.ui.restrictions_ref.setChecked(int(self.module.get_parameter("limit_ref")))
        self.ui.restrictions_for.setChecked(int(self.module.get_parameter("limit_for")))

        # --- EXISTING ASSETS ---

        # --- SELECT TECHNOLOGIES ---
        self.ui.biof.setChecked(int(self.module.get_parameter("use_BIOF")))
        self.ui.wsur.setChecked(int(self.module.get_parameter("use_WSUR")))
        self.ui.evap.setChecked(int(self.module.get_parameter("use_EVAP")))
        self.ui.infs.setChecked(int(self.module.get_parameter("use_INFS")))
        self.ui.pond.setChecked(int(self.module.get_parameter("use_POND")))
        self.ui.swal.setChecked(int(self.module.get_parameter("use_SWAL")))
        self.ui.roof.setChecked(int(self.module.get_parameter("use_ROOF")))
        self.ui.wall.setChecked(int(self.module.get_parameter("use_WALL")))
        self.ui.pave.setChecked(int(self.module.get_parameter("use_PAVE")))
        self.ui.tank.setChecked(int(self.module.get_parameter("use_TANK")))
        self.ui.basn.setChecked(int(self.module.get_parameter("use_BASN")))
        self.ui.filt.setChecked(int(self.module.get_parameter("use_FILT")))
        self.ui.disc.setChecked(int(self.module.get_parameter("use_DISC")))
        self.ui.bank.setChecked(int(self.module.get_parameter("use_BANK")))

        # --- SIMULATION SETTINGS ---
        self.ui.planalgo_combo.setCurrentIndex(
            self.planning_algorithms.index(str(self.module.get_parameter("planning_algorithm"))))
        self.ui.planscales_lot_check.setChecked(int(self.module.get_parameter("scale_lot")))
        self.ui.planscales_lot_rigour.setValue(int(self.module.get_parameter("scale_lot_rig")))
        self.ui.planscales_street_check.setChecked(int(self.module.get_parameter("scale_street")))
        self.ui.planscales_street_rigour.setValue(int(self.module.get_parameter("scale_street_rig")))
        self.ui.planscales_region_check.setChecked(int(self.module.get_parameter("scale_region")))
        self.ui.planscales_region_rigour.setValue(int(self.module.get_parameter("scale_region_rig")))
        self.ui.scalepref_check.setChecked(int(self.module.get_parameter("scale_preference")))
        self.ui.scalepref_slider.setValue(int(self.module.get_parameter("scale_preference_score")))

        # --- LIFE CYCLE COSTING DETAILS ---
        self.ui.lcc_check.setChecked(int(self.module.get_parameter("lcc_check")))
        self.ui.lcc_years_spin.setValue(int(self.module.get_parameter("lcc_period")))
        self.ui.lcc_capital_check.setChecked(int(self.module.get_parameter("lcc_capital")))
        self.ui.lcc_disc_spin.setValue(self.module.get_parameter("lcc_dc"))
        self.ui.lcc_infla_spin.setValue(self.module.get_parameter("lcc_if"))
        # self.ui.lcc_currency_combo.setCurrentIndex()
        self.ui.lcc_currency_combo2.setCurrentIndex(self.ui.lcc_currency_combo.currentIndex())
        self.ui.lcc_currency_convert_check.setChecked(int(self.module.get_parameter("lcc_conversion")))
        self.ui.lcc_currency_rate.setText(str(self.module.get_parameter("lcc_convrate")))
        self.ui.lcc_decom_at_end.setChecked(int(self.module.get_parameter("lcc_decom")))
        self.ui.lcc_maintain_also.setChecked(int(self.module.get_parameter("lcc_maintain")))
        self.ui.lcc_ignore_lifespan.setChecked(int(self.module.get_parameter("lcc_ignorelc")))

        # --- IMPLEMENTATION RULES ---

        # --- TECHNOLOGIES ---
        # - BIORETENTION SYSTEMS -


        # - CONSTRUCTED WETLANDS -


        # - EVAPORATION FIELDS -
        # - GREEN ROOF SYSTEMS -
        # - GREEN WALLS / FACADES -

        # - INFILTRATION SYSTEMS -

        # - PONDS & SEDIMENTATION BASINS -

        # - POROUS PAVEMENTS / PERVIOUS PAVEMENTS -

        # - RAINWATER / STORMWATER TANK SYSTEMS -


        # - RETARDING BASINS -
        # - SAND / GRAVEL FILTERS (French Drains) -

        # - SWALES -


        # - IMPERVIOUS SURFACE DISCONNECTION -
        # - RIVERBANK RESTORATION -

        # --- TECHNOLOGY PREFERENCE SCORES ---
        # --- EVALUATION, RANKING & SELECTION ---

        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        # --- PLANNING OBJECTIVES FOR BGS ---
        self.module.set_parameter("obj_run", int(self.ui.runoff_check.isChecked()))
        self.module.set_parameter("obj_run_priority", int(self.ui.runoff_pri_combo.currentIndex())+1)
        self.module.set_parameter("obj_run_target", float(self.ui.runoff_target_spin.value()))
        self.module.set_parameter("obj_run_service", float(self.ui.runoff_service_spin.value()))
        self.module.set_parameter("obj_run_redund", float(self.ui.runoff_redundancy_spin.value()))
        self.module.set_parameter("obj_run_reignore", int(self.ui.runoff_redundancy_ignore.isChecked()))

        self.module.set_parameter("obj_wq", int(self.ui.pollute_check.isChecked()))
        self.module.set_parameter("obj_wq_priority", int(self.ui.pollute_pri_combo.currentIndex()) + 1)
        self.module.set_parameter("obj_wq_target_tss", float(self.ui.pollute_tss_spin.value()))
        self.module.set_parameter("obj_wq_target_tn", float(self.ui.pollute_tn_spin.value()))
        self.module.set_parameter("obj_wq_target_tp", float(self.ui.pollute_tp_spin.value()))
        self.module.set_parameter("obj_wq_service", float(self.ui.pollute_service_spin.value()))
        self.module.set_parameter("obj_wq_redund", float(self.ui.pollute_redundancy_spin.value()))
        self.module.set_parameter("obj_wq_reignore", int(self.ui.pollute_redundancy_ignore.isChecked()))

        self.module.set_parameter("obj_rec", int(self.ui.recycle_check.isChecked()))
        self.module.set_parameter("obj_rec_priority", int(self.ui.recycle_pri_combo.currentIndex()) + 1)
        self.module.set_parameter("obj_rec_target", float(self.ui.recycle_target_spin.value()))
        self.module.set_parameter("obj_rec_service", float(self.ui.recycle_service_spin.value()))
        self.module.set_parameter("obj_rec_redund", float(self.ui.recycle_redundancy_spin.value()))
        self.module.set_parameter("obj_rec_reignore", int(self.ui.recycle_redundancy_ignore.isChecked()))

        self.module.set_parameter("obj_amen", int(self.ui.amenity_check.isChecked()))
        self.module.set_parameter("obj_amen_priority", int(self.ui.amenity_pri_combo.currentIndex()) + 1)
        self.module.set_parameter("obj_amen_target_green", float(self.ui.amenity_green_spin.value()))
        self.module.set_parameter("obj_amen_target_blue", float(self.ui.amenity_blue_spin.value()))
        self.module.set_parameter("obj_amen_target_andor", int(self.ui.amenity_target_andor.currentIndex()))
        self.module.set_parameter("obj_amen_service", float(self.ui.amenity_service_spin.value()))
        self.module.set_parameter("obj_amen_redund", float(self.ui.amenity_redundancy_spin.value()))
        self.module.set_parameter("obj_amen_reignore", int(self.ui.amenity_redundancy_ignore.isChecked()))

        # Ecological Objectives - COMING SOON [TO DO]

        # --- SPATIAL PLANNING RULES ---
        self.module.set_parameter("service_res", int(self.ui.service_res.isChecked()))
        self.module.set_parameter("service_hdr", int(self.ui.service_hdr.isChecked()))
        self.module.set_parameter("service_com", int(self.ui.service_com.isChecked()))
        self.module.set_parameter("service_li", int(self.ui.service_li.isChecked()))
        self.module.set_parameter("service_hi", int(self.ui.service_hi.isChecked()))
        self.module.set_parameter("overlays", int(self.ui.overlays_check.isChecked()))
        self.module.set_parameter("limit_pg_use", int(self.ui.restrictions_pgusable.isChecked()))
        self.module.set_parameter("limit_pg", float(self.ui.restrictions_pgusable_spin.value()))
        self.module.set_parameter("limit_ref", int(self.ui.restrictions_ref.isChecked()))
        self.module.set_parameter("limit_for", int(self.ui.restrictions_for.isChecked()))

        # --- EXISTING ASSETS ---

        # --- SELECT TECHNOLOGIES ---
        self.module.set_parameter("use_BIOF", int(self.ui.biof.isChecked()))
        self.module.set_parameter("use_WSUR", int(self.ui.wsur.isChecked()))
        self.module.set_parameter("use_EVAP", int(self.ui.evap.isChecked()))
        self.module.set_parameter("use_INFS", int(self.ui.infs.isChecked()))
        self.module.set_parameter("use_POND", int(self.ui.pond.isChecked()))
        self.module.set_parameter("use_SWAL", int(self.ui.swal.isChecked()))
        self.module.set_parameter("use_ROOF", int(self.ui.roof.isChecked()))
        self.module.set_parameter("use_WALL", int(self.ui.wall.isChecked()))
        self.module.set_parameter("use_PAVE", int(self.ui.pave.isChecked()))
        self.module.set_parameter("use_TANK", int(self.ui.tank.isChecked()))
        self.module.set_parameter("use_FILT", int(self.ui.filt.isChecked()))
        self.module.set_parameter("use_BASN", int(self.ui.basn.isChecked()))
        self.module.set_parameter("use_DISC", int(self.ui.disc.isChecked()))
        self.module.set_parameter("use_BANK", int(self.ui.bank.isChecked()))

        # --- SIMULATION SETTINGS ---
        self.module.set_parameter("planning_algorithm", self.planning_algorithms[self.ui.planalgo_combo.currentIndex()])
        self.module.set_parameter("scale_lot", int(self.ui.planscales_lot_check.isChecked()))
        self.module.set_parameter("scale_lot_rigour", int(self.ui.planscales_lot_rigour.value()))
        self.module.set_parameter("scale_street", int(self.ui.planscales_street_check.isChecked()))
        self.module.set_parameter("scale_street_rigour", int(self.ui.planscales_street_rigour.value()))
        self.module.set_parameter("scale_region", int(self.ui.planscales_region_check.isChecked()))
        self.module.set_parameter("scale_region_rigour", int(self.ui.planscales_region_rigour.value()))
        self.module.set_parameter("scale_preference", int(self.ui.scalepref_check.isChecked()))
        self.module.set_parameter("scale_preference_score", int(self.ui.scalepref_slider.value()))

        # --- LIFE CYCLE COSTING DETAILS ---
        self.module.set_parameter("lcc_check", int(self.ui.lcc_check.isChecked()))
        self.module.set_parameter("lcc_period", int(self.ui.lcc_years_spin.value()))
        self.module.set_parameter("lcc_capital", int(self.ui.lcc_capital_check.isChecked()))
        self.module.set_parameter("lcc_dc", float(self.ui.lcc_disc_spin.value()))
        self.module.set_parameter("lcc_if", float(self.ui.lcc_infla_spin.value()))
        # self.module.set_parameter("lcc_currency", str(self.ui.lcc_currency_combo.currentIndex()))
        self.module.set_parameter("lcc_conversion", int(self.ui.lcc_currency_convert_check.isChecked()))
        self.module.set_parameter("lcc_convrate", float(self.ui.lcc_currency_rate.text()))
        self.module.set_parameter("lcc_decom", int(self.ui.lcc_decom_at_end.isChecked()))
        self.module.set_parameter("lcc_maintain", int(self.ui.lcc_maintain_also.isChecked()))
        self.module.set_parameter("lcc_ignorelc", int(self.ui.lcc_ignore_lifespan.isChecked()))

        # --- IMPLEMENTATION RULES ---

        # --- TECHNOLOGIES ---
        # - BIORETENTION SYSTEMS -

        # - CONSTRUCTED WETLANDS -

        # - EVAPORATION FIELDS -
        # - GREEN ROOF SYSTEMS -
        # - GREEN WALLS / FACADES -

        # - INFILTRATION SYSTEMS -

        # - PONDS & SEDIMENTATION BASINS -

        # - POROUS PAVEMENTS / PERVIOUS PAVEMENTS -

        # - RAINWATER / STORMWATER TANK SYSTEMS -

        # - RETARDING BASINS -
        # - SAND / GRAVEL FILTERS (French Drains) -

        # - SWALES -

        # - IMPERVIOUS SURFACE DISCONNECTION -
        # - RIVERBANK RESTORATION -

        # --- TECHNOLOGY PREFERENCE SCORES ---
        # --- EVALUATION, RANKING & SELECTION ---

        return True
