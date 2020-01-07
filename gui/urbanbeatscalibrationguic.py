r"""
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

# --- PYTHON LIBRARY IMPORTS ---
import sys
import os
import webbrowser
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

# --- URBANBEATS LIBRARY IMPORTS ---
import model.progref.ubglobals as ubglobals
import model.ublibs.ubmethods as ubmethods
from .urbanbeatscalibration import Ui_CalibrationViewer


# --- ADD DATA DIALOG ---
class LaunchCalibrationViewer(QtWidgets.QDialog):
    """Class definition for the add data dialog window for importing and managing data."""
    def __init__(self, main, simulation, scenario, parent=None):
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
        self.scenario = scenario      # the active scenario to be featured in the calibration viewer

        self.enable_disable_gui()
        if self.scenario is None:
            self.map_attr = None
            self.blockslist = None
        else:
            self.map_attr = scenario.get_asset_with_name("MapAttributes")
            blocks = self.scenario.get_assets_with_identifier("BlockID")
            self.blockslist = []
            for i in range(len(blocks)):
                if not blocks[i].get_attribute("Status"):
                    continue
                self.blockslist.append(blocks[i])   # This blocks list removes all status zero blocks

        self.ui.set_param_combo.setCurrentIndex(0)
        self.ui.set_aggregation_combo.setCurrentIndex(0)
        self.ui.set_datasource_combo.setCurrentIndex(0)
        self.ui.plottype_combo.setCurrentIndex(0)

        self.attribute_keys = {"allots": ["ResAllots"], "houses": ["ResHouses", "HDRFlats"], "tia": ["Blk_TIA"],
                               "roofarea": ["ResRoof", "HDRRoofA"], "tif": ["Blk_TIF"], "demand": ["Blk_WD"],
                               "ww": ["Blk_WW"]}

        # --- STATE VARIABLES ---
        self.active_calib_data = {}     # Active calibration data, dictionary keys represent BlockIDs
        self.active_model_data = {}
        self.active_param = None
        self.active_agg_level = None
        self.active_obs_mod = [[],[],[]]    # [ Key index, Observed, Modelled ]
        self.active_metrics = []

        # --- SIGNALS AND SLOTS ---
        self.ui.set_param_combo.currentIndexChanged.connect(self.setup_calibration)
        self.ui.set_aggregation_combo.currentIndexChanged.connect(self.setup_calibration)
        self.ui.set_datasource_combo.currentIndexChanged.connect(self.setup_calibration)

        self.ui.set_data_load.clicked.connect(self.load_calibration_data)
        self.ui.set_data_export.clicked.connect(self.export_current_data_table)
        self.ui.set_data_table.itemChanged.connect(self.refresh_plot)
        self.ui.set_data_table.itemChanged.connect(self.refresh_results)

        self.ui.set_eval_nash.clicked.connect(self.refresh_results)
        self.ui.set_eval_rmse.clicked.connect(self.refresh_results)
        self.ui.set_eval_error.clicked.connect(self.refresh_results)

        self.ui.out_export.clicked.connect(self.export_current_obs_mod_results)
        self.ui.plottype_combo.currentIndexChanged.connect(self.refresh_plot)
        self.ui.set_eval_11line.clicked.connect(self.refresh_plot)

    def enable_disable_gui(self):
        """Disables the GUI and makes it inaccessible if no scenario is currently selected."""
        if self.scenario is None:
            self.ui.calibrationSettings.setEnabled(0)
            self.ui.calibrationResults.setEnabled(0)
            self.ui.calibrationWebView.setEnabled(0)
        else:
            self.ui.calibrationSettings.setEnabled(1)
            self.ui.calibrationResults.setEnabled(1)
            self.ui.calibrationWebView.setEnabled(1)
            self.ui.set_data_table.setRowCount(0)
            self.ui.out_box.clear()
            self.ui.calibrationView.setHtml("")
            self.ui.set_data_load.setEnabled(0)
            self.ui.set_data_export.setEnabled(0)
            self.ui.out_export.setEnabled(0)
            self.ui.plot_controls_widget.setEnabled(0)
        return True

    def setup_calibration(self):
        """Based on the status of the three combo boxes, the GUI attempts to set up the calibration as far as possible.
        The function immediately quits if it realises it cannot. If it gets to the end, it updates the plots."""
        # PRE-STEP: Clear the data table, clear the results box and clear the viewer
        self.ui.set_data_table.setRowCount(0)
        self.ui.out_box.clear()
        self.ui.calibrationView.setHtml("")
        self.ui.set_data_load.setEnabled(0)
        self.ui.set_data_export.setEnabled(0)
        self.ui.out_export.setEnabled(0)
        self.ui.plot_controls_widget.setEnabled(0)

        # Step 0 - Do we even have data
        if self.map_attr is None:
            prompt_msg = "There is no asset data for this scenario! Please run the simulation first!"
            QtWidgets.QMessageBox.warning(self, 'No Asset Data', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        # Step 1 - Parameter Type
        parametertypes = [None, "allot", "houses", "tia", "tif", "roofarea", "demand", "ww"]
        self.active_param = parametertypes[self.ui.set_param_combo.currentIndex()]
        if self.active_param is None:
            return True
        elif self.active_param in ["allot", "houses", "tia", "tif", "roofarea"] and \
            not self.map_attr.get_attribute("HasURBANFORM"):
            prompt_msg = "Urban Planning Module was not run for this case study. Please run this module first!"
            QtWidgets.QMessageBox.warning(self, 'No Urban Planning Data', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True
        elif self.active_param in ["demand", "ww"] and not self.map_attr.get_attribute("HasSPATIALMAPPING"):
            prompt_msg = "Spatial Mapping Module was not run for this case study. Please run this module first!"
            QtWidgets.QMessageBox.warning(self, 'No Spatial Mapping Data', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True
        else:
            pass

        # Step 2 - Aggregation Level
        agg_levels = [None, "Total", "Region", "Suburb", "PlanZone", "Block"]
        self.active_agg_level = agg_levels[self.ui.set_aggregation_combo.currentIndex()]
        if self.active_agg_level is None:
            return True
        elif self.active_agg_level == "Region" and not self.map_attr.get_attribute("HasGEOPOLITICAL"):
            self.ui.set_aggregation_combo.setCurrentIndex(0)
            prompt_msg = "The current simulation does not contain information on Geopolitical Regions. " \
                         "Please choose another aggregation level!"
            QtWidgets.QMessageBox.warning(self, 'No Geopolitical Data', prompt_msg, QtWidgets.QMessageBox.Ok)
        elif self.active_agg_level == "Suburb" and not self.map_attr.get_attribute("HasSUBURBS"):
            prompt_msg = "The current simulation does not contain information on Suburban Regions. " \
                         "Please choose another aggregation level!"
            QtWidgets.QMessageBox.warning(self, 'No Suburban Data', prompt_msg, QtWidgets.QMessageBox.Ok)
        elif self.active_agg_level == "PlanZone" and not self.map_attr.get_attribute("HasPLANZONES"):
            prompt_msg = "The current simulation does not contain information on Planning Zones. " \
                         "Please choose another aggregation level!"
            QtWidgets.QMessageBox.warning(self, 'No Planning Zone Data', prompt_msg, QtWidgets.QMessageBox.Ok)
        else:
            pass

        # Step 3 - Data Source
        datasources = [None, "User", "MUSIC", "Sponge"]
        ds = datasources[self.ui.set_datasource_combo.currentIndex()]
        if ds is None:
            return True
        elif ds == "User":
            self.ui.set_data_load.setEnabled(1)
            self.setup_data_table()
        elif ds == "MUSIC":
            self.ui.set_data_load.setEnabled(0)
            if self.active_param in ["allot", "houses", "roofarea", "demand", "ww"]:
                prompt_msg = "There is no data for generating a hypothetical data set for the current metric. " \
                             "Select another parameter"
                QtWidgets.QMessageBox.warning(self, 'Non-compatible data', prompt_msg, QtWidgets.QMessageBox.Ok)
                return True
            elif self.active_param == "tia":
                calibdata = self.generate_imp_musicmodellingguide("Area")
            else:
                calibdata = self.generate_imp_musicmodellingguide("Fraction")
            self.active_calib_data = calibdata
            self.setup_data_table(calibdata)
        elif ds == "Sponge":
            self.ui.set_data_load.setEnabled(0)
            prompt_msg = "Guide currently does not exist. Select another option."
            QtWidgets.QMessageBox.warning(self, 'Not yet available', prompt_msg, QtWidgets.QMessageBox.Ok)
            self.generate_hypothetical_dataset("Sponge")
            return True
        else:
            pass
        self.ui.set_data_export.setEnabled(1)   # If we've made it this far, then we have the ability to export

        # Step 4 - Check if the data can be displayed
        self.ui.out_export.setEnabled(1)        # Enable the exporting of results
        self.ui.plot_controls_widget.setEnabled(1)  # Enable the plot control widgets
        self.refresh_results()      # Can the data be presented as results?
        self.refresh_plot()         # Can the data be plotted?

    def setup_data_table(self, calibdata=None):
        """Sets up the data table for the calibration."""
        self.ui.set_data_table.setRowCount(0)
        if self.active_agg_level == "Block":
            for i in range(len(self.blockslist)):
                self.ui.set_data_table.insertRow(0)
                twi = QtWidgets.QTableWidgetItem()
                twi.setText("BlockID"+str(self.blockslist[i].get_attribute("BlockID")))
                self.ui.set_data_table.setItem(0, 0, twi)
                if calibdata is not None:
                    twi = QtWidgets.QTableWidgetItem()
                    try:
                        twi.setText(str(round(calibdata["BlockID" +
                                                        str(self.blockslist[i].get_attribute("BlockID"))], 2)))
                    except KeyError:
                        continue
                    self.ui.set_data_table.setItem(0, 1, twi)
        elif self.active_agg_level == "Total":
            twi = QtWidgets.QTableWidgetItem()
            twi.setText("Case Study")
            self.ui.set_data_table.insertRow(0)
            self.ui.set_data_table.setItem(0, 0, twi)
            if calibdata is not None:
                twi = QtWidgets.QTableWidgetItem()
                try:
                    twi.setText(str(round(calibdata["Case Study"], 2)))
                except KeyError:
                    pass
                self.ui.set_data_table.setItem(0, 1, twi)
        elif self.active_agg_level == "PlanZone":
            names = ubmethods.get_subregions_subset_from_blocks("PlanZone", self.blockslist)
            for n in names:
                twi = QtWidgets.QTableWidgetItem()
                twi.setText(str(n))
                self.ui.set_data_table.insertRow(0)
                self.ui.set_data_table.setItem(0, 0, twi)
                if calibdata is not None:
                    twi = QtWidgets.QTableWidgetItem()
                    try:
                        twi.setText(str(round(calibdata[n], 2)))
                    except KeyError:
                        continue
                    self.ui.set_data_table.setItem(0, 1, twi)
        elif self.active_agg_level == "Region":
            names = ubmethods.get_subregions_subset_from_blocks("Region", self.blockslist)
            for n in names:
                twi = QtWidgets.QTableWidgetItem()
                twi.setText(str(n))
                self.ui.set_data_table.insertRow(0)
                self.ui.set_data_table.setItem(0, 0, twi)
                if calibdata is not None:
                    twi = QtWidgets.QTableWidgetItem()
                    try:
                        twi.setText(str(round(calibdata[n], 2)))
                    except KeyError:
                        continue
                    self.ui.set_data_table.setItem(0, 1, twi)
        elif self.active_agg_level == "Suburb":
            names = ubmethods.get_subregions_subset_from_blocks("Suburb", self.blockslist)
            for n in names:
                twi = QtWidgets.QTableWidgetItem()
                twi.setText(str(n))
                self.ui.set_data_table.insertRow(0)
                self.ui.set_data_table.setItem(0, 0, twi)
                if calibdata is not None:
                    twi = QtWidgets.QTableWidgetItem()
                    try:
                        twi.setText(str(round(calibdata[n], 2)))
                    except KeyError:
                        continue
                    self.ui.set_data_table.setItem(0, 1, twi)

    def load_calibration_data(self):
        """Reads the calibration data file and returns an array.

        :param filename: filename containing the calibration data set split into two columns: Block ID and Value
        :return: final array [ [BlockID], [Value] ]
        """
        message = "Browse for Calibration Data Set (comma-separated)..."
        calibfile, _filter = QtWidgets.QFileDialog.getOpenFileName(self, message, os.curdir,
                                                                   "Comma-delimited (*.csv *.txt)")
        self.scenario.set_active_calibration_data_file(self.active_param, self.active_agg_level, calibfile)
        if calibfile:       # IF TRUE, READ THE DATA FILE
            rawdata = []
            calibdata = {}
            f = open(calibfile, 'r')
            for lines in f:
                rawdata.append(lines.split(','))
            f.close()
            for i in range(len(rawdata)):
                try:
                    calibdata[rawdata[i][0]] = float(rawdata[i][1])
                except ValueError:
                    pass
            self.active_calib_data = calibdata
            self.setup_data_table(calibdata)
        else:
            return None

    def export_current_data_table(self):
        """Exports the current data table to a .csv file."""
        datatype = "CSV (*.csv)"
        message = "Export to .csv file, choose location..."
        datafile, _filter = QtWidgets.QFileDialog.getSaveFileName(self, message, os.curdir, datatype)
        if datafile:
            x_data = []
            y_data = []
            for i in range(self.ui.set_data_table.rowCount()):
                x_data.append(str(self.ui.set_data_table.item(i, 0).text()))
                y_data.append(str(self.ui.set_data_table.item(i, 1).text()))
            f = open(datafile, 'w')
            for i in range(len(x_data)):
                f.write(x_data[i]+","+y_data[i]+"\n")
            f.close()
            prompt_msg = "Function successfully exported!"
            QtWidgets.QMessageBox.information(self, 'Export Complete', prompt_msg, QtWidgets.QMessageBox.Ok)
            self.scenario.set_active_calibration_data_file(self.active_param, self.active_agg_level, datafile)

    def generate_imp_musicmodellingguide(self, metric):
        """Generates an impervious area estimate from the Melbourne Water MUSIC Modelling Guidelines for the current
        Blocks List. Summarises this to regional scale if necessary.
        """
        block_size = self.map_attr.get_attribute("BlockSize")       # Needed for area vs. fraction calculation

        nonreslucmatrix = ["COM", "LI", "HI", "ORC", "CIV", "SVU", "TR", "RD", "PG", "REF", "UND", "NA",
                           "FOR", "AGR", "WAT"]     # Abbreviations for non-residential land uses

        dataset = {}    # Will hold the MW MMG Data Set
        rawdata = []
        f = open(self.maingui.rootfolder + "/ancillary/mw_mmg.cfg", 'r')
        for lines in f:
            rawdata.append(lines.split(','))
        f.close()
        for lines in range(len(rawdata)):
            dataset[str(rawdata[lines][0])] = rawdata[lines][1:]

        # Calculate impervious area for non-residential land uses block by block
        calibdata = {}      # Will hold the calibration data set
        for i in range(len(self.blockslist)):       # Scan all the Blocks
            asset = self.blockslist[i]
            blockID = "BlockID"+str(asset.get_attribute("BlockID"))
            if asset.get_attribute("Status") == 0:
                continue        # Check zero status

            calibdata[blockID] = 0.0     # Initialize the value

            # Non-Residential Land uses - add impervious area for current
            for luc in nonreslucmatrix:
                calibdata[blockID] += asset.get_attribute("pLU_"+luc) * float(dataset[luc][2])  # Grab the Median

            # Residential - figure out lot size first, then work out impervious area
            lotarea = asset.get_attribute("ResLotArea")
            if lotarea == 0 or lotarea is None:
                pass
            if lotarea < 350.0:
                calibdata[blockID] += asset.get_attribute("pLU_RES") * float(dataset["RES-350"][2])
            elif lotarea < 500.0:
                calibdata[blockID] += asset.get_attribute("pLU_RES") * float(dataset["RES-500"][2])
            elif lotarea < 800.0:
                calibdata[blockID] += asset.get_attribute("pLU_RES") * float(dataset["RES-800"][2])
            else:
                calibdata[blockID] += asset.get_attribute("pLU_RES") * float(dataset["RES-4000"][2])

            # HDR
            if asset.get_attribute("HDRFlats") not in [0, None]:
                calibdata[blockID] += asset.get_attribute("pLU_RES") * float(dataset["HDR"][2])

            if metric == "Area":    # Convert proportions to area
                calibdata[blockID] = calibdata[blockID] * asset.get_attribute("Active") * float(block_size) * float(
                    block_size)
            else:
                pass    # Fraction
        if self.active_agg_level == "Block":
            return calibdata
        elif self.active_agg_level == "Total":
            imptot = []
            activetot = []
            for i in range(len(self.blockslist)):
                imptot.append(calibdata["BlockID"+str(self.blockslist[i].get_attribute("BlockID"))])
                activetot.append(self.blockslist[i].get_attribute("Active"))
            if metric == "Area":
                return {"Case Study":sum(imptot)}
            elif metric == "Fraction":
                return {"Case Study": float(sum(imptot) / sum(activetot))}
            else:
                return None
        else:   # There is a smaller aggregation level...
            newcalibdata = {}
            agg_levels = ubmethods.get_subregions_subset_from_blocks(self.active_agg_level, self.blockslist)
            for i in agg_levels:    # Set up the dictionary
                newcalibdata[i] = [[], []]      # [ [imp_total], [activity] ]
            for i in range(len(self.blockslist)):   # Go through Blocks list and add data
                region = self.blockslist[i].get_attribute(self.active_agg_level)
                newcalibdata[region][0].append(calibdata["BlockID"+str(self.blockslist[i].get_attribute("BlockID"))])
                newcalibdata[region][1].append(self.blockslist[i].get_attribute("Active"))
            for i in newcalibdata.keys():       # Go region by region
                # For every region, do the summation
                if metric == "Area":
                    newcalibdata[i] = sum(newcalibdata[i][0])
                else:
                    numerator = []
                    for j in range(len(newcalibdata[i][0])):
                        numerator.append(newcalibdata[i][0][j] * newcalibdata[i][1][j])
                    newcalibdata[i] = float(sum(numerator) / sum(newcalibdata[i][1]))
            return newcalibdata     # Returns a dictionary with "Region": value

    def refresh_results(self):
        """Undertakes the whole calibration procedure of comparing the observed and modelled data. This method also
        writes the results to the results text box."""
        self.get_modelled_data()
        mod_N = len(self.active_model_data)
        obs_N = len(self.active_calib_data)
        keyindex = []
        mod = []
        obs = []
        for i in self.active_model_data.keys():
            if i not in self.active_calib_data.keys():
                continue
            else:
                keyindex.append(i)
                mod.append(self.active_model_data[i])
                obs.append(self.active_calib_data[i])
        self.active_obs_mod = [keyindex, obs, mod]
        pts_NC = max(mod_N - len(mod), obs_N - len(obs))
        err = []
        for i in range(len(mod)):
            err.append(abs(mod[i] - obs[i]))
        discrepancy_maxID = keyindex[err.index(max(err))]

        # Calculate evaluation statistics
        if self.ui.set_eval_nash.isChecked() and self.active_agg_level != "Total":
            nashE = self.calculate_nash_sutcliffe(obs, mod)
        else:
            nashE = "Not Calculated"
        if self.ui.set_eval_rmse.isChecked() and self.active_agg_level != "Total":
            rmse = self.calculate_rmse(obs, mod)
        else:
            rmse = "Not Calculated"
        if self.ui.set_eval_error.isChecked():
            avgerr, minerr, maxerr, e10, e30, e50 = self.calculate_relative_errors(obs, mod)
        else:
            avgerr, minerr, maxerr, e10, e30, e50 = "-", "-", "-", "-", "-", "-"

        self.generate_results_box_text(mod_N, obs_N, pts_NC, discrepancy_maxID,
                                       nashE, rmse, avgerr, minerr, maxerr, e10, e30, e50)
        self.active_metrics = [mod_N, obs_N, pts_NC, discrepancy_maxID, nashE, rmse, avgerr, minerr, maxerr,
                               e10, e30, e50]
        return True

    def get_modelled_data(self):
        """Sets the self.active_model_data variable with the modelled data for comparison with calibration data."""
        attnames = self.attribute_keys[self.active_param]   # The attributes to look up.
        self.active_model_data = {}
        if self.active_agg_level == "Total":    # I want the whole sum across the case study
            self.active_model_data["Case Study"] = 0.0
            adjustment = 0.0    # Holds the adjustment factor for 'tif'
            for i in range(len(self.blockslist)):
                for j in range(len(attnames)):
                    if self.active_param != "tif":
                        self.active_model_data["Case Study"] += self.blockslist[i].get_attribute(attnames[j])
                        adjustment = 1.0
                    else:
                        self.active_model_data["Case Study"] += self.blockslist[i].get_attribute(attnames[j]) * \
                                                                self.blockslist[i].get_attribute("Active")
                        adjustment += self.blockslist[i].get_attribute("Active")
            self.active_model_data["Case Study"] = float(self.active_model_data["Case Study"] / adjustment)
        elif self.active_agg_level == "Block":
            for i in range(len(self.blockslist)):
                blockid = "BlockID" + str(self.blockslist[i].get_attribute("BlockID"))
                self.active_model_data[blockid] = 0.0
                for j in range(len(attnames)):
                    self.active_model_data[blockid] += self.blockslist[i].get_attribute(attnames[j])
        else:   # Region based
            regionnames = ubmethods.get_subregions_subset_from_blocks(self.active_agg_level, self.blockslist)
            for n in regionnames:
                self.active_model_data[n] = 0.0
                subsetblocks = ubmethods.get_subset_of_blocks_by_region(self.active_agg_level, n, self.blockslist)
                adjustment = 0.0
                for i in range(len(subsetblocks)):
                    for j in range(len(attnames)):
                        if self.active_param != "tif":
                            self.active_model_data[n] += subsetblocks[i].get_attribute(attnames[j])
                            adjustment = 1.0
                        else:
                            self.active_model_data[n] += subsetblocks[i].get_attribute(attnames[j]) * \
                                                         subsetblocks[i].get_attribute("Active")
                            adjustment += subsetblocks[i].get_attribute("Active")
                self.active_model_data[n] = float(self.active_model_data[n] / adjustment)
        return True

    def export_current_obs_mod_results(self):
        """Exports the current observed and modelled results to a .csv file."""
        if len(self.active_calib_data) == 0:
            prompt_msg = "No calibration results to export yet!"
            QtWidgets.QMessageBox.warning(self, 'No Calibration Results', prompt_msg, QtWidgets.QMessageBox.Ok)
            return True

        datatype = "CSV (*.csv)"
        message = "Export to .csv file, choose location..."
        datafile, _filter = QtWidgets.QFileDialog.getSaveFileName(self, message, os.curdir, datatype)
        if datafile:
            f = open(datafile, 'w')
            f.write(self.ui.out_box.toPlainText())
            f.write("\n\n")
            f.write("Region_Name, Observed, Modelled\n")
            for i in range(len(self.active_obs_mod[0])):
                f.write(str(self.active_obs_mod[0][i]) + "," + str(self.active_obs_mod[1][i]) + "," +
                        str(self.active_obs_mod[2][i])+"\n")
            f.close()
            QtWidgets.QMessageBox.warning(self, "Export Complete",
                                          "Results for current calibration successfully exported!",
                                          QtWidgets.QMessageBox.Ok)
        return True

    def refresh_plot(self):
        """Plots the modelled vs. observed data on the plot. This function is called either when the combo boxes
        are updated or when the data table is updated or when the plot options are updated."""
        pass
        


        # def plotCalibrationScatter(self, obs, mod):
        #     """Plots a scatter plot showing the correlation of two of the selected attributes at the Block Level
        #     :return:
        #     """
        #     x_name = "Observed Data"
        #     y_name = "Modelled Data"
        #     title = str(self.ui.set_param_combo.currentText()) + " " + self.ui.set_totvalue_units.text()[7:]
        #
        #     x_values = obs
        #     y_values = mod
        #     datadict = {x_name + " vs. " + y_name: []}
        #     for i in range(len(x_values)):
        #         datadict[x_name + " vs. " + y_name].append([x_values[i], y_values[i]])
        #
        #     self.htmlscript = ubhighcharts.scatter_plot(self.ubeatsdir, title, x_name, y_name, 3, "", "", datadict)
        #     self.ui.calibrationView.setHtml(self.htmlscript)
        #



    def generate_results_box_text(self, mod_N, obs_N, pts_NC, maxDID, nashE, rmse, avgerr, minerr, maxerr,
                                  e10, e30, e50):
        """Generates a plain text string for the results viewer box based on the user-input parameters. These are all
        calculated based on the observed and calibrated data as well as the options selected.

        :param mod_N: modelled number of points
        :param obs_N: observed number of points
        :param pts_NC: number of points not compared
        :param maxDID: maximum discrepancy location
        :param nashE: Nash-Sutcliffe Coefficient of Efficiency
        :param rmse: Root-mean square error
        :param avgerr: average relative error
        :param minerr: minimum relative error
        :param maxerr: maximum relative error
        :param e10: number of points with errors less than 10%
        :param e30: number of points with errors less than 30%
        :param e50: number of points with errors less than 50%
        :return: a str() text
        """
        self.ui.out_box.clear()
        summaryline = ""
        summaryline += "Summary of Calibration: \n"
        summaryline += "---------------------------\n"

        # 1.1 General Reporting Stuff, data stats
        summaryline += "Observed Data Points: " + str(obs_N) + "\n"
        summaryline += "Modelled Data Points: " + str(mod_N) + "\n"
        summaryline += "Data Points not compared: " + str(pts_NC) + "\n\n"

        # 1.2 Goodness of Fit Criterion
        summaryline += "Largest Discrepancy: " + str(maxDID) + "\n\n"
        summaryline += "Nash-Sutcliffe E = " + str(nashE) + "\n"
        summaryline += "RMSE = " + str(rmse) + "\n"
        summaryline += "Average Relative Error = " + str(avgerr) + "%\n"
        summaryline += "Min. Relative Error = " + str(minerr) + "%\n"
        summaryline += "Max Relative Error = " + str(maxerr) + "%\n\n"
        summaryline += "Data Points with < 10% Error = " + str(e10) + "\n"
        summaryline += "Data Points with < 30% Error = " + str(e30) + "\n"
        summaryline += "Data Points with < 50% Error = " + str(e50) + "\n"
        self.ui.out_box.setPlainText(summaryline)
        return True

    def calculate_nash_sutcliffe(self, observed, modelled):
        """Calculates the Nash-Sutcliffe Coefficient of Efficiency, which indicates whether the average of a data
        set is a better predictor than a range o modelled values."""
        # 1 - sum(mod/obs diff squared) / sum(mod/modavg diff squared)
        modavg = np.average(modelled)
        omsq, mmsq = 0.0, 0.0
        for i in range(len(observed)):
            omsq += pow((observed[i] - modelled[i]), 2)
            mmsq += pow((modelled[i] - modavg), 2)
        return round((1.0 - (omsq / mmsq)), 2)

    def calculate_rmse(self, observed, modelled):
        """Calcualtes the root-mean-squared error between the observed and modelled data sets."""
        errordiff = 0
        for i in range(len(observed)):
            errordiff += pow((observed[i] - modelled[i]), 2)
        return round(np.sqrt(errordiff / float(len(observed))), 2)

    def calculate_relative_errors(self, observed, modelled):
        """Calcualtes the relative error between the observed and modelled data sets. Also returns a distribution of
        errors."""
        relErrors = []
        for i in range(len(observed)):
            if observed[i] == 0:
                relErrors.append(100.0)
            else:
                relErrors.append(abs(round((observed[i] - modelled[i]) / observed[i], 1) * 100.0))

        if len(relErrors) > 1:
            avgerr = np.average(relErrors)
            maxerr = np.max(relErrors)
            minerr = np.min(relErrors)

            counterr50 = 0
            counterr30 = 0
            counterr10 = 0
            for i in range(len(relErrors)):
                if relErrors[i] < 10.0:
                    counterr50 += 1
                    counterr30 += 1
                    counterr10 += 1
                elif relErrors[i] < 30.0:
                    counterr50 += 1
                    counterr30 += 1
                elif relErrors[i] < 50.0:
                    counterr50 += 1
            return round(avgerr, 2), round(minerr, 2), round(maxerr, 2), \
                   round(counterr10, 2), round(counterr30, 2), round(counterr50, 2)
        else:
            avgerr = relErrors[0]
            maxerr = relErrors[0]
            minerr = relErrors[0]
            return round(avgerr, 2), round(maxerr, 2), round(minerr, 2), "-", "-", "-"

    # [COMING SOON]
    def generate_imparea_spongecitiesguide(self):
        """Generates an impervious area estimate from the Sponge Cities Guidelines for the current Blocks List.
        Summarises this to regional scale if necessary."""
        pass

