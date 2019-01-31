# -*- coding: utf-8 -*-
"""
@file   md_urbplanbbguic.py
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
import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from md_urbdevelop import Ui_Urbandev_Dialog


# --- MAIN GUI FUNCTION ---
class UrbdevelopGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Urbandev_Dialog()
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
        # simyears = self.active_scenario.get_simulation_years()  # gets the simulation years
        # if len(simyears) > 1:
        #     self.ui.year_combo.setEnabled(1)  # if more than one year, enables the box for selection
        #     self.ui.autofillButton.setEnabled(1)
        #     self.ui.same_params.setEnabled(1)
        #     self.ui.year_combo.clear()
        #     for yr in simyears:
        #         self.ui.year_combo.addItem(str(yr))
        # else:
        #     self.ui.autofillButton.setEnabled(0)  # if static or benchmark, then only one year is available
        #     self.ui.same_params.setEnabled(0)  # so all of the sidebar buttons get disabled.
        #     self.ui.year_combo.setEnabled(0)
        #     self.ui.year_combo.clear()
        #     self.ui.year_combo.addItem(str(simyears[0]))
        # self.ui.year_combo.setCurrentIndex(0)  # Set to the first item on the list.

        # --- SETUP ALL DYNAMIC COMBO BOXES ---

        # --- SIGNALS AND SLOTS ---


    def adjust_module_img(self):
        """Changes the module's image based on the currently selected tab in the GUI."""
        pass


    def get_dataref_array(self, dataclass, datatype, *args):
        """Retrieves a list of data files loaded into the current scenario for display in the GUI

        :param dataclass: the data class i.e. spatial, temporal, qualitative
        :param datatype: the name that goes with the data class e.g. landuse, population, etc.
        """

        return True

    def pre_fill_parameters(self):
        """Pre-filling method, will set up the module with all values contained in the pre-loaded parameter file or
        settings. This method is called when the Combo box index is changed or a file has been browsed and entered into
        the text box on the GENERALS tab."""
        pass    # [TO DO]

    def change_active_module(self):
        """Searches for the active module based on the simulation year combo box and updates the GUI."""
        return True

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""

        # END OF FILING IN GUI VALUES
        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""

        return True
