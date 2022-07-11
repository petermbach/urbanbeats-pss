r"""
@file   ubdatatypes.py
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

# --- CODE STRUCTURE ---
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import ast
import numpy as np
import gc
import pickle
import os

# --- URBANBEATS LIBRARY IMPORTS ---


class UBRasterData(object):
    """The UrbanBEATS Raster Data Object, which holds raster information and allows querying of raster cell
    values.
    """
    def __init__(self, metadata, rasterdata, rw):
        """ Initialises the UBRasterData Class, takes two arguments that are created either in ubspatial.py or can
        be formatted by the user.

        :param metadata: Python dictionary with following keys (lowercase): "ncols", "nrows", "nodata_value"
                        "xllcorner", "yllcorner"
        :param rasterdata: Numpy array with dimensions that correspond to "nrows" x "ncols" and with nodata values
                        corresponding to "nodata_value". Metadata MUST match!
        :param rw: stands for readwrite privileges, Boolean - True: write-enabled, False: read-only
        """
        self.__raster_name = ""
        self.__origin_filepath = ""
        self.__ncols = int(metadata["ncols"])                   # Number of columns
        self.__nrows = int(metadata["nrows"])                   # Number of rows
        self.__xllcorner = float(metadata["xllcorner"])         # The x-coordinate of the raster data's corner extent
        self.__yllcorner = float(metadata["yllcorner"])         # The y-coordinate of the raster data's corner extent
        self.__cellsize = float(metadata["cellsize"])           # Size of a raster cell (usually in [m])
        self.__nodatavalue = float(metadata["nodata_value"])    # The value used to represent 'no data'
        self.__data = rasterdata    # a numpy array of the data with dimensions nrows x ncols
        self.__setdata_option = rw  # depending on the setting, it'll allow the program to read/write to this file

    def set_name(self, raster_name):
        """Sets a name for the raster data. This may not necessarily be unique. Generally a string input."""
        self.__raster_name = raster_name

    def get_name(self):
        """Returns the name of the current raster data object instance."""
        return self.__raster_name

    def set_filepath(self, filepath):
        """Sets the origin filepath of the raster file, this is generally done if the Raster Data is loaded from
        an existing file. It allows the program to then call has_filepath() to check on the status of the data."""
        self.__origin_filepath = filepath

    def has_filepath(self):
        """Checks if the current rasterdata object has a filepath, i.e. has been saved onto the harddrive.

        :return the filename if the data has a filepath, False otherwise.
        """
        if self.__origin_filepath != "":
            return self.__origin_filepath
        else:
            return False

    def get_value(self, col, row):
        """Returns the cells value of the given column 'col' (x) and row (y), if there is an index error,
        then function return the corresponding 'nodata value'."""
        try:
            return self.__data[row, col]  # data[y][x]
        except IndexError:
            return "ERROR" #self.__nodatavalue

    def get_data(self):
        """Returns the full numpy raster array."""
        return self.__data

    def get_data_square(self, col_start, row_start, cells_wide, cells_tall):
        """Returns an entire rectangular section of the raster at the given coordinates.

        :param col_start: the starting column index
        :param row_start: the starting row index
        :param cells_wide: number of cells along columns
        :param cells_tall: number of cells along rows
        :return a matrix of raster data.
        """
        if cells_tall == 0 and cells_wide == 0:      # If the resolutions are identical or the input resolution > cells
            return self.__data[row_start, col_start]
        datamatrix = self.__data[row_start:row_start + cells_tall, col_start:col_start+cells_wide].astype('float32')
        return datamatrix

    def set_value(self, col, row, value):
        """Sets the value in the given column 'col' (x) and row (y) to the provided 'value'. If the raster
        is read-only, it does not carry out this operation and simply ends the function."""
        if self.__setdata_option:
            self.__data[row, col] = value
        return True

    def get_nodatavalue(self):
        """Returns the nodata value for the raster."""
        return self.__nodatavalue

    def get_dimensions(self):
        """Returns a vector [x,y] number of columns, number of rows"""
        return [self.__ncols, self.__nrows]

    def get_extents(self):
        """Returns a vector of the [x,y] extents of the raster data file"""
        return [self.__xllcorner, self.__yllcorner]

    def get_cellsize(self):
        """Returns the cell size of the raster data"""
        return self.__cellsize

    def reset_data(self):
        """Erases the data matrix (to free up memory), use only if necessary!"""
        self.__data = None
        return True

    def replace_nodatavalues(self, value):
        """Replaces the entire raster's nodata value with the specified 'value'"""
        self.__data[self.__data == self.__nodatavalue] = value
        return True

    def get_nonzero_count(self):
        """Returns the number of elements in the entire raster with non-zero values"""
        return np.count_nonzero(self.__data)

    def get_raster_sum(self):
        """Returns the straight up sum of the entire data set raster. Useful for querying map totals."""
        return self.__data.sum()


class UBComponent(object):
    """The most basic data container in UrbanBEATS, the UBComponent(), which can be used to store and manage
    any form of non-spatial data, e.g. an attributes list. It has several functions that allows its children
    to access when inherited.
    """
    def __init__(self):
        """Only contains the attribute property, but this is a private dictionary and can only be accessed
        through the class methods."""
        self.__attributes = {}

    def add_attribute(self, name, value):
        """Adds attribute of name and value to the self.__attribute dictionary."""
        self.__attributes[name] = value
        return True

    def set_attribute(self, name, value):
        """Allows setting of the attribute 'name' value to value only if that attribute exists."""
        try:
            self.__attributes[name] = value
        except KeyError:
            print("WARNING NO ATTRIBUTE NAMED: "+str(name))
        return True

    def change_attribute(self, name, value):
        """Changes an attribute of the Component() with name and value, if the attribute doesn't exist, it adds it
        to the list. The naming of this function is intentional even though it does the same thing as 'add attribute'
        """
        if name in self.__attributes.keys():
            self.__attributes[name] = value
        else:
            self.__attributes[name] = value

    def get_attribute(self, name):
        """Tries to return the value of attribute by name, if KeyError, returns None."""
        try:
            return self.__attributes[name]
        except KeyError:
            return None

    def get_all_attributes(self):
        """Returns the entire dictionary, use sparingly or primarily for exporting data."""
        return self.__attributes


class UBVector(UBComponent):
    """UrbanBEATS Vector Data Format, inherited from UBComponent, it stores geometric information
    for polygons, lines and points along with the ability to hold attributes."""
    def __init__(self, points, edges=None):
        UBComponent.__init__(self)
        self.__dtype = ""
        self.__points = points     # Required to draw the geometry
        self.__edges = edges
        self.__extents = []
        self.__centroidXY = []
        self.__nativeEPSG = None
        # self.__edges has None type if the data type is a point otherwise a tuple array of edges
        # of format ( ( (x1, y1), (x2, y2) ), ( ... ),  ... )

        self.determine_geometry(self.__points)

    def set_epsg(self, epsg):
        """Sets the native EPSG coordinate system code of the UBVector"""
        self.__nativeEPSG = epsg

    def get_epsg(self):
        """Returns the native EPSG code of the UBVector object."""
        return self.__nativeEPSG

    def change_coordinates(self, points):
        """Allows for the current coordinates to be changed, this may lead to a change in geometry
        which is communicated as a warning."""
        currentgeometry = self.__dtype
        self.__points = points
        self.determine_geometry(self.__points)
        if currentgeometry != self.__dtype:
            print("WARNING: GEOMETRY TYPE HAS CHANGED!")

    def get_points(self):
        """Returns an array of points (tuples), each having (x, y, z) sets of
        coordinates"""
        if len(self.__points) == 1:     # If the feature is simply a POINT features, then just return the x, y as tuple
            return self.__points[0]     # This catches the exception in scripts with points.
        return self.__points

    def get_edges(self):
        """Returns an array of edges (tuples), each having two pts with (x, y, z) sets of coordinates."""
        return self.__edges

    def get_extents(self):
        """Returns the map extents as [xmin, xmax, ymin, ymax]"""
        return self.__extents

    def get_centroid(self):
        """Returns the centroid XY coordinates."""
        return self.__centroidXY

    def shares_geometry(self, geom_object, geom_type="points", select="all"):
        """Determines whether the current geometry shares similar geometry with another UBVector object
        based on either points or edges.

        :param geom_object: the input UBVector object
        :param geom_type: check whether they share "points" or "edges"
        :param select: allows selection of specific points and/or edges to compare with (i.e. hexagonal edges),
        specified as an index of points in the list based on drawing convention (e.g. squares bottom left)
        :param precision: number of decimals to compare with, truncates the values to this value.
        :return: True if the geometries share at least one point/edge, false if they don't
        """
        if geom_type == "points":
            checkpoints = geom_object.get_points()
            if select == "all":
                thisgeom = self.__points
            else:
                thisgeom = [self.__points[i] for i in select]
            for pt in thisgeom:
                if pt in checkpoints:
                    return True
        elif geom_type == "edges":
            checkedges = geom_object.get_edges()
            if select == "all":
                thisgeom = self.__edges
            else:
                thisgeom = [self.__edges[i] for i in select]
            for ed in thisgeom:
                if ed in checkedges:
                    return True
        else:
            pass
        return False

    def determine_geometry(self, coordinates):
        """Determines what kind of geometry the current instance is and stores the type in
        the self.__dtype attribute."""
        if len(coordinates) == 1:
            self.__dtype = "POINT"
        elif len(coordinates) == 2:
            self.__dtype = "LINE"
        elif len(coordinates) > 2:
            if coordinates[0] == coordinates[len(coordinates) - 1]:
                self.__dtype = "FACE"
            else:
                self.__dtype = "POLYLINE"
        self.determine_extents()
        return True

    def get_geometry_type(self):
        return self.__dtype

    def determine_extents(self):
        """Determines the xmin, xmax, ymin, ymax and centroid"""
        xpoints = [self.__points[i][0] for i in range(len(self.__points))]
        ypoints = [self.__points[i][1] for i in range(len(self.__points))]
        self.__extents = [min(xpoints), max(xpoints), min(ypoints), max(ypoints)]
        self.__centroidXY = [(min(xpoints) + max(xpoints))/2.0, (min(ypoints) + max(ypoints))/2.0]
        return True


class UBCollection(object):
    """The UrbanBEATS Collection class structure. A collection stores a whole array of assets
    from the modelling outputs. It ca be used to organise geometric and non-geometric assets based
    on scenarios or other aspects of the spatial environment."""
    def __init__(self, identifier, containertype="Other"):
        self.__containername = identifier
        self.__containertype = containertype    # "Scenario", "Standalone", "Other"
        self.__assettypes = {}      # Type: [AssetGeometry, count]
        self.__globalassetcount = 0
        self.__assets = {}

    # General container management
    def get_container_name(self):
        return self.__containername

    def get_container_type(self):
        return self.__containertype

    def add_asset_type(self, assettype, geometry):
        if assettype not in self.__assettypes.keys():
            self.__assettypes[assettype] = [geometry, 0]

    def get_asset_types(self):
        return self.__assettypes

    # Simulation management - asset creation, modification etc.
    def add_asset(self, name, asset):
        """Adds a new asset with the given 'name' to the asset library and increases the global asset and
        asset type counters respectively."""
        self.__assets[name] = asset
        self.__globalassetcount += 1
        try:
            self.__assettypes[name.split("ID")[0]][1] += 1
        except KeyError:
            pass
        return True

    def get_asset_with_name(self, name):
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
        if "ID" in asset_identifier:  # e.g. if someone wrote "BlockID" as the asset identifier...
            nameid = asset_identifier
        else:
            nameid = asset_identifier + "ID"

        attribute_values = [[], []]  # Asset ID, Asset Value
        for asset in assetcol:
            if asset.get_attribute(nameid) in asset_ids:
                attribute_values[0].append(asset.get_attribute(nameid))
                attribute_values[1].append(asset.get_attribute(attribute_name))
        return attribute_values  # returned in ascending order of the asset_ids

    def remove_asset_by_name(self, name):
        """Removes an asset from the collection based on the name specified
        :param name: the key of the asset in the self.__assets dictionary.
        """
        try:
            del self.__assets[name]
            self.__globalassetcount -= 1
            try:
                self.__assettypes[name.split("ID")[0]][1] -= 1
            except KeyError:
                pass
        except KeyError:
            return True

    def reset_assets(self):
        """Erases all assets, leaves an empty assets dictionary. Carried out when resetting the simulation."""
        self.__assets = {}
        self.__assettypes = {}
        self.__globalassetcount = 0
        gc.collect()


class NeighbourhoodInfluenceFunction(object):
    """The neighbourhood influence function. A function type used in urban modelling to determine the interaction
    effects of one land use to another and to use its weight as a basis for determining the likelihood of a transition
    to that land use."""
    def __init__(self, nickname="unnamed", oluc="RES", tluc="RES", functiondict=None):
        """Initialisation of class constructor, takes several basic parameters.

        :param fid: Tracks the current ID of the
        :param oluc: origin land use, the land use the function applies to
        :param tluc: target land use, the land use the function searches for
        :param functiondict: a dictionary containing all parameters preset as str() type.
        """
        self.__functiontype = "IF"    # default function type is 'influence function'
        if functiondict is None:
            self.__functionID = None      # The function ID
            self.__functionnickname = nickname
            self.origin_landuse = oluc  # The land use the function applies to
            self.target_landuse = tluc  # The land use the function checks for
            self.__distance = []          # The distance list ()
            self.__weight = []            # The function y-value, weight list()
            self.datapoints = 0
        else:       # Define the function from the dictionary, which is full of strings.
            self.__functionID = functiondict["fid"]
            self.__functionnickname = functiondict["name"]
            self.origin_landuse = functiondict["oluc"]
            self.target_landuse = functiondict["tluc"]
            self.__distance = ast.literal_eval(functiondict["xdata"])
            self.__weight = ast.literal_eval(functiondict["ydata"])
            self.datapoints = len(self.__distance)

    def assign_id(self, idnum):
        """Assigns the provided idnum to the __functionID property. idnum is based on the function library
        current count with fx_ as prefix."""
        self.__functionID = idnum

    def get_y_range(self):
        return [min(self.__weight), max(self.__weight)]

    def get_x_range(self):
        return [min(self.__distance), max(self.__distance)]

    def assign_xy_data(self, xdata, ydata):
        """Assigns the list of x points to the __distance property and the list of y-points to the
        __weight property. Also updates data count."""
        self.__distance = xdata
        self.__weight = ydata
        self.datapoints = len(self.__distance)

    def get_xy_data(self):
        """Returns a multi-dimensional array of x and y points."""
        return [self.__distance, self.__weight]

    def get_function_type(self):
        """Returns the function type of 'IF', so that parts of the program know that this function belongs to the
        urban models."""
        return self.__functiontype

    def get_id(self):
        """Returns the unique ID of the function."""
        return self.__functionID

    def get_function_name(self):
        """Returns the name of the function."""
        return self.__functionnickname

    def set_function_name(self, fname):
        """Sets a new function name to fname."""
        self.__functionnickname = str(fname)

    def export_function_to_ubif(self, filepath):
        """Exports the current data to a ubif file. The file has origin and target land use saved.

        :param filepath: the full filepath where the file should be saved to including filename.
        """
        if ".ubif" not in filepath:
            f = open(filepath+".ubif", "w")
        else:
            f = open(filepath, "w")
        f.write("functionname,"+str(self.__functionnickname)+"\n")
        f.write("originluc,"+str(self.origin_landuse)+"\n")
        f.write("targetluc,"+str(self.target_landuse)+"\n")
        f.write("dist, weight\n")
        for i in range(len(self.__distance)):
            f.write(str(self.__distance[i]) + "," + str(self.__weight[i]) + "\n")
        f.close()
        return True

    def get_function_data_as_xml(self):
        """Serialises the function's data as an xml text that is used when saving the data to file."""
        xmltext = []
        xmltext.append('\t\t<function>\n')
        xmltext.append('\t\t\t<functiontype>IF</functiontype>\n')
        xmltext.append('\t\t\t<fid>'+str(self.__functionID)+'</fid>\n')
        xmltext.append('\t\t\t<name>'+str(self.__functionnickname)+'</name>\n')
        xmltext.append('\t\t\t<oluc>'+str(self.origin_landuse)+'</oluc>\n')
        xmltext.append('\t\t\t<tluc>'+str(self.target_landuse)+'</tluc>\n')
        xmltext.append('\t\t\t<xdata>'+str(self.__distance)+'</xdata>\n')
        xmltext.append('\t\t\t<ydata>'+str(self.__weight)+'</ydata>\n')
        xmltext.append('\t\t</function>\n')
        return xmltext

    def create_from_ubif(self, filepath):
        """Infills the distance and weight variables from a .ubif file. These files are written by default
        in the project directory when working with this data, but could also originate from a custom ubif.

        :param filepath: Full filepath to the ubif file. Stored in project\datalib folder
        :return:
        """
        f = open(filepath, 'r')
        data = []
        for lines in f:
            data.append(lines.rstrip("\n").split(","))
        f.close()
        for i in range(len(data)):
            if i == 0:
                self.__functionnickname = data[i][1]
            elif i == 1:
                self.origin_landuse = data[i][1]
            elif i == 2:
                self.target_landuse = data[i][1]
            elif i == 3:
                continue
            else:
                self.__distance.append(float(data[i][0]))
                self.__weight.append(float(data[i][1]))
        self.datapoints = len(self.__distance)
        return True

    def return_weight_by_distance(self, dist):
        """Scans the function and returns the weight value for a given distance. Interpolates if the value is
        not within the distance list.

        :param dist: the distance [m] from origin.
        """
        if dist < self.__distance[0]:
            return self.__weight[0]
        elif dist > self.__distance[len(self.__distance) - 1]:
            return self.__weight[len(self.__weight) - 1]

        for i in range(len(self.__distance) - 1):
            if self.__distance[i] <= dist < self.__distance[i + 1]:
                y1, y2 = self.__weight[i], self.__weight[i + 1]
                x1, x2 = self.__distance[i], self.__distance[i + 1]
                return float(y1+(dist - x1)*((y2-y1)/(x2-x1)))
            else:
                continue
        return True


def save_asset_collection(fullpath, collection):
    """Save the asset collection to a serialized object using pickle into the 'collections' folder of the project
    directory."""
    filePath = fullpath+"/collections/"+str(collection.get_container_name()+".ubcol")
    if os.path.exists(filePath):
        os.remove(filePath)
    f = open(filePath, 'wb')
    pickle.dump(collection, f)
    f.close()


def load_asset_collection(fullpath):
    """Load a serialized asset collection object using pickle from the specified fullpath."""
    if '.ubcol' not in fullpath:        # Add the extension if it doesn't exist
        fullpath = fullpath+".ubcol"
    print(fullpath)
    if os.path.exists(fullpath):
        f = open(fullpath, 'rb')
        obj = pickle.load(f)
        print(obj)
        f.close()
        return obj
    else:
        return None
