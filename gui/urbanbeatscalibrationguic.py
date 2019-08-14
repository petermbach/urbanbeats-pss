# -*- coding: utf-8 -*-
"""
@file   urbanbeatscalibrationguic.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2019  Peter M. Bach

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

from urbanbeatscalibration import Ui_CalibrationViewer

# --- ADD DATA DIALOG ---
class LaunchCalibrationViewer(QtWidgets.QDialog):
    """Class definition for the add data dialog window for importing and managing data."""
    def __init__(self, main, simulation, datalibrary, parent=None):
        """Class constructor, references the data library object active in the simulation as well as the main
        runtime class.

        :param main: referring to the main GUI so that changes can be made in real-time to the main interface
        :param datalibrary: the data library object, which will be updated as data files are added to the project.
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_CalibrationViewer()
        self.ui.setupUi(self)

        # --- INITIALIZE MAIN VARIABLES ---
        self.maingui = main    # the main runtime - for GUI changes
        self.simulation = simulation
        self.datalibrary = datalibrary      # the simulation object's data library

        # Update the category and sub-category combo boxes


        # --- SIGNALS AND SLOTS ---


