# -*- coding: utf-8 -*-
"""
@file   ubspatial.py
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

import osgeo.osr as osr
import osgeo.ogr as ogr
import numpy as np

# URBANBEATS IMPORT
import ubdatatypes as ubdata


def import_ascii_raster(filepath, naming):
    """ Imports an ESRI ASCII format raster, i.e. text file format (different file extensions if created with ArcMap
    or QGIS, but internal data structure is the same. Returns an output UBRasterData() object

    The raster data loaded from this function is flipped to ensure that it conincides with the x and y. The indexing
    of the raster data, however, starts from zero! So n_cols and n_rows indices should be subtracted by 1 if the
    value is to be called from the file.

    Specification:
    http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/spatial_analyst_tools/esri_ascii_raster_format.htm
    NODATA_value is listed as 'optional', this function requires the NODATA value to be listed!

    :param filepath: The full filepath to the ASCII raster data file
    :return: UBRasterData() type
    """
    f = open(filepath, 'r')
    metadata = {}
    for i in range(6):
        metadata_line = f.readline().split()
        metadata[str(metadata_line[0]).lower()] = float(metadata_line[1])

    try:    # Attempt to create the numpy array to store the data
        dataarray = np.full((int(metadata["nrows"]), int(metadata["ncols"])), metadata["nodata_value"])
        # Numpy Array is created by specifying the "ROWS" first then "COLUMNS"
    except KeyError:
        print "Error, ASCII data not correctly labelled"
        return 0

    irow = 0     # To track the rows - i-th row and j-th column below
    for lines in f:
        a = lines.split()
        for jcol in range(len(a)):
            dataarray[irow, jcol] = a[jcol]
        irow += 1
    f.close()

    # Create the UBRasterData() data type
    rasterdata = ubdata.UBRasterData(metadata, dataarray, False)     # Create the object as read-only
    rasterdata.set_name(naming)
    rasterdata.set_filepath(filepath)
    return rasterdata


def calculate_offsets(raster_a, raster_b, cellsize):
    """Calculates the map offset between two rasters, based on raster A. This is used particularly in block delineation
    where the Land use Raster's extents are used and all other input maps are shifted and adjusted accordingly.

    :param rasterA: UBRasterData() object with fully contained data
    :param rasterB: UBRasterData() object with fully contained data
    :param cellsize: the cellsize of the raster files, preferably raster A
    """
    xllA, yllA = raster_a.get_extents()
    xllB, yllB = raster_b.get_extents()
    offset = [xllA - xllB, yllA - yllB]
    offset = [int(offset[0]/cellsize), int(offset[1]/cellsize)]
    return offset


def get_epsg(projcs, rootpath):
    """Uses ancillary/epsg.cfg to retrieve the EPSG code for a given spatial reference, if the coordinate
    system description is incorrect, it will return None.

    :param projcs: attribute value for the osr.SpatialReference() PROJCS, obtained using .GetAttrValue("PROJCS")
    :return:
    """
    f = open(rootpath+"/ancillary/epsg.cfg", 'r')   # Open the EPSG.cfg file and extract data
    epsg = None     # Holds the EPSG code
    for lines in f:
        epsg_line = lines.rstrip("\n").split(",")   # Prepares the line of data in the cfg file
        if epsg_line[1] == projcs:      # If the data file line matches the project coordinate system input
            epsg = int(epsg_line[0])     # Assign the EPSG
    f.close()   # The function is deliberately written in a way that forgoes the need for an array of EPSG data
    return epsg


def get_epsg_all(rootpath):
    """Returns a full list of all EPSG entries as a dictionary from ancillary/epsg.cfg"""
    f = open(rootpath+"/ancillary/epsg.cfg", 'r')   # Open the EPSG.cfg file and extract all data
    f.readline()
    epsg_dict = {}
    for lines in f:
        epsg_line = lines.rstrip("\n").split(",")
        epsg_dict[epsg_line[1]] = epsg_line[0]
    f.close()
    return epsg_dict


def create_coord_transformation_leaflet(inputEPSG):
    """Creates the coordinate transformation variable for the leaflet map, uses OSR library. The leaflet
    EPSG code is 4326, which is WGS84, geographic coordinate system.

    :param inputEPSG: the input EPSG code, format int(), specifying the EPSG of the input map. Can use get_epsg()
    :return: osr.CoordinateTransformation() object
    """
    inSpatial = osr.SpatialReference()
    inSpatial.ImportFromEPSG(inputEPSG)

    outSpatial = osr.SpatialReference()
    outSpatial.ImportFromEPSG(4326)

    coordTrans = osr.CoordinateTransformation(inSpatial, outSpatial)
    return coordTrans


def get_bounding_polygon(boundaryfile, option, rootpath):
    """Loads the boundary Shapefile and obtains the coordinates of the bounding polygon, returns as a list of coords.

    :param boundaryfile: full filepath to the boundary shapefile to load
    :param option: can obtain coordinates either in the input coordinate system or EPSG4326
    :return: a list() of coordinates in the format []
    """
    mapstats = {}
    driver = ogr.GetDriverByName('ESRI Shapefile')  # Load the shapefile driver and data source
    datasource = driver.Open(boundaryfile)
    if datasource is None:
        print "Could not open shapefile!"
        return []

    layer = datasource.GetLayer(0)  # Get the first layer, which should be the only layer!
    xmin, xmax, ymin, ymax = layer.GetExtent()
    # print xmin, xmax, ymin, ymax

    # Get some Map Metadata - the extents of the map, this is displayed later on in the pop-up window.
    point1 = ogr.Geometry(ogr.wkbPoint)
    point1.AddPoint(xmin, ymin)
    point2 = ogr.Geometry(ogr.wkbPoint)
    point2.AddPoint(xmax, ymax)

    # Get the spatial reference of the map
    spatialref = layer.GetSpatialRef()
    # print spatialref  # Debug Comment - if you want to view shapefile metadata, use this
    inputprojcs = spatialref.GetAttrValue("PROJCS")
    if inputprojcs is None:
        print "Warning, spatial reference epsg cannot be found"
        return []

    featurecount = layer.GetFeatureCount()
    # print "Total number of features: ", featurecount

    feature = layer.GetFeature(0)
    geom = feature.GetGeometryRef()

    area = geom.GetArea() / 1000000.0

    inputepsg1 = spatialref.GetAttrValue("AUTHORITY", 1)
    inputepsg2 = get_epsg(inputprojcs, rootpath)
    if inputepsg1 is None:
        inputepsg = inputepsg2
    else:
        if int(inputepsg1) == int(inputepsg2):
            inputepsg = inputepsg1
        else:
            inputepsg = inputepsg2
            # Experimenting with Marsh Ck Case Study's boundary, the embedded EPSG was not
            # correct. So I will have to default to this lookup config file.

    if option == "leaflet":
        coordtrans = create_coord_transformation_leaflet(int(inputepsg))
        geom.Transform(coordtrans)
        point1.Transform(coordtrans)
        point2.Transform(coordtrans)
        xmin = point1.GetX()
        ymin = point1.GetY()
        xmax = point2.GetX()
        ymax = point2.GetY()
        # print xmin, xmax, ymin, ymax

    mapstats["xmin"] = xmin
    mapstats["xmax"] = xmax
    mapstats["ymin"] = ymin
    mapstats["ymax"] = ymax
    mapstats["area"] = area
    mapstats["centroid"] = [(xmin + xmax)/2.0, (ymin + ymax)/2.0]
    mapstats["inputEPSG"] = inputepsg
    mapstats["coordsysname"] = inputprojcs
    coordinates = []
    ring = geom.GetGeometryRef(0)

    if ring.GetGeometryType() == -2147483645:   # POLYGON25D
        ring.FlattenTo2D()
        ring = ring.GetGeometryRef(0)
    # Need to test this on other Geometry Types including:
    #   -2147483642 MultiPolygon25D
    #   6 MultiPolygon
    #   https://gist.github.com/walkermatt/7121427

    points = ring.GetPointCount()
    # print "Ring Points: ", points
    for i in range(points):
        coordinates.append([ring.GetX(i), ring.GetY(i)])

    if option == "leaflet":
        # Reverse the x, y to form lat, long because in ESRI's case, lat almost always Y and long almost always X
        for p in range(len(coordinates)):
            coordinates[p] = [coordinates[p][1], coordinates[p][0]]
        mapstats["centroid"] = [(ymin + ymax) / 2.0, (xmin + xmax)/2.0]
    return coordinates, mapstats


# TEST SCRIPT - get_bounding_polygon() function
# MAPPATH = "C:/Users/peter/Documents/TempDocs/Files/Upperdandy/Boundary.shp"
# coordinates, mapstats = get_bounding_polygon(MAPPATH, "leaflet",
#                                              "C:/Users/peter/Documents/Coding Projects/UrbanBEATS-PSS")
# print mapstats
# print coordinates