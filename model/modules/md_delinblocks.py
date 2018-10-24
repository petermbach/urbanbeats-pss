# -*- coding: utf-8 -*-
"""
@file   md_delinblocks.py
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

# --- CODE STRUCTURE ---
#       (1) Class Definition
#           1.1 __init__() - primarily for parameter list
#           1.2 run() - the module algorithm
#           1.3 supplementary functions - all other modularised functions belonging to the module
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import math
import random as rand

import threading
import os
import gc
import tempfile
import math
import time
from shapely.geometry import Polygon

# --- URBANBEATS LIBRARY IMPORTS ---
from ubmodule import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
import model.progref.ubglobals as ubglobals


# --- MODULE CLASS DEFINITION ---

class DelinBlocks(UBModule):
    """ SPATIAL SETUP MODULE - Codename: DelinBlocks
    Loads the spatial maps into the model core and processes them into Blocks. Also performs spatial connectivity
    analysis and prepares all spatial input data in a ready-to-use format for all other modules. Links loaded data
    sets into the model.
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        """Initialises UBModule followed by full parameter list definition."""
        UBModule.__init__(self)
        self.name = "Delineation and Spatial Setup Module"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        # (Tab 1.1) ESSENTIAL SPATIAL DATA SETS
        self.create_parameter("landuse_map", STRING, "land use map filepath")
        self.create_parameter("population_map", STRING, "population map filepath")
        self.create_parameter("elevation_map", STRING, "elevation map filepath")
        self.create_parameter("landuse_fud", BOOL, "use urban development land use?")
        self.create_parameter("population_fud", BOOL, "use urban development population?")
        self.landuse_map = ""
        self.population_map = ""
        self.elevation_map = ""
        self.landuse_fud = 0
        self.population_fud = 0

        # (Tab 1.2) SPATIAL GEOMETRY
        self.create_parameter("geometry_type", STRING, "block or future types of geometry e.g. hex")
        self.geometry_type = "BLOCKS"  # BLOCKS, HEXAGONS, VECTORPATCH

        # 1.2.1 BLOCKS
        self.create_parameter("blocksize", DOUBLE, "resolution of the discretisation grid")
        self.create_parameter("blocksize_auto", BOOL, "determine resolution automatically?")
        self.create_parameter("neighbourhood", STRING, "type of neighbourhood to use, Moore or vN")
        self.create_parameter("patchdelin", BOOL, "delineate patches?")
        self.create_parameter("spatialmetrics", BOOL, "calculate spatial metrics?")
        self.blocksize = 500
        self.blocksize_auto = 0
        self.neighbourhood = "M"
        self.patchdelin = 1
        self.spatialmetrics = 1

        # 1.2.2 HEXAGONS    [TO DO]
        # 1.2.3 VECTORPATCHES [TO DO]


        # (Tab 2.1) JURISDICTIONAL AND SUBURBAN BOUNDARIES
        self.create_parameter("include_geopolitical", BOOL, "include geopolitical map?")
        self.create_parameter("geopolitical_map", STRING, "geopolitical map filepath")
        self.create_parameter("geopolitical_attref", STRING, "attribute name reference")
        self.create_parameter("include_suburb", BOOL, "include suburban map?")
        self.create_parameter("suburban_map", STRING, "suburban map filepath")
        self.create_parameter("suburban_attref", STRING, "attribute name reference")
        self.include_geopolitical = 0
        self.geopolitical_map = ""
        self.geopolitical_attref = ""
        self.include_suburb = 0
        self.suburban_map = ""
        self.suburban_attref = ""

        # (Tab 2.2) CENTRAL BUSINESS DISTRICT
        self.create_parameter("considerCBD", BOOL, "consider CBD Location?")
        self.create_parameter("locationOption", STRING, "method for inputting CBD location")
        self.create_parameter("locationCity", STRING, "city name")
        self.create_parameter("locationLong", DOUBLE, "CBD Longitude")
        self.create_parameter("locationLat", DOUBLE, "CBD Latitude")
        self.create_parameter("marklocation", BOOL, "mark location on output map")
        self.considerCBD = 0
        self.locationOption = "S"   # S = Selection, C = coordinates
        self.locationCity = self.activesim.get_project_parameter("city")
        self.locationLong = float(0.0)
        self.locationLat = float(0.0)
        self.marklocation = 0

        # (Tab 2.3) OPEN SPACE NETWORK
        self.create_parameter("osnet_accessibility", BOOL, "Calculate accessibility?")
        self.create_parameter("osnet_network", BOOL, "Delineate open space network?")
        self.osnet_accessibility = 0
        self.osnet_network = 0

        # (Tab 3.1) MAJOR WATER FEATURES
        self.create_parameter("include_rivers", BOOL, "include a rivers map into simulation?")
        self.create_parameter("include_lakes", BOOL, "include a ponds and lakes map into simulation?")
        self.create_parameter("calculate_wbdistance", BOOL, "calculate distance to closest water body?")
        self.create_parameter("river_map", STRING, "river map filepath")
        self.create_parameter("river_attname", STRING, "river map identifier attribute name")
        self.create_parameter("lake_map", STRING, "ponds and lake map filepath")
        self.create_parameter("lake_attname", STRING, "lake map identifier attribute name")
        self.include_rivers = 0
        self.include_lakes = 0
        self.calculate_wbdistance = 0
        self.river_map = ""
        self.river_attname = ""
        self.lake_map = ""
        self.lake_attname = ""

        # (Tab 3.2) BUILT WATER INFRASTRUCTURE #[TO DO]

        # (Tab 3.3) DRAINAGE FLOW PATHS
        self.create_parameter("flowpath_method", STRING, "flowpath method to use")
        self.create_parameter("dem_smooth", BOOL, "smooth DEM map before doing flowpath delineation?")
        self.create_parameter("dem_passes", DOUBLE, "number of passes for smoothing")
        self.create_parameter("guide_natural", BOOL, "guide flowpath delineation using pre-loaded natural feature?")
        self.create_parameter("guide_built", BOOL, "guide flowpath delineation using built infrastructure?")
        self.create_parameter("guide_natural_map", STRING, "filepath to natural features map to guide flowpaths")
        self.create_parameter("guide_built_map", STRING, "filepath to built infrastructure map to guide flowpaths")
        self.flowpath_method = "D8"
        self.dem_smooth = 0
        self.dem_passes = 1
        self.guide_natural = 0
        self.guide_built = 0
        self.guide_natural_map = ""
        self.guide_built_map = ""

        # NON-VISIBLE PARAMETER LIST - USED THROUGHOUT THE SIMULATION
        self.xllcorner = float(0.0)     # Obtained from the loaded raster data (elevation) upon run-time
        self.yllcorner = float(0.0)     # Spatial extents of the input map
        self.final_bs = self.blocksize  # Final_bs = final block size - this is determined at the start

        self.elevation = 0
        self.landuse = 0
        self.population = 0

        self.municipal_boundary = 0
        self.suburban_boundary = 0

        # ----- END OF INPUT PARAMETER LIST -----

    def run_module(self):
        """Contains the main algorithm for the module, links with all other functions thereafter. This is called by
        UrbanBEATSSim() simulation's scenario manager depending on which scenario is currently being simulated.

        :return: True upon successful completion
        """
        self.notify("Start Spatial Delineation Module")     # Module start
        rand.seed()     # Seed the random number generator

        # --- SECTION 1 - PREPARATION FOR CREATING THE GRIDDED MAP BASED ON THE INPUT BOUNDARY MAP ---

        # Check the neighbourhood rule and set the number of adjacent cells, nhd_type, accordingly
        if self.neighbourhood == "M":   # Determine number of neighbour cells depending on the neighbourhood
            nhd_type = 8    # 8 cardinal directions
        else:
            nhd_type = 4    # 4 adjacent cells NSEW

        # GET BOUNDARY EXTENTS AND WORK OUT THE MAP DIMENSIONS
        xmin, xmax, ymin, ymax = self.activesim.get_project_boundary_info("mapextents")
        mapwidth = xmax - xmin      # width of the map [m]
        mapheight = ymax - ymin     # height of map [m]

        Amap_rect = mapwidth * mapheight    # Total area of the rectangular extents [m]
        if self.blocksize_auto:     # AUTO-SIZE Blocks
            bs = ubmethods.autosize_blocks(mapwidth, mapheight)
            self.final_bs = bs
        else:
            bs = self.blocksize
            self.final_bs = bs

        self.notify("Map Width [km] = "+str(mapwidth/1000.0))
        self.notify("Map Height [km] = "+str(mapheight/1000.0))
        self.notify("Extent Area WxH [km2] = "+str(Amap_rect/1000000.0))
        self.notify("Final Block Size [m] = "+str(bs))
        self.notify("---===---")

        # START CREATING BLOCKS MAP
        self.notify("Creating Blocks Map!")

        # ADJUST SIMULATION AREA DIMENSIONS
        blocks_wide = int(math.ceil(mapwidth / float(bs)))      # To figure out how many blocks wide and tall, we use
        blocks_tall = int(math.ceil(mapheight / float(bs)))     # math.ceil(), which rounds the number up.
        numblocks = blocks_wide * blocks_tall

        self.notify("Blocks wide: "+str(blocks_wide))
        self.notify("Blocks tall: "+str(blocks_tall))
        self.notify("Total number of Blocks: "+str(numblocks))

        # CBD DISTANCE CALCULATIONS [TO DO]
        # Look up long and lat of CBD if need to be considered
        if self.considerCBD:        # [TO DO]
            # Grab CBD Coordinates and transform to the local coordinate system
            pass

        if self.marklocation:
            # Mark locations on the map
            pass

        # MAP ATTRIBUTES - CREATE THE FIRST UBCOMPONENT() to save off basic map attributes.
        map_attr = ubdata.UBComponent()
        map_attr.add_attribute("xllcorner", xmin)       # The geographic coordinate x-pos of the actual map
        map_attr.add_attribute("yllcorner", ymin)       # The geographic coordinate y-pos of the actual map
        map_attr.add_attribute("Neigh_Type", nhd_type)
        map_attr.add_attribute("spatialmetrics", self.spatialmetrics)
        map_attr.add_attribute("considerCBD", self.considerCBD)
        map_attr.add_attribute("patchdelin", self.patchdelin)  # Optional with Blocks and Hexes

        # Attributes for Block-based Representation
        map_attr.add_attribute("NumBlocks", numblocks)
        map_attr.add_attribute("BlocksWide", blocks_wide)
        map_attr.add_attribute("BlocksTall", blocks_tall)  # Height of simulation area in # of blocks
        map_attr.add_attribute("BlockSize", bs)  # Size of block [m]

        self.scenario.add_asset("MapAttributes", map_attr)

        # --- SECTION 2 - DRAW THE MAP OF BLOCKS AND DETERMINE ACTIVE AND INACTIVE BLOCKS , NEIGHBOURHOODS ---
        # Get the coordinates for the boundary of the map, this is used to check if the Block is active or inactive
        boundarygeom = self.activesim.get_project_boundary_info("coordinates")
        boundarygeom_zeroorigin = []    # Contains the polygon's coordinates shifted to the zero origin
        for coord in boundarygeom:      # Shift the map to (0,0) origin
            boundarygeom_zeroorigin.append(( coord[0] - xmin, coord[1] - ymin))
        boundarypoly = Polygon(boundarygeom_zeroorigin)     # Test intersect with Block Polygon later using

        blockIDcount = 1    # Counter for BlockID, initialized here
        blockslist = []
        self.notify("Creating Block Geometry...")
        for y in range(blocks_tall):        # Loop across the number of blocks tall and blocks wide
            for x in range(blocks_wide):
                # self.notify("Current BLOCK ID: "+str(blockIDcount))

                # - STEP 1 - CREATE BLOCK GEOMETRY
                current_block = self.create_block_face(x, y, bs, blockIDcount, boundarypoly)
                if current_block is None:
                    blockIDcount += 1  # Increase the Block ID Count by one
                    continue

                xcentre = x * bs + 0.5 * bs
                ycentre = y * bs + 0.5 * bs

                xorigin = x * bs
                yorigin = y * bs

                current_block.add_attribute("CentreX", xcentre)    # ATTRIBUTE: geographic information
                current_block.add_attribute("CentreY", ycentre)
                current_block.add_attribute("OriginX", xorigin)
                current_block.add_attribute("OriginY", yorigin)
                current_block.add_attribute("Status", 1)    # Start with Status = 1 by default

                self.scenario.add_asset("BlockID"+str(blockIDcount), current_block)     # Add the asset to the scenario
                blockslist.append(current_block)
                blockIDcount += 1       # Increase the Block ID Count by one

        # - STEP 2 - GET BASIC RASTER DATA SETS
        # Depending on what's available, certain options can be chosen
        #   - Land use: + population, will allow the model to do urban planning
        #   - Elevation: will allow the model to do Flowpath delineation
        self.notify("Loading Basic Input Maps")

        # STEP 2.1 :: Load Land Use Map
        if self.landuse_map:
            lu_dref = self.datalibrary.get_data_with_id(self.landuse_map)       # Retrieve the land use data reference
            fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
            self.notify("Loading: "+str(fullfilepath))
            landuseraster = ubspatial.import_ascii_raster(fullfilepath, self.landuse_map)
            self.notify("Load Complete!")
            landuse_offset = ubspatial.calculate_offsets(landuseraster, map_attr)
            luc_res = landuseraster.get_cellsize()
            csc = int(bs / luc_res)  # csc = cell selection count - knowing how many cells wide and tall

            # STEP 2.2 :: Assign land use to Blocks
            for i in range(len(blockslist)):
                current_block = blockslist[i]
                col_origin = int(current_block.get_attribute("OriginX") / luc_res)
                row_origin = int(current_block.get_attribute("OriginY") / luc_res)
                lucdatamatrix = landuseraster.get_data_square(col_origin, row_origin, csc, csc)

                # STEP 2.2.1 - Tally Frequency of Land uses
                landclassprop, activity = self.calculate_frequency_of_lu_classes(lucdatamatrix)

                # print current_block.get_attribute("BlockID"), "LUC Props: ", landclassprop
                if activity == 0:
                    blockstatus = 0
                else:
                    blockstatus = 1

                current_block.set_attribute("Status", blockstatus)
                current_block.add_attribute("Active", activity)

                # Land use proportions in block (multiply with block area to get Area
                current_block.add_attribute("pLU_RES", landclassprop[0])    # RES = Residential
                current_block.add_attribute("pLU_COM", landclassprop[1])    # COM = Commercial
                current_block.add_attribute("pLU_ORC", landclassprop[2])    # ORC = Mixed Office/Res Development
                current_block.add_attribute("pLU_LI", landclassprop[3])     # LI = Light Industry
                current_block.add_attribute("pLU_HI", landclassprop[4])     # HI = Heavy Industry
                current_block.add_attribute("pLU_CIV", landclassprop[5])    # CIV = Civic
                current_block.add_attribute("pLU_SVU", landclassprop[6])    # SVU = Service & Utility Land
                current_block.add_attribute("pLU_RD", landclassprop[7])     # RD = Road
                current_block.add_attribute("pLU_TR", landclassprop[8])     # TR = Transport Facility
                current_block.add_attribute("pLU_PG", landclassprop[9])     # PG = Parks & Garden
                current_block.add_attribute("pLU_REF", landclassprop[10])   # REF = Reserves & Floodways
                current_block.add_attribute("pLU_UND", landclassprop[11])   # UND = Undeveloped
                current_block.add_attribute("pLU_NA", landclassprop[12])    # NA = Unclassified
                map_attr.set_attribute("HasLUC", 1)

                # STEP 2.2.2 - Calculate Spatial Metrics
                if self.spatialmetrics:     # Using the land class proportions
                    richness = self.calculate_metric_richness(landclassprop)
                    shdiv, shdom, sheven = self.calculate_metric_shannon(landclassprop, richness)
                    current_block.add_attribute("Rich", richness)
                    current_block.add_attribute("ShDiv", shdiv)
                    current_block.add_attribute("ShDom", shdom)
                    current_block.add_attribute("ShEven", sheven)
                    map_attr.add_attribute("HasSPATIALMETRICS", 1)

                # STEP 2.2.3 - Delineate Patches if necessary
                if self.patchdelin:
                    blockpatches = ubmethods.patchdelin_landscape_patch_delineation(lucdatamatrix,
                                                                                    landuseraster.get_nodatavalue())
                    for p in range(len(blockpatches)):
                        if blockpatches[p]["Landuse"] == landuseraster.get_nodatavalue():
                            continue
                        patchxy = (blockpatches[p]["Centroid_xy"][0] * luc_res + current_block.get_attribute("OriginX"),
                                   blockpatches[p]["Centroid_xy"][1] * luc_res + current_block.get_attribute("OriginY"))
                        # Points X and Y are based on the Centroid, calculated

                        patch_attr = ubdata.UBVector(patchxy)
                        patch_attr.add_attribute("PatchID", blockpatches[p]["PatchID"])   # PatchID counts from 1 to N
                        patch_attr.add_attribute("PatchIndices", blockpatches[p]["PatchIndices"])
                        patch_attr.add_attribute("Landuse", blockpatches[p]["Landuse"])
                        patch_attr.add_attribute("CentroidX", patchxy[0])
                        patch_attr.add_attribute("CentroidY", patchxy[1])
                        patch_attr.add_attribute("AspRatio", blockpatches[p]["AspRatio"])
                        patch_attr.add_attribute("PatchSize", blockpatches[p]["PatchSize"])
                        patch_attr.add_attribute("PatchArea", blockpatches[p]["PatchSize"] * luc_res)

                        # Save the patch to the scenario as B#_PatchID#
                        bID = current_block.get_attribute("BlockID")
                        patch_attr.add_attribute("BlockID", bID)
                        self.scenario.add_asset("B"+str(bID)+"_PatchID"+str(blockpatches[p]["PatchID"]), patch_attr)
        else:
            landuseraster = None    # Indicate that the simulation has no land use data, limits what can be done
            map_attr.set_attribute("HasLUC", 0)
            map_attr.add_attribute("HasSPATIALMETRICS", 0)

        # STEP 2.3 :: Load Population Map
        if self.population_map:
            pop_dref = self.datalibrary.get_data_with_id(self.population_map)   # Retrieve the population data reference
            fullfilepath = pop_dref.get_data_file_path() + pop_dref.get_metadata("filename")
            self.notify("Loading: " + str(fullfilepath))
            populationraster = ubspatial.import_ascii_raster(fullfilepath, self.population_map)
            self.notify("Load Complete!")
            population_offset = ubspatial.calculate_offsets(populationraster, map_attr)
            pop_res = populationraster.get_cellsize()
            csc = int(bs / pop_res)  # csc = cell selection count - knowing how many cells wide and tall

            # STEP 2.4 :: ASSIGN POPULATION TO BLOCKS
            for i in range(len(blockslist)):
                current_block = blockslist[i]
                col_origin = int(current_block.get_attribute("OriginX") / pop_res)
                row_origin = int(current_block.get_attribute("OriginY") / pop_res)
                popdatamatrix = populationraster.get_data_square(col_origin, row_origin, csc, csc)

                # STEP 3.4.1 - Tally up total population
                popfactor = 1.0
                if pop_dref.get_metadata("sub") == "Density":
                    popfactor = (float(pop_res) * float(pop_res)) / 10000.0   # Area of a single cell (persons/ha)
                elif pop_dref.get_metadata("sub") == "Count":
                    popfactor = 1.0   # No multiplication

                pop_values = popdatamatrix.flatten()    # Flatten to a single array
                pop_values[pop_values == populationraster.get_nodatavalue()] = 0    # Remove all no-data values
                total_population = float(sum(pop_values) * popfactor)
                #
                # pop_values = 0
                # for row in range(len(popdatamatrix)):
                #     for col in range(len(popdatamatrix[0])):
                #         if popdatamatrix[row, col] == populationraster.get_nodatavalue():
                #             continue
                #         else:
                #             total_population += (float(popdatamatrix[row, col]) * popfactor)

                current_block.add_attribute("Population", total_population)
                map_attr.add_attribute("HasPOP", 1)
        else:
            populationraster = None     # Indicates that the simulation has no population data, limits features
            map_attr.set_attribute("HasPOP", 0)

        # STEP 2.5 :: Load Elevation Map
        if self.elevation_map:
            elev_dref = self.datalibrary.get_data_with_id(self.elevation_map)     # Retrieves the elevation data ref
            fullfilepath = elev_dref.get_data_file_path() + elev_dref.get_metadata("filename")
            self.notify("Loading: " + str(fullfilepath))
            elevationraster = ubspatial.import_ascii_raster(fullfilepath, self.elevation_map)
            self.notify("Load Complete!")
            elevation_offset = ubspatial.calculate_offsets(elevationraster, map_attr)
            elev_res = elevationraster.get_cellsize()
            csc = int(bs / elev_res)

            # STEP 2.6 :: ASSIGN ELEVATION TO BLOCKS
            for i in range(len(blockslist)):
                current_block = blockslist[i]
                col_origin = int(current_block.get_attribute("OriginX") / elev_res)
                row_origin = int(current_block.get_attribute("OriginY") / elev_res)
                elevdatamatrix = elevationraster.get_data_square(col_origin, row_origin, csc, csc)

                # STEP 2.6.1 - Calculate elevation metrics for the Block
                elevationpoints = []
                for row in range(len(elevdatamatrix)):
                    for col in range(len(elevdatamatrix[0])):
                        if elevdatamatrix[row, col] == elevationraster.get_nodatavalue():
                            continue
                        else:
                            elevationpoints.append(float(elevdatamatrix[row, col]))
                if len(elevationpoints) == 0:
                    current_block.set_attribute("Status", 0)
                else:
                    current_block.set_attribute("Status", 1)
                    current_block.add_attribute("AvgElev", sum(elevationpoints)/max(float(len(elevationpoints)), 1.0))
                    current_block.add_attribute("MaxElev", max(elevationpoints))
                    current_block.add_attribute("MinElev", min(elevationpoints))
                    map_attr.add_attribute("HasELEV", 1)

                # STEP 2.6.2 - Map elevation data onto Block Patches
                pass

        else:
            elevationraster = None  # Indicates that the simulation has no elevation data, many water features disabled
            map_attr.set_attribute("HasELEV", 0)

        # - STEP 3 - FIND BLOCK NEIGHBOURHOOD
        self.notify("Establishing neighbourhoods")
        for i in range(len(blockslist)):  # Loop across current Blocks
            curblock = blockslist[i]
            if curblock.get_attribute("Status") == 0:
                continue    # If the block has zero status, don't consider

            curblock_id = curblock.get_attribute("BlockID")
            nhd = []
            for j in range(len(blockslist)):  # Loop across blocks again
                comp_block_id = blockslist[j].get_attribute("BlockID")
                if comp_block_id == curblock_id or blockslist[j].get_attribute("Status") == 0:
                    # If the IDs are identical or the Block has zero status, then skip
                    continue
                if nhd_type == 8:  # 8 neighbours, search based on points
                    if curblock.shares_geometry(blockslist[j], "points"):
                        nhd.append(comp_block_id)
                elif nhd_type == 4:  # 4 neighbours, search based on edges
                    if curblock.shares_geometry(blockslist[j], "edges"):
                        nhd.append(comp_block_id)
            curblock.add_attribute("Neighbours", nhd)  # ATTRIBUTE: neighbourhood type<list> - [ Block IDs ]

        # - STEP 4 - Assign Municipal Regions and Suburban Regions to Blocks
        municipalities = []
        self.notify("Loading Municipality Map")
        if self.include_geopolitical:                       # LOAD MUNICIPALITY MAP
            map_attr.add_attribute("HasGEOPOLITICAL", 1)
            geopol_map = self.datalibrary.get_data_with_id(self.geopolitical_map)
            fullfilepath = geopol_map.get_data_file_path() + geopol_map.get_metadata("filename")
            municipalities = ubspatial.import_polygonal_map(fullfilepath, "native", "Municipality",
                                                            (map_attr.get_attribute("xllcorner"),
                                                             map_attr.get_attribute("yllcorner")))
            for i in range(len(municipalities)):
                self.scenario.add_asset(municipalities[i].get_attribute("Map_Naming"), municipalities[i])
        else:
            map_attr.add_attribute("HasGEOPOLITICAL", 0)

        suburbs = []
        self.notify("Loading Suburb Map")
        if self.include_suburb:                             # LOAD SUBURBAN MAP
            map_attr.add_attribute("HasSUBURBS", 1)
            suburb_map = self.datalibrary.get_data_with_id(self.suburban_map)
            fullfilepath = suburb_map.get_data_file_path() + suburb_map.get_metadata("filename")
            suburbs = ubspatial.import_polygonal_map(fullfilepath, "native", "Suburb",
                                                     (map_attr.get_attribute("xllcorner"),
                                                      map_attr.get_attribute("yllcorner")))
            for i in range(len(suburbs)):
                self.scenario.add_asset(suburbs[i].get_attribute("Map_Naming"), suburbs[i])
        else:
            map_attr.add_attribute("HasSUBURBS", 0)

        # Future [TO DO] Catchment Map

        # Check intersection with blocks - assign the LGA and suburb based on the Block Centroid
        for i in range(len(blockslist)):
            current_block = blockslist[i]
            coordinates = current_block.get_points()
            coordinates = [c[:2] for c in coordinates]
            blockpoly = Polygon(coordinates)

            # Keep searching (search = 1), block Centroid within municipality and suburb? Until found (search = 0)
            intersectarea = 0
            intersectname = ""
            for m in municipalities:
                featpoly = Polygon(m.get_points())
                if not featpoly.intersects(blockpoly):  # If there is no intersection...
                    continue
                newisectionarea = featpoly.intersection(blockpoly).area
                if newisectionarea > intersectarea:
                    intersectarea = newisectionarea
                    intersectname = m.get_attribute(self.geopolitical_attref)

            if intersectname != "" and intersectarea > 0:
                current_block.add_attribute("Region", intersectname)
            else:
                current_block.add_attribute("Region", "Unassigned")

            intersectarea = 0
            intersectname = ""
            for m in suburbs:
                featpoly = Polygon(m.get_points())
                if not blockpoly.intersects(featpoly):
                    continue
                newisectionarea = blockpoly.intersection(featpoly).area
                if newisectionarea > intersectarea:
                    intersectarea = newisectionarea
                    intersectname = m.get_attribute(self.suburban_attref)

            if intersectname != "" and intersectarea > 0:
                current_block.add_attribute("Suburb", intersectname)
            else:
                current_block.add_attribute("Suburb", "Unassigned")

        # - STEP 5 - Load Rivers and Lakes, assign to Blocks and calculate closest distance
        if self.include_rivers:
            #DO stuff
            pass
        else:
            map_attr.add_attribute("HasRIVERS", 0)

        if self.include_lakes:
            #DO Stuff
            pass
        else:
            map_attr.add_attribute("HasLAKES", 0)

        # - STEP 6 - Delineate Flow Paths and Drainage Basins
        if map_attr.get_attribute("HasELEV"):
            # Delineate flow paths
            if self.dem_smooth:
                self.perform_smooth_dem(blockslist)

            self.delineate_flow_paths(blockslist, map_attr)     # Delineates the flow directions
            totalbasins = self.delineate_basin_structures(blockslist)   # Delineates the sub-catchments

            # Write details to map attributes
            map_attr.add_attribute("TotalBasins", totalbasins)
            map_attr.add_attribute("HasFLOWPATHS", 1)
        else:
            map_attr.add_attribute("HasFLOWPATHS", 0)

        # - STEP 7 - Spatial Connectivity
        # 7.1 - Open Space Distances
        # 7.2 - Open Space Network
        # 7.3 - Sewer and Water Supply Systems (COMING SOON) [TO DO]

        # - CLEAN-UP - RESET ALL VARIABLES FOR GARBAGE COLLECTOR
        self.notify("End of Delinblocks")
        return False

    # ------------------------------------------------
    # |-    ADDITIONAL MODULE FUNCTIONS             -|
    # ------------------------------------------------
    def create_block_flow_hashtable(self, blockslist):
        """Creates a hash table of BlockIDs for quick lookup, this allows the basin delineation algorithm to rapidly
        delineate the sub-catchment

        :param blockslist: the list of UBVector() instances of all blocks in the map
        :return: a 2D list [ [upstreamID], [downstreamID] ]
        """
        hash_table = [[], []]     # COL#1: BlockID (upstream), COL#2: BlockID (downstream)
        for i in range(len(blockslist)):
            current_block = blockslist[i]
            current_id = current_block.get_attribute("BlockID")
            if current_block.get_attribute("Status") == 0:
                continue
            hash_table[0].append(int(current_id))
            hash_table[1].append(int(current_block.get_attribute("downID")))    # [ID or -2]
        return hash_table

    def delineate_basin_structures(self, blockslist):
        """Delineates sub-basins across the entire blocksmap specified by the collection of blocks in 'blockslist'.
        Returns the number of sub-basins in the map, but also writes BasinID information to each Block. Delineation is
        carried out by creating a hash table of BlockID and downstream ID.

        Each block is scanned and all its upstream and downstream Block IDs identified, each is also assigned a
        BasinID.

        :param blocklist: the list [] of UBVector() instances that represent Blocks
        :return: number of total basins. Also writes the "BasinID" attribute to each Block.
        """
        hash_table = self.create_block_flow_hashtable(blockslist)    # Start by creating a hash tables
        basin_id = 0    # Set Basin ID to zero, it will start counting up as soon as basins are found

        for i in range(len(blockslist)):    # Loop  across all Blocks
            current_block = blockslist[i]
            if current_block.get_attribute("Status") == 0:
                continue    # Skip if Status = 0

            # Check if the Block is a single-basin Block
            current_id = current_block.get_attribute("BlockID")
            if current_id not in hash_table[1]:                 # If the current Block not downstream of something...
                current_block.add_attribute("UpstrIDs", [])     # ...then it has NO upstream IDs (empty list)
                if current_id in hash_table[0]:                 # ... if it is in the first column of the hash table
                    if hash_table[1][hash_table[0].index(current_id)] == -2:    # if its second column is -2
                        self.notify("Found a single block basin at BlockID"+str(current_id))
                        basin_id += 1   # Then we have found a single-block Basin
                        current_block.add_attribute("BasinID", basin_id)
                        current_block.add_attribute("DownstrIDs", [])
                        current_block.add_attribute("Outlet", 1)
                        continue

            # Search the current Block for its upstream IDs
            upstream_ids = [current_id]         # Otherwise current ID DOES have upstream blocks
            for uid in upstream_ids:             # Begin scanning! Note that upstream_ids will grow in length!
                for j in range(len(hash_table[1])):
                    if uid == hash_table[1][j]:
                        if hash_table[0][j] not in upstream_ids:    # Only want unique upstream_ids!
                            upstream_ids.append(hash_table[0][j])   # Slowly append more IDs to the hash_table

            # Once scan is complete, remove the current Block's ID from the list as it is NOT upstream of itself.
            upstream_ids.remove(current_id)
            self.notify("BlockID"+str(current_id)+" Upstream: "+str(upstream_ids))
            current_block.add_attribute("UpstrIDs", upstream_ids)

            # Repeat the whole process now for the downstream IDs
            downstream_ids = [current_id]
            for uid in downstream_ids:
                for j in range(len(hash_table[0])):
                    if uid == hash_table[0][j]:
                        if hash_table[1][j] not in downstream_ids:
                            downstream_ids.append(hash_table[1][j])

            # Once scan is complete, remove the current Block's ID from the list as it is NOT downstream of itself.
            downstream_ids.remove(current_id)
            # downstream_ids.remove(-2)   # Also remove the -2, which is specified if the Outlet Block is found
            self.notify("BlockID"+str(current_id)+" DownstreamL "+str(downstream_ids))
            current_block.add_attribute("DownstrIDs", downstream_ids)

            print "Finding Basins now!"

            # Now assign Basin IDs, do this if the current Block has downstream ID -2
            if hash_table[1][hash_table[0].index(current_id)] == -2:    # If the block is an outlet
                print "Found a basin outlet at BlockID" + str(current_id)
                self.notify("Found a basin outlet at BlockID"+str(current_id))
                basin_id += 1
                current_block.add_attribute("BasinID", basin_id)    # Set the current Basin ID
                current_block.add_attribute("Outlet", 1)            # Outlet = TRUE at current Block
                for j in upstream_ids:
                    upblock = self.scenario.get_asset_with_name("BlockID"+str(int(j)))
                    upblock.add_attribute("BasinID", basin_id)      # Assign basin ID to all upstream blocks
                    upblock.add_attribute("Outlet", 0)              # Upstream blocks are NOT outlets!

        self.notify("Total Basins in the Case Study: "+str(basin_id))
        return basin_id     # The final count indicates how many basins were found

    def delineate_flow_paths(self, blockslist, map_attr):
        """Delineates the flow paths according to the chosen method and saves the information to the blocks.

        :param blockslist: a list [] of UBVector instances representing the Blocks
        :param map_attr:  the global map attributes object
        :return: all data is saved to the UBVector instances as new Block data.
        """
        sink_ids = []
        river_ids = []
        lake_ids = []

        for i in range(len(blockslist)):
            current_block = blockslist[i]
            current_blockid = current_block.get_attribute("BlockID")

            # SKIP CONDITION 1 - Block has zero status
            if current_block.get_attribute("Status") == 0:
                continue

            # SKIP CONDITION 2 - Block already contains a river
            if current_block.get_attribute("HasRiver"):
                current_block.add_attribute("downID", -2)   # Immediately assign it the -2 value for downID
                river_ids.append(current_blockid)
                continue

            # SKIP CONDITION 3 - Block contains a lake
            if current_block.get_attribute("HasLake"):
                current_block.add_attribute("downID", -2)  # Immediately assign it the -2 value for downID
                lake_ids.append(current_blockid)
                continue

            z = current_block.get_attribute("AvgElev")
            neighbours_z = self.scenario.retrieve_attribute_value_list("Block", "AvgElev",
                                                                       current_block.get_attribute("Neighbours"))
            # print "Neighbour Z: ", neighbours_z

            # Find the downstream block unless it's a sink
            if self.flowpath_method == "D8":
                flow_id, max_zdrop = self.find_downstream_d8(z, neighbours_z)
            elif self.flowpath_method == "DI" and self.neighbourhood == "M":
                # Only works for the Moore neighbourhood
                flow_id, max_zdrop = self.find_downstream_dinf(z, neighbours_z)
            else:
                self.flowpath_method = "D8"     # Reset to D8 by default
                flow_id, max_zdrop = self.find_downstream_d8(z, neighbours_z)

            if flow_id == -9999:     # if no flowpath has been found
                sink_ids.append(current_blockid)
                downstream_id = -1  # Block is a possible sink. if -2 --> block is a catchment outlet
            else:
                downstream_id = flow_id

            # Grab distances / slope between two Block IDs
            if flow_id == -9999:
                avg_slope = 0
            else:
                down_block = self.scenario.get_asset_with_name("BlockID"+str(downstream_id))
                dx = current_block.get_attribute("CentreX") - down_block.get_attribute("CentreX")
                dy = current_block.get_attribute("CentreY") - down_block.get_attribute("CentreY")
                dist = float(math.sqrt((dx * dx) + (dy * dy)))
                avg_slope = max_zdrop / dist

            # Add attributes
            current_block.add_attribute("downID", downstream_id)
            current_block.add_attribute("max_dz", max_zdrop)
            current_block.add_attribute("avg_slope", avg_slope)
            current_block.add_attribute("h_pond", 0)    # Only for sink blocks will height of ponding h_pond > 0

            # Draw Networks
            if downstream_id != -1 and downstream_id != 0:
                network_link = self.draw_flow_path(current_block, 1)
                self.scenario.add_asset("FlowID"+str(current_blockid), network_link)

        # Unblock the Sinks
        self.unblock_sinks(sink_ids)

        if map_attr.get_attribute("HasRIVER"):
            self.connect_river_blocks(blockslist)   # [TO DO]
        return True

    def connect_river_blocks(self, blockslist):
        """Scans the blocks for those containing a river system and connects them based on adjacency and river
        rules.

        :param blockslist: the list () of block UBVector instances.
        :return: Each block is given a new attribute specifying the Block containing a river that it drains into
        """
        pass    # Scan block list, if HasRiver true, then check neighbours, if they have river and river name is
                # identical, connect, otherwise specify -1 as unconnected
        return True # [TO DO]

    def unblock_sinks(self, sink_ids):
        """Runs the algorithm for scanning all sink blocks and attempting to find a flowpath beyond them.
        This function may also identify certain sinks as definitive catchment outlets.

        :param blockslist: the list [] of block UBVector instances
        :param sink_ids: a list of BlockIDs where a sink is believe to exist based on the flowpath method.
        :return: adds new assets to the scenario if a flowpath has been found for the sinks
        """
        for i in range(len(sink_ids)):
            current_sinkid = sink_ids[i]
            self.notify("Attemtping to unblock flow from BlockID"+str(current_sinkid))
            current_block = self.scenario.get_asset_with_name("BlockID"+str(current_sinkid))

            z = current_block.get_attribute("AvgElev")
            nhd = current_block.get_attribute("Neighbours")
            possible_id_drains = []
            possible_id_z = []
            possibility = 0

            for j in nhd:
                nhd_blk = self.scenario.get_asset_with_name("BlockID"+str(j))
                if nhd_blk.get_attribute("Status") == 0:
                    continue    # Continue if nhd block has zero status

                nhd_downid = nhd_blk.get_attribute("downID")
                if nhd_downid not in [current_sinkid, -1] and nhd_downid not in nhd:
                    possible_id_drains.append(j)
                    possible_id_z.append(nhd_blk.get_attribute("AvgElev") - z)
                    possibility += 1

            if possibility > 0:
                sink_path = min(possible_id_z)
                sink_to_id = possible_id_drains[possible_id_z.index(sink_path)]

                current_block.set_attribute("downID", sink_to_id)   # Overwrite -1 to new ID
                current_block.set_attribute("h_pond", sink_path)    # If ponding depth > 0, then there was a sink
                network_link = self.draw_flow_path(current_block, "Ponded")
                self.scenario.add_asset("FlowID" + str(current_block.get_attribute("BlockID")), network_link)
            else:
                current_block.set_attribute("downID", -2)   # signifies that Block is an outlet
        return True

    def draw_flow_path(self, current_block, flow_type):
        """Creates the flowpath geometry and returns a line asset, which can be saved to the scenario.

        :param current_block: current ID of the block that the flowpath is being drawn for
        :param flow_type: type of flowpath e.g. "Regular", "Ponded"
        :return: UBVector() instance of a network link
        """
        current_id = current_block.get_attribute("BlockID")
        downstream_id = current_block.get_attribute("downID")
        down_block = self.scenario.get_asset_with_name("BlockID"+str(downstream_id))

        x_up = current_block.get_attribute("CentreX")
        y_up = current_block.get_attribute("CentreY")
        z_up = current_block.get_attribute("AvgElev")
        up_point = (x_up, y_up, z_up)

        x_down = down_block.get_attribute("CentreX")
        y_down = down_block.get_attribute("CentreY")
        z_down = down_block.get_attribute("AvgElev")
        down_point = (x_down, y_down, z_down)

        network_link = ubdata.UBVector((up_point, down_point))
        network_link.determine_geometry((up_point, down_point))
        network_link.add_attribute("FlowID", current_id)
        network_link.add_attribute("BlockID", current_id)
        network_link.add_attribute("DownID", downstream_id)
        network_link.add_attribute("Z_up", z_up)
        network_link.add_attribute("Z_down", z_down)
        network_link.add_attribute("max_zdrop", current_block.get_attribute("max_dz"))
        network_link.add_attribute("LinkType", flow_type)
        network_link.add_attribute("AvgSlope", current_block.get_attribute("avg_slope"))
        network_link.add_attribute("h_pond", current_block.get_attribute("h_pond"))
        return network_link

    def find_downstream_d8(self, z, nhd_z):
        """Uses the standard D8 method to find the downstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [NHD_Z - Z] and is
        negative if the neighbouring Block has a lower elevation than the central Block.

        :param z: elevation of the current central Block
        :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return: down_id: block ID that water drains to, min(dz) the largest elevation difference.
        """
        dz = []
        # print nhd_z
        for i in range(len(nhd_z[1])):
            dz.append(nhd_z[1][i] - z)     # Calculate the elevation difference
        if min(dz) < 0:    # If there is a drop in elevation - this also means the area cannot be flat!
            down_id = nhd_z[0][dz.index(min(dz))]    # The ID corresponds to the minimum elevation difference
        else:
            down_id = -9999 # Otherwise there is a sink in the current Block
        return down_id, min(dz)

    def find_downstream_dinf(self, z, nhd_z):
        """Adapted D-infinity method to only direct water in one direction based on the steepest slope
        of the 8 triangular facets surrounding a Block's neighbourhood and a probabilistic choice weighted
        by the propotioning of flow. This is the stochastic option of flowpath delineation for UrbanBEATS
        and ONLY works with the Moore neighbourhood.

        :param z: elevation of the current central Block
        :param nhd_z: :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return:
        """
        pass    # [TO DO]

        # FROM LEGACY CODE
        # facetdict = {}  # Stores all the information about the 8 facets
        # facetdict["e1"] = ["E", "N", "N", "W", "W", "S", "S", "E"]
        # facetdict["e2"] = ["NE", "NE", "NW", "NW", "SW", "SW", "SE", "SE"]
        # facetdict["ac"] = [0, 1, 1, 2, 2, 3, 3, 4]
        # facetdict["af"] = [1, -1, 1, -1, 1, -1, 1, -1]
        # cardin = {"E": 0, "NE": 1, "N": 2, "NW": 3, "W": 4, "SW": 5, "S": 6, "SE": 7}
        #
        # e0 = currentZ  # CONSTANT PARAMETERS (because of constant block grid and centre point)
        # d1 = blocksize
        # d2 = d1
        # facetangles = [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi, 5 * math.pi / 4, 3 * math.pi / 2,
        #                7 * math.pi / 4]
        #
        # # Re-sort the neighbours matrix based on polar angle
        # sortedneighb = [neighboursZ[3], neighboursZ[4], neighboursZ[0], neighboursZ[5], neighboursZ[2], neighboursZ[7],
        #                 neighboursZ[1], neighboursZ[6]]
        # rmatrix = []
        # smatrix = []
        #
        # for i in range(len(sortedneighb)):  # Calculate slopes of all 8 facets
        #     currentfacet = i
        #
        #     e1 = sortedneighb[
        #         cardin[facetdict["e1"][currentfacet]]]  # e1 elevation:  (1) get cardinal direction from dictionary,
        #     #               (2) get the index from cardin and
        #     e2 = sortedneighb[cardin[facetdict["e2"][currentfacet]]]  # (3) get the value from neighbz
        #
        #     ac = facetdict["ac"][currentfacet]
        #     af = facetdict["af"][currentfacet]
        #
        #     s1 = (e0 - e1) / d1
        #     s2 = (e1 - e2) / d2
        #     r = math.atan(s2 / s1)
        #     s = math.sqrt(math.pow(s1, 2) + math.pow(s2, 2))
        #
        #     if r < 0:
        #         r = 0
        #         s = s1
        #     elif r > math.atan(d2 / d1):
        #         r = math.atan(d2 / d1)
        #         s = (e0 - e2) / math.sqrt(math.pow(d1, 2) + math.pow(d2, 2))
        #
        #     rmatrix.append(r)
        #     smatrix.append(s)
        #
        # # Find the maximum slope and get the angle
        # rmax = max(rmatrix)
        # rg = af * rmax + ac * math.pi / 2.0
        #
        # # Find the facet
        # for i in range(len(facetangles)):
        #     if rg > facetangles[i]:
        #         continue
        #     else:
        #         facet = i - 1
        #         theta1 = facetangles[i - 1]
        #         theta2 = facetangles[i]
        # # Adjust angles based on rg to get proportions
        # alpha1 = rg - theta1
        # alpha2 = theta2 - rg
        # p1 = alpha1 / (alpha1 + alpha2)
        # p2 = alpha2 / (alpha2 + alpha1)
        #
        # print "Proportioned Flows:", p1, p2
        #
        # if rand.random() < p1:
        #     choice = p1
        #     directionfacet = int(theta1 / (math.pi / 4))
        # else:
        #     choice = p2
        #     directionfacet = int(theta2 / (math.pi / 4))
        #
        # print "Choice:", choice
        #
        # direction = neighboursZ.index(sortedneighb[directionfacet - 1])
        # return direction, max_Zdrop
        return True

    def perform_smooth_dem(self, blockslist):
        """Performs a smoothing of the DEM on the Blocks map. This is only necessary if the DEM is quite
        tricky to work with and flowpaths are not behaving the way you intend for them to behave.

        :param blockslist: a list [] of the block assets in UBVector objects.
        """
        for i in range(len(self.dem_passes)):
            new_elevs = {}
            for b in range(len(blockslist)):
                current_block = blockslist[i]
                elevs = [current_block.get_attribute("Elevation")]
                neighbours = current_block.get_attribute("Neighbours")
                for n in neighbours:
                    ne_block = self.scenario.get_asset_with_name("BlockID"+str(n)).get_attribute("Elevation")
                    elevs.append(ne_block)
                # print elevs
                # print float(sum(elevs)/len(elevs))
                new_elevs[str(current_block.get_attribute("BlockID"))] = float(sum(elevs) / len(elevs))
            for b in range(len(blockslist)):
                blockslist[i].set_attribute("Elevation", new_elevs[str(blockslist[i].get_attribute("BlockID"))])
        return True

    def create_block_face(self, x, y, cs, ID, boundary):
        """Creates the Block Face, the polygon of the block as a UBVector

        :param x: The starting x coordinate (on 0,0 origin)
        :param y: The starting y coordinate (on 0,0 origin)
        :param cs: Block size [m]
        :param ID: the current ID number to be assigned to the Block
        :param boundary: A Shapely polygon object, used to test if the block face intersects
        with it. Also determines whether to save the Block or not.
        :return: UBVector object containing the BlockID attribute and geometry
        """
        # Define points
        n1 = (x * cs, y * cs, 0)        # Bottom left (x, y, z)
        n2 = ((x + 1)*cs, y * cs, 0)    # Bottom right
        n3 = ((x + 1)*cs, (y + 1)*cs, 0)   # Top right
        n4 = (x * cs, (y + 1) * cs, 0)    # Top left

        # Create the Shapely Polygon and test against the boundary to determine active/inactive.
        blockpoly = Polygon((n1[:2], n2[:2], n3[:2], n4[:2]))
        if Polygon.intersects(boundary, blockpoly):
            # Define edges
            e1 = (n1, n2)   # Bottom left to bottom right
            e2 = (n2, n3)   # Bottom right to top right
            e3 = (n3, n4)   # Top right to top left
            e4 = (n4, n1)   # Top left to bottom left

            # Define the UrbanBEATS Vector Asset
            block_attr = ubdata.UBVector((n1, n2, n3, n4, n1), (e1, e2, e3, e4))
            block_attr.add_attribute("BlockID", int(ID))    # ATTRIBUTE: Block Identification
            return block_attr
        else:
            # Block not within boundary, do not return anything
            return None

    def calculate_frequency_of_lu_classes(self, lucdatamatrix):
        """ Tallies the frequency of land use classes within the given Block/Hex. Returns the 'Activity'
        attribute and a list of LUC frequencies.

        :param lucdatamatrix: the two-dimensional matrix extracted from the LU raster UBRaster() object
        :return a list of all 13 classes and their relative proportion, activity, the total data coverage.
        """
        # Step 1 - Order all data entries into a lit of 13 elements
        # Categories: 'RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA'
        lucprop = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_n_luc = 0     # Counts the total elements of valid land use classes i.e. skips counting NODATA
        matrix_size = 0     # Counts total elements in the 2D array
        for i in range(len(lucdatamatrix)):
            for j in range(len(lucdatamatrix[0])):
                matrix_size += 1
                landclass = lucdatamatrix[i, j]     # numpy array
                if int(landclass) == -9999:
                    pass
                else:
                    lucprop[int(landclass) - 1] += 1
                    total_n_luc += 1

        # Step 2 - Convert frequency to proportion
        if total_n_luc == 0:
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0
        for i in range(len(lucprop)):
            lucprop[i] = float(lucprop[i]) / float(total_n_luc)
        activity = float(total_n_luc) / float(matrix_size)
        return lucprop, activity

    def calculate_metric_richness(self, landclassprop):
        """Calculates the Richness metric, which is simply the total number of unique categories in the provided
        land use proportions list

        :param landclassprop: A list [] specifying the relative proportions of land use categories. Sum = 1
        :return: the richness index
        """
        richness = 0
        for i in landclassprop:
            if i != 0:
                richness += 1
        return richness

    def calculate_metric_shannon(self, landclassprop, richness):
        """Calculates the Shannon diversity, dominance and evenness indices based on the proportion of different land
        use classes and the richness.

        :param landclassprop: A list [] specifying the relative proportions of land use categories. Sum = 1
        :param richness: the richness index, which is the number of unique land use classes in the area
        :return: shandiv (Diversity index), shandom (Dominance index) and shaneven (Evenness index)
        """
        if richness == 0:
            return 0, 0, 0

        # Shannon Diversity Index (Shannon, 1948) - measures diversity in categorical data, the information entropy of
        # the distribution: H = -sum(pi ln(pi))
        shandiv = 0
        for sdiv in landclassprop:
            if sdiv != 0:
                shandiv += sdiv * math.log(sdiv)
        shandiv = -1 * shandiv

        # Shannon Dominance Index: The degree to which a single class dominates in the area, 0 = evenness
        shandom = math.log(richness) - shandiv

        # Shannon Evenness Index: Similar to dominance, the level of evenness among the land classes
        if richness == 1:
            shaneven = 1
        else:
            shaneven = shandiv / math.log(richness)

        return shandiv, shandom, shaneven