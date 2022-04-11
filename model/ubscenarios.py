r"""
@file   ubscenarios.py
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
__copyright__ = "Copyright 2018. Peter M. Bach"

# --- CODE STRUCTURE ---
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import threading
import gc
import xml.etree.ElementTree as ET  # XML parsing for loading scenario files
import ast  # Used for converting a string of a list into a list e.g. "[1, 2, 3, 4]" --> [1, 2, 3, 4]

# --- URBANBEATS LIBRARY IMPORTS ---
from .progref import ubglobals
from .ublibs import ubspatial


# --- SCENARIO CLASS DEFINITION ---
class UrbanBeatsScenario(threading.Thread):
    """The static parent class that contains the basic definition of the
    scenario for UrbanBEATS simulations. Other scenario classes inherit from
    this class and define the type of scenario (i.e. static, dynamic, benchmark)
    """
    def __init__(self, simulation, datalibrary, projectlog):
        threading.Thread.__init__(self)
        self.__observers = []
        self.__progressbars = []
        self.simulation = simulation        # The CORE (UrbanBEATSSim)
        self.datalibrary = datalibrary      # The active data library instance
        self.projectlog = projectlog        # The active log
        self.projectpath = simulation.get_project_path()
        self.runstate = False

        self.__scenariometadata = {"name": "My UrbanBEATS Scenario",
                                   "boundary": "(select simulation boundary)",
                                   "narrative": "(A description of my scenario)",
                                   "startyear": 2018,
                                   "filename": "(enter a naming convention for outputs)",
                                   "usescenarioname": 0}

        self.__spatial_data = [] # a list of map data to be used, holds the data references.
        self.__time_series_data = []   # a list of time series data to be used in the scenario or stored.
        self.__qual_data = []   # a list of qualitative data to be used in the scenario

        self.__assets = {}      # The collection of model assets that are stored for later retrieval
        self.__global_edge_list = []
        self.__global_point_list = []
        # can include: UBComponents(), Input Data, etc.

        self.__active_assets = None  # Will hold a reference to the active asset dictionary based on current dt

        # Calibration history - stores user data on model calibration.
        self.__calibration_history = {
            "tia": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None},
            "tif": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None},
            "allot": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None},
            "houses": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None},
            "roofarea": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None},
            "demand": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None},
            "ww": { "Block": None, "Region": None, "Suburb": None, "PlanZone": None, "Total": None}
            }   # Links to calibration files based on the type of parameter and the aggregation level

    def get_calibration_data_file(self, param, aggreg):
        return self.__calibration_history[param][aggreg]

    def set_active_calibration_data_file(self, param, aggreg, fname):
        try:
            self.__calibration_history[param][aggreg] = fname
        except KeyError:
            return True

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

    def get_assets_with_identifier(self, idstring, **kwargs):
        """Scans the complete Asset List and returns all assets with the idstring contained in their name
        e.g. BlockID contained in the name "BlockID1", "BlockID2", etc.)

        :param idstring: the part of the string to search the asset database for (e.g. "BlockID")
        :param **kwargs: 'assetcol' = {} custom dictionary of assets
        """
        assetcollection = []
        try:
            tempassetcol = kwargs["assetcol"]
        except KeyError:
            tempassetcol = self.__assets
        for i in tempassetcol:
            if idstring in i:
                assetcollection.append(tempassetcol[i])
        return assetcollection

    def retrieve_attribute_value_list(self, asset_identifier, attribute_name, asset_ids):
        """Returns a list [] of the attribute value specified by "attribute_name" for all asset of type "asset_identifier"
        with the IDs "asset_ids". Note that with asset identifiers, use only the legal identifiers, refer to ubglobals

        :param asset_identifier: str() of the asset identifier e.g. "BlockID" or "PatchID", etc.
        :param attribute_name: str() name of the attribute to get the data for
        :param asset_ids: list() of all ID numbers to search for
        :return: list() object containing all values in the ascending order of asset_ids
        """
        assetcol = self.get_assets_with_identifier(asset_identifier)
        if "ID" in asset_identifier:        # e.g. if someone wrote "BlockID" as the asset identifier...
            nameid = asset_identifier
        else:
            nameid = asset_identifier+"ID"

        attribute_values = [[], []]  # Asset ID, Asset Value
        for asset in assetcol:
            if asset.get_attribute(nameid) in asset_ids:
                attribute_values[0].append(asset.get_attribute(nameid))
                attribute_values[1].append(asset.get_attribute(attribute_name))
        return attribute_values     # returned in ascending order of the asset_ids

    def remove_asset_by_name(self, name):
        """Removes an asset from the collection based on the name specified

        :param name: the key of the asset in the self.__assets dictionary.
        """
        try:
            del self.__assets[name]
        except KeyError:
            return True

    def reset_assets(self):
        """Erases all assets, leaves an empty assets dictionary. Carried out when resetting the simulation."""
        self.__assets = {}
        gc.collect()

    def setup_scenario(self):
        """Initializes the scenario with the setup data provided by the user."""
        # [POSSIBLE TO DO] CREATE ASSETS SUPERSTRUCTURE

    def save_scenario(self):
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

        # f.write('\t<scenariomodules>\n')
        # for i in self.__modulesbools.keys():
        #     # Data for all the modules. This includes: active/in-active, number of instances, parameters
        #     f.write('\t\t<' + str(i) + '>\n')     # <MODULENAME>
        #     f.write('\t\t\t<active>'+str(self.__modulesbools[i])+'</active>\n')
        #     f.write('\t\t\t<count>'+str(len(self.__modules[i]))+'</count>\n')
        #     for j in range(len(self.__modules[i])):     # Loop across keys to get the module objects for parameters
        #         f.write('\t\t\t<parameters index="'+str(j)+'">\n')
        #         curmod = self.__modules[i][j]   # The current module object
        #         parlist = curmod.get_module_parameter_list()
        #         for par in parlist.keys():
        #             f.write('\t\t\t\t<'+str(par)+'>'+str(curmod.get_parameter(par))+'</'+str(par)+'>\n')
        #         f.write('\t\t\t</parameters>\n')
        #
        #     f.write('\t\t</' + str(i) + '>\n')
        # f.write('\t</scenariomodules>\n')

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
        for child in root.find("scenariometa"):
            self.__scenariometadata[child.tag] = type(self.__scenariometadata[child.tag])(child.text)

        # Collect data from data library, which should have been loaded by now
        for child in root.find("scenariodata"):
            if child.attrib["type"] == "spatial":
                self.__spatial_data.append(self.datalibrary.get_data_with_id(child.text))
            elif child.attrib["type"] == "temporal":
                self.__time_series_data.append(self.datalibrary.get_data_with_id(child.text))
            else:
                self.__qual_data.append(self.datalibrary.get_data_with_id(child.text))

        # # Create modules and fill out the modules with parameters [REVAMP]
        # mdata = root.find("scenariomodules")
        # for modname in self.__modulesbools.keys():
        #     mbool = int(mdata.find(modname).find("active").text)
        #     self.__modulesbools[modname] = mbool
        # self.setup_scenario()   # Instantiates all modules

        # # Loop through module information and set parameters
        # for modname in self.__modules.keys():
        #     for instance in mdata.find(modname).findall("parameters"):
        #         m = self.get_module_object(modname, int(instance.attrib["index"]))
        #         for child in instance:
        #             print(f"{child.tag}, {child.text}")  # DEBUG WITH THIS IN CASE PROGRAM CRASHES ON LOADING
        #             if m.get_parameter_type(child.tag) == 'LISTDOUBLE':     # IF IT's a LISTDOUBLE
        #                 m.set_parameter(child.tag, ast.literal_eval(child.text))    # Use literal eval
        #             else:
        #                 # Currently this does some explicit type casting based on the parameter types defined
        #                 m.set_parameter(child.tag, type(m.get_parameter(child.tag))(child.text))

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

    def attach_progressbars(self, progbars):
        """Assigns an array of progressbar observers to the Scenario's self.__progressbar variable."""
        self.__progressbars = progbars

    def update_observers(self, message):
        """Sends the message to all observers contained in the core's observer list."""
        for observer in self.__observers:
            observer.update_observer(str(message))

    def update_runtime_progress(self, value):
        """Sends the value to the progress bar(s)."""
        print("Updating Progress")
        for progbar in self.__progressbars:
            progbar.update_progress(int(value))

    def reinitialize(self):
        """Reinitializes the thread, resets the assets, edges and point lists and runs a garbage collection."""
        if self.ident is not None:
            threading.Thread.__init__(self)
        else:
            pass
        self.reset_assets()
        return False

    def run(self):
        """Overrides the thread.run() function, called when thread.start() is used. Determines, which kind of
        simulation to run."""
        pass
        # BEGIN THE SCENARIO'S SIMULATION
        # self.update_observers("Scenario Start!")
        # print("Starting Scenario !!")
        # self.runstate = True
        # if self.get_metadata("type") == "STATIC":
        #     self.run_static_simulation()
        # elif self.get_metadata("type") == "DYNAMIC":
        #     self.run_dynamic_simulation()
        # else:
        #     self.run_benchmark_simulation()
        # self.simulation.on_thread_finished()

    # def run_static_simulation(self):
    #     """This function presents the logical module flow for a STATIC simulation."""
    #     # --- STEP 0: Begin by setting up the basic global variables ---
    #     self.update_observers("Scenario Type: STATIC")
    #     temp_directory = self.simulation.get_global_options("tempdir")
    #     self.update_observers("Current temp directory: "+str(temp_directory))
    #     self.update_runtime_progress(5)
    #
    #     # --- STATIC STEP 1: Block delineation ---
    #     self.update_runtime_progress(10)
    #     delinblocks = self.get_module_object("SPATIAL", 0)
    #     delinblocks.attach(self.__observers)
    #     delinblocks.run_module()
    #
    #     # --- STATIC STEP 2: Climate Setup ---
    #     self.update_runtime_progress(20)
    #     # Skip this for now.
    #
    #     # --- STATIC STEP 3: Urban Planning ---
    #     self.update_runtime_progress(30)             # From this point forth, modules may be optional!
    #     urbplanbb = self.get_module_object("URBPLAN", 0)
    #     map_attr = self.get_asset_with_name("MapAttributes")
    #     if urbplanbb is None:
    #         map_attr.add_attribute("HasURBANFORM", 0)
    #     else:
    #         map_attr.add_attribute("HasURBANFORM", 1)
    #         urbplanbb.attach(self.__observers)
    #         urbplanbb.run_module()
    #
    #     # --- STATIC STEP 4: Spatial Analyst ---
    #     self.update_runtime_progress(40)
    #     spatialmap = self.get_module_object("MAP", 0)
    #     map_attr = self.get_asset_with_name("MapAttributes")
    #     if spatialmap is None:
    #         map_attr.add_attribute("HasSPATIALMAPPING", 0)
    #     else:
    #         map_attr.add_attribute("HasSPATIALMAPPING", 1)
    #         spatialmap.attach(self.__observers)
    #         spatialmap.run_module()
    #
    #     # --- STATIC STEP 6: Infrastructure ---
    #     self.update_runtime_progress(50)
    #     infrastructure = self.get_module_object("INFRA", 0)
    #     if infrastructure is None:
    #         map_attr.add_attribute("HasINFRA", 0)
    #     else:
    #         map_attr.add_attribute("HasINFRA", 1)
    #         infrastructure.attach(self.__observers)
    #         infrastructure.run_module()
    #
    #
    #     # --- STATIC STEP 7: Blue-Green Systems ---
    #     self.update_runtime_progress(60)
    #     # Skip this for now...
    #
    #     # --- STATIC STEP 8: Water Cycle ---
    #     self.update_runtime_progress(70)
    #     # Skip this for now...
    #
    #     # --- STATIC STEP 9: Microclimate ---
    #     self.update_runtime_progress(75)
    #     # Skip this for now...
    #
    #     # --- STATIC STEP 10: Flood ---
    #     self.update_runtime_progress(80)
    #     # Skip this for now...
    #
    #     # --- STATIC STEP 11: Economics ---
    #     self.update_runtime_progress(85)
    #     # Skip this for now...
    #
    #     # --- DATA EXPORT AND CLEANUP STEPS ---
    #     self.update_runtime_progress(90)
    #
    #     # Export the data maps available - first check scenario name
    #     if int(self.get_metadata("usescenarioname")):
    #         file_basename = self.get_metadata("name").replace(" ", "_")
    #     else:
    #         file_basename = self.get_metadata("filename")
    #
    #     print(self.projectpath)
    #     map_attributes = self.get_asset_with_name("MapAttributes")
    #     epsg = self.simulation.get_project_parameter("project_epsg")
    #
    #     # SHAPEFILE EXPORT FUNCTIONS
    #     # -- SECTION 1 - BASE GEOMETRY
    #     if map_attributes.get_attribute("GeometryType") in ["SQUARES", "HEXAGONS"]:
    #         xblocks.export_block_assets_to_gis_shapefile(self.get_assets_with_identifier("BlockID"), map_attributes,
    #                                                        self.projectpath+"/output", file_basename + "_Blocks",
    #                                                        int(epsg))
    #
    #         xpatches.export_patches_to_gis_shapefile(self.get_assets_with_identifier("PatchID"), map_attributes,
    #                                                  self.projectpath + "/output", file_basename + "_Patches",
    #                                                  int(epsg))
    #
    #     if map_attributes.get_attribute("GeometryType") in ["VECTORPATCH"]:
    #         xpatches.export_vectorpatches_to_gis_shapefile(self.get_assets_with_identifier("PatchID"), map_attributes,
    #                                                        self.projectpath+"/output", file_basename + "_Patches",
    #                                                        int(epsg))
    #
    #     self.update_runtime_progress(93)
    #
    #     # -- SECTION 2 - FLOW PATHS
    #     xflowpaths.export_flowpaths_to_gis_shapefile(self.get_assets_with_identifier("FlowID"), map_attributes,
    #                                                  self.projectpath + "/output", file_basename + "_Flowpaths",
    #                                                  int(epsg))  # Export FlowPaths
    #
    #     if map_attributes.get_attribute("GeometryType") in ["SQUARES", "HEXAGONS"]:
    #         # Patch Flowpaths
    #         xpatches.export_patch_flowpaths_to_gis_shapefile(self.get_assets_with_identifier("PatchFloID"),
    #                                                          map_attributes, self.projectpath + "/output",
    #                                                          file_basename + "_PatchFlowpaths", int(epsg))
    #     if map_attributes.get_attribute("GeometryType") in ["VECTORPATCH"]:
    #         # Dirichlet Network
    #         xpatches.export_dirichletnetwork_to_gis_shapefile(self.get_assets_with_identifier("LinkID"),
    #                                                           map_attributes, self.projectpath + "/output",
    #                                                           file_basename + "_Dirichletnet", int(epsg))
    #
    #     self.update_runtime_progress(96)
    #     # -- SECTION 3 - Other Maps
    #     print("Exporting Open Space Stuff")
    #     xopenspace.export_oslink_to_gis_shapefile(self.get_assets_with_identifier("OSLinkID"), map_attributes,
    #                                                 self.projectpath + "/output", file_basename + "_OSLink",
    #                                                 int(epsg))
    #     xopenspace.export_osnet_to_gis_shapefile(self.get_assets_with_identifier("OSNetID"), map_attributes,
    #                                                 self.projectpath + "/output", file_basename + "_OSNet",
    #                                                 int(epsg))
    #     xopenspace.export_patch_buffers_to_gis_shapefile(self.get_assets_with_identifier("PatchID"), map_attributes,
    #                                                 self.projectpath + "/output", file_basename + "_OSBuffer",
    #                                                 int(epsg))
    #
    #     # xinfra.export_sww_network_to_gis_shapefile(self.get_assets_with_identifier("SwwID"), map_attributes,
    #     #                                             self.projectpath + "/output", file_basename + "_SwwNet",
    #     #                                             int(epsg), "Blocks")
    #     # xinfra.export_sww_links_to_gis_shapefile(self.get_assets_with_identifier("LinkID"), map_attributes,
    #     #                                             self.projectpath + "/output", file_basename + "_Links",
    #     #                                             int(epsg), "Blocks")
    #     # xinfra.export_sww_mst_to_gis_shapefile(self.get_assets_with_identifier("MST"), map_attributes,
    #     #                                          self.projectpath + "/output", file_basename + "_MST",
    #     #                                          int(epsg), "Blocks")
    #     # [TO DO] Export options - WSUD Systems
    #     # [TO DO] Export options - centrepoints
    #
    #     self.update_runtime_progress(100)
    #     return True

    # def run_dynamic_simulation(self):
    #     """This function presents the logical module flow for a DYNAMIC simulation."""
    #     self.update_observers("Scenario Type: DYNAMIC")
    #     temp_directory = self.simulation.get_global_options("tempdir")
    #     self.update_observers("Current temp directory: " + str(temp_directory))
    #     self.update_runtime_progress(5)
    #
    #     # --- DYNAMIC STEP 1: Development Mapping Module ---
    #     self.update_runtime_progress(10)
    #     urbdev = self.get_module_object("URBDEV", 0)
    #     if urbdev is None:
    #         pass
    #     else:
    #         urbdev.attach(self.__observers)
    #         urbdev.run_module()
    #
    #     # --- DYNAMIC STEP 2: Urban Dynamics Module ---
    #     self.update_runtime_progress(20)
    #     # Skip for now
    #
    #     # --- DYNAMIC STEP 3: Block delineation ---
    #
    #     # --- DYNAMIC STEP 4: Climate setup ---
    #     # --- DYNAMIC STEP 5: Urban Planning ---
    #     # --- DYNAMIC STEP 6: Spatial Analyst ---
    #     # --- DYNAMIC STEP 7: Infrastructure ---
    #     # --- DYNAMIC STEP 8: Blue-Green Systems ---
    #     # --- DYNAMIC STEP 9: Water Cycle ---
    #     # --- DYNAMIC STEP 10: Microclimate ---
    #     # --- DYNAMIC STEP 11: Flood ---
    #     # --- DYNAMIC STEP 12: Economics ---
    #
    #     # --- DATA EXPORT AND CLEANUP STEPS ---
    #     self.update_runtime_progress(90)
    #
    #     # Export the data maps available - first check scenario name
    #     if int(self.get_metadata("usescenarioname")):
    #         file_basename = self.get_metadata("name").replace(" ", "_")
    #     else:
    #         file_basename = self.get_metadata("filename")
    #
    #     print(self.projectpath)
    #     map_attributes = self.get_asset_with_name("MapAttributes")
    #     epsg = self.simulation.get_project_parameter("project_epsg")
    #
    #     xurbanmodel.export_urbandev_cells_to_gis_shapefile(self.get_assets_with_identifier("CellID"), map_attributes,
    #                                                        self.projectpath+"/output", file_basename + "_Cells",
    #                                                        int(epsg))
    #     self.update_runtime_progress(95)
    #     # xregions.export_municipalities_to_gis_shapefile()
    #
    #     self.update_runtime_progress(100)
    #
    # def run_benchmark_simulation(self):
    #     """This function presents the logical module flow for a BENCHMARK simulation."""
    #     pass
    #     self.update_runtime_progress(100)













