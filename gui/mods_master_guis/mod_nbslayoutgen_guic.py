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
from .mod_nbslayoutgen_gui import Ui_NbSLayoutGen_Gui

# --- MAIN GUI FUNCTION ---
class NbSLayoutGenerationLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "NbS Planning and Design"
    catorder = 3
    longname = "NbS Scheme Generation"
    icon = ":/icons/nbs_layout.png"

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
        self.ui = Ui_NbSLayoutGen_Gui()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None
        self.geomtype = None    # The active asset collection's geometry type

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
            if mode != 1:   # If we are running standalone mode
                if simgrids[n].get_container_type() == "Standalone":
                    self.ui.assetcol_combo.addItem(str(n))
                self.ui.assetcol_combo.setEnabled(1)
            else:
                self.ui.assetcol_combo.addItem(
                    self.active_scenario.get_asset_collection_container().get_container_name())
                self.ui.assetcol_combo.setEnabled(0)
        self.update_asset_col_metadata()

        # OTHER COMBOs

        # --- SIGNALS AND SLOTS ---
        # self.ui.assetcol_combo.currentIndexChanged.connect(self.update_method_combo)
        self.ui.service_luc_check.clicked.connect(self.enable_disable_guis)
        self.ui.scalepref_check.clicked.connect(self.enable_disable_guis)
        self.ui.techpref_check.clicked.connect(self.enable_disable_guis)
        self.ui.techpref_ubeatsdefault_check.clicked.connect(self.enable_disable_guis)
        self.ui.techpref_matrixbrowse.clicked.connect(self.load_custom_techprefmatrix)
        self.ui.techpref_tech_check.clicked.connect(self.enable_disable_guis)
        self.ui.techpref_env_check.clicked.connect(self.enable_disable_guis)
        self.ui.techpref_econ_check.clicked.connect(self.enable_disable_guis)
        self.ui.techpref_soc_check.clicked.connect(self.enable_disable_guis)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.setup_gui_with_parameters()
        self.enable_disable_guis()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def enable_disable_guis(self):
        """Enables and disables a large proportion of GUI elements depending on signals"""
        # Land use checkboxes
        self.ui.service_res.setEnabled(self.ui.service_luc_check.isChecked())
        self.ui.service_hdr.setEnabled(self.ui.service_luc_check.isChecked())
        self.ui.service_com.setEnabled(self.ui.service_luc_check.isChecked())
        self.ui.service_li.setEnabled(self.ui.service_luc_check.isChecked())
        self.ui.service_hi.setEnabled(self.ui.service_luc_check.isChecked())

        # Evaluation Tab
        self.ui.scalepref_widget.setEnabled(self.ui.scalepref_check.isChecked())
        self.ui.techpref_widget.setEnabled(self.ui.techpref_check.isChecked())
        self.ui.techpref_weights_widget.setEnabled(self.ui.techpref_check.isChecked())
        if self.ui.techpref_check.isChecked():
            self.ui.techpref_matrix_box.setEnabled(not self.ui.techpref_ubeatsdefault_check.isChecked())
            self.ui.techpref_matrixbrowse.setEnabled(not self.ui.techpref_ubeatsdefault_check.isChecked())

        if self.ui.techpref_check.isChecked():
            self.ui.techpref_tech_spin.setEnabled(self.ui.techpref_tech_check.isChecked())
            self.ui.techpref_env_spin.setEnabled(self.ui.techpref_env_check.isChecked())
            self.ui.techpref_econ_spin.setEnabled(self.ui.techpref_econ_check.isChecked())
            self.ui.techpref_soc_spin.setEnabled(self.ui.techpref_soc_check.isChecked())

    def load_custom_techprefmatrix(self):
        """Browses and loads a custom technology scoring matrix"""
        dir = self.simulation.get_project_path()
        message = "Load Custom Technology Preference Matrix (.csv)"
        filename, fmt = QtWidgets.QFileDialog.getOpenFileName(self, message, dir, "CSV (*.csv)")
        if filename:
            self.ui.techpref_matrix_box.setText(filename)
        return True

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # SERVICE LEVEL SETTINGS
        self.ui.service_runoff_spin.setValue(float(self.module.get_parameter("runoff_service")))
        self.ui.service_pollute_spin.setValue(float(self.module.get_parameter("wq_service")))
        self.ui.service_recycle_spin.setValue(float(self.module.get_parameter("rec_service")))
        self.ui.service_luc_check.setChecked(int(self.module.get_parameter("service_luc")))
        self.ui.service_res.setChecked(int(self.module.get_parameter("service_res")))
        self.ui.service_hdr.setChecked(int(self.module.get_parameter("service_hdr")))
        self.ui.service_com.setChecked(int(self.module.get_parameter("service_com")))
        self.ui.service_li.setChecked(int(self.module.get_parameter("service_li")))
        self.ui.service_hi.setChecked(int(self.module.get_parameter("service_hi")))
        self.ui.service_redundancy.setValue(float(self.module.get_parameter("redundancy")))

        if self.module.get_parameter("search_method") == "UNTARGET":
            self.ui.montecarlo_method_combo.setCurrentIndex(0)
        else:
            self.ui.montecarlo_method_combo.setCurrentIndex(1)

        self.ui.montecarlo_maxiter_spin.setValue(int(self.module.get_parameter("maxiter")))
        self.ui.montecarlo_select_spin.setValue(int(self.module.get_parameter("numstrats")))

        if self.module.get_parameter("selectstrat") == "TOP":
            self.ui.montecarlo_score_combo.setCurrentIndex(0)
        else:
            self.ui.montecarlo_score_combo.setCurrentIndex(1)

        if self.module.get_parameter("selectmethod") == "RANK":
            self.ui.montecarlo_ranks_radio.setChecked(1)
        else:
            self.ui.montecarlo_ci_radio.setChecked(1)

        # EVALUATION TAB
        self.ui.scalepref_check.setChecked(int(self.module.get_parameter("scalepref")))
        self.ui.scalepref_slider.setValue(int(self.module.get_parameter("scaleweight")))
        self.ui.techpref_check.setChecked(int(self.module.get_parameter("techpref")))
        self.ui.techpref_matrix_box.setText(str(self.module.get_parameter("techprefmatrixfile")))
        self.ui.techpref_ubeatsdefault_check.setChecked(int(self.module.get_parameter("techprefmatrixdef")))
        self.ui.techpref_tech_check.setChecked(int(self.module.get_parameter("tech_incl")))
        self.ui.techpref_env_check.setChecked(int(self.module.get_parameter("env_incl")))
        self.ui.techpref_econ_check.setChecked(int(self.module.get_parameter("econ_incl")))
        self.ui.techpref_soc_check.setChecked(int(self.module.get_parameter("soc_incl")))
        self.ui.techpref_tech_spin.setValue(int(self.module.get_parameter("tech_w")))
        self.ui.techpref_env_spin.setValue(int(self.module.get_parameter("env_w")))
        self.ui.techpref_econ_spin.setValue(int(self.module.get_parameter("econ_w")))
        self.ui.techpref_soc_spin.setValue(int(self.module.get_parameter("soc_w")))

        scoringstrats = ["NP", "LP", "EP"]
        self.ui.scoring_strat_combo.setCurrentIndex(scoringstrats.index(self.module.get_parameter("scoringstrat")))

        if self.module.get_parameter("scoringmethod") == "WPM":
            self.ui.scoring_method_combo.setCurrentIndex(0)
        else:
            self.ui.scoring_method_combo.setCurrentIndex(1)

        self.ui.scoring_method_check.setChecked(int(self.module.get_parameter("includestoch")))
        self.ui.scoring_multifunction_spin.setValue(float(self.module.get_parameter("multifunction_bonus")))

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        # SERVICE LEVEL SETTINGS
        self.module.set_parameter("runoff_service", float(self.ui.service_runoff_spin.value()))
        self.module.set_parameter("wq_service", float(self.ui.service_pollute_spin.value()))
        self.module.set_parameter("rec_service", float(self.ui.service_recycle_spin.value()))
        self.module.set_parameter("service_luc", int(self.ui.service_luc_check.isChecked()))
        self.module.set_parameter("service_res", int(self.ui.service_res.isChecked()))
        self.module.set_parameter("service_hdr", int(self.ui.service_hdr.isChecked()))
        self.module.set_parameter("service_com", int(self.ui.service_com.isChecked()))
        self.module.set_parameter("service_li", int(self.ui.service_li.isChecked()))
        self.module.set_parameter("service_hi", int(self.ui.service_hi.isChecked()))
        self.module.set_parameter("redundancy", float(self.ui.service_redundancy.value()))

        if self.ui.montecarlo_method_combo.currentIndex() == 0:
            self.module.set_parameter("search_method", "UNTARGET")
        else:
            self.module.set_parameter("search_method", "TARGET")

        self.module.set_parameter("maxiter", int(self.ui.montecarlo_maxiter_spin.value()))
        self.module.set_parameter("numstrats", int(self.ui.montecarlo_select_spin.value()))

        if self.ui.montecarlo_score_combo.currentIndex() == 0:
            self.module.set_parameter("selectstrat", "TOP")
        else:
            self.module.set_parameter("selectstrat", "RAND")

        if self.ui.montecarlo_ranks_radio.isChecked():
            self.module.set_parameter("selectmethod", "RANK")
        else:
            self.module.set_parameter("selectmethod", "CONF")

        # EVALUATION TAB
        self.module.set_parameter("scalepref", int(self.ui.scalepref_check.isChecked()))
        self.module.set_parameter("scaleweight", int(self.ui.scalepref_slider.value()))
        self.module.set_parameter("techpref", int(self.ui.techpref_check.isChecked()))
        self.module.set_parameter("techprefmatrixfile", str(self.ui.techpref_matrix_box.text()))
        self.module.set_parameter("techprefmatrixdef", int(self.ui.techpref_ubeatsdefault_check.isChecked()))
        self.module.set_parameter("tech_incl", int(self.ui.techpref_tech_check.isChecked()))
        self.module.set_parameter("env_incl", int(self.ui.techpref_env_check.isChecked()))
        self.module.set_parameter("econ_incl", int(self.ui.techpref_econ_check.isChecked()))
        self.module.set_parameter("soc_incl", int(self.ui.techpref_soc_check.isChecked()))
        self.module.set_parameter("tech_w", int(self.ui.techpref_tech_spin.value()))
        self.module.set_parameter("env_w", int(self.ui.techpref_env_spin.value()))
        self.module.set_parameter("econ_w", int(self.ui.techpref_econ_spin.value()))
        self.module.set_parameter("soc_w", int(self.ui.techpref_soc_spin.value()))

        scoringstrats = ["NP", "LP", "EP"]
        self.module.set_parameter("scoringstrat", scoringstrats[int(self.ui.scoring_strat_combo.currentIndex())])

        if self.ui.scoring_method_combo.currentIndex() == 0:
            self.module.set_parameter("scoringmethod", "WPM")
        else:
            self.module.set_parameter("scoringmethod", "WSM")

        self.module.set_parameter("includestoch", int(self.ui.scoring_method_check.isChecked()))
        self.module.set_parameter("multifunction_bonus", float(self.ui.scoring_multifunction_spin.value()))

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
