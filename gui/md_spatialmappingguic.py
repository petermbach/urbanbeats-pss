__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2018. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.md_spatialmappinggui import Ui_Spatialmap_Dialog
from gui.md_subgui_dp import Ui_CustomPatternDialog


# --- MAIN GUI FUNCTION ---
class SpatialMappingGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Spatial Mapping GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Spatialmap_Dialog()
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
        # seasonal_scaledata_combo - climate data

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        # self.ui.parameters.currentChanged.connect(self.adjust_module_img)   # Changes the module's image
        self.ui.planning_check.clicked.connect(self.enable_disable_whole_gui_tabs)
        self.ui.landcover_check.clicked.connect(self.enable_disable_whole_gui_tabs)
        self.ui.pos_check.clicked.connect(self.enable_disable_whole_gui_tabs)
        self.ui.wateruse_check.clicked.connect(self.enable_disable_whole_gui_tabs)
        self.ui.pollution_check.clicked.connect(self.enable_disable_whole_gui_tabs)

        # TAB 1 - PLANNING RULES PARAMETERS
        # No current signals or slots

        # TAB 2 - LAND SURFACE COVER PARAMETERS
        self.ui.lc_restrees_slider.valueChanged.connect(self.slider_landcover_update)
        self.ui.lc_nrestrees_slider.valueChanged.connect(self.slider_landcover_update)

        # TAB 3 - OPEN SPACES PARAMETERS
        # No current signals or slots

        # TAB 4 - WATER USE PARAMETERS
        self.ui.res_standard_button.clicked.connect(self.show_res_standard_details)
        self.ui.res_standard_combo.currentIndexChanged.connect(self.populate_ratings_combo)
        self.ui.res_enduse_summarybutton.clicked.connect(self.show_res_enduse_summary)
        self.ui.kitchen_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.shower_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.toilet_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.laundry_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.dish_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.res_irrigate_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.indoor_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.outdoor_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.nres_irrigate_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.com_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.ind_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.pos_dp.currentIndexChanged.connect(self.enable_disable_custom_buttons)
        self.ui.res_direct_ww_slider.valueChanged.connect(self.slider_res_value_update)
        self.ui.civic_presetsbutton.clicked.connect(self.view_civic_wateruse_presets)
        self.ui.nres_ww_com_slider.valueChanged.connect(self.slider_nres_com_update)
        self.ui.nres_ww_ind_slider.valueChanged.connect(self.slider_nres_ind_update)
        self.ui.losses_check.clicked.connect(self.enable_disable_losses_widgets)
        self.ui.weekly_reducenres_check.clicked.connect(self.enable_disable_weekly_widgets)
        self.ui.weekly_increaseres_check.clicked.connect(self.enable_disable_weekly_widgets)
        self.ui.seasonal_check.clicked.connect(self.enable_disable_seasonal_widgets)
        self.ui.seasonal_globalavg_check.clicked.connect(self.enable_disable_seasonal_widgets)
        self.ui.seasonal_noirrigaterain_check.clicked.connect(self.enable_disable_seasonal_widgets)

        self.ui.kitchen_dpcustom.clicked.connect(lambda: self.call_pattern_gui("res_kitchen"))      # Custom patterns
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

        # TAB 5 - POLLUTION EMISSIONS PARAMETERS
        # No current signals or slots

        # OTHERS
        self.ui.buttonBox.accepted.connect(self.save_values)

    def adjust_module_img(self):
        """Changes the module's image based on the currently selected tab in the GUI."""
        self.ui.module_img.setPixmap(QtGui.QPixmap(self.pixmap_ref[self.ui.parameters.currentIndex()]))

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
        self.module = self.active_scenario.get_module_object("MAP", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()
        return True

    def call_pattern_gui(self, enduse):
        """Call the sub-gui for setting a custom End Use Diurnal Patterns."""
        custompatternguic = CustomPatternLaunch(self.module, enduse)
        custompatternguic.exec_()

    def show_res_standard_details(self):
        """"""
        pass    # [TO DO]

    def show_res_enduse_summary(self):
        """Calculates an average per capita water use and displays it in the box beneath the end use analysis
        parameters."""
        standard_dict = self.module.retrieve_standards(str(
            ubglobals.RESSTANDARDS[self.ui.res_standard_combo.currentIndex()]))
        if standard_dict["Name"] == "Others...":
            self.ui.res_enduse_summarybox.setText("Total: (undefined) L/person/day)")
            return True

        # OMFG.... I need an average occupancy from another GUI element... urrgh.
        avg_occupancy = self.simulation.get_active_scenario().get_module_object("URBPLAN", 0).get_parameter("occup_avg")

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
                                              str(avg_occupancy)+")")   # OMG it actually worked...
        return True

    def view_civic_wateruse_presets(self):
        """"""
        pass    # [TO DO]

    def slider_landcover_update(self):
        """Updates all land cover slider values."""
        self.ui.lc_restrees_box.setText(str(self.ui.lc_restrees_slider.value())+"%")
        self.ui.lc_nrestrees_box.setText(str(self.ui.lc_nrestrees_slider.value()) + "%")
        return True

    def slider_res_value_update(self):
        """Updates the residential blackwater/greywater slider value boxes to reflect the current slider's value."""
        self.ui.res_direct_wwboxgrey.setText(str(int((self.ui.res_direct_ww_slider.value()*-1+100)/2))+"%")
        self.ui.res_direct_wwboxblack.setText(str(int((self.ui.res_direct_ww_slider.value()+100)/2))+"%")
        return True

    def slider_nres_com_update(self):
        """Updates the non-residential slider for commercial wastewater volumes"""
        self.ui.nres_ww_com_greybox.setText(str(int((self.ui.nres_ww_com_slider.value()*-1+100)/2))+"%")
        self.ui.nres_ww_com_blackbox.setText(str(int((self.ui.nres_ww_com_slider.value() + 100) / 2)) + "%")
        return True

    def slider_nres_ind_update(self):
        """Updates the non-residential slider for industrial wastewater volumes"""
        self.ui.nres_ww_ind_greybox.setText(str(int((self.ui.nres_ww_ind_slider.value() * -1 + 100) / 2)) + "%")
        self.ui.nres_ww_ind_blackbox.setText(str(int((self.ui.nres_ww_ind_slider.value() + 100) / 2)) + "%")
        return True

    def enable_disable_whole_gui_tabs(self):
        """Enables and disables the entire GUI chunks depending on which assessment checkboxes have been checked."""
        self.ui.overlays_scrollArea.setEnabled(self.ui.planning_check.isChecked())
        self.ui.landcover_scrollArea.setEnabled(self.ui.landcover_check.isChecked())
        self.ui.pos_scrollArea.setEnabled(self.ui.pos_check.isChecked())
        self.ui.wateruse_master_widget.setEnabled(self.ui.wateruse_check.isChecked())
        self.ui.pollution_scrollArea.setEnabled(self.ui.pollution_check.isChecked())
        return True

    def enable_disable_losses_widgets(self):
        """Enables and disables the water losses options when clicking the respective radio buttons."""
        self.ui.losses_volspin.setEnabled(self.ui.losses_check.isChecked())
        return True

    def enable_disable_weekly_widgets(self):
        """Enables and disables the weekly water use behaviour options."""
        self.ui.weekly_reducenres_spin.setEnabled(self.ui.weekly_reducenres_check.isChecked())
        self.ui.weekly_increaseres_spin.setEnabled(self.ui.weekly_increaseres_check.isChecked())
        return True

    def enable_disable_seasonal_widgets(self):
        """Enables and disables the seasonal widgets."""
        self.ui.seasonal_globalavg_box.setEnabled(not self.ui.seasonal_globalavg_check.isChecked())
        self.ui.seasonal_irrigateresume_spin.setEnabled(self.ui.seasonal_noirrigaterain_check.isChecked())
        self.ui.seasonal_widget.setEnabled(self.ui.seasonal_check.isChecked())
        return True

    def enable_disable_custom_buttons(self):
        """Enables and disables all the diurnal pattern custom buttons depending on the state of the combo boxes."""
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
        return True

    def populate_ratings_combo(self):
        """Fills out the rating levels combo, based on the standard."""
        standards_dict = self.module.retrieve_standards(str(
            ubglobals.RESSTANDARDS[self.ui.res_standard_combo.currentIndex()]))
        ratinglist = standards_dict["RatingCats"]
        self.ui.res_standard_eff.clear()
        for i in ratinglist:
            self.ui.res_standard_eff.addItem(i)
        self.ui.res_standard_eff.setCurrentIndex(0)
        return True

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""
        # MAIN CHECK BOXES
        self.ui.planning_check.setChecked(int(self.module.get_parameter("planrules")))
        self.ui.landcover_check.setChecked(int(self.module.get_parameter("landcover")))
        self.ui.pos_check.setChecked(int(self.module.get_parameter("openspaces")))
        self.ui.wateruse_check.setChecked(int(self.module.get_parameter("wateruse")))
        self.ui.pollution_check.setChecked(int(self.module.get_parameter("emissions")))

        # TAB 1 - PLANNING RULES PARAMETERS

        # TAB 2 - LAND SURFACE COVER PARAMETERS
        self.ui.lc_respave_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfDriveway")))
        if self.module.get_parameter("surfResIrrigate") == "G":
            self.ui.lc_resirri_garden.setChecked(1)
        else:
            self.ui.lc_resirri_allperv.setChecked(1)
        self.ui.lc_restrees_slider.setValue(int(self.module.get_parameter("trees_Res") * 100))
        self.ui.lc_nrespark_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfParking")))
        self.ui.lc_nresbay_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfBay")))
        self.ui.lc_nreshard_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfHard")))
        self.ui.lc_nrestrees_slider.setValue(int(self.module.get_parameter("trees_NRes")*100))
        self.ui.lc_nrestreeloc_checkon.setChecked(int(self.module.get_parameter("trees_Site")))
        self.ui.lc_nrestreeloc_checkoff.setChecked(int(self.module.get_parameter("trees_Front")))
        self.ui.lc_rdloc_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfArt")))
        self.ui.lc_rdhwy_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfHwy")))
        self.ui.lc_rdfpath_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfFpath")))
        self.ui.lc_rdtreedens_spin.setValue(self.module.get_parameter("trees_roaddens"))
        self.ui.lc_openpave_combo.setCurrentIndex(ubglobals.LANDCOVERMATERIALS.index(
            self.module.get_parameter("surfSquare")))
        self.ui.lc_opentrees_spin.setValue(self.module.get_parameter("trees_opendens"))
        self.ui.lc_reftrees_spin.setValue(self.module.get_parameter("trees_refdens"))
        self.ui.lc_vegetation_combo.setCurrentIndex(ubglobals.TREETYPES.index(self.module.get_parameter("tree_type")))

        self.slider_landcover_update()      # Enable/disable functions

        # TAB 3 - OPEN SPACE MAPPING AND STRATEGIES
        self.ui.osnet_accessibility_check.setChecked(int(self.module.get_parameter("osnet_accessibility")))
        self.ui.osnet_spacenet_check.setChecked(int(self.module.get_parameter("osnet_network")))
        self.ui.pg_usable_prohibit.setChecked(int(self.module.get_parameter("parks_restrict")))
        self.ui.ref_limit_check.setChecked(int(self.module.get_parameter("reserves_restrict")))

        # TAB 4 - WATER USE PARAMETERS
        # RESIDENTIAL Water Use
        if self.module.get_parameter("residential_method") == "EUA":
            self.ui.resdemand_analysis_combo.setCurrentIndex(0)
            self.ui.res_analysis_stack.setCurrentIndex(0)
        else:
            self.ui.resdemand_analysis_combo.setCurrentIndex(1)
            self.ui.res_analysis_stack.setCurrentIndex(1)

        self.ui.res_standard_combo.setCurrentIndex(ubglobals.RESSTANDARDS.index(
            self.module.get_parameter("res_standard")))
        self.populate_ratings_combo()
        self.ui.res_standard_eff.setCurrentIndex(int(self.module.get_parameter("res_baseefficiency")))

        self.ui.kitchen_freq.setValue(float(self.module.get_parameter("res_kitchen_fq")))
        self.ui.kitchen_dur.setValue(int(self.module.get_parameter("res_kitchen_dur")))
        self.ui.kitchen_hot.setValue(int(self.module.get_parameter("res_kitchen_hot")))
        self.ui.kitchen_vary.setValue(int(self.module.get_parameter("res_kitchen_var")))
        self.ui.kitchen_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("res_kitchen_ffp")))
        self.ui.kitchen_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_kitchen_pat")))
        if self.module.get_parameter("res_kitchen_wwq") == "B":
            self.ui.kitchen_blackradio.setChecked(1)
        else:
            self.ui.kitchen_greyradio.setChecked(1)

        self.ui.shower_freq.setValue(float(self.module.get_parameter("res_shower_fq")))
        self.ui.shower_dur.setValue(int(self.module.get_parameter("res_shower_dur")))
        self.ui.shower_hot.setValue(int(self.module.get_parameter("res_shower_hot")))
        self.ui.shower_vary.setValue(int(self.module.get_parameter("res_shower_var")))
        self.ui.shower_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("res_shower_ffp")))
        self.ui.shower_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_shower_pat")))
        if self.module.get_parameter("res_shower_wwq") == "B":
            self.ui.shower_blackradio.setChecked(1)
        else:
            self.ui.shower_greyradio.setChecked(1)

        self.ui.toilet_freq.setValue(float(self.module.get_parameter("res_toilet_fq")))
        self.ui.toilet_hot.setValue(int(self.module.get_parameter("res_toilet_hot")))
        self.ui.toilet_vary.setValue(int(self.module.get_parameter("res_toilet_var")))
        self.ui.toilet_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("res_toilet_ffp")))
        self.ui.toilet_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_toilet_pat")))
        if self.module.get_parameter("res_toilet_wwq") == "B":
            self.ui.toilet_blackradio.setChecked(1)
        else:
            self.ui.toilet_greyradio.setChecked(1)

        self.ui.laundry_freq.setValue(float(self.module.get_parameter("res_laundry_fq")))
        self.ui.laundry_hot.setValue(int(self.module.get_parameter("res_laundry_hot")))
        self.ui.laundry_vary.setValue(int(self.module.get_parameter("res_laundry_var")))
        self.ui.laundry_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("res_laundry_ffp")))
        self.ui.laundry_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_laundry_pat")))
        if self.module.get_parameter("res_laundry_wwq") == "B":
            self.ui.laundry_blackradio.setChecked(1)
        else:
            self.ui.laundry_greyradio.setChecked(1)

        self.ui.dish_freq.setValue(float(self.module.get_parameter("res_dishwasher_fq")))
        self.ui.dish_hot.setValue(int(self.module.get_parameter("res_dishwasher_hot")))
        self.ui.dish_vary.setValue(int(self.module.get_parameter("res_dishwasher_var")))
        self.ui.dish_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("res_dishwasher_ffp")))
        self.ui.dish_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_dishwasher_pat")))
        if self.module.get_parameter("res_dishwasher_wwq") == "B":
            self.ui.dish_blackradio.setChecked(1)
        else:
            self.ui.dish_greyradio.setChecked(1)

        self.ui.res_irrigate_vol.setValue(float(self.module.get_parameter("res_outdoor_vol")))
        self.ui.res_irrigate_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("res_outdoor_ffp")))
        self.ui.res_irrigate_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_outdoor_pat")))

        self.ui.res_direct_vol.setValue(float(self.module.get_parameter("res_dailyindoor_vol")))
        self.ui.res_direct_np.setValue(int(self.module.get_parameter("res_dailyindoor_np")))
        self.ui.res_direct_hot.setValue(int(self.module.get_parameter("res_dailyindoor_hot")))
        self.ui.res_direct_vary.setValue(int(self.module.get_parameter("res_dailyindoor_var")))
        self.ui.indoor_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_dailyindoor_pat")))
        self.ui.res_direct_ww_slider.setValue(self.module.get_parameter("res_dailyindoor_bgprop"))

        self.ui.res_direct_irrigate.setValue(float(self.module.get_parameter("res_outdoor_vol")))
        self.ui.res_direct_irrigate_ffp.setCurrentIndex(ubglobals.FFP.index(
            self.module.get_parameter("res_outdoor_ffp")))
        self.ui.outdoor_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("res_outdoor_pat")))

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
        self.ui.com_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("com_pat")))

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
        self.ui.ind_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("ind_pat")))

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
        self.ui.nres_irrigate_ffp.setCurrentIndex(ubglobals.FFP.index(
            self.module.get_parameter("nonres_landscape_ffp")))
        self.ui.nres_irrigate_dp.setCurrentIndex(ubglobals.DPS.index(
            self.module.get_parameter("nonres_landscape_pat")))

        self.ui.nres_ww_com_slider.setValue(int(self.module.get_parameter("com_ww_bgprop")))
        self.ui.nres_ww_ind_slider.setValue(int(self.module.get_parameter("ind_ww_bgprop")))

        # PUBLIC OPEN SPACE AND DISTRICTS Water Use
        self.ui.pos_annual_vol.setValue(float(self.module.get_parameter("pos_irrigation_vol")))
        self.ui.pos_ffp.setCurrentIndex(ubglobals.FFP.index(self.module.get_parameter("pos_irrigation_ffp")))
        self.ui.pos_spaces_pg.setChecked(int(self.module.get_parameter("irrigate_parks")))
        self.ui.pos_spaces_na.setChecked(int(self.module.get_parameter("irrigate_landmarks")))
        self.ui.pos_spaces_ref.setChecked(int(self.module.get_parameter("irrigate_reserves")))
        self.ui.pos_dp.setCurrentIndex(ubglobals.DPS.index(self.module.get_parameter("pos_irrigation_pat")))

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

        self.enable_disable_custom_buttons()    # Enable/Disable Functions
        self.enable_disable_losses_widgets()
        self.enable_disable_seasonal_widgets()
        self.enable_disable_weekly_widgets()
        self.slider_nres_com_update()
        self.slider_nres_ind_update()
        self.slider_res_value_update()

        # TAB 5 - POLLUTION EMISSIONS

        # END OF FILING IN GUI VALUES
        self.enable_disable_whole_gui_tabs()
        self.show_res_enduse_summary()
        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        # MAIN CHECK BOXES
        self.module.set_parameter("planrules", int(self.ui.planning_check.isChecked()))
        self.module.set_parameter("landcover", int(self.ui.landcover_check.isChecked()))
        self.module.set_parameter("openspaces", int(self.ui.pos_check.isChecked()))
        self.module.set_parameter("wateruse", int(self.ui.wateruse_check.isChecked()))
        self.module.set_parameter("emissions", int(self.ui.pollution_check.isChecked()))

        # TAB 1 - PLANNING RULES PARAMETERS

        # TAB 2 - LAND SURFACE COVER PARAMETERS
        self.module.set_parameter("surfDriveway", ubglobals.LANDCOVERMATERIALS[self.ui.lc_respave_combo.currentIndex()])
        if self.ui.lc_resirri_garden.isChecked():
            self.module.set_parameter("surfResIrrigate", "G")
        else:
            self.module.set_parameter("surfResIrrigate", "A")
        self.module.set_parameter("trees_Res", float(self.ui.lc_restrees_slider.value())/100.0)
        self.module.set_parameter("surfParking", ubglobals.LANDCOVERMATERIALS[self.ui.lc_nrespark_combo.currentIndex()])
        self.module.set_parameter("surfBay", ubglobals.LANDCOVERMATERIALS[self.ui.lc_nresbay_combo.currentIndex()])
        self.module.set_parameter("surfHard", ubglobals.LANDCOVERMATERIALS[self.ui.lc_nreshard_combo.currentIndex()])
        self.module.set_parameter("trees_NRes", float(self.ui.lc_nrestrees_slider.value())/100.0)
        self.module.set_parameter("trees_Site", int(self.ui.lc_nrestreeloc_checkon.isChecked()))
        self.module.set_parameter("trees_Front", int(self.ui.lc_nrestreeloc_checkoff.isChecked()))
        self.module.set_parameter("surfArt", ubglobals.LANDCOVERMATERIALS[self.ui.lc_rdloc_combo.currentIndex()])
        self.module.set_parameter("surfHwy", ubglobals.LANDCOVERMATERIALS[self.ui.lc_rdhwy_combo.currentIndex()])
        self.module.set_parameter("surfFpath", ubglobals.LANDCOVERMATERIALS[self.ui.lc_rdfpath_combo.currentIndex()])
        self.module.set_parameter("trees_roaddens", float(self.ui.lc_rdtreedens_spin.value()))
        self.module.set_parameter("surfSquare", ubglobals.LANDCOVERMATERIALS[self.ui.lc_openpave_combo.currentIndex()])
        self.module.set_parameter("trees_opendens", float(self.ui.lc_opentrees_spin.value()))
        self.module.set_parameter("trees_refdens", float(self.ui.lc_reftrees_spin.value()))
        self.module.set_parameter("tree_type", ubglobals.TREETYPES[self.ui.lc_vegetation_combo.currentIndex()])

        # TAB 3 - OPEN SPACE CONNECTIVITY AND NETWORKS
        self.module.set_parameter("osnet_accessibility", int(self.ui.osnet_accessibility_check.isChecked()))
        self.module.set_parameter("osnet_network", int(self.ui.osnet_spacenet_check.isChecked()))
        self.module.set_parameter("parks_restrict", int(self.ui.pg_usable_prohibit.isChecked()))
        self.module.set_parameter("reserves_restrict", int(self.ui.ref_limit_check.isChecked()))

        # TAB 4 - WATER USE PARAMETERS
        # RESIDENTIAL Water Use
        if self.ui.resdemand_analysis_combo.currentIndex() == 0:
            self.module.set_parameter("residential_method", "EUA")
        else:
            self.module.set_parameter("residential_method", "DQI")

        self.module.set_parameter("res_standard", ubglobals.RESSTANDARDS[self.ui.res_standard_combo.currentIndex()])
        self.module.set_parameter("res_baseefficiency", float(self.ui.res_standard_eff.currentIndex()))

        self.module.set_parameter("res_kitchen_fq", float(self.ui.kitchen_freq.value()))
        self.module.set_parameter("res_kitchen_dur", float(self.ui.kitchen_dur.value()))
        self.module.set_parameter("res_kitchen_hot", float(self.ui.kitchen_hot.value()))
        self.module.set_parameter("res_kitchen_var", float(self.ui.kitchen_vary.value()))
        self.module.set_parameter("res_kitchen_ffp", ubglobals.FFP[self.ui.kitchen_ffp.currentIndex()])
        self.module.set_parameter("res_kitchen_pat", ubglobals.DPS[self.ui.kitchen_dp.currentIndex()])
        if self.ui.kitchen_blackradio.isChecked():
            self.module.set_parameter("res_kitchen_wwq", "B")
        else:
            self.module.set_parameter("res_kitchen_wwq", "G")

        self.module.set_parameter("res_shower_fq", float(self.ui.shower_freq.value()))
        self.module.set_parameter("res_shower_dur", float(self.ui.shower_dur.value()))
        self.module.set_parameter("res_shower_hot", float(self.ui.shower_hot.value()))
        self.module.set_parameter("res_shower_var", float(self.ui.shower_vary.value()))
        self.module.set_parameter("res_shower_ffp", ubglobals.FFP[self.ui.shower_ffp.currentIndex()])
        self.module.set_parameter("res_shower_pat", ubglobals.DPS[self.ui.shower_dp.currentIndex()])
        if self.ui.shower_blackradio.isChecked():
            self.module.set_parameter("res_shower_wwq", "B")
        else:
            self.module.set_parameter("res_shower_wwq", "G")

        self.module.set_parameter("res_toilet_fq", float(self.ui.toilet_freq.value()))
        self.module.set_parameter("res_toilet_hot", float(self.ui.toilet_hot.value()))
        self.module.set_parameter("res_toilet_var", float(self.ui.toilet_vary.value()))
        self.module.set_parameter("res_toilet_ffp", ubglobals.FFP[self.ui.toilet_ffp.currentIndex()])
        self.module.set_parameter("res_toilet_pat", ubglobals.DPS[self.ui.toilet_dp.currentIndex()])
        if self.ui.toilet_blackradio.isChecked():
            self.module.set_parameter("res_toilet_wwq", "B")
        else:
            self.module.set_parameter("res_toilet_wwq", "G")

        self.module.set_parameter("res_laundry_fq", float(self.ui.laundry_freq.value()))
        self.module.set_parameter("res_laundry_hot", float(self.ui.laundry_hot.value()))
        self.module.set_parameter("res_laundry_var", float(self.ui.laundry_vary.value()))
        self.module.set_parameter("res_laundry_ffp", ubglobals.FFP[self.ui.laundry_ffp.currentIndex()])
        self.module.set_parameter("res_laundry_pat", ubglobals.DPS[self.ui.laundry_dp.currentIndex()])
        if self.ui.laundry_blackradio.isChecked():
            self.module.set_parameter("res_laundry_wwq", "B")
        else:
            self.module.set_parameter("res_laundry_wwq", "G")

        self.module.set_parameter("res_dishwasher_fq", float(self.ui.dish_freq.value()))
        self.module.set_parameter("res_dishwasher_hot", float(self.ui.dish_hot.value()))
        self.module.set_parameter("res_dishwasher_var", float(self.ui.dish_vary.value()))
        self.module.set_parameter("res_dishwasher_ffp", ubglobals.FFP[self.ui.dish_ffp.currentIndex()])
        self.module.set_parameter("res_dishwasher_pat", ubglobals.DPS[self.ui.dish_dp.currentIndex()])
        if self.ui.dish_blackradio.isChecked():
            self.module.set_parameter("res_dishwasher_wwq", "B")
        else:
            self.module.set_parameter("res_dishwasher_wwq", "G")

        if self.ui.resdemand_analysis_combo.currentIndex() == 0:  # If End Use Analysis
            self.module.set_parameter("res_outdoor_vol", float(self.ui.res_irrigate_vol.value()))
            self.module.set_parameter("res_outdoor_ffp", ubglobals.FFP[self.ui.res_irrigate_ffp.currentIndex()])
            self.module.set_parameter("res_outdoor_pat", ubglobals.DPS[self.ui.res_irrigate_dp.currentIndex()])
        else:
            self.module.set_parameter("res_outdoor_vol", float(self.ui.res_direct_irrigate.value()))
            self.module.set_parameter("res_outdoor_ffp", ubglobals.FFP[self.ui.res_direct_irrigate_ffp.currentIndex()])
            self.module.set_parameter("res_outdoor_pat", ubglobals.DPS[self.ui.outdoor_dp.currentIndex()])

        self.module.set_parameter("res_dailyindoor_vol", float(self.ui.res_direct_vol.value()))
        self.module.set_parameter("res_dailyindoor_np", float(self.ui.res_direct_np.value()))
        self.module.set_parameter("res_dailyindoor_hot", float(self.ui.res_direct_hot.value()))
        self.module.set_parameter("res_dailyindoor_var", float(self.ui.res_direct_vary.value()))
        self.module.set_parameter("res_dailyindoor_pat", ubglobals.DPS[self.ui.indoor_dp.currentIndex()])
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
        self.module.set_parameter("com_pat", ubglobals.DPS[self.ui.com_dp.currentIndex()])
        self.module.set_parameter("office_var", float(self.ui.office_demandspin.value()))
        self.module.set_parameter("office_hot", float(self.ui.office_hotbox.value()))
        self.module.set_parameter("li_var", float(self.ui.li_demandspin.value()))
        self.module.set_parameter("li_hot", float(self.ui.li_hotbox.value()))
        self.module.set_parameter("ind_pat", ubglobals.DPS[self.ui.ind_dp.currentIndex()])
        self.module.set_parameter("hi_var", float(self.ui.hi_demandspin.value()))
        self.module.set_parameter("hi_hot", float(self.ui.hi_hotbox.value()))
        self.module.set_parameter("nonres_landscape_vol", float(self.ui.nres_irrigate_vol.value()))
        self.module.set_parameter("nonres_landscape_ffp", ubglobals.FFP[self.ui.nres_irrigate_ffp.currentIndex()])
        self.module.set_parameter("nonres_landscape_pat", ubglobals.DPS[self.ui.nres_irrigate_dp.currentIndex()])
        self.module.set_parameter("com_ww_bgprop", float(self.ui.nres_ww_com_slider.value()))
        self.module.set_parameter("ind_ww_bgprop", float(self.ui.nres_ww_ind_slider.value()))

        # PUBLIC OPEN SPACES AND DISTRICTS
        self.module.set_parameter("pos_irrigation_vol", float(self.ui.pos_annual_vol.value()))
        self.module.set_parameter("pos_irrigation_ffp", ubglobals.FFP[self.ui.pos_ffp.currentIndex()])
        self.module.set_parameter("irrigate_parks", int(self.ui.pos_spaces_pg.isChecked()))
        self.module.set_parameter("irrigate_landmarks", int(self.ui.pos_spaces_na.isChecked()))
        self.module.set_parameter("irrigate_reserves", int(self.ui.pos_spaces_ref.isChecked()))
        self.module.set_parameter("pos_irrigation_pat", ubglobals.DPS[self.ui.pos_dp.currentIndex()])

        # REGIONAL WATER LOSSES
        self.module.set_parameter("estimate_waterloss", int(self.ui.losses_check.isChecked()))
        self.module.set_parameter("waterloss_volprop", float(self.ui.losses_volspin.value()))
        if self.ui.loss_dp.currentIndex() == 0:
            self.module.set_parameter("loss_pat", "CDP")    # Constant pattern
        else:
            self.module.set_parameter("loss_pat", "INV")    # Inverse of demands

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

        # TAB 5 - POLLUTION EMISSIONS PARAMETERS
        return True


class CustomPatternLaunch(QtWidgets.QDialog):
    """The class definition for the sub-GUI for setting custom diurnal patterns. This sub-gui launches if the custom
    button is clicked on any of the diurnal patterns within the Spatial Mapping Module."""
    def __init__(self, module, enduse, parent = None):
        """Initialization of the subGUI for entering custom diurnal patterns. This sub-gui is launched and filled with
        the current custom pattern selected.

        :param module: reference to the UBModule() Spatial Mapping Module Instance
        :param enduse: the end use key as per ubglobals.DIURNAL_CATS
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_CustomPatternDialog()
        self.ui.setupUi(self)
        self.module = module
        self.enduse = enduse

        # Transfer pattern data into table
        self.ui.endusetype.setText(ubglobals.DIURNAL_LABELS[ubglobals.DIURNAL_CATS.index(self.enduse)])
        self.pattern = self.module.get_wateruse_custompattern(self.enduse)
        self.ui.avg_box.setText(str(round(sum(self.pattern) / len(self.pattern), 3)))

        for i in range(24):     # Populate the table
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
            self.ui.avg_box.setText("ERROR")    # If a user enters text instead of a proper number!

    def save_values(self):
        """Creates a new pattern vector and saves this to the module."""
        for i in range(24):
            try:
                self.pattern[i] = float(self.ui.tableWidget.item(i, 0).text())
            except ValueError:  # Catch stupid entries by setting the default multiplier to 1.0
                self.pattern[i] = 1.0

        self.module.set_wateruse_custompattern(self.enduse, self.pattern)
        return True
