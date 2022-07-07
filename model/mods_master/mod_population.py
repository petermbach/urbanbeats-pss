r"""
@file   mod_population.py
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

class MapPopulationToSimGrid(UBModule):
    """ Maps population data to the simulation grid, using data from a raster or shapefile based population data set.
    Several additional options allow for correction of the population data depenidng on the mapping process where
    errors may emerge."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 4
    longname = "Map Population"
    icon = ":/icons/demographics.png"

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
        self.create_parameter("popmapdataid", STRING, "Name of the population map to load for mapping")
        self.create_parameter("popdataattr", STRING, "Attribute name to use if population file is .shp")
        self.assetcolname = "(select asset collection)"
        self.popmapdataid = "(no population maps in project)"
        self.popdataattr = "(attribute name)"

        self.create_parameter("popdataformat", STRING, "Format of the population data, density or totals")
        self.create_parameter("applypopcorrect", BOOL, "Apply a population correction factor?")
        self.create_parameter("popcorrectfact", DOUBLE, "Population correction factor")
        self.create_parameter("popcorrectauto", BOOL, "Auto-determine population correction factor")
        self.popdataformat = "DEN"     # DEN = density (people/ha) or TOT = total counts
        self.applypopcorrect = 0
        self.popcorrectfact = 1.0      # Adjusts all mapped populations by this factor
        self.popcorrectauto = 0        # Determines the popcorrectfact based on input map's total population

        self.create_parameter("mappoptolanduse", BOOL, "Map Population to land use?")
        self.create_parameter("landusemapdataid", STRING, "Name of the land use map to map population against")
        self.create_parameter("landuseattr", STRING, "Attribute name to use if land use file is .shp")
        self.mappoptolanduse = 0
        self.landusemapdataid = "(select land use map)"
        self.landuseattr = "(attribute name)"

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
        self.meta.add_attribute("mod_population", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Population to Simulation")
        self.notify("--- === ---")
        self.notify("Geometry Type: " +self.assetident)
        self.notify_progress(0)

        # --- SECTION 1 - (description)
        # --- SECTION 2 - (description)
        # --- SECTION 3 - (description)

        self.notify("Mapping of population data to simulation grid complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass