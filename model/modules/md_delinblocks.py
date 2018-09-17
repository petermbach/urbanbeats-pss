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

        # --- SECTION 1 - PREPARATION FOR CREATING THE BLOCKS MAP BASED ON THE INPUT BOUNDARY MAP ---

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
            cs = ubmethods.autosize_blocks(mapwidth, mapheight)
        else:
            cs = self.blocksize

        self.notify("Map Width [km] = "+str(mapwidth/1000.0))
        self.notify("Map Height [km] = "+str(mapheight/1000.0))
        self.notify("Final Block Size [m] = "+str(cs))
        self.notify("---===---")

        # START CREATING BLOCKS MAP
        self.notify("Creating Blocks Map!")

        # ADJUST SIMULATION AREA DIMENSIONS
        blocks_wide = int(math.ceil(mapwidth / float(cs)))      # To figure out how many blocks wide and tall, we use
        blocks_tall = int(math.ceil(mapheight / float(cs)))     # math.ceil(), which rounds the number up.
        numblocks = blocks_wide * blocks_tall

        self.notify("Blocks wide: "+str(blocks_wide))
        self.notify("Blocks tall: "+str(blocks_tall))
        self.notify("Total number of Blocks: "+str(numblocks))

        # CBD DISTANCE CALCULATIONS [TO DO]
        # Look up long and lat of CBD if need to be considered
        if self.considerCBD:
            # Grab CBD Coordinates and transform to the local coordinate system
            pass

        if self.marklocation:
            # Mark locations on the map
            pass

        # MAP ATTRIBUTES - CREATE THE FIRST UBCOMPONENT() to save off basic map attributes.
        map_attr = ubdata.UBComponent()
        map_attr.add_attribute("NumBlocks", numblocks)
        map_attr.add_attribute("BlocksWide", blocks_wide)
        map_attr.add_attribute("BlocksTall", blocks_tall)  # Height of simulation area in # of blocks
        map_attr.add_attribute("BlockSize", cs)  # Size of block [m]
        map_attr.add_attribute("xllcorner", xmin)       # The geographic coordinate x-pos of the actual map
        map_attr.add_attribute("yllcorner", ymin)       # The geographic coordinate y-pos of the actual map
        map_attr.add_attribute("Neigh_Type", nhd_type)
        map_attr.add_attribute("ConsiderCBD", self.considerCBD)
        map_attr.add_attribute("patchdelin", self.patchdelin)
        map_attr.add_attribute("spatialmetrics", self.spatialmetrics)
        map_attr.add_attribute("considerCBD", self.considerCBD)
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
                block_attr = self.create_block_face(x, y, cs, blockIDcount, boundarypoly)
                if block_attr is None:
                    blockIDcount += 1  # Increase the Block ID Count by one
                    continue

                xcentre = x * cs + 0.5 * cs
                ycentre = y * cs + 0.5 * cs

                xorigin = x * cs
                yorigin = y * cs

                block_attr.add_attribute("CentreX", xcentre)    # ATTRIBUTE: geographic information
                block_attr.add_attribute("CentreY", ycentre)
                block_attr.add_attribute("OriginX", xorigin)
                block_attr.add_attribute("OriginY", yorigin)

                self.scenario.add_asset("BlockID"+str(blockIDcount), block_attr)     # Add the asset to the scenario
                blockslist.append(block_attr)
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
        self.notify("Loading Basic Input Maps")

        # Load Land Use Map
        lu_dref = self.datalibrary.get_data_with_id(self.landuse_map)       # Retrieve the land use data reference
        fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
        self.notify("Loading: "+str(fullfilepath))
        landuseraster = ubspatial.import_ascii_raster(fullfilepath, self.landuse_map)
        self.notify("Load Complete!")
        xllcorner, yllcorner = landuseraster.get_extents()  # Master xll/yll corner - the whole map is based on this

        # x_start = x * cellsinblock
        # y_start = y * cellsinblock
        # cellsinblock = int(cs / inputres)
        #
        # # Load Population Map
        # pop_dref = self.datalibrary.get_data_with_id(self.population_map)   # Retrieve the population data reference
        # fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
        # self.notify("Loading: " + str(fullfilepath))
        # populationraster = ubspatial.import_ascii_raster(fullfilepath, self.population_map)
        # self.notify("Load Complete!")
        # pop_offset = ubspatial.calculate_offsets(landuseraster, populationraster, landuseraster.get_cellsize())
        # # Check Map Offset so that the data can be aligned
        # self.notify("Population map cell offsets: " + str(pop_offset[0]) + "," + str(pop_offset[1]))
        #
        # # Load Elevation Map
        # elev_dref = self.datalibrary.get_data_with_id(self.elevation_map)     # Retrieves the elevation data ref
        # fullfilepath = elev_dref.get_data_file_path() + elev_dref.get_metadata("filename")
        # self.notify("Loading: " + str(fullfilepath))
        # elevationraster = ubspatial.import_ascii_raster(fullfilepath, self.elevation_map)
        # self.notify("Load Complete!")
        # elev_offset = ubspatial.calculate_offsets(landuseraster, elevationraster, landuseraster.get_cellsize())
        # self.notify("Elevation map cell offsets: "+str(elev_offset[0])+","+str(elev_offset[1]))
        #
        # inputres = landuseraster.get_cellsize()
        # width = landuseraster.get_dimensions()[0] * inputres
        # height = landuseraster.get_dimensions()[1] * inputres
        self.notify("Simulation Finished for now")
        return False

    # ------------------------------------------------
    # |-    ADDITIONAL MODULE FUNCTIONS             -|
    # ------------------------------------------------
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
