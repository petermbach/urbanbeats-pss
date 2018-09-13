# -*- coding: utf-8 -*-
"""
@file   ubdatatypes.py
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
import numpy as np
import os
import gc
import tempfile

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
        """Returns the cells value of the given column 'col' (x) and row (y)"""
        try:
            return self.__data[row, col]  # data[y][x]
        except IndexError:
            return self.__nodatavalue

    def get_data(self):
        """Returns the full numpy raster array."""
        return self.__data

    def set_value(self, col, row, value):
        """Sets the value in the given column 'col' (x) and row (y) to the provided 'value'. If the raster
        is read-only, it does not carry out this operation and simply ends the function."""
        if self.__setdata_option:
            self.__data[row, col] = value
        return True

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
            print "WARNING NO ATTTRIBUTE NAMED: "+str(name)
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
    def __init__(self, coordinates):
        UBComponent.__init__(self)
        self.__dtype = ""
        self.__coordinates = coordinates
        self.determine_geometry(self.__coordinates)

    def change_coordintaes(self, coordinates):
        """Allows for the current coordinates to be changed, this may lead to a change in geometry
        which is communicated as a warning."""
        currentgeometry = self.__dtype
        self.__coordinates = coordinates
        self.determine_geometry(self.__coordinates)
        if currentgeometry != self.__dtype:
            print "WARNING: GEOMETRY TYPE HAS CHANGED!"

    def get_coordinates(self):
        """Returns an array of points (tuples), each having (x, y, z) sets of
        coordinates"""
        return self.__coordinates

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
        return True

class UBCollection(object):
    """The UrbanBEATS Collection class structure. A collection stores a whole array of assets
    from the modelling outputs. It ca be used to organise geometric and non-geometric assets based
    on scenarios or other aspects of the spatial environment."""
    def __init__(self):
        self.__assetcount = 0
        self.__assets = []

    def append_asset(self, asset):
        """Adds an asset object to the collection."""
        self.__assets.append(asset)
        return True

    def get_asset_by_attribute(self, attribute, value):
        """Scans all assets for the attribute and returns the ones with the correct attribute and value."""
        # TO DO
        return True
