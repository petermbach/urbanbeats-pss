# -*- coding: utf-8 -*-
"""
@file   main.pyw
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

# --- CODE STRUCTURE ---
#       (1) Preferences Dialog
#       (2)
#
# --- --- --- --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import sys
import os
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit

# --- URBANBEATS LIBRARY IMPORTS ---
from preferencesdialog import Ui_PreferencesDialog


# --- PREFERENCES DIALOG ---
class PreferenceDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the preferences dialog. Connects the GUI
    Ui_PreferenceDialog() with the Main Window. This dialog is primarily for adjusting
    global model options. These options are saved in the Main Window class (main.pyw) rather than
    model core."""
    updateCFG = QtCore.pyqtSignal(dict, bool, name="updateCFG")     # Update config file signal
    resetCFG = QtCore.pyqtSignal(int, bool, name="resetCFG")      # Reset all options signal

    def __init__(self, main):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self.module = main
        self.options = main.get_options()

        # SIGNALS AND SLOTS
        self.accepted.connect(self.save_values)
        self.ui.reset_button.clicked.connect(self.reset_values)

    def reset_values(self):
        """Resets all option values and closes the options/preferences dialog window."""
        self.reject()   # close the dialog window but do not update it
        self.resetCFG.emit(None, True)  # emit reset Signal with no dictionary and True reset bool

    def save_values(self):
        """Saves the updated options to the main window and calls the update function to modify the
        .cfg file with new options.

        :return: None
        """
        self.updateCFG.emit(self.options, False)    # emit update Signal with new dictionary and no reset


