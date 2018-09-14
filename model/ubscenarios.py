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
import gc
import os
import time
import xml.etree.ElementTree as ET  # XML parsing for loading scenario files
import ast  # Used for converting a string of a list into a list e.g. "[1, 2, 3, 4]" --> [1, 2, 3, 4]

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
        self.__observers = []
        self.simulation = simulation
        self.datalibrary = datalibrary
        self.projectlog = projectlog
        self.projectpath = simulation.get_project_path()

        self.__scenariometadata = {"name": "My UrbanBEATS Scenario",
                                   "type": "STATIC",
                                   "narrative": "(A description of my scenario)",
                                   "startyear": 2018,
                                   "endyear": 2068,
                                   "dt": 1,
                                   "dt_irregular": 0,
                                   "dt_array_parameter": [],
                                   "yearlist": [],
                                   "benchmarks": 100,
                                   "filename": "(enter a naming convention for outputs)",
                                   "usescenarioname": 0}

        self.__modulesbools = {"SPATIAL": 1, "CLIMATE": 1, "URBDEV": 0, "URBPLAN": 0,
                          "SOCIO": 0, "MAP": 0, "REG": 0, "INFRA": 0, "PERF": 0,
                          "IMPACT": 0, "DECISION": 0}

        self.__spatial_data = [] # a list of map data to be used, holds the data references.
        self.__time_series_data = []   # a list of time series data to be used in the scenario or stored.
        self.__qual_data = []   # a list of qualitative data to be used in the scenario

        # A dictionary of arrays, containing modules, depending on scenario type
        self.__modules = {"SPATIAL" : [], "CLIMATE" : [], "URBDEV": [], "URBPLAN": [],
                           "SOCIO" : [], "MAP": [], "REG": [], "INFRA": [], "PERF": [],
                           "IMPACT": [], "DECISION": []}

        self.__dt_array = []

        self.__assets = {}      # The collection of model assets that are stored for later retrieval, these
        self.__global_edge_list = []
        self.__global_point_list = []
        # can include: UBComponents(), Input Data, etc.

        self.__active_assets = None  # Will hold a reference to the active asset dictionary based on current dt

    def reset_scenario_runtime(self):
        """Resets the scenario such that runtime can be carried ou again"""
        self.__assets = {}
        self.__global_edge_list = []
        self.__global_point_list = []
        gc.collect()

    def append_point(self, pt):
        """ Adds a point tuple (x, y) to the global point list."""
        if pt not in self.__global_point_list:
            self.__global_point_list.append(pt)

    def get_point_list_id(self, pt):
        """Returns the index of the point pt in the global point list."""
        try:
            return self.__global_point_list.index(pt)
        except ValueError:
            return None

    def append_edge(self, ed):
        """ Adds an edge tuple ((x1, y1), (x2, y2)) to the global edge list."""
        if (ed[0], ed[1]) not in self.__global_edge_list or (ed[1], ed[0]) not in self.__global_edge_list:
            self.__global_edge_list.append(ed)

    def get_edge_id(self, ed):
        """Tries to locate the edge in the global edge list and return the index i.e. the ID of the edge. Tries
        both ((x1, y1), (x2, y2)) and ((x2, y2), (x1, y1))."""
        try:
            return self.__global_edge_list.index(ed)
        except ValueError:
            try:
                return self.__global_edge_list.index((ed[1], ed[0]))
            except ValueError:
                return None

    def add_asset(self, name, asset):
        """Adds a new asset object to the asset dictionary with the key 'name'."""
        self.__assets[name] = asset
        return True

    def get_asset_with_name(self, name):
        """Returns the asset within self.__assets with the key 'name'. Returns None if the asset does not exist."""
        try:
            return self.__assets[name]
        except KeyError:
            return None

    def get_asset_with_identifier(self, idstring, **kwargs):
        """Scans the complete Asset List and returns all assets with the idstring contained in their name
        e.g. BlockID contained in the name "BlockID1", "BlockID2", etc.)

        :param idstring: the part of the string to search the asset database for (e.g. "BlockID")
        :param **kwargs: 'assetcol' = {} custom dictionary of assets
        """
        pass

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
        # print "setting up scenario"
        inputs = [self.simulation, self, self.datalibrary, self.projectlog]
        self.__dt_array = []
        if self.get_metadata("type") in ["STATIC", "BENCHMARK"]:
            self.__dt_array.append(self.get_metadata("startyear"))
        elif self.get_metadata("dt_irregular"):
            self.__dt_array = self.get_metadata("dt_array_parameter")
        else:
            currentyear = self.get_metadata("startyear")
            while currentyear < self.get_metadata("endyear"):
                self.__dt_array.append(currentyear)
                currentyear += self.get_metadata("dt")

        # INSTANTIATE MODULES
        for i in self.__dt_array:
            if self.check_is_module_active("SPATIAL"):
                self.__modules["SPATIAL"].append(
                    md_delinblocks.DelinBlocks(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("CLIMATE"):
                self.__modules["CLIMATE"].append(
                    md_climatesetup.ClimateSetup(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("URBDEV"):
                self.__modules["URBDEV"].append(
                    md_urbandev.UrbanDevelopment(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("URBPLAN"):
                self.__modules["URBPLAN"].append(
                    md_urbplanbb.UrbanPlanning(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("SOCIO"):
                self.__modules["SOCIO"].append(
                    md_socioecon.SocioEconomics(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("MAP"):
                self.__modules["MAP"].append(
                    md_spatialmapping.SpatialMapping(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("REG"):
                self.__modules["REG"].append(
                    md_regulation.RegulationModule(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("INFRA"):
                self.__modules["INFRA"].append(
                    md_techplacement.Techplacement(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("PERF"):
                self.__modules["PERF"].append(
                    md_perfassess.PerformanceAssessment(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("IMPACT"):
                self.__modules["IMPACT"].append(
                    md_impactasess.ImpactAssess(inputs[0], inputs[1], inputs[2], inputs[3], i))
            if self.check_is_module_active("DECISION"):
                self.__modules["DECISION"].append(
                    md_decisionanalysis.DecisionAnalysis(inputs[0], inputs[1], inputs[2], inputs[3], i))

            # CREATE ASSETS SUPERSTRUCTURE
            self.__assets[str(i)] = {}
        return True

    def consolidate_scenario(self):
        """Creates an updated scenario_name.xml file of the current scenario including all module parameters."""
        scenario_fname = self.projectpath+"/scenarios/"+self.__scenariometadata["name"].replace(" ", "_")+".xml"

        f = open(scenario_fname, 'w')
        f.write('<URBANBEATSSCENARIO creator="Peter M. Bach" version="1.0">\n')

        f.write('\t<scenariometa>\n')
        smeta = self.get_metadata("ALL")
        for i in smeta.keys():
            f.write('\t\t<'+str(i)+'>'+str(smeta[i])+'</'+str(i)+'>\n')
        f.write('\t</scenariometa>\n')

        f.write('\t<scenariodata>\n')
        for i in [self.__spatial_data, self.__time_series_data, self.__qual_data]:
            for dref in i:
                f.write('\t\t<datarefid type="'+str(dref.get_metadata("class"))+'">'+str(dref.get_data_id())+'</datarefid>\n')
        f.write('\t</scenariodata>\n')

        f.write('\t<scenariomodules>\n')
        for i in self.__modulesbools.keys():
            # Data for all the modules. This includes: active/in-active, number of instances, parameters
            f.write('\t\t<' + str(i) + '>\n')     # <MODULENAME>
            f.write('\t\t\t<active>'+str(self.__modulesbools[i])+'</active>\n')
            f.write('\t\t\t<count>'+str(len(self.__modules[i]))+'</count>\n')
            for j in range(len(self.__modules[i])):     # Loop across keys to get the module objects for parameters
                f.write('\t\t\t<parameters index="'+str(j)+'">\n')
                curmod = self.__modules[i][j]   # The current module object
                parlist = curmod.get_module_parameter_list()
                for par in parlist.keys():
                    f.write('\t\t\t\t<'+str(par)+'>'+str(curmod.get_parameter(par))+'</'+str(par)+'>\n')
                f.write('\t\t\t</parameters>\n')

            f.write('\t\t</' + str(i) + '>\n')
        f.write('\t</scenariomodules>\n')

        f.write('</URBANBEATSSCENARIO>')
        f.close()

        # NOTE TO SELF: when you read from the .xml file, there will be a string list e.g. '[2008, 2009, 2010, ...]'
        # to convert this to a list, use import ast and then yearlist = ast.literal_eval('[2008, 2009, 2010, ...]')

    def setup_scenario_from_xml(self, filename):
        """Scans the scenarios folder and restores all scenarios based on the information contained in the .xml
        files if they exist."""
        # print self.projectpath + "/scenarios/" + filename
        f = ET.parse(self.projectpath+"/scenarios/"+filename)
        root = f.getroot()

        # Load metadata of the scenario
        metadata = {}       # Fill out self.__scenariometadata
        for child in root.find("scenariometa"):
            if child.tag in ["dt_array_parameter", "yearlist"]:
                metadata[child.tag] = ast.literal_eval(child.text)
            elif child.tag in ["startyear", "endyear", "dt", "dt_irregular", "usescenarioname", "benchmarks"]:
                metadata[child.tag] = int(child.text)
            else:
                metadata[child.tag] = child.text

        self.__scenariometadata = metadata

        # Collect data from data library, which should have been loaded by now
        for child in root.find("scenariodata"):
            if child.attrib["type"] == "spatial":
                self.__spatial_data.append(self.datalibrary.get_data_with_id(child.text))
            elif child.attrib["type"] == "temporal":
                self.__time_series_data.append(self.datalibrary.get_data_with_id(child.text))
            else:
                self.__qual_data.append(self.datalibrary.get_data_with_id(child.text))

        # Create modules and fill out the modules with parameters
        mdata = root.find("scenariomodules")
        for modname in self.__modulesbools.keys():
            mbool = int(mdata.find(modname).find("active").text)
            self.__modulesbools[modname] = mbool
        self.setup_scenario()   # Instantiates all modules

        # Loop through module information and set parameters
        for modname in self.__modules.keys():
            for instance in mdata.find(modname).findall("parameters"):
                m = self.get_module_object(modname, int(instance.attrib["index"]))
                for child in instance:
                    # Currently this does some explicit type casting based on the parameter types defined
                    m.set_parameter(child.tag, type(m.get_parameter(child.tag))(child.text))


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
        if parname == "ALL":
            return self.__scenariometadata
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

    def attach_observers(self, observers):
        """Assigns an array of observers to the Scenario's self.__observers variable."""
        self.__observers = observers

    def update_observers(self, message):
        """Sends the message to all observers contained in the core's observer list."""
        for observer in self.__observers:
            observer.update_observer(str(message))

    def run_scenario(self):
        # BEGIN THE SCENARIO'S SIMULATION
        self.update_observers("Scenario Start!")
        # time.sleep(1)
        if self.get_metadata("type") == "STATIC":
            while self.run_static_simulation():
                pass
            return False
        elif self.get_metadata("type") == "DYNAMIC":
            self.run_dynamic_simulation()
        else:
            self.run_benchmark_simulation()

    def run_static_simulation(self):
        """This function presents the logical module flow for a STATIC simulation."""
        # --- STEP 0: Begin by setting up the basic global variables ---
        self.update_observers("Scenario Type: STATIC")
        temp_directory = self.simulation.get_global_options("tempdir")
        self.update_observers("Current temp directory: "+str(temp_directory))
        #self.simulation.update_runtime_progress(5)
        # self.resetAssets()    # reset the Assets Vector

        # --- STATIC STEP 1: Block delineation ---
        #self.simulation.update_runtime_progress(10)
        delinblocks = self.get_module_object("SPATIAL", 0)
        delinblocks.attach(self.__observers)
        delinblocks.run_module()

        # --- STATIC STEP 2: Climate Setup ---
        # --- STATIC STEP 3: Urban Planning ---
        # --- STATIC STEP 4: Socio-Economic ---
        # --- STATIC STEP 5: Spatial Mapping ---
        # --- STATIC STEP 6: Regulation ---
        # --- STATIC STEP 7: Infrastructure ---
        # --- STATIC STEP 8: Performance ---
        # --- STATIC STEP 9: Impact ---
        # --- STATIC STEP 10: Decision Analysis ---
        # --- DATA EXPORT AND CLEANUP STEPS ---

        #self.simulation.update_runtime_progress(100)

    def run_dynamic_simulation(self):
        """This function presents the logical module flow for a DYNAMIC simulation."""
        pass
        self.simulation.update_runtime_progress(100)

    def run_benchmark_simulation(self):
        """This function presents the logical module flow for a BENCHMARK simulation."""
        pass
        self.simulation.update_runtime_progress(100)













