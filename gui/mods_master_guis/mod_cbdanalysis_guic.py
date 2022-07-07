r"""
@file   mod_cbdanalysis_guic.py
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
from .mod_cbdanalysis_gui import Ui_UrbanCentralityGui

# --- MAIN GUI FUNCTION ---
class UrbanCentralityAnalysisLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Regional Analysis"
    catorder = 1
    longname = "Urban Centrality Analysis"
    icon = ":/icons/City_icon_(Noun_Project).svg.png"

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
        self.ui = Ui_UrbanCentralityGui()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main  # the main runtime
        self.simulation = simulation  # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog
        self.metadata = None

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


        # --- SIGNALS AND SLOTS ---
        # self.ui.lu_combo.currentIndexChanged.connect(self.update_land_use_attributes)
        # self.ui.lureclass_check.clicked.connect(self.refresh_lu_reclassification_widgets)
        # self.ui.lureclass_save_button.clicked.connect(self.save_current_reclassification)
        # self.ui.lureclass_load_button.clicked.connect(self.load_reclassification)
        # self.ui.lureclass_reset_button.clicked.connect(self.reset_reclassification)
        # self.ui.single_landuse_check.clicked.connect(self.enable_disable_guis)

        # --- RUNTIME SIGNALS AND SLOTS ---
        # self.accepted.connect(self.save_values)
        # self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        # self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        # self.ui.lureclass_table.setRowCount(0)
        # self.setup_gui_with_parameters()
        # self.enable_disable_guis()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")



    def enable_disable_guis(self):
        self.ui.lureclass_table.setEnabled(self.ui.lureclass_check.isChecked())
        self.ui.lureclass_widget.setEnabled(self.ui.lureclass_check.isChecked())
        self.ui.patchdelin_check.setEnabled(not self.ui.single_landuse_check.isChecked())
        self.ui.spatialmetrics_check.setEnabled(not self.ui.single_landuse_check.isChecked())

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # Combo Boxes
        # try:
        #     self.ui.lu_combo.setCurrentIndex(
        #         self.lumaps[1].index(self.module.get_parameter("landusemapid")))
        # except:
        #     self.ui.lu_combo.setCurrentIndex(0)
        #
        # self.ui.luattr_combo.setCurrentIndex(0)
        # if self.ui.lu_combo.currentIndex() != 0:
        #     attname = self.module.get_parameter("landuseattr")
        #     for i in range(self.ui.luattr_combo.count()):
        #         if self.ui.luattr_combo.itemText(i) == attname:
        #             self.ui.luattr_combo.setCurrentIndex(i)
        # else:
        #     self.ui.lureclass_table.setRowCount(0)
        #
        # # Reclassification Table
        # self.ui.lureclass_check.setChecked(self.module.get_parameter("lureclass"))
        # if self.ui.lureclass_check.isChecked() and self.ui.luattr_combo.currentIndex() != 0:
        #     # Populate Table with reclassification system...
        #     self.refresh_lu_reclassification_widgets()
        #     reclass = self.module.get_parameter("lureclasssystem")
        #     self.classify_table(reclass)
        #
        # self.ui.single_landuse_check.setChecked(self.module.get_parameter("singlelu"))
        # self.ui.patchdelin_check.setChecked(self.module.get_parameter("patchdelin"))
        # self.ui.spatialmetrics_check.setChecked(self.module.get_parameter("spatialmetrics"))

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        pass
        # self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())
        # self.module.set_parameter("landusemapid", self.lumaps[1][self.ui.lu_combo.currentIndex()])
        # self.module.set_parameter("landuseattr", self.ui.luattr_combo.currentText())
        #
        # self.module.set_parameter("lureclass", int(self.ui.lureclass_check.isChecked()))
        #
        # # Reclassification scheme
        # if self.ui.lureclass_check.isChecked():
        #     self.module.set_parameter("lureclasssystem", self.generate_reclassification_dict())
        # else:
        #     self.module.set_parameter("lureclasssystem", {})
        #
        # self.module.set_parameter("singlelu", int(self.ui.single_landuse_check.isChecked()))
        # self.module.set_parameter("patchdelin", int(self.ui.patchdelin_check.isChecked()))
        # self.module.set_parameter("spatialmetrics", int(self.ui.spatialmetrics_check.isChecked()))

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
