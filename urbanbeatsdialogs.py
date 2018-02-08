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
from aboutdialog import Ui_AboutDialog
from preferencesdialog import Ui_PreferencesDialog


# --- ABOUT DIALOG ---
class AboutDialogLaunch(QtWidgets.QDialog):
    """Class definition for the about dialog window. Connects the GUI
    Ui_AboutDialog() with the Main Window"""
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)


# --- PREFERENCES DIALOG ---
class PreferenceDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the preferences dialog. Connects the GUI
    Ui_PreferenceDialog() with the Main Window. This dialog is primarily for adjusting
    global model options. These options are saved in the Main Window class (main.pyw) rather than
    model core."""
    updateCFG = QtCore.pyqtSignal(dict, bool, name="updateCFG")     # Update config file signal
    resetCFG = QtCore.pyqtSignal(int, bool, name="resetCFG")      # Reset all options signal

    def __init__(self, main, tabindex):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self.ui.options_tabs.setCurrentIndex(tabindex)

        self.module = main
        self.options = main.get_options()

        # --- FILL IN GUI ---
        # GENERAL TAB
        self.ui.modellername_line.setText(str(self.options["defaultmodeller"]))
        self.ui.modelleraffil_line.setText(str(self.options["defaultaffil"]))

        if self.options["projectlogstyle"] == "comprehensive":
            self.ui.projectlog_compreh.setChecked(1)
        else:
            self.ui.projectlog_simple.setChecked(0)

        languagecombo = ["DE", "EN", "ES", "FR", "PO", "CN", "JP"]
        self.ui.lang_combo.setCurrentIndex(languagecombo.index(self.options["language"]))

        cities = ["Adelaide", "Brisbane", "Innsbruck", "Melbourne", "Nanjing", "Perth",
                  "SanFrancisco", "Sydney", "Zurich", "Other"]
        self.ui.location_combo.setCurrentIndex(cities.index(self.options["city"]))
        self.ui_coords_line_enabledisable()

        self.ui.projpath_line.setText(str(self.options["defaultpath"]))
        self.ui.temppath_line.setText(str(self.options["tempdir"]))
        self.ui.temppath_check.setChecked(bool(self.options["tempdefault"]))
        self.ui_temppath_line_enabledisable()

        # Text Appearance

        # SIMULATION TAB
        self.ui.numiter_spin.setValue(int(self.options["maxiterations"]))
        self.ui.tolerance_spin.setValue(float(self.options["globaltolerance"]))

        decisions = ["best", "random", "none"]
        self.ui.decision_combo.setCurrentIndex(decisions.index(self.options["defaultdecision"]))

        # MAP SETTINGS TAB
        mapstyles = ["CARTO", "ESRI", "OSM", "TONER", "TERRAIN"]
        self.ui.mapstyle_combo.setCurrentIndex(mapstyles.index(self.options["mapstyle"]))
        self.ui_setmapstyle_pixmap()

        self.ui.tileserver_line.setText(self.options["tileserverURL"])
        self.ui.cache_check.setChecked(bool(self.options["cachetiles"]))
        self.ui.offline_check.setChecked(bool(self.options["offline"]))

        coordinatesystems = ["GDA", "UTM", "Other"]
        self.ui.coords_combo.setCurrentIndex(coordinatesystems.index(self.options["defaultcoordsys"]))
        self.ui.epsg_line.setText(self.options["customepsg"])
        self.ui_epsg_line_enabledisable()

        # EXTERNAL TAB
        self.ui.epanetpath_line.setText(self.options["epanetpath"])
        self.ui.swmmpath_line.setText(self.options["swmmpath"])
        self.ui.musicpath_line.setText(self.options["musicpath"])

        # ONLINE TAB
        # Coming Soon.

        # --- SIGNALS AND SLOTS ---
        self.accepted.connect(self.save_values)
        self.ui.reset_button.clicked.connect(self.reset_values)
        self.ui.location_combo.currentIndexChanged.connect(self.ui_coords_line_enabledisable)
        self.ui.temppath_check.clicked.connect(self.ui_temppath_line_enabledisable)
        self.ui.projpath_button.clicked.connect(lambda: self.get_path("P"))
        self.ui.temppath_button.clicked.connect(lambda: self.get_path("T"))
        self.ui.mapstyle_combo.currentIndexChanged.connect(self.ui_setmapstyle_pixmap)
        self.ui.coords_combo.currentIndexChanged.connect(self.ui_epsg_line_enabledisable)
        self.ui.epanetpath_button.clicked.connect(lambda: self.get_path("E"))
        self.ui.swmmpath_button.clicked.connect(lambda: self.get_path("S"))
        self.ui.musicpath_button.clicked.connect(lambda: self.get_path("M"))

    def get_path(self, path_type):
        """Opens a browse window in search for a folder path based on the input path_type. After user
        chooses the path, data is filled into the relevant GUI widget.

        :param path_type: type of path, "P" = project, "T" = temp, "E" = epanet, "S" = swmm, "M" = MUSIC
        :return: None
        """
        if path_type == "P":
            message = "Default Path for Projects"
        elif path_type == "T":
            message = "Default Path for Temp Directory"
        elif path_type == "E":
            message = "Installation Directory for EPANET2"
        elif path_type == "S":
            message = "Installation Directory for SWMM"
        elif path_type == "M":
            message = "Installation Directory for MUSIC"
        else:
            message = "How am I supposed to know what path I want!?"

        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
        if folderpath:
            if path_type == "P":
                self.ui.projpath_line.setText(folderpath)
            elif path_type == "T":
                self.ui.temppath_line.setText(folderpath)
            elif path_type == "E":
                self.ui.epanetpath_line.setText(folderpath)
            elif path_type == "S":
                self.ui.swmmpath_line.setText(folderpath)
            elif path_type == "M":
                self.ui.musicpath_line.setText(folderpath)

    def ui_setmapstyle_pixmap(self):
        """Dynamically changes the displayed minimap on the preference dialog Map Settings Tab to the appropriate
        map style."""
        mapstylepixmaps = ["mt_cartodb.png", "mt_esriworld.png", "mt_osm.png",
                           "mt_stamentoner.png", "mt_stamenterrain.png"]
        self.ui.mapstyle_pic.setPixmap(QtGui.QPixmap(":/media/map templates/" +
                                                     mapstylepixmaps[self.ui.mapstyle_combo.currentIndex()]))

    def ui_epsg_line_enabledisable(self):
        """Enables or disables the EPSG line edit depending on whether 'Other' coordinate system was selected."""
        if self.ui.coords_combo.currentIndex() == self.ui.coords_combo.count() - 1:
            self.ui.epsg_line.setEnabled(1)
        else:
            self.ui.epsg_line.setEnabled(0)

    def ui_temppath_line_enabledisable(self):
        """Enables/Disables the temppath_line widget and button based on the tempdir temppath checkbox."""
        if self.ui.temppath_check.isChecked():
            self.ui.temppath_line.setEnabled(0)
            self.ui.temppath_button.setEnabled(0)
        else:
            self.ui.temppath_line.setEnabled(1)
            self.ui.temppath_button.setEnabled(1)

    def ui_coords_line_enabledisable(self):
        """Enables/Disables the coordinates input box based on selected city"""
        if self.ui.location_combo.currentIndex() == self.ui.location_combo.count()-1:
            self.ui.coords_line.setEnabled(1)
        else:
            self.ui.coords_line.setEnabled(0)

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


