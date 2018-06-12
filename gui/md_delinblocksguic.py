# -*- coding: utf-8 -*-
"""
@file   md_delinblocksguic.py
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

# --- PYTHON LIBRARY IMPORTS ---

# --- URBANBEATS LIBRARY IMPORTS ---

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from md_delinblocksgui import Ui_Delinblocks_Dialog


# --- MAIN GUI FUNCTION ---
class DelinBlocksGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The active simulation object
        :param scenario:
        :param datalibrary:
        :param simlog:
        :param parent:
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Delinblocks_Dialog()
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

        # --- SIMULATION YEAR SETTINGS ---
        simyears = self.active_scenario.get_simulation_years()  # gets the simulation years
        if len(simyears) > 1:
            self.ui.year_combo.setEnabled(1)        # if more than one year, enables the box for selection
            self.ui.autofillButton.setEnabled(1)
            self.ui.same_params.setEnabled(1)
            self.ui.year_combo.clear()
            for yr in simyears:
                self.ui.year_combo.addItem(str(yr))
        else:
            self.ui.autofillButton.setEnabled(0)    # if static or benchmark, then only one year is available
            self.ui.same_params.setEnabled(0)       # so all of the sidebar buttons get disabled.
            self.ui.year_combo.setEnabled(0)
            self.ui.year_combo.clear()
            self.ui.year_combo.addItem(str(simyears[0]))

        self.gui_state = "initial"
        self.change_active_module()
        self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---
        self.ui.year_combo.currentIndexChanged.connect(self.change_active_module)
        self.ui.reset_button.clicked.connect(self.reset_parameters_to_default)

    def reset_parameters_to_default(self):
        """Resets all parameters of the current module instance back to default values."""
        pass

    def change_active_module(self):
        """Searches for the active module based on the simulation year combo box and updates the GUI."""
        if self.gui_state != "initial":
            self.update_module_parameters()     # Saves the current parameters
        self.module = self.active_scenario.get_module_object("SPATIAL", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()

    def setup_gui_with_parameters(self):
        """Sets all parameters in the GUI based on the current year."""
        # --- INPUT MAPS TAB ---

        # --- GEOMETRIC REPRESENTATION TAB ---

        # --- SPATIAL CONTEXT TAB ---
        pass

    def update_module_parameters(self):
        """Saves the active values"""
        pass

    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        pass