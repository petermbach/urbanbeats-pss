# -*- coding: utf-8 -*-
"""
@file   main.pyw
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2012  Peter M. Bach

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
__copyright__ = "Copyright 2012. Peter M. Bach"

# --- CODE STRUCTURE ---
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import threading
import os
import gc
import tempfile

# --- URBANBEATS LIBRARY IMPORTS ---
from ubmodule import *


# --- MODULE CLASS DEFINITION ---
class SpatialMapping(UBModule):
    """ SPATIAL MAPPING MODULE
    Undertakes the task of mapping a range of aspects of the urban
    environment including land cover, water demands, pollution emissions.
    Flood-prone areas
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "Spatial Mapping Module for UrbanBEATS"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        # This module is somewhat special in that parameters are in separate groups based on what the user wants to map
        # within the case study. Each group has a boolean at the start that determines whether that part of the module
        # is activated or not.

        # --- ACTIVATE/DEACTIVATION PARAMETERS ---
        self.create_parameter("planrules", BOOL, "Introduce special planning rules into model?")
        self.planrules = 0

        self.create_parameter("landcover", BOOL, "Map land cover across urban form?")
        self.landcover = 0

        self.create_parameter("wateruse", BOOL, "Calculate spatio-temporal water consumption and wastewater?")
        self.wateruse = 0

        self.create_parameter("emissions", BOOL, "Map pollution emissions across map?")
        self.emissions = 0

        # DEVELOPER NOTE: Add future sub-module BOOLEANS here

        # --- PLANNING RULES PARAMETERS ---
        # Includes a range of options for setting up planning restrictions in the case study. This includes limiting the
        # construction of infrastructure in certain land uses or the introduction of planning overlays that will have
        # some form of impact on how much can be constructed in various regions.

        # Overlays

        # Encumbrances
        self.create_parameter("parks_restrict", BOOL, "Restrict park space usage for decentral. water infrastructure?")
        self.create_parameter("reserves_restrict", BOOL, "Restrict reserve and floodway space to stormwater?")
        self.parks_restrict = 0
        self.reserves_restrict = 0

        # --- LAND COVER MAPPING PARAMETERS ---
        # Assigns land cover types to a range of urban characteristics determined in the previous urban planning module
        # for the purpose of mapping land cover, urban microclimate and other aspects.
        self.create_parameter("surfDriveway", STRING, "Land cover class of paved surfaces.")
        self.create_parameter("surfResIrrigate", STRING, "Which surfaces to irrigate?")
        self.create_parameter("trees_Res", DOUBLE, "Residential tree cover 0 to 1")
        self.surfDriveway = "CO"
        self.surfResIrrigate = "G"
        self.trees_Res = 0.1

        self.create_parameter("surfParking", STRING, "Surface cover of parking lots.")
        self.create_parameter("surfBay", STRING, "Surface cover of loading bay.")
        self.create_parameter("surfHard", STRING, "Surface cover of hard landscaping")
        self.create_parameter("trees_Nres", DOUBLE, "Non-residential tree cover 0 to 1")
        self.create_parameter("trees_Site", BOOL, "Are trees located on-site?")
        self.create_parameter("trees_Front", BOOL, "Are trees located along the frontage?")
        self.surfParking = "AS"
        self.surfBay = "AS"
        self.surfHard = "CO"
        self.trees_Nres = 0.0
        self.trees_Site = 0
        self.trees_Front = 0

        self.create_parameter("surfArt", STRING, "Surface cover of arterial road/street")
        self.create_parameter("surfHwy", STRING, "Surface cover of a highway")
        self.create_parameter("surfFpath", STRING, "Surface cover of footpath")
        self.create_parameter("trees_roaddens", DOUBLE, "Tensity of trees per 100m road length")
        self.surfArt = "AS"
        self.surfHwy = "AS"
        self.surfFpath = "CO"
        self.trees_roaddens = 1

        self.create_parameter("surfFpath", STRING, "Surface cover of paved areas in parks")
        self.create_parameter("trees_opendens", DOUBLE, "Density of tree cover in parks")
        self.create_parameter("trees_refdens", DOUBLE, "Density of tree cover in reserves")
        self.create_parameter("tree_type", STRING, "Default and predominant type of tree in the case study region.")
        self.surfSquare = "CO"
        self.trees_opendens = 10
        self.trees_refdens = 10
        self.tree_type = "RB"

        # GLOBALS
        self.materialtypes = ["AS", "CO", "DG"]  # AS = asphalt, CO = concrete, DG = bare dirt ground
        self.treetypes = ["RB", "RN", "TB", "TN", "OB", "ON"]
        # Explanation of tree types: R = round, T = tall, O = open, B = broad leaves, N = needle leaves

        # --- SPATIO-TEMPORAL WATER USE AND WASTEWATER VOLUMES ---
        # Calculates the water demands, irrigation volumes and wastewater generated. Also includes downscaling of water
        # consumption to daily diurnal patterns and scaling across a year for seasonal trends.




        # --- STORMWATER POLLUTION EMISSIONS ---
        # Pollutions emissions mapping, stormwater system, this module analyses the land use diversity and determines
        # build-up wash-off pollutant concentrations that can then be mapped spatially or modelled temporally.

    def run_module(self):
        """Runs the current module. Note that this module is set up to only call the relevant mapping functions
        according to user-defined inputs, see the value of Activate/Deactivation Parameters to find out which aspects
        of this module run.
        """
        self.notify("Begin Spatial Maping Module")
        map_attr = self.scenario.get_asset_with_name("MapAttributes")
        blockslist = self.scenario.get_assets_with_identifier("BlockID")

        # PLANNING RULES
        if self.planrules:
            self.map_planning_rules()

        # LAND COVER
        if self.landcover:
            for block_attr in blockslist:
                if block_attr.get_attribute("Status") == 0:
                    continue
            self.map_land_surface_covers(block_attr)

        # WATER USE
        if self.wateruse:
            for block_attr in blockslist:
                if block_attr.get_attribute("Status") == 0:
                    continue
            self.map_water_consumption(block_attr)

        # POLLUTION EMISSIONS
        if self.emissions:
            self.map_pollution_emissions()

        return True

    def map_planning_rules(self):
        pass

    def map_land_surface_covers(self, block_attr):
        """Maps the land surface covers of the current Block passed to this method.

        :param block_attr: The UBVector() format of the current Block whose land cover needs to be determined
        :return: No return, block attributes are writen to the current block_attr object
        """

        pass

        return True

    def map_water_consumption(self, block_attr):
        pass

    def map_pollution_emissions(self):
        pass