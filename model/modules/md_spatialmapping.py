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
from model.progref.ubglobals import as ubglobals


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

        # --- ACTIVATE/DEACTIVATION PARAMETERS -------------------------------------------------------------------------
        # These are the key booleans at the start of each tab that enable/disable the GUI elements depending on whether
        # they are to be featured in the simulation.
        # --------------------------------------------------------------------------------------------------------------
        self.create_parameter("planrules", BOOL, "Introduce special planning rules into model?")
        self.planrules = 0

        self.create_parameter("landcover", BOOL, "Map land cover across urban form?")
        self.landcover = 0

        self.create_parameter("openspaces", BOOL, "Conduct analysis of open space characteristics/distribution.")
        self.openspaces = 0

        self.create_parameter("wateruse", BOOL, "Calculate spatio-temporal water consumption and wastewater?")
        self.wateruse = 0

        self.create_parameter("emissions", BOOL, "Map pollution emissions across map?")
        self.emissions = 0

        # DEVELOPER NOTE: Add future sub-module BOOLEANS here

        # --- PLANNING OVERLAY PARAMETERS ------------------------------------------------------------------------------
        # Includes a range of options for setting up planning restrictions in the case study. This includes limiting the
        # construction of infrastructure in certain land uses or the introduction of planning overlays that will have
        # some form of impact on how much can be constructed in various regions.
        # --------------------------------------------------------------------------------------------------------------

        # OVERLAYS
        
        # --- LAND COVER MAPPING PARAMETERS ----------------------------------------------------------------------------
        # Assigns land cover types to a range of urban characteristics determined in the previous urban planning module
        # for the purpose of mapping land cover, urban microclimate and other aspects.
        # --------------------------------------------------------------------------------------------------------------
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
        self.materialtypes = ubglobals.LANDCOVERMATERIALS
        self.treetypes = ubglobals.TREETYPES

        # --- OPEN SPACE MAPPING AND STRATEGIES ------------------------------------------------------------------------
        # Parameters to conduct the analysis of open space 'networks' within the case study. This spatial mapping
        # feature looks at the links and distribution of open spaces and exports maps accordingly as well as statistics
        # on open space accessibility, similar to what is done in the urban development, but at a different level.
        # --------------------------------------------------------------------------------------------------------------
        # OPEN SPACE ACCESSIBILITY AND NETWORKS
        self.create_parameter("osnet_accessibility", BOOL, "Calculate accessibility?")
        self.create_parameter("osnet_network", BOOL, "Delineate open space network?")
        self.osnet_accessibility = 0
        self.osnet_network = 0

        # Parameters for Undertaking Open Space Analysis

        # ENCUMBRANCES
        self.create_parameter("parks_restrict", BOOL, "Restrict park space usage for decentral. water infrastructure?")
        self.create_parameter("reserves_restrict", BOOL, "Restrict reserve and floodway space to stormwater?")
        self.parks_restrict = 0
        self.reserves_restrict = 0

        # --- SPATIO-TEMPORAL WATER USE AND WASTEWATER VOLUMES ---------------------------------------------------------
        # Calculates the water demands, irrigation volumes and wastewater generated. Also includes downscaling of water
        # consumption to daily diurnal patterns and scaling across a year for seasonal trends.
        # --------------------------------------------------------------------------------------------------------------
        # -- RESIDENTIAL WATER USE --
        self.create_parameter("residential_method", STRING, "Method for determinining residential water use.")
        self.residential_method = "EUA"     # EUA = end use analysis, DQI = direct flow input

        # END USE ANALYSIS
        self.create_parameter("res_standard", STRING, "The water appliances standard to use in calculations.")
        self.res_standard = "AS6400"

        self.create_parameter("res_kitchen_fq", DOUBLE, "Frequency of kitchen water use.")
        self.create_parameter("res_kitchen_dur", DOUBLE, "Duration of kitchen water use.")
        self.create_parameter("res_kitchen_hot", DOUBLE, "Proportion of kitchen water from hot water")
        self.create_parameter("res_kitchen_var", DOUBLE, "Stochastic variation in kitchen water use")
        self.create_parameter("res_kitchen_ffp", STRING, "Minimum Fit for purpose water source for kitchen use.")
        self.res_kitchen_fq = 5.0
        self.res_kitchen_dur = 2.0
        self.res_kitchen_hot = 30
        self.res_kitchen_var = 0
        self.res_kitchen_ffp = "PO"     # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_shower_fq", DOUBLE, "Frequency of shower water use.")
        self.create_parameter("res_shower_dur", DOUBLE, "Duration of shower water use.")
        self.create_parameter("res_shower_hot", DOUBLE, "Proportion of shower water from hot water")
        self.create_parameter("res_shower_var", DOUBLE, "Stochastic variation in shower water use")
        self.create_parameter("res_shower_ffp", STRING, "Minimum Fit for purpose water source for shower use.")
        self.res_shower_fq = 5.0
        self.res_shower_dur = 2.0
        self.res_shower_hot = 30
        self.res_shower_var = 0
        self.res_shower_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_toilet_fq", DOUBLE, "Frequency of toilet water use.")
        self.create_parameter("res_toilet_hot", DOUBLE, "Proportion of toilet water from hot water")
        self.create_parameter("res_toilet_var", DOUBLE, "Stochastic variation in toilet water use")
        self.create_parameter("res_toilet_ffp", STRING, "Minimum Fit for purpose water source for toilet use.")
        self.res_toilet_fq = 5.0
        self.res_toilet_hot = 30
        self.res_toilet_var = 0
        self.res_toilet_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_laundry_fq", DOUBLE, "Frequency of laundry water use.")
        self.create_parameter("res_laundry_hot", DOUBLE, "Proportion of laundry water from hot water")
        self.create_parameter("res_laundry_var", DOUBLE, "Stochastic variation in laundry water use")
        self.create_parameter("res_laundry_ffp", STRING, "Minimum Fit for purpose water source for laundry use.")
        self.res_laundry_fq = 5.0
        self.res_laundry_hot = 30
        self.res_laundry_var = 0
        self.res_laundry_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_dishwasher_fq", DOUBLE, "Frequency of dishwasher water use.")
        self.create_parameter("res_dishwasher_hot", DOUBLE, "Proportion of dishwasher water from hot water")
        self.create_parameter("res_dishwasher_var", DOUBLE, "Stochastic variation in dishwasher water use")
        self.create_parameter("res_dishwasher_ffp", STRING, "Minimum Fit for purpose water source for dishwasher use.")
        self.res_dishwasher_fq = 5.0
        self.res_dishwasher_hot = 30
        self.res_dishwasher_var = 0
        self.res_dishwasher_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_outdoor_vol", DOUBLE, "Outdoor irrigation volume")
        self.create_parameter("res_outdoor_ffp", STRING, "Outdoor min fit-for-purpose water source")
        self.res_outdoor_vol = 1.0
        self.res_outdoor_ffp = "RW"

        # Diurnal patterns
        self.create_parameter("res_kitchen_pat", STRING, "Diurnal pattern for kitchen water use")
        self.create_parameter("res_kitchen_cp", LISTDOUBLE, "The diurnal pattern for kitchen water use if custom")
        self.res_kitchen_pat = "SDD"
        self.res_kitchen_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                               1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("res_shower_pat", STRING, "Diurnal pattern for shower water use")
        self.create_parameter("res_shower_cp", LISTDOUBLE, "The diurnal pattern for shower water use if custom")
        self.res_shower_pat = "SDD"
        self.res_shower_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                              1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("res_toilet_pat", STRING, "Diurnal pattern for toilet water use")
        self.create_parameter("res_toilet_cp", LISTDOUBLE, "The diurnal pattern for toilet water use if custom")
        self.res_toilet_pat = "SDD"
        self.res_toilet_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                              1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("res_laundry_pat", STRING, "Diurnal pattern for laundry water use")
        self.create_parameter("res_laundry_cp", LISTDOUBLE, "The diurnal pattern for laundry water use if custom")
        self.res_laundry_pat = "SDD"
        self.res_laundry_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                               1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("res_dishwasher_pat", STRING, "Diurnal pattern for dishwasher water use")
        self.create_parameter("res_dishwasher_cp", LISTDOUBLE, "The diurnal pattern for dishwasher water use if custom")
        self.res_dishwasher_pat = "SDD"
        self.res_dishwasher_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                  1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("res_outdoor_pat", STRING, "Diurnal pattern for outdoor water use")
        self.create_parameter("res_outdoor_cp", LISTDOUBLE, "The diurnal pattern for outdoor water use if custom")
        self.res_outdoor_pat = "SDD"
        self.res_outdoor_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                               1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        # Wastewater Generation
        self.create_parameter("res_kitchen_wwq", STRING, "Wastewater quality level for kitchen use")
        self.create_parameter("res_shower_wwq", STRING, "Wastewater quality level for shower use")
        self.create_parameter("res_toilet_wwq", STRING, "Wastewater quality for toilet use")
        self.create_parameter("res_laundry_wwq", STRING, "Wastewater quality for laundry use")
        self.create_parameter("res_dishwasher_wwq", STRING, "Wastewater quality for dishwasher use")
        self.res_kitchen_wwq = "B"  # G = grey, B = black
        self.res_shower_wwq = "G"
        self.res_toilet_wwq = "B"
        self.res_laundry_wwq = "G"
        self.res_dishwasher_wwq = "B"

        # RESIDENTIAl DIRECT FLOW INPUT
        self.create_parameter("res_dailyindoor_vol", DOUBLE, "Approx. daily indoor per capita water use")
        self.create_parameter("res_dailyindoor_np", DOUBLE, "Proportion of daily indoor use from non-potable source")
        self.create_parameter("res_dailyindoor_hot", DOUBLE, "Proportion of daily indoor use requiring hot water")
        self.create_parameter("res_dailyindoor_var", DOUBLE, "Variation to daily indoor use")
        self.res_dailyindoor_vol = 155
        self.res_dailyindoor_np = 60
        self.res_dailyindoor_hot = 30
        self.res_dailyindoor_var = 0.0
        # Outdoor water use - use the same parameters as before

        self.create_parameter("res_dailyindoor_pat", STRING, "Diurnal pattern to use for daily indoor res use")
        self.create_parameter("res_dailyindoor_cp", LISTDOUBLE, "The default custom pattern if used for daily indoor")
        self.res_dailyindoor_pat = "SDD"
        self.res_dailyindoor_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                   1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        # Outdoor patterns, use the same parameters as before

        self.create_parameter("res_dailyindoor_bgprop", DOUBLE, "Blackwater-greywater proportion of daily indoor use.")
        self.res_dailyindoor_bgprop = 0.0   # default = 0 which is 50-50

        # -- NON-RESIDENTIAL WATER USE --
        self.create_parameter("nonres_method", STRING, "Method for estimating non-residential water consumption")
        self.nonres_method = "UQR"      # UQR = unit flow rate, PES = Population equivalents

        # UNIT FLOW RATES
        self.create_parameter("com_demand", DOUBLE, "Commercial water demand value")
        self.create_parameter("com_var", DOUBLE, "Variation in commercial water demand")
        self.create_parameter("com_units", STRING, "Units for commercial water demands")
        self.create_parameter("com_hot", DOUBLE, "Proportion of hot water for commercial water demand")
        self.com_demand = 20.0
        self.com_var = 0.0
        self.com_units = "LSQMD"    # LSQMD = L/sqm/day and LPAXD = L/persons/day
        self.com_hot = 20.0

        self.create_parameter("office_demand", DOUBLE, "Office water demand value")
        self.create_parameter("office_var", DOUBLE, "Variation in office water demand")
        self.create_parameter("office_units", STRING, "Units for office water demands")
        self.create_parameter("office_hot", DOUBLE, "Proportion of hot water for office water demand")
        self.office_demand = 20.0
        self.office_var = 0.0
        self.office_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day
        self.office_hot = 20.0

        self.create_parameter("li_demand", DOUBLE, "Light Industry water demand value")
        self.create_parameter("li_var", DOUBLE, "Variation in Light Industry water demand")
        self.create_parameter("li_units", STRING, "Units for Light Industry water demands")
        self.create_parameter("li_hot", DOUBLE, "Proportion of hot water for Light Industry water demand")
        self.li_demand = 20.0
        self.li_var = 0.0
        self.li_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day
        self.li_hot = 20.0

        self.create_parameter("hi_demand", DOUBLE, "Heavy Industry water demand value")
        self.create_parameter("hi_var", DOUBLE, "Variation in Heavy Industry water demand")
        self.create_parameter("hi_units", STRING, "Units for Heavy Industry water demands")
        self.create_parameter("hi_hot", DOUBLE, "Proportion of hot water for Heavy Industry water demand")
        self.hi_demand = 20.0
        self.hi_var = 0.0
        self.hi_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day
        self.hi_hot = 20.0

        self.create_parameter("nonres_landscape_vol", DOUBLE, "Landscape irrigation volume")
        self.create_parameter("nonres_landscape_ffp", STRING, "Minimum fit-for-purpose irrigation volume")
        self.nonres_landscape_vol = 1.0
        self.nonres_landscape_ffp = "PO"

        self.create_parameter("com_pat", STRING, "Daily diurnal pattern for commercial water demands.")
        self.create_parameter("com_cp", LISTDOUBLE, "Custom patternf or commercial water demands.")
        self.com_pat = "SDD"
        self.com_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                       1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("ind_pat", STRING, "Daily diurnal pattern for limercial water demands.")
        self.create_parameter("ind_cp", LISTDOUBLE, "Custom patternf or limercial water demands.")
        self.ind_pat = "SDD"
        self.ind_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                       1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("nonres_landscape_pat", STRING, "Daily diurnal pattern for himercial water demands.")
        self.create_parameter("nonres_landscape_cp", LISTDOUBLE, "Custom patternf or himercial water demands.")
        self.nonres_landscape_pat = "SDD"
        self.nonres_landscape_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.create_parameter("com_ww_bgprop", DOUBLE, "Proportion of black and greywater from commercial areas.")
        self.create_parameter("ind_ww_bgprop", DOUBLE, "Proportion of black and greywater from industrial areas.")
        self.com_ww_bgprop = 0.0
        self.ind_ww_bgprop = 0.0

        # POPULATION EQUIVALENTS METHOD (ADDITINOAL PARAMETERS)
        self.create_parameter("com_pefactor", DOUBLE, "Population equivalent for commercial water use")
        self.create_parameter("office_pefactor", DOUBLE, "Population equivalent for office water use")
        self.create_parameter("li_pefactor", DOUBLE, "Population equivalent factor for light industry water use.")
        self.create_parameter("hi_pefactor", DOUBLE, "Population equivalent factor for heavy industry water use.")
        self.com_pefactor = 1.0
        self.office_pefactor = 1.0
        self.li_pefactor = 1.0
        self.hi_pefactor = 1.0

        # -- PUBLIC OPEN SPACES AND DISTRICTS --
        self.create_parameter("pos_irrigation_vol", DOUBLE, "POS Irrigation Volume")
        self.create_parameter("pos_irrigation_ffp", STRING, "POS Fit-for-purpose minimum quality")
        self.pos_irrigation_vol = 1.0
        self.pos_irrigation_ffp = "NP"

        self.create_parameter("irrigate_parks", BOOL, "Irrigate parks and gardens?")
        self.create_parameter("irrigate_landmarks", BOOL, "Irrigate green parts of landmarks?")
        self.create_parameter("irrigate_reserves", BOOL, "Irrigate reserves and floodways?")
        self.irrigate_parks = 1
        self.irrigate_landmarks = 1
        self.irrigate_reserves = 0

        self.create_parameter("pos_irrigation_pat", STRING, "Diurnal pattern for POS irrigation")
        self.create_parameter("pos_irrigation_cp", LISTDOUBLE, "Custom pattern for POS irrigation diurnal")
        self.pos_irrigation_pat = "SDD"
        self.pos_irrigation_cp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                  1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        # -- REGIONAL WATER LOSSES --
        self.create_parameter("estimate_waterloss", BOOL, "Estimate water losses?")
        self.create_parameter("waterloss_method", STRING, "Method for estimating water loss")
        self.create_parameter("waterloss_volprop", DOUBLE, "Loss as volume of total demand proportion")
        self.create_parameter("waterloss_constant", DOUBLE, "Loss as constant global amount")
        self.create_parameter("waterloss_constant_units", STRING, "Units for constant global loss amount")
        self.estimate_waterloss = 1
        self.waterloss_method = "VOLPROP"   # VOLPROP = proportionate volume, CONSTANT = constant global loss
        self.waterloss_volprop = 10.0
        self.waterloss_constant = 1.0
        self.waterloss_constant_units = "MLY"   # MLY = ML/year, MLHAY = ML/ha/year

        # -- TEMPORAL AND SEASONAL DYNAMICS --
        # WEEKLY DYNAMICS
        self.create_parameter("weekend_nonres_reduce", BOOL, "Reduce non-res water demand during weekends?")
        self.create_parameter("weekend_nonres_factor", DOUBLE, "Reduction factor for non-res weekend volumes.")
        self.weekend_nonres_reduce = 1
        self.weekend_nonres_factor = 0.2

        self.create_parameter("weekend_res_increase", BOOL, "Increase residential water use on weekends?")
        self.create_parameter("weekend_res_factor", DOUBLE, "Scaling factor for residential water use on weekends")
        self.weekend_res_increase = 1
        self.weekend_res_factor = 1.4

        # SEASONAL DYNAMICS
        self.create_parameter("seasonal_analysis", BOOL, "Perform seasonal analysis?")
        self.create_parameter("scaling_dataset", STRING, "Data set to perform scaling against")
        self.create_parameter("scaling_years", DOUBLE, "Number of years to use for scaling")
        self.create_parameter("scaling_average", DOUBLE, "Global average for scaling")
        self.create_parameter("scaling_average_fromdata", BOOL, "Calculate global average from data?")
        self.create_parameter("no_irrigate_during_rain", BOOL, "Do not irrigate during rain event?")
        self.create_parameter("irrigation_resume_time", DOUBLE, "Resume irrigation after how many hours?")
        self.seasonal_analysis = 0
        self.scaling_dataset = ""
        self.scaling_years = 1
        self.scaling_average = 1.0
        self.scaling_average_fromdata = 1
        self.no_irrigate_during_rain = 1
        self.irrigation_resume_time = 24

        # ADVANCED - DIURNAL PATTERNS
        self.sdd = ubglobals.SDD
        self.cdp = ubglobals.CDP
        self.oht = ubglobals.OHT
        self.ahc = ubglobals.AHC

        # --- STORMWATER POLLUTION EMISSIONS ---------------------------------------------------------------------------
        # Pollutions emissions mapping, stormwater system, this module analyses the land use diversity and determines
        # build-up wash-off pollutant concentrations that can then be mapped spatially or modelled temporally.
        # --------------------------------------------------------------------------------------------------------------
        pass

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

        # OPEN SPACE ANALYSIS
        if self.openspaces:
            self.open_space_analysis()

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
        return True

    def map_open_spaces(self):
        """Maps the open space connectivity and accessibility as well as some key planning aspects surrounding POS."""
        pass

    def map_water_consumption(self, block_attr):
        pass

    def map_pollution_emissions(self):
        pass