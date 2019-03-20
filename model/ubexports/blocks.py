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

    if map_attr.get_attribute("HasELEV"):       # IF AN ELEVATION MAP WAS INCLUDED
        fielddefmatrix.append(ogr.FieldDefn("BasinID", ogr.OFTInteger))

    fielddefmatrix.append(ogr.FieldDefn("CentreX", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("CentreY", ogr.OFTReal))
    fielddefmatrix.append(ogr.FieldDefn("Neighbours", ogr.OFTString))

    if map_attr.get_attribute("HasLUC"):        # IF A LAND USE MAP WAS LOADED
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
        fielddefmatrix.append(ogr.FieldDefn("pLU_WAT", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_FOR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_AGR", ogr.OFTReal))

        if map_attr.get_attribute("HasSPATIALMETRICS"):     # IF SPATIAL METRICS WERE CALCULATED
            fielddefmatrix.append(ogr.FieldDefn("Rich", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ShDiv", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ShDom", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ShEven", ogr.OFTReal))

    if map_attr.get_attribute("HasPOP"):        # IF POPULATION DATA WAS LOADED
        fielddefmatrix.append(ogr.FieldDefn("Population", ogr.OFTReal))

    if map_attr.get_attribute("HasELEV"):       # IF ELEVATION AND FLOWPATH DELINEATION WAS CONDUCTED
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MaxElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MinElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("downID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("max_dz", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avg_slope", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("h_pond", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Outlet", ogr.OFTInteger))

    if map_attr.get_attribute("HasGEOPOLITICAL"):   # IF A GEOPOLITICAL MAP WAS INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("Region", ogr.OFTString))

    if map_attr.get_attribute("HasSUBURBS"):        # IF SUBURBS WERE INCLUDED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("Suburb", ogr.OFTString))

    if map_attr.get_attribute("HasRIVERS"):         # IF A RIVERS MAP WAS LOADED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("HasRiver", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("RiverNames", ogr.OFTString))

    if map_attr.get_attribute("HasLAKES"):          # IF A LAKES MAP WAS LOADED IN THE SIMULATION
        fielddefmatrix.append(ogr.FieldDefn("HasLake", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("LakeNames", ogr.OFTString))

    if map_attr.get_attribute("HasURBANFORM"):      # IF URBAN PLANNING MODULE HAS BEEN EXECUTED
        fielddefmatrix.append(ogr.FieldDefn("MiscAtot", ogr.OFTReal))    # Unclassified Areas
        fielddefmatrix.append(ogr.FieldDefn("MiscAimp", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("MiscThresh", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("UND_Type", ogr.OFTString))    # Undeveloped Land
        fielddefmatrix.append(ogr.FieldDefn("UND_av", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("OpenSpace", ogr.OFTReal))   # Parks/Gardens and Reserves
        fielddefmatrix.append(ogr.FieldDefn("AGreenOS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ASquare", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("PG_av", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("REF_av", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("ANonW_Util", ogr.OFTReal))  # Services & Utilities
        fielddefmatrix.append(ogr.FieldDefn("SVU_avWS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avWW", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avSW", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avOTH", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("RoadTIA", ogr.OFTReal))     # Roads & Highways
        fielddefmatrix.append(ogr.FieldDefn("ParkBuffer", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("RD_av", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("HouseOccup", ogr.OFTReal))     # Residential
        fielddefmatrix.append(ogr.FieldDefn("ResParcels", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("ResFrontT", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avSt_RES", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WResNstrip", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResAllots", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("ResDWpLot", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("ResHouses", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("ResLotArea", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResRoof", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_RES", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResHFloors", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("ResLotTIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResLotEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResGarden", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResRoofCon", ogr.OFTString))
        fielddefmatrix.append(ogr.FieldDefn("ResLotALS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResLotARS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRFlats", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("HDRRoofA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDROccup", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDR_TIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDR_EIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRFloors", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("av_HDRes", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRGarden", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRCarPark", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("LIjobs", ogr.OFTInteger))      # Light Industry
        fielddefmatrix.append(ogr.FieldDefn("LIestates", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("avSt_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIFloors", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("LIAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeTIA", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("HIjobs", ogr.OFTInteger))      # Heavy Industry
        fielddefmatrix.append(ogr.FieldDefn("HIestates", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("avSt_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIFloors", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("HIAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeTIA", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("COMjobs", ogr.OFTInteger))  # Commercial
        fielddefmatrix.append(ogr.FieldDefn("COMestates", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("avSt_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMFloors", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("COMAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeTIA", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("ORCjobs", ogr.OFTInteger))  # Offices
        fielddefmatrix.append(ogr.FieldDefn("ORCestates", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("avSt_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCFloors", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeTIA", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("Blk_TIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_EIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_EIF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_TIF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_RoofsA", ogr.OFTReal))

    if map_attr.get_attribute("HasLANDCOVER"):
        fielddefmatrix.append(ogr.FieldDefn("LC_RES_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RES_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RES_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RES_AS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RES_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RES_RF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_COM_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_COM_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_COM_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_COM_AS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_COM_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_COM_RF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_LI_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_LI_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_LI_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_LI_AS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_LI_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_LI_RF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_HI_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_HI_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_HI_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_HI_AS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_HI_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_HI_RF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_ORC_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_ORC_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_ORC_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_ORC_AS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_ORC_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_ORC_RF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_NA_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_NA_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_NA_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_UND_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_UND_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_SVU_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_PG_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_PG_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_PG_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_PG_AS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_PG_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_REF_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_REF_IG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RD_DG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RD_CO", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LC_RD_AS", ogr.OFTReal))

    if map_attr.get_attribute("HasWATERUSE"):
        if map_attr.get_attribute("WD_RES_Method") == "EUA":
            fielddefmatrix.append(ogr.FieldDefn("WD_HHKitch", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHShow", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHToil", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHLaund", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHDish", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHIn", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHHot", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("HH_GreyW", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("HH_BlackW", ogr.OFTReal))
        else:
            fielddefmatrix.append(ogr.FieldDefn("WD_HHIn", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHHot", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WD_HHNonPo", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("HH_GreyW", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("HH_BlackW", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("WD_In", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_Out", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_Hot", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WW_ResG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WW_ResB", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("WD_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_HotCOM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_Office", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_HotOff", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_HotLI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_HotHI", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("WD_NRes", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_HotNRes", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_NResIrr", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WW_ComG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WW_ComB", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WW_IndG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WW_IndB", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WD_POSIrr", ogr.OFTReal))

        fielddefmatrix.append(ogr.FieldDefn("Blk_WD", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WDIrr", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WDHot", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WW", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WWG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WWB", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_Loss", ogr.OFTReal))

    if map_attr.get_attribute("HasINFRA"):
        if map_attr.get_attribute("HasSWW"):
            fielddefmatrix.append(ogr.FieldDefn("HasSWW", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("HasWWTP", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("HasCarved", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("Sww_DownID", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ModAvgElev", ogr.OFTReal))

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

        if map_attr.get_attribute("HasELEV"):
            feature.SetField("BasinID", int(currentAttList.get_attribute("BasinID")))

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
            feature.SetField("pLU_WAT", float(currentAttList.get_attribute("pLU_WAT")))
            feature.SetField("pLU_FOR", float(currentAttList.get_attribute("pLU_FOR")))
            feature.SetField("pLU_AGR", float(currentAttList.get_attribute("pLU_AGR")))

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
            feature.SetField("downID", int(currentAttList.get_attribute("downID")))
            feature.SetField("max_dz", float(currentAttList.get_attribute("max_dz")))
            feature.SetField("avg_slope", float(currentAttList.get_attribute("avg_slope")))
            feature.SetField("h_pond", float(currentAttList.get_attribute("h_pond")))
            feature.SetField("Outlet", int(currentAttList.get_attribute("Outlet")))

        if map_attr.get_attribute("HasGEOPOLITICAL"):
            feature.SetField("Region", str(currentAttList.get_attribute("Region")))

        if map_attr.get_attribute("HasSUBURBS"):
            feature.SetField("Suburb", str(currentAttList.get_attribute("Suburb")))

        if map_attr.get_attribute("HasRIVERS"):
            feature.SetField("HasRiver", int(currentAttList.get_attribute("HasRiver")))
            feature.SetField("RiverNames", str(",".join(map(str, currentAttList.get_attribute("RiverNames")))))

        if map_attr.get_attribute("HasLAKES"):
            feature.SetField("HasLake", int(currentAttList.get_attribute("HasLake")))
            feature.SetField("LakeNames", str(",".join(map(str, currentAttList.get_attribute("LakeNames")))))

        if map_attr.get_attribute("HasURBANFORM"):
            feature.SetField("MiscAtot", float(currentAttList.get_attribute("MiscAtot")))       # Unclassified
            feature.SetField("MiscAimp", float(currentAttList.get_attribute("MiscAimp")))
            feature.SetField("MiscThresh", float(currentAttList.get_attribute("MiscThresh")))

            feature.SetField("UND_Type", str(currentAttList.get_attribute("UND_Type")))         # Undeveloped
            feature.SetField("UND_av", float(currentAttList.get_attribute("UND_av")))

            feature.SetField("OpenSpace", float(currentAttList.get_attribute("OpenSpace")))     # Open Spaces
            feature.SetField("AGreenOS", float(currentAttList.get_attribute("AGreenOS")))
            feature.SetField("ASquare", float(currentAttList.get_attribute("ASquare")))
            feature.SetField("PG_av", float(currentAttList.get_attribute("PG_av")))
            feature.SetField("REF_av", float(currentAttList.get_attribute("REF_av")))

            feature.SetField("ANonW_Util", float(currentAttList.get_attribute("ANonW_Util")))   # Service & Utility
            feature.SetField("SVU_avWS", float(currentAttList.get_attribute("SVU_avWS")))
            feature.SetField("SVU_avWW", float(currentAttList.get_attribute("SVU_avWW")))
            feature.SetField("SVU_avSW", float(currentAttList.get_attribute("SVU_avSW")))
            feature.SetField("SVU_avOTH", float(currentAttList.get_attribute("SVU_avOTH")))

            feature.SetField("RoadTIA", float(currentAttList.get_attribute("RoadTIA")))         # Roads
            feature.SetField("ParkBuffer", int(currentAttList.get_attribute("ParkBuffer")))
            feature.SetField("RD_av", float(currentAttList.get_attribute("RD_av")))

            if currentAttList.get_attribute("HasHouses"):
                feature.SetField("HouseOccup", float(currentAttList.get_attribute("HouseOccup")))   # Residential
                feature.SetField("ResParcels", int(currentAttList.get_attribute("ResParcels")))
                feature.SetField("ResFrontT", float(currentAttList.get_attribute("ResFrontT")))
                feature.SetField("WResNstrip", float(currentAttList.get_attribute("WResNstrip")))
                feature.SetField("avLt_RES", float(currentAttList.get_attribute("avSt_RES")))
                feature.SetField("ResAllots", int(currentAttList.get_attribute("ResAllots")))
                feature.SetField("ResDWpLot", int(currentAttList.get_attribute("ResDWpLot")))
                feature.SetField("ResHouses", int(currentAttList.get_attribute("ResHouses")))
                feature.SetField("ResLotArea", float(currentAttList.get_attribute("ResLotArea")))
                feature.SetField("ResRoof", float(currentAttList.get_attribute("ResRoof")))
                feature.SetField("avLt_RES", float(currentAttList.get_attribute("avLt_RES")))
                feature.SetField("ResHFloors", int(currentAttList.get_attribute("ResHFloors")))
                feature.SetField("ResLotTIA", float(currentAttList.get_attribute("ResLotTIA")))
                feature.SetField("ResLotEIA", float(currentAttList.get_attribute("ResLotEIA")))
                feature.SetField("ResGarden", float(currentAttList.get_attribute("ResGarden")))
                feature.SetField("ResRoofCon", str(currentAttList.get_attribute("ResRoofCon")))
                feature.SetField("ResLotALS", float(currentAttList.get_attribute("ResLotALS")))
                feature.SetField("ResLotARS", float(currentAttList.get_attribute("ResLotARS")))

            if currentAttList.get_attribute("HasFlats"):
                feature.SetField("HDRFlats", int(currentAttList.get_attribute("HDRFlats")))         # High-Density
                feature.SetField("HDRRoofA", float(currentAttList.get_attribute("HDRRoofA")))
                feature.SetField("HDROccup", float(currentAttList.get_attribute("HDROccup")))
                feature.SetField("HDR_TIA", float(currentAttList.get_attribute("HDR_TIA")))
                feature.SetField("HDR_EIA", float(currentAttList.get_attribute("HDR_EIA")))
                feature.SetField("HDRFloors", int(currentAttList.get_attribute("HDRFloors")))
                feature.SetField("av_HDRes", float(currentAttList.get_attribute("av_HDRes")))
                feature.SetField("HDRGarden", float(currentAttList.get_attribute("HDRGarden")))
                feature.SetField("HDRCarPark", float(currentAttList.get_attribute("HDRCarPark")))

            if currentAttList.get_attribute("Has_LI"):
                feature.SetField("LIjobs", int(currentAttList.get_attribute("LIjobs")))             # Light Industry
                feature.SetField("LIestates", int(currentAttList.get_attribute("LIestates")))
                feature.SetField("avSt_LI", float(currentAttList.get_attribute("avSt_LI")))
                feature.SetField("LIAfront", float(currentAttList.get_attribute("LIAfront")))
                feature.SetField("LIAfrEIA", float(currentAttList.get_attribute("LIAfrEIA")))
                feature.SetField("LIAestate", float(currentAttList.get_attribute("LIAestate")))
                feature.SetField("LIAeBldg", float(currentAttList.get_attribute("LIAeBldg")))
                feature.SetField("LIFloors", int(currentAttList.get_attribute("LIFloors")))
                feature.SetField("LIAeLoad", float(currentAttList.get_attribute("LIAeLoad")))
                feature.SetField("LIAeCPark", float(currentAttList.get_attribute("LIAeCPark")))
                feature.SetField("avLt_LI", float(currentAttList.get_attribute("avLt_LI")))
                feature.SetField("LIAeLgrey", float(currentAttList.get_attribute("LIAeLgrey")))
                feature.SetField("LIAeEIA", float(currentAttList.get_attribute("LIAeEIA")))
                feature.SetField("LIAeTIA", float(currentAttList.get_attribute("LIAeTIA")))

            if currentAttList.get_attribute("Has_HI"):
                feature.SetField("HIjobs", int(currentAttList.get_attribute("HIjobs")))             # Heavy Industry
                feature.SetField("HIestates", int(currentAttList.get_attribute("HIestates")))
                feature.SetField("avSt_HI", float(currentAttList.get_attribute("avSt_HI")))
                feature.SetField("HIAfront", float(currentAttList.get_attribute("HIAfront")))
                feature.SetField("HIAfrEIA", float(currentAttList.get_attribute("HIAfrEIA")))
                feature.SetField("HIAestate", float(currentAttList.get_attribute("HIAestate")))
                feature.SetField("HIAeBldg", float(currentAttList.get_attribute("HIAeBldg")))
                feature.SetField("HIFloors", int(currentAttList.get_attribute("HIFloors")))
                feature.SetField("HIAeLoad", float(currentAttList.get_attribute("HIAeLoad")))
                feature.SetField("HIAeCPark", float(currentAttList.get_attribute("HIAeCPark")))
                feature.SetField("avLt_HI", float(currentAttList.get_attribute("avLt_HI")))
                feature.SetField("HIAeLgrey", float(currentAttList.get_attribute("HIAeLgrey")))
                feature.SetField("HIAeEIA", float(currentAttList.get_attribute("HIAeEIA")))
                feature.SetField("HIAeTIA", float(currentAttList.get_attribute("HIAeTIA")))

            if currentAttList.get_attribute("Has_COM"):
                feature.SetField("COMjobs", int(currentAttList.get_attribute("COMjobs")))           # Commercial
                feature.SetField("COMestates", int(currentAttList.get_attribute("COMestates")))
                feature.SetField("avSt_COM", float(currentAttList.get_attribute("avSt_COM")))
                feature.SetField("COMAfront", float(currentAttList.get_attribute("COMAfront")))
                feature.SetField("COMAfrEIA", float(currentAttList.get_attribute("COMAfrEIA")))
                feature.SetField("COMAestate", float(currentAttList.get_attribute("COMAestate")))
                feature.SetField("COMAeBldg", float(currentAttList.get_attribute("COMAeBldg")))
                feature.SetField("COMFloors", int(currentAttList.get_attribute("COMFloors")))
                feature.SetField("COMAeLoad", float(currentAttList.get_attribute("COMAeLoad")))
                feature.SetField("COMAeCPark", float(currentAttList.get_attribute("COMAeCPark")))
                feature.SetField("avLt_COM", float(currentAttList.get_attribute("avLt_COM")))
                feature.SetField("COMAeLgrey", float(currentAttList.get_attribute("COMAeLgrey")))
                feature.SetField("COMAeEIA", float(currentAttList.get_attribute("COMAeEIA")))
                feature.SetField("COMAeTIA", float(currentAttList.get_attribute("COMAeTIA")))

            if currentAttList.get_attribute("Has_ORC"):
                feature.SetField("ORCjobs", int(currentAttList.get_attribute("ORCjobs")))           # Offices
                feature.SetField("ORCestates", int(currentAttList.get_attribute("ORCestates")))
                feature.SetField("avSt_ORC", float(currentAttList.get_attribute("avSt_ORC")))
                feature.SetField("ORCAfront", float(currentAttList.get_attribute("ORCAfront")))
                feature.SetField("ORCAfrEIA", float(currentAttList.get_attribute("ORCAfrEIA")))
                feature.SetField("ORCAestate", float(currentAttList.get_attribute("ORCAestate")))
                feature.SetField("ORCAeBldg", float(currentAttList.get_attribute("ORCAeBldg")))
                feature.SetField("ORCFloors", int(currentAttList.get_attribute("ORCFloors")))
                feature.SetField("ORCAeLoad", float(currentAttList.get_attribute("ORCAeLoad")))
                feature.SetField("ORCAeCPark", float(currentAttList.get_attribute("ORCAeCPark")))
                feature.SetField("avLt_ORC", float(currentAttList.get_attribute("avLt_ORC")))
                feature.SetField("ORCAeLgrey", float(currentAttList.get_attribute("ORCAeLgrey")))
                feature.SetField("ORCAeEIA", float(currentAttList.get_attribute("ORCAeEIA")))
                feature.SetField("ORCAeTIA", float(currentAttList.get_attribute("ORCAeTIA")))

            feature.SetField("Blk_TIA", float(currentAttList.get_attribute("Blk_TIA")))
            feature.SetField("Blk_EIA", float(currentAttList.get_attribute("Blk_EIA")))
            feature.SetField("Blk_EIF", float(currentAttList.get_attribute("Blk_EIF")))
            feature.SetField("Blk_TIF", float(currentAttList.get_attribute("Blk_TIF")))
            feature.SetField("Blk_RoofsA", float(currentAttList.get_attribute("Blk_RoofsA")))

        if map_attr.get_attribute("HasLANDCOVER"):
            feature.SetField("LC_RES_DG", float(currentAttList.get_attribute("LC_RES_DG")))
            feature.SetField("LC_RES_IG", float(currentAttList.get_attribute("LC_RES_IG")))
            feature.SetField("LC_RES_CO", float(currentAttList.get_attribute("LC_RES_CO")))
            feature.SetField("LC_RES_AS", float(currentAttList.get_attribute("LC_RES_AS")))
            feature.SetField("LC_RES_TR", float(currentAttList.get_attribute("LC_RES_TR")))
            feature.SetField("LC_RES_RF", float(currentAttList.get_attribute("LC_RES_RF")))
            feature.SetField("LC_COM_DG", float(currentAttList.get_attribute("LC_COM_DG")))
            feature.SetField("LC_COM_IG", float(currentAttList.get_attribute("LC_COM_IG")))
            feature.SetField("LC_COM_CO", float(currentAttList.get_attribute("LC_COM_CO")))
            feature.SetField("LC_COM_AS", float(currentAttList.get_attribute("LC_COM_AS")))
            feature.SetField("LC_COM_TR", float(currentAttList.get_attribute("LC_COM_TR")))
            feature.SetField("LC_COM_RF", float(currentAttList.get_attribute("LC_COM_RF")))
            feature.SetField("LC_LI_DG", float(currentAttList.get_attribute("LC_LI_DG")))
            feature.SetField("LC_LI_IG", float(currentAttList.get_attribute("LC_LI_IG")))
            feature.SetField("LC_LI_CO", float(currentAttList.get_attribute("LC_LI_CO")))
            feature.SetField("LC_LI_AS", float(currentAttList.get_attribute("LC_LI_AS")))
            feature.SetField("LC_LI_TR", float(currentAttList.get_attribute("LC_LI_TR")))
            feature.SetField("LC_LI_RF", float(currentAttList.get_attribute("LC_LI_RF")))
            feature.SetField("LC_HI_DG", float(currentAttList.get_attribute("LC_HI_DG")))
            feature.SetField("LC_HI_IG", float(currentAttList.get_attribute("LC_HI_IG")))
            feature.SetField("LC_HI_CO", float(currentAttList.get_attribute("LC_HI_CO")))
            feature.SetField("LC_HI_AS", float(currentAttList.get_attribute("LC_HI_AS")))
            feature.SetField("LC_HI_TR", float(currentAttList.get_attribute("LC_HI_TR")))
            feature.SetField("LC_HI_RF", float(currentAttList.get_attribute("LC_HI_RF")))
            feature.SetField("LC_ORC_DG", float(currentAttList.get_attribute("LC_ORC_DG")))
            feature.SetField("LC_ORC_IG", float(currentAttList.get_attribute("LC_ORC_IG")))
            feature.SetField("LC_ORC_CO", float(currentAttList.get_attribute("LC_ORC_CO")))
            feature.SetField("LC_ORC_AS", float(currentAttList.get_attribute("LC_ORC_AS")))
            feature.SetField("LC_ORC_TR", float(currentAttList.get_attribute("LC_ORC_TR")))
            feature.SetField("LC_ORC_RF", float(currentAttList.get_attribute("LC_ORC_RF")))
            feature.SetField("LC_NA_DG", float(currentAttList.get_attribute("LC_NA_DG")))
            feature.SetField("LC_NA_IG", float(currentAttList.get_attribute("LC_NA_IG")))
            feature.SetField("LC_NA_CO", float(currentAttList.get_attribute("LC_NA_CO")))
            feature.SetField("LC_UND_DG", float(currentAttList.get_attribute("LC_UND_DG")))
            feature.SetField("LC_UND_IG", float(currentAttList.get_attribute("LC_UND_IG")))
            feature.SetField("LC_SVU_DG", float(currentAttList.get_attribute("LC_SVU_DG")))
            feature.SetField("LC_PG_DG", float(currentAttList.get_attribute("LC_PG_DG")))
            feature.SetField("LC_PG_IG", float(currentAttList.get_attribute("LC_PG_IG")))
            feature.SetField("LC_PG_CO", float(currentAttList.get_attribute("LC_PG_CO")))
            feature.SetField("LC_PG_AS", float(currentAttList.get_attribute("LC_PG_AS")))
            feature.SetField("LC_PG_TR", float(currentAttList.get_attribute("LC_PG_TR")))
            feature.SetField("LC_REF_DG", float(currentAttList.get_attribute("LC_REF_DG")))
            feature.SetField("LC_REF_IG", float(currentAttList.get_attribute("LC_REF_IG")))
            feature.SetField("LC_RD_DG", float(currentAttList.get_attribute("LC_RD_DG")))
            feature.SetField("LC_RD_CO", float(currentAttList.get_attribute("LC_RD_CO")))
            feature.SetField("LC_RD_AS", float(currentAttList.get_attribute("LC_RD_AS")))

        if map_attr.get_attribute("HasWATERUSE"):
            if map_attr.get_attribute("WD_RES_Method") == "EUA":
                feature.SetField("WD_HHKitch", float(currentAttList.get_attribute("WD_HHKitchen")))
                feature.SetField("WD_HHShow", float(currentAttList.get_attribute("WD_HHShower")))
                feature.SetField("WD_HHToil", float(currentAttList.get_attribute("WD_HHToilet")))
                feature.SetField("WD_HHLaund", float(currentAttList.get_attribute("WD_HHLaundry")))
                feature.SetField("WD_HHDish", float(currentAttList.get_attribute("WD_HHDish")))
                feature.SetField("WD_HHIn", float(currentAttList.get_attribute("WD_HHIndoor")))
                feature.SetField("WD_HHHot", float(currentAttList.get_attribute("WD_HHHot")))
                feature.SetField("HH_GreyW", float(currentAttList.get_attribute("HH_GreyW")))
                feature.SetField("HH_BlackW", float(currentAttList.get_attribute("HH_BlackW")))
            else:
                feature.SetField("WD_HHIn", float(currentAttList.get_attribute("WD_HHIndoor")))
                feature.SetField("WD_HHHot", float(currentAttList.get_attribute("WD_HHHot")))
                feature.SetField("WD_HHNonPo", float(currentAttList.get_attribute("WD_HHNonPot")))
                feature.SetField("HH_GreyW", float(currentAttList.get_attribute("HH_GreyW")))
                feature.SetField("HH_BlackW", float(currentAttList.get_attribute("HH_BlackW")))

            feature.SetField("WD_In", float(currentAttList.get_attribute("WD_Indoor")))
            feature.SetField("WD_Out", float(currentAttList.get_attribute("WD_Outdoor")))
            feature.SetField("WD_Hot", float(currentAttList.get_attribute("WD_HotVol")))
            feature.SetField("WW_ResG", float(currentAttList.get_attribute("WW_ResGrey")))
            feature.SetField("WW_ResB", float(currentAttList.get_attribute("WW_ResBlack")))

            feature.SetField("WD_COM", float(currentAttList.get_attribute("WD_COM")))
            feature.SetField("WD_HotCOM", float(currentAttList.get_attribute("WD_HotCOM")))
            feature.SetField("WD_Office", float(currentAttList.get_attribute("WD_Office")))
            feature.SetField("WD_HotOff", float(currentAttList.get_attribute("WD_HotOffice")))
            feature.SetField("WD_LI", float(currentAttList.get_attribute("WD_LI")))
            feature.SetField("WD_HotLI", float(currentAttList.get_attribute("WD_HotLI")))
            feature.SetField("WD_HI", float(currentAttList.get_attribute("WD_HI")))
            feature.SetField("WD_HotHI", float(currentAttList.get_attribute("WD_HotHI")))

            feature.SetField("WD_NRes", float(currentAttList.get_attribute("WD_NRes")))
            feature.SetField("WD_HotNRes", float(currentAttList.get_attribute("WD_HotNRes")))
            feature.SetField("WD_NResIrr", float(currentAttList.get_attribute("WD_NResIrri")))
            feature.SetField("WW_ComG", float(currentAttList.get_attribute("WW_ComGrey")))
            feature.SetField("WW_ComB", float(currentAttList.get_attribute("WW_ComBlack")))
            feature.SetField("WW_IndG", float(currentAttList.get_attribute("WW_IndGrey")))
            feature.SetField("WW_IndB", float(currentAttList.get_attribute("WW_IndBlack")))
            feature.SetField("WD_POSIrr", float(currentAttList.get_attribute("WD_POSIrri")))

            feature.SetField("Blk_WD", float(currentAttList.get_attribute("Blk_WD")))
            feature.SetField("Blk_WDIrr", float(currentAttList.get_attribute("Blk_WDIrri")))
            feature.SetField("Blk_WDHot", float(currentAttList.get_attribute("Blk_WDHot")))
            feature.SetField("Blk_WW", float(currentAttList.get_attribute("Blk_WW")))
            feature.SetField("Blk_WWG", float(currentAttList.get_attribute("Blk_WWGrey")))
            feature.SetField("Blk_WWB", float(currentAttList.get_attribute("Blk_WWBlack")))
            feature.SetField("Blk_Loss", float(currentAttList.get_attribute("Blk_Losses")))

        if map_attr.get_attribute("HasINFRA"):
            if map_attr.get_attribute("HasSWW"):
                feature.SetField("HasSWW", int(currentAttList.get_attribute("HasSWW")))
                feature.SetField("HasWWTP", int(currentAttList.get_attribute("HasWWTP")))
                feature.SetField("HasCarved", int(currentAttList.get_attribute("HasCarved")))
                feature.SetField("Sww_DownID", int(currentAttList.get_attribute("Sww_DownID")))
                feature.SetField("ModAvgElev", float(currentAttList.get_attribute("ModAvgElev")))

        layer.CreateFeature(feature)

    shapefile.Destroy()
    return True
