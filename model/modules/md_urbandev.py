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
import numpy as np
from shapely.geometry import Polygon, Point

# --- URBANBEATS LIBRARY IMPORTS ---
from ubmodule import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
import model.ublibs.ubmcda as ubmcda
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

        # Passive and Constrained Land Uses
        self.create_parameter("zoning_passive_luc", LISTDOUBLE, "Land use categories in passive group of uses")
        self.create_parameter("zoning_constrained_luc", LISTDOUBLE, "Land use categories in constrained group")
        self.zoning_passive_luc = [5, 6, 7, 8, 9, 10, 11, 12, 14, 15]   # These are numerical encodings of LUC categories
        self.zoning_constrained_luc = []                        # refer to ubglobals.py for key

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

        # --- TAB 1 - SPATIAL RELATIONSHIPS: ACCESSIBILITY ---
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
        self.access_roads_weight = 1.0
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
        self.access_rail_weight = 1.0
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
        self.access_waterways_weight = 1.0
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
        self.access_lakes_weight = 1.0
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
        self.access_pos_weight = 1.0
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
        self.access_poi_weight = 1.0
        self.access_poi_res = 1
        self.access_poi_com = 1
        self.access_poi_ind = 1
        self.access_poi_offices = 1
        self.access_poi_ares = 0.4
        self.access_poi_acom = 0.4
        self.access_poi_aind = 0.4
        self.access_poi_aoffices = 0.4

        # Accessibility to Public Transport Hubs (PTHs)
        self.create_parameter("access_pth_include", BOOL, "Include accessibility assessment to nearest pth?")
        self.create_parameter("access_pth_data", STRING, "data set to use for pth.")
        self.create_parameter("access_pth_weight", DOUBLE, "Weight assigned to the importance of pth access")
        self.create_parameter("access_pth_res", BOOL, "consider for residential?")
        self.create_parameter("access_pth_com", BOOL, "consider for commercial?")
        self.create_parameter("access_pth_ind", BOOL, "consider for industrial?")
        self.create_parameter("access_pth_offices", BOOL, "consider for offices?")
        self.create_parameter("access_pth_ares", DOUBLE, "a-value for pth access to residential areas")
        self.create_parameter("access_pth_acom", DOUBLE, "a-value for pth access to commercial areas")
        self.create_parameter("access_pth_aind", DOUBLE, "a-value for pth access to industrial areas")
        self.create_parameter("access_pth_aoffices", DOUBLE, "a-value for pth access to offices areas")
        self.access_pth_include = 1
        self.access_pth_data = ""
        self.access_pth_weight = 1.0
        self.access_pth_res = 1
        self.access_pth_com = 1
        self.access_pth_ind = 1
        self.access_pth_offices = 1
        self.access_pth_ares = 0.4
        self.access_pth_acom = 0.4
        self.access_pth_aind = 0.4
        self.access_pth_aoffices = 0.4

        # --- TAB 2 - SPATIAL RELATIONSHIPS: SUITABILITY ---
        self.create_parameter("suit_export", BOOL, "export the created suitability map?")
        self.suit_export = 1

        # Suitability Criteria
        self.create_parameter("suit_elevation_data", STRING, "dataset to use for slope")
        self.create_parameter("suit_slope_include", BOOL, "include slope assessment in suitability?")
        self.create_parameter("suit_slope_weight", DOUBLE, "weight assigned to slope in suitability assessment")
        self.suit_elevation_data = ""
        self.suit_slope_include = 1
        self.suit_slope_weight = 5.0

        self.create_parameter("suit_aspect_include", BOOL, "include slope assessment in suitability?")
        self.create_parameter("suit_aspect_weight", DOUBLE, "weight assigned to slope in suitability assessment")
        self.suit_aspect_include = 1
        self.suit_aspect_weight = 5.0

        self.create_parameter("suit_soil_include", BOOL, "include soil assessment in suitability?")
        self.create_parameter("suit_soil_data", STRING, "dataset to use for soil")
        self.create_parameter("suit_soil_weight", DOUBLE, "weight assigned to soil in suitability assessment")
        self.suit_soil_include = 1
        self.suit_soil_data = ""
        self.suit_soil_weight = 5.0

        self.create_parameter("suit_gw_include", BOOL, "include groundwater assessment in suitability?")
        self.create_parameter("suit_gw_data", STRING, "dataset to use for groundwater")
        self.create_parameter("suit_gw_weight", DOUBLE, "weight assigned to groundwater in suitability assessment")
        self.suit_gw_include = 1
        self.suit_gw_data = ""
        self.suit_gw_weight = 5.0

        self.create_parameter("suit_custom_include", BOOL, "include custom1 assessment in suitability?")
        self.create_parameter("suit_custom_data", STRING, "dataset to use for custom1")
        self.create_parameter("suit_custom_weight", DOUBLE, "weight assigned to custom1 in suitability assessment")
        self.suit_custom_include = 1
        self.suit_custom_data = ""
        self.suit_custom_weight = 5.0

        # SUITABILITY - SLOPE
        # The concept for slope is based on a maximum allowable slope. Suitability decreases from 100% at 0% slope to
        # 0% at the maximum threshold. One parameter per land use + trend + mid-point.
        self.create_parameter("slope_trend", STRING, "trend to use for in between values on slope scale")
        self.create_parameter("slope_midpoint", BOOL, "include mid-point value for suitability calcs?")
        self.create_parameter("slope_res", DOUBLE, "threshold % at which slope no longer suitable for RES land use")
        self.create_parameter("slope_com", DOUBLE, "threshold % at which slope no longer suitable for COM land use")
        self.create_parameter("slope_ind", DOUBLE, "threshold % at which slope no longer suitable for IND land use")
        self.create_parameter("slope_orc", DOUBLE, "threshold % at which slope no longer suitable for ORC land use")
        self.create_parameter("slope_res_mid", DOUBLE, "mid-point value of slope for RES land use")
        self.create_parameter("slope_com_mid", DOUBLE, "mid-point value of slope for COM land use")
        self.create_parameter("slope_ind_mid", DOUBLE, "mid-point value of slope for IND land use")
        self.create_parameter("slope_orc_mid", DOUBLE, "mid-point value of slope for ORC land use")
        self.slope_trend = "L"  # L (Linear), Q (Quadratic), C (Cubic), S (sigmoid), T (triangular), IT (inverse tri)
        self.slope_midpoint = 1
        self.slope_res = 25.0
        self.slope_com = 25.0
        self.slope_ind = 25.0
        self.slope_orc = 25.0
        self.slope_res_mid = 12.5
        self.slope_com_mid = 12.5
        self.slope_ind_mid = 12.5
        self.slope_orc_mid = 12.5

        # SUITABILITY - ASPECT
        # The concept for Aspect is based on the compass rose. Suitability is interpolated between the different
        # cardinal directions as specified by the user, e.g. N-W, N-E, S-W, S-E.
        self.create_parameter("aspect_res_north", DOUBLE, "suitability value for north-facing aspects in RES land use")
        self.create_parameter("aspect_res_east", DOUBLE, "suitability value for north-facing aspects in RES land use")
        self.create_parameter("aspect_res_south", DOUBLE, "suitability value for north-facing aspects in RES land use")
        self.create_parameter("aspect_res_west", DOUBLE, "suitability value for north-facing aspects in RES land use")
        self.aspect_res_north = 0.0
        self.aspect_res_east = 80.0
        self.aspect_res_south = 100.0
        self.aspect_res_west = 40.0

        self.create_parameter("aspect_com_north", DOUBLE, "suitability value for north-facing aspects in com land use")
        self.create_parameter("aspect_com_east", DOUBLE, "suitability value for north-facing aspects in com land use")
        self.create_parameter("aspect_com_south", DOUBLE, "suitability value for north-facing aspects in com land use")
        self.create_parameter("aspect_com_west", DOUBLE, "suitability value for north-facing aspects in com land use")
        self.aspect_com_north = 0.0
        self.aspect_com_east = 80.0
        self.aspect_com_south = 100.0
        self.aspect_com_west = 40.0

        self.create_parameter("aspect_ind_north", DOUBLE, "suitability value for north-facing aspects in ind land use")
        self.create_parameter("aspect_ind_east", DOUBLE, "suitability value for north-facing aspects in ind land use")
        self.create_parameter("aspect_ind_south", DOUBLE, "suitability value for north-facing aspects in ind land use")
        self.create_parameter("aspect_ind_west", DOUBLE, "suitability value for north-facing aspects in ind land use")
        self.aspect_ind_north = 0.0
        self.aspect_ind_east = 80.0
        self.aspect_ind_south = 100.0
        self.aspect_ind_west = 40.0

        self.create_parameter("aspect_orc_north", DOUBLE, "suitability value for north-facing aspects in orc land use")
        self.create_parameter("aspect_orc_east", DOUBLE, "suitability value for north-facing aspects in orc land use")
        self.create_parameter("aspect_orc_south", DOUBLE, "suitability value for north-facing aspects in orc land use")
        self.create_parameter("aspect_orc_west", DOUBLE, "suitability value for north-facing aspects in orc land use")
        self.aspect_orc_north = 0.0
        self.aspect_orc_east = 80.0
        self.aspect_orc_south = 100.0
        self.aspect_orc_west = 40.0

        # SUITABILITY - SOIL CLASSIFICATION
        # A histogram representation, discrete suitabilities based on the type of soil, suitability is simply assigned
        # according to soil type registered.
        self.create_parameter("soil_res_sand", DOUBLE, "suitability value for sand soils in RES land use")
        self.create_parameter("soil_res_sandclay", DOUBLE, "suitability value for sandy clay soils in RES land use")
        self.create_parameter("soil_res_medclay", DOUBLE, "suitability value for med. clay soils in RES land use")
        self.create_parameter("soil_res_heavyclay", DOUBLE, "suitability value for heavy clay soils in RES land use")
        self.soil_res_sand = 100.0
        self.soil_res_sandclay = 100.0
        self.soil_res_medclay = 80.0
        self.soil_res_heavyclay = 60.0

        self.create_parameter("soil_com_sand", DOUBLE, "suitability value for sand soils in com land use")
        self.create_parameter("soil_com_sandclay", DOUBLE, "suitability value for sandy clay soils in com land use")
        self.create_parameter("soil_com_medclay", DOUBLE, "suitability value for med. clay soils in com land use")
        self.create_parameter("soil_com_heavyclay", DOUBLE, "suitability value for heavy clay soils in com land use")
        self.soil_com_sand = 100.0
        self.soil_com_sandclay = 100.0
        self.soil_com_medclay = 80.0
        self.soil_com_heavyclay = 60.0

        self.create_parameter("soil_ind_sand", DOUBLE, "suitability value for sand soils in ind land use")
        self.create_parameter("soil_ind_sandclay", DOUBLE, "suitability value for sandy clay soils in ind land use")
        self.create_parameter("soil_ind_medclay", DOUBLE, "suitability value for med. clay soils in ind land use")
        self.create_parameter("soil_ind_heavyclay", DOUBLE, "suitability value for heavy clay soils in ind land use")
        self.soil_ind_sand = 100.0
        self.soil_ind_sandclay = 100.0
        self.soil_ind_medclay = 100.0
        self.soil_ind_heavyclay = 100.0

        self.create_parameter("soil_orc_sand", DOUBLE, "suitability value for sand soils in orc land use")
        self.create_parameter("soil_orc_sandclay", DOUBLE, "suitability value for sandy clay soils in orc land use")
        self.create_parameter("soil_orc_medclay", DOUBLE, "suitability value for med. clay soils in orc land use")
        self.create_parameter("soil_orc_heavyclay", DOUBLE, "suitability value for heavy clay soils in orc land use")
        self.soil_orc_sand = 100.0
        self.soil_orc_sandclay = 100.0
        self.soil_orc_medclay = 60.0
        self.soil_orc_heavyclay = 60.0

        # SUITABILITY - DEPTH TO GROUNDWATER TABLE [m]
        # Like the slope, suitability for groundwater ranges from 0% suitable when groundwater table at surface 0m to
        # 100% beyond a certain threshold, parameters here indicate the threshold.
        self.create_parameter("gw_trend", STRING, "trend to use for in-between values")
        self.create_parameter("gw_midpoint", BOOL, "include mid-point value for suitability scale?")
        self.create_parameter("gw_res", DOUBLE, "threshold % at which groundwater no longer suitable for RES land use")
        self.create_parameter("gw_com", DOUBLE, "threshold % at which groundwater no longer suitable for COM land use")
        self.create_parameter("gw_ind", DOUBLE, "threshold % at which groundwater no longer suitable for IND land use")
        self.create_parameter("gw_orc", DOUBLE, "threshold % at which groundwater no longer suitable for ORC land use")
        self.create_parameter("gw_res_mid", DOUBLE, "mid-point suitability for RES land use")
        self.create_parameter("gw_com_mid", DOUBLE, "mid-point suitability for COM land use")
        self.create_parameter("gw_ind_mid", DOUBLE, "mid-point suitability for IND land use")
        self.create_parameter("gw_orc_mid", DOUBLE, "mid-point suitability for ORC land use")
        self.gw_trend = "L"  # L (Linear), Q (Quadratic), C (Cubic), S (sigmoid), T (triangular), IT (inverse tri)
        self.gw_midpoint = 1
        self.gw_res = 10.0
        self.gw_com = 10.0
        self.gw_ind = 10.0
        self.gw_orc = 10.0
        self.gw_res_mid = 5.0
        self.gw_com_mid = 5.0
        self.gw_ind_mid = 5.0
        self.gw_orc_mid = 5.0

        # SUITABILITY - CUSTOM CRITERION
        # Users can select a minimum/maximum threshold, a custom mid-point and then assign suitabilities in forward
        # or reverse order.
        self.create_parameter("custom_trend", STRING, "trend to use for the suitability scaling")
        self.create_parameter("custom_midpoint", BOOL, "mid-point value to use if this trend is selected")
        self.create_parameter("custom_res_min", DOUBLE, "minimum threshold at which suitability is 0%")
        self.create_parameter("custom_res_max", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_res_mid", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_com_min", DOUBLE, "minimum threshold at which suitability is 0%")
        self.create_parameter("custom_com_max", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_com_mid", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_ind_min", DOUBLE, "minimum threshold at which suitability is 0%")
        self.create_parameter("custom_ind_max", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_ind_mid", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_orc_min", DOUBLE, "minimum threshold at which suitability is 0%")
        self.create_parameter("custom_orc_max", DOUBLE, "maximum threshold at which suitability is 0%")
        self.create_parameter("custom_orc_mid", DOUBLE, "maximum threshold at which suitability is 0%")
        self.custom_trend = "L"  # L (Linear), Q (Quadratic), C (Cubic), S (sigmoid), M (midpoint), IQ/IC (inverse)
        self.custom_midpoint = 0
        self.custom_res_min = 0.0
        self.custom_res_max = 0.0
        self.custom_res_mid = 0.0
        self.custom_com_min = 0.0
        self.custom_com_max = 0.0
        self.custom_com_mid = 0.0
        self.custom_ind_min = 0.0
        self.custom_ind_max = 0.0
        self.custom_ind_mid = 0.0
        self.custom_orc_min = 0.0
        self.custom_orc_max = 0.0
        self.custom_orc_mid = 0.0

        # --- TAB 3 - SPATIAL RELATIONSHIPS: ZONING ---
        self.create_parameter("zoning_export", BOOL, "export aggregated zoning maps for each land use?")
        self.zoning_export = 1

        # GENERAL Zoning rules for active land uses
        self.create_parameter("zoning_rules_resmap", STRING, "Zoning map for designating residential uses")
        self.create_parameter("zoning_rules_resauto", BOOL, "Auto-determine residential regions?")
        self.create_parameter("zoning_rules_reslimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_respassive", BOOL, "Include all passive areas?")
        self.zoning_rules_resmap = ""
        self.zoning_rules_resauto = 1
        self.zoning_rules_reslimit = 0
        self.zoning_rules_respassive = 1

        self.create_parameter("zoning_rules_commap", STRING, "Zoning map for designating comidential uses")
        self.create_parameter("zoning_rules_comauto", BOOL, "Auto-determine comidential regions?")
        self.create_parameter("zoning_rules_comlimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_compassive", BOOL, "Include all passive areas?")
        self.zoning_rules_commap = ""
        self.zoning_rules_comauto = 1
        self.zoning_rules_comlimit = 0
        self.zoning_rules_compassive = 1

        self.create_parameter("zoning_rules_indmap", STRING, "Zoning map for designating indidential uses")
        self.create_parameter("zoning_rules_indauto", BOOL, "Auto-determine indidential regions?")
        self.create_parameter("zoning_rules_indlimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_indpassive", BOOL, "Include all passive areas?")
        self.zoning_rules_indmap = ""
        self.zoning_rules_indauto = 1
        self.zoning_rules_indlimit = 0
        self.zoning_rules_indpassive = 1

        self.create_parameter("zoning_rules_officesmap", STRING, "Zoning map for designating officesidential uses")
        self.create_parameter("zoning_rules_officesauto", BOOL, "Auto-determine officesidential regions?")
        self.create_parameter("zoning_rules_officeslimit", BOOL, "Limit zoning to current base year active area?")
        self.create_parameter("zoning_rules_officespassive", BOOL, "Include all passive areas?")
        self.zoning_rules_officesmap = ""
        self.zoning_rules_officesauto = 1
        self.zoning_rules_officeslimit = 0
        self.zoning_rules_officespassive = 1

        # Additional Zoning Constraints
        self.create_parameter("zoning_water", STRING, "water bodies map to use in creating zoning.")
        self.create_parameter("zoning_heritage", STRING, "historical significant/heritage.")
        self.create_parameter("zoning_public", STRING, "historical significant/heritage.")
        self.create_parameter("zoning_enviro", STRING, "environmental significant overlay usable for zoning.")
        self.create_parameter("zoning_flood", STRING, "land subject to inundation overlay.")
        self.create_parameter("zoning_custom", STRING, "custom map that can be used to further constrain development.")
        self.zoning_water = ""
        self.zoning_heritage = ""
        self.zoning_public = ""
        self.zoning_enviro = ""
        self.zoning_flood = ""
        self.zoning_custom = ""

        self.create_parameter("zoning_heritage_res", BOOL, "disallow residential in heritage areas?")
        self.create_parameter("zoning_heritage_com", BOOL, "disallow commercial in heritage areas?")
        self.create_parameter("zoning_heritage_ind", BOOL, "disallow industrial in heritage areas?")
        self.create_parameter("zoning_heritage_orc", BOOL, "disallow mixed development in heritage areas?")
        self.zoning_heritage_res = 1
        self.zoning_heritage_com = 0
        self.zoning_heritage_ind = 1
        self.zoning_heritage_orc = 0

        self.create_parameter("zoning_public_res", BOOL, "disallow residential in public areas?")
        self.create_parameter("zoning_public_com", BOOL, "disallow commercial in public areas?")
        self.create_parameter("zoning_public_ind", BOOL, "disallow industrial in public areas?")
        self.create_parameter("zoning_public_orc", BOOL, "disallow mixed development in public areas?")
        self.zoning_public_res = 1
        self.zoning_public_com = 0
        self.zoning_public_ind = 1
        self.zoning_public_orc = 0

        self.create_parameter("zoning_enviro_res", BOOL, "disallow residential in enviro areas?")
        self.create_parameter("zoning_enviro_com", BOOL, "disallow commercial in enviro areas?")
        self.create_parameter("zoning_enviro_ind", BOOL, "disallow industrial in enviro areas?")
        self.create_parameter("zoning_enviro_orc", BOOL, "disallow mixed development in enviro areas?")
        self.zoning_enviro_res = 1
        self.zoning_enviro_com = 1
        self.zoning_enviro_ind = 1
        self.zoning_enviro_orc = 1

        self.create_parameter("zoning_flood_res", BOOL, "disallow residential in flood areas?")
        self.create_parameter("zoning_flood_com", BOOL, "disallow commercial in flood areas?")
        self.create_parameter("zoning_flood_ind", BOOL, "disallow industrial in flood areas?")
        self.create_parameter("zoning_flood_orc", BOOL, "disallow mixed development in flood areas?")
        self.zoning_flood_res = 1
        self.zoning_flood_com = 0
        self.zoning_flood_ind = 1
        self.zoning_flood_orc = 0

        self.create_parameter("zoning_custom_res", BOOL, "disallow residential in custom areas?")
        self.create_parameter("zoning_custom_com", BOOL, "disallow commercial in custom areas?")
        self.create_parameter("zoning_custom_ind", BOOL, "disallow industrial in custom areas?")
        self.create_parameter("zoning_custom_orc", BOOL, "disallow mixed development in custom areas?")
        self.zoning_custom_res = 1
        self.zoning_custom_com = 0
        self.zoning_custom_ind = 1
        self.zoning_custom_orc = 0

        # --- TAB 4 - NEIGHBOURHOOD INTERACTION
        self.create_parameter("function_ids", LISTDOUBLE, "list of function ids containing interaction data")
        self.create_parameter("edge_effects_method", STRING, "method for accounting for edge effects")
        self.function_ids = []
        self.edge_effects_method = "NA"     # NA = no accounting, AVG = average, PP = proportioning, PPAVG=both

        # ADVANCED PARAMETERS
        self.global_offsets = None

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
        self.global_offsets = (xmin, ymin)
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
        municipalities = []
        if self.lga_inputmap == "":
            self.notify("Region is treated as a single municipality")
            print ("Region is treated as a single municipality")
            map_attr.add_attribute("HasGEOPOLITICAL", 0)
        else:
            self.notify("Loading and Assigning Municipalities")
            print("Loading and Assigning Municipalities")
            map_attr.add_attribute("HasGEOPOLITICAL", 1)
            geopol_map = self.datalibrary.get_data_with_id(self.lga_inputmap)
            fullfilepath = geopol_map.get_data_file_path() + geopol_map.get_metadata("filename")
            municipalities = ubspatial.import_polygonal_map(fullfilepath, "native", "Municipality", self.global_offsets)

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
                    current_cell.add_attribute("LUC_Type", "Fixed")
                else:
                    current_cell.add_attribute("LUC_Type", "UNDEFINED")

                # STEP 2.2.4 :: ASSIGN THE ZONING=TRUE ATTRIBUTE BY DEFAULT - masked later in Section 2.8
                current_cell.add_attribute("ZONE_RES", 1)
                current_cell.add_attribute("ZONE_COM", 1)
                current_cell.add_attribute("ZONE_IND", 1)
                current_cell.add_attribute("ZONE_ORC", 1)

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
                col_start = int(current_cell.get_attribute("OriginX") / pop_res)
                row_start = int(current_cell.get_attribute("OriginY") / pop_res)
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

        # - 2.5 - SPATIAL RELATIONSHIPS - ACCESSIBILITY
        # - 2.5.1 - Determine individual accessibility maps
        # self.notify("Entering Accessibility Calculations")
        # print("Entering Accessibility Calculations")
        #
        # map_attr.add_attribute("ACCESS_ROAD", 0)
        # if self.access_roads_include:
        #     aj = [float(self.access_roads_res * self.access_roads_ares),
        #           float(self.access_roads_com * self.access_roads_acom),
        #           float(self.access_roads_ind * self.access_roads_aind),
        #           float(self.access_roads_offices * self.access_roads_aoffices)]
        #     self.calculate_accessibility_linearfeatures(self.access_roads_data, map_attr, aj, cellslist, "ROAD")
        #
        # map_attr.add_attribute("ACCESS_RAIL", 0)
        # if self.access_rail_include:
        #     aj = [float(self.access_rail_res * self.access_rail_ares),
        #           float(self.access_rail_com * self.access_rail_acom),
        #           float(self.access_rail_ind * self.access_rail_aind),
        #           float(self.access_rail_offices * self.access_rail_aoffices)]
        #     self.calculate_accessibility_linearfeatures(self.access_rail_data, map_attr, aj, cellslist, "RAIL")
        #
        # map_attr.add_attribute("ACCESS_WWAY", 0)
        # if self.access_waterways_include:
        #     aj = [float(self.access_waterways_res * self.access_waterways_ares),
        #           float(self.access_waterways_com * self.access_waterways_acom),
        #           float(self.access_waterways_ind * self.access_waterways_aind),
        #           float(self.access_waterways_offices * self.access_waterways_aoffices)]
        #     self.calculate_accessibility_linearfeatures(self.access_waterways_data, map_attr, aj, cellslist, "WWAY")
        #
        # map_attr.add_attribute("ACCESS_LAKE", 0)
        # if self.access_lakes_include:
        #     aj = [float(self.access_lakes_res * self.access_lakes_ares),
        #           float(self.access_lakes_com * self.access_lakes_acom),
        #           float(self.access_lakes_ind * self.access_lakes_aind),
        #           float(self.access_lakes_offices * self.access_lakes_aoffices)]
        #     self.calculate_accessibility_polygonfeatures(self.access_lakes_data, map_attr, aj, cellslist, "LAKE",
        #                                                  Landuses=["Water"])
        #
        # map_attr.add_attribute("ACCESS_POSS", 0)
        # if self.access_pos_include:
        #     aj = [float(self.access_pos_res * self.access_pos_ares),
        #           float(self.access_pos_com * self.access_pos_acom),
        #           float(self.access_pos_ind * self.access_pos_aind),
        #           float(self.access_pos_offices * self.access_pos_aoffices)]
        #     self.calculate_accessibility_polygonfeatures(self.access_pos_data, map_attr, aj, cellslist, "POSS",
        #                                                  Landuses=["Parks and Gardens", "Reserves and Floodway",
        #                                                            "Forest"])
        #
        # map_attr.add_attribute("ACCESS_POIS", 0)
        # if self.access_poi_include:
        #     aj = [float(self.access_poi_res * self.access_poi_ares),
        #           float(self.access_poi_com * self.access_poi_acom),
        #           float(self.access_poi_ind * self.access_poi_aind),
        #           float(self.access_poi_offices * self.access_poi_aoffices)]
        #     self.calculate_accessibility_pointfeatures(self.access_poi_data, map_attr, aj, cellslist, "POIS")
        #
        # map_attr.add_attribute("ACCESS_PTHS", 0)
        # if self.access_pth_include:
        #     aj = [float(self.access_pth_res * self.access_pth_ares),
        #           float(self.access_pth_com * self.access_pth_acom),
        #           float(self.access_pth_ind * self.access_pth_aind),
        #           float(self.access_pth_offices * self.access_pth_aoffices)]
        #     self.calculate_accessibility_pointfeatures(self.access_pth_data, map_attr, aj, cellslist, "PTHS")
        #
        # # - 2.5.2 - Combine Accessibility criteria into full map
        # accessibility_weights = [float(self.access_roads_weight * self.access_roads_include),
        #                          float(self.access_rail_weight * self.access_rail_include),
        #                          float(self.access_waterways_weight * self.access_waterways_include),
        #                          float(self.access_lakes_weight * self.access_lakes_include),
        #                          float(self.access_pos_weight * self.access_pos_include),
        #                          float(self.access_poi_weight * self.access_poi_include),
        #                          float(self.access_pth_weight * self.access_pth_include)]
        #
        # print "ACCESS WEIGHTS", accessibility_weights
        # accessibility_weights = ubmethods.normalize_weights(accessibility_weights, "SUM")   # 0 to 1 normalize
        #
        # accessibility_attributes = ["ACC_ROAD", "ACC_RAIL", "ACC_WWAY", "ACC_LAKE", "ACC_POSS", "ACC_POIS", "ACC_PTHS"]
        # print "ACCESS WEIGHTS", accessibility_weights
        #
        # # Loop across blocks, get the five attributes and calculate total accessibility
        # for i in range(len(cellslist)):
        #     final_acc_res, final_acc_com, final_acc_ind, final_acc_orc = 0, 0, 0, 0
        #     for acc in range(len(accessibility_attributes)):
        #         val_res = cellslist[i].get_attribute(accessibility_attributes[acc]+"_RES")
        #         if val_res is None: val_res = 0
        #         final_acc_res += accessibility_weights[acc] * val_res
        #
        #         val_com = cellslist[i].get_attribute(accessibility_attributes[acc] + "_COM")
        #         if val_com is None: val_com = 0
        #         final_acc_com += accessibility_weights[acc] * val_com
        #
        #         val_ind = cellslist[i].get_attribute(accessibility_attributes[acc] + "_IND")
        #         if val_ind is None: val_ind = 0
        #         final_acc_ind += accessibility_weights[acc] * val_ind
        #
        #         val_orc = cellslist[i].get_attribute(accessibility_attributes[acc] + "_ORC")
        #         if val_orc is None: val_orc = 0
        #         final_acc_orc += accessibility_weights[acc] * val_orc
        #
        #     cellslist[i].add_attribute("ACCESS_RES", final_acc_res)
        #     cellslist[i].add_attribute("ACCESS_COM", final_acc_com)
        #     cellslist[i].add_attribute("ACCESS_IND", final_acc_ind)
        #     cellslist[i].add_attribute("ACCESS_ORC", final_acc_orc)

        # - 2.6 - SPATIAL RELATIONSHIPS - SUITABILITY
        # self.notify("Beginning Suitability calculations...")
        # print("Beginning Suitability calculations...")
        #
        # # - 2.6.1 - Neighbourhood - Determine Immediate Cardinal and Ordinal direction neighbours (use Moore)
        # self.notify("Determining adjacent neighbours")
        # print("Determining adjacent neighbours")
        # for i in range(len(cellslist)):
        #     cellslist[i].add_attribute("NHD_N", 0)
        #     cellslist[i].add_attribute("NHD_NE", 0)
        #     cellslist[i].add_attribute("NHD_E", 0)
        #     cellslist[i].add_attribute("NHD_SE", 0)
        #     cellslist[i].add_attribute("NHD_S", 0)
        #     cellslist[i].add_attribute("NHD_SW", 0)
        #     cellslist[i].add_attribute("NHD_W", 0)
        #     cellslist[i].add_attribute("NHD_NW", 0)
        #     neighbours = []
        #     ixy = ubmethods.get_central_coordinates(cellslist[i])
        #     for j in range(len(cellslist)):     # Oh how I hate to use double for loops....
        #         if cellslist[j] == cellslist[i]:
        #             continue
        #         jxy = ubmethods.get_central_coordinates(cellslist[j])
        #         if abs(ixy[0] - jxy[0]) <= self.cellsize and abs(ixy[1] - jxy[1]) <= self.cellsize:
        #             # ASSIGN THE CARDINAL/ORDINAL DIRECTION
        #             d = ""  # Piece together the direction from dx, dy rules.
        #             if (ixy[1] - jxy[1]) < 0:   # If dy < 0, then jxy is greater i.e NORTH
        #                 d += "N"
        #             elif (ixy[1] - jxy [1]) >0: # if dy > 0, then jxy is less i.e. SOUTH
        #                 d += "S"
        #
        #             if (ixy[0] - jxy[0]) < 0:   # If dx < 0, then jxy is greater i.e. EAST
        #                 d += "E"
        #             elif (ixy[0] - jxy[0]) > 0: # if dx > 0, then jxy is less i.e. WEST
        #                 d += "W"
        #
        #             if d == "":     # DEBUG
        #                 print "Something went wrong!!!"
        #
        #             cellslist[i].add_attribute("NHD_"+d, cellslist[j].get_attribute("CellID"))
        #             neighbours.append(cellslist[j].get_attribute("CellID"))
        #     cellslist[i].add_attribute("AdjacentNH", neighbours)
        #
        # # - 2.6.2 - Load all relevant data sets
        # self.notify("Loading maps for suitability assessment...")
        # print("Loading map for suitability assessment...")
        #
        # map_attr.add_attribute("SUIT_ELEV", 0)
        # if (self.suit_slope_include or self.suit_aspect_include) and self.suit_elevation_data:
        #     # If either criteria has been included, map elevation to cells
        #     elev_dref = self.datalibrary.get_data_with_id(self.suit_elevation_data)
        #     fullfilepath = elev_dref.get_data_file_path() + elev_dref.get_metadata("filename")
        #     elevraster = ubspatial.import_ascii_raster(fullfilepath, self.suit_elevation_data)
        #     elev_offset = ubspatial.calculate_offsets(elevraster, map_attr)
        #     elev_res = elevraster.get_cellsize()
        #     elev_csc = int(self.cellsize / elev_res)     # knowing how many cells wide and tall
        #     map_attr.change_attribute("SUIT_ELEV", 1)
        #
        # map_attr.add_attribute("SUIT_SOIL", 0)
        # if self.suit_soil_include and self.suit_soil_data:
        #     soil_dref = self.datalibrary.get_data_with_id(self.suit_soil_data)
        #     fullfilepath = soil_dref.get_data_file_path() + soil_dref.get_metadata("filename")
        #     soilraster = ubspatial.import_ascii_raster(fullfilepath, self.suit_soil_data)
        #     soil_offset = ubspatial.calculate_offsets(soilraster, map_attr)
        #     soil_res = soilraster.get_cellsize()
        #     soil_csc = int(self.cellsize / soil_res)
        #     map_attr.change_attribute("SUIT_SOIL", 1)
        #
        # map_attr.add_attribute("SUIT_GW", 0)
        # if self.suit_gw_include and self.suit_gw_data:
        #     gw_dref = self.datalibrary.get_data_with_id(self.suit_gw_data)
        #     fullfilepath = gw_dref.get_data_file_path() + gw_dref.get_metadata("filename")
        #     gwraster = ubspatial.import_ascii_raster(fullfilepath, self.suit_gw_data)
        #     gw_offset = ubspatial.calculate_offsets(gwraster, map_attr)
        #     gw_res = gwraster.get_cellsize()
        #     gw_csc = int(self.cellsize / gw_res)
        #     map_attr.change_attribute("SUIT_GW", 1)
        #
        # if self.suit_custom_include and self.suit_custom_data:
        #     pass
        #     # CUSTOM - [TO DO]
        #     # Need to figure out 'data type', 'data format', etc.
        #
        # # - 2.6.3 - ASSIGN ALL DATA TO CELLS
        # self.notify("Assigning data to cells...")
        # print("Assigning data to cells...")
        #
        # nodata_cells_elev, nodata_cells_gw, nodata_cells_soil = [], [], []  # Lists to hold no-data cells
        #
        # for i in range(len(cellslist)):
        #     current_cell = cellslist[i]
        #
        #     # SLOPE AND ASPECT - MAP ELEVATION DATA TO THE CELLS
        #     if (self.suit_slope_include or self.suit_aspect_include) and self.suit_elevation_data:
        #         col_start = int(current_cell.get_attribute("OriginX") / elev_res)
        #         row_start = int(current_cell.get_attribute("OriginY") / elev_res)
        #         elevdatamatrix = elevraster.get_data_square(col_start, row_start, elev_csc, elev_csc)
        #
        #         # TRANSFER ELEVATION TO CELLS
        #         if elev_csc > 1.0:   # Then the cell size greater than the input raster resolution
        #             elevvalues = elevdatamatrix.flatten()
        #             avg_elev, n_elev = 0, 0
        #             for j in elevvalues:
        #                 if j == elevraster.get_nodatavalue():
        #                     continue
        #                 avg_elev += j
        #                 n_elev += 1
        #             if n_elev == 0:
        #                 current_cell.add_attribute("Elevation", -9999)
        #                 nodata_cells_elev.append(current_cell)
        #             else:
        #                 current_cell.add_attribute("Elevation", float(avg_elev / n_elev))
        #         else:   # The cell size is not greater, either smaller or same size as raster resolution
        #             if elevdatamatrix == elevraster.get_nodatavalue():
        #                 current_cell.add_attribute("Elevation", -9999)
        #                 nodata_cells_elev.append(current_cell)
        #             else:
        #                 current_cell.add_attribute("Elevation", elevdatamatrix)
        #
        #     # SOIL CLASSIFICATION - MAP SOIL CLASSES TO THE CELLS
        #     if self.suit_soil_include:      # SOIL CLASSES: 1=sand, 2=sandy clay, 3=medium clay, 4=heavy clay
        #         col_start = int(current_cell.get_attribute("OriginX") / soil_res)
        #         row_start = int(current_cell.get_attribute("OriginY") / soil_res)
        #         soildatamatrix = soilraster.get_data_square(col_start, row_start, soil_csc, soil_csc)
        #
        #         # TRANSFER ELEVATION TO CELLS
        #         if soil_csc > 1.0:      # Cell > raster - need to find dominant class
        #             soilclass = ubmethods.find_dominant_category(soildatamatrix, soilraster.get_nodatavalue())
        #             if soilclass == soilraster.get_nodatavalue():
        #                 current_cell.add_attribute("SoilClass", "Undefined")
        #                 nodata_cells_soil.append(current_cell)
        #             else:
        #                 current_cell.add_attribute("SoilClass", ubglobals.SOILCLASSES[int(soilclass) - 1])
        #         else:       # Cell < raster - only one class
        #             if soildatamatrix == soilraster.get_nodatavalue():
        #                 current_cell.add_attribute("SoilClass", "Undefined")
        #                 nodata_cells_soil.append(current_cell)
        #             else:
        #                 current_cell.add_attribute("SoilClass", ubglobals.SOILCLASSES[int(soildatamatrix) - 1])
        #
        #     # GROUNDWATER DEPTH - MAP GROUNDWATER DEPTHS TO THE CELLS
        #     if self.suit_gw_include:
        #         col_start = int(current_cell.get_attribute("OriginX") / gw_res)
        #         row_start = int(current_cell.get_attribute("OriginY") / gw_res)
        #         gwdatamatrix = gwraster.get_data_square(col_start, row_start, gw_csc, gw_csc)
        #
        #         # TRANSFER GROUNDWATER TO CELLS
        #         if gw_csc > 1.0:
        #             gwvalues = gwdatamatrix.flatten()
        #             avg_gwd, n_gw = 0, 0
        #             for j in gwvalues:
        #                 if j == gwraster.get_nodatavalue():
        #                     continue
        #                 avg_gwd += j
        #                 n_gw += 1
        #             if n_gw == 0:
        #                 current_cell.add_attribute("DepthToGW", -9999)
        #                 nodata_cells_gw.append(current_cell)
        #             else:
        #                 current_cell.add_attribute("DepthToGW", float(avg_gwd / n_gw))
        #         else:
        #             if gwdatamatrix == gwraster.get_nodatavalue():
        #                 current_cell.add_attribute("DepthToGW", -9999)
        #                 nodata_cells_gw.append(current_cell)
        #             else:
        #                 current_cell.add_attribute("DepthToGW", gwdatamatrix)
        #
        #     # CUSTOM DATA SET
        #     if self.suit_custom_include:
        #         pass    # [TO DO]
        #
        # # - 2.6.4 - INFILL MISSING VALUES AND CALCULATE ADDITIONAL INDICATORS (e.g. SLOPE, ASPECT
        # print("Infilling missing values...")
        # if (self.suit_slope_include or self.suit_aspect_include) and self.suit_elevation_data:
        #     self.infill_nodata_values(nodata_cells_elev, "Elevation", "Average", elevraster.get_nodatavalue())
        #     self.calculate_cell_slope_and_aspect(cellslist)
        # if self.suit_soil_data:
        #     self.infill_nodata_values(nodata_cells_soil, "SoilClass", "Categorical", "Undefined")
        # if self.suit_gw_data:
        #     self.infill_nodata_values(nodata_cells_gw, "DepthToGW", "Average", gwraster.get_nodatavalue())
        # if self.suit_custom_data:
        #     pass
        #     # Infill no data values
        #
        # # - 2.6.5 - CALCULATE SUITABILITIES
        # # PREPARE ARRAYS FOR COMBINING SUITABILITY VALUES
        # self.notify("Now calculating suitabilities...")
        # print("Now calculating suitabilities...")
        #
        # # SET UP VALUE-SCALES FOR EACH CRITERIA
        # slope_value_scales = []         # CRITERIA 1 - SLOPE ---------------------------------------------
        # if self.suit_slope_include and self.suit_elevation_data:  # If slope is considered...
        #     xmin_values = [0, 0, 0, 0]
        #     xmax_values = [self.slope_res, self.slope_com, self.slope_ind, self.slope_orc]
        #     if self.slope_midpoint:
        #         mid_points = [self.slope_res_mid, self.slope_com_mid, self.slope_ind_mid, self.slope_orc_mid]
        #     else:
        #         mid_points = None
        #     slope_value_scales = []
        #     for i in range(len(xmin_values)):
        #         if mid_points is None:
        #             vs = ubmcda.ValueScale([xmin_values[i], xmax_values[i]], [1.0, 0.0])    # Slope is reverse linear
        #         else:
        #             vs = ubmcda.ValueScale([xmin_values[i], mid_points[i], xmax_values[i]],
        #                                    [1.0, 0.5, 0.0])
        #         slope_value_scales.append(vs)
        #
        # aspect_value_scales = []        # CRITERIA 2 - ASPECT ---------------------------------------------
        # if self.suit_aspect_include and self.suit_elevation_data:   # If aspect is considered...
        #     y_res = [self.aspect_res_north/100.0, self.aspect_res_east/100.0, self.aspect_res_south/100.0,
        #              self.aspect_res_west/100.0, self.aspect_res_north/100.0]
        #     y_com = [self.aspect_com_north/100.0, self.aspect_com_east/100.0, self.aspect_com_south/100.0,
        #              self.aspect_com_west/100.0, self.aspect_com_north/100.0]
        #     y_ind = [self.aspect_ind_north/100.0, self.aspect_ind_east/100.0, self.aspect_ind_south/100.0,
        #              self.aspect_ind_west/100.0, self.aspect_ind_north/100.0]
        #     y_orc = [self.aspect_orc_north/100.0, self.aspect_orc_east/100.0, self.aspect_orc_south/100.0,
        #              self.aspect_orc_west/100.0, self.aspect_orc_north/100.0]
        #     y_values = [y_res, y_com, y_ind, y_orc]
        #     aspect_value_scales = []
        #     for i in range(len(y_values)):
        #         aspect_value_scales.append(ubmcda.ValueScale([0, 90, 180, 270, 360], y_values[i]))
        #
        # soil_value_scales = []          # CRITERIA 3 - SOIL ---------------------------------------------
        # if self.suit_soil_include and self.suit_soil_data:      # If soil is considered...
        #     y_res = [self.soil_res_sand/100.0, self.soil_res_sandclay/100.0, self.soil_res_medclay/100.0,
        #              self.soil_res_heavyclay/100.0]
        #     y_com = [self.soil_com_sand/100.0, self.soil_com_sandclay/100.0, self.soil_com_medclay/100.0,
        #              self.soil_com_heavyclay/100.0]
        #     y_ind = [self.soil_ind_sand/100.0, self.soil_ind_sandclay/100.0, self.soil_ind_medclay/100.0,
        #              self.soil_ind_heavyclay/100.0]
        #     y_orc = [self.soil_orc_sand/100.0, self.soil_orc_sandclay/100.0, self.soil_orc_medclay/100.0,
        #              self.soil_orc_heavyclay/100.0]
        #     y_values = [y_res, y_com, y_ind, y_orc]
        #     soil_value_scales = []
        #     for i in range(len(y_values)):
        #         soil_value_scales.append(ubmcda.ValueScale(ubglobals.SOILCLASSES, y_values[i]))
        #
        # gw_value_scales = []            # CRITERIA 4 - DEPTH TO GROUNDWATER -----------------------------
        # if self.suit_gw_include and self.suit_gw_data:      # If groundwater is considered...
        #     xmin_values = [0, 0, 0, 0]      # 0m depth for all land uses = 0% suitable
        #     xmax_values = [self.gw_res, self.gw_com, self.gw_ind, self.gw_orc]
        #     if self.gw_midpoint:
        #         mid_points = [self.gw_res_mid, self.gw_com_mid, self.gw_ind_mid, self.gw_orc_mid]
        #     else:
        #         mid_points = None
        #     gw_value_scales = []
        #     for i in range(len(xmin_values)):
        #         if mid_points is None:
        #             vs = ubmcda.ValueScale([xmin_values[i], xmax_values[i]], [0.0, 1.0])  # Slope is reverse linear
        #         else:
        #             vs = ubmcda.ValueScale([xmin_values[i], mid_points[i], xmax_values[i]],
        #                                    [0.0, 0.5, 1.0])
        #         gw_value_scales.append(vs)
        #
        # # if self.suit_custom   # [ TO DO ] # CRITERIA CUSTOM ---------------------------------------------
        #
        # # ASSIGN SUITABILITIES TO CELLS
        # print "Assigning Suitabilities to Cells"
        # map_max_suit = [0, 0, 0, 0]     # Holds the maximum suitability value across the map, updated when necessary
        # for i in range(len(cellslist)):
        #     if cellslist[i].get_attribute("Status") == 0:
        #         continue
        #     # Looping across each cell
        #     suit_values = [[], [], [], []]  # [ [RES], [COM], [IND], [ORC] ]
        #     current_cell = cellslist[i]
        #     print current_cell.get_attribute("CellID")
        #     # - 2.6.5a - SUITABILITY CALCULATION FOR SLOPE
        #     if self.suit_slope_include and self.suit_elevation_data:    # If slope is considered...
        #         cur_slope = float(current_cell.get_attribute("Slope_PCT")/100.0)
        #         suitability = []
        #         for j in range(len(slope_value_scales)):
        #             suitability.append(slope_value_scales[j].return_value_scale(cur_slope))
        #
        #         current_cell.add_attribute("SU_SLOPE_R", suitability[0])
        #         current_cell.add_attribute("SU_SLOPE_C", suitability[1])
        #         current_cell.add_attribute("SU_SLOPE_I", suitability[2])
        #         current_cell.add_attribute("SU_SLOPE_O", suitability[3])
        #
        #         suit_values[0].append(suitability[0] * self.suit_slope_weight)
        #         suit_values[1].append(suitability[1] * self.suit_slope_weight)
        #         suit_values[2].append(suitability[2] * self.suit_slope_weight)
        #         suit_values[3].append(suitability[3] * self.suit_slope_weight)
        #
        #     # - 2.6.5b - SUITABILITY CALCULATION FOR ASPECT
        #     if self.suit_aspect_include and self.suit_elevation_data:
        #         cur_aspect = float(current_cell.get_attribute("Aspect_DEG"))
        #         suitability = []
        #         for j in range(len(aspect_value_scales)):
        #             suitability.append(aspect_value_scales[j].return_value_scale(cur_aspect))
        #         current_cell.add_attribute("SU_ASPCT_R", suitability[0])
        #         current_cell.add_attribute("SU_ASPCT_C", suitability[1])
        #         current_cell.add_attribute("SU_ASPCT_I", suitability[2])
        #         current_cell.add_attribute("SU_ASPCT_O", suitability[3])
        #
        #         suit_values[0].append(suitability[0] * self.suit_aspect_weight)
        #         suit_values[1].append(suitability[1] * self.suit_aspect_weight)
        #         suit_values[2].append(suitability[2] * self.suit_aspect_weight)
        #         suit_values[3].append(suitability[3] * self.suit_aspect_weight)
        #
        #     # - 2.6.5c - SUITABILITY CALCULATION FOR SOIL TYPE
        #     if self.suit_soil_include and self.suit_soil_data:
        #         cur_soil = current_cell.get_attribute("SoilClass")
        #         suitability = []
        #         for j in range(len(soil_value_scales)):
        #             suitability.append(soil_value_scales[j].return_value_scale(cur_soil, option="discrete"))
        #         current_cell.add_attribute("SU_SOIL_R", suitability[0])
        #         current_cell.add_attribute("SU_SOIL_C", suitability[1])
        #         current_cell.add_attribute("SU_SOIL_I", suitability[2])
        #         current_cell.add_attribute("SU_SOIL_O", suitability[3])
        #
        #         suit_values[0].append(suitability[0] * self.suit_soil_weight)
        #         suit_values[1].append(suitability[1] * self.suit_soil_weight)
        #         suit_values[2].append(suitability[2] * self.suit_soil_weight)
        #         suit_values[3].append(suitability[3] * self.suit_soil_weight)
        #
        #     # - 2.6.5d - SUITABILITY CALCULATION FOR GROUNDWATER DEPTH
        #     if self.suit_gw_include and self.suit_gw_data:
        #         cur_gw = current_cell.get_attribute("DepthToGW")
        #         suitability = []
        #         for j in range(len(gw_value_scales)):
        #             suitability.append(gw_value_scales[j].return_value_scale(cur_gw))
        #         current_cell.add_attribute("SU_GWATD_R", suitability[0])
        #         current_cell.add_attribute("SU_GWATD_C", suitability[0])
        #         current_cell.add_attribute("SU_GWATD_I", suitability[0])
        #         current_cell.add_attribute("SU_GWATD_O", suitability[0])
        #
        #         suit_values[0].append(suitability[0] * self.suit_gw_weight)
        #         suit_values[1].append(suitability[1] * self.suit_gw_weight)
        #         suit_values[2].append(suitability[2] * self.suit_gw_weight)
        #         suit_values[3].append(suitability[3] * self.suit_gw_weight)
        #
        #     # - 2.6.5e - SUITABILITY CALCULATION FOR CUSTOM CRITERION
        #     if self.suit_custom_include and self.suit_custom_data:
        #         pass    # [TO DO]
        #
        #     # COMBINED SUITABILITY
        #     current_cell.add_attribute("SUIT_RES", sum(suit_values[0]))
        #     current_cell.add_attribute("SUIT_COM", sum(suit_values[1]))
        #     current_cell.add_attribute("SUIT_IND", sum(suit_values[2]))
        #     current_cell.add_attribute("SUIT_ORC", sum(suit_values[3]))
        #
        #     for j in range(len(suit_values)):                                   # Take the larger suitability
        #         map_max_suit[j] = max(map_max_suit[j], sum(suit_values[j]))     # value and replace in map_max_suit
        #
        # # - 2.6.6 - NORMALIZE SUITABILITY VALUES
        # for i in range(len(cellslist)):
        #     if cellslist[i].get_attribute("Status") == 0:
        #         continue
        #     cellslist[i].change_attribute("SUIT_RES", float(cellslist[i].get_attribute("SUIT_RES") / map_max_suit[0]))
        #     cellslist[i].change_attribute("SUIT_COM", float(cellslist[i].get_attribute("SUIT_COM") / map_max_suit[1]))
        #     cellslist[i].change_attribute("SUIT_IND", float(cellslist[i].get_attribute("SUIT_IND") / map_max_suit[2]))
        #     cellslist[i].change_attribute("SUIT_ORC", float(cellslist[i].get_attribute("SUIT_ORC") / map_max_suit[3]))
        # # ----- END OF SUITABILITY CALCULATIONS -----

        # - 2.8 - SPATIAL RELATIONSHIPS - ZONING
        # Start by loading all relevant zoning maps. Preferably want to do this in one single loop
        # self.notify("Creating Zoning maps for active land uses...")
        # print("Creating Zoning maps for active land uses...")
        #
        # # - 2.8.1 - LOAD ALL RELEVANT MAPS IF NECESSARY AND TRANSFER DATA ACROSS - MASK = TRUE
        # # If the map is not used or doesn't exist, then the polygon list will be empty [], there are four polygonal
        # # lists in total.
        # self.notify("Loading Zoning Maps...")
        # print("Loading Zoning Maps...")
        # respolygons, compolygons, indpolygons, officespolygons = [], [], [], []
        # if not self.zoning_rules_resauto:   # RESIDENTIAL MAP
        #     respolygons = self.get_rings_maps_for_zoning(self.zoning_rules_resmap)
        # if not self.zoning_rules_comauto:  # COMMERCIAL MAP
        #     compolygons = self.get_rings_maps_for_zoning(self.zoning_rules_commap)
        # if not self.zoning_rules_indauto:  # INDUSTRIAL MAP
        #     indpolygons = self.get_rings_maps_for_zoning(self.zoning_rules_indmap)
        # if not self.zoning_rules_officesauto:  # MIXED DEVELOPMENT MAP
        #     officespolygons = self.get_rings_maps_for_zoning(self.zoning_rules_resmap)
        #
        # # - 2.8.2 - Scan through all Blocks, allocate zoning where applicable.
        # # Mark all land uses where a map is not used as having Zoning possibility of 1. This is changed later on.
        # # The land zoning maps represent the FIRST MASK
        # for i in range(len(cellslist)):     # - 2.8.3 - Fixed land use, automatically mask - SECOND MASK
        #     if cellslist[i].get_attribute("LUC_Type") in ["Fixed", "UNDEFINED"]:
        #         cellslist[i].change_attribute("ZONE_RES", 0)  # If fixed or undefined, immediately set to zero
        #         cellslist[i].change_attribute("ZONE_COM", 0)  # no exceptions, if not fixed, move to passive
        #         cellslist[i].change_attribute("ZONE_IND", 0)
        #         cellslist[i].change_attribute("ZONE_ORC", 0)
        #         continue    # Skip the 'Fixed Land Use Cells' to save time on the looping
        #
        #     coordinates = cellslist[i].get_points()
        #     coordinates = [c[:2] for c in coordinates]
        #     cellpoly = Polygon(coordinates)
        #
        #     if not self.zoning_rules_resauto:       # RESIDENTIAL LAND
        #         if not self.determine_zoning_against_polygons(cellpoly, respolygons, 0):
        #             cellslist[i].change_attribute("ZONE_RES", 0)    # If an intersection was NOT detected, not zoned!
        #     if not self.zoning_rules_comauto:       # COMMERCIAL LAND
        #         if not self.determine_zoning_against_polygons(cellpoly, compolygons, 0):
        #             cellslist[i].change_attribute("ZONE_COM", 0)
        #     if not self.zoning_rules_indauto:       # INDUSTRIAL LAND
        #         if not self.determine_zoning_against_polygons(cellpoly, indpolygons, 0):
        #             cellslist[i].change_attribute("ZONE_IND", 0)
        #     if not self.zoning_rules_officesauto:  # MIXED DEVELOPMENT LAND
        #         if not self.determine_zoning_against_polygons(cellpoly, officespolygons, 0):
        #             cellslist[i].change_attribute("ZONE_ORC", 0)
        #
        # # - 2.8.4 - Auto-assignment options - if the auto-assign function is on, then perform this NOW
        # # Only touch the land uses where the auto checkbox was ticked.
        # respassive, compassive, indpassive, orcpassive = 1, 1, 1, 1     # By default = 1 - generally passive always 1
        # if self.zoning_rules_resauto:
        #     respassive = self.zoning_rules_resauto * int((not self.zoning_rules_reslimit or
        #                                                   (self.zoning_rules_reslimit * self.zoning_rules_respassive)))
        #
        # if self.zoning_rules_comauto:
        #     compassive = self.zoning_rules_comauto * int((not self.zoning_rules_comlimit or
        #                                                   (self.zoning_rules_comlimit * self.zoning_rules_compassive)))
        #
        # if self.zoning_rules_indauto:
        #     indpassive = self.zoning_rules_indauto * int((not self.zoning_rules_indlimit or
        #                                                   (self.zoning_rules_indlimit * self.zoning_rules_indpassive)))
        #
        # if self.zoning_rules_officesauto:
        #     orcpassive = self.zoning_rules_officesauto * int((not self.zoning_rules_officeslimit or
        #                                                       (self.zoning_rules_officeslimit *
        #                                                        self.zoning_rules_officespassive)))
        #
        # for i in range(len(cellslist)):
        #     if cellslist[i].get_attribute("LUC_Type") in ["Fixed", "UNDEFINED"]:    # DONE - skip!
        #         continue
        #     elif cellslist[i].get_attribute("LUC_Type") == "Passive":  # If passive, set based on parameter
        #         bool(self.zoning_rules_resauto) and cellslist[i].change_attribute("ZONE_RES", int(respassive))
        #         bool(self.zoning_rules_comauto) and cellslist[i].change_attribute("ZONE_COM", int(compassive))
        #         bool(self.zoning_rules_indauto) and cellslist[i].change_attribute("ZONE_IND", int(indpassive))
        #         bool(self.zoning_rules_officesauto) and cellslist[i].change_attribute("ZONE_ORC", int(orcpassive))
        #     elif cellslist[i].get_attribute("Base_LUC") == "Residential":
        #         bool(self.zoning_rules_resauto) and cellslist[i].change_attribute("ZONE_RES", 1)  # Always, regardless
        #         bool(self.zoning_rules_comauto) and \
        #             cellslist[i].change_attribute("ZONE_COM", int(not self.zoning_rules_comlimit))
        #         bool(self.zoning_rules_indauto) and \
        #             cellslist[i].change_attribute("ZONE_IND", int(not self.zoning_rules_indlimit))
        #         bool(self.zoning_rules_officesauto) and \
        #             cellslist[i].change_attribute("ZONE_ORC",int(not self.zoning_rules_officeslimit))
        #     elif cellslist[i].get_attribute("Base_LUC") == "Commercial":
        #         bool(self.zoning_rules_comauto) and cellslist[i].change_attribute("ZONE_COM", 1)  # Always, regardless
        #         bool(self.zoning_rules_resauto) and \
        #         cellslist[i].change_attribute("ZONE_RES", int(not self.zoning_rules_comlimit))
        #         bool(self.zoning_rules_indauto) and \
        #         cellslist[i].change_attribute("ZONE_IND", int(not self.zoning_rules_indlimit))
        #         bool(self.zoning_rules_officesauto) and \
        #         cellslist[i].change_attribute("ZONE_ORC", int(not self.zoning_rules_officeslimit))
        #     elif cellslist[i].get_attribute("Base_LUC") in ["Light Industry", "Heavy Industry"]:
        #         bool(self.zoning_rules_indauto) and cellslist[i].change_attribute("ZONE_IND", 1)
        #         bool(self.zoning_rules_resauto) and \
        #         cellslist[i].change_attribute("ZONE_RES", int(not self.zoning_rules_comlimit))
        #         bool(self.zoning_rules_comauto) and \
        #         cellslist[i].change_attribute("ZONE_COM", int(not self.zoning_rules_comlimit))
        #         bool(self.zoning_rules_officesauto) and \
        #         cellslist[i].change_attribute("ZONE_ORC", int(not self.zoning_rules_officeslimit))
        #     elif cellslist[i].get_attribute("Base_LUC") in ["Offices Res Mix"]:
        #         bool(self.zoning_rules_officesauto) and cellslist[i].change_attribute("ZONE_ORC", 1)
        #         bool(self.zoning_rules_resauto) and \
        #         cellslist[i].change_attribute("ZONE_RES", int(not self.zoning_rules_comlimit))
        #         bool(self.zoning_rules_comauto) and \
        #         cellslist[i].change_attribute("ZONE_COM", int(not self.zoning_rules_comlimit))
        #         bool(self.zoning_rules_indauto) and \
        #         cellslist[i].change_attribute("ZONE_IND", int(not self.zoning_rules_indlimit))
        #     else:
        #         print "DEBUG: Should not be here..."
        #
        # # - 2.8.5 - Overlay Maps - THIRD MASK
        # waterpoly = self.get_rings_maps_for_zoning(self.zoning_water)           # Water bodies
        # heritagepoly = self.get_rings_maps_for_zoning(self.zoning_heritage)     # Historical/Heritage areas
        # publicpoly = self.get_rings_maps_for_zoning(self.zoning_public)         # Public Acquisition
        # enviropoly = self.get_rings_maps_for_zoning(self.zoning_enviro)         # Environmental Significance
        # floodpoly = self.get_rings_maps_for_zoning(self.zoning_flood)           # Flood Inundation
        # custompoly = self.get_rings_maps_for_zoning(self.zoning_custom)         # Custom Overlay
        #
        # totfeatures = len(waterpoly) + len(heritagepoly) + len(publicpoly) + len(enviropoly) + len(floodpoly) + len(custompoly)
        # print "Total Features of overlays to check against...", totfeatures
        #
        # # Scan all remaining cells against overlay conditions
        # for i in range(len(cellslist)):
        #     zstates = self.get_zoning_states(cellslist[i])      # If all four zones are 0, then skip
        #     if sum(zstates) == 0:
        #         continue
        #
        #     coordinates = cellslist[i].get_points()
        #     coordinates = [c[:2] for c in coordinates]
        #     cellpoly = Polygon(coordinates)
        #
        #     # CHECK WATER BODIES - 100% threshold - i.e. cells must be fully covered
        #     if len(waterpoly) != 0:
        #         restrict = self.determine_zoning_against_polygons(cellpoly, waterpoly, 1.0)
        #         # One-liner If Statement: If the zoning state is already 0 i.e. False, then don't change the state
        #         bool(zstates[0]) and cellslist[i].change_attribute("ZONE_RES", restrict)
        #         bool(zstates[1]) and cellslist[i].change_attribute("ZONE_COM", restrict)
        #         bool(zstates[2]) and cellslist[i].change_attribute("ZONE_IND", restrict)
        #         bool(zstates[3]) and cellslist[i].change_attribute("ZONE_ORC", restrict)
        #
        #         zstates = self.get_zoning_states(cellslist[i])   # Update zstates
        #         if sum(zstates) == 0:
        #             continue
        #
        #     # CHECK HERITAGE - 50% threshold - i.e. half of the cell must be designated heritage
        #     if len(heritagepoly) != 0:
        #         restrict = self.determine_zoning_against_polygons(cellpoly, heritagepoly, 0.5)
        #         if zstates[0] and self.zoning_heritage_res:     # If zoning allowed AND heritage considered?
        #             cellslist[i].change_attribute("ZONE_RES", restrict)
        #         if zstates[1] and self.zoning_heritage_com:
        #             cellslist[i].change_attribute("ZONE_COM", restrict)
        #         if zstates[2] and self.zoning_heritage_ind:
        #             cellslist[i].change_attribute("ZONE_IND", restrict)
        #         if zstates[3] and self.zoning_heritage_orc:
        #             cellslist[i].change_attribute("ZONE_ORC", restrict)
        #
        #         zstates = self.get_zoning_states(cellslist[i])   # Update zstates
        #         if sum(zstates) == 0:
        #             continue
        #
        #     # CHECK PUBLIC ACQUISITION - 51% Threshold, absolute majority of the cell for land use dominance
        #     if len(publicpoly) != 0:
        #         restrict = self.determine_zoning_against_polygons(cellpoly, publicpoly, 0.51)
        #         if zstates[0] and self.zoning_public_res:
        #             cellslist[i].change_attribute("ZONE_RES", restrict)
        #         if zstates[1] and self.zoning_public_com:
        #             cellslist[i].change_attribute("ZONE_COM", restrict)
        #         if zstates[2] and self.zoning_public_ind:
        #             cellslist[i].change_attribute("ZONE_IND", restrict)
        #         if zstates[3] and self.zoning_public_orc:
        #             cellslist[i].change_attribute("ZONE_ORC", restrict)
        #
        #         zstates = self.get_zoning_states(cellslist[i])  # Update zstates
        #         if sum(zstates) == 0:
        #             continue
        #
        #     # CHECK ENVIRONMENTAL SIGNIFICANCE - 50% threshold, enough environmental significance to disallow zone
        #     if len(enviropoly) != 0:
        #         restrict = self.determine_zoning_against_polygons(cellpoly, enviropoly, 0.50)
        #         if zstates[0] and self.zoning_enviro_res:
        #             cellslist[i].change_attribute("ZONE_RES", restrict)
        #         if zstates[1] and self.zoning_enviro_com:
        #             cellslist[i].change_attribute("ZONE_COM", restrict)
        #         if zstates[2] and self.zoning_enviro_ind:
        #             cellslist[i].change_attribute("ZONE_IND", restrict)
        #         if zstates[3] and self.zoning_enviro_orc:
        #             cellslist[i].change_attribute("ZONE_ORC", restrict)
        #
        #         zstates = self.get_zoning_states(cellslist[i])  # Update zstates
        #         if sum(zstates) == 0:
        #             continue
        #
        #     # CHECK INUNDATION - using a 20% threshold. If land is subject to flooding, somewhat, then disallow zone!
        #     if len(floodpoly) != 0:
        #         restrict = self.determine_zoning_against_polygons(cellpoly, floodpoly, 0.20)
        #         if zstates[0] and self.zoning_flood_res:
        #             cellslist[i].change_attribute("ZONE_RES", restrict)
        #         if zstates[1] and self.zoning_flood_com:
        #             cellslist[i].change_attribute("ZONE_COM", restrict)
        #         if zstates[2] and self.zoning_flood_ind:
        #             cellslist[i].change_attribute("ZONE_IND", restrict)
        #         if zstates[3] and self.zoning_flood_orc:
        #             cellslist[i].change_attribute("ZONE_ORC", restrict)
        #
        #         zstates = self.get_zoning_states(cellslist[i])  # Update zstates
        #         if sum(zstates) == 0:
        #             continue
        #
        #     # CHECK CUSTOM - using a 50% threshold by default
        #     if len(custompoly) != 0:
        #         restrict = self.determine_zoning_against_polygons(cellpoly, custompoly, 0.50)
        #         if zstates[0] and self.zoning_custom_res:
        #             cellslist[i].change_attribute("ZONE_RES", restrict)
        #         if zstates[1] and self.zoning_custom_com:
        #             cellslist[i].change_attribute("ZONE_COM", restrict)
        #         if zstates[2] and self.zoning_custom_ind:
        #             cellslist[i].change_attribute("ZONE_IND", restrict)
        #         if zstates[3] and self.zoning_custom_orc:
        #             cellslist[i].change_attribute("ZONE_ORC", restrict)

        # - 2.8 - DETERMINE LARGE NEIGHBOURHOODS ---
        self.notify("Establishing Neighbourhoods")
        print ("Establishing Neighbourhoods")
        hashtable = [[], []]    # [Cell_Obj, NhD_Objs]
        nhd_rad = self.nhd_radius * 1000    # Convert to [m]
        sqdist = nhd_rad * nhd_rad
        maxnhd = 0

        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            hashtable[0].append(cur_cell)   # Add the current cell object to the hash_table
            neighbours = []
            neighbour_IDs = []
            coords = (cur_cell.get_attribute("CentreX"), cur_cell.get_attribute("CentreY"))
            for j in range(len(cellslist)):
                dx = (cellslist[j].get_attribute("CentreX") - coords[0])
                dy = (cellslist[j].get_attribute("CentreY") - coords[1])
                if (dx * dx + dy * dy) <= sqdist:
                    # The Cell is part of the neighbourhood
                    neighbours.append(cellslist[j])
                    neighbour_IDs.append(cellslist[j].get_attribute("CellID"))
            cur_cell.add_attribute("NHD_IDs", neighbour_IDs)
            cur_cell.add_attribute("NHD_Num", len(neighbour_IDs))
            hashtable[1].append(neighbours)
            if len(neighbours) > maxnhd:
                maxnhd = len(neighbours)

        # - 2.9 - SPATIAL RELATIONSHIPS - NEIGHBOURHOOD EFFECT
        # We have the land use types defined, now we need to define the maps for the individual four active land uses
        ifos = []       # Get the IF objects for the simulation
        for i in range(len(self.function_ids)):
            ifos.append(self.activesim.get_function_with_id(self.function_ids[i]))

        for i in range(len(hashtable[0])):          # LOOP 1 - ACROSS CELLS
            curcell = hashtable[0][i]               # Establish list of cells and list of neighbours
            if curcell.get_attribute("Status") == 0:
                continue
            nhdcells = hashtable[1][i]
            influence_Nij = [[], [], [], []]            # INFLU Attributes

            for j in range(len(ifos)):              # LOOP 2 - ACROSS INFLUENCE FUNCTIONS
                ifo = ifos[j]
                tluc = ubglobals.UM_LUCNAMES[ubglobals.UM_LUCABBRS.index(ifo.target_landuse)]  # Target LUC for function
                # Need to convert the land use to the full name, for comparison with neighbourhoood cells.

                for k in range(len(nhdcells)):      # LOOP 3 - ACROSS CELL NEIGHBOURHOOD
                    nc = nhdcells[k]
                    ncluc = nc.get_attribute("Base_LUC")        # Base LUC  # NOTE LUC - MUST CHANGE THIS LATER TO GENERIC
                    if ncluc in ['Light Industry', 'Heavy Industry'] and tluc == 'Industrial':
                        dist = self.calculate_distance_between_cells(curcell, nc) / 1000.0  # [km]
                        w = ifo.return_weight_by_distance(dist)  # Interpolate the weight based on distance
                        influence_Nij[2].append(w)
                        continue
                    if ncluc != tluc:       # If the land uses are not equal and they're not industrial either...
                        continue

                    # Function Applies to the Neighbouring Cell, so calculate contribution to Nij
                    dist = self.calculate_distance_between_cells(curcell, nc) / 1000.0    # [km]
                    w = ifo.return_weight_by_distance(dist)     # Interpolate the weight based on distance
                    if ifo.origin_landuse == "RES":     # Assign to correct land use based on origin of function
                        influence_Nij[0].append(w)
                    elif ifo.origin_landuse == "COM":
                        influence_Nij[1].append(w)
                    elif ifo.origin_landuse == "IND":
                        influence_Nij[2].append(w)
                    elif ifo.origin_landuse == "ORC":
                        influence_Nij[3].append(w)

            final_Nij = [0,0,0,0]
            if self.edge_effects_method == "NA":        # NO ACCOUNTING - JUST CREATE THE FOUR ATTRIBUTES
                final_Nij = [sum(influence_Nij[0]), sum(influence_Nij[1]), sum(influence_Nij[2]), sum(influence_Nij[3])]
            elif self.edge_effects_method == "AVG":     # AVERAGING - DIVIDE BY THE LENGTH OF VALID CELLS IF THE
                final_Nij = [0,0,0,0]                   # LIST IS NON-ZERO
                for i in range(len(final_Nij)):
                    if len(influence_Nij[i]) == 0:
                        final_Nij[i] = 0
                    else:
                        final_Nij[i] = sum(influence_Nij[i])/len(influence_Nij[i])
            elif self.edge_effects_method == "PP" or self.edge_effects_method == "PPAVG":      # PROPORTION METHODS
                if len(nhdcells) != maxnhd:     # The Block is near the edge, correct for this
                    final_Nij = [0,0,0,0]
                    scaling_factor = maxnhd / len(nhdcells)     # Calculate scaling factor
                    for i in range(len(final_Nij)):             # Modify the data
                        if self.edge_effects_method == "PP":
                            final_Nij[i] = sum(influence_Nij[i]) * scaling_factor
                        elif len(influence_Nij[i]) == 0:
                            final_Nij[i] = 0
                        else:
                            final_Nij[i] = sum(influence_Nij[i]) / len(influence_Nij[i]) * scaling_factor
                elif self.edge_effects_method == "PPAVG":       # If not an edge block, average anyway
                    final_Nij = [0, 0, 0, 0]
                    for i in range(len(final_Nij)):
                        if len(influence_Nij[i]) == 0:
                            final_Nij[i] = 0
                        else:
                            final_Nij[i] = sum(influence_Nij[i])/len(influence_Nij[i])
                else:       # IF not an edge cell and no averaging required, just create the straightforward Nij.
                    final_Nij = [sum(influence_Nij[0]), sum(influence_Nij[1]), sum(influence_Nij[2]),
                                 sum(influence_Nij[3])]

            curcell.add_attribute("INFLU_RES", final_Nij[0])      # Add the four attributes
            curcell.add_attribute("INFLU_COM", final_Nij[1])
            curcell.add_attribute("INFLU_IND", final_Nij[2])
            curcell.add_attribute("INFLU_ORC", final_Nij[3])

        # - 2.10 - TRANSITION POTENTIAL - CALCULATE TRANSITION POTENTIAL ACROSS MAP
        # [Coming Soon]

        self.notify("Current End of Module")
        print ("Current end of module")
        return True

    def calculate_distance_between_cells(self, cellA, cellB):
        """Calculates the Euclidean Distance between two cells, for the sake of neighbourhood effect. Returns
        distance in [m]."""
        dx2 = pow((cellA.get_attribute("CentreX") - cellB.get_attribute("CentreX")), 2)
        dy2 = pow((cellA.get_attribute("CentreY") - cellB.get_attribute("CentreY")), 2)
        return math.sqrt(dx2 + dy2)

    def infill_nodata_values(self, nodata_cells, att_name, infill_method, nodatavalue):
        """Attempts to infill cells with no-data values of a given attribute based on the attributes of its
        neighbours.

        :param nodata_cells: list of no-data cell objects, function performs infill on each object
        :param att_name: the attribute name of the no-data value
        :param infill_method: the infill_method, "Average" - uses the average of the neighbour values, "Median"
                                - uses the median, "Categorical" - uses the most common category, otherwise
                                randomly assigns, "Min/Max", uses minimum or maximum value among neighbours.
        :param nodatavalue: the data set's standard no-data value
        :return:
        """
        for i in range(len(nodata_cells)):
            cur_cell = nodata_cells[i]
            nhd_values = []
            for n in ubglobals.COMPASS:     # Get all neighbours
                nhd_id = cur_cell.get_attribute("NHD_"+n)
                if nhd_id == 0:     # No neighbour in that direction
                    continue
                else:   # If it has a neighbour
                    nhd_cell = self.scenario.get_asset_with_name("CellID"+str(int(nhd_id)))
                    if nhd_cell.get_attribute(att_name) == nodatavalue:     # Neighbour has nodata value
                        continue
                    else:
                        nhd_values.append(nhd_cell.get_attribute(att_name))

            if len(nhd_values) == 0:
                continue    # If there is no data around, just skip, we are looking for 'edge effects'
            elif infill_method == "Average":    # Otherwise figure out what to do
                cur_cell.change_attribute(att_name, float(sum(nhd_values) / len(nhd_values)))
            elif infill_method == "Median":
                cur_cell.change_attribute(att_name, np.median(nhd_values))
            elif infill_method == "Min":
                cur_cell.change_attribute(att_name, min(nhd_values))
            elif infill_method == "Max":
                cur_cell.change_attribute(att_name, max(nhd_values))
            elif infill_method == "Categorical":
                cur_cell.change_attribute(att_name, nhd_values[0])      # Need to figure out how to calculate mode
            else:
                pass    # Should never get here...
        return True

    def calculate_cell_slope_and_aspect(self, cellslist):
        """Evaluates the slope and aspect of each cell based on the available elevation data. The calculation writes
        attributes "Slope" and "Aspect" to the cell."""
        cs = self.cellsize
        for i in range(len(cellslist)):
            if cellslist[i].get_attribute("Status") == 0:
                continue
            c = cellslist[i]    # Current cell
            c_elev = c.get_attribute("Elevation")
            c_nhd = [c.get_attribute("NHD_N"), c.get_attribute("NHD_NE"), c.get_attribute("NHD_E"),
                     c.get_attribute("NHD_SE"), c.get_attribute("NHD_S"), c.get_attribute("NHD_SW"),
                     c.get_attribute("NHD_W"), c.get_attribute("NHD_NW")]
            c_nhdZ = [-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999]
            for j in range(len(c_nhd)):
                if c_nhd[j] == 0:
                    c_nhdZ[j] = c_elev
                else:
                    c_nhdZ[j] = self.scenario.get_asset_with_name("CellID"+str(c_nhd[j])).get_attribute("Elevation")
            slope_rad, slope_deg = ubmethods.calculate_slope(c_elev, c_nhdZ, cs, cs, -9999)
            c.add_attribute("Slope_PCT", round(slope_rad * 100, 2))
            c.add_attribute("Slope_DEG", round(slope_deg * 2))

            aspect_deg = ubmethods.calculate_aspect(c_elev, c_nhdZ, -9999)
            c.add_attribute("Aspect_DEG", round(aspect_deg, 0))
        return True

    def get_zoning_states(self, cell):
        """Gets a 4-element list of booleans denoting the zoning states of the four active land uses RES, COM, IND, ORC
        based on the current input cell.

        :param cell: the UBVector () Object of the active cell being checked.
        :return: [bool, bool, bool, bool] where 0 = zoning prohibited, 1 = zoning allowed.
        """
        return [cell.get_attribute("ZONE_RES"), cell.get_attribute("ZONE_COM"), cell.get_attribute("ZONE_IND"),
                cell.get_attribute("ZONE_ORC")]

    def determine_zoning_against_polygons(self, cellpoly, polygonlist, threshold):
        """Compares the current cell polygon to that of a polygon list for potential intersections with an area greater
        than the threshold value until a zoning constraint has been found. Returns 0 if the zoning is to be disallowed,
        1 if no match has been found.

        :param cellpoly: the cell polygon (Shapely Polygon)
        :param polygonlist: the list of polygonal rings to compare the cell polygon against
        :param threshold: the proportion of cell area that needs to be covered for the zoning to apply
        :return: 0 if an intersection area > threshold has been found, 1 if no big enough intersection has been found.
        """
        if threshold == 0:
            for p in polygonlist:
                if Polygon(p).intersects(cellpoly):
                    return 1
            return 0
        else:
            # calculate threshold area, if intersection area > x% of block area, then threshold exceeded, stop search.
            threshold_area = (self.cellsize * self.cellsize) * threshold
            for p in polygonlist:
                if Polygon(p).intersection(cellpoly).area > threshold_area:
                    return 0    # Intersection found, stop algorithm
            return 1    # No intersection found, cell is OK to be treated as potential zone for active LUC

    def get_rings_maps_for_zoning(self, map_input):
        """Gets and returns a list of ring polygons from

        :param map_input: the input dataref ID to search for
        :return: the list of ring coordinates (used to make polygons)
        """
        dref = self.datalibrary.get_data_with_id(map_input)
        if dref is None:
            return []
        else:
            fullfilepath = dref.get_data_file_path() + dref.get_metadata("filename")
            polylist = ubspatial.import_polygonal_map(fullfilepath, "RINGS", None, self.global_offsets)
        return polylist

    def calculate_accessibility_pointfeatures(self, map_input, map_attr, aj, cellslist, att_name):
        """Calculates the accessibility from a Point Features Map and adds the individual accessibility values
        to the map.

        :param map_input: the input map to calculate the accessibility from
        :param map_attr: the global map attributes list
        :param aj: the list of parameters for accessibility calculations - the importance factors
        :param cellslist: the list of cells in the simulation
        :param att_name: the prefix attribute name to use (e.g. ROADS --> "ACC_ROAD_"
        :return: Nothing, updates the cells with accessibility attributes
        """
        self.notify("Determining Accessibility to: " + att_name)

        # GET THE MAP'S FILEPATH
        dref = self.datalibrary.get_data_with_id(map_input)  # Retrieve the land use map
        fullfilepath = dref.get_data_file_path() + dref.get_metadata("filename")

        # LOAD THE POINT FEATURES
        pointfeatures = ubspatial.import_point_features(fullfilepath, "POINTCOORDS", self.global_offsets)

        self.notify("Number of loaded features to compare for "+str(att_name)+": " + str(len(pointfeatures)))
        print "Length of the featurepoints list for "+str(att_name)+": ", str(len(pointfeatures))

        # CALCULATE CLOSEST DISTANCE TO EACH CELL
        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            loc = (cellslist[i].get_attribute("CentreX"), cellslist[i].get_attribute("CentreY"))
            dist = 99999999.0
            for j in range(len(pointfeatures)):  # Loop through all feature points
                feat_point = pointfeatures[j]  # Make a Shapely point
                dx = loc[0] - feat_point[0]
                dy = loc[1] - feat_point[1]
                newdist = math.sqrt(dx * dx + dy * dy)
                if newdist < dist:
                    dist = newdist
            dist = dist / 1000.0        # Convert to [km]
            cur_cell.add_attribute("ACC_" + att_name + "_DIST", dist)  # Distance in [km]
            cur_cell.add_attribute("ACC_" + att_name + "_RES", ubmethods.calculate_accessibility_factor(dist, aj[0]))
            cur_cell.add_attribute("ACC_" + att_name + "_COM", ubmethods.calculate_accessibility_factor(dist, aj[1]))
            cur_cell.add_attribute("ACC_" + att_name + "_IND", ubmethods.calculate_accessibility_factor(dist, aj[2]))
            cur_cell.add_attribute("ACC_" + att_name + "_ORC", ubmethods.calculate_accessibility_factor(dist, aj[3]))

        map_attr.add_attribute("ACCESS_" + att_name, 1)
        return True

    def calculate_accessibility_linearfeatures(self, map_input, map_attr, aj, cellslist, att_name):
        """Calculates the accessibility from a Point Features Map and adds the individual accessibility values
        to the map.

        :param map_input: the input map to calculate the accessibility from
        :param map_attr: the global map attributes list
        :param aj: the list of parameters for accessibility calculations - the importance factors
        :param cellslist: the list of cells in the simulation
        :param att_name: the prefix attribute name to use (e.g. ROADS --> "ROAD"
        :return: Nothing, updates the cells with accessibility attributes
        """
        self.notify("Determining Accessibility to: "+att_name)

        # GET THE FULL FILENAME OF THE MAP INPUT
        dref = self.datalibrary.get_data_with_id(map_input)  # Retrieve the land use map
        fullfilepath = dref.get_data_file_path() + dref.get_metadata("filename")

        # LOAD LINEAR FEATURES AND SEGMENTIZE
        linearfeatures = ubspatial.import_linear_network(fullfilepath, "POINTS", self.global_offsets,
                                                         Segments=self.cellsize)  # Segmentation

        self.notify("Number of loaded features to compare for "+str(att_name)+": "+str(len(linearfeatures)))
        print "Length of the featurepoints list for "+str(att_name)+": ", str(len(linearfeatures))

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
            dist = dist / 1000.0  # Convert to [km]
            cur_cell.add_attribute("ACC_"+att_name+"_DIST", dist)   # Distance in [km]
            cur_cell.add_attribute("ACC_"+att_name+"_RES", ubmethods.calculate_accessibility_factor(dist, aj[0]))
            cur_cell.add_attribute("ACC_"+att_name+"_COM", ubmethods.calculate_accessibility_factor(dist, aj[1]))
            cur_cell.add_attribute("ACC_"+att_name+"_IND", ubmethods.calculate_accessibility_factor(dist, aj[2]))
            cur_cell.add_attribute("ACC_"+att_name+"_ORC", ubmethods.calculate_accessibility_factor(dist, aj[3]))

        map_attr.add_attribute("ACCESS_"+att_name, 1)
        return True

    def calculate_accessibility_polygonfeatures(self, map_input, map_attr, aj, cellslist, att_name, **kwargs):
        """Calculates the accessibility from a Point Features Map and adds the individual accessibility values
        to the map.

        :param map_input: the input map to calculate the accessibility from
        :param map_attr: the global map attributes list
        :param aj: the list of parameters for accessibility calculations - the importance factors
        :param cellslist: the list of cells in the simulation
        :param att_name: the prefix attribute name to use (e.g. ROADS --> "ACC_ROAD_"
        :param **kwargs: Exception-handling. Need to specify land use categories to exclude to prevent doubling up
                        e.g. Landuses=["Parks and Gardens", "Reserves and Floodways", "Forest"]
        :return: Nothing, updates the cells with accessibility attributes
        """
        self.notify("Determining Accessibility to: " + att_name)

        # GET THE FULL FILENAME OF THE MAP INPUT
        dref = self.datalibrary.get_data_with_id(map_input)  # Retrieve the land use map
        fullfilepath = dref.get_data_file_path() + dref.get_metadata("filename")

        # LOAD POLYGONAL FEATURES AS RING POINTS COORDINATES
        polypoints = ubspatial.import_polygonal_map(fullfilepath, "RINGPOINTS", None, self.global_offsets)

        self.notify("Number of loaded features to compare for "+str(att_name)+": " + str(len(polypoints)))
        print "Length of the featurepoints list for "+str(att_name)+": ", str(len(polypoints))

        for i in range(len(cellslist)):
            cur_cell = cellslist[i]
            if cur_cell.get_attribute("Base_LUC") in kwargs["Landuses"]:
                # The cell itself is the land use, so distance is zero
                dist = 0
            else:
                loc = (cellslist[i].get_attribute("CentreX"), cellslist[i].get_attribute("CentreY"))
                dist = 99999999.0
                for j in range(len(polypoints)):  # Loop through all feature points
                    feat_point = polypoints[j]
                    dx = loc[0] - feat_point[0]
                    dy = loc[1] - feat_point[1]
                    newdist = math.sqrt(dx * dx + dy * dy)
                    if newdist < dist:
                        dist = newdist
            dist = dist / 1000.0  # Convert to [km]
            cur_cell.add_attribute("ACC_" + att_name + "_DIST", dist)  # Distance in [km]
            cur_cell.add_attribute("ACC_" + att_name + "_RES", ubmethods.calculate_accessibility_factor(dist, aj[0]))
            cur_cell.add_attribute("ACC_" + att_name + "_COM", ubmethods.calculate_accessibility_factor(dist, aj[1]))
            cur_cell.add_attribute("ACC_" + att_name + "_IND", ubmethods.calculate_accessibility_factor(dist, aj[2]))
            cur_cell.add_attribute("ACC_" + att_name + "_ORC", ubmethods.calculate_accessibility_factor(dist, aj[3]))

        map_attr.add_attribute("ACCESS_" + att_name, 1)
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
