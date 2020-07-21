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
from ..progref import ubglobals

def export_dirichletnetwork_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """ Exports the full dirichlet network among VectorPatches to GIS Shapefile based on current filepath.

    :param asset_col: [] list containing all UBVector Link objects
    :param map_attr: global map attributes to track relevant information
    :param filepath: active filepath to export assets to
    :param filename: name of file to export (without the .shp extension)
    :param epsg: the EPSG code for the coordinate system to use
    :return:
    """
    if map_attr.get_attribute("HasDIRICHLET_NET") != 1:
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
    fielddefmatrix.append(ogr.FieldDefn("LinkID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NodeA", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("NodeB", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Distance", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("EdgeWidth", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Traversal", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_link = asset_col[i]
        linepoints = current_link.get_points()
        line = ogr.Geometry(ogr.wkbLineString)
        p1 = linepoints[0]
        p2 = linepoints[1]
        line.AddPoint(p1[0] + xmin, p1[1] + ymin)
        line.AddPoint(p2[0] + xmin, p2[1] + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        feature.SetField("LinkID", int(current_link.get_attribute("LinkID")))
        feature.SetField("NodeA", int(current_link.get_attribute("NodeA")))
        feature.SetField("NodeB", int(current_link.get_attribute("NodeB")))
        feature.SetField("Distance", float(current_link.get_attribute("Distance")))
        feature.SetField("EdgeWidth", float(current_link.get_attribute("EdgeWidth")))
        feature.SetField("Traversal", float(current_link.get_attribute("Traversal")))
        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True


def export_vectorpatches_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all the vector patches in the asset_col list to a GIS Shapefile based on current filepath. Also exports
    the centroids to a point shapefile.

    :param asset_col: [] list containing all UBVector patch objects
    :param map_attr: global map attributes to track any relevant information
    :param filepath: the active filepath to export these assets to
    :param filename: name of the file to export (without the 'shp' extension)
    :param epsg: the EPSG code for the coordinate system to use
    :return:
    """
    if map_attr.get_attribute("GeometryType") != "VECTORPATCH" or map_attr.get_attribute("HasLUC") != 1:
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
    fielddefmatrix.append(ogr.FieldDefn("Area", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("LandUse", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("CentreX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentreY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("OriginX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("OriginY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Neighbours", ogr.OFTString))

    if map_attr.get_attribute("HasPOP"):
        fielddefmatrix.append(ogr.FieldDefn("Population", ogr.OFTInteger))

    if map_attr.get_attribute("HasELEV"):
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MinElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MaxElev", ogr.OFTReal))

    if map_attr.get_attribute("HasGEOPOLITICAL"):  # IF A GEOPOLITICAL MAP WAS INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("Region", ogr.OFTString))

    if map_attr.get_attribute("HasSUBURBS"):  # IF SUBURBS WERE INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("Suburb", ogr.OFTString))

    if map_attr.get_attribute("HasPLANZONES"):  # IF PLANNING ZONES WERE INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("PlanZone", ogr.OFTString))

    if map_attr.get_attribute("HasRIVERS"):         # IF A RIVERS MAP WAS LOADED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("HasRiver", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("RiverNames", ogr.OFTString))

    if map_attr.get_attribute("HasLAKES"):          # IF A LAKES MAP WAS LOADED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("HasLake", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("LakeNames", ogr.OFTString))



    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_patch = asset_col[i]
        if current_patch.get_attribute("Status") == 0:
            continue

        line = ogr.Geometry(ogr.wkbPolygon)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        nl = current_patch.get_points()
        for point in nl:
            ring.AddPoint(point[0] + xmin, point[1] + ymin)
        line.AddGeometry(ring)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        feature.SetField("PatchID", int(current_patch.get_attribute("PatchID")))
        feature.SetField("BlockID", int(current_patch.get_attribute("BlockID")))
        feature.SetField("Area", float(current_patch.get_attribute("Area")))
        feature.SetField("LandUse", str(current_patch.get_attribute("LandUse")))
        feature.SetField("CentreX", float(current_patch.get_attribute("CentreX")))
        feature.SetField("CentreY", float(current_patch.get_attribute("CentreY")))
        feature.SetField("OriginX", float(current_patch.get_attribute("OriginX")))
        feature.SetField("OriginY", float(current_patch.get_attribute("OriginY")))

        if map_attr.get_attribute("HasPOP"):
            feature.SetField("Population", int(current_patch.get_attribute("Population")))

        if map_attr.get_attribute("HasELEV"):
            feature.SetField("AvgElev", float(current_patch.get_attribute("AvgElev")))
            feature.SetField("MinElev", float(current_patch.get_attribute("MinElev")))
            feature.SetField("MaxElev", float(current_patch.get_attribute("MaxElev")))

        if map_attr.get_attribute("HasGEOPOLITICAL"):
            feature.SetField("Region", str(current_patch.get_attribute("Region")))

        if map_attr.get_attribute("HasSUBURBS"):
            feature.SetField("Suburb", str(current_patch.get_attribute("Suburb")))

        if map_attr.get_attribute("HasPLANZONES"):
            feature.SetField("PlanZone", str(current_patch.get_attribute("PlanZone")))

        if map_attr.get_attribute("HasRIVERS"):
            feature.SetField("HasRiver", int(current_patch.get_attribute("HasRiver")))
            feature.SetField("RiverNames", str(",".join(map(str, current_patch.get_attribute("RiverNames")))))

        if map_attr.get_attribute("HasLAKES"):
            feature.SetField("HasLake", int(current_patch.get_attribute("HasLake")))
            feature.SetField("LakeNames", str(",".join(map(str, current_patch.get_attribute("LakeNames")))))

        feature.SetField("Neighbours", str(",".join(map(str, current_patch.get_attribute("Neighbours")))))

        layer.CreateFeature(feature)
    shapefile.Destroy()

    # Export Representative Points
    driver = ogr.GetDriverByName('ESRI Shapefile')
    usefilename = fullname+"_Centroids"
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename+".shp")):
        fileduplicate_counter += 1
        usefilename = fullname+"_Centroids" + "(" + str(fileduplicate_counter)+ ")"
    shapefile = driver.CreateDataSource(str(usefilename)+".shp")

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbPoint)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("PatchID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Area", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("LandUse", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("CentreX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentreY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("RepX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("RepY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Neighbours", ogr.OFTString))

    if map_attr.get_attribute("HasPOP"):
        fielddefmatrix.append(ogr.FieldDefn("Population", ogr.OFTInteger))

    if map_attr.get_attribute("HasELEV"):
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MinElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MaxElev", ogr.OFTReal))

    if map_attr.get_attribute("HasGEOPOLITICAL"):  # IF A GEOPOLITICAL MAP WAS INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("Region", ogr.OFTString))

    if map_attr.get_attribute("HasSUBURBS"):  # IF SUBURBS WERE INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("Suburb", ogr.OFTString))

    if map_attr.get_attribute("HasPLANZONES"):  # IF PLANNING ZONES WERE INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("PlanZone", ogr.OFTString))

    if map_attr.get_attribute("HasRIVERS"):         # IF A RIVERS MAP WAS LOADED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("HasRiver", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("RiverNames", ogr.OFTString))

    if map_attr.get_attribute("HasLAKES"):          # IF A LAKES MAP WAS LOADED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("HasLake", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("LakeNames", ogr.OFTString))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_patch = asset_col[i]
        if current_patch.get_attribute("Status") == 0:
            continue

        centroid = ogr.Geometry(ogr.wkbPoint)
        centroid.AddPoint(current_patch.get_attribute("RepX") + xmin, current_patch.get_attribute("RepY") + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(centroid)
        feature.SetFID(0)

        feature.SetField("PatchID", int(current_patch.get_attribute("PatchID")))
        feature.SetField("BlockID", int(current_patch.get_attribute("BlockID")))
        feature.SetField("Area", float(current_patch.get_attribute("Area")))
        feature.SetField("LandUse", str(current_patch.get_attribute("LandUse")))
        feature.SetField("CentreX", float(current_patch.get_attribute("CentreX")))
        feature.SetField("CentreY", float(current_patch.get_attribute("CentreY")))
        feature.SetField("RepX", float(current_patch.get_attribute("RepX")))
        feature.SetField("RepY", float(current_patch.get_attribute("RepY")))

        if map_attr.get_attribute("HasPOP"):
            feature.SetField("Population", int(current_patch.get_attribute("Population")))

        if map_attr.get_attribute("HasELEV"):
            feature.SetField("AvgElev", float(current_patch.get_attribute("AvgElev")))
            feature.SetField("MinElev", float(current_patch.get_attribute("MinElev")))
            feature.SetField("MaxElev", float(current_patch.get_attribute("MaxElev")))

        if map_attr.get_attribute("HasGEOPOLITICAL"):
            feature.SetField("Region", str(current_patch.get_attribute("Region")))

        if map_attr.get_attribute("HasSUBURBS"):
            feature.SetField("Suburb", str(current_patch.get_attribute("Suburb")))

        if map_attr.get_attribute("HasPLANZONES"):
            feature.SetField("PlanZone", str(current_patch.get_attribute("PlanZone")))

        feature.SetField("Neighbours", str(",".join(map(str, current_patch.get_attribute("Neighbours")))))

        layer.CreateFeature(feature)

    shapefile.Destroy()


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
    fielddefmatrix.append(ogr.FieldDefn("PatchName", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Landuse", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("AspRatio", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("PatchSize", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("PatchArea", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("BuffRadius", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentroidX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentroidY", ogr.OFTReal))

    if map_attr.get_attribute("HasPOP"):
        fielddefmatrix.append(ogr.FieldDefn("Population", ogr.OFTReal))

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

    if map_attr.get_attribute("HasPATCHFLOW"):
        fielddefmatrix.append(ogr.FieldDefn("downPatch", ogr.OFTString))
        fielddefmatrix.append(ogr.FieldDefn("downDist", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("down_dz", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_patch = asset_col[i]
        if current_patch.get_attribute("Status") == 0:
            continue

        patchpoint = current_patch.get_points()
        centroid = ogr.Geometry(ogr.wkbPoint)
        centroid.AddPoint(patchpoint[0] + xmin, patchpoint[1] + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(centroid)
        feature.SetFID(0)

        feature.SetField("PatchID", int(current_patch.get_attribute("PatchID")))
        feature.SetField("BlockID", int(current_patch.get_attribute("BlockID")))
        feature.SetField("PatchName", str(current_patch.get_attribute("PatchName")))
        feature.SetField("Landuse", ubglobals.LANDUSENAMES[int(current_patch.get_attribute("Landuse"))-1])
        feature.SetField("AspRatio", float(current_patch.get_attribute("AspRatio")))
        feature.SetField("PatchSize", int(current_patch.get_attribute("PatchSize")))
        feature.SetField("PatchArea", float(current_patch.get_attribute("PatchArea")))
        feature.SetField("BuffRadius", float(current_patch.get_attribute("BuffRadius")))
        feature.SetField("CentroidX", float(current_patch.get_attribute("CentroidX")))
        feature.SetField("CentroidY", float(current_patch.get_attribute("CentroidY")))
        if map_attr.get_attribute("HasPOP"):
            feature.SetField("Population", float(current_patch.get_attribute("Population")))

        if map_attr.get_attribute("HasOSLINK"):
            feature.SetField("GSD_Dist", float(current_patch.get_attribute("GSD_Dist")))
            feature.SetField("GSD_Loc", str(current_patch.get_attribute("GSD_Loc")))
            feature.SetField("GSD_Deg", int(current_patch.get_attribute("GSD_Deg")))
            feature.SetField("GSD_ACon", float(current_patch.get_attribute("GSD_ACon")))

        if map_attr.get_attribute("HasOSNET"):
            feature.SetField("OSNet_Deg", int(current_patch.get_attribute("OSNet_Deg")))
            feature.SetField("OSNet_MinD", float(current_patch.get_attribute("OSNet_MinD")))

        if map_attr.get_attribute("HasELEV"):
            feature.SetField("Elevation", float(current_patch.get_attribute("Elevation")))

        if map_attr.get_attribute("HasPATCHFLOW"):
            feature.SetField("downPatch", str(current_patch.get_attribute("downPatch")))
            feature.SetField("downDist", float(current_patch.get_attribute("downDist")))
            feature.SetField("down_dz", float(current_patch.get_attribute("down_dz")))

        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True


def export_patch_flowpaths_to_gis_shapefile(asset_col, map_attr, filepath, filename, epsg):
    """Exports all the flowpaths between patches the asset_col list to a GIS Shapefile based on
    the current filepath.

    :param asset_col: [] list containing all UBVector PatchFloID objects
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

    layer = shapefile.CreateLayer('layer1', spatial_ref, ogr.wkbLineString)
    layerDefinition = layer.GetLayerDefn()

    fielddefmatrix = []
    fielddefmatrix.append(ogr.FieldDefn("PatchFloID", ogr.OFTInteger))
    fielddefmatrix.append(ogr.FieldDefn("Upstream", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Downstream", ogr.OFTString))
    fielddefmatrix.append(ogr.FieldDefn("Distance", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("dZ", ogr.OFTReal))

    for field in fielddefmatrix:
        layer.CreateField(field)
        layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_patchflow = asset_col[i]
        linepoints = current_patchflow.get_points()
        line = ogr.Geometry(ogr.wkbLineString)
        p1 = linepoints[0]
        p2 = linepoints[1]
        line.AddPoint(p1[0] + xmin, p1[1] + ymin)
        line.AddPoint(p2[0] + xmin, p2[1] + ymin)

        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(line)
        feature.SetFID(0)

        feature.SetField("PatchFloID", int(current_patchflow.get_attribute("PatchFloID")))
        feature.SetField("Upstream", str(current_patchflow.get_attribute("Upstream")))
        feature.SetField("Downstream", str(current_patchflow.get_attribute("Downstream")))
        feature.SetField("Distance", float(current_patchflow.get_attribute("Distance")))
        feature.SetField("dZ", int(current_patchflow.get_attribute("dZ")))

        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True