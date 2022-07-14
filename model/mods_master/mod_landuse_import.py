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
import math
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
        self.create_parameter("spatialmetrics", BOOL, "Calculate spatial metrics?")
        self.singlelu = 0
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

        if self.assetident not in ["BlockID", "HexID", "GeohashID"]:
            self.singlelu = 1       # If the asset type is not a Block, Hexagon or Geohash, then always use single class

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
        griditems = self.assets.get_assets_with_identifier(self.assetident)

        for i in range(len(griditems)):
            if griditems[i].get_attribute("Status") == 0:
                continue

            # Get the current asset's UBVector() Object and Geometry
            curasset = griditems[i]
            curassetpts = curasset.get_points()
            curassetpoly = Polygon([c[:2] for c in curassetpts])

            mdata = []          # Trackers of land use within the asset
            areavector = []

            for j in self.landusemap:           # Loop across the land use map
                feat = Polygon(j.get_points())
                if not feat.intersects(curassetpoly):
                    continue
                isectionarea = feat.intersection(curassetpoly).area

                if isectionarea != 0:
                    # Add information to the landuse tally - get the class and reclassify if necessary
                    lucclass = j.get_attribute(self.landuseattr)
                    if self.lureclass:
                        lucclass = self.lureclasssystem[lucclass]       # Reclassify before figuring out the number

                    if lucclass in UBLANDUSEABBR:       # Check for the abbreviated form first...
                        luccat = UBLANDUSEABBR.index(lucclass) + 1
                    elif lucclass in UBLANDUSENAMES:       # Check for the full name form
                        luccat = UBLANDUSENAMES.index(lucclass) + 1
                    elif int(lucclass) >= 1 and int(lucclass) <= 16:    # Could be the number code for the category
                        luccat = int(lucclass)
                    else:
                        continue    # Unrecognised land use, skip
                    mdata.append(luccat)
                    areavector.append(isectionarea)

            if self.singlelu:
                luc, activity = self.find_dominant_luc(mdata, curassetpoly.area, areavector)
                curasset.add_attribute("Activity", activity)
                curasset.add_attribute("LandUse", UBLANDUSENAMES[luc-1])
            else:
                luc, activity = self.tally_lu_frequency(mdata, curassetpoly.area, areavector)
                curasset.add_attribute("Activity", activity)
                self.write_lu_prop_attributes(curasset, luc)
                if self.spatialmetrics:
                    self.calculate_spatial_metrics(curasset, mdata, areavector)
        return True

    def map_raster_landuse_to_simgrid(self):
        """Maps the land use raster data to the simulation grid using raster masking."""
        griditems = self.assets.get_assets_with_identifier(self.assetident)

        for i in range(len(griditems)):
            if griditems[i].get_attribute("Status") == 0:
                continue

            curasset = griditems[i]
            curassetid = curasset.get_attribute(self.assetident)
            curassetpts = curasset.get_points()
            curassetpoly = Polygon([c[:2] for c in curassetpts])

            # DEBUG
            if curassetid in [1, 2, 13, 17, 80, 111, 196, 745, 804, 812, 830]:
                debug = True
                print("Current ID", curassetid)
            else:
                debug = False

            mdata = ubspatial.retrieve_raster_data_from_mask(self.landusemap, curasset, self.xllcorner, self.yllcorner, debug)

            if mdata is None or len(mdata) == 0:
                self.notify(self.assetident + str(curassetid) + " not within bounds or has no land use data, skipping!")
                self.set_landuse_to_none(curasset)
                continue

            # Tally Land Use Frequency or Find the Dominant Land use + spatial metrics
            if self.singlelu:
                luc, activity = self.find_dominant_luc(mdata, curassetpoly.area)
                curasset.add_attribute("Activity", activity)
                curasset.add_attribute("LandUse", UBLANDUSENAMES[luc-1])
            else:
                luc, activity = self.tally_lu_frequency(mdata, curassetpoly.area)
                curasset.add_attribute("Activity", activity)
                self.write_lu_prop_attributes(curasset, luc)
                if self.spatialmetrics:
                    self.calculate_spatial_metrics(curasset, mdata)
        return True

    def set_landuse_to_none(self, asset):
        """Sets all possible land use attributes to nothing depending on whether we are looking at mono or mix LU
        classes in the simulation asset."""
        asset.add_attribute("Activity", 0)  # Activity = 0 - i.e., no land use
        if self.singlelu:
            asset.add_attribute("LandUse", "")
        else:
            for i in range(len(UBLANDUSEABBR)):
                asset.add_attribute("pLU_"+UBLANDUSEABBR[i], 0)
        return True

    def write_lu_prop_attributes(self, asset, luprops):
        """Writes all land use proportion attributes"""
        for i in range(len(UBLANDUSEABBR)):
            asset.add_attribute("pLU_"+UBLANDUSEABBR[i], luprops[i])
        return True

    def tally_lu_frequency(self, masklist, assetarea, areavector=None):
        """Tallies the frequency of each land use category in the masklist and returns the proportions of total area
        and the total activity for the specified asset. Areavector is specified if the masklist items do not have
        uniform area."""
        luclist = self.count_luc_data(masklist, areavector)      # This returns the frequency matrix

        sum_luc = sum(luclist)  # Global sum across the classes - either a count or an area depending on raster/vect
        for i in range(len(luclist)):
            luclist[i] = float(luclist[i] / sum_luc)      # Relative proportion of LUCs... pLU_??? attribute

        activity = self.calculate_asset_activity(masklist, assetarea, areavector)
        return luclist, activity

    def find_dominant_luc(self, masklist, assetarea, areavector=None):
        """Finds the dominant land use based on area within a provided mask list and returns the single dominant land
        use category. If the areavector is provided, then items in the masklist do not have the same uniform area. Also
        returns total Activity of the current data tallied."""
        luclist = self.count_luc_data(masklist, areavector)
        luccat = luclist.index(max(luclist)) + 1        # Category is +1
        activity = self.calculate_asset_activity(masklist, assetarea, areavector)
        return luccat, activity

    def calculate_asset_activity(self, masklist, assetarea, areavector=None):
        """Determines the amount of the cell for which data is available, max of 1.0"""
        if areavector is None:  # RASTER - COUNT * RESOLUTION / ASSET AREA
            cellarea = self.landusemap.res[0] * self.landusemap.res[1]
            activity = min((len(masklist) * cellarea) / assetarea, 1.0)  # N * Acell / Assetarea
        else:  # VECTOR - AREAS DIVIDED BY EACH OTHER
            activity = min(sum(areavector) / assetarea, 1.0)  # Sum of the area vector
        return activity

    def count_luc_data(self, masklist, areavector=None):
        """A counting algorithm to sort the input mask list land uses into the 16 classes."""
        luclist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Holds counts for all 16 land uses

        for i in range(len(masklist)):
            if areavector is None:  # If raster...
                luclist[masklist[i] - 1] += 1  # Tally frequency
            else:  # Vector data...
                luclist[masklist[i] - 1] += areavector[i]  # Tally total area
        return luclist

    def calculate_spatial_metrics(self, asset, masklist, areavector=None):
        """Calculates the Richness, Shannon Dominance, Evenness and Diversity indices for the specified asset given
        its masklist. If the areavector is specified, then the items in the masklist do not have uniform area."""
        lucprops = self.count_luc_data(masklist, areavector)
        sumluc = sum(lucprops)
        for i in range(len(lucprops)):
            lucprops[i] = lucprops[i] / sumluc

        # Richness Index
        # The total number of unique categories in the asset
        richness = 0
        for i in lucprops:
            if i != 0:
                richness += 1

        # Shannon Diversity Index - measures diversity in categorical data, the information entropy of
        # the distribution: H = -sum(pi ln(pi)) - where pi is the proportion of land use i
        shandiv = 0
        for sdiv in lucprops:
            if sdiv != 0:
                shandiv += sdiv * math.log(sdiv)
        shandiv *= -1

        # Shannon Dominance Index - The degree to which a single class dominates in the area, 0 = evenness
        shandom = math.log(richness) - shandiv

        # Shannon Evenness Index: Similar to dominance, the level of evenness among the land classes
        if richness == 1:
            shaneven = 1
        else:
            shaneven = shandiv / math.log(richness)

        asset.add_attribute("Richness", richness)
        asset.add_attribute("Diversity", shandiv)
        asset.add_attribute("Dominance", shandom)
        asset.add_attribute("Evenness", shaneven)
        return True

# GLOBAL VARIABLES TIED TO THIS MODULE
UBLANDUSENAMES = ["Residential", "Commercial", "Mixed Offices & Res", "Light Industry", "Heavy Industry", "Civic",
                  "Services & Utility", "Road", "Transport", "Parks & Garden", "Reserves & Floodway", "Undeveloped",
                  "Unclassified", "Water", "Forest", "Agriculture"]
UBLANDUSEABBR = ["RES", "COM", "ORC", "LI", "HI", "CIV", "SVU", "RD", "TR", "PG", "REF", "UND",
                 "UNC", "WAT", "FOR", "AGR"]