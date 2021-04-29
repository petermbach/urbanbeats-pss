r"""
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
from . import ubdatatypes as ubdata


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
        dataarray = np.empty([int(metadata["nrows"]), int(metadata["ncols"])])
        # Numpy Array is created by specifying the "ROWS" first then "COLUMNS"
    except KeyError:
        print("Error, ASCII data not correctly labelled")
        return 0

    irow = 0     # To track the rows - i-th row and j-th column below
    for lines in f:
        a = lines.split()
        for jcol in range(len(a)):
            dataarray[irow, jcol] = a[jcol]
        irow += 1
    f.close()

    # Flip the raster data
    dataarray = np.flip(dataarray, 0)

    # Create the UBRasterData() data type
    rasterdata = ubdata.UBRasterData(metadata, dataarray, False)     # Create the object as read-only
    rasterdata.set_name(naming)
    rasterdata.set_filepath(filepath)
    return rasterdata


def import_polygonal_map(filepath, option, naming, global_offsets):
    """Imports a polygonal map and saves the information into a UBVector format. Returns a list [ ] of UBVector()
    objects.

    :param filepath: full filepath to the file
    :param option: can obtain coordinates either in the input coordinate system or EPSG4326
                    if the option is "RINGPOINTS", returns simply a points list of all ring points
    :param naming: naming convention of type str() to be used.
    :param global_offsets: (x, y) coordinates that are used to offset the map's coordinates to 0,0 system
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')  # Load the shapefile driver and data source
    datasource = driver.Open(filepath)
    if datasource is None:
        print("Could not open shapefile!")
        return None

    layer = datasource.GetLayer(0)
    layerDefinition = layer.GetLayerDefn()
    attributecount = layerDefinition.GetFieldCount()
    attnames = []   # Will contain all the names of attributes in the Shapefile
    for a in range(attributecount):
        attnames.append(layerDefinition.GetFieldDefn(a).GetName())

    spatialref = layer.GetSpatialRef()
    inputprojcs = spatialref.GetAttrValue("PROJCS")
    if inputprojcs is None:
        print("Warning, spatial reference epsg cannot be found!")
        return None

    geometry_collection = []
    featurecount = layer.GetFeatureCount()
    # print(f"Feature Count in Map: {featurecount}")  # For Debugging
    # print(attnames)    # For Debugging

    for i in range(featurecount):
        feature = layer.GetFeature(i)
        geom = feature.GetGeometryRef()
        area = geom.GetArea() / 1000000.0   # Conversion to km2
        # print(f"Name {str(naming)}_ID{str(i + 1)}")    # For Debugging
        # print(f"Area: {area}")  # For Debugging

        # Projection    check for later... [TO DO]
        if option == "leaflet":     # [TO DO]
            pass

        if geom.GetGeometryName() == "MULTIPOLYGON":
            for g in geom:
                ring = g.GetGeometryRef(0)
                points = ring.GetPointCount()
                coordinates = []
                for j in range(points):
                    coordinates.append((ring.GetX(j) - global_offsets[0], ring.GetY(j) - global_offsets[1]))
                if option == "RINGPOINTS":
                    for c in coordinates:
                        geometry_collection.append(c)
                elif option == "RINGS":
                    geometry_collection.append(coordinates)
                else:
                    polygon = ubdata.UBVector(coordinates)
                    polygon.determine_geometry(coordinates)
                    polygon.add_attribute("Map_Naming", str(naming)+"_ID"+str(i+1)+"-"+str(j+1))
                    polygon.add_attribute("Area_sqkm", area)
                    for n in attnames:      # Assign all attribute data to the UBVector() instance
                        polygon.add_attribute(str(n), feature.GetFieldAsString(n))
                    geometry_collection.append(polygon)
        else:
            ring = geom.GetGeometryRef(0)
            if ring.GetGeometryType() == -2147483645:   # POLYGON25D
                ring.FlattenTo2D()
                ring = ring.GetGeometryRef(0)

            points = ring.GetPointCount()
            coordinates = []
            for j in range(points):
                coordinates.append((ring.GetX(j) - global_offsets[0], ring.GetY(j) - global_offsets[1]))
            if option == "RINGPOINTS":      # Just want a map of points
                for c in coordinates:
                    geometry_collection.append(c)
            elif option == "RINGS":
                geometry_collection.append(coordinates)
            else:
                polygon = ubdata.UBVector(coordinates)
                polygon.determine_geometry(coordinates)
                polygon.add_attribute("Map_Naming", str(naming)+"_ID"+str(i+1))
                polygon.add_attribute("Area_sqkm", area)
                for n in attnames:
                    polygon.add_attribute(str(n), feature.GetFieldAsString(n))
                geometry_collection.append(polygon)
    return geometry_collection


def import_linear_network(filename, option, global_offsets, **kwargs):
    """Imports the shapefile containing the line data and transfers the information into an array of tuples.
    The import algorithm checks the shapefile's geometry and Segmentizes Lines and MultiLine geometry. The function
    should be called on operations involving rivers, water infrastructure, roads and other types of networks. If a
    UBVector() object is returned, then all attributes from the original shapefile will be contained therein.

    :param filename: Full filepath to the shapefile to be imported
    :param option: Data format to be returned by the function "Points" or "Lines" or "Leaflet"
    :param global_offsets: The global xmin/ymin to convert the data to (0,0) origin
    :param kwargs: "Segments" - specifies the number of segmentations if using POINTS format, usually Blocksize / 4
    :return: A list of tuples containing all points of the river (POINTS) or a list of UBVector() instances.
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')  # Open the file and get the total number of features
    data = driver.Open(filename, 0)
    if data is None:
        return None
    layer = data.GetLayer()
    totfeatures = layer.GetFeatureCount()

    spatial_ref = layer.GetSpatialRef()     # Obtain spatial reference
    inputprojcs = spatial_ref.GetAttrValue("PROJCS")
    if inputprojcs is None:
        print("Warning, spatial reference epsg cannot be found!")
        return None

    layerDef = layer.GetLayerDefn()
    attnames = []
    for f in range(layerDef.GetFieldCount()):
        attnames.append(layerDef.GetFieldDefn(f).GetName())

    # LEAFLET FORMAT , need to do Projection [TO DO]
    if option == "LEAFLET":  # [TO DO]
        pass

    if option == "POINTS":      # We only care about the coordinates, but not the actual lines and attributes
        try:
            segmentmax = kwargs["Segments"]     # Checks the segments, if this hasn't been specified, continue
        except KeyError:
            print("Error, no segments specified.")
            return None
        featurepoints = []
        for i in range(totfeatures):
            currentfeature = layer.GetFeature(i)
            geometry = currentfeature.GetGeometryRef()
            if geometry.GetGeometryType() in [2, -2147483646]:  # LINE or LINESTRING25D
                if geometry.GetGeometryType() == -2147483646:
                    geometry.FlattenTo2D()
                geometry.Segmentize(segmentmax)
                for j in range(geometry.GetPointCount()):  # Get points
                    featurepoints.append((geometry.GetX(j) - global_offsets[0], geometry.GetY(j) - global_offsets[1]))
            elif geometry.GetGeometryType() in [5, -2147483643]:  # MULTILINESTRING
                if geometry.GetGeometryType() == -2147483643:
                    geometry.FlattenTo2D()
                for j in range(geometry.GetGeometryCount()):  # Loop through geometries
                    linestring = geometry.GetGeometryRef(j)
                    linestring.Segmentize(segmentmax)
                    for k in range(linestring.GetPointCount()):  # Get points
                        featurepoints.append((linestring.GetX(k) - global_offsets[0],
                                              linestring.GetY(k) - global_offsets[1]))
        return featurepoints
    elif option == "LINES":     # We want UBVector() instances of line objects to do geometric operations with
        linefeatures = []
        for i in range(totfeatures):
            currentfeature = layer.GetFeature(i)
            geometry = currentfeature.GetGeometryRef()
            if geometry.GetGeometryType() in [2, -2147483646]:     # LINESTRING or LINESTRING25D
                if geometry.GetGeometryType() == -2147483646:
                    geometry.FlattenTo2D()
                    # geometry = geometry.GetGeometryRef(0)
                coordinates = []
                for j in range(geometry.GetPointCount()):
                    coordinates.append((geometry.GetX(j) - global_offsets[0], geometry.GetY(j) - global_offsets[1]))
                linefeature = ubdata.UBVector(coordinates)
                linefeature.determine_geometry(coordinates)
                for a in attnames:
                    linefeature.add_attribute(str(a), currentfeature.GetFieldAsString(a))
                linefeatures.append(linefeature)
            elif geometry.GetGeometryType() in [5, -2147483643]:   # MULTILINESTRING or MULTILINESTRING25D
                if geometry.GetGeometryType() == -2147483643:
                    geometry.FlattenTo2D()
                    # geometry = geometry.GetGeometryRef(0)       # Need to check if this is possible...
                for j in range(geometry.GetGeometryCount()):
                    linestring = geometry.GetGeometryRef(j)
                    coordinates = []
                    for k in range(linestring.GetPointCount()):
                        coordinates.append((linestring.GetX(k) - global_offsets[0],
                                            linestring.GetY(k) - global_offsets[1]))
                    linefeature = ubdata.UBVector(coordinates)
                    linefeature.determine_geometry(coordinates)
                    for a in attnames:
                        linefeature.add_attribute(str(a), currentfeature.GetFieldAsString(a))
                    linefeatures.append(linefeature)
        return linefeatures


def import_point_features(filepath, option, global_offsets):
    """Imports a map of points and saves the information into a UBVector format. Returns a list [ ] of UBVector()
    objects.

    :param filepath: full filepath to the file
    :param option: "LEAFLET" - uses coordinate system or EPSG4326, "POINTS" - returns UBVectors() in corresponding CS
                    "POINTCOORD" - returns just the coordinates in local coordinate system.
    :param global_offsets: (x, y) coordinates that are used to offset the map's coordinates to 0,0 system
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')  # Create the Shapefile driver
    datasource = driver.Open(filepath)
    if datasource is None:
        return None     # Return none if there is no map

    layer = datasource.GetLayer(0)  # Get the first layer, which should be the only layer!

    spatialref = layer.GetSpatialRef()
    inputprojcs = spatialref.GetAttrValue("PROJCS")
    if inputprojcs is None:
        print("Warning, spatial reference epsg cannot be found")
        return None

    featurecount = layer.GetFeatureCount()

    layerDefinition = layer.GetLayerDefn()
    attnames = []
    for att in range(layerDefinition.GetFieldCount()):
        attnames.append(layerDefinition.GetFieldDefn(att).GetName())

    # LEAFLET FORMAT, need to do Project [TO DO]
    if option == "LEAFLET":
        pass

    if option in ["POINTS", "POINTCOORDS"]:     # POINTS --> UBVECTORS() get return, otherwise just coordinates
        pointfeatures = []
        for i in range(featurecount):
            feature = layer.GetFeature(i)
            geom = feature.GetGeometryRef()  # GET GEOMETRY
            if geom.GetGeometryType() in [4, -2147483644]:      # MULTIPOINT or MULTIPOINT25D
                if geom.GetGeometryType == -2147483644:
                    geom.FlattenTo2D()
                for g in range(geom.GetGeometryCount()):
                    pt = geom.GetGeometryRef(g)
                    coordinates = (pt.GetX() - global_offsets[0], pt.GetY() - global_offsets[1])
                    if option == "POINTS":
                        pointfeature = ubdata.UBVector(coordinates)
                        pointfeature.determine_geometry(coordinates)
                        for a in attnames:
                            pointfeature.add_attribute(str(a), feature.GetFieldAsString(a))
                        pointfeatures.append(pointfeature)
                    else:
                        pointfeatures.append(coordinates)
            else:  # Geometry Type in [1, -2147483647] # Point or Point 25D
                if geom.GetGeometryType() == -2147483647:  # POINT25D
                    geom.FlattenTo2D()
                coordinates = (geom.GetX() - global_offsets[0], geom.GetY() - global_offsets[1])
                if option == "POINTS":
                    pointfeature = ubdata.UBVector(coordinates)
                    pointfeature.determine_geometry(coordinates)
                    for a in attnames:
                        pointfeature.add_attribute(str(a), feature.GetFieldAsString(a))
                    pointfeatures.append(pointfeature)
                else:
                    pointfeatures.append(coordinates)
        return pointfeatures


def calculate_offsets(map_input, global_extents):
    """Calculates the map offset between two rasters, based on raster A. This is used particularly in block delineation
    where the Land use Raster's extents are used and all other input maps are shifted and adjusted accordingly.

    :param map_input: UBRasterData() object with fully contained data
    :param global_extents: map_attributes asset object with fully contained data
    """
    xll_map, yll_map = map_input.get_extents()
    cellsize = float(map_input.get_cellsize())
    offset = [xll_map - global_extents.get_attribute("xllcorner"),
              yll_map - global_extents.get_attribute("yllcorner")]
    offset = [int(offset[0]/cellsize), int(offset[1]/cellsize)]
    return offset

def adjust_position_by_offset(origin_position, offset, csc):
    """Adjusts the starting position index based on a given offset. For example, a population input map offset by
    an x or y value will not align correctly with a boundary map. This function, determines where in the raster to
    look for."""
    if (origin_position - offset) < 0:
        csc_adj = csc + origin_position
        start_position = 0
    else:
        csc_adj = csc
        start_position = origin_position - offset
    return start_position, csc_adj


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


def load_shapefile_details(file):
    """ Loads the basic shapefile for a few key properties including Map Extent, Number of Features, List of Attributes
    and EPSG Code

    :param file: Full path to the shapefile
    :return: a list containing geometry type (0) map extent (1-4), spatialref (5-6), feature count (7),
            attribute names (8-list)
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')  # Loads the shapefile driver and data source
    datasource = driver.Open(file)
    if datasource is None:
        return "Shapefile not found!"

    layer = datasource.GetLayer(0)
    xmin, xmax, ymin, ymax = layer.GetExtent()  # Map extents
    print(f"{xmin}, {xmax}, {ymin}, {ymax}")

    spatialref = layer.GetSpatialRef()          # Coordinate system
    inputprojcs = "(none)"
    epsg = "(none)"
    if spatialref is not None:
        inputprojcs = spatialref.GetAttrValue("PROJCS")
        epsg = spatialref.GetAttrValue("PROJCS|AUTHORITY", 1)
    print(epsg)

    featurecount = layer.GetFeatureCount()      # Total number of features
    print(featurecount)
    if featurecount == 0:
        return "Shapefile has no features!"

    layerDefn = layer.GetLayerDefn()            # Get attribute names
    attnames = [layerDefn.GetFieldDefn(i).name for i in range(layerDefn.GetFieldCount())]

    feature = layer.GetFeature(0)               # Get Geometry Type
    geometry = feature.GetGeometryRef()
    print ([geometry.GetGeometryName(), xmin, xmax, ymin, ymax, inputprojcs, epsg, featurecount, attnames])
    return [geometry.GetGeometryName(), xmin, xmax, ymin, ymax, inputprojcs, epsg, featurecount, attnames]


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
        print("Could not open shapefile!")
        return []

    layer = datasource.GetLayer(0)  # Get the first layer, which should be the only layer!
    xmin, xmax, ymin, ymax = layer.GetExtent()      # CONVENTION: LATITUDE = Y, LONGITUDE = X
    print(f"{xmin}, {xmax}, {ymin}, {ymax}")

    # Get some Map Metadata - the extents of the map, this is displayed later on in the pop-up window.
    point1 = ogr.Geometry(ogr.wkbPoint)
    point1.AddPoint(xmin, ymin)
    point2 = ogr.Geometry(ogr.wkbPoint)
    point2.AddPoint(xmax, ymax)

    # Get the spatial reference of the map
    spatialref = layer.GetSpatialRef()
    print(spatialref)  # Debug Comment - if you want to view shapefile metadata, use this
    inputprojcs = spatialref.GetAttrValue("PROJCS")
    if inputprojcs is None:
        print("Warning, spatial reference epsg cannot be found")
        return []

    featurecount = layer.GetFeatureCount()
    print(f"Total number of features: {featurecount}")

    feature = layer.GetFeature(0)
    geom = feature.GetGeometryRef()

    area = geom.GetArea() / 1000000.0

    inputepsg1 = spatialref.GetAttrValue("AUTHORITY", 1)
    inputepsg2 = get_epsg(inputprojcs, rootpath)

    if inputepsg1 is None:
        inputepsg = inputepsg2
    elif inputepsg2 is None:
        inputepsg = inputepsg1
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
    # print(f"Ring Points: {points}")
    for i in range(points):
        coordinates.append((ring.GetX(i), ring.GetY(i)))

    if option == "leaflet":
        # Reverse the x, y to form lat, long because in ESRI's case, lat almost always Y and long almost always X
        for p in range(len(coordinates)):
            coordinates[p] = [coordinates[p][0], coordinates[p][1]]
        mapstats["centroid"] = [(xmin + xmax) / 2.0, (ymin + ymax)/2.0]
    return coordinates, mapstats

# # TEST SCRIPT - get_bounding_polygon() function
# MAPPATH = r"C:\Users\peter\Dropbox\UrbanBEATS Benchmark Case Studies\AU VIC Upper Dandenong Ck\Input Files\Boundary_UTM.shp"
# coordinates, mapstats = get_bounding_polygon(MAPPATH, "leaflet",
#                                              "C:/Users/peter/Documents/Coding Projects/UrbanBEATS-PSS")
# print(mapstats)
# print(coordinates)