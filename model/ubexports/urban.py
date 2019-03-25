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
    # fielddefmatrix.append(ogr.FieldDefn("NHD_Num", ogr.OFTInteger))

    # ACCESSIBILIY INDICATORS
    fielddefmatrix.append(ogr.FieldDefn("DIST_ROAD", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_ROAD_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_ROAD_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_ROAD_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_ROAD_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("DIST_RAIL", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_RAIL_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_RAIL_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_RAIL_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_RAIL_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("DIST_WWAY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_WWAY_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_WWAY_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_WWAY_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_WWAY_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("DIST_LAKE", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_LAKE_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_LAKE_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_LAKE_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_LAKE_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("DIST_POSS", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POSS_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POSS_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POSS_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POSS_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("DIST_POIS", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POIS_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POIS_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POIS_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_POIS_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("DIST_PTHS", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_PTHS_R", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_PTHS_C", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_PTHS_I", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACC_PTHS_O", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("ACCESS_RES", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACCESS_COM", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACCESS_IND", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("ACCESS_ORC", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("ZONE_RES", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("ZONE_COM", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("ZONE_IND", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("ZONE_ORC", ogr.OFTInteger))

    fielddefmatrix.append(ogr.FieldDefn("NHD_N", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_NE", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_E", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_SE", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_S", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_SW", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_W", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHD_NW", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NHAdjacent", ogr.OFTString))

    fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("SoilClass", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("DepthToGW", ogr.OFTReal))

    fielddefmatrix.append(ogr.FieldDefn("SUIT_SLOPE", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Elevation", ogr.OFTReal))

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
        # feature.SetField("NHD_Num", int(currentAttList.get_attribute("NHD_Num")))

        feature.SetField("DIST_ROAD", float(currentAttList.get_attribute("ACC_ROAD_DIST")))
        feature.SetField("ACC_ROAD_R", float(currentAttList.get_attribute("ACC_ROAD_RES")))
        feature.SetField("ACC_ROAD_C", float(currentAttList.get_attribute("ACC_ROAD_COM")))
        feature.SetField("ACC_ROAD_I", float(currentAttList.get_attribute("ACC_ROAD_IND")))
        feature.SetField("ACC_ROAD_O", float(currentAttList.get_attribute("ACC_ROAD_ORC")))

        feature.SetField("DIST_RAIL", float(currentAttList.get_attribute("ACC_RAIL_DIST")))
        feature.SetField("ACC_RAIL_R", float(currentAttList.get_attribute("ACC_RAIL_RES")))
        feature.SetField("ACC_RAIL_C", float(currentAttList.get_attribute("ACC_RAIL_COM")))
        feature.SetField("ACC_RAIL_I", float(currentAttList.get_attribute("ACC_RAIL_IND")))
        feature.SetField("ACC_RAIL_O", float(currentAttList.get_attribute("ACC_RAIL_ORC")))

        feature.SetField("DIST_WWAY", float(currentAttList.get_attribute("ACC_WWAY_DIST")))
        feature.SetField("ACC_WWAY_R", float(currentAttList.get_attribute("ACC_WWAY_RES")))
        feature.SetField("ACC_WWAY_C", float(currentAttList.get_attribute("ACC_WWAY_COM")))
        feature.SetField("ACC_WWAY_I", float(currentAttList.get_attribute("ACC_WWAY_IND")))
        feature.SetField("ACC_WWAY_O", float(currentAttList.get_attribute("ACC_WWAY_ORC")))

        feature.SetField("DIST_LAKE", float(currentAttList.get_attribute("ACC_LAKE_DIST")))
        feature.SetField("ACC_LAKE_R", float(currentAttList.get_attribute("ACC_LAKE_RES")))
        feature.SetField("ACC_LAKE_C", float(currentAttList.get_attribute("ACC_LAKE_COM")))
        feature.SetField("ACC_LAKE_I", float(currentAttList.get_attribute("ACC_LAKE_IND")))
        feature.SetField("ACC_LAKE_O", float(currentAttList.get_attribute("ACC_LAKE_ORC")))

        feature.SetField("DIST_POSS", float(currentAttList.get_attribute("ACC_POSS_DIST")))
        feature.SetField("ACC_POSS_R", float(currentAttList.get_attribute("ACC_POSS_RES")))
        feature.SetField("ACC_POSS_C", float(currentAttList.get_attribute("ACC_POSS_COM")))
        feature.SetField("ACC_POSS_I", float(currentAttList.get_attribute("ACC_POSS_IND")))
        feature.SetField("ACC_POSS_O", float(currentAttList.get_attribute("ACC_POSS_ORC")))

        feature.SetField("DIST_POIS", float(currentAttList.get_attribute("ACC_POIS_DIST")))
        feature.SetField("ACC_POIS_R", float(currentAttList.get_attribute("ACC_POIS_RES")))
        feature.SetField("ACC_POIS_C", float(currentAttList.get_attribute("ACC_POIS_COM")))
        feature.SetField("ACC_POIS_I", float(currentAttList.get_attribute("ACC_POIS_IND")))
        feature.SetField("ACC_POIS_O", float(currentAttList.get_attribute("ACC_POIS_ORC")))

        feature.SetField("DIST_PTHS", float(currentAttList.get_attribute("ACC_PTHS_DIST")))
        feature.SetField("ACC_PTHS_R", float(currentAttList.get_attribute("ACC_PTHS_RES")))
        feature.SetField("ACC_PTHS_C", float(currentAttList.get_attribute("ACC_PTHS_COM")))
        feature.SetField("ACC_PTHS_I", float(currentAttList.get_attribute("ACC_PTHS_IND")))
        feature.SetField("ACC_PTHS_O", float(currentAttList.get_attribute("ACC_PTHS_ORC")))

        feature.SetField("ACCESS_RES", float(currentAttList.get_attribute("ACCESS_RES")))
        feature.SetField("ACCESS_COM", float(currentAttList.get_attribute("ACCESS_COM")))
        feature.SetField("ACCESS_IND", float(currentAttList.get_attribute("ACCESS_IND")))
        feature.SetField("ACCESS_ORC", float(currentAttList.get_attribute("ACCESS_ORC")))

        feature.SetField("ZONE_RES", int(currentAttList.get_attribute("ZONE_RES")))
        feature.SetField("ZONE_COM", int(currentAttList.get_attribute("ZONE_COM")))
        feature.SetField("ZONE_IND", int(currentAttList.get_attribute("ZONE_IND")))
        feature.SetField("ZONE_ORC", int(currentAttList.get_attribute("ZONE_ORC")))

        feature.SetField("NHD_N", int(currentAttList.get_attribute("NHD_N")))
        feature.SetField("NHD_NE", int(currentAttList.get_attribute("NHD_NE")))
        feature.SetField("NHD_E", int(currentAttList.get_attribute("NHD_E")))
        feature.SetField("NHD_SE", int(currentAttList.get_attribute("NHD_SE")))
        feature.SetField("NHD_S", int(currentAttList.get_attribute("NHD_S")))
        feature.SetField("NHD_SW", int(currentAttList.get_attribute("NHD_SW")))
        feature.SetField("NHD_W", int(currentAttList.get_attribute("NHD_W")))
        feature.SetField("NHD_NW", int(currentAttList.get_attribute("NHD_NW")))
        # feature.SetField("NHAdjacent", str(",".join(map(str, currentAttList.get_attribute("NHAdjacent")))))
        # Neighbourhood attribute converts the [ ] array of BlockIDs to a comma-separated list "#,#,#,#"

        feature.SetField("Elevation", float(currentAttList.get_attribute("Elevation")))
        feature.SetField("SoilClass", str(currentAttList.get_attribute("SoilClass")))
        feature.SetField("DepthToGW", float(currentAttList.get_attribute("DepthToGW")))

        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True