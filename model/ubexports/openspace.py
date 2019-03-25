r"""
@file   model\ubexports\openspace.py
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
import os

# URBANBEATS IMPORT
from ..ublibs import ubdatatypes as ubdata
from ..progref import ubglobals


def export_osnet_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports the open space network links to a GIS shapefile based on all OSNetID assets in the
    asset collection.

    :param asset_col: [] list containing all UBVector() OSNetID objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: active filepath to export these assets to
    :param filename: name of the file to export (without any .shp extension)
    :param epsg: the EPSG code for the coordinate system to use.
    :return:
    """
    if map_attr.get_attribute("HasOSNET") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname  # Placeholder filename
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename + ".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename) + ".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbLineString)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("OSNetID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NodeA", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("NodeB", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Distance", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_path = asset_col[i]
        linepoints = current_path.get_points()
        line = ogr.Geometry(ogr.wkbLineString)
        p1 = linepoints[0]
        p2 = linepoints[1]
        line.AddPoint(p1[0] + xmin, p1[1] + ymin)
        line.AddPoint(p2[0] + xmin, p2[1] + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        feature.SetField("OSNetID", int(current_path.get_attribute("OSNetID")))
        feature.SetField("NodeA", str(current_path.get_attribute("NodeA")))
        feature.SetField("NodeB", str(current_path.get_attribute("NodeB")))
        feature.SetField("Distance", float(current_path.get_attribute("Distance")))
        layer.CreateFeature(feature)

    shapefile.Destroy()
    return True


def export_oslink_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all flowpaths in the asset_col list to a GIS Shapefile based on the current filepath.

    :param asset_col: [] list containing all UBVector() OSLinkID objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :return:
    """
    if map_attr.get_attribute("HasOSLINK") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname  # Placeholder filename
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename + ".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename) + ".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbLineString)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("OSLinkID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Distance", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Location", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Landuse", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("AreaAccess", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("OS_Size", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_path = asset_col[i]
        linepoints = current_path.get_points()
        line = ogr.Geometry(ogr.wkbLineString)
        p1 = linepoints[0]
        p2 = linepoints[1]
        line.AddPoint(p1[0] + xmin, p1[1] + ymin)
        line.AddPoint(p2[0] + xmin, p2[1] + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        feature.SetField("OSLinkID", int(current_path.get_attribute("OSLinkID")))
        feature.SetField("Distance", float(current_path.get_attribute("Distance")))
        feature.SetField("Location", str(current_path.get_attribute("Location")))
        feature.SetField("Landuse", str(ubglobals.LANDUSENAMES[int(current_path.get_attribute("Landuse")) - 1]))
        feature.SetField("AreaAccess", float(current_path.get_attribute("AreaAccess")))
        feature.SetField("OS_Size", float(current_path.get_attribute("OS_Size")))
        layer.CreateFeature(feature)

    shapefile.Destroy()
    return True


def export_patch_buffers_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports buffers for all open space patches in the asset_col list to a GIS Shapefile based on the
    current filepath.

    :param asset_col: [] list containing all UBVector patch objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :return:
    """
    if map_attr.get_attribute("HasOSNET") != 1 or map_attr.get_attribute("HasOSLINK") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname  # A placeholder filename
    fileduplicate_counter = 0  # Tracks the number of duplicates
    while os.path.exists(str(usefilename + ".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename) + ".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbPolygon)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("PatchID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Landuse", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("PatchArea", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("BuffRadius", ogr.OFTReal))

    if map_attr.get_attribute("HasOSNET"):
        fielddefmatrix.append(ogr.FieldDefn("OSNet_Deg", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("OSNet_MinD", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_patch = asset_col[i]
        if current_patch.get_attribute("Landuse") not in [10, 11, 15]:
            continue
        patchpoint = current_patch.get_points()

        wkt = "POINT (" + str(patchpoint[0]+xmin) + " " + str(patchpoint[1]+ymin) + ")"
        pt = ogr.CreateGeometryFromWkt(wkt)
        buffer_radius = current_patch.get_attribute("BuffRadius")
        poly = pt.Buffer(buffer_radius)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(poly)
        feature.SetFID(0)

        feature.SetField("PatchID", int(current_patch.get_attribute("PatchID")))
        feature.SetField("BlockID", int(current_patch.get_attribute("BlockID")))
        feature.SetField("Landuse", ubglobals.LANDUSENAMES[int(current_patch.get_attribute("Landuse")) - 1])
        feature.SetField("PatchArea", float(current_patch.get_attribute("PatchArea")))
        feature.SetField("BuffRadius", float(current_patch.get_attribute("BuffRadius")))

        if map_attr.get_attribute("HasOSNET"):
            feature.SetField("OSNet_Deg", int(current_patch.get_attribute("OSNet_Deg")))
            feature.SetField("OSNet_MinD", float(current_patch.get_attribute("OSNet_MinD")))

        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True
