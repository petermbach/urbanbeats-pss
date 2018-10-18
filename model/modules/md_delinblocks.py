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
        # (1) Parameters for Input Data
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

        # (2) Parameters for Geometric Delineation
        self.create_parameter("geometry_type", STRING, "block or future types of geometry e.g. hex")
        self.create_parameter("blocksize", DOUBLE, "resolution of the discretisation grid")
        self.create_parameter("blocksize_auto", BOOL, "determine resolution automatically?")
        self.create_parameter("neighbourhood", STRING, "type of neighbourhood to use, Moore or vN")
        self.create_parameter("patchdelin", BOOL, "delineate patches?")
        self.create_parameter("spatialmetrics", BOOL, "calculate spatial metrics?")
        self.geometry_type = "BLOCKS"       # BLOCKS, HEXAGONS
        self.blocksize = 500
        self.blocksize_auto = 0
        self.neighbourhood = "M"
        self.patchdelin = 1
        self.spatialmetrics = 1

        # (3) Parameters for Spatial Context
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

        self.create_parameter("include_rivers", BOOL, "include a rivers map into simulation?")
        self.create_parameter("include_lakes", BOOL, "include a ponds and lakes map into simulation?")
        self.create_parameter("calculate_wbdistance", BOOL, "calculate distance to closest water body?")
        self.create_parameter("river_map", STRING, "river map filepath")
        self.create_parameter("lake_map", STRING, "ponds and lake map filepath")
        self.create_parameter("flowpath_method", STRING, "flowpath method to use")
        self.create_parameter("dem_smooth", BOOL, "smooth DEM map before doing flowpath delineation?")
        self.create_parameter("dem_passes", DOUBLE, "number of passes for smoothing")
        self.create_parameter("guide_natural", BOOL, "guide flowpath delineation using pre-loaded natural feature?")
        self.create_parameter("guide_built", BOOL, "guide flowpath delineation using built infrastructure?")
        self.create_parameter("guide_natural_map", STRING, "filepath to natural features map to guide flowpaths")
        self.create_parameter("guide_built_map", STRING, "filepath to built infrastructure map to guide flowpaths")
        self.include_rivers = 0
        self.include_lakes = 0
        self.calculate_wbdistance = 0
        self.river_map = ""
        self.lake_map = ""
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
        else:
            bs = self.blocksize

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

                self.scenario.add_asset("BlockID"+str(blockIDcount), current_block)     # Add the asset to the scenario
                blockslist.append(current_block)
                blockIDcount += 1       # Increase the Block ID Count by one

        # - STEP 2 - FIND BLOCK NEIGHBOURHOOD
        self.notify("Establishing neighbourhoods")
        for i in range(len(blockslist)):    # Loop across current Blocks
            curblock = blockslist[i]
            curblock_id = curblock.get_attribute("BlockID")
            nhd = []
            for j in range(len(blockslist)):    # Loop across blocks again
                comp_block_id = blockslist[j].get_attribute("BlockID")
                if comp_block_id == curblock_id:  # If the IDs are identical, then skip
                    continue
                if nhd_type == 8:  # 8 neighbours, search based on points
                    if curblock.shares_geometry(blockslist[j], "points"):
                        nhd.append(comp_block_id)
                elif nhd_type == 4: # 4 neighbours, search based on edges
                    if curblock.shares_geometry(blockslist[j], "edges"):
                        nhd.append(comp_block_id)
            curblock.add_attribute("Neighbours", nhd)   # ATTRIBUTE: neighbourhood type<list> - [ Block IDs ]

        # - STEP 3 - GET BASIC RASTER DATA SETS
        # Depending on what's available, certain options can be chosen
        #   - Land use: + population, will allow the model to do urban planning
        #   - Elevation: will allow the model to do Flowpath delineation
        self.notify("Loading Basic Input Maps")

        # STEP 3.1 :: Load Land Use Map
        if self.landuse_map:
            lu_dref = self.datalibrary.get_data_with_id(self.landuse_map)       # Retrieve the land use data reference
            fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
            self.notify("Loading: "+str(fullfilepath))
            landuseraster = ubspatial.import_ascii_raster(fullfilepath, self.landuse_map)
            self.notify("Load Complete!")
            landuse_offset = ubspatial.calculate_offsets(landuseraster, map_attr)
            luc_res = landuseraster.get_cellsize()
            csc = int(bs / luc_res)  # csc = cell selection count - knowing how many cells wide and tall

            # STEP 3.2 :: Assign land use to Blocks
            for i in range(len(blockslist)):
                current_block = blockslist[i]
                col_origin = int(current_block.get_attribute("OriginX") / luc_res)
                row_origin = int(current_block.get_attribute("OriginY") / luc_res)
                lucdatamatrix = landuseraster.get_data_square(col_origin, row_origin, csc, csc)

                # STEP 3.2.1 - Tally Frequency of Land uses
                landclassprop, activity = self.calculate_frequency_of_lu_classes(lucdatamatrix)

                # print current_block.get_attribute("BlockID"), "LUC Props: ", landclassprop
                if activity == 0:
                    blockstatus = 0
                else:
                    blockstatus = 1

                current_block.add_attribute("Status", blockstatus)
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

                # STEP 3.2.2 - Calculate Spatial Metrics
                if self.spatialmetrics:     # Using the land class proportions
                    richness = self.calculate_metric_richness(landclassprop)
                    shdiv, shdom, sheven = self.calculate_metric_shannon(landclassprop, richness)
                    current_block.add_attribute("Rich", richness)
                    current_block.add_attribute("ShDiv", shdiv)
                    current_block.add_attribute("ShDom", shdom)
                    current_block.add_attribute("ShEven", sheven)
                    map_attr.add_attribute("HasSPATIALMETRICS", 1)

                # STEP 3.2.3 - Delineate Patches if necessary
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

        # STEP 3.3 :: Load Population Map
        if self.population_map:
            pop_dref = self.datalibrary.get_data_with_id(self.population_map)   # Retrieve the population data reference
            fullfilepath = pop_dref.get_data_file_path() + pop_dref.get_metadata("filename")
            self.notify("Loading: " + str(fullfilepath))
            populationraster = ubspatial.import_ascii_raster(fullfilepath, self.population_map)
            self.notify("Load Complete!")
            population_offset = ubspatial.calculate_offsets(populationraster, map_attr)
            pop_res = populationraster.get_cellsize()
            csc = int(bs / pop_res)  # csc = cell selection count - knowing how many cells wide and tall

            # STEP 3.4 :: ASSIGN POPULATION TO BLOCKS
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

                total_population = 0
                for row in range(len(popdatamatrix)):
                    for col in range(len(popdatamatrix[0])):
                        if popdatamatrix[row, col] == populationraster.get_nodatavalue():
                            continue
                        else:
                            total_population += (float(popdatamatrix[row, col]) * popfactor)

                current_block.add_attribute("Population", total_population)
                map_attr.add_attribute("HasPOP", 1)
        else:
            populationraster = None     # Indicates that the simulation has no population data, limits features
            map_attr.set_attribute("HasPOP", 0)

        # STEP 3.5 :: Load Elevation Map
        if self.elevation_map:
            elev_dref = self.datalibrary.get_data_with_id(self.elevation_map)     # Retrieves the elevation data ref
            fullfilepath = elev_dref.get_data_file_path() + elev_dref.get_metadata("filename")
            self.notify("Loading: " + str(fullfilepath))
            elevationraster = ubspatial.import_ascii_raster(fullfilepath, self.elevation_map)
            self.notify("Load Complete!")
            elevation_offset = ubspatial.calculate_offsets(elevationraster, map_attr)
            elev_res = elevationraster.get_cellsize()
            csc = int(bs / elev_res)

            # STEP 3.6 :: ASSIGN ELEVATION TO BLOCKS
            for i in range(len(blockslist)):
                current_block = blockslist[i]
                col_origin = int(current_block.get_attribute("OriginX") / elev_res)
                row_origin = int(current_block.get_attribute("OriginY") / elev_res)
                elevdatamatrix = elevationraster.get_data_square(col_origin, row_origin, csc, csc)

                # STEP 3.6.1 - Calculate elevation metrics for the Block
                elevationpoints = []
                for row in range(len(elevdatamatrix)):
                    for col in range(len(elevdatamatrix[0])):
                        if elevdatamatrix[row, col] == elevationraster.get_nodatavalue():
                            continue
                        else:
                            elevationpoints.append(float(elevdatamatrix[row, col]))
                current_block.add_attribute("AvgElev", sum(elevationpoints)/max(float(len(elevationpoints)), 1.0))
                current_block.add_attribute("MaxElev", max(elevationpoints))
                current_block.add_attribute("MinElev", min(elevationpoints))
                map_attr.add_attribute("HasELEV", 1)

                # STEP 3.6.2 - Map elevation data onto Block Patches
                pass

        else:
            elevationraster = None  # Indicates that the simulation has no elevation data, many water features disabled
            map_attr.set_attribute("HasELEV", 0)

        # - STEP 4 - Assign Municipal Regions and Suburban Regions to Blocks
        municipalities = []
        self.notify("Loading Municipality Map")
        if self.include_geopolitical:
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
        if self.include_suburb:
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
            #Delineate flow paths
            if self.dem_smooth:
                self.perform_smooth_dem(blockslist)

            self.delineate_flow_paths(blockslist, map_attr)
            # Create hash table
            # Find the basins
            # Write this to the map attributes

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
    def delineate_flow_paths(self, blockslist, map_attr):
        """Delineates the flow paths according to the chosen method and saves the information to the blocks.

        :param blockslist: a list [] of UBVector instances representing the Blocks
        :param map_attr:  the global map attributes object
        :return: all data is saved to the UBVector instances as new Block data.
        """
        pass

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
                print elevs
                print float(sum(elevs)/len(elevs))
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
        richness = 0
        for i in landclassprop:
            if i != 0:
                richness += 1
        return richness

    def calculate_metric_shannon(self, landclassprop, richness):
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

