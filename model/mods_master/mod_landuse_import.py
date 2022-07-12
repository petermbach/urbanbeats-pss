r"""
@file   mod_landuse_import.py
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
from shapely.geometry import Polygon, Point
import rasterio
import rasterio.features
import numpy as np

from model.ubmodule import *
import model.ublibs.ubspatial as ubspatial

class MapLandUseToSimGrid(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 3
    longname = "Map Land Use"
    icon = ":/icons/region.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES
        self.assets = None
        self.meta = None
        self.xllcorner = None
        self.yllcorner = None
        self.assetident = ""
        self.landusemap = None
        self.nodata = None

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.create_parameter("landusemapid", STRING, "Name of the land use map to load for mapping")
        self.create_parameter("landuseattr", STRING, "Attribute containing the classification if .shp")
        self.assetcolname = "(select asset collection)"
        self.landusemapid = "(no land use map in the project)"
        self.landuseattr = "(attribute name)"

        self.create_parameter("lureclass", BOOL, "Reclassify the land use map?")
        self.create_parameter("lureclasssystem", DICT, "List of dictionaries to do the reclassification")
        self.lureclass = 0
        self.lureclasssystem = {}

        self.create_parameter("singlelu", BOOL, "Use only a single land use per grid unit?")
        self.create_parameter("patchdelin", BOOL, "Delineate Land Use Patches?")
        self.create_parameter("spatialmetrics", BOOL, "Calculate spatial metrics?")
        self.singlelu = 0
        self.patchdelin = 0
        self.spatialmetrics = 0

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
        self.meta.add_attribute("mod_landuse_import", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Land Use to Simulation")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 1 - LOAD LAND USE MAP
        lumap = self.datalibrary.get_data_with_id(self.landusemapid)
        filename = lumap.get_metadata("filename")
        fullpath = lumap.get_data_file_path() + filename
        self.notify("Loading Land Use Map: "+str(filename))

        # DETERMINE DATA FORMAT (1) Vector or (2) Raster
        if ".shp" in filename:
            # VECTOR FORMAT
            self.landusemap = ubspatial.import_polygonal_map(fullpath, "native", "LandUse",
                                                             (self.xllcorner, self.yllcorner))
            lufmt = "VECTOR"

            # Metadata
            self.notify("Polygon Features: "+str(len(self.landusemap)))
        else:
            # RASTER FORMAT - OPEN THE FILE
            self.landusemap = rasterio.open(fullpath)
            self.nodata = self.landusemap.nodata
            lufmt = "RASTER"

            # Metadata
            self.notify("Raster Shape: " + str(self.landusemap.shape))
            self.notify(str(self.landusemap.bounds))
            self.notify("Nodata Value: " + str(self.nodata))
            self.notify("Raster Resolution: " + str(self.landusemap.res))
            self.notify_progress(30)

        # --- SECTION 2 - MAP LAND USE TO SIM GRID - RECLASSIFY IF NECESSARY
        self.notify("Mapping land use to simulation grid")
        if lufmt == "VECTOR":
            self.map_polygonal_landuse_to_simgrid()
        else:
            self.map_raster_landuse_to_simgrid()

        self.notify("Mapping of land use data to simulation grid complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def map_polygonal_landuse_to_simgrid(self):
        pass

    def map_raster_landuse_to_simgrid(self):
        pass


# GLOBAL VARIABLES TIED TO THIS MODULE
UBLANDUSENAMES = ["Residential", "Commercial", "Mixed Offices & Res", "Light Industry", "Heavy Industry", "Civic",
                  "Services & Utility", "Road", "Transport", "Parks & Garden", "Reserves & Floodway", "Undeveloped",
                  "Unclassified", "Water", "Forest", "Agriculture"]
UBLANDUSEABBR = ["RES", "COM", "ORC", "LI", "HI", "CIV", "SVU", "RD", "TR", "PG", "REF", "UND",
                 "UNC", "WAT", "FOR", "AGR"]