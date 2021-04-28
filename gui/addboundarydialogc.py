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

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from .addboundarydialog import Ui_AddBoundaryDialog


# --- MAIN GUI FUNCTION ---
class AddBoundaryDialogLaunch(QtWidgets.QDialog):
    """Class definition for launching the setup of a new project dialog window Ui_ProjectSetupDialog
    with the main window or startup dialog. This dialog helps the user set up a new project from
    scratch and includes the essential elements for creating the initial project folder."""
    def __init__(self, main, simulation, parent=None):
        """Initialization of class, takes two key parameters that differentiate the dialog window's
        use as a viewer or a setup dialog.

        :param main: the instance of the main runtime environment
        :param viewer: int, if 0, then the dialog is being opened for a new project, 1 to modify, 2 to view
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_AddBoundaryDialog()
        self.ui.setupUi(self)
        self.simulation = simulation
        self.epsg_dict = main.epsg_dict     # [REVAMP]

        # self.ui.projectboundary_line.setText(self.simulation.get_project_parameter("boundaryshp"))

        # - COORDINATE SYSTEM
        # self.update_coord_combo()
        # self.ui.epsg_line.setText(self.simulation.get_project_parameter("project_epsg"))
        # self.update_combo_from_epsg()

        # Enable Pop-up completion for the coordinate system combo box. Note that the combo box has to be editable!
        # self.ui.coords_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # - SIGNALS AND SLOTS
        # self.ui.projectboundary_browse.clicked.connect(self.browse_boundary_file)

        # self.timer_linedit = QtCore.QTimer()
        # self.timer_linedit.setSingleShot(True)
        # self.timer_linedit.setInterval(300)
        # self.timer_linedit.timeout.connect(self.update_combo_from_epsg)

        # self.ui.epsg_line.textEdited.connect(lambda: self.timer_linedit.start())
        # self.ui.coords_combo.currentIndexChanged.connect(self.update_epsg_from_combo)

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

        def browse_boundary_file(self):
            """Opens a file dialog, which requests a shapefile of the case study boundary. UrbanBEATS
            uses this to delineate data for the project and for visualisation purposes and other calculations."""
            message = "Browse for Project Boundary Shapefile..."
            boundaryfile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir, "Shapefile (*.shp)")
            if boundaryfile:
                self.ui.projectboundary_line.setText(boundaryfile)

        def disable_all_parameters(self):
            self.ui.boundary_widget.setEnabled(0)

        def done(self):
            # CONDITION FOR A VALID BOUNDARY SHAPEFILE - conditions_met[1]
            if os.path.isfile(self.ui.projectboundary_line.text()):
                pass
            else:
                prompt_msg = "Please select a valid boundary shapefile!"
                QtWidgets.QMessageBox.warning(self, 'Invalid Boundary File', prompt_msg, QtWidgets.QMessageBox.Ok)
                conditions_met[1] = 0

            # CONDITIONS FOR THE COORDINATE SYSTEM SELECTION - conditions_met[2]
            if self.ui.coords_combo.currentText() not in ["Other...", "(select coordinate system)"]:
                # Case 1 - the coordinate system combo has a valid selection
                pass
                # datatype.append(self.ui.coord_combo.currentText())  # index 4
                # datatype.append(int(self.ui.epsg_box.text()))  # index 5
            else:
                try:  # Case 2 - the EPSG box can be converted to an integer and is not empty
                    if self.ui.epsg_line != "":
                        epsg = int(self.ui.epsg_line.text())
                        # datatype.append(self.ui.coord_combo.currentText())  # index 4
                        # datatype.append(int(self.ui.epsg_box.text()))
                    else:
                        prompt_msg = "Error, please select a valid coordinate system or EPSG code!"
                        QtWidgets.QMessageBox.warning(self, 'Invalid Coordinate System', prompt_msg,
                                                      QtWidgets.QMessageBox.Ok)
                        conditions_met[2] = 0
                except ValueError:  # Case 3 - the EPSG box has illegal entry
                    prompt_msg = "Error, please select a valid coordinate system or EPSG code!"
                    QtWidgets.QMessageBox.warning(self, 'Invalid Coordinate System', prompt_msg,
                                                  QtWidgets.QMessageBox.Ok)
                    conditions_met[2] = 0

            if sum(conditions_met) == len(conditions_met):
                self.save_values()
                QtWidgets.QDialog.done(self, r)
            else:
                return

        def save_values(self):
            self.simulation.set_project_parameter("boundaryshp", self.ui.projectboundary_line.text())
            self.simulation.set_project_parameter("project_coord_sys", self.ui.coords_combo.currentText())
            self.simulation.set_project_parameter("project_epsg", int(self.ui.epsg_line.text()))


# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Coordinates:</strong> x """+str(mapstats["centroid"][0])+""", y """+str(mapstats["centroid"][1])+"""</span></p>
# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Case Study Size:</strong> """+str(round(mapstats["area"], 2))+""" km</span><span style=" font-size:8pt; vertical-align:super;">2</span></p>
# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"><strong>Coordinate System:</strong> """+mapstats["coordsysname"]+""" ("""+str(mapstats["inputEPSG"])+""")</span></p>