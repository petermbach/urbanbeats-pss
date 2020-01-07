"""
@file   urbanbeatsdialogs.py
@author Martijn Kuller <martijnkuller@gmail.com>, Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS), SSANTO
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

__author__ = "Martijn Kuller"
__copyright__ = "Copyright 2019. Martijn Kuller"

# --- CODE STRUCTURE ---
#       (1) Preferences Dialog
#       (2)
#
# --- --- --- --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets

# --- URBANBEATS LIBRARY IMPORTS ---
from .ssanto_maingui import Ui_SSANTOMain


# --- MAIN WINDOW ---
class SSANTOMainLaunch(QtWidgets.QDialog):
    """Class definition for the about dialog window. Connects the GUI
    Ui_AboutDialog() with the Main Window"""
    def __init__(self, activesim, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_SSANTOMain()
        self.ui.setupUi(self)
        self.urbanbeatssim = activesim

        self.ui.statusbar.showMessage("Hello World")


    def setup_gui_with_activesimdata(self):
        pass



# --- VALUE SCALING ---



# --- WEIGHTING DIALOG ---




# --- SWING WEIGHTING ---
