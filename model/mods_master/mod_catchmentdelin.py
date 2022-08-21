r"""
@file   mod_catchmentdelin.py
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
from model.ubmodule import *

class DelineateFlowSubCatchments(UBModule):
    """ Delineates water flow paths and sub-catchments across the simulation grid. These flowpaths are topogrpahically
    based but can also be guided by the presence of natural features or input data sets to help the delineation. Finds
    outlets in the simulation grid."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Hydrology"
    catorder = 2
    longname = "Flow Paths & Sub-catchments"
    icon = ":/icons/river_flow.png"

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
        self.nodata = None

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.assetcolname = "(select asset collection)"

        self.create_parameter("flowpath_method", STRING, "flowpath method to use")
        self.create_parameter("guide_natural", BOOL, "Use natural features to guide delineation")
        self.create_parameter("guide_built", BOOL, "Use built drainage features to guide delineation")
        self.create_parameter("built_map", STRING, "DataID for the built infrastructure map to use as guide")
        self.create_parameter("ignore_rivers", BOOL, "Ignore rivers in delineation of outlets")
        self.create_parameter("ignore_lakes", BOOL, "Ignore lake features in the delineation of outlets")
        self.flowpath_method = "D8"     # D-inf, D8, LCP
        self.guide_natural = 0
        self.guide_built = 0
        self.built_map = "(select built infrastructure map)"
        self.ignore_rivers = 0
        self.ignore_lakes = 0

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")
            return False

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
            return False

        # Pre-requisite - needs to have at least the elevation mapping done
        if self.meta.get_attribute("mod_topography") != 1:
            self.notify("Cannot start module! No elevation data. Please run the Map Topography module first")
            return False

        self.meta.add_attribute("mod_catchmentdelin", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")
        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")
        return True

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        if not self.initialize_runstate():
            self.notify("Module run terminated!")
            return True

        self.notify("Delineating flow paths and sub-catchments")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 0 - Grab asset information
        griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets within the map: "+str(len(griditems)))
        self.notify_progress(10)

        # --- SECTION 1 - Flowpath Delineation
        if self.assetident in ["BlockID", "HexID", "GeohashID"]:        # REGULAR GRID
            pass    # Regular Grid Flowpath Delineation
        elif self.assetident in ["PatchID", "ParcelID"]:        # IRREGULAR GRID
            pass    # Irregular Grid Flowpath Delineation
        else:
            pass    # Raster map, quite different...



        self.notify_progress(50)

        # --- SECTION 2 - Sub-catchment Delineation



        self.notify("Flowpath and catchment delineation complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass