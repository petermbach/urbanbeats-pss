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


def export_urbandev_cells_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all the assets in 'asset_col' to a GIS Shapefile based on the current filepath.

    :param asset_col: a list containing all assets to be exported to a shapefile
    :param map_attr: the global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    """
    xmin = map_attr.get_attribute("xllcorner")
    ymin = map_attr.get_attribute("yllcorner")

    fullname = filepath + "/" + filename

    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    usefilename = fullname  # A placeholder filename
    fileduplicate_counter = 0  # Tracks the number of duplicates
    while os.path.exists(str(usefilename + ".shp")):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"
    shapefile = driver.CreateDataSource(str(usefilename) + ".shp")

    layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPolygon)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("CellID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("CentreX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentreY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Region", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Active", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Base_LUC", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Base_POP", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Base_EMP", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("LUC_Type", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("NHD_N", ogr.OFTInteger))
    # fielddefmatrix.append(ogr.FieldDefn("NHD_IDs", ogr.OFTString))

    # Create the fields
    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    # Get Cell Data
    for i in range(len(asset_col)):
        currentAttList = asset_col[i]
        if currentAttList.get_attribute("Status") == 0:
            continue

        # Draw Geometry
        line = ogr.Geometry(ogr.wkbPolygon)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        nl = currentAttList.get_points()
        for point in nl:
            ring.AddPoint(point[0] + xmin, point[1] + ymin)
        line.AddGeometry(ring)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        # Add Attributes
        feature.SetField("CellID", int(currentAttList.get_attribute("CellID")))
        feature.SetField("CentreX", float(currentAttList.get_attribute("CentreX")))
        feature.SetField("CentreY", float(currentAttList.get_attribute("CentreY")))
        feature.SetField("Region", str(currentAttList.get_attribute("Region")))
        feature.SetField("Active", str(currentAttList.get_attribute("Active")))
        feature.SetField("Base_LUC", str(currentAttList.get_attribute("Base_LUC")))
        feature.SetField("Base_POP", int(currentAttList.get_attribute("Base_POP")))
        feature.SetField("Base_EMP", int(currentAttList.get_attribute("Base_EMP")))
        feature.SetField("LUC_Type", str(currentAttList.get_attribute("LUC_Type")))
        feature.SetField("NHD_N", str(currentAttList.get_attribute("NHD_N")))
        # feature.SetField("NHD_IDs", str(",".join(map(str, currentAttList.get_attribute("NHD_IDs")))))
        # Neighbourhood attribute converts the [ ] array of BlockIDs to a comma-separated list "#,#,#,#"
        layer.CreateFeature(feature)

    shapefile.Destroy()
    return True