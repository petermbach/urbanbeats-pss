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
from md_urbplanbbgui import Ui_Urbplanbb_Dialog


# --- MAIN GUI FUNCTION ---
class UrbplanbbGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Block Delineation GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Urbplanbb_Dialog()
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
        self.pixmap_ref = [":/images/images/md_urbplanbb_general.jpg",
                           ":/images/images/md_urbplanbb_residential.jpg",
                           ":/images/images/md_urbplanbb_nonres.jpg",
                           ":/images/images/md_urbplanbb_roads.jpg",
                           ":/images/images/md_urbplanbb_openspaces.jpg",
                           ":/images/images/md_urbplanbb_others.jpg"]
        self.adjust_module_img()

        self.set_module_parameters()

        # --- SIGNALS AND SLOTS ---
        self.ui.parameters.currentChanged.connect(self.adjust_module_img)   # Changes the module's image
        self.ui.buttonBox.accepted.connect(self.save_values)

    def adjust_module_img(self):
        """Changes the module's image based on the currently selected tab in the GUI."""
        self.ui.module_img.setPixmap(QtGui.QPixmap(self.pixmap_ref[self.ui.parameters.currentIndex()]))

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""
        # TAB 1 - GENERAL PARAMETERS

        # TAB 2 - RESIDENTIAL PLANNING PARAMETERS

        # TAB 3 - NON-RESIDENTIAL PLANNING PARAMETERS

        # TAB 4 - TRANSPORT PLANNING PARAMETERS

        # TAB 5 - OPEN SPACES PLANNING PARAMETERS

        # TAB 6 - OTHER LAND USES
        pass

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        print "Save Values"
        pass