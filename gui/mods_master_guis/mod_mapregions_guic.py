r"""
@file   mod_mapregions_guic.py
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
import random

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ublibs.ubspatial as ubspatial

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.observers import ProgressBarObserver
from .mod_mapregions_gui import Ui_Map_Regions


# --- MAIN GUI FUNCTION ---
class MapRegionsLaunch(QtWidgets.QDialog):
    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 2
    longname = "Map Regions"
    icon = ":/icons/admin_border.png"

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
        self.ui = Ui_Map_Regions()
        self.ui.setupUi(self)
        random.seed()

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
        self.datalibrary = datalibrary
        self.log = simlog

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
            if mode != 1:   # Standalone
                if simgrids[n].get_container_type() == "Standalone":
                    self.ui.assetcol_combo.addItem(str(n))
                self.ui.assetcol_combo.setEnabled(1)
            else:
                self.ui.assetcol_combo.addItem(
                    self.active_scenario.get_asset_collection_container().get_container_name())
                self.ui.assetcol_combo.setEnabled(0)
        self.update_asset_col_metadata()

        # Boundaries Combo Box
        self.reset_combos()

        # --- RESET TABLE ---
        self.ui.boundarytable.setRowCount(0)

        # --- SIGNALS AND SLOTS ---
        self.ui.boundarycat_combo.currentIndexChanged.connect(self.update_boundary_combos)
        self.ui.boundary_combo.currentIndexChanged.connect(self.update_boundary_attributes)
        self.ui.boundaryatt_combo.currentIndexChanged.connect(self.enable_final_boundary_widgets)
        self.boundarymaps = []
        self.ui.add.clicked.connect(self.add_boundary_info_to_table)
        self.ui.remove.clicked.connect(self.remove_current_selection_from_table)
        self.ui.reset.clicked.connect(self.reset_boundarytable)

        # --- RUNTIME SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.run_button.clicked.connect(self.run_module_in_runtime)
        self.progressbarobserver.updateProgress[int].connect(self.update_progress_bar_value)

        # --- SETUP GUI PARAMETERS ---
        self.setup_gui_with_parameters()

    def update_asset_col_metadata(self):
        """Whenever the asset collection name is changed, then update the current metadata info"""
        assetcol = self.simulation.get_asset_collection_by_name(self.ui.assetcol_combo.currentText())
        if assetcol is None:
            self.metadata = None
        else:
            self.metadata = assetcol.get_asset_with_name("meta")

    def update_boundary_combos(self):
        """Updates maps in the boundary combo depending on which category has been selected. Resets if no category."""
        self.ui.boundary_combo.setEnabled(1)
        self.ui.boundary_combo.clear()
        self.ui.boundary_combo.addItem("(select Map)")
        if self.ui.boundarycat_combo.currentIndex() == 0:
            self.reset_combos()
            return True
        elif self.ui.boundarycat_combo.currentIndex() == 1:     # Jurisdictional
            self.boundarymaps = self.datalibrary.get_dataref_array("spatial", ["Boundaries"], subtypes="Geopolitical",
                                                                   scenario=self.active_scenario_name)
        elif self.ui.boundarycat_combo.currentIndex() == 2:     # Suburban
            self.boundarymaps = self.datalibrary.get_dataref_array("spatial", ["Boundaries"], subtypes="Suburban",
                                                                   scenario=self.active_scenario_name)
        else:
            self.boundarymaps = self.datalibrary.get_dataref_array("spatial", ["Boundaries"], subtypes="Planning Zones",
                                                                   scenario=self.active_scenario_name)
        if len(self.boundarymaps) != 0:
            [self.ui.boundary_combo.addItem(str(self.boundarymaps[0][i])) for i in range(len(self.boundarymaps[0]))]
        return True

    def update_boundary_attributes(self):
        """Updates the attributes combo box for the boundaries. Called when a map is selected."""
        if self.ui.boundary_combo.currentIndex() <= 0:      # .clear() sets the index to -1, otherwise we set to 0
            return True
        else:   # It is a map, grab its shapefile information and fill the attributes list
            self.ui.boundaryatt_combo.clear()
            self.ui.boundaryatt_combo.addItem("(select attribute name for labelling)")
            dataref = self.datalibrary.get_data_with_id(self.boundarymaps[1][self.ui.boundary_combo.currentIndex()-1])
            filepath = dataref.get_data_file_path() + self.ui.boundary_combo.currentText()
            fileprops = ubspatial.load_shapefile_details(filepath)
            for i in fileprops[8]:
                self.ui.boundaryatt_combo.addItem(i)
            self.ui.boundaryatt_combo.setCurrentIndex(0)
            self.ui.boundaryatt_combo.setEnabled(1)
        pass

    def enable_final_boundary_widgets(self):
        """Enables the final widgets knowing that an attribute was selected in the attributes combo. This walks the
        user through the full interface."""
        if self.ui.boundaryatt_combo.currentIndex() <= 0:
            self.ui.simgrid_label_line.setEnabled(0)
            self.ui.stakeholder_check.setEnabled(0)
            self.ui.add.setEnabled(0)
        else:
            self.ui.simgrid_label_line.setEnabled(1)
            self.ui.stakeholder_check.setEnabled(1)
            self.ui.add.setEnabled(1)

    def reset_combos(self):
        self.ui.boundarycat_combo.setCurrentIndex(0)  # 1 = Jurisdictional, 2 = Suburban, 3 = Planning
        self.ui.boundary_combo.clear()
        self.ui.boundary_combo.addItem("(select Map)")
        self.ui.boundary_combo.setCurrentIndex(0)
        self.ui.boundary_combo.setEnabled(0)
        self.ui.boundaryatt_combo.clear()
        self.ui.boundaryatt_combo.addItem("(select attribute name for labelling)")
        self.ui.boundaryatt_combo.setCurrentIndex(0)
        self.ui.boundaryatt_combo.setEnabled(0)
        self.ui.simgrid_label_line.setEnabled(0)
        self.ui.stakeholder_check.setChecked(0)
        self.ui.stakeholder_check.setEnabled(0)
        self.ui.add.setEnabled(0)

    def add_boundary_info_to_table(self):
        """Adds the current details to the table as a new entry for boundary mapping."""
        catlabel = self.ui.boundarycat_combo.currentText()[0]+"_"+str(self.ui.simgrid_label_line.text()) # J_, S_ or P_
        stakeholder = int(self.ui.stakeholder_check.isChecked())
        datafilename = self.ui.boundary_combo.currentText()
        attribute = self.ui.boundaryatt_combo.currentText()
        self.add_tabledata(catlabel, stakeholder, datafilename, attribute)
        self.reset_combos()

    def add_tabledata(self, label, stakeholder, datafile, attname):
        """Called with the relevant info to populate the data table. Called either by setting up the GUI or pressing the
        add button."""
        if stakeholder == 1:
            sh = "Yes"
            pixmaps = [":/icons/man.png", ":/icons/woman.png", ":/icons/owl.png", ":/icons/frog.png"]
            icon = pixmaps[random.randint(0, 3)]
            twiicon = QtGui.QIcon()
            twiicon.addPixmap(QtGui.QPixmap(icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            sh = "No"

        self.ui.boundarytable.insertRow(self.ui.boundarytable.rowCount())  # Insert row below
        metadata = [label, sh ,datafile, attname]
        for i in range(len(metadata)):
            twi = QtWidgets.QTableWidgetItem()
            twi.setText(str(metadata[i]))
            if stakeholder == 1 and i == 1:
                twi.setIcon(twiicon)
            self.ui.boundarytable.setItem(self.ui.boundarytable.rowCount()-1, i, twi)
        self.ui.boundarytable.resizeColumnsToContents()
        self.ui.boundarytable.verticalHeader().stretchLastSection()

    def remove_current_selection_from_table(self):
        """Removes the actively selected boundary entry in the table from the table."""
        self.ui.boundarytable.removeRow(self.ui.boundarytable.currentRow())

    def reset_boundarytable(self):
        """Removes all rows from the boundary table. Resets the combo boxes"""
        prompt_msg = "Do you wish to reset the list of regions to map?"
        answer = QtWidgets.QMessageBox.question(self, "Reset Table?", prompt_msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if answer == QtWidgets.QMessageBox.Yes:
            self.ui.boundarytable.setRowCount(0)
            self.reset_combos()
        else:
            return True

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        tabledata = self.module.get_parameter("boundaries_to_map")
        self.ui.boundarytable.setRowCount(0)
        for row in tabledata:
            self.add_tabledata(row["label"], row["stakeholder"], row["datafile"], row["attname"])

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        self.module.set_parameter("assetcolname", self.ui.assetcol_combo.currentText())

        self.module.reset_boundaries_to_map()
        for i in range(self.ui.boundarytable.rowCount()):
            metadata = []
            for j in range(self.ui.boundarytable.columnCount()):
                metadata.append(self.ui.boundarytable.item(i, j).text())
            if metadata[1] == "Yes":
                stakeholder = 1
            else:
                stakeholder = 0
            self.module.add_boundary_to_map(metadata[0], metadata[2], metadata[3], stakeholder)

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
        # (1) Are there items in the boundary table to map?
        if self.ui.assetcol_combo.currentIndex() == 0:
            prompt_msg = "Please select an Asset Collection to use for this simulation!"
            QtWidgets.QMessageBox.warning(self, "No Asset Collection selected", prompt_msg, QtWidgets.QMessageBox.Ok)
            return False
        return True