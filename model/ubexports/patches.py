# -*- coding: utf-8 -*-
"""
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

# URBANBEATS IMPORT
from ..ublibs import ubdatatypes as ubdata
from ..progref import ubglobals


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
    fielddefmatrix.append(ogr.FieldDefn("AspRatio", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("PatchSize", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("PatchArea", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("BuffRadius", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentroidX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentroidY", ogr.OFTReal))

    if map_attr.get_attribute("HasOSLINK"):
        fielddefmatrix.append(ogr.FieldDefn("GSD_Dist", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("GSD_Loc", ogr.OFTString))
        fielddefmatrix.append(ogr.FieldDefn("GSD_Deg", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("GSD_ACon", ogr.OFTReal))
    if map_attr.get_attribute("HasOSNET"):
        fielddefmatrix.append(ogr.FieldDefn("OSNet_Deg", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("OSNet_MinD", ogr.OFTReal))

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
        feature.SetField("Landuse", ubglobals.LANDUSENAMES[int(current_patch.get_attribute("Landuse"))-1])
        feature.SetField("AspRatio", float(current_patch.get_attribute("AspRatio")))
        feature.SetField("PatchSize", int(current_patch.get_attribute("PatchSize")))
        feature.SetField("PatchArea", float(current_patch.get_attribute("PatchArea")))
        feature.SetField("BuffRadius", float(current_patch.get_attribute("BuffRadius")))
        feature.SetField("CentroidX", float(current_patch.get_attribute("CentroidX")))
        feature.SetField("CentroidY", float(current_patch.get_attribute("CentroidY")))

        if map_attr.get_attribute("HasOSLINK"):
            feature.SetField("GSD_Dist", float(current_patch.get_attribute("GSD_Dist")))
            feature.SetField("GSD_Loc", str(current_patch.get_attribute("GSD_Loc")))
            feature.SetField("GSD_Deg", int(current_patch.get_attribute("GSD_Deg")))
            feature.SetField("GSD_ACon", float(current_patch.get_attribute("GSD_ACon")))

        if map_attr.get_attribute("HasOSNET"):
            feature.SetField("OSNet_Deg", int(current_patch.get_attribute("OSNet_Deg")))
            feature.SetField("OSNet_MinD", float(current_patch.get_attribute("OSNet_MinD")))

        # if map_attr.get_attribute("HasELEV"):
        #     feature.SetField("Elevation", float(current_patch.get_attribute("Elevation")))

        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True