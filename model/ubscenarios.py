# -*- coding: utf-8 -*-
"""
@file   ubscenarios.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2018  Peter M. Bach

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
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import threading

# --- URBANBEATS LIBRARY IMPORTS ---
import modules.md_decisionanalysis as md_decisionanalysis
import modules.md_climatesetup as md_climatesetup
import modules.md_delinblocks as md_delinblocks
import modules.md_impactassess as md_impactasess
import modules.md_perfassess as md_perfassess
import modules.md_regulation as md_regulation
import modules.md_socioecon as md_socioecon
import modules.md_spatialmapping as md_spatialmapping
import modules.md_techplacement as md_techplacement
import modules.md_urbandev as md_urbandev
import modules.md_urbplanbb as md_urbplanbb

# --- SCENARIO CLASS DEFINITION ---
class UrbanBeatsScenario(object):
    """The static parent class that contains the basic definition of the
    scenario for UrbanBEATS simulations. Other scenario classes inherit from
    this class and define the type of scenario (i.e. static, dynamic, benchmark)
    """
    def __init__(self, simulation, datalibrary, projectlog):
        self.simulation = simulation
        self.datalibrary = datalibrary
        self.projectlog = projectlog
        self.projectpath = simulation.get_project_path()

        self.__scenariometadata = {"name": "My UrbanBEATS Scenario",
                                   "type": "STATIC",
                                   "narrative": "<A description of my scenario>",
                                   "startyear": 2018,
                                   "endyear": 2068,
                                   "dt": 1,
                                   "dt_irregular": 0,
                                   "yearlist": [],
                                   "benchmarks": 100,
                                   "filename": "<enter a naming convention for outputs>",
                                   "usescenarioname": 0}

        self.__modulesbools = {"SPATIAL": 1, "CLIMATE": 1, "URBDEV": 0, "URBPLAN": 0,
                          "SOCIO": 0, "MAP": 0, "REG": 0, "INFRA": 0, "PERF": 0,
                          "IMPACT": 0, "DECISION": 0}

        self.__spatial_data = [] # a list of map data to be used, holds the data references.
        self.__time_series_data = []   # a list of time series data to be used in the scenario or stored.
        self.__qual_data = []   # a list of qualitative data to be used in the scenario

        self.__modules = {"SPATIAL" : [], "CLIMATE" : [], "URBDEV": [], "URBPLAN": [],
                           "SOCIO" : [], "MAP": [], "REG": [], "INFRA": [], "PERF": [],
                           "IMPACT": [], "DECISION": []}

        self.__dt_array = []
        # A dictionary of arrays, containing modules, depending on scenario type

    def get_simulation_years(self):
        """Retrieves the list of simulation years to use."""
        return self.__dt_array

    def get_module_object(self, modulecat, dt_index):
        """Returns the active module instance from self.__modules based on the key 'modulecat' and the index from
        self.__dt_array i.e. the simulation year. In the GUI, this directly corresponds to the combo box index.

        :param modulecat: module category e.g. SPATIAL, CLIMATE, URBDEV, etc.
        :param index: the list index to look up for the module.
        :return: the instantiated module object e.g. DelinBlocks() or UrbPlanBB()
        """
        try:
            return self.__modules[modulecat][dt_index]
        except KeyError:
            print "Error, cannot find module instance!"
            return None

    def setup_scenario(self):
        """Initializes the scenario with the setup data provided by the user."""
        print "setting up scenario"
        inputs = [self.simulation, self, self.datalibrary, self.projectlog]
        self.__dt_array = []
        if self.get_metadata("type") in ["STATIC", "BENCHMARK"]:
            self.__dt_array.append(self.get_metadata("startyear"))
        else:
            currentyear = self.get_metadata("startyear")
            while currentyear < self.get_metadata("endyear"):
                self.__dt_array.append(currentyear)
                currentyear += self.get_metadata("dt")
        print self.__dt_array

        # INSTANTIATE MODULES
        for i in self.__dt_array:
            if self.check_is_module_active("SPATIAL"):
                self.__modules["SPATIAL"].append(
                    md_delinblocks.DelinBlocks(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("CLIMATE"):
                self.__modules["CLIMATE"].append("YES")
            if self.check_is_module_active("URBDEV"):
                self.__modules["URBDEV"].append("YES")
            if self.check_is_module_active("URBPLAN"):
                self.__modules["URBPLAN"].append("YES")
            if self.check_is_module_active("SOCIO"):
                self.__modules["SOCIO"].append("YES")
            if self.check_is_module_active("MAP"):
                self.__modules["MAP"].append("YES")
            if self.check_is_module_active("REG"):
                self.__modules["REG"].append("YES")
            if self.check_is_module_active("INFRA"):
                self.__modules["INFRA"].append("YES")
            if self.check_is_module_active("PERF"):
                self.__modules["PERF"].append("YES")
            if self.check_is_module_active("IMPACT"):
                self.__modules["IMPACT"].append("YES")
            if self.check_is_module_active("DECISION"):
                self.__modules["DECISION"].append("YES")
        return True

    def add_data_reference(self, dataref):
        """Adds the data reference to the scenario's data store depending on its class."""
        if dataref.get_metadata("class") == "spatial":
            self.__spatial_data.append(dataref)
        elif dataref.get_metadata("class") == "temporal":
            self.__time_series_data.append(dataref)
        else:
            self.__qual_data.append(dataref)

    def get_data_reference(self, dataclass):
        """Returns a list of data references for a specific class of data set.

        :param dataclass: 'spatial', 'temporal' or 'qualitative' as input string.
        :return: list type object containing UrbanBeatsDataReference() objects
        """
        if dataclass == "spatial":
            return self.__spatial_data
        elif dataclass == "temporal":
            return self.__time_series_data
        else:
            return self.__qual_data

    def remove_data_reference(self, dataID):
        """Removes the dataref object from the corresponding list. Scans the list for the
        corresponding data reference until it finds it and then pops it from the list.

        :param dataID: the data reference unique identifier.
        """
        for i in range(len(self.__spatial_data)):
            if self.__spatial_data[i].get_data_id() == dataID:
                self.__spatial_data.pop(i)
                return
        for i in range(len(self.__time_series_data)):
            if self.__time_series_data[i].get_data_id() == dataID:
                self.__time_series_data.pop(i)
                return
        for i in range(len(self.__qual_data)):
            if self.__qual_data[i].get_data_id() == dataID:
                self.__qual_data.pop(i)
                return

    def create_dataset_file_list(self):
        """Creates a table of the data contained in the scenario with the attributes:
        dataID, filename, parent classification, sub-classification. Returns a list
        object.

        :return: list type containing metadata of the loaded data files."""
        datalist = []   # [dataID, filename, parent, sub]
        for dset in [self.__spatial_data, self.__time_series_data, self.__qual_data]:
            for dref in dset:
                dataid = dref.get_data_id()
                filename = dref.get_metadata("filename")
                filepath = dref.get_data_file_path()
                category = dref.get_metadata("parent")
                sub = dref.get_metadata("sub")
                if sub == "<undefined>":
                    sub = "-"
                datalist.append([dataid, filename, filepath, category, sub])
        return datalist

    def check_is_module_active(self, modulename):
        """Checks if a particular module is currently active in the scenario. Returns false if
        the module is not active.

        :param modulename: the short-form name of each module e.g. URBPLAN, PERF, etc.
        :return: True if module is active, false if inactive.
        """
        if self.__modulesbools[modulename] == 1:
            return True
        else:
            return False

    def set_module_active(self, modulename):
        """Actives a module. Note that this does not go both ways. The scenario creation and module
        activation is done only once, cannot be changed for that scenario to prevent me from doing
        more work, haha."""
        self.__modulesbools[modulename] = 1

    def set_metadata(self, parname, value):
        """Used to change a parameter in the scenario metadata.

        :param parname: the metadata parameter name, dictionary key.
        :param value: value of the parameter
        """
        self.__scenariometadata[parname] = value

    def get_metadata(self, parname):
        """Returns the parameter value from the metadata of the scenario.

        :param parname: parameter name of str type.
        """
        try:
            return self.__scenariometadata[parname]
        except KeyError:
            return None

    def add_data_to_scenario(self, dataclass, dref):
        """Adds a data set from the data library of type UrbanBeatsDataReference() to the current
        list of data sets available to that scenario.

        :param dataclass: one of three classes "spatial", "temporal", "qualitative"
        :param dref: the UrbanBeatsDataReference() object.
        :return: False if the data already exists, i.e. the method does nothing. True otherwise
        """
        if self.has_dataref(dref.get_data_id()):
            return False
        else:
            if dataclass == "spatial":
                self.__spatial_data.append(dref)
            elif dataclass == "temporal":
                self.__time_series_data.append(dref)
            else:
                self.__qual_data.append(dref)
        return True

    def has_dataref(self, datanumID):
        """Scans all three arrays to see if the data set has already been added to the project.
        Note that the function simply scans all three lists and checks for an existing data ID.

        :param datanumID: the unique identifier ID of the data set being checked.
        :return: True if the data is already in one of the lists, False otherwise.
        """
        for dataset in [self.__spatial_data, self.__time_series_data, self.__qual_data]:
            for i in range(len(dataset)):
                if datanumID == dataset[i].get_data_id():
                    return True
        return False    # Else, return false if all tests fail

    def run(self):
        pass

