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

        # BIOFILTER
        self.ui.bf_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.bf_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_curveselect_custom_browse.clicked.connect(self.load_bf_designcurve_file)
        # bf_curveselect_custom_browse [TO DO]
        self.ui.bf_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.bf_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

        # WETLANDS
        self.ui.wet_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.wet_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.wet_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.wet_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        # wet_curveselect_custom_browse [TO DO]
        self.ui.wet_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.wet_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

        # GREEN ROOF SYSTEMS
        # [TO DO]
        # GREEN WALLS FACADES
        # [TO DO]
        # INFILTRATION SYSTEMS
        self.ui.infil_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.infil_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.infil_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.infil_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        # infil_curveselect_custom_browse [TO DO]
        self.ui.infil_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.infil_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

        # PONDS AND SEDIMENTATION BASINS
        self.ui.pb_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.pb_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.pb_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.pb_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        # pb_curveselect_custom_browse [TO DO]
        self.ui.pb_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.pb_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

        # POROUS PAVEMENTS
        # RAINWATER/STORMWATER TANKS
        self.ui.tank_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.tank_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.tank_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.tank_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        # tank_curveselect_custom_browse [TO DO]
        self.ui.tank_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.tank_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

        # RETARDING BASINS/FLOODPLAINS
        # SWALES
        self.ui.sw_specmethod_combo.currentIndexChanged.connect(self.enable_disable_system_guis)
        self.ui.sw_capture_check.clicked.connect(self.enable_disable_system_guis)
        self.ui.sw_curveselect_default_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.sw_curveselect_custom_radio.clicked.connect(self.enable_disable_system_guis)
        # sw_curveselect_custom_browse [TO DO]
        self.ui.sw_lcc_costdetailed_radio.clicked.connect(self.enable_disable_system_guis)
        self.ui.sw_lcc_costindicative_radio.clicked.connect(self.enable_disable_system_guis)

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
        self.ui.wet_spec_stack.setCurrentIndex(self.ui.wet_specmethod_combo.currentIndex())
        self.ui.wet_capturewq_widget.setEnabled(not self.ui.wet_capture_check.isChecked())
        self.ui.wet_curveselect_custom_box.setEnabled(self.ui.wet_curveselect_custom_radio.isChecked())
        self.ui.wet_curveselect_custom_browse.setEnabled(self.ui.wet_curveselect_custom_radio.isChecked())
        if self.ui.wet_lcc_costdetailed_radio.isChecked():
            self.ui.wet_lcc_coststack.setCurrentIndex(0)
        else:
            self.ui.wet_lcc_coststack.setCurrentIndex(1)

        # GREEN ROOF SYSTEMS
        # [TO DO]
        # GREEN WALLS FACADES
        # [TO DO]
        # INFILTRATION SYSTEMS
        self.ui.infil_scrollarea.setEnabled(bool(self.ui.nbs_selector.item(8).checkState()))
        self.ui.infil_spec_stack.setCurrentIndex(self.ui.infil_specmethod_combo.currentIndex())
        self.ui.infil_capturewq_widget.setEnabled(not self.ui.infil_capture_check.isChecked())
        self.ui.infil_curveselect_custom_box.setEnabled(self.ui.infil_curveselect_custom_radio.isChecked())
        self.ui.infil_curveselect_custom_browse.setEnabled(self.ui.infil_curveselect_custom_radio.isChecked())
        if self.ui.infil_lcc_costdetailed_radio.isChecked():
            self.ui.infil_lcc_coststack.setCurrentIndex(0)
        else:
            self.ui.infil_lcc_coststack.setCurrentIndex(1)

        # PONDS AND SEDIMENTATION BASINS
        self.ui.pb_scrollarea.setEnabled(bool(self.ui.nbs_selector.item(9).checkState()))
        self.ui.pb_spec_stack.setCurrentIndex(self.ui.pb_specmethod_combo.currentIndex())
        self.ui.pb_capturewq_widget.setEnabled(not self.ui.pb_capture_check.isChecked())
        self.ui.pb_curveselect_custom_box.setEnabled(self.ui.pb_curveselect_custom_radio.isChecked())
        self.ui.pb_curveselect_custom_browse.setEnabled(self.ui.pb_curveselect_custom_radio.isChecked())
        if self.ui.pb_lcc_costdetailed_radio.isChecked():
            self.ui.pb_lcc_coststack.setCurrentIndex(0)
        else:
            self.ui.pb_lcc_coststack.setCurrentIndex(1)

        # POROUS PAVEMENTS
        # RAINWATER/STORMWATER TANKS
        self.ui.tank_scrollarea.setEnabled(bool(self.ui.nbs_selector.item(11).checkState()))
        self.ui.tank_spec_stack.setCurrentIndex(self.ui.tank_specmethod_combo.currentIndex())
        self.ui.tank_capturewq_widget.setEnabled(not self.ui.tank_capture_check.isChecked())
        self.ui.tank_curveselect_custom_box.setEnabled(self.ui.tank_curveselect_custom_radio.isChecked())
        self.ui.tank_curveselect_custom_browse.setEnabled(self.ui.tank_curveselect_custom_radio.isChecked())
        if self.ui.tank_lcc_costdetailed_radio.isChecked():
            self.ui.tank_lcc_coststack.setCurrentIndex(0)
        else:
            self.ui.tank_lcc_coststack.setCurrentIndex(1)

        # RETARDING BASINS/FLOODPLAINS
        # SWALES
        self.ui.sw_scrollarea.setEnabled(bool(self.ui.nbs_selector.item(13).checkState()))
        self.ui.sw_spec_stack.setCurrentIndex(self.ui.sw_specmethod_combo.currentIndex())
        self.ui.sw_capturewq_widget.setEnabled(not self.ui.sw_capture_check.isChecked())
        self.ui.sw_curveselect_custom_box.setEnabled(self.ui.sw_curveselect_custom_radio.isChecked())
        self.ui.sw_curveselect_custom_browse.setEnabled(self.ui.sw_curveselect_custom_radio.isChecked())
        if self.ui.sw_lcc_costdetailed_radio.isChecked():
            self.ui.sw_lcc_coststack.setCurrentIndex(0)
        else:
            self.ui.sw_lcc_coststack.setCurrentIndex(1)

    # BROWSE FUNCTINS FOR DESIGN CURVE FILE FOR EACH SYSTEM
    # --- Biofilters ---
    def load_bf_designcurve_file(self):
        """Browse for a .dcv filename to load into the module."""
        dir = self.simulation.get_project_path()
        message = "Load Custom Design Curve File (.dcv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB DesignCurve (*.dcv)")
        if filename:
            self.ui.bf_curveselect_custom_box.setText(filename)
        return True

    # --- Wetlands ---
    def load_wet_designcurve_file(self):
        """Browse for a .dcv filename to load into the module."""
        dir = self.simulation.get_project_path()
        message = "Load Custom Design Curve File (.dcv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB DesignCurve (*.dcv)")
        if filename:
            self.ui.wet_curveselect_custom_box.setText(filename)
        return True

    # --- Green Roofs ---
    # --- Green Walls/Living Walls ---

    # --- Infiltration Systems ---
    def load_infil_designcurve_file(self):
        """Browse for a .dcv filename to load into the module."""
        dir = self.simulation.get_project_path()
        message = "Load Custom Design Curve File (.dcv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB DesignCurve (*.dcv)")
        if filename:
            self.ui.infil_curveselect_custom_box.setText(filename)
        return True

    # --- Ponds & Basins ---
    def load_pb_designcurve_file(self):
        """Browse for a .dcv filename to load into the module."""
        dir = self.simulation.get_project_path()
        message = "Load Custom Design Curve File (.dcv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB DesignCurve (*.dcv)")
        if filename:
            self.ui.pb_curveselect_custom_box.setText(filename)
        return True

    # --- Porous Pavements ---

    # --- Rainwater Tanks ---
    def load_tank_designcurve_file(self):
        """Browse for a .dcv filename to load into the module."""
        dir = self.simulation.get_project_path()
        message = "Load Custom Design Curve File (.dcv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB DesignCurve (*.dcv)")
        if filename:
            self.ui.tank_curveselect_custom_box.setText(filename)
        return True

    # --- Retarding Basins/Floodplains ---

    # --- Swales ---
    def load_sw_designcurve_file(self):
        """Browse for a .dcv filename to load into the module."""
        dir = self.simulation.get_project_path()
        message = "Load Custom Design Curve File (.dcv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "UB DesignCurve (*.dcv)")
        if filename:
            self.ui.sw_curveselect_custom_box.setText(filename)
        return True

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # === SECTION: MENU OF SYSTEMS ================================================
        if self.module.get_parameter("bf"): self.ui.nbs_selector.item(4).setCheckState(QtCore.Qt.CheckState.Checked)
        if self.module.get_parameter("wet"): self.ui.nbs_selector.item(5).setCheckState(QtCore.Qt.CheckState.Checked)
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
        self.ui.bf_specmethod_combo.setCurrentIndex(self.sizingmethod.index(self.module.get_parameter("bf_method")))
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
        self.ui.bf_curveselect_custom_box.setText(str(self.module.get_parameter("bf_dccustomfile")))

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
        # Scales and Types of Application and permissible location
        self.ui.wet_st_check.setChecked(int(self.module.get_parameter("wet_street")))
        self.ui.wet_reg_check.setChecked(int(self.module.get_parameter("wet_region")))
        self.ui.wet_flow_check.setChecked(int(self.module.get_parameter("wet_flow")))
        self.ui.wet_pollute_check.setChecked(int(self.module.get_parameter("wet_wq")))
        self.ui.wet_recycle_check.setChecked(int(self.module.get_parameter("wet_rec")))

        wet_locs = self.module.get_parameter("wet_permissions")
        self.ui.wet_pg_check.setChecked(int(wet_locs["PG"]))
        self.ui.wet_ref_check.setChecked(int(wet_locs["REF"]))
        self.ui.wet_for_check.setChecked(int(wet_locs["FOR"]))
        self.ui.wet_agr_check.setChecked(int(wet_locs["AGR"]))
        self.ui.wet_und_check.setChecked(int(wet_locs["UND"]))

        # System Sizing and Spec
        self.ui.wet_specmethod_combo.setCurrentIndex(self.sizingmethod.index(self.module.get_parameter("wet_method")))
        self.ui.wet_capture_check.setChecked(int(self.module.get_parameter("wet_univcapt")))
        self.ui.wet_captureflow_ratiospin.setValue(self.module.get_parameter("wet_flow_surfAratio"))
        if self.module.get_parameter("wet_flow_ratiodef") == "ALL":
            self.ui.wet_captureflow_area_radio.setChecked(1)
        else:
            self.ui.wet_captureflow_imp_radio.setChecked(1)
        self.ui.wet_capturewq_ratiospin.setValue(self.module.get_parameter("wet_wq_surfAratio"))
        if self.module.get_parameter("wet_wq_ratiodef") == "ALL":
            self.ui.wet_capturewq_area_radio.setChecked(1)
        else:
            self.ui.wet_capturewq_imp_radio.setChecked(1)
        if self.module.get_parameter("dcurvemethod") == "UBEATS":
            self.ui.wet_curveselect_default_radio.setChecked(1)
        else:
            self.ui.wet_curveselect_custom_radio.setChecked(1)
        self.ui.wet_curveselect_custom_box.setText(str(self.module.get_parameter("wet_dccustomfile")))

        # General System Characteristics
        wet_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.ui.wet_spec_systemchar_combo.setCurrentIndex(int(self.module.get_parameter("wet_spec")))
        self.ui.wet_spec_systemchar_rangemin_box.setText(str(self.module.get_parameter("wet_minsize")))
        self.ui.wet_spec_systemchar_rangemax_box.setText(str(self.module.get_parameter("wet_maxsize")))
        self.ui.wet_spec_systemchar_exfil_combo.setCurrentIndex(wet_exfil.index(self.module.get_parameter("wet_exfil")))

        # Life Cycle and Costing Information
        self.ui.wet_lcc_avglife_spin.setValue(self.module.get_parameter("wet_avglife"))
        self.ui.wet_lcc_renewal_spin.setValue(self.module.get_parameter("wet_renewcycle"))
        if self.module.get_parameter("wet_costmethod") == "DETAIL":
            self.ui.wet_lcc_costdetailed_radio.setChecked(1)
        else:
            self.ui.wet_lcc_costindicative_radio.setChecked(1)
        self.ui.wet_lcc_tac_box.setText(str(self.module.get_parameter("wet_tac")))
        self.ui.wet_lcc_tacind_box.setText(str(self.module.get_parameter("wet_tac")))
        self.ui.wet_lcc_tam_box.setText(str(self.module.get_parameter("wet_tam")))
        self.ui.wet_lcc_rc_box.setText(str(self.module.get_parameter("wet_new")))
        self.ui.wet_lcc_dc_box.setText(str(self.module.get_parameter("wet_decom")))
        self.ui.wet_lcc_tamind_spin.setValue(self.module.get_parameter("wet_tam_pct"))
        self.ui.wet_lcc_rcind_spin.setValue(self.module.get_parameter("wet_new_pct"))
        self.ui.wet_lcc_dcind_spin.setValue(self.module.get_parameter("wet_decom_pct"))
        # --- END OF CONSTRUCTED WETLANDS ---

        # === SECTION: GREEN ROOF SYSTEMS =======================================
        # --- END OF GREEN ROOF SYSTEMS ---

        # === SECTION: GREEN WALLS/LIVING WALLS =======================================
        # --- END OF GREEN WALLS/LIVING WALLS ---

        # === SECTION: INFILTRATION SYSTEMS =======================================
        # Scales and Types of Application and permissible location
        self.ui.infil_lot_check.setChecked(int(self.module.get_parameter("infil_lot")))
        self.ui.infil_st_check.setChecked(int(self.module.get_parameter("infil_street")))
        self.ui.infil_reg_check.setChecked(int(self.module.get_parameter("infil_region")))
        self.ui.infil_flow_check.setChecked(int(self.module.get_parameter("infil_flow")))
        self.ui.infil_pollute_check.setChecked(int(self.module.get_parameter("infil_wq")))
        self.ui.infil_recycle_check.setChecked(int(self.module.get_parameter("infil_rec")))

        infil_locs = self.module.get_parameter("infil_permissions")
        self.ui.infil_pg_check.setChecked(int(infil_locs["PG"]))
        self.ui.infil_ref_check.setChecked(int(infil_locs["REF"]))
        self.ui.infil_for_check.setChecked(int(infil_locs["FOR"]))
        self.ui.infil_agr_check.setChecked(int(infil_locs["AGR"]))
        self.ui.infil_und_check.setChecked(int(infil_locs["UND"]))
        self.ui.infil_ns_check.setChecked(int(infil_locs["nstrip"]))
        self.ui.infil_garden_check.setChecked(int(infil_locs["garden"]))

        # System Sizing and Spec
        self.ui.infil_specmethod_combo.setCurrentIndex(
            self.sizingmethod.index(self.module.get_parameter("infil_method")))
        self.ui.infil_capture_check.setChecked(int(self.module.get_parameter("infil_univcapt")))
        self.ui.infil_captureflow_ratiospin.setValue(self.module.get_parameter("infil_flow_surfAratio"))
        if self.module.get_parameter("infil_flow_ratiodef") == "ALL":
            self.ui.infil_captureflow_area_radio.setChecked(1)
        else:
            self.ui.infil_captureflow_imp_radio.setChecked(1)
        self.ui.infil_capturewq_ratiospin.setValue(self.module.get_parameter("infil_wq_surfAratio"))
        if self.module.get_parameter("infil_wq_ratiodef") == "ALL":
            self.ui.infil_capturewq_area_radio.setChecked(1)
        else:
            self.ui.infil_capturewq_imp_radio.setChecked(1)
        if self.module.get_parameter("dcurvemethod") == "UBEATS":
            self.ui.infil_curveselect_default_radio.setChecked(1)
        else:
            self.ui.infil_curveselect_custom_radio.setChecked(1)
        self.ui.infil_curveselect_custom_box.setText(str(self.module.get_parameter("infil_dccustomfile")))

        # General System Characteristics
        infil_ed = [0, 100, 200, 300, 400]
        infil_fd = [200, 400, 600, 800]
        infil_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.ui.infil_spec_systemchar_ed.setCurrentIndex(infil_ed.index(self.module.get_parameter("infil_ed")))
        self.ui.infil_spec_systemchar_fd.setCurrentIndex(infil_fd.index(self.module.get_parameter("infil_fd")))
        self.ui.infil_spec_systemchar_rangemin_box.setText(str(self.module.get_parameter("infil_minsize")))
        self.ui.infil_spec_systemchar_rangemax_box.setText(str(self.module.get_parameter("infil_maxsize")))
        self.ui.infil_spec_systemchar_exfil_combo.setCurrentIndex(
            infil_exfil.index(self.module.get_parameter("infil_exfil")))

        # Life Cycle and Costing Information
        self.ui.infil_lcc_avglife_spin.setValue(self.module.get_parameter("infil_avglife"))
        self.ui.infil_lcc_renewal_spin.setValue(self.module.get_parameter("infil_renewcycle"))
        if self.module.get_parameter("infil_costmethod") == "DETAIL":
            self.ui.infil_lcc_costdetailed_radio.setChecked(1)
        else:
            self.ui.infil_lcc_costindicative_radio.setChecked(1)
        self.ui.infil_lcc_tac_box.setText(str(self.module.get_parameter("infil_tac")))
        self.ui.infil_lcc_tacind_box.setText(str(self.module.get_parameter("infil_tac")))
        self.ui.infil_lcc_tam_box.setText(str(self.module.get_parameter("infil_tam")))
        self.ui.infil_lcc_rc_box.setText(str(self.module.get_parameter("infil_new")))
        self.ui.infil_lcc_dc_box.setText(str(self.module.get_parameter("infil_decom")))
        self.ui.infil_lcc_tamind_spin.setValue(self.module.get_parameter("infil_tam_pct"))
        self.ui.infil_lcc_rcind_spin.setValue(self.module.get_parameter("infil_new_pct"))
        self.ui.infil_lcc_dcind_spin.setValue(self.module.get_parameter("infil_decom_pct"))
        # --- END OF INFILTRATION SYSTEMS ---

        # === SECTION: PONDS & SEDIMENTATION BASINS =======================================
        # Scales and Types of Application and permissible location
        self.ui.pb_lot_check.setChecked(int(self.module.get_parameter("pb_lot")))
        self.ui.pb_st_check.setChecked(int(self.module.get_parameter("pb_street")))
        self.ui.pb_reg_check.setChecked(int(self.module.get_parameter("pb_region")))
        self.ui.pb_flow_check.setChecked(int(self.module.get_parameter("pb_flow")))
        self.ui.pb_pollute_check.setChecked(int(self.module.get_parameter("pb_wq")))
        self.ui.pb_recycle_check.setChecked(int(self.module.get_parameter("pb_rec")))

        pb_locs = self.module.get_parameter("pb_permissions")
        self.ui.pb_pg_check.setChecked(int(pb_locs["PG"]))
        self.ui.pb_ref_check.setChecked(int(pb_locs["REF"]))
        self.ui.pb_for_check.setChecked(int(pb_locs["FOR"]))
        self.ui.pb_agr_check.setChecked(int(pb_locs["AGR"]))
        self.ui.pb_und_check.setChecked(int(pb_locs["UND"]))
        self.ui.pb_garden_check.setChecked(int(pb_locs["garden"]))

        # System Sizing and Spec
        self.ui.pb_specmethod_combo.setCurrentIndex(
            self.sizingmethod.index(self.module.get_parameter("pb_method")))
        self.ui.pb_capture_check.setChecked(int(self.module.get_parameter("pb_univcapt")))
        self.ui.pb_captureflow_ratiospin.setValue(self.module.get_parameter("pb_flow_surfAratio"))
        if self.module.get_parameter("pb_flow_ratiodef") == "ALL":
            self.ui.pb_captureflow_area_radio.setChecked(1)
        else:
            self.ui.pb_captureflow_imp_radio.setChecked(1)
        self.ui.pb_capturewq_ratiospin.setValue(self.module.get_parameter("pb_wq_surfAratio"))
        if self.module.get_parameter("pb_wq_ratiodef") == "ALL":
            self.ui.pb_capturewq_area_radio.setChecked(1)
        else:
            self.ui.pb_capturewq_imp_radio.setChecked(1)
        if self.module.get_parameter("dcurvemethod") == "UBEATS":
            self.ui.pb_curveselect_default_radio.setChecked(1)
        else:
            self.ui.pb_curveselect_custom_radio.setChecked(1)
        self.ui.pb_curveselect_custom_box.setText(str(self.module.get_parameter("pb_dccustomfile")))

        # General System Characteristics
        pb_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.ui.pb_spec_systemchar_combo.setCurrentIndex(int(self.module.get_parameter("pb_spec")))
        self.ui.pb_spec_systemchar_rangemin_box.setText(str(self.module.get_parameter("pb_minsize")))
        self.ui.pb_spec_systemchar_rangemax_box.setText(str(self.module.get_parameter("pb_maxsize")))
        self.ui.pb_spec_systemchar_exfil_combo.setCurrentIndex(
            pb_exfil.index(self.module.get_parameter("pb_exfil")))

        # Life Cycle and Costing Information
        self.ui.pb_lcc_avglife_spin.setValue(self.module.get_parameter("pb_avglife"))
        self.ui.pb_lcc_renewal_spin.setValue(self.module.get_parameter("pb_renewcycle"))
        if self.module.get_parameter("pb_costmethod") == "DETAIL":
            self.ui.pb_lcc_costdetailed_radio.setChecked(1)
        else:
            self.ui.pb_lcc_costindicative_radio.setChecked(1)
        self.ui.pb_lcc_tac_box.setText(str(self.module.get_parameter("pb_tac")))
        self.ui.pb_lcc_tacind_box.setText(str(self.module.get_parameter("pb_tac")))
        self.ui.pb_lcc_tam_box.setText(str(self.module.get_parameter("pb_tam")))
        self.ui.pb_lcc_rc_box.setText(str(self.module.get_parameter("pb_new")))
        self.ui.pb_lcc_dc_box.setText(str(self.module.get_parameter("pb_decom")))
        self.ui.pb_lcc_tamind_spin.setValue(self.module.get_parameter("pb_tam_pct"))
        self.ui.pb_lcc_rcind_spin.setValue(self.module.get_parameter("pb_new_pct"))
        self.ui.pb_lcc_dcind_spin.setValue(self.module.get_parameter("pb_decom_pct"))
        # --- END OF PONDS & SEDIMENTATION BASINS ---

        # === SECTION: POROUS/PERVIOUS PAVEMENTS =======================================
        # --- END OF POROUS PAVEMENTS ---

        # === RAINWATER/STORMWATER TANKS =======================================
        # Scales and Types of Application and permissible location
        self.ui.tank_lot_check.setChecked(int(self.module.get_parameter("tank_lot")))
        self.ui.tank_st_check.setChecked(int(self.module.get_parameter("tank_street")))
        self.ui.tank_reg_check.setChecked(int(self.module.get_parameter("tank_region")))
        self.ui.tank_flow_check.setChecked(int(self.module.get_parameter("tank_flow")))
        self.ui.tank_pollute_check.setChecked(int(self.module.get_parameter("tank_wq")))
        self.ui.tank_recycle_check.setChecked(int(self.module.get_parameter("tank_rec")))

        tank_locs = self.module.get_parameter("tank_permissions")
        self.ui.tank_pg_check.setChecked(int(tank_locs["PG"]))
        self.ui.tank_ref_check.setChecked(int(tank_locs["REF"]))
        self.ui.tank_for_check.setChecked(int(tank_locs["FOR"]))
        self.ui.tank_agr_check.setChecked(int(tank_locs["AGR"]))
        self.ui.tank_und_check.setChecked(int(tank_locs["UND"]))
        self.ui.tank_garden_check.setChecked(int(tank_locs["garden"]))

        # System Sizing and Spec
        self.ui.tank_specmethod_combo.setCurrentIndex(
            self.sizingmethod.index(self.module.get_parameter("tank_method")))
        self.ui.tank_capture_check.setChecked(int(self.module.get_parameter("tank_univcapt")))
        self.ui.tank_captureflow_ratiospin.setValue(self.module.get_parameter("tank_flow_surfAratio"))
        if self.module.get_parameter("tank_flow_ratiodef") == "ALL":
            self.ui.tank_captureflow_area_radio.setChecked(1)
        else:
            self.ui.tank_captureflow_imp_radio.setChecked(1)
        self.ui.tank_capturewq_ratiospin.setValue(self.module.get_parameter("tank_wq_surfAratio"))
        if self.module.get_parameter("tank_wq_ratiodef") == "ALL":
            self.ui.tank_capturewq_area_radio.setChecked(1)
        else:
            self.ui.tank_capturewq_imp_radio.setChecked(1)
        if self.module.get_parameter("dcurvemethod") == "UBEATS":
            self.ui.tank_curveselect_default_radio.setChecked(1)
        else:
            self.ui.tank_curveselect_custom_radio.setChecked(1)
        self.ui.tank_curveselect_custom_box.setText(str(self.module.get_parameter("tank_dccustomfile")))

        # General System Characteristics
        self.ui.tank_spec_systemchar_maxdepth.setText(str(self.module.get_parameter("tank_maxdepth")))
        self.ui.tank_spec_systemchar_mindead.setText(str(self.module.get_parameter("tank_mindead")))

        # Life Cycle and Costing Information
        self.ui.tank_lcc_avglife_spin.setValue(self.module.get_parameter("tank_avglife"))
        self.ui.tank_lcc_renewal_spin.setValue(self.module.get_parameter("tank_renewcycle"))
        if self.module.get_parameter("tank_costmethod") == "DETAIL":
            self.ui.tank_lcc_costdetailed_radio.setChecked(1)
        else:
            self.ui.tank_lcc_costindicative_radio.setChecked(1)
        self.ui.tank_lcc_tac_box.setText(str(self.module.get_parameter("tank_tac")))
        self.ui.tank_lcc_tacind_box.setText(str(self.module.get_parameter("tank_tac")))
        self.ui.tank_lcc_tam_box.setText(str(self.module.get_parameter("tank_tam")))
        self.ui.tank_lcc_rc_box.setText(str(self.module.get_parameter("tank_new")))
        self.ui.tank_lcc_dc_box.setText(str(self.module.get_parameter("tank_decom")))
        self.ui.tank_lcc_tamind_spin.setValue(self.module.get_parameter("tank_tam_pct"))
        self.ui.tank_lcc_rcind_spin.setValue(self.module.get_parameter("tank_new_pct"))
        self.ui.tank_lcc_dcind_spin.setValue(self.module.get_parameter("tank_decom_pct"))
        # --- END OF RAINWATER/STORMWATER TANKS ---

        # === RETARDING BASINS / FLOODPLAINS ============================================
        # --- END OF RETARDING BASINS/FLOODPLAINS ---

        # === SWALES ====================================================================
        self.ui.sw_st_check.setChecked(int(self.module.get_parameter("sw_street")))
        self.ui.sw_reg_check.setChecked(int(self.module.get_parameter("sw_region")))
        self.ui.sw_flow_check.setChecked(int(self.module.get_parameter("sw_flow")))
        self.ui.sw_pollute_check.setChecked(int(self.module.get_parameter("sw_wq")))

        sw_locs = self.module.get_parameter("sw_permissions")
        self.ui.sw_pg_check.setChecked(int(sw_locs["PG"]))
        self.ui.sw_ref_check.setChecked(int(sw_locs["REF"]))
        self.ui.sw_for_check.setChecked(int(sw_locs["FOR"]))
        self.ui.sw_agr_check.setChecked(int(sw_locs["AGR"]))
        self.ui.sw_und_check.setChecked(int(sw_locs["UND"]))
        self.ui.sw_ns_check.setChecked(int(sw_locs["nstrip"]))

        # System Sizing and Spec
        self.ui.sw_specmethod_combo.setCurrentIndex(self.sizingmethod.index(self.module.get_parameter("sw_method")))
        self.ui.sw_capture_check.setChecked(int(self.module.get_parameter("sw_univcapt")))
        self.ui.sw_captureflow_ratiospin.setValue(self.module.get_parameter("sw_flow_surfAratio"))
        if self.module.get_parameter("sw_flow_ratiodef") == "ALL":
            self.ui.sw_captureflow_area_radio.setChecked(1)
        else:
            self.ui.sw_captureflow_imp_radio.setChecked(1)
        self.ui.sw_capturewq_ratiospin.setValue(self.module.get_parameter("sw_wq_surfAratio"))
        if self.module.get_parameter("sw_wq_ratiodef") == "ALL":
            self.ui.sw_capturewq_area_radio.setChecked(1)
        else:
            self.ui.sw_capturewq_imp_radio.setChecked(1)
        if self.module.get_parameter("dcurvemethod") == "UBEATS":
            self.ui.sw_curveselect_default_radio.setChecked(1)
        else:
            self.ui.sw_curveselect_custom_radio.setChecked(1)
        self.ui.sw_curveselect_custom_box.setText(str(self.module.get_parameter("sw_dccustomfile")))

        # General System Characteristics
        sw_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.ui.sw_spec_systemchar_combo.setCurrentIndex(int(self.module.get_parameter("sw_spec")))
        self.ui.sw_spec_systemchar_rangemin_box.setText(str(self.module.get_parameter("sw_minsize")))
        self.ui.sw_spec_systemchar_rangemax_box.setText(str(self.module.get_parameter("sw_maxsize")))
        self.ui.sw_spec_systemchar_maxlength_box.setText(str(self.module.get_parameter("sw_maxlength")))
        self.ui.sw_spec_systemchar_exfil_combo.setCurrentIndex(sw_exfil.index(self.module.get_parameter("sw_exfil")))

        # Life Cycle and Costing Information
        self.ui.sw_lcc_avglife_spin.setValue(self.module.get_parameter("sw_avglife"))
        self.ui.sw_lcc_renewal_spin.setValue(self.module.get_parameter("sw_renewcycle"))
        if self.module.get_parameter("sw_costmethod") == "DETAIL":
            self.ui.sw_lcc_costdetailed_radio.setChecked(1)
        else:
            self.ui.sw_lcc_costindicative_radio.setChecked(1)
        self.ui.sw_lcc_tac_box.setText(str(self.module.get_parameter("sw_tac")))
        self.ui.sw_lcc_tacind_box.setText(str(self.module.get_parameter("sw_tac")))
        self.ui.sw_lcc_tam_box.setText(str(self.module.get_parameter("sw_tam")))
        self.ui.sw_lcc_rc_box.setText(str(self.module.get_parameter("sw_new")))
        self.ui.sw_lcc_dc_box.setText(str(self.module.get_parameter("sw_decom")))
        self.ui.sw_lcc_tamind_spin.setValue(self.module.get_parameter("sw_tam_pct"))
        self.ui.sw_lcc_rcind_spin.setValue(self.module.get_parameter("sw_new_pct"))
        self.ui.sw_lcc_dcind_spin.setValue(self.module.get_parameter("sw_decom_pct"))
        # --- END OF SWALES ---
        return True

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        # === SECTION: MENU OF SYSTEMS ================================================
        self.module.set_parameter("bf", int(bool(self.ui.nbs_selector.item(4).checkState())))
        self.module.set_parameter("wet", int(bool(self.ui.nbs_selector.item(5).checkState())))
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
            self.module.set_parameter("bf_method", "CAPTURE")
        else:
            self.module.set_parameter("bf_method", "CURVE")

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
        self.module.set_parameter("bf_dccustomfile", str(self.ui.bf_curveselect_custom_box.text()))

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

        # === SECTION: CONSTRUCTED WETLANDS =======================================
        # Scales and Types of Application and permissible location
        self.module.set_parameter("wet_street", int(self.ui.wet_st_check.isChecked()))
        self.module.set_parameter("wet_region", int(self.ui.wet_reg_check.isChecked()))
        self.module.set_parameter("wet_flow", int(self.ui.wet_flow_check.isChecked()))
        self.module.set_parameter("wet_wq", int(self.ui.wet_pollute_check.isChecked()))
        self.module.set_parameter("wet_rec", int(self.ui.wet_recycle_check.isChecked()))

        wet_locs = {
            "PG": int(self.ui.wet_pg_check.isChecked()),
            "REF": int(self.ui.wet_ref_check.isChecked()),
            "FOR": int(self.ui.wet_for_check.isChecked()),
            "AGR": int(self.ui.wet_agr_check.isChecked()),
            "UND": int(self.ui.wet_und_check.isChecked()),
        }
        self.module.set_parameter("wet_permissions", wet_locs)

        # System Sizing and Spec
        if self.ui.wet_specmethod_combo.currentIndex() == 0:
            self.module.set_parameter("wet_method", "CAPTURE")
        else:
            self.module.set_parameter("wet_method", "CURVE")

        self.module.set_parameter("wet_univcapt", int(self.ui.wet_capture_check.isChecked()))
        self.module.set_parameter("wet_flow_surfAratio", float(self.ui.wet_captureflow_ratiospin.value()))
        if self.ui.wet_captureflow_area_radio.isChecked():
            self.module.set_parameter("wet_flow_ratiodef", "ALL")
        else:
            self.module.set_parameter("wet_flow_ratiodef", "IMP")
        self.module.set_parameter("wet_wq_surfAratio", float(self.ui.wet_capturewq_ratiospin.value()))
        if self.ui.wet_capturewq_area_radio.isChecked():
            self.module.set_parameter("wet_wq_ratiodef", "ALL")
        else:
            self.module.set_parameter("wet_wq_ratiodef", "IMP")
        if self.ui.wet_curveselect_default_radio.isChecked():
            self.module.set_parameter("dcurvemethod", "UBEATS")
        else:
            self.module.set_parameter("dcurvemethod", "CUSTOM")
        self.module.set_parameter("wet_dccustomfile", str(self.ui.wet_curveselect_custom_box.text()))

        # General System Characteristics
        wet_exfil = [0, 0.18, 0.36, 1.8, 3.6]

        self.module.set_parameter("wet_spec", int(self.ui.wet_spec_systemchar_combo.currentIndex()))
        self.module.set_parameter("wet_minsize", float(self.ui.wet_spec_systemchar_rangemin_box.text()))
        self.module.set_parameter("wet_maxsize", float(self.ui.wet_spec_systemchar_rangemax_box.text()))
        self.module.set_parameter("wet_exfil", wet_exfil[self.ui.wet_spec_systemchar_exfil_combo.currentIndex()])

        # Life Cycle and Costing Information
        self.module.set_parameter("wet_avglife", float(self.ui.wet_lcc_avglife_spin.value()))
        self.module.set_parameter("wet_renewcycle", float(self.ui.wet_lcc_renewal_spin.value()))
        if self.ui.wet_lcc_costdetailed_radio.isChecked():
            self.module.set_parameter("wet_costmethod", "DETAIL")  # Set only the detailed parameters
            self.module.set_parameter("wet_tac", float(self.ui.wet_lcc_tac_box.text()))
            self.module.set_parameter("wet_tam", float(self.ui.wet_lcc_tam_box.text()))
            self.module.set_parameter("wet_new", float(self.ui.wet_lcc_rc_box.text()))
            self.module.set_parameter("wet_decom", float(self.ui.wet_lcc_dc_box.text()))
        else:
            self.module.set_parameter("wet_costmethod", "INDIC")  # Set only the indicative parameters
            self.module.set_parameter("wet_tac", float(self.ui.wet_lcc_tacind_box.text()))
            self.module.set_parameter("wet_tam_pct", float(self.ui.wet_lcc_tamind_spin.value()))
            self.module.set_parameter("wet_new_pct", float(self.ui.wet_lcc_rcind_spin.value()))
            self.module.set_parameter("wet_decom_pct", float(self.ui.wet_lcc_dcind_spin.value()))
        # --- END OF CONSTRUCTED WETLANDS ---

        # === SECTION: GREEN ROOF SYSTEMS =======================================
        # --- END OF GREEN ROOF SYSTEMS ---

        # === SECTION: GREEN WALLS/LIVING WALLS =======================================
        # --- END OF GREEN WALLS/LIVING WALLS ---

        # === SECTION: INFILTRATION SYSTEMS =======================================
        # Scales and Types of Application and permissible location
        self.module.set_parameter("infil_lot", int(self.ui.infil_lot_check.isChecked()))
        self.module.set_parameter("infil_street", int(self.ui.infil_st_check.isChecked()))
        self.module.set_parameter("infil_region", int(self.ui.infil_reg_check.isChecked()))
        self.module.set_parameter("infil_flow", int(self.ui.infil_flow_check.isChecked()))
        self.module.set_parameter("infil_wq", int(self.ui.infil_pollute_check.isChecked()))
        self.module.set_parameter("infil_rec", int(self.ui.infil_recycle_check.isChecked()))

        infil_locs = {
            "PG": int(self.ui.infil_pg_check.isChecked()),
            "REF": int(self.ui.infil_ref_check.isChecked()),
            "FOR": int(self.ui.infil_for_check.isChecked()),
            "AGR": int(self.ui.infil_agr_check.isChecked()),
            "UND": int(self.ui.infil_und_check.isChecked()),
            "nstrip": int(self.ui.infil_ns_check.isChecked()),
            "garden": int(self.ui.infil_garden_check.isChecked())
        }
        self.module.set_parameter("infil_permissions", infil_locs)

        # System Sizing and Spec
        if self.ui.infil_specmethod_combo.currentIndex() == 0:
            self.module.set_parameter("infil_method", "CAPTURE")
        else:
            self.module.set_parameter("infil_method", "CURVE")

        self.module.set_parameter("infil_univcapt", int(self.ui.infil_capture_check.isChecked()))
        self.module.set_parameter("infil_flow_surfAratio", float(self.ui.infil_captureflow_ratiospin.value()))
        if self.ui.infil_captureflow_area_radio.isChecked():
            self.module.set_parameter("infil_flow_ratiodef", "ALL")
        else:
            self.module.set_parameter("infil_flow_ratiodef", "IMP")
        self.module.set_parameter("infil_wq_surfAratio", float(self.ui.infil_capturewq_ratiospin.value()))
        if self.ui.infil_capturewq_area_radio.isChecked():
            self.module.set_parameter("infil_wq_ratiodef", "ALL")
        else:
            self.module.set_parameter("infil_wq_ratiodef", "IMP")
        if self.ui.infil_curveselect_default_radio.isChecked():
            self.module.set_parameter("dcurvemethod", "UBEATS")
        else:
            self.module.set_parameter("dcurvemethod", "CUSTOM")
        self.module.set_parameter("infil_dccustomfile", str(self.ui.infil_curveselect_custom_box.text()))

        # General System Characteristics
        infil_ed = [0, 100, 200, 300, 400]
        infil_fd = [200, 400, 600, 800]
        infil_exfil = [0, 0.18, 0.36, 1.8, 3.6]

        self.module.set_parameter("infil_ed", infil_ed[self.ui.infil_spec_systemchar_ed.currentIndex()])
        self.module.set_parameter("infil_fd", infil_fd[self.ui.infil_spec_systemchar_fd.currentIndex()])
        self.module.set_parameter("infil_minsize", float(self.ui.infil_spec_systemchar_rangemin_box.text()))
        self.module.set_parameter("infil_maxsize", float(self.ui.infil_spec_systemchar_rangemax_box.text()))
        self.module.set_parameter("infil_exfil",
                                  infil_exfil[self.ui.infil_spec_systemchar_exfil_combo.currentIndex()])

        # Life Cycle and Costing Information
        self.module.set_parameter("infil_avglife", float(self.ui.infil_lcc_avglife_spin.value()))
        self.module.set_parameter("infil_renewcycle", float(self.ui.infil_lcc_renewal_spin.value()))
        if self.ui.infil_lcc_costdetailed_radio.isChecked():
            self.module.set_parameter("infil_costmethod", "DETAIL")  # Set only the detailed parameters
            self.module.set_parameter("infil_tac", float(self.ui.infil_lcc_tac_box.text()))
            self.module.set_parameter("infil_tam", float(self.ui.infil_lcc_tam_box.text()))
            self.module.set_parameter("infil_new", float(self.ui.infil_lcc_rc_box.text()))
            self.module.set_parameter("infil_decom", float(self.ui.infil_lcc_dc_box.text()))
        else:
            self.module.set_parameter("infil_costmethod", "INDIC")  # Set only the indicative parameters
            self.module.set_parameter("infil_tac", float(self.ui.infil_lcc_tacind_box.text()))
            self.module.set_parameter("infil_tam_pct", float(self.ui.infil_lcc_tamind_spin.value()))
            self.module.set_parameter("infil_new_pct", float(self.ui.infil_lcc_rcind_spin.value()))
            self.module.set_parameter("infil_decom_pct", float(self.ui.infil_lcc_dcind_spin.value()))
        # --- END OF INFILTRATION SYSTEMS ---

        # === SECTION: PONDS & SEDIMENTATION BASINS =======================================
        # Scales and Types of Application and permissible location
        self.module.set_parameter("pb_lot", int(self.ui.pb_lot_check.isChecked()))
        self.module.set_parameter("pb_street", int(self.ui.pb_st_check.isChecked()))
        self.module.set_parameter("pb_region", int(self.ui.pb_reg_check.isChecked()))
        self.module.set_parameter("pb_flow", int(self.ui.pb_flow_check.isChecked()))
        self.module.set_parameter("pb_wq", int(self.ui.pb_pollute_check.isChecked()))
        self.module.set_parameter("pb_rec", int(self.ui.pb_recycle_check.isChecked()))

        pb_locs = {
            "PG": int(self.ui.pb_pg_check.isChecked()),
            "REF": int(self.ui.pb_ref_check.isChecked()),
            "FOR": int(self.ui.pb_for_check.isChecked()),
            "AGR": int(self.ui.pb_agr_check.isChecked()),
            "UND": int(self.ui.pb_und_check.isChecked()),
            "garden": int(self.ui.pb_garden_check.isChecked())
        }
        self.module.set_parameter("pb_permissions", pb_locs)

        # System Sizing and Spec
        if self.ui.pb_specmethod_combo.currentIndex() == 0:
            self.module.set_parameter("pb_method", "CAPTURE")
        else:
            self.module.set_parameter("pb_method", "CURVE")

        self.module.set_parameter("pb_univcapt", int(self.ui.pb_capture_check.isChecked()))
        self.module.set_parameter("pb_flow_surfAratio", float(self.ui.pb_captureflow_ratiospin.value()))
        if self.ui.pb_captureflow_area_radio.isChecked():
            self.module.set_parameter("pb_flow_ratiodef", "ALL")
        else:
            self.module.set_parameter("pb_flow_ratiodef", "IMP")
        self.module.set_parameter("pb_wq_surfAratio", float(self.ui.pb_capturewq_ratiospin.value()))
        if self.ui.pb_capturewq_area_radio.isChecked():
            self.module.set_parameter("pb_wq_ratiodef", "ALL")
        else:
            self.module.set_parameter("pb_wq_ratiodef", "IMP")
        if self.ui.pb_curveselect_default_radio.isChecked():
            self.module.set_parameter("dcurvemethod", "UBEATS")
        else:
            self.module.set_parameter("dcurvemethod", "CUSTOM")
        self.module.set_parameter("pb_dccustomfile", str(self.ui.pb_curveselect_custom_box.text()))

        # General System Characteristics
        pb_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.module.set_parameter("pb_spec", int(self.ui.pb_spec_systemchar_combo.currentIndex()))
        self.module.set_parameter("pb_minsize", float(self.ui.pb_spec_systemchar_rangemin_box.text()))
        self.module.set_parameter("pb_maxsize", float(self.ui.pb_spec_systemchar_rangemax_box.text()))
        self.module.set_parameter("pb_exfil", pb_exfil[self.ui.pb_spec_systemchar_exfil_combo.currentIndex()])

        # Life Cycle and Costing Information
        self.module.set_parameter("pb_avglife", float(self.ui.pb_lcc_avglife_spin.value()))
        self.module.set_parameter("pb_renewcycle", float(self.ui.pb_lcc_renewal_spin.value()))
        if self.ui.pb_lcc_costdetailed_radio.isChecked():
            self.module.set_parameter("pb_costmethod", "DETAIL")  # Set only the detailed parameters
            self.module.set_parameter("pb_tac", float(self.ui.pb_lcc_tac_box.text()))
            self.module.set_parameter("pb_tam", float(self.ui.pb_lcc_tam_box.text()))
            self.module.set_parameter("pb_new", float(self.ui.pb_lcc_rc_box.text()))
            self.module.set_parameter("pb_decom", float(self.ui.pb_lcc_dc_box.text()))
        else:
            self.module.set_parameter("pb_costmethod", "INDIC")  # Set only the indicative parameters
            self.module.set_parameter("pb_tac", float(self.ui.pb_lcc_tacind_box.text()))
            self.module.set_parameter("pb_tam_pct", float(self.ui.pb_lcc_tamind_spin.value()))
            self.module.set_parameter("pb_new_pct", float(self.ui.pb_lcc_rcind_spin.value()))
            self.module.set_parameter("pb_decom_pct", float(self.ui.pb_lcc_dcind_spin.value()))
        # --- END OF PONDS & SEDIMENTATION BASINS ---

        # === SECTION: POROUS/PERVIOUS PAVEMENTS =======================================
        # --- END OF POROUS PAVEMENTS ---

        # === RAINWATER/STORMWATER TANKS =======================================
        # Scales and Types of Application and permissible location
        self.module.set_parameter("tank_lot", int(self.ui.tank_lot_check.isChecked()))
        self.module.set_parameter("tank_street", int(self.ui.tank_st_check.isChecked()))
        self.module.set_parameter("tank_region", int(self.ui.tank_reg_check.isChecked()))
        self.module.set_parameter("tank_flow", int(self.ui.tank_flow_check.isChecked()))
        self.module.set_parameter("tank_wq", int(self.ui.tank_pollute_check.isChecked()))
        self.module.set_parameter("tank_rec", int(self.ui.tank_recycle_check.isChecked()))

        tank_locs = {
            "PG": int(self.ui.tank_pg_check.isChecked()),
            "REF": int(self.ui.tank_ref_check.isChecked()),
            "FOR": int(self.ui.tank_for_check.isChecked()),
            "AGR": int(self.ui.tank_agr_check.isChecked()),
            "UND": int(self.ui.tank_und_check.isChecked()),
            "garden": int(self.ui.tank_garden_check.isChecked())
        }
        self.module.set_parameter("tank_permissions", tank_locs)

        # System Sizing and Spec
        if self.ui.tank_specmethod_combo.currentIndex() == 0:
            self.module.set_parameter("tank_method", "CAPTURE")
        else:
            self.module.set_parameter("tank_method", "CURVE")

        self.module.set_parameter("tank_univcapt", int(self.ui.tank_capture_check.isChecked()))
        self.module.set_parameter("tank_flow_surfAratio", float(self.ui.tank_captureflow_ratiospin.value()))
        if self.ui.tank_captureflow_area_radio.isChecked():
            self.module.set_parameter("tank_flow_ratiodef", "ALL")
        else:
            self.module.set_parameter("tank_flow_ratiodef", "IMP")
        self.module.set_parameter("tank_wq_surfAratio", float(self.ui.tank_capturewq_ratiospin.value()))
        if self.ui.tank_capturewq_area_radio.isChecked():
            self.module.set_parameter("tank_wq_ratiodef", "ALL")
        else:
            self.module.set_parameter("tank_wq_ratiodef", "IMP")
        if self.ui.tank_curveselect_default_radio.isChecked():
            self.module.set_parameter("dcurvemethod", "UBEATS")
        else:
            self.module.set_parameter("dcurvemethod", "CUSTOM")
        self.module.set_parameter("tank_dccustomfile", str(self.ui.tank_curveselect_custom_box.text()))

        # General System Characteristics
        self.module.set_parameter("tank_maxdepth", float(self.ui.tank_spec_systemchar_maxdepth.text()))
        self.module.set_parameter("tank_mindead", float(self.ui.tank_spec_systemchar_mindead.text()))

        # Life Cycle and Costing Information
        self.module.set_parameter("tank_avglife", float(self.ui.tank_lcc_avglife_spin.value()))
        self.module.set_parameter("tank_renewcycle", float(self.ui.tank_lcc_renewal_spin.value()))
        if self.ui.tank_lcc_costdetailed_radio.isChecked():
            self.module.set_parameter("tank_costmethod", "DETAIL")  # Set only the detailed parameters
            self.module.set_parameter("tank_tac", float(self.ui.tank_lcc_tac_box.text()))
            self.module.set_parameter("tank_tam", float(self.ui.tank_lcc_tam_box.text()))
            self.module.set_parameter("tank_new", float(self.ui.tank_lcc_rc_box.text()))
            self.module.set_parameter("tank_decom", float(self.ui.tank_lcc_dc_box.text()))
        else:
            self.module.set_parameter("tank_costmethod", "INDIC")  # Set only the indicative parameters
            self.module.set_parameter("tank_tac", float(self.ui.tank_lcc_tacind_box.text()))
            self.module.set_parameter("tank_tam_pct", float(self.ui.tank_lcc_tamind_spin.value()))
            self.module.set_parameter("tank_new_pct", float(self.ui.tank_lcc_rcind_spin.value()))
            self.module.set_parameter("tank_decom_pct", float(self.ui.tank_lcc_dcind_spin.value()))
        # --- END OF RAINWATER/STORMWATER TANKS ---

        # === RETARDING BASINS / FLOODPLAINS ============================================
        # --- END OF RETARDING BASINS/FLOODPLAINS ---

        # === SWALES ====================================================================
        # Scales and Types of Application and permissible location
        self.module.set_parameter("sw_street", int(self.ui.sw_st_check.isChecked()))
        self.module.set_parameter("sw_region", int(self.ui.sw_reg_check.isChecked()))
        self.module.set_parameter("sw_flow", int(self.ui.sw_flow_check.isChecked()))
        self.module.set_parameter("sw_wq", int(self.ui.sw_pollute_check.isChecked()))

        sw_locs = {
            "PG": int(self.ui.sw_pg_check.isChecked()),
            "REF": int(self.ui.sw_ref_check.isChecked()),
            "FOR": int(self.ui.sw_for_check.isChecked()),
            "AGR": int(self.ui.sw_agr_check.isChecked()),
            "UND": int(self.ui.sw_und_check.isChecked()),
            "nstrip": int(self.ui.sw_ns_check.isChecked()),
        }
        self.module.set_parameter("sw_permissions", sw_locs)

        # System Sizing and Spec
        if self.ui.sw_specmethod_combo.currentIndex() == 0:
            self.module.set_parameter("sw_method", "CAPTURE")
        else:
            self.module.set_parameter("sw_method", "CURVE")

        self.module.set_parameter("sw_univcapt", int(self.ui.sw_capture_check.isChecked()))
        self.module.set_parameter("sw_flow_surfAratio", float(self.ui.sw_captureflow_ratiospin.value()))
        if self.ui.sw_captureflow_area_radio.isChecked():
            self.module.set_parameter("sw_flow_ratiodef", "ALL")
        else:
            self.module.set_parameter("sw_flow_ratiodef", "IMP")
        self.module.set_parameter("sw_wq_surfAratio", float(self.ui.sw_capturewq_ratiospin.value()))
        if self.ui.sw_capturewq_area_radio.isChecked():
            self.module.set_parameter("sw_wq_ratiodef", "ALL")
        else:
            self.module.set_parameter("sw_wq_ratiodef", "IMP")
        if self.ui.sw_curveselect_default_radio.isChecked():
            self.module.set_parameter("dcurvemethod", "UBEATS")
        else:
            self.module.set_parameter("dcurvemethod", "CUSTOM")
        self.module.set_parameter("sw_dccustomfile", str(self.ui.sw_curveselect_custom_box.text()))

        # General System Characteristics
        sw_exfil = [0, 0.18, 0.36, 1.8, 3.6]
        self.module.set_parameter("sw_spec", int(self.ui.sw_spec_systemchar_combo.currentIndex()))
        self.module.set_parameter("sw_minsize", float(self.ui.sw_spec_systemchar_rangemin_box.text()))
        self.module.set_parameter("sw_maxsize", float(self.ui.sw_spec_systemchar_rangemax_box.text()))
        self.module.set_parameter("sw_maxlength", float(self.ui.sw_spec_systemchar_maxlength_box.text()))
        self.module.set_parameter("sw_exfil", sw_exfil[self.ui.sw_spec_systemchar_exfil_combo.currentIndex()])

        # Life Cycle and Costing Information
        self.module.set_parameter("sw_avglife", float(self.ui.sw_lcc_avglife_spin.value()))
        self.module.set_parameter("sw_renewcycle", float(self.ui.sw_lcc_renewal_spin.value()))
        if self.ui.sw_lcc_costdetailed_radio.isChecked():
            self.module.set_parameter("sw_costmethod", "DETAIL")  # Set only the detailed parameters
            self.module.set_parameter("sw_tac", float(self.ui.sw_lcc_tac_box.text()))
            self.module.set_parameter("sw_tam", float(self.ui.sw_lcc_tam_box.text()))
            self.module.set_parameter("sw_new", float(self.ui.sw_lcc_rc_box.text()))
            self.module.set_parameter("sw_decom", float(self.ui.sw_lcc_dc_box.text()))
        else:
            self.module.set_parameter("sw_costmethod", "INDIC")  # Set only the indicative parameters
            self.module.set_parameter("sw_tac", float(self.ui.sw_lcc_tacind_box.text()))
            self.module.set_parameter("sw_tam_pct", float(self.ui.sw_lcc_tamind_spin.value()))
            self.module.set_parameter("sw_new_pct", float(self.ui.sw_lcc_rcind_spin.value()))
            self.module.set_parameter("sw_decom_pct", float(self.ui.sw_lcc_dcind_spin.value()))
        # --- END OF SWALES ---
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
