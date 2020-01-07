r"""
@file   model\ubexports\blocks.py
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


def export_sww_network_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg, fptype):
    """Exports all sewer networks in the asset_col list to a GIS Shapefile based on the current filepath.

    :param asset_col: [] list containing all UBVector() Flowpath objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :param fptype: type of Flowpath ("Blocks", "Patches")
    :return:
    """
    print(fptype)
    if map_attr.get_attribute("HasSWW") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname      # Placeholder filename
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename+".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename)+".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbLineString)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("SwwID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("UpID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("DownID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Z_up", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Z_down", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Length", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Min_zdrop", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("LinkType", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Slope", ogr.OFTReal))
    # fielddefmatrix.append(ogr.FieldDefn("BasinID", ogr.OFTInteger))
    # fielddefmatrix.append(ogr.FieldDefn("Outlet", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("UpstrIDs", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("DownstrIDs", ogr.OFTString))
    # fielddefmatrix.append(ogr.FieldDefn("HasSWW", ogr.OFTReal))

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

        feature.SetField("SwwID", int(current_path.get_attribute("SwwID")))
        feature.SetField("UpID", int(current_path.get_attribute("UpID")))
        feature.SetField("DownID", int(current_path.get_attribute("DownID")))
        feature.SetField("Z_up", float(current_path.get_attribute("Z_up")))
        feature.SetField("Z_down", float(current_path.get_attribute("Z_down")))
        feature.SetField("Length", float(current_path.get_attribute("Length")))
        feature.SetField("Min_zdrop", float(current_path.get_attribute("Min_zdrop")))
        feature.SetField("LinkType", str(current_path.get_attribute("LinkType")))
        feature.SetField("Slope", float(current_path.get_attribute("Slope")))
        # feature.SetField("BasinID", int(current_path.get_attribute("BasinID")))
        # feature.SetField("Outlet", int(current_path.get_attribute("Outlet")))
        feature.SetField("UpstrIDs", str(current_path.get_attribute("UpstrIDs")))
        feature.SetField("DownstrIDs", str(current_path.get_attribute("DownstrIDs")))

        # feature.SetField("HasSWW", int(current_path.get_attribute("HasSWW")))

        layer.CreateFeature(feature)
    shapefile.Destroy()


def export_sww_links_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg, fptype):
    """Exports all sewer networks in the asset_col list to a GIS Shapefile based on the current filepath.

    :param asset_col: [] list containing all UBVector() Flowpath objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :param fptype: type of Flowpath ("Blocks", "Patches")
    :return:
    """
    print(fptype)
    if map_attr.get_attribute("HasSWW") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname      # Placeholder filename
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename+".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename)+".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbLineString)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("LinkID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("v1", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("v2", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Length", ogr.OFTReal))
    # fielddefmatrix.append(ogr.FieldDefn("HasSWW", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("X1", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Y1", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Z1", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("X2", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Y2", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Z2", ogr.OFTReal))

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

        feature.SetField("LinkID", int(current_path.get_attribute("LinkID")))
        feature.SetField("v1", int(current_path.get_attribute("v1")))
        feature.SetField("v2", int(current_path.get_attribute("v2")))
        feature.SetField("Length", float(current_path.get_attribute("Length")))
        # feature.SetField("HasSWW", int(current_path.get_attribute("HasSWW")))
        feature.SetField("X1", float(current_path.get_attribute("X1")))
        feature.SetField("Y1", float(current_path.get_attribute("Y1")))
        feature.SetField("Z1", float(current_path.get_attribute("Z1")))
        feature.SetField("X2", float(current_path.get_attribute("X2")))
        feature.SetField("Y2", float(current_path.get_attribute("Y2")))
        feature.SetField("Z2", float(current_path.get_attribute("Z2")))

        layer.CreateFeature(feature)
    shapefile.Destroy()


def export_sww_mst_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg, fptype):
    """Exports links that belong to the minimum spanning tree of the sewer network in the asset_col list
    to a GIS Shapefile based on the current filepath.

    :param asset_col: [] list containing all UBVector() Flowpath objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :param fptype: type of Flowpath ("Blocks", "Patches")
    :return:
    """
    print(fptype)
    if map_attr.get_attribute("HasSWW") != 1:
        return True

    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname      # Placeholder filename
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename+".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename)+".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbLineString)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("MST_ID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("v1", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("v2", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Length", ogr.OFTReal))
    # fielddefmatrix.append(ogr.FieldDefn("HasSWW", ogr.OFTReal))

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

        feature.SetField("MST_ID", int(current_path.get_attribute("MST_ID")))
        feature.SetField("v1", int(current_path.get_attribute("v1")))
        feature.SetField("v2", int(current_path.get_attribute("v2")))
        feature.SetField("Length", float(current_path.get_attribute("Length")))
        # feature.SetField("HasSWW", int(current_path.get_attribute("HasSWW")))

        layer.CreateFeature(feature)
    shapefile.Destroy()
