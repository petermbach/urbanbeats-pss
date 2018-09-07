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

    def run(self):
        """Contains the main algorithm for the module, links with all other functions thereafter. This is called by
        UrbanBEATSSim() simulation's scenario manager depending on which scenario is currently being simulated.

        :return: True upon successful completion
        """
        self.notify("Start Spatial Delineation Module")     # Module start
        rand.seed()     # Seed the random number generator

        # Check the neighbourhood rule and set the number of adjacent cells, nhd_type, accordingly
        if self.neighbourhood == "M":   # Determine number of neighbour cells depending on the neighbourhood
            nhd_type = 8    # 8 cardinal directions
        else:
            nhd_type = 4    # 4 adjacent cells NSEW

        # GET BASIC RASTER DATA SETS
        self.notify("Loading Basic Input Maps")

        # Load Land Use Map
        lu_dref = self.datalibrary.get_data_with_id(self.landuse_map)       # Retrieve the land use data reference
        fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
        self.notify("Loading: "+str(fullfilepath))
        landuseraster = ubspatial.import_ascii_raster(fullfilepath, self.landuse_map)
        self.notify("Load Complete!")
        xllcorner, yllcorner = landuseraster.get_extents()  # Master xll/yll corner - the whole map is based on this

        # Load Population Map
        pop_dref = self.datalibrary.get_data_with_id(self.population_map)   # Retrieve the population data reference
        fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
        self.notify("Loading: " + str(fullfilepath))
        populationraster = ubspatial.import_ascii_raster(fullfilepath, self.population_map)
        self.notify("Load Complete!")
        pop_offset = ubspatial.calculate_offsets(landuseraster, populationraster, landuseraster.get_cellsize())
        # Check Map Offset so that the data can be aligned
        self.notify("Population map cell offsets: " + str(pop_offset[0]) + "," + str(pop_offset[1]))

        # Load Elevation Map
        elev_dref = self.datalibrary.get_data_with_id(self.elevation_map)     # Retrieves the elevation data ref
        fullfilepath = elev_dref.get_data_file_path() + elev_dref.get_metadata("filename")
        self.notify("Loading: " + str(fullfilepath))
        elevationraster = ubspatial.import_ascii_raster(fullfilepath, self.elevation_map)
        self.notify("Load Complete!")
        elev_offset = ubspatial.calculate_offsets(landuseraster, elevationraster, landuseraster.get_cellsize())
        self.notify("Elevation map cell offsets: "+str(elev_offset[0])+","+str(elev_offset[1]))

        # START CREATING BLOCKS MAP
        self.notify("Creating Blocks Map!")
        inputres = landuseraster.get_cellsize()
        width = landuseraster.get_dimensions()[0] * inputres
        height = landuseraster.get_dimensions()[1] * inputres

        # Step 1- AUTO-SIZE Blocks?
        if self.blocksize_auto:
            cs = ubmethods.autosize_blocks(width, height)
        else:
            cs = self.blocksize
        cellsinblock = int(cs/inputres)

        self.notify("Width "+str(width))
        self.notify("Height "+str(height))
        self.notify("Block Size: "+str(cs))
        self.notify("Cells in Block: "+str(cellsinblock))

        # Get the actual simulation area width and height, usually the width will not match the block dimensions
        # perfectly, so we use a whfactor based on the Block Size to ensure that an extra amount of 'width' is added
        # and we can then add an extra column or row of blocks to capture the edges.
        whfactor = 1.0 - (1.0/(float(cs)*2.0))
        widthnew = int(width/float(cs)+whfactor)
        heightnew = int(height / float(cs) + whfactor)
        numblocks = widthnew * heightnew

        # MAP ATTRIBUTES - CREATE THE FIRST UBCOMPONENT() to save off basic map attributes.
        map_attr = ubdata.UBComponent()
        map_attr.add_attribute("NumBlocks", numblocks)
        map_attr.add_attribute("WidthBlocks", widthnew)
        map_attr.add_attribute("HeightBlocks", heightnew)  # Height of simulation area in # of blocks
        map_attr.add_attribute("BlockSize", cs)  # Size of block [m]
        map_attr.add_attribute("InputReso", inputres)  # Resolution of the input data [m]
        map_attr.add_attribute("xllcorner", xllcorner)
        map_attr.add_attribute("yllcorner", yllcorner)
        map_attr.add_attribute("Neigh_Type", nhd_type)
        map_attr.add_attribute("ConsiderCBD", self.considerCBD)
        map_attr.add_attribute("patchdelin", self.patchdelin)
        map_attr.add_attribute("spatialmetrics", self.spatialmetrics)
        map_attr.add_attribute("considerCBD", self.considerCBD)

        # Look up long and lat of CBD if need to be considered
        if self.considerCBD:    # TO DO ----
            # Grab CBD Coordinates and transform to the local coordinate system
            pass

        if self.marklocation:   # TO DO ----
            # Mark locations on the map
            pass

        self.scenario.add_asset("MapAttributes", map_attr)

        print "Simulation Finished up to this point!"


    # Additional Module Functions
    def otherfunctions(self):
        pass
        return True
