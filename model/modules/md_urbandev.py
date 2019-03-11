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
        self.zoning_passive_luc = [5, 6, 7, 8, 9, 10, 11, 12]   # These are numerical encodings of LUC categories
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
                        current_cell.change_attribute("Base_LUC", "Unclassified")
                    else:
                        current_cell.add_attribute("Base_LUC", landuse_cat)
                        current_cell.add_attribute("Active", float(activity))
                else:   # Single value from landusedata matrix
                    landuse_cat = ubglobals.LANDUSENAMES[int(landusedatamatrix - 1)]
                    current_cell.add_attribute("Base_LUC", landuse_cat)
                    current_cell.add_attribute("Active", 1.0)

            map_attr.set_attribute("HasLUC", 1)
        else:
            map_attr.set_attribute("HasLUC", 1)

        # - 2.3 - POPULATION ---
        # STEP 2.3.1 :: Load Population Map
        

        # STEP 2.3.2 :: Transfer Population to Cells


        # - 2.4 - EMPLOYMENT ---
        # STEP 2.4.1 :: Calculate/Load Employment


        self.notify("Current End of Module")
        print ("Current end of module")
        return True

    def determine_dominant_landusecat(self, lucdata):
        """Analyses the available LUC data based on frequency and returns category with the highest frequency."""
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

