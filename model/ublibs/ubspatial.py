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
import os

# URBANBEATS IMPORT
import ubdatatypes as ubdata
from ..progref import ubglobals


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
        print "Error, ASCII data not correctly labelled"
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
    :param naming: naming convention of type str() to be used.
    :param global_offsets: (x, y) coordinates that are used to offset the map's coordinates to 0,0 system
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')  # Load the shapefile driver and data source
    datasource = driver.Open(filepath)
    if datasource is None:
        print "Could not open shapefile!"
        return None

    layer = datasource.GetLayer(0)
    layerDefinition = layer.GetLayerDefn()
    attributecount = layerDefinition.GetFieldCount()
    attnames = []
    for a in range(attributecount):
        attnames.append(layerDefinition.GetFieldDefn(a).GetName())

    spatialref = layer.GetSpatialRef()
    inputprojcs = spatialref.GetAttrValue("PROJCS")
    if inputprojcs is None:
        print "Warning, spatial reference epsg cannot be found!"
        return None

    geometry_collection = []
    featurecount = layer.GetFeatureCount()
    # print "Feature Count in Map: ", featurecount  # For Debugging
    # print attnames    # For Debugging

    for i in range(featurecount):
        feature = layer.GetFeature(i)
        geom = feature.GetGeometryRef()
        area = geom.GetArea() / 1000000.0   # Conversion to km2
        # print "Name", str(naming) + "_ID" + str(i + 1)    # For Debugging
        # print "Area: ", area  # For Debugging

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
                polygon = ubdata.UBVector(coordinates)
                polygon.determine_geometry(coordinates)
                polygon.add_attribute("Map_Naming", str(naming)+"_ID"+str(i+1)+"-"+str(j+1))
                polygon.add_attribute("Area_sqkm", area)
                for n in attnames:
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

            polygon = ubdata.UBVector(coordinates)
            polygon.determine_geometry(coordinates)
            polygon.add_attribute("Map_Naming", str(naming)+"_ID"+str(i+1))
            polygon.add_attribute("Area_sqkm", area)
            for n in attnames:
                polygon.add_attribute(str(n), feature.GetFieldAsString(n))
            geometry_collection.append(polygon)
    return geometry_collection


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
        coordinates.append((ring.GetX(i), ring.GetY(i)))

    if option == "leaflet":
        # Reverse the x, y to form lat, long because in ESRI's case, lat almost always Y and long almost always X
        for p in range(len(coordinates)):
            coordinates[p] = [coordinates[p][1], coordinates[p][0]]
        mapstats["centroid"] = [(ymin + ymax) / 2.0, (xmin + xmax)/2.0]
    return coordinates, mapstats


def export_patches_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all the patches in the asset_col list to a GIS Shapefile based on the current filepath.

    :param asset_col: [] list containing all UBVector patch objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :return:
    """
    if map_attr.get_attribute("patchdelin") != 1 or map_attr.get_attribute("HasLUC") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname      # A placeholder filename
    fileduplicate_counter = 0   # Tracks the number of duplicates
    while os.path.exists(str(usefilename+".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename)+".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbPoint)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("PatchID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Landuse", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("AspectRatio", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("PatchSize", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("PatchArea", ogr.OFTReal))

    if map_attr.get_attribute("HasELEV"):
        fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_patch = asset_col[i]
        patchpoint = current_patch.get_points()
        centroid = ogr.Geometry(ogr.wkbPoint)
        centroid.AddPoint(patchpoint[0] + xmin, patchpoint[1] + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(centroid)
        feature.SetFID(0)

        feature.SetField("PatchID", int(current_patch.get_attribute("PatchID")))
        feature.SetField("BlockID", int(current_patch.get_attribute("BlockID")))
        feature.SetField("Landuse", ubglobals.LANDUSENAMES[int(current_patch.get_attribute("Landuse"))])
        feature.SetField("AspectRatio", float(current_patch.get_attribute("AspectRatio")))
        feature.SetField("PatchSize", int(current_patch.get_attribute("PatchSize")))
        feature.SetField("PatchArea", float(current_patch.get_attribute("PatchArea")))

        if map_attr.get_attribute("HasELEV"):
            feature.SetField("Elevation", float(current_patch.get_attribute("Elevation")))

        layer.CreateFeature(feature)

    shapefile.Destroy()
    return True

def export_block_assets_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all the assets in 'asset_col' to a GIS Shapefile based on the current filepath.

    :param asset_col: a list containing all assets to be exported to a shapefile
    :param map_attr: the global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    """
    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" +filename

    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname  # A placeholder filename
    fileduplicate_counter = 0   # Tracks the number of duplicates
    while os.path.exists(str(usefilename+".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename)+".shp")

    layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPolygon)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []

    # >>> FROM DELINBLOCKS
    fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("CentreX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentreY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Neighbours", ogr.OFTString))

    if map_attr.get_attribute("HasLUC"):
        # fielddefmatrix.append(ogr.FieldDefn("Status", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Active", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_RES", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_CIV", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_SVU", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_RD", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_PG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_REF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_UND", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_NA", ogr.OFTReal))

        if map_attr.get_attribute("HasSPATIALMETRICS"):
            fielddefmatrix.append(ogr.FieldDefn("Rich", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ShDiv", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ShDom", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ShEven", ogr.OFTReal))

    if map_attr.get_attribute("HasPOP"):
        fielddefmatrix.append(ogr.FieldDefn("Population", ogr.OFTReal))

    if map_attr.get_attribute("HasELEV"):
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MaxElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MinElev", ogr.OFTReal))

    if map_attr.get_attribute("HasGEOPOLITICAL"):
        fielddefmatrix.append(ogr.FieldDefn("Region", ogr.OFTString))

    if map_attr.get_attribute("HasSUBURBS"):
        fielddefmatrix.append(ogr.FieldDefn("Suburb", ogr.OFTString))


    # More attributes to come in future
    # Create the fields
    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    # Get Blocks Data
    for i in range(len(asset_col)):
        currentAttList = asset_col[i]
        if currentAttList.get_attribute("Status") == 0:
            continue

        # Draw Geometry
        line = ogr.Geometry(ogr.wkbPolygon)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        nl = currentAttList.get_points()
        for point in nl:
            ring.AddPoint(point[0]+xmin, point[1]+ymin)
        line.AddGeometry(ring)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        # Add Attributes
        feature.SetField("BlockID", int(currentAttList.get_attribute("BlockID")))
        feature.SetField("CentreX", float(currentAttList.get_attribute("CentreX")))
        feature.SetField("CentreY", float(currentAttList.get_attribute("CentreY")))
        feature.SetField("Neighbours", str(",".join(map(str, currentAttList.get_attribute("Neighbours")))))
        # Neighbourhood attribute converts the [ ] array of BlockIDs to a comma-separated list "#,#,#,#"

        if map_attr.get_attribute("HasLUC"):
            # feature.SetField("Status", float(currentAttList.get_attribute("Status")))
            feature.SetField("Active", float(currentAttList.get_attribute("Active")))
            feature.SetField("pLU_RES", float(currentAttList.get_attribute("pLU_RES")))
            feature.SetField("pLU_COM", float(currentAttList.get_attribute("pLU_COM")))
            feature.SetField("pLU_ORC", float(currentAttList.get_attribute("pLU_ORC")))
            feature.SetField("pLU_LI", float(currentAttList.get_attribute("pLU_LI")))
            feature.SetField("pLU_HI", float(currentAttList.get_attribute("pLU_HI")))
            feature.SetField("pLU_CIV", float(currentAttList.get_attribute("pLU_CIV")))
            feature.SetField("pLU_SVU", float(currentAttList.get_attribute("pLU_SVU")))
            feature.SetField("pLU_RD", float(currentAttList.get_attribute("pLU_RD")))
            feature.SetField("pLU_TR", float(currentAttList.get_attribute("pLU_TR")))
            feature.SetField("pLU_PG", float(currentAttList.get_attribute("pLU_PG")))
            feature.SetField("pLU_REF", float(currentAttList.get_attribute("pLU_REF")))
            feature.SetField("pLU_UND", float(currentAttList.get_attribute("pLU_UND")))
            feature.SetField("pLU_NA", float(currentAttList.get_attribute("pLU_NA")))

            if map_attr.get_attribute("HasSPATIALMETRICS"):
                feature.SetField("Rich", float(currentAttList.get_attribute("Rich")))
                feature.SetField("ShDiv", float(currentAttList.get_attribute("ShDiv")))
                feature.SetField("ShDom", float(currentAttList.get_attribute("ShDom")))
                feature.SetField("ShEven", float(currentAttList.get_attribute("ShEven")))

        if map_attr.get_attribute("HasPOP"):
            feature.SetField("Population", float(currentAttList.get_attribute("Population")))

        if map_attr.get_attribute("HasELEV"):
            feature.SetField("AvgElev", float(currentAttList.get_attribute("AvgElev")))
            feature.SetField("MaxElev", float(currentAttList.get_attribute("MaxElev")))
            feature.SetField("MinElev", float(currentAttList.get_attribute("MinElev")))

        if map_attr.get_attribute("HasGEOPOLITICAL"):
            feature.SetField("Region", str(currentAttList.get_attribute("Region")))

        if map_attr.get_attribute("HasSUBURBS"):
            feature.SetField("Suburb", str(currentAttList.get_attribute("Suburb")))


        layer.CreateFeature(feature)

    shapefile.Destroy()
    return True



# TEST SCRIPT - get_bounding_polygon() function
# MAPPATH = "C:/Users/peter/Documents/TempDocs/Files/Upperdandy/Boundary.shp"
# coordinates, mapstats = get_bounding_polygon(MAPPATH, "leaflet",
#                                              "C:/Users/peter/Documents/Coding Projects/UrbanBEATS-PSS")
# print mapstats
# print coordinates