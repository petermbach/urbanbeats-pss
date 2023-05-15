r"""
@file   mod_waterdemand_guic.py
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
import model.mods_master.mod_waterdemand as mod_waterdemand

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_waterdemand_gui import Ui_WaterDemandGui
from .subguis.md_subgui_dp import Ui_CustomPatternDialog


# --- MAIN GUI FUNCTION ---
class WaterDemandLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Water Management"
    catorder = 1
    longname = "Water Demand Mapping"
    icon = ":/icons/hand-washing.png"

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
        self.ui = Ui_WaterDemandGui()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None

        # --- PROGRESSBAR  OBSERVER ---
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
        # Boundary combo box
        self.ui.assetcol_combo.clear()
        self.ui.assetcol_combo.addItem("(select simulation grid)")
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

        # --- SIGNALS AND SLOTS ---
        self.ui.resdemand_analysis_combo.currentIndexChanged.connect(self.update_demand_method_stack)
        self.ui.res_standard_button.clicked.connect(self.show_res_standard_details)
        self.ui.res_standard_combo.currentIndexChanged.connect(self.populate_ratings_combo)
        self.ui.res_enduse_summarybutton.clicked.connect(self.show_res_enduse_summary)
        self.ui.kitchen_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.shower_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.toilet_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.laundry_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.dish_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.res_irrigate_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.indoor_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.outdoor_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.nres_irrigate_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.com_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.ind_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.pos_dp.currentIndexChanged.connect(self.enable_disable_guis)
        self.ui.res_direct_ww_slider.valueChanged.connect(self.slider_res_value_update)
        self.ui.civic_presetsbutton.clicked.connect(self.view_civic_wateruse_presets)
        self.ui.nres_ww_com_slider.valueChanged.connect(self.slider_nres_com_update)
        self.ui.nres_ww_ind_slider.valueChanged.connect(self.slider_nres_ind_update)
        self.ui.losses_check.clicked.connect(self.enable_disable_guis)
        self.ui.weekly_reducenres_check.clicked.connect(self.enable_disable_guis)
        self.ui.weekly_increaseres_check.clicked.connect(self.enable_disable_guis)
        self.ui.seasonal_check.clicked.connect(self.enable_disable_guis)
        self.ui.seasonal_globalavg_check.clicked.connect(self.enable_disable_guis)
        self.ui.seasonal_noirrigaterain_check.clicked.connect(self.enable_disable_guis)

        self.ui.kitchen_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_kitchen"))  # Custom patterns
        self.ui.shower_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_shower"))
        self.ui.toilet_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_toilet"))
        self.ui.laundry_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_laundry"))
        self.ui.dish_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_dishwasher"))
        self.ui.res_irrigate_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_outdoor"))
        self.ui.outdoor_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_outdoor"))
        self.ui.indoor_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_dailyindoor_cp"))
        self.ui.com_dpcustom.clicked.connect(lambda: self.call_pattern_gui("com"))
        self.ui.ind_dpcustom.clicked.connect(lambda: self.call_pattern_gui("ind"))
        self.ui.nres_irrigate_dpcustom.clicked.connect(lambda: self.call_pattern_gui("nonres_landscape"))
        self.ui.pos_dpcustom.clicked.connect(lambda: self.call_pattern_gui("pos_irrigation"))

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.enable_disable_guis()
        self.setup_gui_with_parameters()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def enable_disable_guis(self):
        """Enables and disables items in the GUI based on conditions."""
        self.ui.losses_volspin.setEnabled(self.ui.losses_check.isChecked())
        self.ui.weekly_reducenres_spin.setEnabled(self.ui.weekly_reducenres_check.isChecked())
        self.ui.weekly_increaseres_spin.setEnabled(self.ui.weekly_increaseres_check.isChecked())
        self.ui.seasonal_globalavg_box.setEnabled(not self.ui.seasonal_globalavg_check.isChecked())
        self.ui.seasonal_irrigateresume_spin.setEnabled(self.ui.seasonal_noirrigaterain_check.isChecked())
        self.ui.seasonal_widget.setEnabled(self.ui.seasonal_check.isChecked())

        # Custom buttons
        self.ui.kitchen_dpcustom.setEnabled(self.ui.kitchen_dp.currentIndex() == self.ui.kitchen_dp.count() - 1)
        self.ui.shower_dpcustom.setEnabled(self.ui.shower_dp.currentIndex() == self.ui.shower_dp.count() - 1)
        self.ui.toilet_dpcustom.setEnabled(self.ui.toilet_dp.currentIndex() == self.ui.toilet_dp.count() - 1)
        self.ui.laundry_dpcustom.setEnabled(self.ui.laundry_dp.currentIndex() == self.ui.laundry_dp.count() - 1)
        self.ui.dish_dpcustom.setEnabled(self.ui.dish_dp.currentIndex() == self.ui.dish_dp.count() - 1)
        self.ui.res_irrigate_dpcustom.setEnabled(self.ui.res_irrigate_dp.currentIndex() ==
                                                 self.ui.res_irrigate_dp.count() - 1)
        self.ui.indoor_dpcustom.setEnabled(self.ui.indoor_dp.currentIndex() == self.ui.indoor_dp.count() - 1)
        self.ui.outdoor_dpcustom.setEnabled(self.ui.outdoor_dp.currentIndex() == self.ui.outdoor_dp.count() - 1)
        self.ui.nres_irrigate_dpcustom.setEnabled(self.ui.nres_irrigate_dp.currentIndex() ==
                                                  self.ui.nres_irrigate_dp.count() - 1)
        self.ui.com_dpcustom.setEnabled(self.ui.com_dp.currentIndex() == self.ui.com_dp.count() - 1)
        self.ui.ind_dpcustom.setEnabled(self.ui.ind_dp.currentIndex() == self.ui.ind_dp.count() - 1)
        self.ui.pos_dpcustom.setEnabled(self.ui.pos_dp.currentIndex() == self.ui.pos_dp.count() - 1)

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # RESIDENTIAL Water Use
        if self.module.get_parameter("residential_method") == "EUA":
            self.ui.resdemand_analysis_combo.setCurrentIndex(0)
            self.ui.res_analysis_stack.setCurrentIndex(0)
        else:
            self.ui.resdemand_analysis_combo.setCurrentIndex(1)
            self.ui.res_analysis_stack.setCurrentIndex(1)

        self.ui.res_standard_combo.setCurrentIndex(mod_waterdemand.RESSTANDARDS.index(
            self.module.get_parameter("res_standard")))
        self.populate_ratings_combo()
        self.ui.res_standard_eff.setCurrentIndex(int(self.module.get_parameter("res_baseefficiency")))

        self.ui.kitchen_freq.setValue(float(self.module.get_parameter("res_kitchen_fq")))
        self.ui.kitchen_dur.setValue(int(self.module.get_parameter("res_kitchen_dur")))
        self.ui.kitchen_hot.setValue(int(self.module.get_parameter("res_kitchen_hot")))
        self.ui.kitchen_vary.setValue(int(self.module.get_parameter("res_kitchen_var")))
        self.ui.kitchen_ffp.setCurrentIndex(mod_waterdemand.FFP.index(self.module.get_parameter("res_kitchen_ffp")))
        self.ui.kitchen_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_kitchen_pat")))
        if self.module.get_parameter("res_kitchen_wwq") == "B":
            self.ui.kitchen_blackradio.setChecked(1)
        else:
            self.ui.kitchen_greyradio.setChecked(1)

        self.ui.shower_freq.setValue(float(self.module.get_parameter("res_shower_fq")))
        self.ui.shower_dur.setValue(int(self.module.get_parameter("res_shower_dur")))
        self.ui.shower_hot.setValue(int(self.module.get_parameter("res_shower_hot")))
        self.ui.shower_vary.setValue(int(self.module.get_parameter("res_shower_var")))
        self.ui.shower_ffp.setCurrentIndex(mod_waterdemand.FFP.index(self.module.get_parameter("res_shower_ffp")))
        self.ui.shower_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_shower_pat")))
        if self.module.get_parameter("res_shower_wwq") == "B":
            self.ui.shower_blackradio.setChecked(1)
        else:
            self.ui.shower_greyradio.setChecked(1)

        self.ui.toilet_freq.setValue(float(self.module.get_parameter("res_toilet_fq")))
        self.ui.toilet_hot.setValue(int(self.module.get_parameter("res_toilet_hot")))
        self.ui.toilet_vary.setValue(int(self.module.get_parameter("res_toilet_var")))
        self.ui.toilet_ffp.setCurrentIndex(mod_waterdemand.FFP.index(self.module.get_parameter("res_toilet_ffp")))
        self.ui.toilet_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_toilet_pat")))
        if self.module.get_parameter("res_toilet_wwq") == "B":
            self.ui.toilet_blackradio.setChecked(1)
        else:
            self.ui.toilet_greyradio.setChecked(1)

        self.ui.laundry_freq.setValue(float(self.module.get_parameter("res_laundry_fq")))
        self.ui.laundry_hot.setValue(int(self.module.get_parameter("res_laundry_hot")))
        self.ui.laundry_vary.setValue(int(self.module.get_parameter("res_laundry_var")))
        self.ui.laundry_ffp.setCurrentIndex(mod_waterdemand.FFP.index(self.module.get_parameter("res_laundry_ffp")))
        self.ui.laundry_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_laundry_pat")))
        if self.module.get_parameter("res_laundry_wwq") == "B":
            self.ui.laundry_blackradio.setChecked(1)
        else:
            self.ui.laundry_greyradio.setChecked(1)

        self.ui.dish_freq.setValue(float(self.module.get_parameter("res_dishwasher_fq")))
        self.ui.dish_hot.setValue(int(self.module.get_parameter("res_dishwasher_hot")))
        self.ui.dish_vary.setValue(int(self.module.get_parameter("res_dishwasher_var")))
        self.ui.dish_ffp.setCurrentIndex(mod_waterdemand.FFP.index(self.module.get_parameter("res_dishwasher_ffp")))
        self.ui.dish_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_dishwasher_pat")))
        if self.module.get_parameter("res_dishwasher_wwq") == "B":
            self.ui.dish_blackradio.setChecked(1)
        else:
            self.ui.dish_greyradio.setChecked(1)

        self.ui.res_irrigate_vol.setValue(float(self.module.get_parameter("res_outdoor_vol")))
        self.ui.res_irrigate_ffp.setCurrentIndex(
            mod_waterdemand.FFP.index(self.module.get_parameter("res_outdoor_ffp")))
        self.ui.res_irrigate_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_outdoor_pat")))

        self.ui.res_direct_vol.setValue(float(self.module.get_parameter("res_dailyindoor_vol")))
        self.ui.res_direct_np.setValue(int(self.module.get_parameter("res_dailyindoor_np")))
        self.ui.res_direct_hot.setValue(int(self.module.get_parameter("res_dailyindoor_hot")))
        self.ui.res_direct_vary.setValue(int(self.module.get_parameter("res_dailyindoor_var")))
        self.ui.indoor_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_dailyindoor_pat")))
        self.ui.res_direct_ww_slider.setValue(self.module.get_parameter("res_dailyindoor_bgprop"))

        self.ui.res_direct_irrigate.setValue(float(self.module.get_parameter("res_outdoor_vol")))
        self.ui.res_direct_irrigate_ffp.setCurrentIndex(mod_waterdemand.FFP.index(
            self.module.get_parameter("res_outdoor_ffp")))
        self.ui.outdoor_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("res_outdoor_pat")))

        # NON-RESIDENTIAL Water Use
        self.ui.com_demandbox.setText(str(self.module.get_parameter("com_demand")))
        self.ui.com_demandspin.setValue(int(self.module.get_parameter("com_var")))
        if self.module.get_parameter("com_units") == "LSQMD":
            self.ui.com_demandunits.setCurrentIndex(0)
        elif self.module.get_parameter("com_units") == "LPAXD":
            self.ui.com_demandunits.setCurrentIndex(1)
        else:
            self.ui.com_demandunits.setCurrentIndex(2)

        self.ui.com_hotbox.setValue(int(self.module.get_parameter("com_hot")))
        self.ui.com_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("com_pat")))

        self.ui.office_demandbox.setText(str(self.module.get_parameter("office_demand")))
        self.ui.office_demandspin.setValue(int(self.module.get_parameter("office_var")))
        if self.module.get_parameter("office_units") == "LSQMD":
            self.ui.office_demandunits.setCurrentIndex(0)
        elif self.module.get_parameter("office_units") == "LPAXD":
            self.ui.office_demandunits.setCurrentIndex(1)
        else:
            self.ui.office_demandunits.setCurrentIndex(2)

        self.ui.office_hotbox.setValue(int(self.module.get_parameter("office_hot")))

        self.ui.li_demandbox.setText(str(self.module.get_parameter("li_demand")))
        self.ui.li_demandspin.setValue(int(self.module.get_parameter("li_var")))
        if self.module.get_parameter("li_units") == "LSQMD":
            self.ui.li_demandunits.setCurrentIndex(0)
        elif self.module.get_parameter("li_units") == "LPAXD":
            self.ui.li_demandunits.setCurrentIndex(1)
        else:
            self.ui.li_demandunits.setCurrentIndex(2)

        self.ui.li_hotbox.setValue(int(self.module.get_parameter("li_hot")))
        self.ui.ind_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("ind_pat")))

        self.ui.hi_demandbox.setText(str(self.module.get_parameter("hi_demand")))
        self.ui.hi_demandspin.setValue(int(self.module.get_parameter("hi_var")))
        if self.module.get_parameter("hi_units") == "LSQMD":
            self.ui.hi_demandunits.setCurrentIndex(0)
        elif self.module.get_parameter("hi_units") == "LPAXD":
            self.ui.hi_demandunits.setCurrentIndex(1)
        else:
            self.ui.hi_demandunits.setCurrentIndex(2)

        self.ui.hi_hotbox.setValue(int(self.module.get_parameter("hi_hot")))

        self.ui.nres_irrigate_vol.setValue(float(self.module.get_parameter("nonres_landscape_vol")))
        self.ui.nres_irrigate_ffp.setCurrentIndex(mod_waterdemand.FFP.index(
            self.module.get_parameter("nonres_landscape_ffp")))
        self.ui.nres_irrigate_dp.setCurrentIndex(mod_waterdemand.DPS.index(
            self.module.get_parameter("nonres_landscape_pat")))

        self.ui.nres_ww_com_slider.setValue(int(self.module.get_parameter("com_ww_bgprop")))
        self.ui.nres_ww_ind_slider.setValue(int(self.module.get_parameter("ind_ww_bgprop")))

        # PUBLIC OPEN SPACE AND DISTRICTS Water Use
        self.ui.pos_annual_vol.setValue(float(self.module.get_parameter("pos_irrigation_vol")))
        self.ui.pos_ffp.setCurrentIndex(mod_waterdemand.FFP.index(self.module.get_parameter("pos_irrigation_ffp")))
        self.ui.pos_spaces_pg.setChecked(int(self.module.get_parameter("irrigate_parks")))
        self.ui.pos_spaces_na.setChecked(int(self.module.get_parameter("irrigate_landmarks")))
        self.ui.pos_spaces_ref.setChecked(int(self.module.get_parameter("irrigate_reserves")))
        self.ui.pos_dp.setCurrentIndex(mod_waterdemand.DPS.index(self.module.get_parameter("pos_irrigation_pat")))

        self.ui.losses_check.setChecked(int(self.module.get_parameter("estimate_waterloss")))
        self.ui.losses_volspin.setValue(float(self.module.get_parameter("waterloss_volprop")))
        if self.module.get_parameter("loss_pat") == "CDP":
            self.ui.loss_dp.setCurrentIndex(0)
        else:
            self.ui.loss_dp.setCurrentIndex(1)

        # TEMPORAL DYNAMICS
        self.ui.weekly_reducenres_check.setChecked(int(self.module.get_parameter("weekend_nonres_reduce")))
        self.ui.weekly_increaseres_check.setChecked(int(self.module.get_parameter("weekend_res_increase")))
        self.ui.weekly_reducenres_spin.setValue(float(self.module.get_parameter("weekend_nonres_factor")))
        self.ui.weekly_increaseres_spin.setValue(float(self.module.get_parameter("weekend_res_factor")))

        self.ui.seasonal_check.setChecked(int(self.module.get_parameter("seasonal_analysis")))
        # self.ui.seasonal_scaledata_combo.setCurrentIndex(???)
        self.ui.seasonal_numyears_spin.setValue(int(self.module.get_parameter("scaling_years")))
        self.ui.seasonal_globalavg_box.setText(str(self.module.get_parameter("scaling_average")))
        self.ui.seasonal_globalavg_check.setChecked(int(self.module.get_parameter("scaling_average_fromdata")))
        self.ui.seasonal_irrigateresume_spin.setValue(int(self.module.get_parameter("irrigation_resume_time")))
        self.ui.seasonal_noirrigaterain_check.setChecked(int(self.module.get_parameter("no_irrigate_during_rain")))

        self.enable_disable_guis()
        self.slider_nres_com_update()
        self.slider_nres_ind_update()
        self.slider_res_value_update()

    def call_pattern_gui(self, enduse):
        """Call the sub-gui for setting a custom End Use Diurnal Patterns."""
        custompatternguic = CustomPatternLaunch(self.module, enduse)
        custompatternguic.exec_()

    def show_res_standard_details(self):
        """"""
        pass  # [TO DO]

    def show_res_enduse_summary(self):
        """Calculates an average per capita water use and displays it in the box beneath the end use analysis
        parameters."""
        standard_dict = self.module.retrieve_standards(str(
            mod_waterdemand.RESSTANDARDS[self.ui.res_standard_combo.currentIndex()]))
        if standard_dict["Name"] == "Others...":
            self.ui.res_enduse_summarybox.setText("Total: (undefined) L/person/day)")
            return True

        # Get the current asset selected and calculate. If the asset has no urban form info, good to remind user
        # - if no mod_urbanformgen --> Display message and (undefined)
        # - else: get self.meta(Occupancy) and calculate
        # [TO DO] if used in a scenario, grab the occupancy from the module info

        if self.ui.assetcol_combo.currentIndex() != 0:
            self.assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
            self.meta = self.assetcol.get_asset_with_name("meta")
            if self.meta is not None:
                avg_occupancy = self.meta.get_attribute("AvgOccup")
        else:
            self.ui.res_enduse_summarybox.setText("Total: (undefined) L/person/day)")
            return True

        avg_use = self.ui.kitchen_freq.value() * self.ui.kitchen_dur.value() * \
                  standard_dict["Kitchen"][int(self.ui.res_standard_eff.currentIndex())] + \
                  self.ui.shower_freq.value() * self.ui.shower_dur.value() * \
                  standard_dict["Shower"][int(self.ui.res_standard_eff.currentIndex())] + \
                  self.ui.toilet_freq.value() * \
                  standard_dict["Toilet"][int(self.ui.res_standard_eff.currentIndex())] + \
                  self.ui.laundry_freq.value() * \
                  standard_dict["Laundry"][int(self.ui.res_standard_eff.currentIndex())] / float(avg_occupancy) + \
                  self.ui.dish_freq.value() * \
                  standard_dict["Dishwasher"][int(self.ui.res_standard_eff.currentIndex())] / float(avg_occupancy)

        self.ui.res_enduse_summarybox.setText("Total: " + str(round(avg_use, 1)) + " L/person/day (Occupancy: " +
                                              str(avg_occupancy) + ")")  # OMG it actually worked...
        return True

    def view_civic_wateruse_presets(self):
        """"""
        pass  # [TO DO]

    def slider_res_value_update(self):
        """Updates the residential blackwater/greywater slider value boxes to reflect the current slider's value."""
        self.ui.res_direct_wwboxgrey.setText(str(int((self.ui.res_direct_ww_slider.value() * -1 + 100) / 2)) + "%")
        self.ui.res_direct_wwboxblack.setText(str(int((self.ui.res_direct_ww_slider.value() + 100) / 2)) + "%")
        return True

    def slider_nres_com_update(self):
        """Updates the non-residential slider for commercial wastewater volumes"""
        self.ui.nres_ww_com_greybox.setText(str(int((self.ui.nres_ww_com_slider.value() * -1 + 100) / 2)) + "%")
        self.ui.nres_ww_com_blackbox.setText(str(int((self.ui.nres_ww_com_slider.value() + 100) / 2)) + "%")
        return True

    def slider_nres_ind_update(self):
        """Updates the non-residential slider for industrial wastewater volumes"""
        self.ui.nres_ww_ind_greybox.setText(str(int((self.ui.nres_ww_ind_slider.value() * -1 + 100) / 2)) + "%")
        self.ui.nres_ww_ind_blackbox.setText(str(int((self.ui.nres_ww_ind_slider.value() + 100) / 2)) + "%")
        return True

    def populate_ratings_combo(self):
        """Fills out the rating levels combo, based on the standard."""
        standards_dict = self.module.retrieve_standards(str(
            mod_waterdemand.RESSTANDARDS[self.ui.res_standard_combo.currentIndex()]))
        ratinglist = standards_dict["RatingCats"]
        self.ui.res_standard_eff.clear()
        for i in ratinglist:
            self.ui.res_standard_eff.addItem(i)
        self.ui.res_standard_eff.setCurrentIndex(0)
        return True

    def update_demand_method_stack(self):
        """Switches the stack of parameters depending on the method chosen for residential analysis."""
        self.ui.res_analysis_stack.setCurrentIndex(self.ui.resdemand_analysis_combo.currentIndex())
        return True

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        # RESIDENTIAL Water Use
        if self.ui.resdemand_analysis_combo.currentIndex() == 0:
            self.module.set_parameter("residential_method", "EUA")
        else:
            self.module.set_parameter("residential_method", "DQI")

        self.module.set_parameter("res_standard",
                                  mod_waterdemand.RESSTANDARDS[self.ui.res_standard_combo.currentIndex()])
        self.module.set_parameter("res_baseefficiency", float(self.ui.res_standard_eff.currentIndex()))

        self.module.set_parameter("res_kitchen_fq", float(self.ui.kitchen_freq.value()))
        self.module.set_parameter("res_kitchen_dur", float(self.ui.kitchen_dur.value()))
        self.module.set_parameter("res_kitchen_hot", float(self.ui.kitchen_hot.value()))
        self.module.set_parameter("res_kitchen_var", float(self.ui.kitchen_vary.value()))
        self.module.set_parameter("res_kitchen_ffp", mod_waterdemand.FFP[self.ui.kitchen_ffp.currentIndex()])
        self.module.set_parameter("res_kitchen_pat", mod_waterdemand.DPS[self.ui.kitchen_dp.currentIndex()])
        if self.ui.kitchen_blackradio.isChecked():
            self.module.set_parameter("res_kitchen_wwq", "B")
        else:
            self.module.set_parameter("res_kitchen_wwq", "G")

        self.module.set_parameter("res_shower_fq", float(self.ui.shower_freq.value()))
        self.module.set_parameter("res_shower_dur", float(self.ui.shower_dur.value()))
        self.module.set_parameter("res_shower_hot", float(self.ui.shower_hot.value()))
        self.module.set_parameter("res_shower_var", float(self.ui.shower_vary.value()))
        self.module.set_parameter("res_shower_ffp", mod_waterdemand.FFP[self.ui.shower_ffp.currentIndex()])
        self.module.set_parameter("res_shower_pat", mod_waterdemand.DPS[self.ui.shower_dp.currentIndex()])
        if self.ui.shower_blackradio.isChecked():
            self.module.set_parameter("res_shower_wwq", "B")
        else:
            self.module.set_parameter("res_shower_wwq", "G")

        self.module.set_parameter("res_toilet_fq", float(self.ui.toilet_freq.value()))
        self.module.set_parameter("res_toilet_hot", float(self.ui.toilet_hot.value()))
        self.module.set_parameter("res_toilet_var", float(self.ui.toilet_vary.value()))
        self.module.set_parameter("res_toilet_ffp", mod_waterdemand.FFP[self.ui.toilet_ffp.currentIndex()])
        self.module.set_parameter("res_toilet_pat", mod_waterdemand.DPS[self.ui.toilet_dp.currentIndex()])
        if self.ui.toilet_blackradio.isChecked():
            self.module.set_parameter("res_toilet_wwq", "B")
        else:
            self.module.set_parameter("res_toilet_wwq", "G")

        self.module.set_parameter("res_laundry_fq", float(self.ui.laundry_freq.value()))
        self.module.set_parameter("res_laundry_hot", float(self.ui.laundry_hot.value()))
        self.module.set_parameter("res_laundry_var", float(self.ui.laundry_vary.value()))
        self.module.set_parameter("res_laundry_ffp", mod_waterdemand.FFP[self.ui.laundry_ffp.currentIndex()])
        self.module.set_parameter("res_laundry_pat", mod_waterdemand.DPS[self.ui.laundry_dp.currentIndex()])
        if self.ui.laundry_blackradio.isChecked():
            self.module.set_parameter("res_laundry_wwq", "B")
        else:
            self.module.set_parameter("res_laundry_wwq", "G")

        self.module.set_parameter("res_dishwasher_fq", float(self.ui.dish_freq.value()))
        self.module.set_parameter("res_dishwasher_hot", float(self.ui.dish_hot.value()))
        self.module.set_parameter("res_dishwasher_var", float(self.ui.dish_vary.value()))
        self.module.set_parameter("res_dishwasher_ffp", mod_waterdemand.FFP[self.ui.dish_ffp.currentIndex()])
        self.module.set_parameter("res_dishwasher_pat", mod_waterdemand.DPS[self.ui.dish_dp.currentIndex()])
        if self.ui.dish_blackradio.isChecked():
            self.module.set_parameter("res_dishwasher_wwq", "B")
        else:
            self.module.set_parameter("res_dishwasher_wwq", "G")

        if self.ui.resdemand_analysis_combo.currentIndex() == 0:  # If End Use Analysis
            self.module.set_parameter("res_outdoor_vol", float(self.ui.res_irrigate_vol.value()))
            self.module.set_parameter("res_outdoor_ffp", mod_waterdemand.FFP[self.ui.res_irrigate_ffp.currentIndex()])
            self.module.set_parameter("res_outdoor_pat", mod_waterdemand.DPS[self.ui.res_irrigate_dp.currentIndex()])
        else:
            self.module.set_parameter("res_outdoor_vol", float(self.ui.res_direct_irrigate.value()))
            self.module.set_parameter("res_outdoor_ffp",
                                      mod_waterdemand.FFP[self.ui.res_direct_irrigate_ffp.currentIndex()])
            self.module.set_parameter("res_outdoor_pat", mod_waterdemand.DPS[self.ui.outdoor_dp.currentIndex()])

        self.module.set_parameter("res_dailyindoor_vol", float(self.ui.res_direct_vol.value()))
        self.module.set_parameter("res_dailyindoor_np", float(self.ui.res_direct_np.value()))
        self.module.set_parameter("res_dailyindoor_hot", float(self.ui.res_direct_hot.value()))
        self.module.set_parameter("res_dailyindoor_var", float(self.ui.res_direct_vary.value()))
        self.module.set_parameter("res_dailyindoor_pat", mod_waterdemand.DPS[self.ui.indoor_dp.currentIndex()])
        self.module.set_parameter("res_dailyindoor_bgprop", float(self.ui.res_direct_ww_slider.value()))

        # NON-RESIDENTIAL Water Use
        self.module.set_parameter("com_demand", float(self.ui.com_demandbox.text()))
        if self.ui.com_demandunits.currentIndex() == 0:
            self.module.set_parameter("com_units", "LSQMD")
        elif self.ui.com_demandunits.currentIndex() == 1:
            self.module.set_parameter("com_units", "LPAXD")
        else:
            self.module.set_parameter("com_units", "PES")

        self.module.set_parameter("office_demand", float(self.ui.office_demandbox.text()))
        if self.ui.office_demandunits.currentIndex() == 0:
            self.module.set_parameter("office_units", "LSQMD")
        elif self.ui.office_demandunits.currentIndex() == 1:
            self.module.set_parameter("office_units", "LPAXD")
        else:
            self.module.set_parameter("office_units", "PES")

        self.module.set_parameter("li_demand", float(self.ui.li_demandbox.text()))
        if self.ui.li_demandunits.currentIndex() == 0:
            self.module.set_parameter("li_units", "LSQMD")
        elif self.ui.li_demandunits.currentIndex() == 1:
            self.module.set_parameter("li_units", "LPAXD")
        else:
            self.module.set_parameter("li_units", "PES")

        self.module.set_parameter("hi_demand", float(self.ui.hi_demandbox.text()))
        if self.ui.hi_demandunits.currentIndex() == 0:
            self.module.set_parameter("hi_units", "LSQMD")
        elif self.ui.hi_demandunits.currentIndex() == 1:
            self.module.set_parameter("hi_units", "LPAXD")
        else:
            self.module.set_parameter("hi_units", "PES")

        self.module.set_parameter("com_var", float(self.ui.com_demandspin.value()))
        self.module.set_parameter("com_hot", float(self.ui.com_hotbox.value()))
        self.module.set_parameter("com_pat", mod_waterdemand.DPS[self.ui.com_dp.currentIndex()])
        self.module.set_parameter("office_var", float(self.ui.office_demandspin.value()))
        self.module.set_parameter("office_hot", float(self.ui.office_hotbox.value()))
        self.module.set_parameter("li_var", float(self.ui.li_demandspin.value()))
        self.module.set_parameter("li_hot", float(self.ui.li_hotbox.value()))
        self.module.set_parameter("ind_pat", mod_waterdemand.DPS[self.ui.ind_dp.currentIndex()])
        self.module.set_parameter("hi_var", float(self.ui.hi_demandspin.value()))
        self.module.set_parameter("hi_hot", float(self.ui.hi_hotbox.value()))
        self.module.set_parameter("nonres_landscape_vol", float(self.ui.nres_irrigate_vol.value()))
        self.module.set_parameter("nonres_landscape_ffp", mod_waterdemand.FFP[self.ui.nres_irrigate_ffp.currentIndex()])
        self.module.set_parameter("nonres_landscape_pat", mod_waterdemand.DPS[self.ui.nres_irrigate_dp.currentIndex()])
        self.module.set_parameter("com_ww_bgprop", float(self.ui.nres_ww_com_slider.value()))
        self.module.set_parameter("ind_ww_bgprop", float(self.ui.nres_ww_ind_slider.value()))

        # PUBLIC OPEN SPACES AND DISTRICTS
        self.module.set_parameter("pos_irrigation_vol", float(self.ui.pos_annual_vol.value()))
        self.module.set_parameter("pos_irrigation_ffp", mod_waterdemand.FFP[self.ui.pos_ffp.currentIndex()])
        self.module.set_parameter("irrigate_parks", int(self.ui.pos_spaces_pg.isChecked()))
        self.module.set_parameter("irrigate_landmarks", int(self.ui.pos_spaces_na.isChecked()))
        self.module.set_parameter("irrigate_reserves", int(self.ui.pos_spaces_ref.isChecked()))
        self.module.set_parameter("pos_irrigation_pat", mod_waterdemand.DPS[self.ui.pos_dp.currentIndex()])

        # REGIONAL WATER LOSSES
        self.module.set_parameter("estimate_waterloss", int(self.ui.losses_check.isChecked()))
        self.module.set_parameter("waterloss_volprop", float(self.ui.losses_volspin.value()))
        if self.ui.loss_dp.currentIndex() == 0:
            self.module.set_parameter("loss_pat", "CDP")  # Constant pattern
        else:
            self.module.set_parameter("loss_pat", "INV")  # Inverse of demands

        # TEMPORAL AND SEASONAL DYNAMICS
        self.module.set_parameter("weekend_nonres_reduce", int(self.ui.weekly_reducenres_check.isChecked()))
        self.module.set_parameter("weekend_nonres_factor", float(self.ui.weekly_reducenres_spin.value()))
        self.module.set_parameter("weekend_res_increase", int(self.ui.weekly_increaseres_check.isChecked()))
        self.module.set_parameter("weekend_res_factor", float(self.ui.weekly_increaseres_spin.value()))

        self.module.set_parameter("seasonal_analysis", int(self.ui.seasonal_check.isChecked()))
        # self.module.set_parameter("seasonal_dataset", )
        self.module.set_parameter("scaling_years", int(self.ui.seasonal_numyears_spin.value()))
        self.module.set_parameter("scaling_average", float(self.ui.seasonal_globalavg_box.text()))
        self.module.set_parameter("scaling_average_fromdata", int(self.ui.seasonal_globalavg_check.isChecked()))
        self.module.set_parameter("no_irrigate_during_rain", int(self.ui.seasonal_noirrigaterain_check.isChecked()))
        self.module.set_parameter("irrigation_resume_time", int(self.ui.seasonal_irrigateresume_spin.value()))

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

        # (2) Selected asset collection does not have urban form data
        self.update_asset_col_metadata()
        if self.metadata.get_attribute("mod_urbanformgen") != 1 and \
                self.metadata.get_attribute("mod_urbanformdata") != 1:
            prompt_msg = "The current asset collection selected does not contain urban form information to calculate" \
                         "water demands. Please run the Abstract Urban Form Module on this asset collection first."
            QtWidgets.QMessageBox.warning(self, "Pre-requisite Modules required", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False
        return True


class CustomPatternLaunch(QtWidgets.QDialog):
    """The class definition for the sub-GUI for setting custom diurnal patterns. This sub-gui launches if the custom
    button is clicked on any of the diurnal patterns within the Spatial Mapping Module."""

    def __init__(self, module, enduse, parent=None):
        """Initialization of the subGUI for entering custom diurnal patterns. This sub-gui is launched and filled with
        the current custom pattern selected.

        :param module: reference to the UBModule() Spatial Mapping Module Instance
        :param enduse: the end use key as per module.DIURNAL_CATS
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_CustomPatternDialog()
        self.ui.setupUi(self)
        self.module = module
        self.enduse = enduse

        # Transfer pattern data into table
        self.ui.endusetype.setText(mod_waterdemand.DIURNAL_LABELS[mod_waterdemand.DIURNAL_CATS.index(self.enduse)])
        self.pattern = self.module.get_wateruse_custompattern(self.enduse)
        self.ui.avg_box.setText(str(round(sum(self.pattern) / len(self.pattern), 3)))

        for i in range(24):  # Populate the table
            self.ui.tableWidget.item(i, 0).setText(str(self.pattern[i]))

        self.ui.tableWidget.itemChanged.connect(self.recalculate_avg)
        self.ui.button_Box.clicked.connect(self.save_values)

    def recalculate_avg(self):
        """Recalculates the average of the whole pattern and displays the result in the 'Average Scaling' text box."""
        subpattern = []
        try:
            for i in range(24):
                subpattern.append(float(self.ui.tableWidget.item(i, 0).text()))
            self.ui.avg_box.setText(str(round(sum(subpattern) / len(subpattern), 3)))
        except ValueError or TypeError:
            self.ui.avg_box.setText("ERROR")  # If a user enters text instead of a proper number!

    def save_values(self):
        """Creates a new pattern vector and saves this to the module."""
        for i in range(24):
            try:
                self.pattern[i] = float(self.ui.tableWidget.item(i, 0).text())
            except ValueError:  # Catch stupid entries by setting the default multiplier to 1.0
                self.pattern[i] = 1.0

        self.module.set_wateruse_custompattern(self.enduse, self.pattern)
        return True
