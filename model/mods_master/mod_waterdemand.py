r"""
@file   mod_waterdemand.py
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

class WaterDemandMapping(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Water Management"
    catorder = 1
    longname = "Water Demand Mapping"
    icon = ":/icons/hand-washing.png"

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
        self.populationmap = None
        self.nodata = None

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.assetcolname = "(select asset collection)"


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
        self.meta.add_attribute("mod_mapregions", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Regions to the Simulation Grid")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        print(self.boundaries_to_map)

        # --- SECTION 1 - (description)
        # --- SECTION 2 - (description)
        # --- SECTION 3 - (description)

        self.notify("Mapping of regions to simulation grid complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass




# WATER-RELATED ELEMENTS
RESSTANDARDS = ["AS6400", "Others..."]
FFP = ["PO", "NP", "RW", "SW", "GW"]    # Fit for purpose water qualities
DPS = ["SDD", "CDP", "OHT", "AHC", "USER"]    # Types of diurnal patterns

# Diurnal Patterns
# SDD = STANDARD DAILY DIURNAL PATTERN SCALING FACTORS
SDD = [0.3, 0.3, 0.3, 0.3, 0.5, 1.0, 1.5, 1.5, 1.3, 1.0, 1.0, 1.5, 1.5, 1.2, 1.0, 1.0, 1.0, 1.3, 1.3, 0.8,
       0.8, 0.5, 0.5, 0.5]

# CDP = CONSTANT DAILY DIURNAL PATTERN SCALING FACTORS
CDP = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
       1.0, 1.0, 1.0, 1.0]

# OHT = OFFICE HOURS TRAPEZOIDAL DIURNAL PATTERN SCALING FACTORS
OHT = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.0, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5,
       0.0, 0.0, 0.0, 0.0]

# AHC = AFTER HOURS CONSTANT DIURNAL PATTERN
AHC = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
       2.0, 2.0, 2.0, 2.0]

DIURNAL_CATS = ["res_kitchen", "res_shower", "res_toilet", "res_laundry", "res_dishwasher", "res_outdoor",
                "res_dailyindoor", "com", "ind", "nonres_landscape", "pos_irrigation"]

DIURNAL_LABELS = ["Kitchen", "Shower", "Toilet", "Laundry", "Dishwasher", "Garden",
                  "Residential Indoor", "Commercial and Offices", "Industries", "Non-residential Outdoor",
                  "Public Irrigation"]
