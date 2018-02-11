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
from adddatadialog import Ui_AddDataDialog
from startnewprojectdialog import Ui_ProjectSetupDialog
from logdialog import Ui_LogDialog

# --- GLOBAL VARIABLES ---
LANGUAGECOMBO = ["DE", "EN", "ES", "FR", "PO", "CN", "JP"]
DECISIONS = ["best", "random", "none"]
COORDINATESYSTEMS = ["GDA", "UTM", "Other"]
CITIES = ["Adelaide", "Brisbane", "Innsbruck", "Melbourne", "Nanjing", "Perth",
                  "SanFrancisco", "Sydney", "Zurich", "Other"]
MAPSTYLES = ["CARTO", "ESRI", "OSM", "TONER", "TERRAIN"]


# --- ABOUT DIALOG ---
class AboutDialogLaunch(QtWidgets.QDialog):
    """Class definition for the about dialog window. Connects the GUI
    Ui_AboutDialog() with the Main Window"""
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)


# --- ADD DATA DIALOG ---
class AddDataDialogLaunch(QtWidgets.QDialog):
    """Class definition for the add data dialog window for importing and managing data."""
    def __init__(self, main, datalibrary, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_AddDataDialog()

        # --- INITIALIZE MAIN VARIABLES ---
        self.main = main    # the main runtime - for GUI changes
        self.datalibrary = datalibrary      # the simulation object's data library

        # --- SIGNALS AND SLOTS ---
        self.ui.spatial_radio.clicked.connect(self.update_datacat_combo)
        self.ui.temporal_radio.clicked.connect(self.update_datacat_combo)
        self.ui.qualitative_radio.clicked.connect(self.update_datacat_combo)
        self.ui.datacat_combo.currentIndexChanged.connect(self.update_datacatsub_combo)

        self.ui.cleardata_button.clicked.connect(self.clear_interface)
        self.ui.done_button.clicked.connect(self.accept)
        self.ui.adddata_button.connect(self.add_data_to_project)

    def update_datacat_combo(self):
        pass

    def update_datacatsub_combo(self):
        pass

    def clear_interface(self):
        pass

    def add_data_to_project(self):
        dataset = {}
        dataset["file"] = str(self.ui.databox.text())
        if self.ui.spatial_radio.isChecked():
            dataset["datatype"] = "SPATIAL"
        elif self.ui.temporal_radio.isChecked():
            dataset["datatype"] = "TEMPORAL"
        else:
            dataset["datatype"] = "QUALITATIVE"

        self.addnewdata.emit(dataset)
        self.clear_interface()


# --- SETUP NEW PROJECT DIALOG ---
class NewProjectDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the setup of a new project dialog window Ui_ProjectSetupDialog
    with the main window or startup dialog. This dialog helps the user set up a new project from
    scratch and includes the essential elements for creating the initial project folder."""
    def __init__(self, simulation, viewer, parent=None):
        """Initialization of class, takes two key parameters that differentiate the dialog window's
        use as a viewer or a setup dialog.

        :param main: the instance of the main runtime environment
        :param viewer: int, if 0, then the dialog is being opened for a new project, 1 to modify, 2 to view
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_ProjectSetupDialog()
        self.ui.setupUi(self)
        self.__viewer = viewer
        self.simulation = simulation

        # --- PRE-FILLING GUI SETUP ---
        if self.__viewer == 1:     # Edit Project Details
            self.disable_non_modifiable_parameters()
        if self.__viewer == 2:     # View Project Details
            self.disable_all_parameters()

        # --- GUI PARAMETERS ---
        self.ui.projname_line.setText(self.simulation.get_project_parameter("name"))
        self.ui.region_line.setText(self.simulation.get_project_parameter("region"))
        self.ui.location_combo.setCurrentIndex(CITIES.index(self.simulation.get_project_parameter("city")))
        self.ui.modellername_box.setText(self.simulation.get_project_parameter("modeller"))
        self.ui.affiliation_box.setText(self.simulation.get_project_parameter("affiliation"))
        self.ui.otherpersons_box.setPlainText(self.simulation.get_project_parameter("otherpersons"))
        self.ui.synopsis_box.setPlainText(self.simulation.get_project_parameter("synopsis"))
        self.ui.projectboundary_line.setText(self.simulation.get_project_parameter("boundaryshp"))

        if self.simulation.get_project_parameter("logstyle") == "comprehensive":
            self.ui.projectlog_compreh.setChecked(1)
        else:
            self.ui.projectlog_simple.setChecked(1)

        self.ui.projpath_line.setText(self.simulation.get_project_parameter("projectpath"))
        self.ui.keepcopy_check.setChecked(int(self.simulation.get_project_parameter("keepcopy")))

        # --- SIGNALS AND SLOTS ---
        self.ui.projectboundary_browse.clicked.connect(self.browse_boundary_file)
        self.ui.projpath_button.clicked.connect(self.browse_project_path)
        self.accepted.connect(self.run_setup_project)

    def browse_boundary_file(self):
        """Opens a file dialog, which requests a shapefile of the case study boundary. UrbanBEATS
        uses this to delineate data for the project and for visualisation purposes and other calculations."""
        message = "Browse for Project Boundary Shapefile..."
        boundaryfile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir, "Shapefile (*.shp)")
        if boundaryfile:
            self.ui.projectboundary_line.setText(boundaryfile)

    def browse_project_path(self):
        """Opens a file dialog, which requests for a folder path within which UrbanBEATS will
        create the project folders and move input maps if requested."""
        message = "Select the folder you wish to create the project in..."
        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
        if folderpath:
            self.ui.projpath_line.setText(str(folderpath))

    def disable_non_modifiable_parameters(self):
        """Disabled several key input parameters that cannot be modified if the project
        has already been created. The method is called if the GUI is being opened as a viewer
        rather than for the setup of a new proejct. Items disabled include the project name,
        the log settings, the path and whether to copy data into the project folder."""
        self.ui.projname_line.setEnabled(0)
        self.ui.projectlog_compreh.setEnabled(0)
        self.ui.projectlog_simple.setEnabled(0)
        self.ui.projpath_line.setEnabled(0)
        self.ui.projpath_button.setEnabled(0)
        self.ui.keepcopy_check.setEnabled(0)

    def disable_all_parameters(self):
        """Disables the whole interface as it was opened just for viewing the information."""
        self.ui.aboutproject_widget1.setEnabled(0)
        self.ui.aboutproject_widget2.setEnabled(0)
        self.ui.aboutuser_widget.setEnabled(0)
        self.ui.synopsis_box.setEnabled(0)
        self.ui.boundary_widget.setEnabled(0)
        self.ui.projectlog_widget.setEnabled(0)
        self.ui.path_widget.setEnabled(0)

    def run_setup_project(self):
        """Determines based on how the GUI was opened what needs to occur. If self.__viewer == 0 then
        new project signal is emitted with the dictionary of details. If self.__viewer == 1 then an update
        of project parameters is passed back to the main runtime. If self.__viewer == 2, then nothing
        happens and the dialog window just closes."""
        if self.__viewer == 0:
            # Do stuff
            self.save_values()
        elif self.__viewer == 1:
            self.save_values()
        else:
            pass    # Just viewing, just close the window.

    def save_values(self):
        """Saves all project parameters values and returns a dictionary for use to setup simulation."""
        self.simulation.set_project_parameter("name", self.ui.projname_line.text())
        self.simulation.set_project_parameter("region", self.ui.region_line.text())
        self.simulation.set_project_parameter("city", CITIES[self.ui.location_combo.currentIndex()])
        self.simulation.set_project_parameter("modeller", self.ui.modellername_box.text())
        self.simulation.set_project_parameter("affiliation", self.ui.affiliation_box.text())
        self.simulation.set_project_parameter("otherpersons", self.ui.otherpersons_box.toPlainText())
        self.simulation.set_project_parameter("synopsis", self.ui.synopsis_box.toPlainText())
        self.simulation.set_project_parameter("boundaryshp", self.ui.projectboundary_line.text())
        self.simulation.set_project_parameter("projectpath", self.ui.projpath_line.text())
        self.simulation.set_project_parameter("keepcopy", int(self.ui.keepcopy_check.isChecked()))

        if self.ui.projectlog_compreh.isChecked():
            self.simulation.set_project_parameter("logstyle", "comprehensive")
        else:
            self.simulation.set_project_parameter("logstyle", "simplfied")


# --- PREFERENCES DIALOG ---
class PreferenceDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the preferences dialog. Connects the GUI
    Ui_PreferenceDialog() with the Main Window. This dialog is primarily for adjusting
    global model options. These options are saved in the Main Window class (main.pyw) rather than
    model core."""
    def __init__(self, main, tabindex, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
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

        self.ui.lang_combo.setCurrentIndex(LANGUAGECOMBO.index(self.options["language"]))

        self.ui.location_combo.setCurrentIndex(CITIES.index(self.options["city"]))
        self.ui_coords_line_enabledisable()

        self.ui.projpath_line.setText(str(self.options["defaultpath"]))
        self.ui.temppath_line.setText(str(self.options["tempdir"]))
        self.ui.temppath_check.setChecked(bool(self.options["tempdefault"]))
        self.ui_temppath_line_enabledisable()

        # Text Appearance

        # SIMULATION TAB
        self.ui.numiter_spin.setValue(int(self.options["maxiterations"]))
        self.ui.tolerance_spin.setValue(float(self.options["globaltolerance"]))

        self.ui.decision_combo.setCurrentIndex(DECISIONS.index(self.options["defaultdecision"]))

        # MAP SETTINGS TAB
        self.ui.mapstyle_combo.setCurrentIndex(MAPSTYLES.index(self.options["mapstyle"]))
        self.ui_setmapstyle_pixmap()

        self.ui.tileserver_line.setText(self.options["tileserverURL"])
        self.ui.cache_check.setChecked(bool(self.options["cachetiles"]))
        self.ui.offline_check.setChecked(bool(self.options["offline"]))

        self.ui.coords_combo.setCurrentIndex(COORDINATESYSTEMS.index(self.options["defaultcoordsys"]))
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
        self.module.reset_default_options()
        self.reject()   # close the dialog window but do not update it

    def save_values(self):
        """Saves the updated options to the main window and calls the update function to modify the
        .cfg file with new options.

        :return: None
        """
        # GENERAL TAB
        self.options["defaultmodeller"] = str(self.ui.modellername_line.text())
        self.options["defaultaffil"] = str(self.ui.modelleraffil_line.text())
        if self.ui.projectlog_compreh.isChecked():
            self.options["projectlogstyle"] = "comprehensive"
        else:
            self.options["projectlogstyle"] = "simplified"

        self.options["language"] = str(LANGUAGECOMBO[self.ui.lang_combo.currentIndex()])
        self.options["city"] = str(CITIES[self.ui.location_combo.currentIndex()])

        self.options["coordinates"] = str(self.ui.coords_line.text())
        self.options["defaultpath"] = str(self.ui.projpath_line.text())
        self.options["tempdir"] = str(self.ui.temppath_line.text())
        self.options["tempdefault"] = int(self.ui.temppath_check.isChecked())

        # Text Appearance

        # SIMULATION TAB
        self.options["maxiterations"] = int(self.ui.numiter_spin.value())
        self.options["globaltolerance"] = float(self.ui.tolerance_spin.value())
        self.options["defaultdecision"] = str(DECISIONS[self.ui.decision_combo.currentIndex()])

        # MAP SETTINGS TAB
        self.options["mapstyle"] = str(MAPSTYLES[self.ui.mapstyle_combo.currentIndex()])
        self.options["tileserverURL"] = str(self.ui.tileserver_line.text())
        self.options["cachetiles"] = int(self.ui.cache_check.isChecked())
        self.options["offline"] = int(self.ui.offline_check.isChecked())
        self.options["defaultcoordsys"] = str(COORDINATESYSTEMS[self.ui.coords_combo.currentIndex()])
        self.options["customepsg"] = str(self.ui.epsg_line.text())

        # EXTERNAL TAB
        self.options["epanetpath"] = str(self.ui.epanetpath_line.text())
        self.options["swmmpath"] = str(self.ui.swmmpath_line.text())
        self.options["musicpath"] = str(self.ui.musicpath_line.text())

        #ONLINE TAB
        # Coming Soon

        #UPDATE THE CFG FILE BY EMITTING THE SIGNAL
        self.module.write_new_options(self.options)


# --- PROJECT LOG DIALOG ---
class ProjectLogLaunch(QtWidgets.QDialog):
    """Class instance for the project log window."""
    def __init__(self, logobject, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_LogDialog()
        self.ui.setupUi(self)
        self.__logobject = logobject

        # --- SIGNALS AND SLOTS ---
        self.ui.export_log.clicked.connect(self.export_log)
        self.ui.log_widget.currentChanged.connect(self.disable_clear_button)
        self.ui.done_button.clicked(self.accept)

    def disable_clear_button(self):
        if self.ui.log_widget.currentIndex() == 1:
            self.ui.clear_log.setEnabled(0)
        else:
            self.ui.clear_log.setEnabled(1)

    def export_log(self):
        pass

