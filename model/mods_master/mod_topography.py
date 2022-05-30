r"""
@file   mod_simgrid.py
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
__copyright__ = "Copyright 2022. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
from model.ubmodule import *

class MapTopographyToSimGrid(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 5
    longname = "Map Topography"
    icon = ":/icons/topography.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES HOLDING IMPORTANT REFERENCES TO SIMULATION - SET AT INITIALIZATION
        self.assets = None  # If used as one-off on-the-fly modelling, then scenario is None
        self.meta = None  # Simulation metadata contained in assets, this variable will hold it
        self.assetident = ""

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.create_parameter("elevmapname", STRING, "Name of the elevation map to load for mapping")
        self.assetcolname = "(select asset collection)"
        self.elevmapname = "(no elevation maps in project)"

        self.create_parameter("demsmooth", BOOL, "Perform smoothing on the DEM?")
        self.create_parameter("dempasses", DOUBLE, "Number of passes to perform smoothing for")
        self.demsmooth = 0
        self.dempasses = 1

        self.create_parameter("demstats", BOOL, "Calculate statistics for coarse grid DEMs?")
        self.create_parameter("demminmax", BOOL, "Indicate lowest elevation point on the map?")
        self.create_parameter("slope", BOOL, "Calculate slope?")
        self.create_parameter("aspect", BOOL, "Calculate aspect?")
        self.demstats = 0
        self.demminmax = 0
        self.slope = 0
        self.aspect = 0

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error! Missing Asset Collection!")

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection Missing Metadata")
        self.meta.add_attribute("mod_topography", 1)    # This denotes that the module will be run
        self.assetident = self.meta.get_attribute("AssetIdent")     # Get the geometry type before starting!

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Topography data to Simulation")
        self.notify("--- === ---")
        self.notify_progress(0)

        # --- SECTION 1 - Get the elevation map data to be mapped


        # --- SECTION 2 - Begin mapping the data based on geometry type - calculate relevant stats if needed


        # --- SECTION 3 - Perform DEM Smoothing if requested


        # --- SECTION 4 - Calculate slope and aspect


        self.notify("Finished SimGrid Creation")
        self.notify_progress(100)  # Must notify of 100% progress if the 'close' button is to be renabled.
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass