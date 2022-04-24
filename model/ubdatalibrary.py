r"""
@file   ubdatalibrary.py
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
import os
import shutil
import pickle
import xml.etree.ElementTree as ET


# --- URBANBEATS DATA LIBRARY CLASS DEFINITION ---
class UrbanBeatsDataLibrary(object):
    def __init__(self, projectpath, keepcopy):
        # Data containers
        self.__spatial_data = []        # A list containing data reference objects for spatial data
        self.__temporal_data = []    # List for data reference of time series data
        self.__qual_data = []           # List of data references for qualitative data
        self.__functions = []

        # General Project Management
        self.__data_library_idcount = 0 # Tracks the current ID number
        self.__projectpath = projectpath    # The active project path - includes project name
        self.__keepcopy = keepcopy  # Tracks whether to copy each data to the project folder

        # Create the data directory
        if os.path.isdir(projectpath+"/datalib"):  # Creates the data folder in the project path
            pass
        else:
            os.mkdir(projectpath+"/datalib")
        self.__projectdatafolder = projectpath+"/datalib/"

    def get_project_path(self):
        """Returns the full path to the project folder."""
        return self.__projectpath

    def get_num_datafiles(self):
        """Returns the total number of data files currently in the data library."""
        return len(self.__spatial_data)+len(self.__temporal_data)+len(self.__qual_data)

    def add_data_to_library(self, dataref, count_incr):
        """Adds an UrbanBeatsDataReference() instance to the data library. The reference object
        is created in the import_data() method. Required for the

        :param dataref: The data reference object created by instantiating the
                        UrbanBeatsDataReference() class
        :param count_incr: A boolean, if True, increase the counting increment and adds an ID, if
                        false, then don't increase the counting increment (used when restoring library)
        """
        dataclass = dataref.get_metadata("class")
        if count_incr:
            dataref.assign_id("ID#ds_"+str(self.__data_library_idcount))

        if dataclass == "spatial":
            self.__spatial_data.append(dataref)
        elif dataclass == "temporal":
            self.__temporal_data.append(dataref)
        elif dataclass == "qualitative":
            self.__qual_data.append(dataref)
        elif dataclass == "function":
            self.__functions.append(dataref)

        if count_incr:
            self.__data_library_idcount += 1
            self.copy_data_to_project_folder(dataref)

    def copy_data_to_project_folder(self, dataref):
        """Copies the different data formats to the project folder depending on what has been selected."""
        if self.__keepcopy:
            # Path to directories (in case of multiple files copying)
            sourcefolder = dataref.get_original_data_path()+"/"
            destinationfolder = self.get_project_path() + str("/datalib/")

            # Path to the main data file
            sourcepath = dataref.get_original_data_path()+"/"+dataref.get_metadata("filename")
            destination = self.get_project_path()+str("/datalib/")+dataref.get_metadata("filename")

            filename, file_extension = os.path.splitext(sourcepath) # Gets the file extension and full path
            filename = os.path.basename(filename)   # Extracts the filename from the path

            if file_extension == ".shp":        # Are we dealing with a shapefile?
                for i in SHAPEFILEEXT:
                    if os.path.exists(sourcefolder+filename+i):  # Check for all files and delete them
                        shutil.copyfile(sourcefolder+filename+i, destinationfolder+filename+i)
            elif file_extension == ".tif":
                for i in GEOTIFF:
                    if os.path.exists(sourcefolder+filename+i):
                        shutil.copyfile(sourcefolder+filename+i, destinationfolder+filename+i)
            else:   # For any other normal file, we just copy source path to destination.
                shutil.copyfile(sourcepath, destination)

    def delete_data(self, dataID):
        """Removes a data set from the library by searching for its unique dataID.

        :param dataID: the unique ID assigned to the data set upon importing.
        :return: None
        """
        for i in range(len(self.__spatial_data)):
            if self.__spatial_data[i].get_data_id() == dataID:
                self.delete_data_from_project_folder(self.__spatial_data[i])
                self.__spatial_data.pop(i)
                return
        for i in range(len(self.__temporal_data)):
            if self.__temporal_data[i].get_data_id() == dataID:
                self.delete_data_from_project_folder(self.__time_series_data[i])
                self.__temporal_data.pop(i)
                return
        for i in range(len(self.__qual_data)):
            if self.__qual_data[i].get_data_id() == dataID:
                self.delete_data_from_project_folder(self.__qual_data[i])
                self.__qual_data.pop(i)

    def delete_data_from_project_folder(self, dataref):
        """Checks if the data file is present in the project folder and deletes it.

        :param dataref: the data reference object to be removed from the data library.
        """
        if self.__keepcopy:
            fulldatapath = self.get_project_path() + str("/datalib/") + dataref.get_metadata("filename")
            filename, ext = os.path.splitext(fulldatapath)
            if ext == ".shp":
                for i in SHAPEFILEEXT:
                    if os.path.isfile(filename+i):
                        os.remove(filename+i)
            elif ext == ".tif":
                for i in GEOTIFF:
                    if os.path.isfile(filename+i):
                        os.remove(filename+i)
            else:
                if os.path.isfile(fulldatapath):
                    os.remove(fulldatapath)

    def get_all_data_of_class(self, dataclass):
        """Returns one of the three data lists based on the input dataclass.

        :param dataclass: str() can be 'spatial', 'temporal' or 'qualitative'
        :return: list type of either self.__spatial_data, self.__time_series_data or self.__qual_data
        """
        if dataclass == "spatial":
            return self.__spatial_data
        elif dataclass == "temporal":
            return self.__temporal_data
        elif dataclass == "qualitative":
            return self.__qual_data
        else:
            return self.__functions

    def get_data_with_id(self, dataid):
        """Returns the data reference object with the indicated dataID.

        :param dataid: the unique dataID of the data reference given to it upon adding to the library
        :return: UrbanBeatsDataReference() object
        """
        for dataarray in [self.__spatial_data, self.__temporal_data, self.__qual_data, self.__functions]:
            for dataref in dataarray:
                if dataref.get_data_id() == dataid:
                    return dataref
        return None

    def remove_all_reference_to_scenario(self, scenario_name):
        """Removes all references to a given scenario name."""
        [dref.remove_from_scenario(scenario_name) for dref in self.__spatial_data]
        [dref.remove_from_scenario(scenario_name) for dref in self.__temporal_data]
        [dref.remove_from_scenario(scenario_name) for dref in self.__qual_data]
        [dref.remove_from_scenario(scenario_name) for dref in self.__functions]

    def reset_library(self):
        """Resets the entire data library, i.e. deletes all files from the project /data folder
        and sets all data arrays to empty.

        :return: None
        """
        if self.__keepcopy:
            pass    # Delete all data from the data folder
        self.__spatial_data = []
        self.__temporal_data = []
        self.__qual_data = []
        self.__functions = []
        self.__data_library_idcount = 0


# --- URBANBEATS DATA REFERENCE CLASS DEFINITION ---
class UrbanBeatsDataReference(object):
    def __init__(self, datatype, fullfilepath, projectpath, keepcopy, notes_text):
        """A data reference object that helps organise metadata information
        about the loaded data files in UrbanBEATS' data library.

        Data sets in the reference class are assigned metadata that will help the model
        identify how they are used throughout the project.

        Data naming convention are in the ubglobals.py file, which contains global variables.

        :param datatype: basic metadata in list form [class, category, subtype, format]
        :param fullfilepath: original path to the data file
        :param projectpath: path to the project folder
        :param keepcopy: bool, keep a copy of the data in the project folder?
        :param notes_text: user written notes about the data file, can contain other metadata
        """
        # KEY METADATA
        self.__dataID = None                # The unique ID assigned to the reference in the project

        # -- Data class and type
        self.__dataclass = datatype[0]      # Overarching class (i.e. spatial, temporal, qualitative, function)
        self.__type = datatype[1]           # Main category (i.e., land use, demographic, etc.)
        self.__subtype = datatype[2]        # Subtype (e.g. river, planning overlay, None, etc.)
        self.__data_format = datatype[4]    # General data format e.g., polygon, raster, point, line, time series

        # -- File Format
        self.__file_ext = datatype[3]       # File extension: .csv, .shp, etc.
        self.__originaldatapath = os.path.dirname(fullfilepath)  # Original filepath
        self.__projectdatapath = projectpath  # Path to the project data folder
        self.__datafilename = os.path.basename(fullfilepath)  # Filename

        # -- Description of data
        self.__notes = notes_text               # Further metadata or data description.

        # SCENARIO ORGANIZATION
        self.__scenarionames = []   # Tracks all scenarios that this data is used in.

        # HANDLING
        self.__keepcopy = keepcopy

    # DATA ID MANAGEMENT
    def assign_id(self, idnum):
        """Assigns the provided idnum to the dataID property.  idnum is based on data library's current count with
        ds_ as prefix."""
        self.__dataID = idnum

    def get_data_id(self):
        """Returns the identifier for the data object"""
        return self.__dataID

    # METADATA MANAGEMENT
    def get_metadata(self, attribute):
        """Returns the corresponding piece of metadata (except for ID) based on input attribute

        :param attribute: str Options are 'class', 'parent', 'sub', 'format', 'notes'
        :return: corresponding meta data, if attribute is incorrect, returns None
        """
        if attribute == "class":        # "spatial", "temporal", "qualitative"
            return self.__dataclass
        elif attribute == "type":     # "landuse", "population", etc.
            return self.__type
        elif attribute == "subtype":        # "density", "classification", etc.
            return self.__subtype
        elif attribute == "dataformat":     # ".shp", ".txt.", etc.
            return self.__data_format
        elif attribute == "file_ext":
            return self.__file_ext
        elif attribute == "filename":   # filename + extension.
            return self.__datafilename
        elif attribute == "notes":  # detailed notes on the data set.
            return self.__notes
        else:
            return None

    # SCENARIOS MANAGEMENT, whatever scenario the data is contained in
    def assign_scenario(self, scenarioname):
        """Assigns the scenario name that has selected the data to its list of scenarios being used in."""
        if scenarioname not in self.__scenarionames:
            self.__scenarionames.append(scenarioname)
        else:
            pass

    def get_scenario_list(self):
        """Returns the list of scenarios that the data file is intended to be used in."""
        return self.__scenarionames

    def remove_from_scenario(self, scenarioname):
        """Removes the scenarioname from the list of scenarios the data is used in."""
        if scenarioname in self.__scenarionames:
            self.__scenarionames.remove(scenarioname)
        else:
            pass

    # FILE MANAGEMENT
    def get_data_file_path(self):
        """Returns the full filepath to the data set. If keep copy is active (i.e. keep a copy
        in the project folder), then method returns the project-local filepath. Otherwise it returns
        the original filepath of the data."""
        if self.__keepcopy:
            return self.__projectdatapath+"/datalib/"
        else:
            return self.__originaldatapath+"/"

    def get_original_data_path(self):
        return self.__originaldatapath


# DATA LIBRARY METHODS
def save_data_library(datalibraryobj):
    """Serializes the entire data library to project folder. File extension of the pickle object is .ubdata"""
    fullpath = datalibraryobj.get_project_path()
    f = open(fullpath+'/datalib.ubdata', 'wb')
    pickle.dump(datalibraryobj, f)
    f.close()
    return True


def load_data_library(path):
    """Loads the entire data library object from project folder and returns the data library object."""
    if os.path.isfile(path+"/datalib.ubdata"):
        f = open(path+"/datalib.ubdata", 'rb')
        datalibrary = pickle.load(f)
        f.close()
        print(datalibrary.get_num_datafiles())
        return datalibrary
    return None

    #
    # def save_library(self):
    #     """Writes the data library information into the data library folder."""
    #     f = open(self.__projectdatafolder+"/dataindex.xml", 'w')
    #     f.write('<URBANBEATSDATALIBRARY creator="Peter M. Bach" version="1.0">\n')
    #     f.write('\t<datalibmeta>\n')
    #     f.write('\t\t<data_library_idcount>'+str(self.__data_library_idcount)
    #             +'</data_library_idcount>\n')
    #     f.write('\t</datalibmeta>\n')
    #     f.write('\t<datasets>\n')
    #     for dset in [self.__spatial_data, self.__time_series_data, self.__qual_data]:
    #         for d in dset:
    #             f.write('\t\t<dataref>\n')
    #             f.write('\t\t\t<dataid>'+str(d.get_data_id())+'</dataid>\n')
    #             f.write('\t\t\t<dataclass>' + str(d.get_metadata("class")) + '</dataclass>\n')
    #             f.write('\t\t\t<datafilename>' + str(d.get_metadata("filename")) + '</datafilename>\n')
    #             f.write('\t\t\t<dataformat>' + str(d.get_metadata("format")) + '</dataformat>\n')
    #             f.write('\t\t\t<datasubtype>' + str(d.get_metadata("sub")) + '</datasubtype>\n')
    #             f.write('\t\t\t<datatype>' + str(d.get_metadata("parent")) + '</datatype>\n')
    #             f.write('\t\t\t<notes>' + str(d.get_metadata("notes")) + '</notes>\n')
    #             f.write('\t\t\t<originaldatapath>' + str(d.get_original_data_path()) + '</originaldatapath>\n')
    #             f.write('\t\t\t<scenarionames>\n')
    #             scenario_list = d.get_scenario_list()
    #             if len(scenario_list) == 0:
    #                 f.write('\t\t\t\t<scenario></scenario>\n')
    #             for s in scenario_list:
    #                 f.write('\t\t\t\t<scenario>'+ str(s) + '</scenario>\n')
    #             f.write('\t\t\t</scenarionames>\n')
    #             f.write('\t\t</dataref>\n')
    #     f.write('\t</datasets>\n')
    #     f.write('</URBANBEATSDATALIBRARY>')
    #     f.close()
    #     return True
    #
    # def setup_library_from_xml(self):
    #     """Sets up the library from an xml file and restores all data references based on the
    #     information contained in the .xml file if it exists."""
    #     if os.path.isfile(self.__projectdatafolder + "/dataindex.xml"):
    #         dlib = ET.parse(self.__projectdatafolder + "/dataindex.xml")
    #         root = dlib.getroot()
    #         metadata = {}
    #         for child in root.find('datalibmeta'):      # Finding tag <datalibmeta> </datalibmeta>
    #             metadata[child.tag] = child.text
    #         self.__data_library_idcount = int(metadata["data_library_idcount"])
    #
    #         datasets = []
    #         for child in root.find('datasets'):     # Finding tag <datasets> </datasets>
    #             dataref = {}
    #             for d in child:
    #                 if d.tag == "scenarionames":
    #                     scenarios = []
    #                     for c in d:
    #                         scenarios.append(c.text)
    #                     dataref[d.tag] = scenarios
    #                     continue
    #                 dataref[d.tag] = d.text
    #
    #             # Create the Data Reference and add it to the data library
    #             datatype = [dataref["dataclass"], dataref["datatype"], dataref["datasubtype"],
    #                         dataref["dataformat"]]
    #             new_dref = UrbanBeatsDataReference(datatype,
    #                                                dataref["originaldatapath"]+"/"+dataref["datafilename"],
    #                                                self.__projectpath, self.__keepcopy,
    #                                                dataref["notes"])
    #             new_dref.assign_id(dataref["dataid"])
    #             self.add_data_to_library(new_dref, False)
    #         return True
    #     else:
    #         return False
    #
    # def import_data(self):
    #     pass    # [TO DO]
    #
    #
    #


# GLOBAL VARIABLES & CONSTANTS
DATACATEGORIES = ["Spatial Data", "Time Series Data", "Qualitative Data", "Functions"]

SPATIALDATA_DEFN = {"Boundaries": ["Geopolitical", "Suburban", "Planning Zones"],
                    "Built Environment": ["Buildings", "Roads", "Railways", "Urban Spaces", "Water Infrastructure"],
                    "Demographic": ["Population", "Employment", "Census", "Economic"],
                    "Features": ["Locality Map", "Monitoring Points"],
                    "Land Use/Cover": ["Land Use", "Land Cover"],
                    "Natural Features": ["Groundwater", "Lakes", "Rivers", "Soil", "Vegetation"],
                    "Overlays": ["Ecological", "Environmental", "Planning", "Regulatory"],
                    "Topography": [],
                    "Miscellaneous": []
                    }

TEMPORALDATA_DEFN = {"Economic": ["Discount/Inflation", "Growth Rates", "Valuation"],
                     "Hydrological": ["Rainfall", "Evapotranspiration", "Water Table"],
                     "Meteorological": ["Air Pressure", "Relative Humidity", "Solar Radiation", "Temperature"]
                     }

QUALDATA_DEFN = {"Preference Matrices": ["Sentiment", "Weighting"]
                 }

FUNCTIONS_DEFN = {"Adoption Curve": [],
                  "Influence": [],
                  "Value Scale": []}

# FILE FORMATS - some formats have multiple files associated with them, we need to know these when copying files over
# (1) -- SHAPEFILE --
# If we are dealing with a shapefile, need to copy all possible files across, file formats
# available at: https://www.loc.gov/preservation/digital/formats/fdd/fdd000280.shtml
SHAPEFILEEXT = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain",
                                ".aih", ".ixs", ".mxs", ".atx", ".shp.xml", ".cpg", ".qix"]
# (2) -- GEOTIFF --
# So far, noticing 4 key file formatst that may go hand in hand with the geotiff
GEOTIFF = [".tif", ".tfw", "tif.aux.xml", ".tif.ovr"]   # Need not necessarily use all, but used for checking

