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
import random as rand
import math
from shapely.geometry import Polygon, Point

# --- URBANBEATS LIBRARY IMPORTS ---
from ubmodule import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
from ..progref import ubglobals

# --- MODULE CLASS DEFINITION ---
class UrbanDevelopment(UBModule):
    """ URBAN DEVELOPMENT MODULE
    Performs the filtering and narrowing of options within the technology
    portfolio. The module also contains relevant information that other modules
    may ask for.
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "Urban Development Module for UrbanBEATS"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        # --- TAB 1 - GENERAL: GENERAL PARAMETERS ---
        self.create_parameter("cellsize", DOUBLE, "cell size of the simulation area, 100m or 50m")
        self.create_parameter("nhd_radius", DOUBLE, "radius of the cell neighbourhood in [km]")
        self.create_parameter("alpha", DOUBLE, "stochastic perturbation factor alpha")
        self.cellsize = 100
        self.nhd_radius = 0.8
        self.alpha = 0.0

        self.create_parameter("baseyear", DOUBLE, "the base year of the simulation")
        self.create_parameter("dt", DOUBLE, "simulation time step in [years]")
        self.baseyear = self.scenario.get_metadata("startyear")
        self.dt = self.scenario.get_metadata("dt")

        # --- TAB 1 - GENERAL: DATA INPUTS AND DETAILS ---
        self.create_parameter("lga_inputmap", STRING, "local municipality map to be used in simulation")
        self.create_parameter("lga_attribute", STRING, "attribute name for identifiers in input map")
        self.lga_inputmap = ""
        self.lga_attribute = ""

        self.create_parameter("luc_inputmap", STRING, "land use map to be used in the simulation")
        self.create_parameter("luc_aggregation", STRING, "aggregation method for the land use")
        self.luc_inputmap = ""
        self.luc_aggregation = "S"  # S = single, MS = mixed static, MA = mixed all fully dynamic

        self.create_parameter("pop_inputmap", STRING, "population input map used in the simulation")
        self.create_parameter("pop_birthrate", DOUBLE, "birth rate")
        self.create_parameter("pop_birthtrend", STRING, "the growth trend to apply")
        self.create_parameter("pop_deathrate", DOUBLE, "death rate")
        self.create_parameter("pop_deathtrend", STRING, "the death trend to apply")
        self.create_parameter("pop_migration", DOUBLE, "migration rate")
        self.create_parameter("pop_migrationtrend", STRING, "migration trend to be applied")
        self.pop_inputmap = ""
        self.pop_birthrate = 6.0
        self.pop_birthtrend = "L"   # L = linear, E = exponential, S = sigmoid, P = stochastic, C = custom
        self.pop_deathrate = 6.0
        self.pop_deathtrend = "L"
        self.pop_migration = 6.0
        self.pop_migrationtrend = "L"

        self.create_parameter("employ_datasource", STRING, "data source for employment information")
        self.employ_datasource = "I"    # I = input map, P = from population, L = from land use

        # Employment parameters when using the input map
        self.create_parameter("employ_inputmap", STRING, "input map for mployment")
        self.create_parameter("employ_inputmaprate", DOUBLE, "annual rate of change for employment")
        self.employ_inputmap = ""
        self.employ_inputmaprate = 6.0

        # Employment parameters when using estimates from population
        self.create_parameter("employ_pop_comfactor", DOUBLE, "factor for estimating commercial employment")
        self.create_parameter("employ_pop_indfactor", DOUBLE, "factor for estimating industrial employment")
        self.create_parameter("employ_pop_officefactor", DOUBLE, "factor for estimating offices employment")
        self.create_parameter("employ_pop_rocbool", BOOL, "use separate rate of change or keep estimating?")
        self.create_parameter("employ_pop_roc", DOUBLE, "rate of change in employment")
        self.employ_pop_comfactor = 0.7
        self.employ_pop_indfactor = 0.9
        self.employ_pop_officefactor = 0.3
        self.employ_pop_rocbool = 0
        self.employ_pop_roc = 6.0

        # Employment parameters when using estimates from land use
        self.create_parameter("employ_land_comfactor", DOUBLE, "factor for estimating commercial employment from land")
        self.create_parameter("employ_land_indfactor", DOUBLE, "factor for estimating industrial employment from land")
        self.create_parameter("employ_land_officefactor", DOUBLE, "factor for estimating office employment from land")
        self.create_parameter("employ_land_rocbool", BOOL, "use separate rate of change?")
        self.create_parameter("employ_land_roc", DOUBLE, "rate of change in employment")
        self.employ_land_comfactor = 70.0
        self.employ_land_indfactor = 50.0
        self.employ_land_officefactor = 100.0
        self.employ_land_rocbool = 0
        self.employ_land_roc = 6.0

        # --- TAB 2 - SPATIAL RELATIONSHIPS: ACCESSIBILITY ---
        self.create_parameter("access_export_combined", BOOL, "export combined accessibility map?")
        self.create_parameter("access_export_individual", BOOL, "export individual accessibility maps?")
        self.access_export_combined = 1
        self.access_export_individual = 1

        # Accessibility to Roads
        self.create_parameter("access_roads_include", BOOL, "Include accessibility assessment to nearest roads?")
        self.create_parameter("access_roads_data", STRING, "data set to use for roads.")
        self.create_parameter("access_roads_weight", DOUBLE, "Weight assigned to the importance of road access")
        self.create_parameter("access_roads_res", BOOL, "consider for residential?")
        self.create_parameter("access_roads_com", BOOL, "consider for commercial?")
        self.create_parameter("access_roads_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_roads_offices", BOOL, "consider for offices?")
        self.create_parameter("access_roads_ares", DOUBLE, "a-value for road access to residential areas")
        self.create_parameter("access_roads_acom", DOUBLE, "a-value for road access to commercial areas")
        self.create_parameter("access_roads_aind", DOUBLE, "a-value for road access to industrial areas")
        self.create_parameter("access_roads_aoffices", DOUBLE, "a-value for road access to offices areas")
        self.access_roads_include = 1
        self.access_roads_data = ""
        self.access_roads_weight = 0.0
        self.access_roads_res = 1
        self.access_roads_com = 1
        self.access_roads_ind = 1
        self.access_roads_offices = 1
        self.access_roads_ares = 0.4
        self.access_roads_acom = 0.4
        self.access_roads_aind = 0.4
        self.access_roads_aoffices = 0.4

        # Accessibility to Rail
        self.create_parameter("access_rail_include", BOOL, "Include accessibility assessment to nearest rail?")
        self.create_parameter("access_rail_data", STRING, "data set to use for rail.")
        self.create_parameter("access_rail_weight", DOUBLE, "Weight assigned to the importance of rail access")
        self.create_parameter("access_rail_res", BOOL, "consider for residential?")
        self.create_parameter("access_rail_com", BOOL, "consider for commercial?")
        self.create_parameter("access_rail_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_rail_offices", BOOL, "consider for offices?")
        self.create_parameter("access_rail_ares", DOUBLE, "a-value for rail access to residential areas")
        self.create_parameter("access_rail_acom", DOUBLE, "a-value for rail access to commercial areas")
        self.create_parameter("access_rail_aind", DOUBLE, "a-value for rail access to industrial areas")
        self.create_parameter("access_rail_aoffices", DOUBLE, "a-value for rail access to offices areas")
        self.access_rail_include = 1
        self.access_rail_data = ""
        self.access_rail_weight = 0
        self.access_rail_res = 1
        self.access_rail_com = 1
        self.access_rail_ind = 1
        self.access_rail_offices = 1
        self.access_rail_ares = 0.4
        self.access_rail_acom = 0.4
        self.access_rail_aind = 0.4
        self.access_rail_aoffices = 0.4

        # Accessibility to Waterways
        self.create_parameter("access_waterways_include", BOOL, "Include accessibility assessment to nearest waterway?")
        self.create_parameter("access_waterways_data", STRING, "data set to use for waterway.")
        self.create_parameter("access_waterways_weight", DOUBLE, "Weight assigned to the importance of waterway access")
        self.create_parameter("access_waterways_res", BOOL, "consider for residential?")
        self.create_parameter("access_waterways_com", BOOL, "consider for commercial?")
        self.create_parameter("access_waterways_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_waterways_offices", BOOL, "consider for offices?")
        self.create_parameter("access_waterways_ares", DOUBLE, "a-value for waterway access to residential areas")
        self.create_parameter("access_waterways_acom", DOUBLE, "a-value for waterway access to commercial areas")
        self.create_parameter("access_waterways_aind", DOUBLE, "a-value for waterway access to industrial areas")
        self.create_parameter("access_waterways_aoffices", DOUBLE, "a-value for waterway access to offices areas")
        self.access_waterways_include = 1
        self.access_waterways_data = ""
        self.access_waterways_weight = 0.0
        self.access_waterways_res = 1
        self.access_waterways_com = 1
        self.access_waterways_ind = 1
        self.access_waterways_offices = 1
        self.access_waterways_ares = 0.4
        self.access_waterways_acom = 0.4
        self.access_waterways_aind = 0.4
        self.access_waterways_aoffices = 0.4

        # Accessibility to lakes
        self.create_parameter("access_lakes_include", BOOL, "Include accessibility assessment to nearest lake?")
        self.create_parameter("access_lakes_data", STRING, "data set to use for lake.")
        self.create_parameter("access_lakes_weight", DOUBLE, "Weight assigned to the importance of lake access")
        self.create_parameter("access_lakes_res", BOOL, "consider for residential?")
        self.create_parameter("access_lakes_com", BOOL, "consider for commercial?")
        self.create_parameter("access_lakes_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_lakes_offices", BOOL, "consider for offices?")
        self.create_parameter("access_lakes_ares", DOUBLE, "a-value for lake access to residential areas")
        self.create_parameter("access_lakes_acom", DOUBLE, "a-value for lake access to commercial areas")
        self.create_parameter("access_lakes_aind", DOUBLE, "a-value for lake access to industrial areas")
        self.create_parameter("access_lakes_aoffices", DOUBLE, "a-value for lake access to offices areas")
        self.access_lakes_include = 1
        self.access_lakes_data = ""
        self.access_lakes_weight = 0.0
        self.access_lakes_res = 1
        self.access_lakes_com = 1
        self.access_lakes_ind = 1
        self.access_lakes_offices = 1
        self.access_lakes_ares = 0.4
        self.access_lakes_acom = 0.4
        self.access_lakes_aind = 0.4
        self.access_lakes_aoffices = 0.4

        # Accessibility to Public Open Space (POS)
        self.create_parameter("access_pos_include", BOOL, "Include accessibility assessment to nearest pos?")
        self.create_parameter("access_pos_data", STRING, "data set to use for pos.")
        self.create_parameter("access_pos_weight", DOUBLE, "Weight assigned to the importance of pos access")
        self.create_parameter("access_pos_res", BOOL, "consider for residential?")
        self.create_parameter("access_pos_com", BOOL, "consider for commercial?")
        self.create_parameter("access_pos_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_pos_offices", BOOL, "consider for offices?")
        self.create_parameter("access_pos_ares", DOUBLE, "a-value for POS access to residential areas")
        self.create_parameter("access_pos_acom", DOUBLE, "a-value for POS access to commercial areas")
        self.create_parameter("access_pos_aind", DOUBLE, "a-value for POS access to industrial areas")
        self.create_parameter("access_pos_aoffices", DOUBLE, "a-value for POS access to offices areas")
        self.access_pos_include = 1
        self.access_pos_data = ""
        self.access_pos_weight = 0.0
        self.access_pos_res = 1
        self.access_pos_com = 1
        self.access_pos_ind = 1
        self.access_pos_offices = 1
        self.access_pos_ares = 0.4
        self.access_pos_acom = 0.4
        self.access_pos_aind = 0.4
        self.access_pos_aoffices = 0.4

        # Accessibility to Points of Interest (POIs)
        self.create_parameter("access_poi_include", BOOL, "Include accessibility assessment to nearest poi?")
        self.create_parameter("access_poi_data", STRING, "data set to use for poi.")
        self.create_parameter("access_poi_weight", DOUBLE, "Weight assigned to the importance of poi access")
        self.create_parameter("access_poi_res", BOOL, "consider for residential?")
        self.create_parameter("access_poi_com", BOOL, "consider for commercial?")
        self.create_parameter("access_poi_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_poi_offices", BOOL, "consider for offices?")
        self.create_parameter("access_poi_ares", DOUBLE, "a-value for POI access to residential areas")
        self.create_parameter("access_poi_acom", DOUBLE, "a-value for POI access to commercial areas")
        self.create_parameter("access_poi_aind", DOUBLE, "a-value for POI access to industrial areas")
        self.create_parameter("access_poi_aoffices", DOUBLE, "a-value for POI access to offices areas")
        self.access_poi_include = 1
        self.access_poi_data = ""
        self.access_poi_weight = 0.0
        self.access_poi_res = 1
        self.access_poi_com = 1
        self.access_poi_ind = 1
        self.access_poi_offices = 1
        self.access_poi_ares = 0.4
        self.access_poi_acom = 0.4
        self.access_poi_aind = 0.4
        self.access_poi_aoffices = 0.4

        # --- TAB 2 - SPATIAL RELATIONSHIPS: SUITABILITY ---
        self.create_parameter("suit_export", BOOL, "export the created suitability map?")
        self.suit_export = 1

        # Suitability Criteria
        self.create_parameter("suit_slope_include", BOOL, "include slope assessment in suitability?")
        self.create_parameter("suit_slope_data", STRING, "dataset to use for slope")
        self.create_parameter("suit_slope_weight", DOUBLE, "weight assigned to slope in suitability assessment")
        self.create_parameter("suit_slope_attract", BOOL, "should slope be an attraction factor?")
        self.suit_slope_include = 1
        self.suit_slope_data = ""
        self.suit_slope_weight = 5.0
        self.suit_slope_attract = 0

        self.create_parameter("suit_gw_include", BOOL, "include groundwater assessment in suitability?")
        self.create_parameter("suit_gw_data", STRING, "dataset to use for groundwater")
        self.create_parameter("suit_gw_weight", DOUBLE, "weight assigned to groundwater in suitability assessment")
        self.create_parameter("suit_gw_attract", BOOL, "should groundwater be an attraction factor?")
        self.suit_gw_include = 1
        self.suit_gw_data = ""
        self.suit_gw_weight = 5.0
        self.suit_gw_attract = 0

        self.create_parameter("suit_soil_include", BOOL, "include soil assessment in suitability?")
        self.create_parameter("suit_soil_data", STRING, "dataset to use for soil")
        self.create_parameter("suit_soil_weight", DOUBLE, "weight assigned to soil in suitability assessment")
        self.create_parameter("suit_soil_attract", BOOL, "should soil be an attraction factor?")
        self.suit_soil_include = 1
        self.suit_soil_data = ""
        self.suit_soil_weight = 5.0
        self.suit_soil_attract = 0

        self.create_parameter("suit_custom1_include", BOOL, "include custom1 assessment in suitability?")
        self.create_parameter("suit_custom1_data", STRING, "dataset to use for custom1")
        self.create_parameter("suit_custom1_weight", DOUBLE, "weight assigned to custom1 in suitability assessment")
        self.create_parameter("suit_custom1_attract", BOOL, "should custom1 be an attraction factor?")
        self.suit_custom1_include = 1
        self.suit_custom1_data = ""
        self.suit_custom1_weight = 5.0
        self.suit_custom1_attract = 0

        self.create_parameter("suit_custom2_include", BOOL, "include custom2 assessment in suitability?")
        self.create_parameter("suit_custom2_data", STRING, "dataset to use for custom2")
        self.create_parameter("suit_custom2_weight", DOUBLE, "weight assigned to custom2 in suitability assessment")
        self.create_parameter("suit_custom2_attract", BOOL, "should custom2 be an attraction factor?")
        self.suit_custom2_include = 1
        self.suit_custom2_data = ""
        self.suit_custom2_weight = 5.0
        self.suit_custom2_attract = 0

        # [TO DO] THRESHOLDS FOR LAND USE CATEGORIES

        # --- TAB 2 - SPATIAL RELATIONSHIPS: ZONING ---
        self.create_parameter("zoning_export", BOOL, "export aggregated zoning maps for each land use?")
        self.zoning_export = 1

        # General Zoning Constraints
        self.create_parameter("zoning_constraint_water", STRING, "water bodies map to use in creating zoning.")
        self.zoning_constraint_water = ""

        # Passive and Constrained Land Uses
        self.create_parameter("zoning_passive_luc", LISTDOUBLE, "Land use categories in passive group of uses")
        self.create_parameter("zoning_constrained_luc", LISTDOUBLE, "Land use categories in constrained group")
        self.zoning_passive_luc = [5, 6, 7, 8, 9, 10, 11, 12, 14, 15]   # These are numerical encodings of LUC categories
        self.zoning_constrained_luc = []                        # refer to ubglobals.py for key

        # Additional Zoning Areas for Land uses
        self.create_parameter("zoning_rules_resmap", STRING, "Zoning map for designating residential uses")
        self.create_parameter("zoning_rules_resauto", BOOL, "Auto-determine residential regions?")
        self.create_parameter("zoning_rules_reslimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_respassive", BOOL, "Include all passive areas?")
        self.create_parameter("zoning_rules_resundev", BOOL, "Include all undeveloped areas?")
        self.zoning_rules_resmap = ""
        self.zoning_rules_resauto = 1
        self.zoning_rules_reslimit = 0
        self.zoning_rules_respassive = 1
        self.zoning_rules_resundev = 1

        self.create_parameter("zoning_rules_commap", STRING, "Zoning map for designating comidential uses")
        self.create_parameter("zoning_rules_comauto", BOOL, "Auto-determine comidential regions?")
        self.create_parameter("zoning_rules_comlimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_compassive", BOOL, "Include all passive areas?")
        self.create_parameter("zoning_rules_comundev", BOOL, "Include all undeveloped areas?")
        self.zoning_rules_commap = ""
        self.zoning_rules_comauto = 1
        self.zoning_rules_comlimit = 0
        self.zoning_rules_compassive = 1
        self.zoning_rules_comundev = 1

        self.create_parameter("zoning_rules_indmap", STRING, "Zoning map for designating indidential uses")
        self.create_parameter("zoning_rules_indauto", BOOL, "Auto-determine indidential regions?")
        self.create_parameter("zoning_rules_indlimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_indpassive", BOOL, "Include all passive areas?")
        self.create_parameter("zoning_rules_indundev", BOOL, "Include all undeveloped areas?")
        self.zoning_rules_indmap = ""
        self.zoning_rules_indauto = 1
        self.zoning_rules_indlimit = 0
        self.zoning_rules_indpassive = 1
        self.zoning_rules_indundev = 1

        self.create_parameter("zoning_rules_officesmap", STRING, "Zoning map for designating officesidential uses")
        self.create_parameter("zoning_rules_officesauto", BOOL, "Auto-determine officesidential regions?")
        self.create_parameter("zoning_rules_officeslimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_officespassive", BOOL, "Include all passive areas?")
        self.create_parameter("zoning_rules_officesundev", BOOL, "Include all undeveloped areas?")
        self.zoning_rules_officesmap = ""
        self.zoning_rules_officesauto = 1
        self.zoning_rules_officeslimit = 0
        self.zoning_rules_officespassive = 1
        self.zoning_rules_officesundev = 1

        # ADVANCED PARAMETERS

    def run_module(self):
        """Runs the urban development module's simulation. Processes all inputs to simulate changes in land use and
        population over time. The run_module function only runs for ONE simulation time step.

        :return: A map of urban cells containing land use, population and other information.
        """
        # --- PRECURSOR: CHECK IF THE MODEL IS ABLE TO RUN ---
        # if not self.lga_inputmap and not self.pop_inputmap and not self.luc_inputmap:
        #     self.notify("Error, data missing, cannot run the Urban Development Module")
        #   [TO DO IN FUTURE]

        self.notify("Begin Urban Development Simulation")
        print "Begin Urban Development Simulation"
        rand.seed()

        # --- SECTION 1 - Get Boundary, Setup Details for the Simulation Grid and MapAttributes Component
        xmin, xmax, ymin, ymax = self.activesim.get_project_boundary_info("mapextents")
        mapwidth = xmax - xmin  # width of the map [m]
        mapheight = ymax - ymin  # height of map [m]

        self.notify("Map Width [km] = " + str(mapwidth / 1000.0))
        self.notify("Map Height [km] = " + str(mapheight / 1000.0))
        self.notify("---===---")
        print("Map Width [km] = " + str(mapwidth / 1000.0))
        print("Map Height [km] = " + str(mapheight / 1000.0))
        print("---===---")

        # DETERMINE SIMULATION GRID
        self.notify("Creating Simulation Grid with size: "+str(self.cellsize)+" m")
        print("Creating Simulation Grid with size: "+str(self.cellsize)+" m")

        cells_wide = int(math.ceil(mapwidth / float(self.cellsize)))
        cells_tall = int(math.ceil(mapheight / float(self.cellsize)))
        numcells = cells_wide * cells_tall

        self.notify("Map Dimensions WxH [cells]: "+str(cells_wide)+" x "+str(cells_tall))
        self.notify("Total Cells in map: "+str(numcells))
        print("Map Dimensions WxH [cells]: " + str(cells_wide) + " x " + str(cells_tall))
        print("Total Cells in map: " + str(numcells))

        # CREATE MAP ATTRIBUTES UBCOMPONENT() to track
        map_attr = ubdata.UBComponent()
        map_attr.add_attribute("xllcorner", xmin)  # The geographic coordinate x-pos of the actual map
        map_attr.add_attribute("yllcorner", ymin)  # The geographic coordinate y-pos of the actual map
        map_attr.add_attribute("NumCells", numcells)
        map_attr.add_attribute("HasURBANDEV", 1)
        map_attr.add_attribute("CellsWide", cells_wide)
        map_attr.add_attribute("CellsTall", cells_tall)
        map_attr.add_attribute("CellSize", self.cellsize)

        self.scenario.add_asset("MapAttributes", map_attr)

        # --- SECTION 2 - Create the simulation grid ---
        boundarygeom = self.activesim.get_project_boundary_info("coordinates")
        boundarygeom_zeroorigin = []    # Contains the polygon's coordinates shifted to the zero origin
        for coord in boundarygeom:      # Shift the map to (0,0) origin
            boundarygeom_zeroorigin.append((coord[0] - xmin, coord[1] - ymin))

        boundarypoly = Polygon(boundarygeom_zeroorigin)  # Test intersect with Block Polygon later using

        cellIDcount = 1     # Setup counter for cells
        cellslist = []
        print ("Creating cell grid")
        for y in range(cells_tall):
            for x in range(cells_wide):
                print ("Current Cell_ID: "+str(cellIDcount))

                # - STEP 1 - GENERATE CELL GEOMETRIES
                current_cell = self.create_cell_face(x, y, self.cellsize, cellIDcount, boundarypoly)
                if current_cell is None:
                    cellIDcount += 1    # Increase the ID counter by one
                    continue

                xcentre = x * self.cellsize + 0.5 * self.cellsize
                ycentre = y * self.cellsize + 0.5 * self.cellsize

                xorigin = x * self.cellsize
                yorigin = y * self.cellsize

                current_cell.add_attribute("CentreX", xcentre)      # ATTRIBUTE: geographic information
                current_cell.add_attribute("CentreY", ycentre)
                current_cell.add_attribute("OriginX", xorigin)
                current_cell.add_attribute("OriginY", yorigin)
                current_cell.add_attribute("Region", "None")
                current_cell.add_attribute("Status", 1)     # Start with Status = 1 by default

                self.scenario.add_asset("CellID"+str(cellIDcount), current_cell)
                cellslist.append(current_cell)
                cellIDcount += 1    # Increase the Cell ID Count by one

        # - STEP 2 - TRANSFER RASTER DATA TO CELLS
        # Depending on availability, start with municipality
        self.notify("Loading input maps")
        print ("Loading input maps")

        # - 2.1 - MUNICIPALITIES ---
        # STEP 2.1.1 :: Load Municipalities
        if self.lga_inputmap == "":
            self.notify("Region is treated as a single municipality")
            print ("Region is treated as a single municipality")
            map_attr.add_attribute("HasGEOPOLITICAL", 0)
        else:
            self.notify("Loading and Assigning Municipalities")
            print("Loading and Assigning Municipalities")
            municipalities = []
            map_attr.add_attribute("HasGEOPOLITICAL", 1)
            geopol_map = self.datalibrary.get_data_with_id(self.lga_inputmap)
            fullfilepath = geopol_map.get_data_file_path() + geopol_map.get_metadata("filename")
            municipalities = ubspatial.import_polygonal_map(fullfilepath, "native", "Municipality",
                                                            (map_attr.get_attribute("xllcorner"),
                                                             map_attr.get_attribute("yllcorner")))

        # STEP 2.1.2 :: Assign Municipalities to Blocks and create municipality polygons
        for i in range(len(municipalities)):
            self.scenario.add_asset(municipalities[i].get_attribute("Map_Naming"), municipalities[i])

        # Assign municipality to cells - based on centroids first, then polygonal intersection
        for i in range(len(cellslist)):
            current_cell = cellslist[i]
            coordinates = current_cell.get_points()
            # List comprehension: creates a list of coordinates with only
            # x, y points. I.e. removes the Z-coordinate
            coordinates = [c[:2] for c in coordinates]
            cellpoly = Polygon(coordinates)

            intersectarea = 0
            intersectname = ""
            for m in municipalities:
                featpoly = Polygon(m.get_points())
                if not featpoly.intersects(cellpoly):  # If there is no intersection...
                    continue
                newisectionarea = featpoly.intersection(cellpoly).area
                if newisectionarea > intersectarea:
                    intersectarea = newisectionarea
                    intersectname = m.get_attribute(self.lga_attribute)

            if intersectname != "" and intersectarea > 0:
                current_cell.add_attribute("Region", intersectname)
            else:
                current_cell.add_attribute("Region", "Unassigned")

        # - 2.2 - LAND USE ---
        # INTERIM STEP - get active/passive/constrained land use type
        active, passive, constrained = self.determine_land_use_types()

        # STEP 2.2.1 :: Load Land Use
        if self.luc_inputmap:
            lu_dref = self.datalibrary.get_data_with_id(self.luc_inputmap)      # Retrieve the land use map
            fullfilepath = lu_dref.get_data_file_path() + lu_dref.get_metadata("filename")
            self.notify("Loading: "+str(fullfilepath))
            print ("Loading: " + str(fullfilepath))
            landuseraster = ubspatial.import_ascii_raster(fullfilepath, self.luc_inputmap)
            self.notify("Load Complete!")
            print("Load Complete!")
            landuse_offset = ubspatial.calculate_offsets(landuseraster, map_attr)
            luc_res = landuseraster.get_cellsize()
            csc = int(self.cellsize / luc_res)  # csc = cell selection count - knowing how many cells wide and tall

            # STEP 2.2.2 :: Aggregate Land Use
            for i in range(len(cellslist)):
                current_cell = cellslist[i]
                col_start = int(current_cell.get_attribute("OriginX") / luc_res)
                row_start = int(current_cell.get_attribute("OriginY") / luc_res)
                landusedatamatrix = landuseraster.get_data_square(col_start, row_start, csc, csc)

                if csc > 1.0:       # Then the cell size greater than the input raster resolution
                    landuse_cat, activity = self.determine_dominant_landusecat(landusedatamatrix)
                    if landuse_cat is None:
                        current_cell.change_attribute("Status", 0)
                    else:
                        current_cell.add_attribute("Base_LUC", landuse_cat)
                        current_cell.add_attribute("Active", float(activity))
                else:   # Single value from landusedata matrix
                    landuse_cat = ubglobals.LANDUSENAMES[int(landusedatamatrix - 1)]
                    current_cell.add_attribute("Base_LUC", landuse_cat)
                    current_cell.add_attribute("Active", 1.0)

                # STEP 2.2.3 :: ASSIGN LAND USE TYPE
                if landuse_cat in active:
                    current_cell.add_attribute("LUC_Type", "Active")
                elif landuse_cat in passive:
                    current_cell.add_attribute("LUC_Type", "Passive")
                elif landuse_cat in constrained:
                    current_cell.add_attribute("LUC_Type", "Constrained")
                else:
                    current_cell.add_attribute("LUC_Type", "UNDEFINED")

            map_attr.set_attribute("HasLUC", 1)
        else:
            map_attr.set_attribute("HasLUC", 1)

        # - 2.3 - POPULATION ---
        # STEP 2.3.1 :: Load Population Map
        if self.pop_inputmap:
            pop_dref = self.datalibrary.get_data_with_id(self.pop_inputmap)  # Retrieve the population data reference
            fullfilepath = pop_dref.get_data_file_path() + pop_dref.get_metadata("filename")
            self.notify("Loading: " + str(fullfilepath))
            print("Loading: " + str(fullfilepath))
            populationraster = ubspatial.import_ascii_raster(fullfilepath, self.pop_inputmap)
            self.notify("Load Complete!")
            print("Load Complete!")
            population_offset = ubspatial.calculate_offsets(populationraster, map_attr)
            pop_res = populationraster.get_cellsize()
            csc = int(self.cellsize / pop_res)  # csc = cell selection count - knowing how many cells wide and tall
            map_population = 0
            discrepancy_pop = 0

            # STEP 2.3.2 :: Transfer Population to Cells
            for i in range(len(cellslist)):
                current_cell = cellslist[i]
                col_start = int(current_cell.get_attribute("OriginX") / luc_res)
                row_start = int(current_cell.get_attribute("OriginY") / luc_res)
                popdatamatrix = populationraster.get_data_square(col_start, row_start, csc, csc)

                popfactor = 1.0
                if pop_dref.get_metadata("sub") == "Density":
                    popfactor = (float(pop_res) * float(pop_res)) / 10000.0  # Area of a single cell (persons/ha)
                elif pop_dref.get_metadata("sub") == "Count":
                    popfactor = 1.0  # No multiplication

                if csc > 1.0:
                    pop_values = popdatamatrix.flatten()
                    pop_values[pop_values == populationraster.get_nodatavalue()] = 0
                    total_population = float(sum(pop_values) * popfactor)
                    map_population += total_population
                    current_cell.add_attribute("Base_POP", int(total_population))
                else:
                    # The cell is either the same size of bigger that of the current cell
                    if pop_dref.get_metadata("sub") == "Density":
                        total_population = popdatamatrix * (self.cellsize * self.cellsize) / 10000.0
                    elif pop_dref.get_metadata("sub") == "Count":
                        total_population = popdatamatrix / (float(pop_res) * float(pop_res)/ 10000.0)
                        total_population = total_population * (self.cellsize * self.cellsize) / 10000.0
                    current_cell.add_attribute("Base_POP", int(total_population))
                    map_population += total_population

                if current_cell.get_attribute("Base_LUC") is not "Residential":
                    discrepancy_pop += current_cell.get_attribute("Base_POP")
                    current_cell.add_attribute("Base_POP", 0)
                    continue

            map_attr.add_attribute("HasPOP", 1)
            map_attr.add_attribute("POP_Map", map_population)
            map_attr.add_attribute("POP_Discrepancy", discrepancy_pop)
            self.notify("The Total Population across the case study: "+str(int(map_population)))
            self.notify("The removed population is: "+str(int(discrepancy_pop)))
            self.notify("The discrepancy is: "+str(int(float(discrepancy_pop / map_population) * 100.0)))
        else:
            map_attr.add_attribute("HasPOP", 0)
            map_attr.add_attribute("POP_Map", 0)
            map_attr.add_attribute("POP_Discrepancy", 0)

        # - 2.4 - EMPLOYMENT Calculate/Load Employment ---
        if self.employ_datasource == "I":   # Input Map
            pass    # [TO DO]
        elif self.employ_datasource == "P":     # From Population
            self.calculate_employment_from_population(cellslist, self.cellsize)
        else:   # From Land use
            for i in range(len(cellslist)):
                current_cell = cellslist[i]
                if current_cell.get_attribute("Base_LUC") not in ["Commercial", "Offices Res Mix",
                                                                  "Light Industry", "Heavy Industry"]:
                    current_cell.add_attribute("Base_EMP", 0)
                    continue
                self.calculate_employment_from_land_use(current_cell, self.cellsize)

        # - 2.5 - DETERMINE NEIGHBOURHOODS ---
        # self.notify("Establishing Neighbourhoods")
        # print ("Establishing Neighbourhoods")
        # hashtable = [[], []]    # [Cell_Obj, NhD_Objs]
        # nhd_rad = self.nhd_radius * 1000    # Convert to [m]
        # sqdist = nhd_rad * nhd_rad
        #
        # for i in range(len(cellslist)):
        #     cur_cell = cellslist[i]
        #     hashtable[0].append(cur_cell)   # Add the current cell object to the hash_table
        #     neighbours = []
        #     neighbour_IDs = []
        #     coords = (cur_cell.get_attribute("CentreX"), cur_cell.get_attribute("CentreY"))
        #     for j in range(len(cellslist)):
        #         dx = (cellslist[j].get_attribute("CentreX") - coords[0])
        #         dy = (cellslist[j].get_attribute("CentreY") - coords[1])
        #         if (dx * dx + dy * dy) <= sqdist:
        #             # The Cell is part of the neighbourhood
        #             neighbours.append(cellslist[j])
        #             neighbour_IDs.append(cellslist[j].get_attribute("CellID"))
        #     cur_cell.add_attribute("NHD_IDs", neighbour_IDs)
        #     cur_cell.add_attribute("NHD_N", len(neighbour_IDs))
        #     hashtable[1].append(neighbours)

        # - 2.6 - SPATIAL RELATIONSHIPS - ACCESSIBILITY
        # - 2.6.1 - Determine individual accessibility maps
        self.notify("Entering Accessibility Calculations")
        print("Entering Accessibility Calculations")

        if self.access_roads_include:
            aj = [float(self.access_roads_res * self.access_roads_ares),
                  float(self.access_roads_com * self.access_roads_acom),
                  float(self.access_roads_ind * self.access_roads_aind),
                  float(self.access_roads_offices * self.access_roads_aoffices)]
            self.calculate_accessibility_linearfeatures(self.access_roads_data, map_attr, aj, cellslist, "ROAD")
        if self.access_rail_include:
            aj = [float(self.access_rail_res * self.access_rail_ares),
                  float(self.access_rail_com * self.access_rail_acom),
                  float(self.access_rail_ind * self.access_rail_aind),
                  float(self.access_rail_offices * self.access_rail_aoffices)]
            self.calculate_accessibility_linearfeatures(self.access_rail_data, map_attr, aj, cellslist, "RAIL")
        if self.access_waterways_include:
            aj = [float(self.access_waterways_res * self.access_waterways_ares),
                  float(self.access_waterways_com * self.access_waterways_acom),
                  float(self.access_waterways_ind * self.access_waterways_aind),
                  float(self.access_waterways_offices * self.access_waterways_aoffices)]
            self.calculate_accessibility_linearfeatures(self.access_waterways_data, map_attr, aj, cellslist, "WWAY")
        if self.access_lakes_include:
            aj = [float(self.access_lakes_res * self.access_lakes_ares),
                  float(self.access_lakes_com * self.access_lakes_acom),
                  float(self.access_lakes_ind * self.access_lakes_aind),
                  float(self.access_lakes_offices * self.access_lakes_aoffices)]
            self.calculate_accessibility_polygonfeatures(self.access_lakes_data, map_attr, aj, cellslist, "LAKE")
        if self.access_pos_include:
            aj = [float(self.access_pos_res * self.access_pos_ares),
                  float(self.access_pos_com * self.access_pos_acom),
                  float(self.access_pos_ind * self.access_pos_aind),
                  float(self.access_pos_offices * self.access_pos_aoffices)]
            self.calculate_accessibility_polygonfeatures(self.access_pos_data, map_attr, aj, cellslist, "POSS")
        if self.access_poi_include:
            aj = [float(self.access_poi_res * self.access_poi_ares),
                  float(self.access_poi_com * self.access_poi_acom),
                  float(self.access_poi_ind * self.access_poi_aind),
                  float(self.access_poi_offices * self.access_poi_aoffices)]
            self.calculate_accessibility_pointfeatures(self.access_poi_data, map_attr, aj, cellslist, "POIS")

        # - 2.6.2 - Combine Accessibility criteria into full map
        accessibility_weights = [float(self.access_roads_weight * self.access_roads_include),
                                 float(self.access_rail_weight * self.access_rail_include),
                                 float(self.access_waterways_weight * self.access_waterways_include),
                                 float(self.access_lakes_weight * self.access_lakes_include),
                                 float(self.access_pos_weight * self.access_pos_include),
                                 float(self.access_poi_weight * self.access_poi_include)]
        accessibility_weights = ubmethods.normalize_weights(accessibility_weights, "SUM")   # 0 to 1 normalize
        accessibility_attributes = ["ACC_ROAD", "ACC_RAIL", "ACC_WWAY", "ACC_LAKE", "ACC_POSS", "ACC_POIS"]

        for i in range(len(cellslist)):
            final_acc_res, final_acc_com, final_acc_ind, final_acc_orc = 0, 0, 0, 0
            val_res, val_com, val_ind, val_orc = 0, 0, 0, 0     # Initialize
            for acc in range(len(accessibility_attributes)):
                val_res = cellslist[i].get_attribute(accessibility_attributes[acc]+"_RES")
                if val_res is None: val_res = 0
                final_acc_res += accessibility_weights[acc] * val_res

                val_com = cellslist[i].get_attribute(accessibility_attributes[acc] + "_COM")
                if val_com is None: val_com = 0
                final_acc_com += accessibility_weights[acc] * val_com

                val_ind = cellslist[i].get_attribute(accessibility_attributes[acc] + "_IND")
                if val_ind is None: val_ind = 0
                final_acc_ind += accessibility_weights[acc] * val_ind

                val_orc = cellslist[i].get_attribute(accessibility_attributes[acc] + "_ORC")
                if val_orc is None: val_orc = 0
                final_acc_orc += accessibility_weights[acc] * val_orc

            cellslist[i].add_attribute("ACCESS_RES", final_acc_res)
            cellslist[i].add_attribute("ACCESS_COM", final_acc_com)
            cellslist[i].add_attribute("ACCESS_IND", final_acc_ind)
            cellslist[i].add_attribute("ACCESS_ORC", final_acc_orc)

        # Loop across blocks, get the five attributes and calculate total accessibility


        # - 2.7 - SPATIAL RELATIONSHIPS - SUITABILITY



        # - 2.8 - SPATIAL RELATIONSHIPS - ZONING



        # - 2.9 - SPATIAL RELATIONSHIPS - NEIGHBOURHOOD EFFECT




        self.notify("Current End of Module")
        print ("Current end of module")
        return True

    def calculate_accessibility_pointfeatures(self, map_input, map_attr, aj, cellslist, att_name):
        """Calculates the accessibility from a Point Features Map and adds the individual accessibility values
        to the map.

        :param map_input: the input map to calculate the accessibility from
        :param aj: the list of parameters for accessibility calculations - the importance factors
        :param cellslist: the list of cells in the simulation
        :param att_name: the prefix attribute name to use (e.g. ROADS --> "ACC_ROAD_"
        :return:
        """
        self.notify("Determining Accessibility to: " + att_name)

        # LOAD POINT FEATURES GET POINTS COORDINATES
        pointfeatures = []

        # CALCULATE CLOSEST DISTANCE TO EACH CELL
        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            loc = Point(cellslist[i].get_attribute("CentreX"), cellslist[i].get_attribute("CentreY"))
            dist = 99999999.0
            for j in range(len(pointfeatures)):  # Loop through all feature points
                feat_point = Point(pointfeatures[j])  # Make a Shapely point
                if loc.distance(feat_point) < dist:
                    dist = loc.distance(feat_point)  # Get the shortest distance

            cur_cell.add_attribute("ACC_" + att_name + "_RES",
                                   ubmethods.calculate_accessibility_factor(dist, params[0]))
            cur_cell.add_attribute("ACC_" + att_name + "_COM",
                                   ubmethods.calculate_accessibility_factor(dist, params[1]))
            cur_cell.add_attribute("ACC_" + att_name + "_IND",
                                   ubmethods.calculate_accessibility_factor(dist, params[2]))
            cur_cell.add_attribute("ACC_" + att_name + "_ORC",
                                   ubmethods.calculate_accessibility_factor(dist, params[3]))
        return True

    def calculate_accessibility_linearfeatures(self, map_input, map_attr, params, cellslist, att_name):
        """Calculates the accessibility from a Point Features Map and adds the individual accessibility values
        to the map.

        :param map_input: the input map to calculate the accessibility from
        :param aj: the list of parameters for accessibility calculations - the importance factors
        :param cellslist: the list of cells in the simulation
        :param att_name: the prefix attribute name to use (e.g. ROADS --> "ROAD"
        :return:
        """
        self.notify("Determining Accessibility to: "+att_name)

        # GET THE FULL FILENAME OF THE MAP INPUT
        dref = self.datalibrary.get_data_with_id(map_input)  # Retrieve the land use map
        fullfilepath = dref.get_data_file_path() + dref.get_metadata("filename")

        # LOAD LINEAR FEATURES AND SEGMENTIZE
        linearfeatures = ubspatial.import_linear_network(fullfilepath, "POINTS",
                                                         (map_attr.get_attribute("xllcorner"),
                                                          map_attr.get_attribute("yllcorner")),
                                                         Segments=self.cellsize)  # Segmentation

        self.notify("Number of loaded features to compare: "+str(len(linearfeatures)))
        print "Length of the featurepoints list: ", str(len(linearfeatures))

        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            loc = (cellslist[i].get_attribute("CentreX"), cellslist[i].get_attribute("CentreY"))
            dist = 99999999.0
            for j in range(len(linearfeatures)):        # Loop through all feature points
                feat_point = linearfeatures[j]   # Make a Shapely point
                dx = loc[0] - feat_point[0]
                dy = loc[1] - feat_point[1]
                newdist = math.sqrt(dx * dx + dy * dy)
                if newdist < dist:
                    dist = newdist
            cur_cell.add_attribute("ACC_"+att_name+"_DIST", dist / 1000.0)   # Distance in [km]
            cur_cell.add_attribute("ACC_"+att_name+"_RES", ubmethods.calculate_accessibility_factor(dist, params[0]))
            cur_cell.add_attribute("ACC_"+att_name+"_COM", ubmethods.calculate_accessibility_factor(dist, params[1]))
            cur_cell.add_attribute("ACC_"+att_name+"_IND", ubmethods.calculate_accessibility_factor(dist, params[2]))
            cur_cell.add_attribute("ACC_"+att_name+"_ORC", ubmethods.calculate_accessibility_factor(dist, params[3]))
        return True

    def calculate_accessibility_polygonfeatures(self, map_input, map_attr, params, cellslist, att_name):
        """Calculates the accessibility from a Point Features Map and adds the individual accessibility values
        to the map.

        :param map_input: the input map to calculate the accessibility from
        :param aj: the list of parameters for accessibility calculations - the importance factors
        :param cellslist: the list of cells in the simulation
        :param att_name: the prefix attribute name to use (e.g. ROADS --> "ACC_ROAD_"
        :return:
        """
        self.notify("Determining Accessibility to: " + att_name)

        # LOAD POLYGONAL FEATURES
        linearfeatures = ubspatial.import_linear_network(map_input, "POINTS",
                                                         (map_attr.get_attribute("xllcorner"),
                                                          map_attr.get_attribute("yllcorner")),
                                                         Segments=self.cellsize / 4.0)  # Segmentation
        # GET RING COORDINATES FROM POLYGONAL FEATURES


        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            loc = Point(cellslist[i].get_attribute("CentreX"), cellslist[i].get_attribute("CentreY"))
            dist = 99999999.0
            for j in range(len(linearfeatures)):  # Loop through all feature points
                feat_point = Point(linearfeatures[j])  # Make a Shapely point
                if loc.distance(feat_point) < dist:
                    dist = loc.distance(feat_point)  # Get the shortest distance

            cur_cell.add_attribute("ACC_" + att_name + "_RES",
                                   ubmethods.calculate_accessibility_factor(dist, params[0]))
            cur_cell.add_attribute("ACC_" + att_name + "_COM",
                                   ubmethods.calculate_accessibility_factor(dist, params[1]))
            cur_cell.add_attribute("ACC_" + att_name + "_IND",
                                   ubmethods.calculate_accessibility_factor(dist, params[2]))
            cur_cell.add_attribute("ACC_" + att_name + "_ORC",
                                   ubmethods.calculate_accessibility_factor(dist, params[3]))
        return True

    def determine_land_use_types(self):
        """Analyses based on user inputs the land use categories for active, passive and constrained types and returns
        three specific lists of categories.

        :return: active, passive and constrained, [ ] lists containing category names.
        """
        active = ['Residential', 'Commercial', 'Offices Res Mix', 'Light Industry', 'Heavy Industry']   # ALWAYS ACTIVE
        passive = []
        constrained = ['Water']
        for luc in self.zoning_passive_luc:
            passive.append(ubglobals.LANDUSENAMES[int(luc)])
        for luc in self.zoning_constrained_luc:
            constrained.append(ubglobals.LANDUSENAMES[int(luc)])
        return active, passive, constrained

    def calculate_employment_from_land_use(self, cell, res):
        """Calculates the total employment in a cell based on the land use data. The current cell's land use
        is passed to the function to calculate based on employment densities specified by the user input.

        :param cell: The UBComponent() object of the current cell to analyse.
        :param res: cell size [m]
        :return: Nothing, the cell object's attribute list is updated to include "Base_EMP"
        """
        base_luc = cell.get_attribute("Base_LUC")
        if base_luc == "Commercial":
            cell.add_attribute("Base_EMP", int(self.employ_land_comfactor * (res * res)/10000.0))
        elif base_luc == "Offices Res Mix":
            cell.add_attribute("Base_EMP", int(self.employ_land_officefactor * (res * res)/10000.0))
        else:
            cell.add_attribute("Base_EMP", int(self.employ_land_indfactor * (res * res)/10000.0))
        return True

    def calculate_employment_from_population(self, cellslist, res):
        """Calculates the employment as a proportion of employment and returns an employee density for each land
        use based on the factors used.

        :param cellslist: the list of case study cells
        :param res: resolution of the cell
        :return:
        """
        # ANALYZE FREQUENCIES AND TOTALS ACROSS MAP
        total_pop = 0
        total_luc = [0, 0, 0]    # COM, LI/HI, ORC
        cellarea = res * res
        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            total_pop += cur_cell.get_attribute("Base_POP")
            if cur_cell.get_attribute("Base_LUC") == "Commercial":
                total_luc[0] += cellarea
            elif cur_cell.get_attribute("Base_LUC") == "Offices Res Mix":
                total_luc[2] += cellarea
            elif cur_cell.get_attribute("Base_LUC") in ["Light Industry", "Heavy Industry"]:
                total_luc[1] += cellarea
            else:
                pass

        # CALCULATE DENSITIES FOR EACH MAIN EMPLOYMENT SECTOR [jobs/cell]
        emp_com = self.employ_pop_comfactor * total_pop / (total_luc[0] / 10000.0) * (cellarea / 10000.0)
        emp_ind = self.employ_pop_indfactor * total_pop / (total_luc[1] / 10000.0) * (cellarea / 10000.0)
        emp_orc = self.employ_pop_officefactor * total_pop / (total_luc[2] / 10000.0) * (cellarea / 10000.0)

        # ASSIGN TO ALL BLOCKS
        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            if cur_cell.get_attribute("Base_LUC") == "Commercial":
                cur_cell.add_attribute("Base_EMP", emp_com)
            elif cur_cell.get_attribute("Base_LUC") == "Offices Res Mix":
                cur_cell.add_attribute("Base_EMP", emp_orc)
            elif cur_cell.get_attribute("Base_LUC") in ["Light Industry", "Heavy Industry"]:
                cur_cell.add_attribute("Base_EMP", emp_ind)
            else:
                cur_cell.add_attribute("Base_EMP", 0)
        return True

    def determine_dominant_landusecat(self, lucdata):
        """Analyses the available LUC data based on frequency and returns category with the highest frequency.

        :param lucdata: the lucdatamatrix containing the section of geographic data currently being analysed
        :return: luc_class (the dominant land use category), activity (the proportion of cell space occupied by data)
        """
        lucprop, activity = ubmethods.calculate_frequency_of_lu_classes(lucdata)
        if activity == 0:
            return None, 0
        else:
            luc_class = ubglobals.LANDUSENAMES[lucprop.index(max(lucprop))]
        return luc_class, activity

    def create_cell_face(self, x, y, cellsize, id, boundary):
        """Creates the Cell Face, the polygon of the cell as a UBVector

        :param x: The starting x coordinate (on 0,0 origin)
        :param y: The starting y coordinate (on 0,0 origin)
        :param cellsize: Cell Size size [m]
        :param id: the current ID number to be assigned to the Block
        :param boundary: A Shapely polygon object, used to test if the block face intersects
        with it. Also determines whether to save the Block or not.
        :return: UBVector object containing the BlockID attribute and geometry
        """
        # Define points
        n1 = (x * cellsize, y * cellsize, 0)  # Bottom left (x, y, z)
        n2 = ((x + 1) * cellsize, y * cellsize, 0)  # Bottom right
        n3 = ((x + 1) * cellsize, (y + 1) * cellsize, 0)  # Top right
        n4 = (x * cellsize, (y + 1) * cellsize, 0)  # Top left

        # Create the Shapely Polygon and test against the boundary to determine active/inactive.
        cellpoly = Polygon((n1[:2], n2[:2], n3[:2], n4[:2]))
        if Polygon.intersects(boundary, cellpoly):
            # Define edges
            e1 = (n1, n2)  # Bottom left to bottom right
            e2 = (n2, n3)  # Bottom right to top right
            e3 = (n3, n4)  # Top right to top left
            e4 = (n4, n1)  # Top left to bottom left

            # Define the UrbanBEATS Vector Asset
            cell_attr = ubdata.UBVector((n1, n2, n3, n4, n1), (e1, e2, e3, e4))
            cell_attr.add_attribute("CellID", int(id))  # ATTRIBUTE: Block Identification
            return cell_attr
        else:
            # Block not within boundary, do not return anything
            return None

