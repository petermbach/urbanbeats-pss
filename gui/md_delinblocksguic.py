# -*- coding: utf-8 -*-
"""
@file   md_delinblocksguic.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2012  Peter M. Bach

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
__copyright__ = "Copyright 2012. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---

# --- URBANBEATS LIBRARY IMPORTS ---

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from md_delinblocksgui import Ui_Delinblocks_Dialog

# --- MAIN GUI FUNCTION ---
class DelinBlocksGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_Delinblocks_Dialog()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main
        self.simulation = simulation
        self.datalibrary = datalibrary
        self.log = simlog

        # --- PARAMETER SETUP ---



        # --- SIGNALS AND SLOTS ---


    def save_values(self):
        """Saves all user-modified values for the module's parameters from the GUI
        into the simulation core."""
        pass