r"""
@file   urbanbeatscore.py
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
import random
import os
import xml.etree.ElementTree as ET
import datetime
import ast
import pickle

# --- URBANBEATS LIBRARY IMPORTS ---
from . import ubdatalibrary
from . import ubscenarios
from . import ubruntime
from . import ubassetexport
from .ublibs import ubspatial as ubspatial
from .ublibs import ubdatatypes as ubdata

# --- URBANBEATS MODULES ---
import inspect
import model.mods_master as ubtoolkit
# import .model.mods_userdef as usertoolkit


# --- URBANBEATS SIMULATION CLASS DEFINITION ---
class UrbanBeatsSim(object):
    """The simulation class for UrbanBEATS, which contains all the information
    about scenarios, models, and other items. Contains the project info, reference
    to all modules, simulation settings and status of the current workflow.
    """
    def __init__(self, rootpath, options, parent=None):
        """Initialization for the class allowing the model to set up the simulation
        and required modules.

        :param rootpath: the root path of the UrbanBEATS Model containing the ancillary folder
        :param options: a dictionary of global options. The core of the model uses only several of these options including
                        ["maxiterations"] ...
        """
        random.seed()  # Seed the random numbers

        # Initialize variables
        self.__rootpath = rootpath          # the root path for UrbanBEATS' runtime
        self.__global_options = options     # global model options
        self.__runtime_progress = 0         # virtual progress bar
        self.__parent = parent
        self.__global_collections = {}      # Stores UBCollection Objects

        #Initialize paths
        self.emptyBlockPath = self.__rootpath+"/ancillary/emptyblockmap.shp"
        self.emptySysPath = self.__rootpath+"/ancillary/emptysystemmap.shp"

        #Observer, Status and Filename
        self.__observers = []   # Observers of the current simulation
        self.__progressbars = []     # Progressbar of the current simulation

        self.__project_saved = 0            # BOOL - has the project been saved?
        self.__simulation_completed = 0     # BOOL - has the simulation completed run?
        self.__projectpath = ""             # Project Path. Starts blank, is then replaced.

        # Project Parameters - base initialization
        self.__project_info = {
            "name": "New UrbanBEATS Project",
            "date": datetime.datetime.today().date(),
            "region": "",
            "country": self.__global_options["country"],
            "city": self.__global_options["city"],
            "modeller": self.__global_options["defaultmodeller"],
            "affiliation": self.__global_options["defaultaffil"],
            "otherpersons": "none",
            "synopsis": "no synopsis",
            "logstyle": self.__global_options["projectlogstyle"],
            "projectpath": self.__global_options["defaultpath"],
            "keepcopy": 0,
            "project_coord_sys": self.__global_options["defaultcoordsys"],
            "project_epsg": self.__global_options["customepsg"]
        }

        # Geography Variables - TRACKING VARIABLES
        self.__activeboundary = None    # Tracking variables
        self.__current_boundary_to_load = []  # Current Boundary Shapefile to load [filename,
        self.__project_extents = [[], [], [], []]  # Tracks ALL extents loaded to determine 'global_extents'
        self.__project_centroids = [[], []]  # Tracks ALL centroids loaded to determine 'global_centroid'
        self.__global_centroid = [0, 0]
        self.__global_extents = None  # xmin, xmax, ymin, ymax

        # Geography Variables - PERSISTENT INFORMATION
        self.__project_boundaries = {}      # Collects different boundaries
        self.__project_locations = {}

        # Major classes that form part of the project
        self.__datalibrary = None       # initialize the data library
        self.__projectlog = None        # initialize the project log
        self.__scenarios = {}           # initialize the scenarios
        self.__functions = []           # initialize the list of functions

        self.__activescenario = None

        # Global Modules Collection
        self.__modules_collection = {}  # A global instance of all modules
        for name, obj in inspect.getmembers(ubtoolkit):  # Get all classes and set up the self.__modules_master
            if inspect.isclass(obj):
                self.__modules_collection[obj.longname] = obj(self, self.__datalibrary, self.__projectlog)

        self.__ubruntime = ubruntime.UrbanBeatsRuntime(self, self.__datalibrary, self.__projectlog)

    # ASSET COLLECTIONS RELATING TO THE GLOBAL PROJECT COLLECTIONS
    def create_new_asset_collection(self, name, collection_type):
        self.__global_collections[name] = ubdata.UBCollection(name, collection_type)

    def add_asset_collection_to_project(self, ubcollection_obj):
        self.__global_collections[ubcollection_obj.get_container_name()] = ubcollection_obj

    def remove_asset_collection_from_project(self, name):
        try:
            if os.path.exists(self.__projectpath+"/collections/"+name+".ubcol"):
                os.remove(self.__projectpath+"/collections/"+name+".ubcol")
            del self.__global_collections[name]
        except KeyError:
            return True

    def get_global_asset_collection(self):
        return self.__global_collections

    def get_asset_collection_by_name(self, name):
        try:
            return self.__global_collections[name]
        except KeyError:
            return None

    # MODULE MANAGEMENT
    def get_module_instance(self, longname):
        return self.__modules_collection[longname]

    # PROJECT LOCATIONS & BOUNDARIES MANAGEMENT
    def add_project_location(self, loc_name, latlng, loc_description, loc_type):
        self.__project_locations[loc_name] = {"loc_name": loc_name, "latitude": latlng[0], "longitude": latlng[1],
                                              "description": loc_description, "loc_type": loc_type}

    def get_project_locations(self):
        return self.__project_locations

    def get_project_location_names(self):
        return self.__project_locations.keys()

    def get_project_location_info(self, locname):
        try:
            return self.__project_locations[locname]
        except KeyError:
            return None

    def remove_project_location(self, locname):
        try:
            del self.__project_locations[locname]
        except KeyError:
            return True

    def get_project_epsg(self):
        return self.__project_info["project_epsg"]

    def set_active_boundary(self, boundaryname):
        try:
            self.__activeboundary = self.__project_boundaries[boundaryname]
        except KeyError:
            self.__activeboundary = None

    def get_active_boundary(self):
        return self.__activeboundary

    def set_current_boundary_file_to_load(self, filename, multifeatoptions, namingoptions, epsg, inputprojcs):
        """Defines the parameters of a boundary shapefile for the core to load. This shapefile is run through

        :param filename: full path to the shapefile
        :param multifeatoptions: ["ALL"/"LRG"/"THR" , THRESHOLD_VALUE [km2]]
        :param namingoptions: ["USER"/"ATTR", "USER-DEFINED-NAME"]
        :param epsg: the EPSG integer code
        :return: updates the self.__current_boundar_to_load variable.
        """
        self.__current_boundary_to_load = [filename, multifeatoptions, namingoptions, epsg, inputprojcs]
        return True

    def get_project_boundaries(self):
        return self.__project_boundaries

    def get_project_boundary_names(self):
        """Returns all names of current boundaries loaded into the project as a list of strings."""
        return self.__project_boundaries.keys()

    def get_project_boundary_by_name(self, boundaryname):
        try:
            return self.__project_boundaries[boundaryname]
        except KeyError:
            return None

    def delete_simulation_boundary(self, boundaryname):
        """Removes the boundary with the name 'boundaryname' from the project."""
        if boundaryname not in self.__project_boundaries.keys():
            print("Error, boundary not found, please check name")
            return True

        # Step 1 - if it's the active boundary, set to None
        if self.__activeboundary is None or self.__activeboundary["boundaryname"] == boundaryname:
            self.__activeboundary = None

        # Step 2 - loop through all scenarios - remove the boundary if it is the selected boundary
        for s in self.__scenarios.keys():
            if self.__scenarios[s].get_metadata("boundary") == boundaryname:
                self.__scenarios[s].set_metadata("boundary", "(select simulation boundary)")

        # Step 3 - delete the Shapefile and all related files
        filepath = self.get_project_parameter("projectpath") + "/" + self.get_project_parameter("name") \
                       + "/boundaries/"
        filename = self.__project_boundaries[boundaryname]["filename"]
        available_files = os.listdir(filepath)
        for file in available_files:
            if filename in file:
                os.remove(filepath+file)

        # Step 4 - Remove the boundary from the boundaries dictionary
        # Remove the extents and centroids from self.__project_extents and self.__project_centroids
        self.__project_extents[0].remove(self.__project_boundaries[boundaryname]["xmin"])
        self.__project_extents[1].remove(self.__project_boundaries[boundaryname]["xmax"])
        self.__project_extents[2].remove(self.__project_boundaries[boundaryname]["ymin"])
        self.__project_extents[3].remove(self.__project_boundaries[boundaryname]["ymax"])
        self.__project_centroids[0].remove(self.__project_boundaries[boundaryname]["centroid"][0])
        self.__project_centroids[1].remove(self.__project_boundaries[boundaryname]["centroid"][1])
        self.update_global_centroid_and_extents()

        # Remove the boundary from the self.__project_boundaries
        try:
            del self.__project_boundaries[boundaryname]
            self.save_project_boundaries()  # Update the save file
        except KeyError:
            return True

    def add_basic_shape_as_simulation_boundary(self, parameters):
        """Adds a basic shape (rectangle, circle, hexagon) as a simulation boundary to the project.

        :param parameters: a dictionary with key parameter keys including 'name', 'epsg', 'inputprojcs', 'centroid',
                'shape', 'shapeparameters'
        """
        if parameters["shape"] == "rect":
            w = parameters["shapeparameters"][0]
            h = parameters["shapeparameters"][1]
            boundarydata = ubspatial.create_rectangle_from_centroid(parameters["name"], parameters["epsg"],
                                                                    parameters["centroid"], w*1000.0, h*1000.0)
        elif parameters["shape"] == "circ":
            boundarydata = ubspatial.create_circle_from_centroid(parameters["name"], parameters["epsg"],
                                                                 parameters["centroid"],
                                                                 parameters["shapeparameters"]*1000.0)
        else:
            w = parameters["shapeparameters"][0]
            orient = parameters["shapeparameters"][1]
            boundarydata = ubspatial.create_hexagon_from_centroid(parameters["name"], parameters["epsg"],
                                                                  parameters["centroid"], w*1000.0, orient)

        self.__project_extents[0].append(boundarydata["xmin"])
        self.__project_extents[1].append(boundarydata["xmax"])
        self.__project_extents[2].append(boundarydata["ymin"])
        self.__project_extents[3].append(boundarydata["ymax"])
        self.__project_centroids[0].append(boundarydata["centroid"][0])
        self.__project_centroids[1].append(boundarydata["centroid"][1])

        namecounter = 0
        boundarynewname = boundarydata["boundaryname"]
        while boundarynewname in self.__project_boundaries.keys():
            namecounter += 1
            boundarynewname = boundarydata["boundaryname"] + "_" + str(namecounter)
        boundarydata["boundaryname"] = boundarynewname
        boundarydata["filename"] = boundarynewname + "_Boundary_"+str(boundarydata["shape"])+"_"\
                                   + str(boundarydata["inputEPSG"])
        boundarydata["coordsysname"] = parameters["inputprojcs"]

        # Save as Shapefile
        boundarypath = self.get_project_parameter("projectpath") + "/" + self.get_project_parameter("name") \
                       + "/boundaries/"
        ubspatial.save_boundary_as_shapefile(boundarydata, boundarypath + boundarydata["filename"])

        # Update central core project boundary information
        self.__project_boundaries[boundarynewname] = boundarydata  # Add new project boundary
        self.update_global_centroid_and_extents()
        # print("Current number of boundaries in the simulation: ", str(len(self.__project_boundaries)))
        return True

    def update_global_centroid_and_extents(self):
        """Updates the global centroid and extents variables."""
        if len(self.__project_centroids[0]) != 0 or len(self.__project_centroids[1]) != 0:
            self.__global_centroid = [sum(self.__project_centroids[0]) / len(self.__project_centroids[0]),
                                      sum(self.__project_centroids[1]) / len(self.__project_centroids[1])]
        if len(self.__project_extents[0]) != 0 or len(self.__project_extents[2]) != 0:
            self.__global_extents = [min(self.__project_extents[0]), max(self.__project_extents[1]),
                                     min(self.__project_extents[2]), max(self.__project_extents[3])]

    def import_simulation_boundaries(self):
        """Imports new boundaries into the simulation based on the self.__current_boundary_to_load variable. After
        loading, it resets the boundary variable to []. Loaded boundaries are updated in the
        self.__project_boundaries variable."""
        if len(self.__current_boundary_to_load) == 0:
            return True

        # Naming Convention
        naming_rule = str(self.__current_boundary_to_load[2][0])
        naming_key = str(self.__current_boundary_to_load[2][1])
        naming = str(naming_rule+"_"+naming_key)

        # GET THE POLYGONS
        boundaries = ubspatial.import_polygonal_map(self.__current_boundary_to_load[0], "native", naming, [0, 0],
                                                    useEPSG=self.__current_boundary_to_load[3])

        # FILTER OUT AND CREATE BOUNDARY ITEMS
        polyareas = [boundaries[i].get_attribute("Area_sqkm") for i in range(len(boundaries))]

        if self.__current_boundary_to_load[1][0] == "LRG":
            boundary_polys = [boundaries[polyareas.index(max(polyareas))]]
        elif self.__current_boundary_to_load[1][0] == "THR":
            boundary_polys = [boundaries[i] for i in range(len(boundaries))
                              if polyareas[i] > self.__current_boundary_to_load[1][1]]
        else:
            boundary_polys = boundaries

        # ADD BOUNDARIES TO SIMULATION AND ORGANISE NAMING-CONVENTION
        for i in range(len(boundary_polys)):
            mapstats = {}
            mapstats["inputEPSG"] = self.__current_boundary_to_load[3]
            mapstats["coordsysname"] = self.__current_boundary_to_load[4]
            mapstats["area"] = boundary_polys[i].get_attribute("Area_sqkm")

            extents = boundary_polys[i].get_extents()
            mapstats["xmin"] = extents[0]
            self.__project_extents[0].append(extents[0])
            mapstats["xmax"] = extents[1]
            self.__project_extents[1].append(extents[1])
            mapstats["ymin"] = extents[2]
            self.__project_extents[2].append(extents[2])
            mapstats["ymax"] = extents[3]
            self.__project_extents[3].append(extents[3])
            mapstats["centroid"] = boundary_polys[i].get_centroid()
            self.__project_centroids[0].append(mapstats["centroid"][0])
            self.__project_centroids[1].append(mapstats["centroid"][1])

            coordinates = boundary_polys[i].get_points()
            mapstats["coordinates"] = coordinates
            mapstats["shape"] = "Polygon"

            if naming_rule == "user":
                boundary_base_name = naming_key
            else:   # naming_rule == "attr"
                boundary_base_name = boundary_polys[i].get_attribute(naming_key)
                if boundary_base_name is None:
                    boundary_base_name = naming_key

            namecounter = 0
            boundarynewname = boundary_base_name
            while boundarynewname in self.__project_boundaries.keys():
                namecounter += 1
                boundarynewname = boundary_base_name + "_" + str(namecounter)
            mapstats["boundaryname"] = boundarynewname

            # Save shapefiles into the 'boundaries' folder
            mapstats["filename"] = boundarynewname+"_Boundary_"+str(mapstats["shape"])+"_"+str(mapstats["inputEPSG"])
            boundarypath = self.get_project_parameter("projectpath") + "/" + self.get_project_parameter("name") \
                           + "/boundaries/"
            ubspatial.save_boundary_as_shapefile(mapstats, boundarypath+mapstats["filename"])

            # Add the boundary data to the project
            self.__project_boundaries[boundarynewname] = mapstats  # Add new project boundary

        self.__current_boundary_to_load = []    # Reset the current boundary to load
        self.update_global_centroid_and_extents()
        print("Current number of boundaries in the simulation: ", str(len(self.__project_boundaries)))
        return True

    def save_project(self):
        """Calls all relevant functions to save the simulation project to the project folder."""
        # (1) SAVE THE DATA LIBRARY
        self.save_data_library()

        # (2) SAVE ALL PROJECT BOUNDARIES AND LOCATIONS
        self.save_project_boundaries()

        # (3) SAVE ANY FUNCTIONS WITHIN THE PROJECT
        self.save_functions_list()

        # (4)

        # (3) SAVE ALL SCENARIOS AS OBJECTS
        for scen_name in self.get_scenario_names():
            self.get_scenario_by_name(scen_name).save_scenario()

        # (5) SAVE THE GLOBAL ASSETS COLLECTION FOR LOADING LATER ON
        for item in self.__global_collections.keys():
            obj = self.__global_collections[item]
            ubdata.save_asset_collection(self.__projectpath, obj)
        return True

    def save_project_boundaries(self):
        """Saves the simulation boundaries data file to list."""
        projectpath = self.get_project_parameter("projectpath")
        projectname = self.get_project_parameter("name")
        f = open(projectpath + "/" + projectname + "/boundloc.ubdata", 'wb')
        pickle.dump([self.__project_boundaries,
                     self.__project_locations,
                     self.__project_extents,
                     self.__project_centroids], f)
        f.close()
        return True

    def restore_project_boundaries_and_locations(self, projectpath):
        """Loads the boundloc.ubdata file from the boundaries folder and restores the dictionaries for
        self.__project_boundaries and self.__project_locations as well as self.__project_extents and
        self.__project_centroids variables."""
        try:
            f = open(projectpath+"/boundloc.ubdata", 'rb')
            bdata = pickle.load(f)
            self.__project_boundaries = bdata[0]
            self.__project_locations = bdata[1]
            self.__project_extents = bdata[2]
            self.__project_centroids = bdata[3]
            self.update_global_centroid_and_extents()  # Once all boundaries have been loaded, update the global values
            f.close()
            return True
        except IOError:
            return False

    def get_global_centroid(self):
        return self.__global_centroid

    def get_global_extents(self):
        return self.__global_extents

    # INITIALIZATION METHODS
    def save_data_library(self):
        if self.__datalibrary is not None:
            ubdatalibrary.save_data_library(self.__datalibrary)

    def initialize_simulation(self, condition):
        """Performs a full initialization of the project simulation, creates
        a folder for holding relevant data and results.

        :return: None
        """
        if condition == "new":  # for starting a new project
            self.setup_project_folder_structure()   # Creates all the folders

            # Create a new data library
            datalib = ubdatalibrary.UrbanBeatsDataLibrary(self.__projectpath,
                                                          self.get_project_parameter("keepcopy"))
            self.set_data_library(datalib)

            # Create a new project log
            projectlog = UrbanBeatsLog(self.__projectpath)
            self.set_project_log(projectlog)
        elif condition == "open":   # for opening a project
            # Folder structure is already present
            self.__projectpath = self.get_project_parameter("projectpath")+"/"+self.get_project_parameter("name")

            # (1) OPEN THE PROJECT'S DATA LIBRARY (datalib.ubdata)
            self.set_data_library(ubdatalibrary.load_data_library(self.__projectpath))

            # (2) ADD SIMULATION BOUNDARIES AND LOCATIONS TO PROJECT
            self.restore_project_boundaries_and_locations(self.__projectpath)

            # (3) RESTORE PRE-DEFINED FUNCTIONS IN THE PROJECT
            self.restore_functions_from_xml(self.__projectpath)

            # (4) RESTORE THE PROJECT LOG
            projectlog = UrbanBeatsLog(self.__projectpath)
            self.set_project_log(projectlog)    # Go through existing project logs and update or add log info [TO DO]
            # - LOAD THE EXISTING LOGS - # FUTURE TO DO

            # (5) RESTORE SCENARIOS
            # Go through scenarios and add the scenarios to the scenario manager
            scenariofiles = os.listdir(self.__projectpath+ "/scenarios/")
            for sf in scenariofiles:
                if ".xml" not in sf:
                    continue
                else:
                    self.create_new_scenario()
                    self.__activescenario.setup_scenario_from_xml(sf)
                    self.add_new_scenario(self.__activescenario)

            # (6) RESTORE ASSET COLLECTIONS
            assetcols = os.listdir(self.__projectpath+"/collections/")
            print(assetcols)
            for ac in assetcols:
                if ".ubcol" not in ac:
                    continue
                else:
                    obj = ubdata.load_asset_collection(self.__projectpath+"/collections/"+ac)
                    self.__global_collections[obj.get_container_name()] = obj

        elif condition == "import": # for importing a project
            pass    # [TO DO]

    # OBSERVER PATTERNS AND PROGRAM MANAGEMENT
    def register_observer(self, observerobj):
        """Adds an observer references by observerobj to the self.__observers array. This uses the Observer design
        pattern."""
        self.__observers.append(observerobj)

    def register_progressbar(self, progressbarobj):
        """Adds a progressbar observer."""
        self.__progressbars.append(progressbarobj)

    def update_observers(self, message):
        """Sends the message to all observers contained in the core's observer list."""
        for observer in self.__observers:
            observer.update_observer(str(message))

    def update_runtime_progress(self, value):
        """Sends the message to all progress trackers in the progressbar observer list."""
        for progbar in self.__progressbars:
            progbar.update_progress(int(value))

    def get_program_rootpath(self):
        """Returns the root path of the program."""
        return self.__rootpath

    # LOADING PROJECTS
    def load_project_info_datafile(self, projectpath):
        """Loads the project's info.ubdata file and writes the information into the simulation core."""
        try:
            f = open(projectpath+"/info.ubdata", 'rb')
            self.__project_info = pickle.load(f)
            f.close()
            return True
        except IOError:
            return False

    def get_scenario_boundary_info(self, param):
        """Retrieves spatial boundary information for the current project from the self.__boundarinfo variable.

        :param param: the name of the key of self.__boundaryinfo.
        :return: value if key is existent, None if not.
        """
        if param == "all":
            return self.__activeboundary
        if param == "mapextents":
            return self.__activeboundary["xmin"], self.__activeboundary["xmax"], \
                   self.__activeboundary["ymin"], self.__activeboundary["ymax"]
        try:
            return self.__activeboundary[param]
        except KeyError:
            return None

    def setup_project_folder_structure(self):
        """Sets up the base folder structure of the project based on the specified path. The folder
        structure contains several fundamental fodlers including 'datalib' and 'output' and one
        folder for each scenario in the simulation."""
        projectpath = self.get_project_parameter("projectpath")
        projectname = self.get_project_parameter("name")
        namecounter = 0
        projectnewname = projectname.rstrip(" ")    # Cull whitespaces at the end of the name
        while os.path.isdir(projectpath+"/"+projectnewname):
            namecounter += 1
            projectnewname = projectname+"_"+str(namecounter)
        self.set_project_parameter("name", projectnewname)
        os.makedirs(projectpath+"/"+projectnewname)
        os.makedirs(projectpath + "/" + projectnewname + "/boundaries")
        os.makedirs(projectpath+"/"+projectnewname+"/datalib")
        os.makedirs(projectpath + "/" + projectnewname + "/collections")
        os.makedirs(projectpath + "/" + projectnewname + "/output")
        os.makedirs(projectpath+"/"+projectnewname+"/scenarios")
        self.write_project_info_file()
        self.__projectpath = projectpath+"/"+projectnewname

    # FUNCTIONS IN THE DATA LIBRARY
    def get_all_function_objects_of_type(self, typename):
        """Returns all instances in the self.function list of the given typename."""
        subset = []
        for f in self.__functions:
            if f.get_function_type() == typename:
                subset.append(f)
        return subset

    def get_function_with_id(self, fid):
        """Returns a function object with a specific ID indicated by fid."""
        for i in range(len(self.__functions)):
            if self.__functions[i].get_id() == fid:
                return self.__functions[i]
        return None

    def remove_function_object_with_id(self, fid):
        """Removes a function object from the library with the ID fid."""
        for i in range(len(self.__functions)):
            if self.__functions[i].get_id() == fid:
                self.__functions.pop(i)
        return True

    def add_new_function_to_library(self, function_obj):
        """Adds a new function to the library of functions."""
        self.__functions.append(function_obj)
        return True

    def save_functions_list(self):
        """Saves functions in the active list to an xml file."""
        projectpath = self.get_project_parameter("projectpath")
        projectname = self.get_project_parameter("name")
        f = open(projectpath+"/"+projectname+"/functions.xml", 'w')
        f.write('<URBANBEATSPROJECTFUNCTIONS creator="Peter M. Bach" version="1.0">\n')
        f.write('\t<functionlist>\n')
        for i in range(len(self.__functions)):
            # Get the text for each function, write the text to the file.
            for line in self.__functions[i].get_function_data_as_xml():
                f.write(line)
        f.write('\t</functionlist>\n')
        f.write('</URBANBEATSPROJECTFUNCTIONS>\n')
        f.close()

    def restore_functions_from_xml(self, projectpath):
        """Restores functions from the project xml file."""
        try:
            projinfo = ET.parse(projectpath+"/functions.xml")
        except IOError:
            return False

        root = projinfo.getroot()
        flist = root.find('functionlist')
        for child in flist:     # Loop across functions
            fdict = {}
            for atts in child:  # Get all the attributes of the current function
                fdict[atts.tag] = atts.text
            # Now figure out how to set the function
            if fdict["functiontype"] == "IF":       # INFLUENCE FUNCTION
                # print(fdict)
                self.__functions.append(ubdata.NeighbourhoodInfluenceFunction(functiondict=fdict))
        return True

    # WRITING PROJECT INFO
    def write_project_info_file(self):
        """Writes the .ubdata file of self.__project_info, which contains the project's metadata to the project folder
        for faster loading and setting up of the interface on the next simulation."""
        projectpath = self.get_project_parameter("projectpath")
        projectname = self.get_project_parameter("name")
        f = open(projectpath+"/"+projectname+"/info.ubdata", 'wb')
        pickle.dump(self.get_all_project_info(), f)
        f.close()

    # SCENARIO MANAGEMENT
    def create_new_scenario(self):
        """Creates a new scenario object and sets it as the active scenario."""
        newscenario = ubscenarios.UrbanBeatsScenario(self, self.__datalibrary, self.__projectlog)
        self.__activescenario = newscenario     # Set the active scenario's name

    def add_new_scenario(self, scenario_object):
        """Adds a new scenario to the simulation by creating a UrbanBeatsScenario() instance and initializing
        it."""
        if scenario_object.get_metadata("name") not in self.__scenarios.keys():
            self.__scenarios[scenario_object.get_metadata("name")] = scenario_object
            if scenario_object.get_metadata("name") not in self.__global_collections:
                assetcol = ubdata.UBCollection(scenario_object.get_metadata("name"), "Scenario")
                self.add_asset_collection_to_project(assetcol)
            scenario_object.define_asset_collection_container(assetcol)
            return True
        else:
            return False    # Cannot have two scenarios of the same name!

    def set_active_scenario(self, scenario_name):
        """Sets the current active scenario to the scenario with the name "name"."""
        try:
            self.__activescenario = self.__scenarios[scenario_name]
            self.__activeboundary = self.__activescenario.get_metadata("boundary")
        except KeyError:
            self.__activescenario = None
            self.__activeboundary = None

    def get_active_scenario(self):
        """Returns the active scenario in the core simulation."""
        return self.__activescenario

    def get_scenario_names(self):
        """Returns all scenario names"""
        try:
            return self.__scenarios.keys()
        except AttributeError:
            return []

    def get_scenario_by_name(self, scenario_name):
        """Returns the scenario with the specified name."""
        try:
            return self.__scenarios[scenario_name]
        except KeyError:
            return None

    def check_for_existing_scenario_by_name(self, scenario_name):
        """Returns True if the scenario exists, false if the scenario doesn't already exist by name

        :return True: scenario exists in simulation, False: scenario does not exist."""
        if scenario_name in self.__scenarios.keys():
            return True
        else:
            return False

    def delete_scenario(self, scenario_name):
        """Removes the scenario with the given scenario name from the simulation core."""
        if self.__activescenario.get_metadata("name") == scenario_name:
            self.__activescenario = None            # Set the active scenario to None
        try:
            del self.__scenarios[scenario_name]  # Delete scenario with the key "scenario_name"
            if os.path.exists(self.__projectpath+"/scenarios/"+scenario_name+".xml"):   # Delete xml file
                os.remove(self.__projectpath+"/scenarios/"+scenario_name+".xml")
            self.remove_asset_collection_from_project(scenario_name)        # Remove asset collection
        except KeyError:
            pass
        self.__datalibrary.remove_all_reference_to_scenario("name")  # Remove all references to scenario

    # GETTERS AND SETTERS
    def get_all_project_info(self):
        """Returns the full project information"""
        return self.__project_info

    def get_num_scenarios(self):
        """Returns the total number of scenarios currently in the project."""
        return len(self.__scenarios)

    def get_num_datasets(self):
        """Returns a single integer indicating the number of data files in the library."""
        return self.__datalibrary.get_num_datafiles()

    def get_project_parameter(self, parname):
        """Get project info either as a whole dictionary or based on individual
        attributes.

        :parname attribute: specific attribute of the project info dictionary, if
                "ALL" is specified, method returns entire dictionary.
        :return: dictionary entry or entire dictionary self.__project_info
        """
        if parname == "ALL":
            return self.__project_info
        try:
            return self.__project_info[parname]
        except KeyError:
            return None

    def set_project_parameter(self, parname, value):
        """Sets a project parameter.

        :param parname: name of the parameter, contained in the keys of self.__project_info
        :param value: value of the parameter to be set
        """
        self.__project_info[parname] = value

    def get_project_path(self):
        """Returns the path of the current project. The path should never be modifiable.

        :return: self.__projectpath as string
        """
        return self.__projectpath

    def get_global_options(self, attribute):
        """Get the global options for the model. If a specific attribute is specified
        then method returns that particular attribute instead.

        :param attribute: specific attribute of option in the dictionary. If
                "ALL" is specified, returns whole dictionary instead.
        :return: self.__global_options or a specific entry of this dictionary.
        """
        if attribute == "ALL":
            return self.__global_options
        else:
            try:
                return self.__global_options[attribute]
            except KeyError:
                return None

    def set_data_library(self, datalib):
        """Sets the active data library using the object datalib of type UrbanBeatsDataLibrary()"""
        self.__datalibrary = datalib

    def get_data_library(self):
        """Returns the active data library of type UrbanBeatsDataLibrary()"""
        return self.__datalibrary

    def import_data_from_project(self, projectpath):
        """Imports and fills in the active data library using data from another project."""
        pass    #[TO DO]

    def import_archive_file(self, uba_filename):
        """Imports data from a data archive file into the active project's data archive."""
        pass    #[TO DO]

    def set_project_log(self, projectlog):
        """Sets the active project log using the object projectlog of type UrbanBeatsLog()"""
        self.__projectlog = projectlog

    def get_project_log(self):
        """Returns the active project log of type UrbanBeatsLog()"""
        return self.__projectlog

    def get_runtime(self):
        return self.__ubruntime

    def execute_runtime(self, module_obj, progressbar_observer):
        """Runs the UrbanBEATS Runtime based on the active module current in the runtime's run list."""
        if self.__ubruntime.runstate:
            self.__ubruntime.reinitialize()
        self.__ubruntime.define_active_module(module_obj)
        self.__ubruntime.attach_observers(self.__observers)
        self.__ubruntime.attach_progressbar(progressbar_observer)
        print("Active Scenario Thread", self.__ubruntime.ident)
        self.__ubruntime.start()

    def run(self):
        """Runs the UrbanBEATS Simulation based on the active scenario, data library, project
        info and other information."""
        if self.get_active_scenario() is None:
            self.update_observers("No active scenario selected!")
            return
        if self.get_active_boundary() is None:
            self.update_observers("Scenario has no assigned boundary!")
            return
        print("Running Active Scenario!")
        if self.__parent is None:
            pass
        else:
            self.__parent.enable_disable_run_controls(0)

        if self.__runtime_method == "SF":
            active_scenario = self.get_active_scenario()        # Get the active scenario
            self.update_runtime_progress(0)                     # Reset progress bar
            if active_scenario.runstate:                        # If active scenario has been run, reinitialize it
                if self.__parent is None:
                    pass
                else:
                    self.__parent.initialize_output_console()
                active_scenario.reinitialize()
            active_scenario.attach_observers(self.__observers)      # Attach the observers
            active_scenario.attach_progressbars(self.__progressbars)  # Attach the progressbar observers
            scenario_name = active_scenario.get_metadata("name")    # Get the name and report
            self.update_observers("Running Scenario: " + str(scenario_name))
            print("Running Scenario")
            print("Active Scenario Thread", active_scenario.ident)
            active_scenario.start()     # Start the active scenario thread      # Start the thread
        elif self.__runtime_method == "AF":
            pass    # TO DO - ALL SCENARIOS FULL SIMULATION AT ONCE.
        elif self.__runtime_method == "SP":
            pass    # TO DO - Single Scenario - Performance ONLY

    def export_assets(self, parameters):
        """Exports a set of assets from the current asset collection selected in the keyword arguments"""
        asset_col = self.__global_collections[parameters["assets"]]     # Grab the correct asset collection
        meta = asset_col.get_assets_with_identifier("meta")[0]          # And its metadata

        typename_geoms = {"Block": "POLYGON", "Hex": "POLYGON", "Fish": "POLYGON", "Geohash": "POLYGON",
                          "Cell": "POINT", "Centroid": "POINT", "Network": "LINE"}

        # Now identify which assets to export and loop through these
        for i in range(len(parameters["typenames"])):
            assettype = parameters["typenames"][i]
            assets = asset_col.get_assets_with_identifier(parameters["typenames"][i])
            ubassetexport.export_to_shapefile(assets, meta, parameters["path"], parameters["filename"],
                                              self.get_project_epsg(), assettype, typename_geoms[assettype])
        self.update_observers("Selected assets exported successfully")
        return True

    def on_thread_finished(self):
        """Called when the scenario has finished running. It updates the observes with the scenario finished message.
        and re-enables the run controls."""
        self.update_observers("Finished")
        # self.__parent and self.__parent.enable_disable_run_controls(1)

    def check_runtime_state(self):
        """Returns the current runtime progress value."""
        return self.__runtime_progress


class UrbanBeatsLog(object):
    """Class for logging the UrbanBEATS workflow, the log manages the history of the project
    as well as the current modelling session and is essential for tracking changes made throughout the
    workflow."""
    def __init__(self, projectpath):
        """Contains two main variables: one that contains the project's history, one that contains the
        current session's log."""
        self.__ublogger = []
        self.__ublogsession = []

    def write_to_log(self, message):
        """Probably the most commonly called function, writes a log entry and saves it to the log array"""
        logstring = ""

    def initialize_session(self):
        """Writes a title string to the log to indicate the start of a new session."""
        logstring = ""

    def save_log(self):
        """Saves the current complete log history to the log file in the project folder"""
        pass

    def load_log_history(self):
        """Loads the project log, reads the entire history."""
        pass

    def export_log(self, filepath):
        """Exports the log to an external file on the harddrive that the user can reader later on."""
        pass


