r"""
@file   md_infrastructureguic.py
@author Peter M Bach <peterbach@gmail.com>, Natalia Duque <natalia.duquevillarreal@eawag.ch>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2019  Peter M. Bach, Natalia Duque

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
import os

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ublibs.ubspatial as ubspatial

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from .addboundarydialog import Ui_AddBoundaryDialog
from .addlocationdialog import Ui_AddLocationDialog
from .addshapedialog import Ui_AddShapeDialog

# --- DIALOG CLASSES ---
class AddLocationDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the dialog to add location points to the project."""
    def __init__(self, main, simulation, parent=None):
        """Initialization of class

        :param main: the instance of the main runtime environment
        :param simulation: the current simulation object
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_AddLocationDialog()
        self.ui.setupUi(self)
        self.simulation = simulation
        self.options = main.get_options()

        self.latlng = [0, 0]

    def done(self, r):
        # CHECKS BEFORE CLOSING AND ADDING THE LOCATION... 2 conditions: illegal lat/long entries, name already exists
        if self.Accepted == r:
            close_conditions = [1,1,1]   # Lat, Long, Name

            if self.ui.locname_line.text() in self.simulation.get_project_location_names():
                prompt = "Warning: Another location with the same name already exists for this project. Please choose" \
                         "a different name for the location you defined!"
                QtWidgets.QMessageBox.warning(self, "Location name already exists", prompt, QtWidgets.QMessageBox.Ok)
                close_conditions[0] = 0

            laterror = 0
            try:
                self.latlng[0] = float(self.ui.loclat_line.text())
                if self.latlng[0] < -90.0 or self.latlng[0] > 90.0:
                    laterror = 1
            except ValueError:
                laterror = 1
            if laterror:
                prompt = "Error: Please enter a valid latitude (number between -90.0 and +90.0 decimal degrees)!"
                QtWidgets.QMessageBox.warning(self, "Invalid Latitude", prompt, QtWidgets.QMessageBox.Ok)
                close_conditions[1] = 0

            longerror = 0
            try:
                self.latlng[1] = float(self.ui.loclong_line.text())
                if self.latlng[1] < -180.0 or self.latlng[1] > 180.0:
                    longerror = 1
            except ValueError:
                longerror = 1
            if longerror:
                prompt = "Error: Please enter a valid longitude (number between -180.0 and +180.0 decimal degrees)!"
                QtWidgets.QMessageBox.warning(self, "Invalid Longitude", prompt, QtWidgets.QMessageBox.Ok)
                close_conditions[2] = 0

            if sum(close_conditions) == len(close_conditions):
                self.simulation.add_project_location(str(self.ui.locname_line.text()), self.latlng,
                                                     str(self.ui.locdescr_textedit.toPlainText()), "Key Location")
                QtWidgets.QDialog.done(self, r)
        else:
            QtWidgets.QDialog.done(self, r)


class AddShapeDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the dialog to add basic shapes as boundaries to the project."""
    def __init__(self, main, simulation, parent=None):
        """Initialization of class.

        :param main: the instance of the main runtime environment
        :param simulation: the current simulation object
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_AddShapeDialog()
        self.ui.setupUi(self)
        self.simulation = simulation
        self.options = main.get_options()
        self.epsg_dict = main.epsg_dict

        # - COMBO BOXES ON PAGE 1 - LOCATIONS & COORDINATE SYSTEM
        self.update_locations_combo()
        self.update_coord_combo()
        self.ui.epsg_line.setText(str(self.simulation.get_project_parameter("project_epsg")))
        self.update_combo_from_epsg()

        # Enable Pop-up completion for the coordinate system combo box. Note that the combo box has to be editable!
        self.ui.coords_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        self.timer_linedit = QtCore.QTimer()
        self.timer_linedit.setSingleShot(True)
        self.timer_linedit.setInterval(300)
        self.timer_linedit.timeout.connect(self.update_combo_from_epsg)

        self.ui.epsg_line.textEdited.connect(lambda: self.timer_linedit.start())
        self.ui.coords_combo.currentIndexChanged.connect(self.update_epsg_from_combo)

        # - WIZARD CONTROLS - SIGNALS AND SLOTS
        self.ui.next_button.clicked.connect(self.advancestack)
        self.ui.back_button.clicked.connect(self.regressstack)
        self.ui.name_loc_same_check.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.rectangle_radio.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.circle_radio.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.hex_radio.clicked.connect(self.enable_disable_wizard_elements)

        self.enable_disable_wizard_elements()

    def advancestack(self):
        """Advances the stack widget one index forward."""
        if self.ui.loc_name_combo.currentIndex() == 0:      # Check #1 - valid location
            prompt = "Please select a valid location from project locations!"
            QtWidgets.QMessageBox.warning(self, 'No location selected', prompt, QtWidgets.QMessageBox.Ok)
            return True

        if not self.ui.name_loc_same_check.isChecked():     # Check #2 - valid boundary name
            for char in ubglobals.NOCHARS:
                if char in self.ui.shape_name_line.text():
                    prompt = "Invalid Boundary Name, one or more illegal characters used, please alter name!"
                    QtWidgets.QMessageBox.warning(self, 'Invalid Boundary Name', prompt, QtWidgets.QMessageBox.Ok)
                    return True

        invalid = 0
        try:    # Check #3 - valid EPSG
            int(self.ui.epsg_line.text())
        except ValueError:  # Case 3 - the EPSG box has illegal entry
            invalid = 1
        if self.ui.epsg_line == "":
            invalid = 1
        if invalid:
            prompt_msg = "Error, please select a valid coordinate system or EPSG code!"
            QtWidgets.QMessageBox.warning(self, 'Invalid Coordinate System', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        self.ui.shape_stack.setCurrentIndex(1)
        return True

    def regressstack(self):
        """Sets the stack widget one index backwards."""
        self.ui.shape_stack.setCurrentIndex(0)

    def enable_disable_wizard_elements(self):
        """Enables and disables elements in the wizard based on conditions of the radio buttons"""
        self.ui.shape_name_line.setEnabled(not self.ui.name_loc_same_check.isChecked())
        self.ui.rect_w_line.setEnabled(self.ui.rectangle_radio.isChecked())
        self.ui.rect_h_line.setEnabled(self.ui.rectangle_radio.isChecked())
        self.ui.circ_radius_line.setEnabled(self.ui.circle_radio.isChecked())
        self.ui.hex_edge_line.setEnabled(self.ui.hex_radio.isChecked())
        self.ui.hex_orient_combo.setEnabled(self.ui.hex_radio.isChecked())

    def update_locations_combo(self):
        """Updates the project locations combo box with location names."""
        self.ui.loc_name_combo.clear()
        self.ui.loc_name_combo.addItem("(select a project location as centroid)")
        locnames = self.simulation.get_project_location_names()
        for i in locnames:
            self.ui.loc_name_combo.addItem(i)
        self.ui.loc_name_combo.setCurrentIndex(0)

    def update_coord_combo(self):
        """Updates the coordinate system's combobox and the UI elements associated with it."""
        self.ui.coords_combo.clear()
        self.ui.coords_combo.addItem("(select coordinate system)")
        names = list(self.epsg_dict.keys())
        names.sort()
        for i in names:
            self.ui.coords_combo.addItem(i)
        self.ui.coords_combo.addItem("Other...")
        self.ui.coords_combo.setCurrentIndex(0)

    def update_combo_from_epsg(self):
        """Updates the coordinate system combo box based on the EPSG code entered in the text box, if the EPSG
        does not exist in the dictionary, the combo box displays "Other...". """
        names = list(self.epsg_dict.keys())
        names.sort()
        try:
            for name, epsg in self.epsg_dict.items():
                if int(epsg) == int(self.ui.epsg_line.text()):
                    curindex = names.index(name) + 1  # +1 to account for Index 0 < > text
                    self.ui.coords_combo.setCurrentIndex(curindex)
                    return True
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'
        except ValueError:
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'

    def update_epsg_from_combo(self):
        """Updates the EPSG text box based on the selected coordinate system in the combo box. If < >, index 0
        or "Other ..." are selected, the EPSG box remains blank."""
        try:
            self.ui.epsg_line.setText(self.epsg_dict[self.ui.coords_combo.currentText()])
        except KeyError:
            pass

    def done(self, r):
        if self.Accepted == r:
            # CHECK VALIDITY OF GEOMETRY TO DRAW - must have readable number inputs and must be greater than
            # minimum Block size - try/except block checks legal input and minimum size requirements (min. block size)
            invalid = 0
            if self.ui.rectangle_radio.isChecked():
                try:
                    invalid = max(float(self.ui.rect_w_line.text()) < 0.2, float(self.ui.rect_h_line.text()) < 0.2)
                except ValueError:
                    invalid = 1

            if self.ui.circle_radio.isChecked():
                try:
                    invalid = float(self.ui.circ_radius_line.text()) < 0.2
                except ValueError:
                    invalid = 1

            if self.ui.hex_radio.isChecked():
                try:
                    invalid = float(self.ui.hex_edge_line.text()) < 0.2
                except ValueError:
                    invalid = 1

            if invalid:
                prompt_msg = "Invalid input for geometric dimensions, please specify a readable number above 0.2 km"
                QtWidgets.QMessageBox.warning(self, "Invalid Geometry", prompt_msg, QtWidgets.QMessageBox.Ok)
            else:
                # Close the GUI and execute boundary creation in the core
                parameters = self.define_shape_boundary_parameter_set()
                self.simulation.add_basic_shape_as_simulation_boundary(parameters)
                QtWidgets.QDialog.done(self, r)
        else:
            QtWidgets.QDialog.done(self, r)

    def define_shape_boundary_parameter_set(self):
        """Sets up a dict() from all inputs across the GUI."""
        parameters = {}
        if self.ui.name_loc_same_check.isChecked():
            parameters["name"] = self.ui.loc_name_combo.currentText()
        else:
            parameters["name"] = self.ui.shape_name_line.text()
        parameters["epsg"] = int(self.ui.epsg_line.text())
        parameters["inputprojcs"] = str(self.ui.coords_combo.currentText())

        locinfo = self.simulation.get_project_location_info(self.ui.loc_name_combo.currentText())
        parameters["centroid"] = [locinfo["latitude"], locinfo["longitude"]]

        if self.ui.rectangle_radio.isChecked():
            parameters["shape"] = "rect"
            parameters["shapeparameters"] = [float(self.ui.rect_w_line.text()), float(self.ui.rect_h_line.text())]
        elif self.ui.circle_radio.isChecked():
            parameters["shape"] = "circ"
            parameters["shapeparameters"] = float(self.ui.circ_radius_line.text())
        else:
            orientation = ["NS", "EW"]
            parameters["shape"] = "hex"
            parameters["shapeparameters"] = [float(self.ui.hex_edge_line.text()),
                                                  orientation[self.ui.hex_orient_combo.currentIndex()]]
        return parameters


class AddBoundaryDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the dialog to add simulation boundaries to the project. The dialog is a
    wizard style, 4 steps that walk the user through the process of loading a shapefile, defining some rules for adding
    and projection as well as naming conventions."""
    def __init__(self, main, simulation, parent=None):
        """Initialization of class.

        :param main: the instance of the main runtime environment
        :param simulation: the current simulation object
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_AddBoundaryDialog()
        self.ui.setupUi(self)
        self.simulation = simulation
        self.options = main.get_options()
        self.epsg_dict = main.epsg_dict     # [REVAMP]

        # Define a dummy set of parameters that are passed to the simulation at the end of the wizard
        self.parameters = {
            "boundaryshp": "(none)",
            "featurecount": 0,
            "multifeatures": "ALL",
            "thresh": 1,
            "attnames": [],
            "extent": [],
            "inputprojcs": "",
            "epsg": None,
            "naming": "user",
            "name": "(none)"
        }

        self.ui.projectboundary_line.setText(self.parameters["boundaryshp"])

        # - SIGNALS AND SLOTS
        self.ui.projectboundary_browse.clicked.connect(self.browse_boundary_file)
        self.ui.include_all_radio.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.include_thresh_radio.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.include_largest_radio.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.name_featureattr_radio.clicked.connect(self.enable_disable_wizard_elements)
        self.ui.name_userdefined_radio.clicked.connect(self.enable_disable_wizard_elements)

        # - COORDINATE SYSTEM
        self.update_coord_combo()
        self.ui.epsg_line.setText(str(self.simulation.get_project_parameter("project_epsg")))
        self.update_combo_from_epsg()

        # Enable Pop-up completion for the coordinate system combo box. Note that the combo box has to be editable!
        self.ui.coords_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        self.timer_linedit = QtCore.QTimer()
        self.timer_linedit.setSingleShot(True)
        self.timer_linedit.setInterval(300)
        self.timer_linedit.timeout.connect(self.update_combo_from_epsg)

        self.ui.epsg_line.textEdited.connect(lambda: self.timer_linedit.start())
        self.ui.coords_combo.currentIndexChanged.connect(self.update_epsg_from_combo)

        # - WIZARD CONTROLS
        self.ui.step1next.clicked.connect(self.advancestack)
        self.ui.step2next.clicked.connect(self.advancestack)
        self.ui.step3next.clicked.connect(self.advancestack)
        self.ui.step4finish.clicked.connect(self.save_values)
        self.ui.step2back.clicked.connect(self.regressstack)
        self.ui.step3back.clicked.connect(self.regressstack)
        self.ui.step4back.clicked.connect(self.regressstack)

    def advancestack(self):
        currentIndex = self.ui.boundaryWizard.currentIndex()
        if currentIndex == 0:   # Load shapefile
            fileprops = ubspatial.load_shapefile_details(self.parameters["boundaryshp"])
            if type(fileprops) is str:
                prompt_msg = "Warning: Invalid Shapefile! Please load a valid Boundary File.\n Message: "+ fileprops
                QtWidgets.QMessageBox.warning(self, fileprops, prompt_msg, QtWidgets.QMessageBox.Ok)
                return True
            if fileprops[0] not in ["POLYGON", "MULTIPOLYGON"]:
                prompt_msg = "Warning: Invalid Geometry! Please load a valid POLYGON File."
                QtWidgets.QMessageBox.warning(self, "Invalid Geometry", prompt_msg, QtWidgets.QMessageBox.Ok)
                return True
            self.parameters["geometry"] = fileprops[0]
            self.parameters["extent"] = fileprops[1:5]
            self.parameters["epsg"] = fileprops[6]
            self.parameters["featurecount"] = fileprops[7]
            self.parameters["attnames"] = fileprops[8]
            print("Fileprops", fileprops[8])

            self.update_rest_of_wizard()

        elif currentIndex == 1:     # Deal with multiple features
            if self.ui.include_all_radio.isChecked():
                self.parameters["multifeatures"] = "ALL"
            elif self.ui.include_largest_radio.isChecked():
                self.parameters["multifeatures"] = "LRG"
            else:
                self.parameters["multifeatures"] = "THR"
            self.parameters["thresh"] = float(self.ui.boundary_thresh_spin.value())

        elif currentIndex == 2:     # Coordinate System
            try:
                if self.ui.epsg_line != "":
                    epsg = int(self.ui.epsg_line.text())
                else:
                    prompt_msg = "Error, please select a valid coordinate system or EPSG code!"
                    QtWidgets.QMessageBox.warning(self, 'Invalid Coordinate System', prompt_msg,
                                                  QtWidgets.QMessageBox.Ok)
                    return True
            except ValueError:  # Case 3 - the EPSG box has illegal entry
                prompt_msg = "Error, please select a valid coordinate system or EPSG code!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Coordinate System', prompt_msg,
                                              QtWidgets.QMessageBox.Ok)
                return True
            self.parameters["epsg"] = int(self.ui.epsg_line.text())
            self.parameters["inputprojcs"] = str(self.ui.coords_combo.currentText())

        self.ui.boundaryWizard.setCurrentIndex(currentIndex + 1)

    def regressstack(self):
        """Sets the stack widget one index backwards."""
        self.ui.boundaryWizard.setCurrentIndex(self.ui.boundaryWizard.currentIndex() - 1)

    def update_rest_of_wizard(self):
        """Updates pages 2 to 4 of the stack widget with new information from the shapefile boundary file."""
        if self.parameters["featurecount"] == 1:        # >> PAGE 2
            self.ui.step2scrollArea.setEnabled(0)
            self.ui.include_all_radio.setChecked(1)
        else:
            self.ui.step2scrollArea.setEnabled(1)
            if self.parameters["multifeatures"] == "ALL":
                self.ui.include_all_radio.setChecked(1)
            elif self.parameters["multifeatures"] == "LRG":
                self.ui.include_largest_radio.setChecked(1)
            else:
                self.ui.include_thresh_radio.setChecked(1)
        self.ui.boundary_thresh_spin.setValue(self.parameters["thresh"])

        self.ui.epsg_line.setText(str(self.parameters["epsg"]))     # >> PAGE 3
        self.update_combo_from_epsg()                   # Use the shapefile's EPSG to update the combo
        self.ui.extent_x.setText("Left: "+str(self.parameters["extent"][0])+
                                 " | Right: "+str(self.parameters["extent"][1]))
        self.ui.extent_y.setText("Bottom: "+str(self.parameters["extent"][2])+
                                 " | Top: "+str(self.parameters["extent"][3]))

        if self.parameters["naming"] == "user":         # >> PAGE 4
            self.ui.name_userdefined_radio.setChecked(1)
        else:
            self.ui.name_featureattr_radio.setChecked(1)

        self.enable_disable_wizard_elements()
        self.update_attnames_combo()

    def browse_boundary_file(self):
        """Opens a file dialog, which requests a shapefile of the case study boundary. UrbanBEATS
        uses this to delineate data for the project and for visualisation purposes and other calculations."""
        message = "Browse for Project Boundary Shapefile..."
        boundaryfile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir, "Shapefile (*.shp)")
        if boundaryfile:
            self.ui.projectboundary_line.setText(boundaryfile)
            self.parameters["boundaryshp"] = boundaryfile

    def enable_disable_wizard_elements(self):
        """Enables and disables elements in the wizard based on conditions of the radio buttons"""
        self.ui.boundary_thresh_spin.setEnabled(self.ui.include_thresh_radio.isChecked())
        self.ui.name_userdefined_line.setEnabled(self.ui.name_userdefined_radio.isChecked())
        self.ui.name_featureattr_combo.setEnabled(self.ui.name_featureattr_radio.isChecked())

    def update_coord_combo(self):
        """Updates the coordinate system's combobox and the UI elements associated with it."""
        self.ui.coords_combo.clear()
        self.ui.coords_combo.addItem("(select coordinate system)")
        names = list(self.epsg_dict.keys())
        names.sort()
        for i in names:
            self.ui.coords_combo.addItem(i)
        self.ui.coords_combo.addItem("Other...")
        self.ui.coords_combo.setCurrentIndex(0)

    def update_attnames_combo(self):
        """Updates the attribute names combo box with the shapefile's attribute names."""
        self.ui.name_featureattr_combo.clear()
        attnames = self.parameters["attnames"]
        attnames.sort()
        self.ui.name_featureattr_combo.addItem("(select attribute name)")
        for i in attnames:
            self.ui.name_featureattr_combo.addItem(i)
        self.ui.name_featureattr_combo.setCurrentIndex(0)

    def update_combo_from_epsg(self):
        """Updates the coordinate system combo box based on the EPSG code entered in the text box, if the EPSG
        does not exist in the dictionary, the combo box displays "Other...". """
        names = list(self.epsg_dict.keys())
        names.sort()
        try:
            for name, epsg in self.epsg_dict.items():
                if int(epsg) == int(self.ui.epsg_line.text()):
                    curindex = names.index(name) + 1  # +1 to account for Index 0 < > text
                    self.ui.coords_combo.setCurrentIndex(curindex)
                    return True
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'
        except ValueError:
            self.ui.coords_combo.setCurrentIndex(len(names) + 1)  # Set to 'Other'

    def update_epsg_from_combo(self):
        """Updates the EPSG text box based on the selected coordinate system in the combo box. If < >, index 0
        or "Other ..." are selected, the EPSG box remains blank."""
        try:
            self.ui.epsg_line.setText(self.epsg_dict[self.ui.coords_combo.currentText()])
        except KeyError:
            pass

    def done(self, r):
        # CONDITIONS FOR THE COORDINATE SYSTEM SELECTION - conditions_met[2]
        if self.Accepted == r:
            close_conditions = [1, 1]   # [feature limit, illegal characters]

            # ISSUE WARNING IF FEATURECOUNT EXCEEDS LIMIT
            if self.parameters["featurecount"] >= int(self.options["featcountwarning"]):
                prompt = "Warning: The boundary file has over "+str(self.options["featcountwarning"])+" features. " \
                            "Loading can take some time. Do you wish to continue?"
                continue_bool = QtWidgets.QMessageBox.question(self, "Feature Count", prompt,
                                                               QtWidgets.QMessageBox.Yes |
                                                               QtWidgets.QMessageBox.No)
                if continue_bool == QtWidgets.QMessageBox.No:
                    close_conditions[0] = 0

            # CHECK FOR ILLEGAL CHARACTERS
            if self.ui.name_userdefined_radio.isChecked():
                for char in ubglobals.NOCHARS:
                    if char in self.ui.name_userdefined_line.text():
                        prompt = "Invalid Boundary Name, one or more illegal characters used, please alter name!"
                        close_conditions[1] = 0
            elif self.ui.name_featureattr_radio.isChecked() and self.ui.name_featureattr_combo.currentIndex() == 0:
                prompt = "Invalid attribute name selected! Please select one of the shapefile's attribute names!"
                close_conditions[1] = 0
            if close_conditions[1] == 0:
                QtWidgets.QMessageBox.warning(self, 'Invalid Boundary Name', prompt, QtWidgets.QMessageBox.Ok)

            if sum(close_conditions) == len(close_conditions):
                self.save_values()
                QtWidgets.QDialog.done(self, r)
        else:
            QtWidgets.QDialog.done(self, r)

    def save_values(self):
        """Saves all values to the current simulation as a boundary to load and process."""
        if self.ui.name_userdefined_radio.isChecked():
            self.parameters["naming"] = "user"
            self.parameters["name"] = str(self.ui.name_userdefined_line.text())
        else:
            self.parameters["naming"] = "attr"
            self.parameters["name"] = str(self.ui.name_featureattr_combo.currentText())

        self.simulation.\
            set_current_boundary_file_to_load(self.parameters["boundaryshp"],
                                              [self.parameters["multifeatures"], self.parameters["thresh"]],
                                              [self.parameters["naming"], self.parameters["name"]],
                                              self.parameters["epsg"],
                                              self.parameters["inputprojcs"])
        return True

# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Coordinates:</strong> x """+str(mapstats["centroid"][0])+""", y """+str(mapstats["centroid"][1])+"""</span></p>
# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Case Study Size:</strong> """+str(round(mapstats["area"], 2))+""" km</span><span style=" font-size:8pt; vertical-align:super;">2</span></p>
# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Coordinate System:</strong> """+mapstats["coordsysname"]+""" ("""+str(mapstats["inputEPSG"])+""")</span></p>
