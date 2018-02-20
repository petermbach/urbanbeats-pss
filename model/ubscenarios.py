# -*- coding: utf-8 -*-
"""
@file   ubscenarios.py
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

        self.__scenariometadata = { "name": "<enter scenario name>",
                                    "type": "STATIC",
                                    "narrative": "<enter scenario description>",
                                    "startyear": "2018",
                                    "endyear": "2068",
                                    "dt": 1,
                                    "benchmarks": 1,
                                    "filename": "<enter a naming convention for outputs>",
                                    "usescenarioname": 0 }

        self.__modulesbools = {"SPATIAL": 1, "CLIMATE": 1, "URBDEV": 0, "URBPLAN": 0,
                          "SOCIO": 0, "MAP": 0, "REG": 0, "INFRA": 0, "PERF": 0,
                          "IMPACT": 0, "DECISION": 0}

        self.__spatial_data = [] # a list of map data to be used, holds the data references.
        self.__time_series_data = []   # a list of time series data to be used in the scenario or stored.
        self.__qual_data = []   # a list of qualitative data to be used in the scenario

        self.__modules = { "SPATIAL" : [], "CLIMATE" : [], "URBDEV": [], "URBPLAN": [],
                           "SOCIO" : [], "MAP": [], "REG": [], "INFRA": [], "PERF": [],
                           "IMPACT": [], "DECISION": [] }

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

    def setup_scenario(self, setupdata):
        """Initializes the scenario with the setup data provided by the user."""

        pass

    def add_data_to_scenario(self, dataclass, dref):
        """Adds a data set from the data library of type UrbanBeatsDataReference() to the current
        list of data sets available to that scenario.

        :param dataclass: one of three classes "spatial", "temporal", "qualitative"
        :param dref: the UrbanBeatsDataReference() object.
        :return: False if the data already exists, i.e. the method does nothing. True otherwise
        """
        if self.has_dataref(dref.get_dataID()):
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
                if datanumID == dataset[i].get_dataID():
                    return True
        return False    # Else, return false if all tests fail

    def run(self):
        pass

