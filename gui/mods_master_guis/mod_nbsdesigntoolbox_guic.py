r"""
@file   mod_nbsdesigntoolbox_guic.py
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
import pickle

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ublibs.ubspatial as ubspatial

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_nbsdesigntoolbox_gui import Ui_NbSDesignToolbox_Gui

# --- MAIN GUI FUNCTION ---
class NbSDesignToolboxSetupLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "NbS Planning and Design"
    catorder = 2
    longname = "Setup NbS Design Toolbox"
    icon = ":/icons/nbs_toolbox.png"

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
        self.ui = Ui_NbSDesignToolbox_Gui()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None
        self.geomtype = None  # The active asset collection's geometry type

        # --- Global Parameter Lookups ---
        self.sizingmethod = ["CAPTURE", "CURVE"]

        # --- PROGRESSBAR OBSERVER ---
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
        # Asset Collection
        self.ui.assetcol_combo.clear()
        self.ui.assetcol_combo.addItem("(select asset collection)")
        simgrids = self.simulation.get_global_asset_collection()
        for n in simgrids.keys():
            if mode != 1:  # If we are running standalone mode
                if simgrids[n].get_container_type() == "Standalone":
                    self.ui.assetcol_combo.addItem(str(n))
                self.ui.assetcol_combo.setEnabled(1)
            else:
                self.ui.assetcol_combo.addItem(
                    self.active_scenario.get_asset_collection_container().get_container_name())
                self.ui.assetcol_combo.setEnabled(0)
        self.update_asset_col_metadata()

        #Other combos

        # --- SIGNALS AND SLOTS ---
        # Navigation
        self.ui.nbs_selector.currentRowChanged.connect(self.navigate_nbs_menu)

        # Non-NbS GUI Pages
        self.ui.runoff_check.clicked.connect(self.enable_disable_guis)
        self.ui.pollute_check.clicked.connect(self.enable_disable_guis)
        self.ui.recycle_check.clicked.connect(self.enable_disable_guis)
        self.ui.overlays_check.clicked.connect(self.enable_disable_guis)
        self.ui.restrictions_pgusable.clicked.connect(self.enable_disable_guis)
        self.ui.planscales_lot_check.clicked.connect(self.enable_disable_guis)
        self.ui.planscales_street_check.clicked.connect(self.enable_disable_guis)
        self.ui.planscales_region_check.clicked.connect(self.enable_disable_guis)
        self.ui.planscales_lot_rigour.valueChanged.connect(self.update_planslider_values)
        self.ui.planscales_street_rigour.valueChanged.connect(self.update_planslider_values)
        self.ui.planscales_region_rigour.valueChanged.connect(self.update_planslider_values)
        self.ui.assets_check.clicked.connect(self.enable_disable_guis)

        # NbS GUI Pages
        self.ui.nbs_selector.itemChanged.connect(self.enable_disable_system_guis)
        self.ui.bf_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.bf_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        # bf_curveselect_custom_browse [TO DO]
        self.ui.bf_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.setup_gui_with_parameters()
        self.enable_disable_guis()
        self.enable_disable_system_guis()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def navigate_nbs_menu(self):
        """Switches the stack widget to the correct page."""
        pageIndex = self.ui.nbs_selector.currentRow()
        if pageIndex in [0, 3]:
            return True     # These are the headers... ignore them
        if pageIndex in [1, 2]: # Skipping the first header
            pageIndex -= 1
        elif pageIndex > 3:     # Skipping headers
            pageIndex -= 2
        self.ui.stackedWidget.setCurrentIndex(pageIndex)
        return True

    def update_planslider_values(self):
        """Updates the boxes for the different scales and levels of rigour sliders."""
        self.ui.planscales_lot_box.setText(str(int(self.ui.planscales_lot_rigour.value())))
        self.ui.planscales_street_box.setText(str(int(self.ui.planscales_street_rigour.value())))
        self.ui.planscales_region_box.setText(str(int(self.ui.planscales_region_rigour.value())))

    def enable_disable_guis(self):
        """Enables and disables GUI elements NOT belonging to the individual NbS Systems"""
        # Spatial Planning Options
        self.ui.runoff_target_spin.setEnabled(self.ui.runoff_check.isChecked())
        self.ui.runoff_pri_combo.setEnabled(self.ui.runoff_check.isChecked())
        self.ui.pollute_tss_spin.setEnabled(self.ui.pollute_check.isChecked())
        self.ui.pollute_pri_combo.setEnabled(self.ui.pollute_check.isChecked())
        self.ui.pollute_tn_spin.setEnabled(self.ui.pollute_check.isChecked())
        self.ui.pollute_tp_spin.setEnabled(self.ui.pollute_check.isChecked())
        self.ui.recycle_target_spin.setEnabled(self.ui.recycle_check.isChecked())
        self.ui.recycle_pri_combo.setEnabled(self.ui.recycle_check.isChecked())

        self.ui.suitability_widget_shp.setEnabled(self.ui.overlays_check.isChecked())
        self.ui.suitability_widget_lu.setEnabled(self.ui.overlays_check.isChecked())
        self.ui.restrictions_pgusable_spin.setEnabled(self.ui.restrictions_pgusable.isChecked())
        self.ui.restrictions_widget.setEnabled(self.ui.overlays_check.isChecked())

        self.ui.planscales_lot_rigour.setEnabled(self.ui.planscales_lot_check.isChecked())
        self.ui.planscales_lot_box.setEnabled(self.ui.planscales_lot_check.isChecked())
        self.ui.planscales_street_rigour.setEnabled(self.ui.planscales_street_check.isChecked())
        self.ui.planscales_street_box.setEnabled(self.ui.planscales_street_check.isChecked())
        self.ui.planscales_region_rigour.setEnabled(self.ui.planscales_region_check.isChecked())
        self.ui.planscales_region_box.setEnabled(self.ui.planscales_region_check.isChecked())

        # Load Existing Systems
        self.ui.assets_widget.setEnabled(self.ui.assets_check.isChecked())
        self.ui.assets_table.setEnabled(self.ui.assets_check.isChecked())
        self.ui.assets_table_widget_2.setEnabled(self.ui.assets_check.isChecked())

    def enable_disable_system_guis(self):
        # BIOFILTERS
        self.ui.bf_scrollarea.setEnabled(bool(self.ui.nbs_selector.item(4).checkState()))
        self.ui.bf_spec_stack.setCurrentIndex(self.ui.bf_specmethod_combo.currentIndex())
        self.ui.bf_capturewq_widget.setEnabled(not self.ui.bf_capture_check.isChecked())
        self.ui.bf_curveselect_custom_box.setEnabled(self.ui.bf_curveselect_custom_radio.isChecked())
        self.ui.bf_curveselect_custom_browse.setEnabled(self.ui.bf_curveselect_custom_radio.isChecked())
        if self.ui.bf_lcc_costdetailed_radio.isChecked():
            self.ui.bf_lcc_coststack.setCurrentIndex(0)
        else:
            self.ui.bf_lcc_coststack.setCurrentIndex(1)

        # CONSTRUCTED WETLANDS
        self.ui.wet_scrollarea.setEnabled(bool(self.ui.nbs_selector.item(5).checkState()))
        # GREEN ROOF SYSTEMS
        # [TO DO]
        # GREEN WALLS FACADES
        # [TO DO]
        # INFILTRATION SYSTEMS
        # PONDS AND SEDIMENTATION BASINS
        # POROUS PAVEMENTS
        # RAINWATER/STORMWATER TANKS
        # RETARDING BASINS/FLOODPLAINS
        # SWALES

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # === SECTION: MENU OF SYSTEMS ================================================
        if self.module.get_parameter("bf"): self.ui.nbs_selector.item(4).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("wsur"): self.ui.nbs_selector.item(5).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("roof"): self.ui.nbs_selector.item(6).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("wall"): self.ui.nbs_selector.item(7).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("infil"): self.ui.nbs_selector.item(8).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("pb"): self.ui.nbs_selector.item(9).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("pp"): self.ui.nbs_selector.item(10).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("tank"): self.ui.nbs_selector.item(11).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("retb"): self.ui.nbs_selector.item(12).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("sw"): self.ui.nbs_selector.item(13).setCheckState(QtCore.Qt.CheckState.Checked)

        # === SECTION: SPATIAL PLANNING OPTIONS =======================================
        # Planning Objectives
        self.ui.runoff_check.setChecked(int(self.module.get_parameter("runoff_obj")))
        self.ui.runoff_pri_combo.setCurrentIndex(int(self.module.get_parameter("runoff_priority")))
        self.ui.runoff_target_spin.setValue(self.module.get_parameter("runoff_tar"))
        self.ui.pollute_check.setChecked(int(self.module.get_parameter("wq_obj")))
        self.ui.pollute_pri_combo.setCurrentIndex(int(self.module.get_parameter("wq_priority")))
        self.ui.pollute_tss_spin.setValue(self.module.get_parameter("wq_tss_tar"))
        self.ui.pollute_tn_spin.setValue(self.module.get_parameter("wq_tn_tar"))
        self.ui.pollute_tp_spin.setValue(self.module.get_parameter("wq_tp_tar"))
        self.ui.recycle_check.setChecked(int(self.module.get_parameter("rec_obj")))
        self.ui.recycle_pri_combo.setCurrentIndex(int(self.module.get_parameter("rec_priority")))
        self.ui.recycle_target_spin.setValue(self.module.get_parameter("rec_tar"))

        # Planning Restrictions
        self.ui.overlays_check.setChecked(int(self.module.get_parameter("consider_overlays")))
        # [ TO DO ] Coming Soon!

        self.ui.restrictions_pgusable.setChecked(int(self.module.get_parameter("allow_pg")))
        self.ui.restrictions_pgusable_spin.setValue(self.module.get_parameter("allow_pg_val"))
        self.ui.restrictions_ref.setChecked(int(self.module.get_parameter("prohibit_ref")))
        self.ui.restrictions_for.setChecked(int(self.module.get_parameter("prohibit_for")))

        # Scales and Levels of Rigour
        self.ui.planscales_lot_check.setChecked(int(self.module.get_parameter("scale_lot")))
        self.ui.planscales_street_check.setChecked(int(self.module.get_parameter("scale_street")))
        self.ui.planscales_region_check.setChecked(int(self.module.get_parameter("scale_region")))
        self.ui.planscales_lot_rigour.setValue(int(self.module.get_parameter("lot_rigour")))
        self.ui.planscales_street_rigour.setValue(int(self.module.get_parameter("street_rigour")))
        self.ui.planscales_lot_rigour.setValue(int(self.module.get_parameter("region_rigour")))

        # === SECTION: LOAD EXISTING NBS ASSETS =======================================

        # === SECTION: BIORETENTION/RAINGARDENS =======================================
        # Scales and Types of Application and permissible location
        self.ui.bf_lot_check.setChecked(int(self.module.get_parameter("bf_lot")))
        self.ui.bf_st_check.setChecked(int(self.module.get_parameter("bf_street")))
        self.ui.bf_reg_check.setChecked(int(self.module.get_parameter("bf_region")))
        self.ui.bf_flow_check.setChecked(int(self.module.get_parameter("bf_flow")))
        self.ui.bf_pollute_check.setChecked(int(self.module.get_parameter("bf_wq")))
        self.ui.bf_recycle_check.setChecked(int(self.module.get_parameter("bf_rec")))

        bf_locs = self.module.get_parameter("bf_permissions")
        self.ui.bf_pg_check.setChecked(int(bf_locs["PG"]))
        self.ui.bf_ref_check.setChecked(int(bf_locs["REF"]))
        self.ui.bf_for_check.setChecked(int(bf_locs["FOR"]))
        self.ui.bf_agr_check.setChecked(int(bf_locs["AGR"]))
        self.ui.bf_und_check.setChecked(int(bf_locs["UND"]))
        self.ui.bf_ns_check.setChecked(int(bf_locs["nstrip"]))
        self.ui.bf_garden_check.setChecked(int(bf_locs["garden"]))

        # System Sizing and Spec
        self.ui.bf_specmethod_combo.setCurrentIndex(self.sizingmethod.index(self.module.get_parameter("bfmethod")))
        self.ui.bf_capture_check.setChecked(int(self.module.get_parameter("bf_univcapt")))
        self.ui.bf_captureflow_ratiospin.setValue(self.module.get_parameter("bf_flow_surfAratio"))
        if self.module.get_parameter("bf_flow_ratiodef") == "ALL":
            self.ui.bf_captureflow_area_radio.setChecked(1)
        else:
            self.ui.bf_captureflow_imp_radio.setChecked(1)
        self.ui.bf_capturewq_ratiospin.setValue(self.module.get_parameter("bf_wq_surfAratio"))
        if self.module.get_parameter("bf_wq_ratiodef") == "ALL":
            self.ui.bf_capturewq_area_radio.setChecked(1)
        else:
            self.ui.bf_capturewq_imp_radio.setChecked(1)
        if self.module.get_parameter("dcurvemethod") == "UBEATS":
            self.ui.bf_curveselect_default_radio.setChecked(1)
        else:
            self.ui.bf_curveselect_custom_radio.setChecked(1)
        self.ui.bf_curveselect_custom_box.setText(self.module.get_parameter("bf_custombox"))

        # General System Characteristics
        bf_ed = [0, 100, 200, 300, 400]
        bf_fd = [200, 400, 600, 800]
        bf_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.ui.bf_spec_systemchar_ed.setCurrentIndex(bf_ed.index(self.module.get_parameter("bf_ed")))
        self.ui.bf_spec_systemchar_fd.setCurrentIndex(bf_fd.index(self.module.get_parameter("bf_fd")))
        self.ui.bf_spec_systemchar_rangemin_box.setText(str(self.module.get_parameter("bf_minsize")))
        self.ui.bf_spec_systemchar_rangemax_box.setText(str(self.module.get_parameter("bf_maxsize")))
        self.ui.bf_spec_systemchar_exfil_combo.setCurrentIndex(bf_exfil.index(self.module.get_parameter("bf_exfil")))

        # Life Cycle and Costing Information
        self.ui.bf_lcc_avglife_spin.setValue(self.module.get_parameter("bf_avglife"))
        self.ui.bf_lcc_renewal_spin.setValue(self.module.get_parameter("bf_renewcycle"))
        if self.module.get_parameter("bf_costmethod") == "DETAIL":
            self.ui.bf_lcc_costdetailed_radio.setChecked(1)
        else:
            self.ui.bf_lcc_costindicative_radio.setChecked(1)
        self.ui.bf_lcc_tac_box.setText(str(self.module.get_parameter("bf_tac")))
        self.ui.bf_lcc_tacind_box.setText(str(self.module.get_parameter("bf_tac")))
        self.ui.bf_lcc_tam_box.setText(str(self.module.get_parameter("bf_tam")))
        self.ui.bf_lcc_rc_box.setText(str(self.module.get_parameter("bf_new")))
        self.ui.bf_lcc_dc_box.setText(str(self.module.get_parameter("bf_decom")))
        self.ui.bf_lcc_tamind_spin.setValue(self.module.get_parameter("bf_tam_pct"))
        self.ui.bf_lcc_rcind_spin.setValue(self.module.get_parameter("bf_new_pct"))
        self.ui.bf_lcc_dcind_spin.setValue(self.module.get_parameter("bf_decom_pct"))
        # --- END OF BIORETENTION / RAINGARDEN ---

        # === SECTION: CONSTRUCTED WETLANDS =======================================

        # --- END OF CONSTRUCTED WETLANDS ---


        return True

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        # === SECTION: MENU OF SYSTEMS ================================================
        self.module.set_parameter("bf", int(bool(self.ui.nbs_selector.item(4).checkState())))
        self.module.set_parameter("wsur", int(bool(self.ui.nbs_selector.item(5).checkState())))
        self.module.set_parameter("roof", int(bool(self.ui.nbs_selector.item(6).checkState())))
        self.module.set_parameter("wall", int(bool(self.ui.nbs_selector.item(7).checkState())))
        self.module.set_parameter("infil", int(bool(self.ui.nbs_selector.item(8).checkState())))
        self.module.set_parameter("pb", int(bool(self.ui.nbs_selector.item(9).checkState())))
        self.module.set_parameter("pp", int(bool(self.ui.nbs_selector.item(10).checkState())))
        self.module.set_parameter("tank", int(bool(self.ui.nbs_selector.item(11).checkState())))
        self.module.set_parameter("retb", int(bool(self.ui.nbs_selector.item(12).checkState())))
        self.module.set_parameter("sw", int(bool(self.ui.nbs_selector.item(13).checkState())))

        # === SECTION: SPATIAL PLANNING OPTIONS =======================================
        # Planning Objectives
        self.module.set_parameter("runoff_obj", int(self.ui.runoff_check.isChecked()))
        self.module.set_parameter("runoff_priority", int(self.ui.runoff_pri_combo.currentIndex()))
        self.module.set_parameter("runoff_tar", float(self.ui.runoff_target_spin.value()))
        self.module.set_parameter("wq_obj", int(self.ui.pollute_check.isChecked()))
        self.module.set_parameter("wq_priority", int(self.ui.pollute_pri_combo.currentIndex()))
        self.module.set_parameter("wq_tss_tar", float(self.ui.pollute_tss_spin.value()))
        self.module.set_parameter("wq_tn_tar", float(self.ui.pollute_tn_spin.value()))
        self.module.set_parameter("wq_tp_tar", float(self.ui.pollute_tp_spin.value()))
        self.module.set_parameter("rec_obj", int(self.ui.recycle_check.isChecked()))
        self.module.set_parameter("rec_priority", int(self.ui.recycle_pri_combo.currentIndex()))
        self.module.set_parameter("rec_tar", float(self.ui.recycle_target_spin.value()))

        # Planning Restrictions
        self.module.set_parameter("consider_overlays", int(self.ui.overlays_check.isChecked()))
        # [ TO DO ] Coming Soon!

        self.module.set_parameter("allow_pg", int(self.ui.restrictions_pgusable.isChecked()))
        self.module.set_parameter("allow_pg_val", float(self.ui.restrictions_pgusable_spin.value()))
        self.module.set_parameter("prohibit_ref", int(self.ui.restrictions_ref.isChecked()))
        self.module.set_parameter("prohibit_for", int(self.ui.restrictions_for.isChecked()))

        # Scales and Levels of Rigour
        self.module.set_parameter("scale_lot", int(self.ui.planscales_lot_check.isChecked()))
        self.module.set_parameter("scale_street", int(self.ui.planscales_street_check.isChecked()))
        self.module.set_parameter("scale_region", int(self.ui.planscales_region_check.isChecked()))
        self.module.set_parameter("lot_rigour", float(self.ui.planscales_lot_rigour.value()))
        self.module.set_parameter("street_rigour", float(self.ui.planscales_street_rigour.value()))
        self.module.set_parameter("region_rigour", float(self.ui.planscales_region_rigour.value()))

        # === SECTION: LOAD EXISTING NBS ASSETS =======================================

        # === SECTION: BIORETENTION/RAINGARDENS =======================================
        # Scales and Types of Application and permissible location
        self.module.set_parameter("bf_lot", int(self.ui.bf_lot_check.isChecked()))
        self.module.set_parameter("bf_street", int(self.ui.bf_st_check.isChecked()))
        self.module.set_parameter("bf_region", int(self.ui.bf_reg_check.isChecked()))
        self.module.set_parameter("bf_flow", int(self.ui.bf_flow_check.isChecked()))
        self.module.set_parameter("bf_wq", int(self.ui.bf_pollute_check.isChecked()))
        self.module.set_parameter("bf_rec", int(self.ui.bf_recycle_check.isChecked()))

        bf_locs = {
            "PG": int(self.ui.bf_pg_check.isChecked()),
            "REF": int(self.ui.bf_ref_check.isChecked()),
            "FOR": int(self.ui.bf_for_check.isChecked()),
            "AGR": int(self.ui.bf_agr_check.isChecked()),
            "UND": int(self.ui.bf_und_check.isChecked()),
            "nstrip": int(self.ui.bf_ns_check.isChecked()),
            "garden": int(self.ui.bf_garden_check.isChecked())
        }
        self.module.set_parameter("bf_permissions", bf_locs)

        # System Sizing and Spec
        if self.ui.bf_specmethod_combo.currentIndex() == 0:
            self.module.set_parameter("bfmethod", "CAPTURE")
        else:
            self.module.set_parameter("bfmethod", "CURVE")

        self.module.set_parameter("bf_univcapt", int(self.ui.bf_capture_check.isChecked()))
        self.module.set_parameter("bf_flow_surfAratio", float(self.ui.bf_captureflow_ratiospin.value()))
        if self.ui.bf_captureflow_area_radio.isChecked():
            self.module.set_parameter("bf_flow_ratiodef", "ALL")
        else:
            self.module.set_parameter("bf_flow_ratiodef", "IMP")
        self.module.set_parameter("bf_wq_surfAratio", float(self.ui.bf_capturewq_ratiospin.value()))
        if self.ui.bf_capturewq_area_radio.isChecked():
            self.module.set_parameter("bf_wq_ratiodef", "ALL")
        else:
            self.module.set_parameter("bf_wq_ratiodef", "IMP")
        if self.ui.bf_curveselect_default_radio.isChecked():
            self.module.set_parameter("dcurvemethod", "UBEATS")
        else:
            self.module.set_parameter("dcurvemethod", "CUSTOM")
        self.module.set_parameter("bf_custombox", str(self.ui.bf_curveselect_custom_box.text()))

        # General System Characteristics
        bf_ed = [0, 100, 200, 300, 400]
        bf_fd = [200, 400, 600, 800]
        bf_exfil = [0, 0.18, 0.36, 1.8, 3.6]

        self.module.set_parameter("bf_ed", bf_ed[self.ui.bf_spec_systemchar_ed.currentIndex()])
        self.module.set_parameter("bf_fd", bf_fd[self.ui.bf_spec_systemchar_fd.currentIndex()])
        self.module.set_parameter("bf_minsize", float(self.ui.bf_spec_systemchar_rangemin_box.text()))
        self.module.set_parameter("bf_maxsize", float(self.ui.bf_spec_systemchar_rangemax_box.text()))
        self.module.set_parameter("bf_exfil", bf_exfil[self.ui.bf_spec_systemchar_exfil_combo.currentIndex()])

        # Life Cycle and Costing Information
        self.module.set_parameter("bf_avglife", float(self.ui.bf_lcc_avglife_spin.value()))
        self.module.set_parameter("bf_renewcycle", float(self.ui.bf_lcc_renewal_spin.value()))
        if self.ui.bf_lcc_costdetailed_radio.isChecked():
            self.module.set_parameter("bf_costmethod", "DETAIL")        # Set only the detailed parameters
            self.module.set_parameter("bf_tac", float(self.ui.bf_lcc_tac_box.text()))
            self.module.set_parameter("bf_tam", float(self.ui.bf_lcc_tam_box.text()))
            self.module.set_parameter("bf_new", float(self.ui.bf_lcc_rc_box.text()))
            self.module.set_parameter("bf_decom", float(self.ui.bf_lcc_dc_box.text()))
        else:
            self.module.set_parameter("bf_costmethod", "INDIC")         # Set only the indicative parameters
            self.module.set_parameter("bf_tac", float(self.ui.bf_lcc_tacind_box.text()))
            self.module.set_parameter("bf_tam_pct", float(self.ui.bf_lcc_tamind_spin.value()))
            self.module.set_parameter("bf_new_pct", float(self.ui.bf_lcc_rcind_spin.value()))
            self.module.set_parameter("bf_decom_pct", float(self.ui.bf_lcc_dcind_spin.value()))
        # --- END OF BIORETENTION / RAINGARDEN ---

        return True

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

        return True
