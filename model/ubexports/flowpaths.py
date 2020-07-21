r"""
@file   model\ubexports\flowpaths.py
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


def export_flowpaths_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all flowpaths in the asset_col list to a GIS Shapefile based on the current filepath.

    :param asset_col: [] list containing all UBVector() Flowpath objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :param fptype: type of Flowpath ("Blocks", "Patches")
    :return:
    """
    idtype = map_attr.get_attribute("idtype")
    if map_attr.get_attribute("HasFLOWPATHS") != 1:
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
    fielddefmatrix.append(ogr.FieldDefn("FlowID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn(idtype, ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("DownID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Z_up", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Z_down", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("max_zdrop", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("LinkType", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("AvgSlope", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("h_pond", ogr.OFTReal))

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

        feature.SetField("FlowID", int(current_path.get_attribute("FlowID")))
        feature.SetField(idtype, int(current_path.get_attribute(idtype)))
        feature.SetField("DownID", int(current_path.get_attribute("DownID")))
        feature.SetField("Z_up", float(current_path.get_attribute("Z_up")))
        feature.SetField("Z_down", float(current_path.get_attribute("Z_down")))
        feature.SetField("max_zdrop", float(current_path.get_attribute("max_zdrop")))
        feature.SetField("LinkType", str(current_path.get_attribute("LinkType")))
        feature.SetField("AvgSlope", float(current_path.get_attribute("AvgSlope")))
        feature.SetField("h_pond", float(current_path.get_attribute("h_pond")))
        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True
