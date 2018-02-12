# -*- coding: utf-8 -*-
"""
@file   ubdatalibrary.py
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
import os

# --- URBANBEATS LIBRARY IMPORTS ---
import modules.md_decisionanalysis
import modules.md_climatesetup
import modules.md_delinblocks
import modules.md_impactassess
import modules.md_perfassess
import modules.md_regulation
import modules.md_socioecon
import modules.md_spatialmapping
import modules.md_techplacement
import modules.md_urbandev
import modules.md_urbplanbb


# --- URBANBEATS DATA LIBRARY CLASS DEFINITION ---
class UrbanBeatsDataLibrary(object):
    def __init__(self, projectpath, keepcopy):
        # Assign properties and initialize variables
        self.__spatial_data = []
        self.__time_series_data = []
        self.__qual_data = []
        self.__data_library_idcount = 0
        self.__projectpath = projectpath
        self.__keepcopy = keepcopy  # Tracks whether to copy each data to the project folder

        # Create the data directory
        if os.path.isdir(projectpath+"/data"):  # Creates the data folder in the project path
            pass
        else:
            os.mkdir(projectpath+"/data")
        self.__projectdatafolder = projectpath+"/data/"

    def import_data(self):
        pass

    def add_data_to_library(self, dataref):
        """Adds an UrbanBeatsDataReference() instance to the data library. The reference object
        is created in the import_data() method. Required for the

        :param dataref: The data reference object created by instantiating the
                        UrbanBeatsDataReference() class
        """
        dataclass = dataref
        dataref.assign_id("ds_"+str(self.__data_library_idcount))
        if dataclass == "spatial":
            self.__spatial_data.append(dataref)
        elif dataclass == "temporal":
            self.__time_series_data.append(dataref)
        elif dataclass == "qualitative":
            self.__qual_data.append(dataref)
        self.__data_library_idcount += 1

    def delete_data(self, dataID):
        """Removes a data set from the library by searching for its unique dataID.

        :param dataID: the unique ID assigned to the data set upon importing.
        :return: None
        """
        pass

    def reset_library(self):
        """Resets the entire data library, i.e. deletes all files from the project /data folder
        and sets all data arrays to empty.

        :return: None
        """
        if self.__keepcopy:
            pass    #Delete all data from the data folder
        self.__spatial_data = []
        self.__time_series_data = []
        self.__qual_data = []
        self.__data_library_idcount = 0


# --- URBANBEATS DATA REFERENCE CLASS DEFINITION ---
class UrbanBeatsDataReference(object):
    def __init__(self, datatype, fullfilepath, projectpath, keepcopy, notes_text):
        """A data reference object that helps organise metadata information
        about the loaded data files in UrbanBEATS' data library.

        Data sets in the reference class are assigned metadata that will help the model
        identify how they are used throughout the project.

        They are differentiated by type, denoted by a 3-letter string:

        SPATIAL STRINGS:
            - LUC = land use classification
            - POP = population map (subtypes: count, density)
            - CAS = case study boundary
            - BND = internal boundaries (subtypes: geopolitical, suburban, catchment)
            - ELV = elevation
            - SOI = soil map (subtypes: infiltration rate, classification)
            - EMP = employment (subtype: count, density)
            - OVR = overlay (subtype: planning, groundwater, environmental, heritage, regulatory)
            - LOC = locality map
            - WAT = water bodies (subtypes: rivers, lakes)
            - INF = built infrastructure, (subtypes: network, WSUD, road)
        TEMPORAL STRINGS:
            - RAI = rainfall time series
            - EVP = evapotranspiration time series
            - SOL = solar radiation time series
            - TMP = temperature time series
        QUALITATIVE STRINGS:
            - QQQ = qualitative data (subtypes: tech matrix, survey, preference matrix)

        :param datatype: a 3-letter string that identifies the data type
        :param fullfilepath: original path to the data file
        :param projectpath: path to the project folder
        :param keepcopy: bool, keep a copy of the data in the project folder?
        :param notes_text: user written notes about the data file, can contain other metadata
        """
        # METADATA
        self.__dataID = None
        self.__dataclass = datatype["class"]    # e.g. spatial, time series, qualitative
        self.__datatype = datatype["parent"]    # e.g. overlay, rainfall, qualitative
        self.__datasubtype = datatype["sub"]    # e.g. heritage, none, tech matrix
        self.__dataformat = datatype["format"]  # e.g. .csv, .shp, .txt - so the model knows how to handle the data
        self.__notes = notes_text               # Further metadata or data description.

        # FILE LOCATION AND NAME
        self.__originaldatapath = os.path.dirname(fullfilepath)
        self.__projectdatapath = projectpath
        self.__datafilename = os.path.basename(fullfilepath)

        # HANDLING
        self.__keepcopy = keepcopy

        # ORGANIZE DATA
        self.__scenarionames = []   # Tracks all scenarios that this data is used in.

    def assign_id(self, idnum):
        """Assigns the provided idnum to the dataID property.  idnum is based on data library's current count with
        ds_ as prefix."""
        self.__dataID = idnum

    def assign_scenario(self, scenarioname):
        """Assigns the scenario name that has selected the data to its list of scenarios being used in."""
        if scenarioname not in self.__scenarionames:
            self.__scenarionames.append(scenarioname)
        else:
            pass

    def remove_from_scenario(self, scenarioname):
        """Removes the scenarioname from the list of scenarios the data is used in."""
        if scenarioname in self.__scenarionames:
            self.__scenarionames.remove(scenarioname)
        else:
            pass

    def check_for_data_file(self):
        """Performs a scan of the system to determine if the data file is still prsent. If the file is missing,
        function returns false."""
        pass

    def get_data_file_path(self):
        """Returns the full filepath to the data set. If keep copy is active (i.e. keep a copy
        in the project folder), then method returns the project-local filepath. Otherwise it returns
        the original filepath of the data."""
        if self.__keepcopy:
            return self.__projectdatapath+"/data/"
        else:
            return self.__originaldatapath

    def get_dataID(self):
        """Returns the identifier for the data object"""
        return self.__dataID

    def get_metadata(self, attribute):
        """Returns the corresponding piece of metadata (except for ID) based on input attribute

        :param attribute: str Options are 'class', 'parent', 'sub', 'format', 'notes'
        :return: corresponding meta data, if attribute is incorrect, returns None
        """
        if attribute == "class":
            return self.__dataclass
        elif attribute == "parent":
            return self.__datatype
        elif attribute == "sub":
            return self.__datasubtype
        elif attribute == "format":
            return self.__dataformat
        elif attribute == "notes":
            return self.__notes
        else:
            return None