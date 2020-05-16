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

__author__ = "Peter M. Bach, Natalia Duque"
__copyright__ = "Copyright 2018. Peter M. Bach, Natalia Duque"

# --- PYTHON LIBRARY IMPORTS ---

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from .md_bgsplanninggui import Ui_BlueGreenDialog


# --- MAIN GUI FUNCTION ---
class BlueGreenGuiLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, datalibrary, simlog, parent=None):
        """ Initialisation of the Spatial Mapping GUI, takes several input parameters.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param datalibrary: The active data library --> main.get_active_data_library()
        :param simlog: The active log --> main.get_active_project_log()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_BlueGreenDialog()
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

        # self.gui_state = "initial"
        # self.change_active_module()
        # self.gui_state = "ready"

        # --- SIGNALS AND SLOTS ---


        # OTHERS
        self.ui.buttonBox.accepted.connect(self.save_values)


    def enable_disable_entire_gui(self):
        """Enables and disables respective GUI elements depending on what the user clicks."""
        pass

    def get_dataref_array(self, dataclass, datatype, *args):
        """Retrieves a list of data files loaded into the current scenario for display in the GUI

        :param dataclass: the data class i.e. spatial, temporal, qualitative
        :param datatype: the name that goes with the data class e.g. landuse, population, etc.
        """
        dataref_array = [["(no map selected)"], [""]]    # index 0:filenames, index 1:object_reference
        for dref in self.active_scenario.get_data_reference(dataclass):
            if dref.get_metadata("parent") == datatype:
                if len(args) > 0 and datatype in ["Boundaries", "Water Bodies", "Built Infrastructure", "Overlays"]:
                    if dref.get_metadata("sub") != args[0]:
                        continue
                dataref_array[0].append(dref.get_metadata("filename"))
                dataref_array[1].append(dref.get_data_id())
        return dataref_array

    def pre_fill_parameters(self):
        """Pre-filling method, will set up the module with all values contained in the pre-loaded parameter file or
        settings. This method is called when the Combo box index is changed or a file has been browsed and entered into
        the text box on the GENERALS tab."""
        pass    # [TO DO]

    def change_active_module(self):
        """Searches for the active module based on the simulation year combo box and updates the GUI."""
        # Send message box to user to ask whether to save current parameters
        if self.gui_state == "ready":
            prompt_msg = "You are about to change the time period, do you wish to save changes made to your parameters " \
                         "for the current time step?"
            reply = QtWidgets.QMessageBox.question(self, "Changing Time Period", prompt_msg,
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                           QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                self.save_values()
            elif reply == QtWidgets.QMessageBox.No:
                pass
            else:
                return

        # Retrieve the Urbplanbb() Reference corresponding to the current year
        self.module = self.active_scenario.get_module_object("URBPLAN", self.ui.year_combo.currentIndex())
        self.setup_gui_with_parameters()
        return True

    def setup_gui_with_parameters(self):
        """Fills in all parameters belonging to the module for the current year."""



        pass
        return True

    def save_values(self):
        """Saves current values to the corresponding module's instance in the active scenario."""
        pass

        return True
