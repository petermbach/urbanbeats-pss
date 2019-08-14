# -*- coding: utf-8 -*-
"""
@file   urbanbeatsresultsguic.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2018  Peter M. Bach

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

# --- CODE STRUCTURE ---
#       (1) Preferences Dialog
#       (2)
#
# --- --- --- --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import sys
import os
import webbrowser
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ubdatalibrary as ubdatalibrary
import model.ublibs.ubspatial as ubspatial

from urbanbeatsresults import Ui_ResultsExplorer

# --- ADD DATA DIALOG ---
class LaunchResultsExplorer(QtWidgets.QDialog):
    """Class definition for the add data dialog window for importing and managing data."""
    def __init__(self, main, simulation, datalibrary, parent=None):
        """Class constructor, references the data library object active in the simulation as well as the main
        runtime class.

        :param main: referring to the main GUI so that changes can be made in real-time to the main interface
        :param datalibrary: the data library object, which will be updated as data files are added to the project.
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_ResultsExplorer()
        self.ui.setupUi(self)

        # --- INITIALIZE MAIN VARIABLES ---
        self.maingui = main    # the main runtime - for GUI changes
        self.simulation = simulation
        self.datalibrary = datalibrary      # the simulation object's data library

        # Update the category and sub-category combo boxes
        self.clear_explorer()
        self.update_all_scenario_combos()

        # --- SIGNALS AND SLOTS ---
        self.ui.summary_scenario_combo.currentIndexChanged.connect(self.update_summary_tab)
        self.ui.map_scenario_combo.currentIndexChanged.connect(self.update_map_tab)
        self.ui.networks_scenario_combo.currentIndexChanged.connect(self.update_networks_tab)
        self.ui.stats_scenario_combo.currentIndexChanged.connect(self.update_stats_tab)
        self.ui.correl_scenario_combo.currentIndexChanged.connect(self.update_correl_tab)
        self.ui.compare_scenarioA_combo.currentIndexChanged.connect(self.update_compare_tab)
        self.ui.compare_scenarioB_combo.currentIndexChanged.connect(self.update_compare_tab)

    def clear_explorer(self):
        self.ui.compare_results_tree.clear()
        self.ui.correl_results_tree.clear()
        self.ui.map_results_tree.clear()
        self.ui.networks_results_tree.clear()
        self.ui.stats_results_tree.clear()
        self.ui.summary_results_tree.clear()

    def update_all_scenario_combos(self):
        """Adds the model's scenarios to the combo boxes."""
        scenarionames = self.simulation.get_all_scenario_names()
        self.ui.summary_scenario_combo.clear()      # Clear the combo box
        self.ui.summary_scenario_combo.addItem("<Select Scenario>")
        [self.ui.summary_scenario_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]

        self.ui.map_scenario_combo.clear()  # Clear the combo box
        self.ui.map_scenario_combo.addItem("<Select Scenario>")
        [self.ui.map_scenario_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]

        self.ui.networks_scenario_combo.clear()  # Clear the combo box
        self.ui.networks_scenario_combo.addItem("<Select Scenario>")
        [self.ui.networks_scenario_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]

        self.ui.stats_scenario_combo.clear()  # Clear the combo box
        self.ui.stats_scenario_combo.addItem("<Select Scenario>")
        [self.ui.stats_scenario_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]

        self.ui.correl_scenario_combo.clear()  # Clear the combo box
        self.ui.correl_scenario_combo.addItem("<Select Scenario>")
        [self.ui.correl_scenario_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]

        self.ui.compare_scenarioA_combo.clear()  # Clear the combo box
        self.ui.compare_scenarioA_combo.addItem("<Select Scenario>")
        [self.ui.compare_scenarioA_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]

        self.ui.compare_scenarioB_combo.clear()  # Clear the combo box
        self.ui.compare_scenarioB_combo.addItem("<Select Scenario>")
        [self.ui.compare_scenarioB_combo.addItem(str(scenarionames[i])) for i in range(len(scenarionames))]
        return True

    def update_summary_tab(self):
        pass

    def update_map_tab(self):
        pass

    def update_networks_tab(self):
        pass

    def update_stats_tab(self):
        pass

    def update_correl_tab(self):
        pass

    def update_compare_tab(self):
        pass

