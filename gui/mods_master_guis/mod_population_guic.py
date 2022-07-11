r"""
@file   mod_population_gui.py
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
import model.progref.ubglobals as ubglobals
import model.ublibs.ubspatial as ubspatial

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_population_gui import Ui_Map_Population


# --- MAIN GUI FUNCTION ---
class PopulationLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 4
    longname = "Map Population"
    icon = ":/icons/demographics.png"

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
        self.ui = Ui_Map_Population()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
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
        # Boundary combo box
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

        # Population Combo Box
        self.ui.pop_combo.clear()
        self.popmaps = self.datalibrary.get_dataref_array("spatial", ["Demographic"],
                                                          subtypes="Population", scenario=self.active_scenario_name)
        if len(self.popmaps[0]) == 0:
            self.ui.pop_combo.addItem(str("(no population maps in project)"))
        else:
            [self.ui.pop_combo.addItem(str(self.popmaps[0][i])) for i in range(len(self.popmaps[0]))]

        # Land use Combo Box
        self.ui.lumap_combo.clear()
        self.lumaps = self.datalibrary.get_dataref_array("spatial", ["Land Use/Cover"],
                                                         subtypes="Land Use", scenario=self.active_scenario_name)

        if len(self.lumaps[0]) == 0:
            self.ui.lumap_combo.addItem(str("(no land use maps in project)"))
        else:
            [self.ui.lumap_combo.addItem(str(self.lumaps[0][i])) for i in range(len(self.lumaps[0]))]

        # --- SIGNALS AND SLOTS ---
        self.ui.assetcol_combo.currentIndexChanged.connect(self.update_asset_col_metadata)
        self.ui.pop_combo.currentIndexChanged.connect(self.update_pop_attributes_combo)
        self.ui.lumap_combo.currentIndexChanged.connect(self.update_lu_attributes_combo)
        self.ui.pop_correct_check.clicked.connect(self.enable_disable_guis)
        self.ui.pop_correct_auto.clicked.connect(self.enable_disable_guis)
        self.ui.popspatial_landuse_check.clicked.connect(self.enable_disable_guis)
        self.ui.popspatial_landuse_check.clicked.connect(self.update_lu_attributes_combo)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.update_pop_attributes_combo()
        self.update_lu_attributes_combo()
        self.setup_gui_with_parameters()
        self.enable_disable_guis()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def update_pop_attributes_combo(self):
        """Updates the attributes combo box with the attributes in the shapefile if the combobox map selected is a
        shapefile format, otherwise leaves disabled."""
        self.ui.popattr_combo.clear()
        if ".shp" in self.ui.pop_combo.currentText():
            dataref = self.datalibrary.get_data_with_id(self.popmaps[1][self.ui.pop_combo.currentIndex()])
            filepath = dataref.get_data_file_path() + self.ui.pop_combo.currentText()
            fileprops = ubspatial.load_shapefile_details(filepath)
            self.ui.popattr_combo.addItem("(attribute name)")
            for i in fileprops[8]:
                self.ui.popattr_combo.addItem(i)
            self.ui.popattr_combo.setCurrentIndex(0)
            self.ui.popattr_combo.setEnabled(1)
        else:
            self.ui.popattr_combo.addItem("(not a shapefile)")
            self.ui.popattr_combo.setCurrentIndex(0)
            self.ui.popattr_combo.setEnabled(0)

    def update_lu_attributes_combo(self):
        """Updates the attributes combo box with the attributes in the shapefile if the combobox map selected is a
        shapefile format, otherwise leaves disabled."""
        self.ui.lumap_attr_combo.clear()
        if ".shp" in self.ui.lumap_combo.currentText():
            dataref = self.datalibrary.get_data_with_id(self.lumaps[1][self.ui.lumap_combo.currentIndex()])
            filepath = dataref.get_data_file_path() + self.ui.lumap_combo.currentText()
            fileprops = ubspatial.load_shapefile_details(filepath)
            self.ui.lumap_attr_combo.addItem("(attribute name)")
            for i in fileprops[8]:
                self.ui.lumap_attr_combo.addItem(i)
            self.ui.lumap_attr_combo.setCurrentIndex(0)
            self.ui.lumap_attr_combo.setEnabled(1)
        else:
            self.ui.lumap_attr_combo.addItem("(not a shapefile)")
            self.ui.lumap_attr_combo.setCurrentIndex(0)
            self.ui.lumap_attr_combo.setEnabled(0)

    def enable_disable_guis(self):
        """Enables and disables items in the GUI based on conditions."""
        if self.ui.pop_correct_check.isChecked():
            self.ui.pop_correct_spin.setEnabled(not self.ui.pop_correct_auto.isChecked())
            self.ui.pop_correct_auto.setEnabled(1)
        else:
            self.ui.pop_correct_spin.setEnabled(0)
            self.ui.pop_correct_auto.setEnabled(0)
        if self.ui.popspatial_landuse_check.isChecked():
            self.ui.lumap_combo.setEnabled(1)
            self.update_lu_attributes_combo()
        else:
            self.ui.lumap_combo.setEnabled(0)
            self.ui.lumap_attr_combo.setEnabled(0)

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        try:    # Population data combo
            self.ui.pop_combo.setCurrentIndex(
                self.popmaps[1].index(self.module.get_parameter("popmapdataid")))
        except ValueError:
            self.ui.pop_combo.setCurrentIndex(0)

        # Attributes Combobox

        if self.module.get_parameter("popdataformat") == "DEN":
            self.ui.popdata_densityradio.setChecked(1)
        else:
            self.ui.popdata_totalradio.setChecked(1)

        self.ui.pop_correct_check.setChecked(int(self.module.get_parameter("applypopcorrect")))
        self.ui.pop_correct_spin.setValue(float(self.module.get_parameter("popcorrectfact")))
        self.ui.pop_correct_auto.setChecked(int(self.module.get_parameter("popcorrectauto")))
        self.ui.popspatial_landuse_check.setChecked(int(self.module.get_parameter("mappoptolanduse")))

        try:    # Land use data combo
            self.ui.lumap_combo.setCurrentIndex(
                self.lumaps[1].index(self.module.get_parameter("landusemapdataid")))
        except ValueError:
            self.ui.lumap_combo.setCurrentIndex(0)

        # Attributes Combo box

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())
        self.module.set_parameter("popmapdataid", self.popmaps[1][self.ui.pop_combo.currentIndex()])
        self.module.set_parameter("popdataattr", self.ui.popattr_combo.currentText())

        if self.ui.popdata_densityradio.isChecked():
            self.module.set_parameter("popdataformat", "DEN")
        else:
            self.module.set_parameter("popdataformat", "TOT")

        self.module.set_parameter("applypopcorrect", int(self.ui.pop_correct_check.isChecked()))
        self.module.set_parameter("popcorrectfact", float(self.ui.pop_correct_spin.value()))
        self.module.set_parameter("popcorrectauto", int(self.ui.pop_correct_auto.isChecked()))
        self.module.set_parameter("mappoptolanduse", int(self.ui.popspatial_landuse_check.isChecked()))

        if self.ui.lumap_combo.currentText() == "(no land use maps in project)":
            self.module.set_parameter("landusemapdataid", "")
        else:
            self.module.set_parameter("landusemapdataid", self.lumaps[1][self.ui.lumap_combo.currentIndex()])
        self.module.set_parameter("landuseattr", self.ui.lumap_attr_combo.currentText())

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

        # (2) Population map not selected
        if self.ui.pop_combo.currentText() == "(no population maps in project)":
            prompt_msg = "Please load a population map into the project to be mapped!"
            QtWidgets.QMessageBox.warning(self, "Missing Population Map", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        # (3) Land use to be used but no map present
        if self.ui.popspatial_landuse_check.isChecked() and self.ui.lumap_combo.currentText() == \
                "(no land use maps in project)":
            prompt_msg = "Please load a land use map into the project if this is to be used to guide population " \
                         "mapping!"
            QtWidgets.QMessageBox.warning(self, "Missing Land Use Map", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        # (4) Population attribute selected
        if ".shp" in self.ui.pop_combo.currentText() and self.ui.popattr_combo.currentIndex() == 0:
            prompt_msg = "Your population map is a shapefile with attributes, please select the attribute that" \
                         "UrbanBEATS should use for population data."
            QtWidgets.QMessageBox.warning(self, "No attribute selected for Population Data",
                                          prompt_msg, QtWidgets.QMessageBox.Ok)
            return False

        # (5) If Land use included, a correctly selected attribute
        if self.ui.popspatial_landuse_check.isChecked() and ".shp" in self.ui.lumap_combo.currentText() and (
                self.ui.lumap_attr_combo.currentIndex() == 0):
            prompt_msg = "You are using a land use map of shapefile format to guide population mapping. It requires " \
                         "that you select an attribute containing the land use classification."
            QtWidgets.QMessageBox.warning(self, "No Land Use Map attribute selected.",
                                          prompt_msg, QtWidgets.QMessageBox.Ok)
            return False
        # If all tests pass, then the module can be run.
        return True