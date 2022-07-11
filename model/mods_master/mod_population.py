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
from shapely.geometry import Polygon, Point
import rasterio
import rasterio.features
import numpy as np

from model.ubmodule import *
import model.ublibs.ubspatial as ubspatial


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
        self.meta.add_attribute("mod_population", 1)        # Note that the module has been run on this asset col
        self.assetident = self.meta.get_attribute("AssetIdent")     # Select what we are dealing with

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Population to Simulation")
        self.notify("--- === ---")
        self.notify("Geometry Type: " +self.assetident)
        self.notify_progress(0)

        # --- SECTION 1 - LOAD POPULATION MAP
        popmap = self.datalibrary.get_data_with_id(self.popmapdataid)
        filename = popmap.get_metadata("filename")
        fullpath = popmap.get_data_file_path() + filename
        self.notify("Loading Population Map: "+str(popmap.get_metadata("filename")))

        # Determine data format... (1) Vector vs. (2) Raster and then (1.1) Points/Polygons vs. (2.1) Tiff/ASCII
        if ".shp" in filename:
            # VECTOR FORMAT
            popfmt = "VECTOR"

        else:
            # RASTER FORMAT - OPEN THE FILE
            self.populationmap = rasterio.open(fullpath)
            self.nodata = self.populationmap.nodata
            popfmt = "RASTER"

            # Metadata
            self.notify("Raster Shape: " + str(self.populationmap.shape))
            self.notify(str(self.populationmap.bounds))
            self.notify("Nodata Value: " + str(self.nodata))
            self.notify("Raster Resolution: " + str(self.populationmap.res))
            self.notify_progress(30)

        # --- SECTION 2 - MAP POPULATION TO LAND USE MAP BEFORE DETERMINING POP
        if self.mappoptolanduse:
            self.notify("Remapping population data to land use map")
            # [TO DO]

        self.notify_progress(50)

        # --- SECTION 3 - CALCULATE THE CORRECTION FACTOR IF WANTED AND AUTO IS CHECKED
        if self.applypopcorrect and self.popcorrectauto:
            self.notify("Determining a population correction factor")
            # [TO DO]
        else:
            self.popcorrectfact = 1.00

        self.notify_progress(70)

        # --- SECTION 4 - MAP THE POPULATION TO THE SIMULATION GRID
        self.notify("Mapping population data to simulation grid")
        if popfmt == "VECTOR":
            self.map_polygonal_population_to_simgrid()
        else:
            self.map_raster_population_to_simgrid()

        self.notify("Mapping of population data to simulation grid complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def map_raster_population_to_simgrid(self):
        """Maps a raster data set of population to the simulation grid."""
        griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets to map data to: "+str(len(griditems)))

        for i in range(len(griditems)):
            if griditems[i].get_attribute("Status") == 0:
                continue    # Skip if status is zero, could have resulted from another module switching it off.

            asset = griditems[i]
            assetid = asset.get_attribute(self.assetident)

            # Mask and grab the data
            mdata = ubspatial.retrieve_raster_data_from_mask(self.populationmap, asset, self.xllcorner, self.yllcorner)

            if mdata is None:
                self.notify(self.assetident + str(assetid) + " not within bounds, skipping!")
                asset.add_attribute("Population", 0)
                continue

            if len(mdata) == 0:
                asset.add_attribute("Population", 0)
                continue
            else:       # Work out metric
                if self.popdataformat == "DEN":     # DENSITY
                    # People per ha, get the resolution
                    resarea = self.populationmap.res[0] * self.populationmap.res[1] / 10000.0   # [ha]
                    assetarea = asset.get_attribute("Area") / 10000.0       # [ha]

                    if assetarea < resarea:
                        totalpop = assetarea * mdata.sum()
                    else:
                        totalpop = sum([mdata[i] * resarea for i in range(len(mdata))])
                    totalpop = totalpop * self.popcorrectfact   # CORRECTION?
                else:   # COUNT
                    totalpop = mdata.sum() * self.popcorrectfact    # CORRECTION?

                asset.add_attribute("Population", round(totalpop))

    def map_polygonal_population_to_simgrid(self):
        """Maps a polygon map of population data to the simgrid depending on the intersection of polygon with the
        simgrid."""
        pass

