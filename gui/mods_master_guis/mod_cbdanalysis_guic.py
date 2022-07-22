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

        # Country Combo box
        self.ui.country_combo.clear()
        self.ui.country_combo.addItem("(select country)")
        countrynames = list(self.maingui.cities_dict.keys())
        countrynames.sort()
        [self.ui.country_combo.addItem(i) for i in countrynames]
        self.ui.country_combo.setCurrentIndex(0)

        countryname = self.simulation.get_project_parameter("country")
        if countryname == "(select country)":
            self.ui.country_combo.setCurrentIndex(0)
        else:
            self.ui.country_combo.setCurrentIndex(countrynames.index(countryname)+1)

        # City Combo
        self.update_city_combo()

        # --- SIGNALS AND SLOTS ---
        self.ui.country_combo.currentIndexChanged.connect(self.update_city_combo)
        self.ui.cbdknown_radio.clicked.connect(self.enable_disable_guis)
        self.ui.cbdmanual_radio.clicked.connect(self.enable_disable_guis)
        self.ui.add.clicked.connect(self.add_to_cbd_table)
        self.ui.remove.clicked.connect(self.remove_from_cbd_table)
        self.ui.reset.clicked.connect(self.reset_button_action)
        self.ui.ignore_distance_check.clicked.connect(self.enable_disable_guis)

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

    def add_to_cbd_table(self):
        """Adds the current entry to the urban centres table, updating the information"""
        if self.ui.cbdknown_radio.isChecked() and self.ui.city_combo.currentText != "(select city)":
            country = self.ui.country_combo.currentText()
            cityname = self.ui.city_combo.currentText()
            coords = self.maingui.cities_dict[country][cityname]
        elif self.ui.cbdmanual_radio.isChecked() and self.ui.cbdlat_box != "" and self.ui.cbdlong_box != "":
            cityname = self.ui.cbdname_line.text()
            coords = (self.ui.cbdlat_box.text(), self.ui.cbdlong_box.text())
        else:
            prompt_msg = "Please enter a valid city, either through the dropdown menus or with correct lat/long info."
            QtWidgets.QMessageBox.warning(self, "No urban area specified", prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        # Check for duplicates
        for row in range(self.ui.urbanareas_table.rowCount()):
            if self.ui.urbanareas_table.item(row, 0).text() == cityname:
                prompt_msg = "A city with the same name already exists in the list, please select another city."
                QtWidgets.QMessageBox.warning(self, "Duplicate city name", prompt_msg, QtWidgets.QMessageBox.Ok)
                return True

        self.ui.urbanareas_table.insertRow(self.ui.urbanareas_table.rowCount())
        metadata = [cityname, coords[0], coords[1]]
        for i in range(len(metadata)):
            twi = QtWidgets.QTableWidgetItem()
            twi.setText(str(metadata[i]))
            self.ui.urbanareas_table.setItem(self.ui.urbanareas_table.rowCount()-1, i, twi)
        self.ui.urbanareas_table.resizeColumnsToContents()
        self.ui.urbanareas_table.verticalHeader().stretchLastSection()

        # Reset GUI elements
        self.ui.city_combo.setCurrentIndex(0)
        self.ui.cbdname_line.clear()
        self.ui.cbdlat_box.clear()
        self.ui.cbdlong_box.clear()
        return True

    def remove_from_cbd_table(self):
        """Removes the currently selected row from the urban centres table."""
        self.ui.urbanareas_table.removeRow(self.ui.urbanareas_table.currentRow())

    def reset_button_action(self):
        """Called when the reset button is pressed to reset the urban areas table."""
        prompt_msg = "Do you wish to reset the table of urban areas?"
        answer = QtWidgets.QMessageBox.question(self, "Reset Table?", prompt_msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if answer == QtWidgets.QMessageBox.Yes:
            self.reset_cbd_table()
        return True

    def reset_cbd_table(self):
        """Resets the table completely."""
        self.ui.urbanareas_table.setRowCount(0)

    def update_city_combo(self):
        """Updates the city combo, called upon opening the GUI but also when the country combo is updated."""
        self.ui.city_combo.clear()
        self.ui.city_combo.addItem("(select city)")
        countryname = self.ui.country_combo.currentText()
        if countryname == "(select country)":
            self.ui.city_combo.setCurrentIndex(0)
        else:
            citynames = list(self.maingui.cities_dict[countryname].keys())
            citynames.sort()
            [self.ui.city_combo.addItem(i) for i in citynames]
            self.ui.city_combo.setCurrentIndex(0)
        return True

    def enable_disable_guis(self):
        """Enables and disables elements of the GUI depending on conditions."""
        if self.ui.cbdknown_radio.isChecked():
            self.ui.country_combo.setEnabled(1)
            self.ui.city_combo.setEnabled(1)
            self.ui.cbdname_line.setEnabled(0)
            self.ui.cbdlat_box.setEnabled(0)
            self.ui.cbdlong_box.setEnabled(0)
        else:
            self.ui.country_combo.setEnabled(0)
            self.ui.city_combo.setEnabled(0)
            self.ui.cbdname_line.setEnabled(1)
            self.ui.cbdlat_box.setEnabled(1)
            self.ui.cbdlong_box.setEnabled(1)
        self.ui.ignore_distance_spin.setEnabled(self.ui.ignore_distance_check.isChecked())

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        self.ui.cbdknown_radio.setChecked(1)        # Always set default for use to select from dropdown

        cbdlist = self.module.get_parameter("cbdlist")
        self.ui.urbanareas_table.setRowCount(0)
        for i in range(len(cbdlist)):
            self.ui.urbanareas_table.insertRow(self.ui.urbanareas_table.rowCount())
            for j in cbdlist[i]:
                twi = QtWidgets.QTableWidgetItem()
                twi.setText(cbdlist[i][j])
                self.ui.urbanareas_table.setItem(self.ui.urbanareas_table.rowCount() - 1, j, twi)

        self.ui.ignore_distance_check.setChecked(int(self.module.get_parameter("ignorebeyond")))
        self.ui.ignore_distance_spin.setValue(float(self.module.get_parameter("ignoredist")))
        self.ui.construct_gradient_check.setChecked(int(self.module.get_parameter("popgradient")))
        self.ui.generate_map_check.setChecked(int(self.module.get_parameter("proximitymap")))

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        cbdlist = []
        for i in range(self.ui.urbanareas_table.rowCount()):
            cityname = self.ui.urbanareas_table.item(i, 0).text()
            lat = self.ui.urbanareas_table.item(i, 1).text()
            long = self.ui.urbanareas_table.item(i, 2).text()
            cbdlist.append([cityname, lat, long])
        self.module.set_parameter("cbdlist", cbdlist)

        self.module.set_parameter("ignorebeyond", int(self.ui.ignore_distance_check.isChecked()))
        self.module.set_parameter("ignoredist", float(self.ui.ignore_distance_spin.value()))
        self.module.set_parameter("popgradient", int(self.ui.construct_gradient_check.isChecked()))
        self.module.set_parameter("proximitymap", int(self.ui.generate_map_check.isChecked()))

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

        # (2) If there are no urban areas to conduct the analysis on, then the module will not run.
        if self.ui.urbanareas_table.rowCount() == 0:
            prompt_msg = "No urban areas defined, module will not run!"
            QtWidgets.QMessageBox.warning(self, "No urban areas defined", prompt_msg, QtWidgets.QMessageBox.Ok)

        return True
