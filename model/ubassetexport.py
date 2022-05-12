r"""
@file   ubassetexport.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2017-2022  Peter M. Bach

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
__copyright__ = "Copyright 2017-2022. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
import osgeo.osr as osr
import osgeo.ogr as ogr
import os


# --- FUNCTION DEFINITIONS ---
def export_to_shapefile(asset_col, metadata, filepath, filename, epsg, asset_type, geom_type):
    """Exports any UBVector to Shapefile format, identifies whether it is Point, Line or Polygon and creates the file
    with all attributes currently in the list.
    """
    if len(asset_col) == 0:
        return
    xmin = metadata.get_attribute("xllcorner")
    ymin = metadata.get_attribute("yllcorner")
    print(xmin, ymin)

    fullname = filepath + "/" + filename
    print(fullname)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(epsg)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    usefilename = fullname
    fileduplicate_counter = 0
    while os.path.exists(str(usefilename)+"_"+asset_type+".shp"):
        fileduplicate_counter += 1
        usefilename = fullname + "(" + str(fileduplicate_counter) + ")"

    shapefile = driver.CreateDataSource(str(usefilename)+"_"+asset_type+".shp")
    if geom_type == "POLYGON":
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPolygon)
    elif geom_type == "LINE":
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbLineString)
    else:   # POINT
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPoint)

    defn = layer.GetLayerDefn()
    attlist = asset_col[0].get_all_attributes()
    for att in attlist.keys():
        print("Attribute: ", att)
        if isinstance(attlist[att], int):
            layer.CreateField(ogr.FieldDefn(att, ogr.OFTInteger))
        elif isinstance(attlist[att], float):
            layer.CreateField(ogr.FieldDefn(att, ogr.OFTReal))
        else:
            layer.CreateField(ogr.FieldDefn(att, ogr.OFTString))
        defn = layer.GetLayerDefn()

    for i in range(len(asset_col)):
        current_asset = asset_col[i]
        if current_asset.get_attribute("Status") == 0:
            continue

        # Draw Geometry
        if geom_type == "POLYGON":
            feat_geom = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)
            nl = current_asset.get_points()
            for point in nl:
                ring.AddPoint(point[0]+xmin, point[1]+ymin)
            feat_geom.AddGeometry(ring)

        elif geom_type == "LINE":
            nl = current_asset.get_points()
            feat_geom = ogr.Geometry(ogr.wkbLineString)
            feat_geom.AddPoint(nl[0][0] + xmin, nl[0][1] + ymin)
            feat_geom.AddPoint(nl[1][0] + xmin, nl[1][1] + ymin)

        else:   #geom_type == "POINT":
            nl = current_asset.get_points()
            feat_geom = ogr.Geometry(ogr.wkbPoint)
            feat_geom.AddPoint(nl[0] + xmin, nl[1] + ymin)

        # Add the feature to the shapefile
        feature = ogr.Feature(defn)
        feature.SetGeometry(feat_geom)
        feature.SetFID(0)
        attlist = current_asset.get_all_attributes()
        for att in attlist.keys():
            feature.SetField(att, current_asset.get_attribute(att))

        layer.CreateFeature(feature)
    shapefile.Destroy()
    return True


def export_to_raster_geotiff():
    pass


def export_to_raster_ascii():
    pass


def export_data_to_csv():
    pass


def export_data_to_netcdf():
    pass
