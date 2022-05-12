r"""
@file   mod_landuse_import.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2017-2022  Peter M. Bach

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
__copyright__ = "Copyright 2017-2022. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---

# --- URBANBEATS LIBRARY IMPORTS ---
import os

import model.progref.ubglobals as ubglobals

# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets
from .exportassetsdialog import Ui_ExportAssetsDialog


# --- MAIN GUI FUNCTION ---
class AssetExportLaunch(QtWidgets.QDialog):
    def __init__(self, main, simulation, parent=None):
        """ Launches the asset export dialog, allows user customization and calls the simulation's export function upon
        completion with the parameters entered.

        :param main: The main runtime object --> the main GUI
        :param simulation: The active simulation object --> main.get_active_simulation_object()
        :param parent: None
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_ExportAssetsDialog()
        self.ui.setupUi(self)

        # --- CONNECTIONS WITH CORE AND GUI ---
        self.maingui = main     # the main runtime
        self.simulation = simulation    # the active object in the scenario manager
        self.asset_col = simulation.get_global_asset_collection()
        self.export_path = self.simulation.get_project_path()+"/output/"

        # --- SETUP ALL DYNAMIC COMBO BOXES ---
        self.ui.asset_col_combo.clear()
        self.ui.asset_col_combo.addItem("(select asset collection)")
        [self.ui.asset_col_combo.addItem(str(asset_name)) for asset_name in self.asset_col.keys()]
        self.ui.asset_col_combo.setCurrentIndex(0)      # Use the 0th index

        self.ui.export_filename_line.setText("(define a file naming convention)")
        self.ui.export_metadata_check.setChecked(0)
        self.ui.export_csvtable_check.setChecked(0)
        self.ui.exportdir_open_check.setChecked(0)
        self.ui.export_rasterfmt_combo.setCurrentIndex(0)
        self.ui.export_seriesfmt_combo.setCurrentIndex(0)

        # PROJECT FOLDER
        self.ui.exportdir_project_radio.setChecked(1)
        self.ui.exportdir_line.setText(self.export_path)
        if self.ui.exportdir_project_radio.isChecked():
            self.ui.exportdir_line.setEnabled(0)
        else:
            self.ui.exportdir_line.setEnabled(1)

        # SIGNALS AND SLOTS
        self.ui.asset_col_combo.currentIndexChanged.connect(self.update_gui_to_new_collection)
        self.ui.select_all_check.clicked.connect(self.check_uncheck_asset_items)
        self.ui.exportdir_project_radio.clicked.connect(self.update_project_folder)
        self.ui.exportdir_custom_radio.clicked.connect(self.update_project_folder)
        self.ui.export_button.clicked.connect(self.export_asset_collection)

        self.update_gui_to_new_collection()

    def update_gui_to_new_collection(self):
        self.ui.asset_col_list.clear()
        if self.ui.asset_col_combo.currentIndex() == 0:
            self.ui.export_filename_line.setText("(define a file naming convention)")
            self.ui.select_all_check.setChecked(1)
            return True
        asset_collection = self.asset_col[self.ui.asset_col_combo.currentText()]
        asset_types = asset_collection.get_asset_types()
        for at in asset_types.keys():
            item = QtWidgets.QListWidgetItem()
            item.setText(at)
            item.setCheckState(QtCore.Qt.Checked)
            self.ui.asset_col_list.addItem(item)
        self.ui.select_all_check.setChecked(1)
        self.ui.export_filename_line.setText(self.ui.asset_col_combo.currentText().replace(" ", "_"))

    def check_uncheck_asset_items(self):
        for i in range(self.ui.asset_col_list.count()):
            if self.ui.select_all_check.isChecked():  # Check all table items
                self.ui.asset_col_list.item(i).setCheckState(QtCore.Qt.Checked)
            else:
                self.ui.asset_col_list.item(i).setCheckState(QtCore.Qt.Unchecked)

    def update_project_folder(self):
        if self.ui.exportdir_project_radio.isChecked():
            self.export_path = self.simulation.get_project_path() + "/output/"
            self.ui.exportdir_line.setEnabled(0)
        else:
            message = "Select Export Directory"
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
            if folderpath:
                self.export_path = folderpath
            self.ui.exportdir_line.setEnabled(1)

        self.ui.exportdir_line.setText(self.export_path)

    def export_asset_collection(self):
        # CHECK ALL CONDITIONS FIRST
        if self.ui.asset_col_combo.currentIndex() == 0:     # If no asset collection selected...
            prompt_msg = "Please select an asset collection to export!"
            QtWidgets.QMessageBox.warning(self, "Nothing to export", prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        no_chars = False        # If illegal characters in file name
        for char in ubglobals.NOCHARS:
            if char in self.ui.export_filename_line.text():
                no_chars = True
        if no_chars:
            prompt_msg = "Please enter a valid file naming convention without special characters!"
            QtWidgets.QMessageBox.warning(self, "Invalid File Naming Convention", prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        if not os.path.exists(self.ui.exportdir_line.text()):       # If path does not exist...
            prompt_msg = "Select a valid directory for the export"
            QtWidgets.QMessageBox.warning(self, "Invalid Directory", prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        # COMPILE PARAMETERS
        parameters = {"path": self.export_path, "assets": self.ui.asset_col_combo.currentText()}
        typenames = []
        for i in range(self.ui.asset_col_list.count()):
            if self.ui.asset_col_list.item(i).checkState() == QtCore.Qt.Checked:
                typenames.append(self.ui.asset_col_list.item(i).text())
        parameters["typenames"] = typenames
        parameters["filename"] = self.ui.export_filename_line.text()
        parameters["metadata"] = int(self.ui.export_metadata_check.isChecked())
        parameters["csv"] = int(self.ui.export_csvtable_check.isChecked())
        parameters["rasterfmt"] = self.ui.export_rasterfmt_combo.currentText()
        parameters["seriesfmt"] = self.ui.export_seriesfmt_combo.currentText()
        parameters["opendir"] = int(self.ui.exportdir_open_check.isChecked())
        self.simulation.export_assets(parameters)
        self.accept()
