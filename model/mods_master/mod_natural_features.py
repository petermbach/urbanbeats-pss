r"""
@file   mod_natural_features.py
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

from model.ubmodule import *
import model.ublibs.ubspatial as ubspatial

class MapNaturalFeaturesToSimGrid(UBModule):
    """ Maps river and lake features to a pre-defined simulation grid, labelling them based on an attribute of the
    original shapefile data set."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 6
    longname = "Map Natural Features"
    icon = ":/icons/nature_lake.png"

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
        self.rivermap = None
        self.lakemap = None

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.assetcolname = "(select asset collection)"

        # RIVERS
        self.create_parameter("rivermapdataid", STRING, "DataID of the river map to use in mapping")
        self.create_parameter("rivermapattr", STRING, "Attribute name containing identifiers for the river data")
        self.create_parameter("riverignorenoname", BOOL, "Ignore features with blank attributes")
        self.rivermapdataid = ""
        self.rivermapattr = ""
        self.riverignorenoname = 0

        # LAKES
        self.create_parameter("lakemapdataid", STRING, "DataID of the river map to use in mapping")
        self.create_parameter("lakemapattr", STRING, "Attribute name containing identifiers for the river data")
        self.create_parameter("lakeignorenoname", BOOL, "Ignore features with blank attributes")
        self.lakemapdataid = ""
        self.lakemapattr = ""
        self.lakeignorenoname = 0

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
        self.meta.add_attribute("mod_natural_features", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Natural Features to the Simulation Grid")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 1 - MAPPING RIVERS
        if self.rivermapdataid == "":
            self.notify("No rivers selected, skipping")
        else:
            self.map_rivers()

        # --- SECTION 2 - MAPPING LAKES
        if self.lakemapdataid == "":
            self.notify("No lakes and water bodies selected, skipping.")
        else:
            self.map_lakes()

        self.notify("Mapping of regions to simulation grid complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def map_rivers(self):
        """Maps the selected river or waterways map to the simulation grid."""
        rivermap = self.datalibrary.get_data_with_id(self.rivermapdataid)
        filename = rivermap.get_metadata("filename")
        fullpath = rivermap.get_data_file_path() + filename
        self.notify("Loading River Map: "+str(filename))

        riverfeats = ubspatial.import_linear_network(fullpath, "LINES", (self.xllcorner, self.yllcorner))
        self.notify("Total River Features to check: "+str(len(riverfeats)))
        self.notify_progress(20)

        

        self.notify_progress(50)
        return True

    def map_lakes(self):
        """Maps the selected lakes and water bodies map to the simulation grid."""
        lakemap = self.datalibrary.get_data_with_id(self.lakemapdataid)
        filename = lakemap.get_metadata("filename")
        fullpath = lakemap.get_data_file_path() + filename
        self.notify("Loading River Map: " + str(filename))

        lakefeats = ubspatial.import_polygonal_map(fullpath, "native", "Lakes", (self.xllcorner, self.yllcorner))
        self.notify("Polygon features in lakes map: "+str(len(lakefeats)))
        self.notify_progress(70)


        self.notify_progress(90)
        return True