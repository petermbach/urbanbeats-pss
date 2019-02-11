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
import random
import math

# --- URBANBEATS LIBRARY IMPORTS ---
from ubmodule import *
import model.progref.ubglobals as ubglobals
import model.ublibs.ubdatatypes as ubdata


# --- MODULE CLASS DEFINITION ---
class SpatialMapping(UBModule):
    """ SPATIAL MAPPING MODULE
    Undertakes the task of mapping a range of aspects of the urban environment including land cover, water demands,
    open space connectivity/accessibility, pollution emissions and planning overlays. The module is preparatory for
    many subsequent regulation/strategy and implementation modules.
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
        self.surfResIrrigate = "G"      #G = Garden, A = ALL
        self.trees_Res = 0.1

        self.create_parameter("surfParking", STRING, "Surface cover of parking lots.")
        self.create_parameter("surfBay", STRING, "Surface cover of loading bay.")
        self.create_parameter("surfHard", STRING, "Surface cover of hard landscaping")
        self.create_parameter("trees_NRes", DOUBLE, "Non-residential tree cover 0 to 1")
        self.create_parameter("trees_Site", BOOL, "Are trees located on-site?")
        self.create_parameter("trees_Front", BOOL, "Are trees located along the frontage?")
        self.surfParking = "AS"
        self.surfBay = "AS"
        self.surfHard = "CO"
        self.trees_NRes = 0.0
        self.trees_Site = 0
        self.trees_Front = 0

        self.create_parameter("surfArt", STRING, "Surface cover of arterial road/street")
        self.create_parameter("surfHwy", STRING, "Surface cover of a highway")
        self.create_parameter("surfFpath", STRING, "Surface cover of footpath")
        self.create_parameter("trees_roaddens", DOUBLE, "Tensity of trees per 100m road length")
        self.surfArt = "AS"
        self.surfHwy = "AS"
        self.surfFpath = "CO"
        self.trees_roaddens = 1.0

        self.create_parameter("surfFpath", STRING, "Surface cover of paved areas in parks")
        self.create_parameter("trees_opendens", DOUBLE, "Density of tree cover in parks")
        self.create_parameter("trees_refdens", DOUBLE, "Density of tree cover in reserves")
        self.create_parameter("tree_type", STRING, "Default and predominant type of tree in the case study region.")
        self.surfSquare = "CO"
        self.trees_opendens = 10.0
        self.trees_refdens = 10.0
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

        self.flowrates = []     # Initialize these variables, used in the EUA method
        self.baserating = 0

        # END USE ANALYSIS
        self.create_parameter("res_standard", STRING, "The water appliances standard to use in calculations.")
        self.res_standard = "AS6400"
        self.create_parameter("res_baseefficiency", STRING, "The base level efficiency to use at simulation begin.")
        self.res_base_efficiency = "none"       # Dependent on standard.

        self.create_parameter("res_kitchen_fq", DOUBLE, "Frequency of kitchen water use.")
        self.create_parameter("res_kitchen_dur", DOUBLE, "Duration of kitchen water use.")
        self.create_parameter("res_kitchen_hot", DOUBLE, "Proportion of kitchen water from hot water")
        self.create_parameter("res_kitchen_var", DOUBLE, "Stochastic variation in kitchen water use")
        self.create_parameter("res_kitchen_ffp", STRING, "Minimum Fit for purpose water source for kitchen use.")
        self.res_kitchen_fq = 5.0
        self.res_kitchen_dur = 2.0
        self.res_kitchen_hot = 30.0
        self.res_kitchen_var = 0.0
        self.res_kitchen_ffp = "PO"     # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_shower_fq", DOUBLE, "Frequency of shower water use.")
        self.create_parameter("res_shower_dur", DOUBLE, "Duration of shower water use.")
        self.create_parameter("res_shower_hot", DOUBLE, "Proportion of shower water from hot water")
        self.create_parameter("res_shower_var", DOUBLE, "Stochastic variation in shower water use")
        self.create_parameter("res_shower_ffp", STRING, "Minimum Fit for purpose water source for shower use.")
        self.res_shower_fq = 5.0
        self.res_shower_dur = 2.0
        self.res_shower_hot = 30.0
        self.res_shower_var = 0.0
        self.res_shower_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_toilet_fq", DOUBLE, "Frequency of toilet water use.")
        self.create_parameter("res_toilet_hot", DOUBLE, "Proportion of toilet water from hot water")
        self.create_parameter("res_toilet_var", DOUBLE, "Stochastic variation in toilet water use")
        self.create_parameter("res_toilet_ffp", STRING, "Minimum Fit for purpose water source for toilet use.")
        self.res_toilet_fq = 5.0
        self.res_toilet_hot = 30.0
        self.res_toilet_var = 0.0
        self.res_toilet_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_laundry_fq", DOUBLE, "Frequency of laundry water use.")
        self.create_parameter("res_laundry_hot", DOUBLE, "Proportion of laundry water from hot water")
        self.create_parameter("res_laundry_var", DOUBLE, "Stochastic variation in laundry water use")
        self.create_parameter("res_laundry_ffp", STRING, "Minimum Fit for purpose water source for laundry use.")
        self.res_laundry_fq = 5.0
        self.res_laundry_hot = 30.0
        self.res_laundry_var = 0.0
        self.res_laundry_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_dishwasher_fq", DOUBLE, "Frequency of dishwasher water use.")
        self.create_parameter("res_dishwasher_hot", DOUBLE, "Proportion of dishwasher water from hot water")
        self.create_parameter("res_dishwasher_var", DOUBLE, "Stochastic variation in dishwasher water use")
        self.create_parameter("res_dishwasher_ffp", STRING, "Minimum Fit for purpose water source for dishwasher use.")
        self.res_dishwasher_fq = 5.0
        self.res_dishwasher_hot = 30.0
        self.res_dishwasher_var = 0.0
        self.res_dishwasher_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.kitchendem = 0     # Placeholders for the base unit demand (for kitchen/shower/toilet, it's per capita)
        self.showerdem = 0      # for laundry and dishwasher it's per household.
        self.toiletdem = 0
        self.laundrydem = 0
        self.dishwasherdem = 0
        self.avg_per_res_capita = 0     # Average per capita use

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
        self.res_dailyindoor_vol = 155.0
        self.res_dailyindoor_np = 60.0
        self.res_dailyindoor_hot = 30.0
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
        self.create_parameter("com_demand", DOUBLE, "Commercial water demand value")
        self.create_parameter("com_var", DOUBLE, "Variation in commercial water demand")
        self.create_parameter("com_units", STRING, "Units for commercial water demands")
        self.create_parameter("com_hot", DOUBLE, "Proportion of hot water for commercial water demand")
        self.com_demand = 20.0
        self.com_var = 0.0
        self.com_units = "LSQMD"    # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
        self.com_hot = 20.0

        self.create_parameter("office_demand", DOUBLE, "Office water demand value")
        self.create_parameter("office_var", DOUBLE, "Variation in office water demand")
        self.create_parameter("office_units", STRING, "Units for office water demands")
        self.create_parameter("office_hot", DOUBLE, "Proportion of hot water for office water demand")
        self.office_demand = 20.0
        self.office_var = 0.0
        self.office_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
        self.office_hot = 20.0

        self.create_parameter("li_demand", DOUBLE, "Light Industry water demand value")
        self.create_parameter("li_var", DOUBLE, "Variation in Light Industry water demand")
        self.create_parameter("li_units", STRING, "Units for Light Industry water demands")
        self.create_parameter("li_hot", DOUBLE, "Proportion of hot water for Light Industry water demand")
        self.li_demand = 20.0
        self.li_var = 0.0
        self.li_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
        self.li_hot = 20.0

        self.create_parameter("hi_demand", DOUBLE, "Heavy Industry water demand value")
        self.create_parameter("hi_var", DOUBLE, "Variation in Heavy Industry water demand")
        self.create_parameter("hi_units", STRING, "Units for Heavy Industry water demands")
        self.create_parameter("hi_hot", DOUBLE, "Proportion of hot water for Heavy Industry water demand")
        self.hi_demand = 20.0
        self.hi_var = 0.0
        self.hi_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
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
        self.create_parameter("waterloss_volprop", DOUBLE, "Loss as volume of total demand proportion")
        self.estimate_waterloss = 1
        self.waterloss_volprop = 10.0

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
            map_attr.add_attribute("HasOVERLAYS", 1)
            self.map_planning_rules()
        else:
            map_attr.add_attribute("HasOVERLAYS", 0)

        # LAND COVER
        if self.landcover:
            map_attr.add_attribute("HasLANDCOVER", 1)
            for block_attr in blockslist:
                if block_attr.get_attribute("Status") == 0:
                    continue
                self.map_land_surface_covers(block_attr)
        else:
            map_attr.add_attribute("HasLANDCOVER", 0)

        # OPEN SPACE ANALYSIS
        if self.openspaces:
            map_attr.add_attribute("HasOPENSPACEMAP", 1)
            self.map_open_spaces(map_attr)
        else:
            map_attr.add_attribute("HasOPENSPACEMAP", 0)

        # WATER USE
        if self.wateruse:
            map_attr.add_attribute("HasWATERUSE", 1)
            if self.residential_method == "EUA":
                self.flowrates = self.retrieve_standards(self.res_standard)  # Get the flowrates from the standards
                self.baserating = self.flowrates["RatingCats"].index(self.res_base_efficiency)  # The index to look up
                self.res_endusebasedemands()    # Initialize the calculation of base end use demands
            self.initialize_per_capita_residential_use()    # As a statistic and also for non-residential stuff.
            for block_attr in blockslist:
                if block_attr.get_attribute("Status") == 0:
                    continue
                self.map_water_consumption(block_attr)
            # SAVE PATTERN DATA INTO MAP ATTRIBUTES
            categories = ubglobals.DIURNAL_CATS
            map_attr.add_attribute("dp_losses", ubglobals.CDP)  # Add constant pattern for losses
            for cat in ubglobals.DIURNAL_CATS:
                if eval("self."+cat+"_pat") == "SDD":
                    map_attr.add_attribute("dp_" + cat, ubglobals.SDD)
                elif eval("self."+cat+"_pat") == "CDP":
                    map_attr.add_attribute("dp_" + cat, ubglobals.CDP)
                elif eval("self."+cat+"_pat") == "OHT":
                    map_attr.add_attribute("dp_" + cat, ubglobals.OHT)
                elif eval("self."+cat+"_pat") == "AHC":
                    map_attr.add_attribute("dp_" + cat, ubglobals.AHC)
                else:
                    map_attr.add_attribute("dp_" + cat, eval("self."+cat+"_cp"))
        else:
            map_attr.add_attribute("HasWATERUSE", 0)

        # POLLUTION EMISSIONS
        if self.emissions:
            map_attr.add_attribute("HasPOLLUTIONMAP", 1)
            self.map_pollution_emissions()
        else:
            map_attr.add_attribute("HasPOLLUTIONMAP", 0)
        return True

    def map_planning_rules(self):
        pass

    def map_land_surface_covers(self, block_attr):
        """Maps the land surface covers of the current Block passed to this method. UrbanBEATS uses a few basic land
        cover types to differentiate including: CO = concrete, AS = asphalt, DG = dry grass, IG = irrigated grass,
        RF = roof, TR = trees.

        A number of attributes are added to each Block by the end of this function, denoting the land surface cover
        distribution for each land cover type. The function also tallies up the total land cover proportions for the
        Block.

        Attributes include:
        ----------------------------------------------------------------------------------------------------------------
        Land Use            Dry Grass (DG)  Irrig. Grass(IG)   Concrete (CO)   Asphalt (AS)    Trees (TR)    Roof (RF)
        ----------------------------------------------------------------------------------------------------------------
        Residential(Houses)     x               x                   x               x               x           x
        Residential (Flats)     x               x                   x               x               x           x
        Commercial (COM)        x               x                   x               x               x           x
        Light Industry (LI)     x               x                   x               x               x           x
        Heavy Industry (HI)     x               x                   x               x               x           x
        Offices Mixed Dev (ORC) x               x                   x               x               x           x
        Parks and Gardens (PG)  x               x                   x               x               x           -
        Reserves (REF)          x               x                   -               -               -           -
        Service/Utility (SVU)   x               -                   -               -               -           -
        Major Roads (RD)        x               -                   x               x               -           -
        Undeveloped (UND)       x               x                   -               -               -           -
        Unclassified (UNC)      x               x                   x               -               -           -
        ----------------------------------------------------------------------------------------------------------------
        Each attribute name is preceded by: LC_[cat]_[type] - note for residential both houses and flats use RES as the
        category abbreviation since a Block can only have either or type of residential typology. Civic and Transport
        Land uses to follow. These should most likely have look-up dictionaries that can simply be mapped over in future
        versions.

        :param block_attr: The UBVector() format of the current Block whose land cover needs to be determined
        :return: No return, block attributes are writen to the current block_attr object
        """
        # MAP RESIDENTIAL LAND COVER
        A_res = float(block_attr.get_attribute("pLU_RES") * block_attr.get_attribute("Active"))
        if block_attr.get_attribute("HasRes") and block_attr.get_attribute("HasFlats"):
            self.landcover_apartments(block_attr, A_res)
        else:
            self.landcover_houses(block_attr, A_res)    # Otherwise map using landcover_houses() as it catches zero case

        # MAP NON-RESIDENTIAL LAND COVER
        abbr = ["COM", "LI", "HI", "ORC"]
        for nonres_type in abbr:        # Loop over the four main types
            A_lu = float(block_attr.get_attribute("pLU_"+str(nonres_type)) * block_attr.get_attribute("Active"))
            self.landcover_nonres(block_attr, nonres_type, A_lu)

        # MAP OTHER TYPES
        self.landcover_unclassified(block_attr)
        self.landcover_undeveloped(block_attr)
        self.landcover_openspaces(block_attr)
        self.landcover_roads(block_attr)
        return True

    def landcover_houses(self, block_attr, A_res):
        """Determines proportions of land cover on residential land and provides a percentage estimate for the
        block. The estimate is done at the house level and then scaled up to the neighbourhood.

        :param block_attr: the UBVector() instance of the current Block.
        :param A_res: the area of the residential land use in the current block.
        """
        lcover = {"IG": 0.00, "DG": 0.00, "CO": 0.00, "AS": 0.00, "TR": 0.00, "RF": 0.00}   # Tracker Dictionary

        if A_res == 0:      # If residential area is zero, just add all the 0.00 proportions
            for k in lcover.keys():
                block_attr.add_attribute("LC_RES_"+str(k), lcover[k])
            return True

        # GOING THROUGH URBAN ELEMENTS (Roof, Paving, Garden, Other Pervious, Nature Strip, Footpath, Road)
        lcover["RF"] += float(block_attr.get_attribute("ResRoof") * block_attr.get_attribute("ResAllots"))  # ROOF
        lcover[self.surfDriveway] += (block_attr.get_attribute("ResLotTIA") - block_attr.get_attribute("ResRoof")) * \
                                     block_attr.get_attribute("ResAllots")      # PAVED SURFACES

        # Irrigated grass - (3) Garden, (4) Other Pervious, (5) Nature Strip
        perviouslot = block_attr.get_attribute("ResGarden") * block_attr.get_attribute("ResAllots")
        freespace = block_attr.get_attribute("avLt_RES") * block_attr.get_attribute("ResAllots")
        nstrip = block_attr.get_attribute("ResANstrip")
        if self.wateruse and self.res_outdoor_vol == 0.0:
            # lcover["IG"] += 0.0       # Note: commented out because it is a redundant operation, just here for clarity
            lcover["DG"] += perviouslot + nstrip        # Allocate all to dry grass if no irrigation
        else:
            if self.surfResIrrigate == "G":     # Only garden irrigated
                lcover["IG"] += freespace
                lcover["DG"] += (perviouslot - freespace) + nstrip
            else:       # All surface irrigated
                lcover["IG"] += perviouslot + nstrip
                # lcover["DG"] += 0.0

        lcover[self.surfArt] += float(block_attr.get_attribute("ResARoad"))
        lcover[self.surfFpath] += float(block_attr.get_attribute("ResAFpath"))

        # WRITE ATTRIBUTES TO THE BLOCK
        for k in lcover.keys():
            block_attr.add_attribute("LC_RES_"+str(k), lcover[k]/float(A_res))
        return True

    def landcover_apartments(self, block_attr, A_res):
        """Maps the land surface cover of Residential Apartment areas. Apartments are distinguished from houses in
        that they are more aggregated in the model. Attributes are therefore different and no scaling-up is required.

        :param block_attr: the UBVector() object of the current Block for which land cover is calculated.
        :param A_res"""
        lcover = {"IG": 0.00, "DG": 0.00, "CO": 0.00, "AS": 0.00, "TR": 0.00, "RF": 0.00}

        if A_res == 0:
            for k in lcover.keys():
                block_attr.add_attribute("LC_RES_"+str(k), float(lcover[k]))    # Write zeroes

        # GOING THROUGH URBAN ELEMENTS (Roof, Paving, Garden, Other Pervious, Nature Strip, Footpath, Road)
        lcover["RF"] += float(block_attr.get_attribute("HDRRoofA"))     # Building Roof
        lcover[self.surfDriveway] += float(block_attr("HDR_TIA") - block_attr("HDR_RoofA"))     # Paving

        # Pervious Areas (3) Garden, (4) Other Pervious, (5) Nature Strip
        perviouslot = block_attr.get_attribute("HDRGarden")
        freespace = block_attr.get_attribute("av_HDRes")
        if self.surfResIrrigate == "G":     # Only garden irrigated
            lcover["IG"] += freespace
            lcover["DG"] += perviouslot - freespace
        else:       # All surface irrigated
            lcover["IG"] += perviouslot
            lcover["DG"] += 0

        # Transfer all attributes to the Block UBVector()
        for k in lcover.keys():
            block_attr.add_attribute("LC_RES_"+str(k), lcover[k]/float(A_res))
        return True

    def landcover_nonres(self, block_attr, nonres_type, A_nres):
        """Maps the land surface covers of non-residential areas. COM, LI, HI or ORC land uses considered here.

        :param block_attr: the UBVector() instance of the current Block
        :param nonres_type: "LI", "HI", "ORC", "COM", string input of one of the four non-res built environment types
        :param A_nres: the current area of the nonresidential district used for totals
        """
        lcover = {"IG": 0.00, "DG": 1.00, "CO": 0.00, "AS": 0.00, "TR": 0.00, "RF": 0.00}   # DG = 1.0 by default
        if not block_attr.get_attribute("Has"+str(nonres_type)) or A_nres == 0:
            # Write default attributes and skip this function.
            for k in lcover.keys():
                block_attr.add_attributes("LC_"+str(nonres_type)+"_"+str(k), float(lcover[k]))
            return True

        # Calculate land covers
        lcover[self.surfArt] += float(block_attr.get_attribute(str(nonres_type)+"ARoad"))   # Road Land cover
        lcover[self.surfParking] += float(block_attr.get_attribute(str(nonres_type)+"AeCPark"))     # Carpark surface
        lcover[self.surfBay] += float(block_attr.get_attribute(str(nonres_type)+"AeLoad"))  # Loading Bay
        lcover["RF"] += float(block_attr.get_attribute(str(nonres_type)+"AeBldg"))      # Roof Cover
        lcover[self.surfHard] += float(block_attr.get_attribute(str(nonres_type)+"AeLgrey"))    # Grey Landscape
        lcover["DG"] += float(block_attr.get_attribute(str(nonres_type)+"ANstrip"))     # Nature Strip
        lcover[self.surfFpath] += float(block_attr.get_attribute(str(nonres_type)+"AFpath"))    # Footpath

        # Determine if landscaped area is irrigated or not
        if self.wateruse and self.nonres_landscape_vol == 0:
            # Dry grass - because irrigation volume is zero!
            lcover["DG"] += float(block_attr.get_attribute("avLt_"+str(nonres_type)))
        else:   # Otherwise assume irrigated!
            lcover["IG"] += float(block_attr.get_attribute("avLt_"+str(nonres_type)))

        # Tally up percentages of land covers and add to block_attr immediately
        for cover in lcover.keys():
            block_attr.add_attribute("LC_"+str(nonres_type)+"_"+str(k), float(lcover[cover] / A_nres))
            # Attributes for e.g. LI:  "LC_LI_IG", "LC_LI_DG", "LC_LI_CO", "LC_LI"AS", "LC_LI_TR", "LC_LI_TR"
        return True

    def landcover_unclassified(self, block_attr):
        """Determines land cover composition for the unclassified land within current block. Three covers considered.
        Writes the results to the current block_attr vector."""
        # UNCLASSIFIED LAND - Three types: Irrigated/dry grass and concrete
        unc_land = block_attr.get_attribute("MiscAtot")
        if unc_land != 0:
            pervious_prop = float(block_attr.get_attribute("MiscAirr") / unc_land)
            if self.wateruse and self.irrigate_landmarks:  # Link with water demand!
                block_attr.add_attribute("LC_NA_IG", pervious_prop)
                block_attr.add_attribute("LC_NA_DG", 0.00)
            else:
                block_attr.add_attribute("LC_NA_DG", pervious_prop)
                block_attr.add_attribute("LC_NA_IG", 0.00)
            block_attr.add_attribute("LC_NA_CO", float(block_attr.get_attribute("MiscAimp") / unc_land))
        else:
            block_attr.add_attribute("LC_NA_DG", 0.00)  # If the area is zero, then all land cover proportions are zero
            block_attr.add_attribute("LC_NA_IG", 0.00)
            block_attr.add_attribute("LC_NA_CO", 0.00)
        return True

    def landcover_undeveloped(self, block_attr):
        """Calculates the land cover composition of undeveloped land. Can take either dry or irrigated grass.
        Writes the information to the current block_attr vector."""
        # UNDEVELOPED LAND - Two types: irrigated/dry grass dependent on type of undev land
        if block_attr.get_attribute("pLU_UND") != 0:
            if block_attr.get_attribute("UND_Type") in ["BF", "GF", "NA"]:  # If greenfield, brownfield or undetermined...
                block_attr.add_attribute("LC_UND_DG", 1.0)
                block_attr.add_attribute("LC_UND_IG", 0.0)
            else:
                block_attr.add_attribute("LC_UND_DG", 0.0)
                block_attr.add_attribute("LC_UND_IG", 1.0)
        else:   # If there is no undeveloped land
            block_attr.add_attribute("LC_UND_DG", 0.0)
            block_attr.add_attribute("LC_UND_IG", 0.0)
        return True

    def landcover_openspaces(self, block_attr):
        """Calculates the land cover composition of open spaces within the current block, 'block_attr'.
        Writes these attributes to the block. Categories covered includes Service and Utility, Parks and
        Gardens and Reserves and Floodways."""
        # SERVICES & UTILITY - Assume dry grass all the time
        if block_attr.get_attribute("pLU_SVU") != 0:
            block_attr.add_attribute("LC_SVU_DG", 1.0)
        else:
            block_attr.add_attribute("LC_SVU_DG", 0.0)

        # OPEN SPACES - Five cover types: Irrigated Grass (IG), Dry Grass (DG), Concrete (CO), Asphalt (AS), Trees (TR)
        ig_lc, dg_lc, co_lc, as_lc, tr_lc = 0, 0, 0, 0, 0  # Initialize

        # Paved Areas - Concrete or Asphalt
        if self.surfSquare == "CO":
            co_lc += block_attr.get_attribute("ASquare")
        elif self.surfSquare == "AS":
            as_lc += block_attr.get_attribute("ASquare")
        else:
            dg_lc += block_attr.get_attribute("ASquare")

        # Irrigated Park Areas - Assume parks are irrigated by default, so check for whether this is not the case
        if self.wateruse and not self.irrigate_parks:
            dg_lc += block_attr("AGreenOS")
        else:
            ig_lc += block_attr("AGreenOS")

        if sum([co_lc, as_lc, dg_lc, ig_lc, tr_lc]) == 0:
            block_attr.add_attribute("LC_PG_CO", 0)
            block_attr.add_attribute("LC_PG_AS", 0)
            block_attr.add_attribute("LC_PG_DG", 0)
            block_attr.add_attribute("LC_PG_IG", 0)
            block_attr.add_attribute("LC_PG_TR", 0)
        else:
            block_attr.add_attribute("LC_PG_CO", float(co_lc / sum([co_lc, as_lc, dg_lc, ig_lc, tr_lc])))
            block_attr.add_attribute("LC_PG_AS", float(as_lc / sum([co_lc, as_lc, dg_lc, ig_lc, tr_lc])))
            block_attr.add_attribute("LC_PG_DG", float(dg_lc / sum([co_lc, as_lc, dg_lc, ig_lc, tr_lc])))
            block_attr.add_attribute("LC_PG_IG", float(ig_lc / sum([co_lc, as_lc, dg_lc, ig_lc, tr_lc])))
            block_attr.add_attribute("LC_PG_TR", float(tr_lc / sum([co_lc, as_lc, dg_lc, ig_lc, tr_lc])))

        # RESERVES - irrigated or dry grass - assume dry by default..
        if block_attr.get_attribute("pLU_REF") != 0:
            if self.wateruse and self.irrigate_reserves:
                block_attr.add_attribute("LC_REF_DG", 0.0)
                block_attr.add_attribute("LC_REF_IG", 1.0)
            else:
                block_attr.add_attribute("LC_REF_DG", 1.0)
                block_attr.add_attribute("LC_REF_IG", 0.0)
        else:
            block_attr.add_attribute("LC_REF_DG", 0.0)
            block_attr.add_attribute("LC_REF_IG", 0.0)
        return True

    def landcover_roads(self, block_attr):
        """Calculates the land cover composition of the road reserves within the current block 'block_attr'.
        Writes these attributes to the block."""
        # ROADS - Dependent on Road Types
        as_lc, co_lc, dg_lc = 0, 0, 0
        dg_lc += block_attr.get_attribute("RD_av")
        if self.surfArt == "AS":
            as_lc += block_attr.get_attribute("RoadTIA")
        elif self.surfArt == "CO":
            co_lc += block_attr.get_attribute("RoadTIA")
        else:
            dg_lc += block_attr.get_attribute("RoadTIA")

        if sum([co_lc, as_lc, dg_lc]) == 0:
            block_attr.add_attribute("LC_RD_CO", 0)
            block_attr.add_attribute("LC_RD_AS", 0)
            block_attr.add_attribute("LC_RD_DG", 0)
        else:
            block_attr.add_attribute("LC_RD_CO", float(co_lc / sum([co_lc, as_lc, dg_lc])))
            block_attr.add_attribute("LC_RD_AS", float(as_lc / sum([co_lc, as_lc, dg_lc])))
            block_attr.add_attribute("LC_RD_DG", float(dg_lc / sum([co_lc, as_lc, dg_lc])))
        # [TO DO] NEED TO FIX UP THE INTRICACIES OF THE ROAD RESERVE, THIS REQUIRES MORE ATTRIBUTES IN URBAN PLAN MOD.
        return True

    def map_open_spaces(self, map_attr):
        """Maps the open space connectivity and accessibility as well as some key planning aspects surrounding POS.
        Two key maps are created and analysed: Open Space Connectivity and Open Space Network. Note that the algorithm
        is only usable if patch delineation is used in the Spatial Delineation. This is therefore checked before
        any function is called.

        Open Space Connectivity: A measure of the distance to the closest open space. All non-green patches are checked
            against green patches and the closest link is calculated.
        Open Space Network: A measure of how connected the open spaces are to each other. A network is plotted of all
            connections between open spaces within an acceptable distance to each other. The network serves to be
            analysed spatially and using network characteristics to better understand how we can better plan open spaces
            in the urban environment. Connected components show how many sub-networks there are, node degree and
            centrality indicates the key locations of crucial connections.

        Sub-Methods Belonging to map_open_spaces():
            -
            -
            -

        :param map_attr: the global MapAttributes UBComponent() instance.
        """
        if not map_attr.get_attribute("patchdelin"):        # Check on whether patches were delineated
            map_attr.add_attribute("HasOSNET", 0)
            map_attr.add_attribute("HasOSLINK", 0)
            return True
        blocksize = map_attr.get_attribute("BlockSize")

        green_patches, grey_patches, non_patches = self.retrieve_patch_groups()
        if len(green_patches) > 0:
            # 7.1 - Open Space Distances
            if self.osnet_accessibility:
                self.find_open_space_distances(green_patches, grey_patches, non_patches)
                map_attr.add_attribute("HasOSLINK", 1)
            else:
                map_attr.add_attribute("HasOSLINK", 0)
            # 7.2 - Open Space Network
            if self.osnet_network:
                # The minimum acceptable distance to connect the network is taken as the final block size, if two
                # entire Block patches exist, they are adjacent and connected by Block centroid
                min_dist = blocksize * math.sqrt(2)
                self.delineate_open_space_network(green_patches, grey_patches, non_patches, min_dist)
                map_attr.add_attribute("HasOSNET", 1)
            else:
                map_attr.add_attribute("HasOSNET", 0)
        else:
            self.notify("Warning, no open spaces in map, cannot check for links")
            map_attr.add_attribute("HasOSLINK", 0)
            map_attr.add_attribute("HasOSNET", 0)
        # [TO DO] other open space functionality
        return True

    def retrieve_patch_groups(self):
        """Scans the simulation's patches and subdivides them into three groups based on land use. Returns three lists,
        each containing all references to UBVector() objects with corresponding patch type.

        :return: greenpatches (list of all PG and REF land use patchs), roadpatches (list of all RD patches), and
                 greypathces (everything else)
        """
        # Get all patches in the collection
        patches = self.scenario.get_assets_with_identifier("PatchID")     # Retrieves all patches

        # From all the patches, sort out the open space patches as a separate array
        greenpatches = []
        greypatches = []
        roadpatches = []
        for i in patches:
            if i.get_attribute("Landuse") in [10, 11]:
                greenpatches.append(i)
            elif i.get_attribute("Landuse") in [8]:
                roadpatches.append(i)
            else:
                greypatches.append(i)
        return greenpatches, greypatches, roadpatches

    def find_open_space_distances(self, green_patches, grey_patches, non_patches):
        """Calculates the location of the closest green space within the map. Considers PG and REF land uses. Distances
        are calculated between the grey patches, which is a list of non-park patches and green patches.

        :param green_patches: list containing UBVector() instances of all PG/REF patches in the map
        :param grey_patches: list containing UBVector() instances fo all non PG/REF patches
        :param non_patches: list containing UBVector() instances fo all patches that should not be considered
        :return: Modifies the existing patch UBVector() instance and adds OSLink assets to the scenario
        """
        # Find the distance to nearest green space in all grey patches
        oslink_id = 1
        for grey in grey_patches:
            prev_dist = 9999999999999999    # Initialize with something absurdly high!
            pts_current = (0, 0)        # Initialize
            current_green = None     # Initialize
            pts1 = grey.get_points()

            for green in green_patches:
                pts2 = green.get_points()
                current_dist = math.sqrt(pow(pts1[0] - pts2[0], 2) + pow(pts1[1] - pts2[1],2))
                if current_dist < prev_dist:
                    prev_dist = current_dist
                    pts_current = pts2
                    current_green = green
                    grey.add_attribute("GSD_Dist", prev_dist)
                    grey.add_attribute("GSD_Loc", str(green.get_attribute("BlockID"))+"_"+
                                       str(green.get_attribute("PatchID")))
                    grey.add_attribute("GSD_Deg", 0)
                    grey.add_attribute("GSD_ACon", 0)

            # Draw the link line
            dist_line = ubdata.UBVector(((pts1[0], pts1[1]), (pts_current[0], pts_current[1])))
            dist_line.add_attribute("OSLinkID", oslink_id)
            dist_line.add_attribute("Distance", prev_dist)
            dist_line.add_attribute("Location", grey.get_attribute("GSD_Loc"))
            dist_line.add_attribute("Landuse", grey.get_attribute("Landuse"))
            dist_line.add_attribute("AreaAccess", grey.get_attribute("PatchArea"))
            dist_line.add_attribute("OS_Size", current_green.get_attribute("PatchArea"))
            self.scenario.add_asset("OSLinkID"+str(oslink_id), dist_line)
            oslink_id += 1

        # For all green patches, write the same attributes and calculate the degree of connection
        for green in green_patches:
            patch_name = str(green.get_attribute("BlockID"))+"_"+str(green.get_attribute("PatchID"))
            degree = 0
            urban_area_connected = 0
            for grey in grey_patches:
                if grey.get_attribute("GSD_Loc") == patch_name:
                    degree += 1
                    urban_area_connected += grey.get_attribute("PatchArea")

            green.add_attribute("GSD_Dist", 0)
            green.add_attribute("GSD_Loc", str(green.get_attribute("BlockID"))+"_"+
                                str(green.get_attribute("PatchID")))
            green.add_attribute("GSD_Deg", degree)
            green.add_attribute("GSD_ACon", urban_area_connected)

        # For non-patches, add all default attributes
        for non in non_patches:
            non.add_attribute("GSD_Dist", -1)
            non.add_attribute("GSD_Loc", "")
            non.add_attribute("GSD_Deg", 0)
            non.add_attribute("GSD_ACon", 0)
        return True

    def delineate_open_space_network(self, green_patches, grey_patches, non_patches, min_dist):
        """Create a network of open spaces, only considers Parks and Reserves/Floodways

        :param green_patches: a list containing UBVector() instances of green patches
        :param grey_patches: a list of UBVector() instances of grey patches
        :param non_patches: a list of UBVector() instances representing road patches
        :return: modifies the existing patch data and adds OSNet assets to the scenario
        """
        osnet_id = 1
        for g in green_patches:             # For each green patch, find the next closest patch
            degrees = 0
            pts1 = g.get_points()   # Get the patchXY
            prev_dist = -1
            for h in green_patches:
                if h.get_attribute("BlockID") == g.get_attribute("BlockID") \
                        and h.get_attribute("PatchID") == g.get_attribute("PatchID"):
                    continue    # If it's the same patch, don't do anything!!
                pts2 = h.get_points()
                current_dist = math.sqrt(pow(pts1[0]-pts2[0], 2) + pow(pts1[1]-pts2[1], 2))
                if current_dist <= min_dist:
                    degrees += 1

                    link = ubdata.UBVector(((pts1[0], pts1[1]), (pts2[0], pts2[1])))
                    link.add_attribute("OSNetID", osnet_id)
                    link.add_attribute("NodeA", str(g.get_attribute("BlockID")) + "_" +
                                       str(g.get_attribute("PatchID")))
                    link.add_attribute("NodeB", str(h.get_attribute("BlockID")) + "_" +
                                       str(h.get_attribute("PatchID")))
                    link.add_attribute("Distance", current_dist)
                    self.scenario.add_asset("OSNetID" + str(osnet_id), link)
                    osnet_id += 1

                    if prev_dist == -1 or current_dist < prev_dist:
                        prev_dist = current_dist

            g.add_attribute("OSNet_Deg", degrees)
            g.add_attribute("OSNet_MinD", prev_dist)

        # Add the new attributes to all patches that aren't parks for completeness
        for g in grey_patches:
            g.add_attribute("OSNet_Deg", 0)
            g.add_attribute("OSNet_MinD", -1)
        for n in non_patches:
            n.add_attribute("OSNet_Deg", 0)
            n.add_attribute("OSNet_MinD", -1)
        return True

    def map_water_consumption(self, block_attr):
        """Calculates the water consumption and temporal water demand/wastewater trends for the input block. The demand
        is broken into Residential, Non-residential, Open Spaces, Losses and the seasonal dynamics thereof.

        :param block_attr: The UBVector() format of the current Block whose water consumption needs to be determined.
        :return: No return, block attributes are written to the current block_attr object.
        """
        # RESIDENTIAL WATER DEMAND
        if self.residential_method == "EUA":
            self.res_enduseanalysis(block_attr)
        else:
            self.res_directanalysis(block_attr)
        self.res_irrigation(block_attr)

        # NON-RESIDENTIAL WATER DEMAND AND PUBLIC OPEN SPACES
        self.nonres_waterdemands(block_attr)
        self.public_spaces_wateruse(block_attr)

        # FINAL TOTALS
        self.tally_total_block_wateruse(block_attr)
        return True

    def res_endusebasedemands(self):
        """Calculates the base demand values for the five end uses, which can then be adjusted depending on the
        stochastic variation introduced in the model and the occupancy."""
        self.kitchendem = self.res_kitchen_fq * self.res_kitchen_dur * self.flowrates["Kitchen"][self.baserating]
        self.showerdem = self.res_shower_fq * self.res_shower_dur * self.flowrates["Shower"][self.baserating]
        self.toiletdem = self.res_toilet_fq * self.flowrates["Toilet"][self.baserating]
        self.laundrydem = self.res_laundry_fq * self.flowrates["Laundry"][self.baserating]
        self.dishwasherdem = self.res_dishwasher_fq * self.flowrates["Dishwasher"][self.baserating]
        return True

    def initialize_per_capita_residential_use(self):
        """Calculates a quick per capita water use [L/day] based on the selected residential method."""
        map_attr = self.scenario.get_asset_with_name("MapAttributes")
        if self.residential_method == "EUA":
            avg_occup = map_attr.get_attribute("AvgOccup")
            self.avg_per_res_capita = self.kitchendem + self.showerdem + self.toiletdem + \
                                      float(self.laundrydem / avg_occup) + float(self.dishwasherdem / avg_occup)
        else:
            self.avg_per_res_capita = self.res_dailyindoor_vol
        map_attr.add_attribute("AvgPerCapWaterUse", self.avg_per_res_capita)
        return True

    def res_enduseanalysis(self, block_attr):
        """Conducts end use analysis for residential districts. Returns the flow rates for all demand sub-components.
        in a dictionary that can be queries. Demands returned are daily values except for irrigation, which is annual.
        """
        if block_attr.get_attribute("HasHouses") or block_attr.get_attribute("HasFlats"):
            # RESIDENTIAL INDOOR WATER DEMANDS
            if block_attr.get_attribute("HasHouses"):
                occup = block_attr.get_attribute("HouseOccup")
                qty = block_attr.get_attribute("ResHouses") # The total number of houses for up-scaling
            else:
                occup = block_attr.get_attribute("HDROccup")
                qty = block_attr.get_attribute("HDRFlats")      # The total number of units for up-scaling

            # Get base demands and scale to household level
            kitchendem = self.kitchendem * occup
            showerdem = self.showerdem * occup
            toiletdem = self.toiletdem * occup
            laundrydem = self.laundrydem
            dishwasherdem = self.dishwasherdem

            # Vary Demands
            kitchendemF = self.vary_demand_stochastically(kitchendem, self.res_kitchen_var/100.0)
            showerdemF = self.vary_demand_stochastically(showerdem, self.res_shower_var / 100.0)
            toiletdemF = self.vary_demand_stochastically(toiletdem, self.res_toilet_var / 100.0)
            laundrydemF = self.vary_demand_stochastically(laundrydem, self.res_laundry_var / 100.0)
            dishwasherdemF = self.vary_demand_stochastically(dishwasherdem, self.res_dishwasher_var / 100.0)

            indoor_demands = [kitchendemF, showerdemF, toiletdemF, laundrydemF, dishwasherdemF]
            hotwater_ratios = [self.res_kitchen_hot/100.0, self.res_shower_hot/100.0, self.res_toilet_hot/100.0,
                               self.res_laundry_hot/100.0, self.res_dishwasher_hot/100.0]
            # hotwater_volumes = indoor_demands X hotwater_ratios
            hotwater_volumes = [a*b for a,b in zip(indoor_demands, hotwater_ratios)]

            # Up-scale to Block Level
            blk_demands = [i * qty for i in indoor_demands]      # up-scale
            blk_hotwater = [i * qty for i in hotwater_volumes]

            # Work out Wastewater volumes by making boolean vectors
            gw = [int(self.res_kitchen_wwq == "GW"), int(self.res_shower_wwq == "GW"), int(self.res_toilet_wwq == "GW"),
                  int(self.res_laundry_wwq == "GW"), int(self.res_dishwasher_wwq == "GW")]
            bw = [int(self.res_kitchen_wwq == "BW"), int(self.res_shower_wwq == "BW"), int(self.res_toilet_wwq == "BW"),
                  int(self.res_laundry_wwq == "BW"), int(self.res_dishwasher_wwq == "BW")]

            # Write the information in terms of the single House level and the Block Level
            block_attr.add_attribute("WD_HHKitchen", indoor_demands[0])   # Household Kitchen use [L/hh/day]
            block_attr.add_attribute("WD_HHShower", indoor_demands[2])    # Household Shower use [L/hh/day]
            block_attr.add_attribute("WD_HHToilet", indoor_demands[2])    # Household Toilet use [L/hh/day]
            block_attr.add_attribute("WD_HHLaundry", indoor_demands[3])   # Household Laundry use [L/hh/day]
            block_attr.add_attribute("WD_HHDish", indoor_demands[4])      # Household Dishwasher [L/hh/day]
            block_attr.add_attribute("WD_HHIndoor", sum(indoor_demands))   # Total Household Use [L/hh/day]
            block_attr.add_attribute("WD_HHHot", sum(hotwater_volumes))    # Total Household Hot Water [L/hh/day]
            block_attr.add_attribute("HH_GreyW", sum([a * b for a, b in zip(gw, indoor_demands)])) # [L/hh/day]
            block_attr.add_attribute("HH_BlackW", sum([a * b for a, b in zip(bw, indoor_demands)]))  # [L/hh/day]

            block_attr.add_attribute("WD_Indoor", sum(blk_demands) / 1000.0)    # Total Block Indoor use [kL/day]
            block_attr.add_attribute("WD_HotVol", sum(blk_hotwater) / 1000.0)   # Total Block Hot Water [kL/day]
            block_attr.add_attribute("WW_ResGrey", sum([a * b for a, b in zip(gw, blk_demands)]))    # [kL/day]
            block_attr.add_attribute("WW_ResBlack", sum([a * b for a, b in zip(bw, blk_demands)]))   # [kL/day]

            map_attr = self.scenario.get_asset_with_name("MapAttributes")
            map_attr.add_attribute("WD_RES_Method", "EUA")
        else:   # If no residential, then simply set all attributes to zero
            block_attr.add_attribute("WD_HHKitchen", 0.0)
            block_attr.add_attribute("WD_HHShower", 0.0)
            block_attr.add_attribute("WD_HHToilet", 0.0)
            block_attr.add_attribute("WD_HHLaundry", 0.0)
            block_attr.add_attribute("WD_HHDish", 0.0)
            block_attr.add_attribute("WD_HHIndoor", 0.0)
            block_attr.add_attribute("WD_HHHot", 0.0)
            block_attr.add_attribute("HH_GreyW", 0.0)
            block_attr.add_attribute("HH_BlackW", 0.0)

            block_attr.add_attribute("WD_Indoor", 0.0)
            block_attr.add_attribute("WD_HotVol", 0.0)
            block_attr.add_attribute("WW_ResGrey", 0.0)
            block_attr.add_attribute("WW_ResBlack", 0.0)
        return True

    def res_directanalysis(self, block_attr):
        """Conducts the direct input analysis of residential water demand."""
        if block_attr.get_attribute("HasHouses") or block_attr.get_attribute("HasFlats"):
            # RESIDENTIAL INDOOR WATER DEMANDS
            if block_attr.get_attribute("HasHouses"):
                occup = block_attr.get_attribute("HouseOccup")
                qty = block_attr.get_attribute("ResHouses")  # The total number of houses for up-scaling
            else:
                occup = block_attr.get_attribute("HDROccup")
                qty = block_attr.get_attribute("HDRFlats")  # The total number of units for up-scaling

            # Calculate indoor demand for one household
            volHH = float(self.res_dailyindoor_vol * occup)
            volHHF = self.vary_demand_stochastically(volHH, self.res_dailyindoor_var/100.0)     # Add variation
            volHot = volHHF * self.res_dailyindoor_hot/100.0    # Work out hot water and non-potable water
            volNp = volHHF * self.res_dailyindoor_np/100.0

            # Work out greywater/blackwater proportions
            propGW = 1.0 - (self.res_dailyindoor_bgprop + 100.0)/100.0/2.0
            propBW = 1.0 - propGW

            # Create attributes, up-scale at the same time.
            block_attr.add_attribute("WD_HHIndoor", volHHF)  # Household Indoor Water use [L/hh/day]
            block_attr.add_attribute("WD_HHHot", volHot)     # Household Indoor hot water [L/hh/day]
            block_attr.add_attribute("WD_HHNonPot", volNp)  # Household non-potable use [L/hh/day]
            block_attr.add_attribute("HH_GreyW", volHHF * propGW)     # HH Greywater [L/hh/day]
            block_attr.add_attribute("HH_BlackW", volHHF * propBW)    # HH Blackwater [L/hh/day]

            block_attr.add_attribute("WD_Indoor", volHHF * qty / 1000.0)    # Block Indoor Residential use [kL/day]
            block_attr.add_attribute("WD_HotVol", volHot * qty / 1000.0)    # Block Indoor Res Hot water use [kL/day]
            block_attr.add_attribute("WD_NonPotable", volNp * qty / 1000.0) # Block Res Nonpotable use [kL/day]
            block_attr.add_attribute("WW_ResGrey", volHHF * qty * propGW / 1000.0)  # Block Res Greywater [kL/day]
            block_attr.add_attribute("WW_ResBlack", volHHF * qty * propBW / 1000.0) # Block Res Blackwater [kL/day]

            map_attr = self.scenario.get_asset_with_name("MapAttributes")
            map_attr.add_attribute("WD_RES_Method", "DQI")
        else:
            block_attr.add_attribute("WD_HHIndoor", 0)
            block_attr.add_attribute("WD_HHHot", 0)
            block_attr.add_attribute("WD_HHNonPot", 0)
            block_attr.add_attribute("HH_GreyW", 0)
            block_attr.add_attribute("HH_BlackW", 0)

            block_attr.add_attribute("WD_Indoor", 0)
            block_attr.add_attribute("WD_HotVol", 0)
            block_attr.add_attribute("WD_NonPotable", 0)
            block_attr.add_attribute("WW_ResGrey", 0.0)
            block_attr.add_attribute("WW_ResBlack", 0.0)
        return True

    def res_irrigation(self, block_attr):
        """Calculates the irrigation water demands for residential households or apartments."""
        # GET METRICS FOR GARDEN SPACE
        if block_attr.get_attribute("HasHouses") or block_attr.get_attribute("HasFlats"):
            if block_attr.get_attribute("HasHouses"):
                garden = block_attr.get_attribute("ResGarden")
                qty = block_attr.get_attribute("ResAllots")  # The total number of houses for up-scaling
            else:
                garden = block_attr.get_attribute("HDRGarden")
                qty = 1     # If it's apartments, we don't sub-divide the garden space

            gardenVolHH = self.res_outdoor_vol * garden * 100.0 / 365.0          # Convert [ML/ha/year] to [L/day]
            block_attr.add_attribute("WD_HHGarden", gardenVolHH)                # Household garden irrigation [L/hh/day]
            block_attr.add_attribute("WD_Outdoor", gardenVolHH * qty / 1000.0)  # Block Residential Irrigation [kL/day]
        else:
            block_attr.add_attribute("WD_HHGarden", 0.0)
            block_attr.add_attribute("WD_Outdoor", 0.0)
        return True

    def nonres_waterdemands(self, block_attr):
        """Calculates non-residential water demands for commercial, industrial, offices land uses based on the unit
        flow rate or Population Equivalents method, which assumes water demands per floor space or employee."""
        # COMMERCIAL AREAS
        if block_attr.get_attribute("Has_COM"):
            if self.com_units == "LSQMD":
                floorspace = block_attr.get_attribute("COMFloors") * block_attr.get_attribute("COMAeBldg") * \
                             block_attr.get_attribute("COMestates")
                comdemand = self.com_demand * floorspace / 1000.0       # [kL/day]
            elif self.com_units == "LPAXD":
                comdemand = self.com_demand * block_attr.get_attribute("COMjobs") / 1000.0  # [kL/day]
            else:   # Units = PES
                comdemand = self.com_demand * self.avg_per_res_capita * block_attr.get_attribute("COMjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            compublicspace = block_attr.get_attribute("avLt_COM")
            comdemand = self.vary_demand_stochastically(comdemand, self.com_var/100.0)
            comhot = self.com_hot/100.0 * comdemand
        else:
            compublicspace = 0
            comdemand = 0
            comhot = 0

        # OFFICES
        if block_attr.get_attribute("Has_ORC"):
            if self.office_units == "LSQMD":
                floorspace = block_attr.get_attribute("ORCFloors") * block_attr.get_attribute("ORCAeBldg") * \
                             block_attr.get_attribute("ORCestates")
                orcdemand = self.office_demand * floorspace / 1000.0       # [kL/day]
            elif self.office_units == "LPAXD":
                orcdemand = self.office_demand * block_attr.get_attribute("ORCjobs") / 1000.0  # [kL/day]
            else:   # Units = PES
                orcdemand = self.office_demand * self.avg_per_res_capita * block_attr.get_attribute("ORCjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            orcpublicspace = block_attr.get_attribute("avLt_ORC")
            orcdemand = self.vary_demand_stochastically(orcdemand, self.office_var/100.0)
            orchot = self.office_hot/100.0 * orcdemand
        else:
            orcpublicspace = 0
            orcdemand = 0
            orchot = 0

        # LIGHT INDUSTRY
        if block_attr.get_attribute("Has_LI"):
            if self.li_units == "LSQMD":
                floorspace = block_attr.get_attribute("LIFloors") * block_attr.get_attribute("LIAeBldg") * \
                             block_attr.get_attribute("LIestates")
                lidemand = self.li_demand * floorspace / 1000.0       # [kL/day]
            elif self.li_units == "LPAXD":
                lidemand = self.li_demand * block_attr.get_attribute("LIjobs") / 1000.0  # [kL/day]
            else:   # Units = PES
                lidemand = self.li_demand * self.avg_per_res_capita * block_attr.get_attribute("LIjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            lipublicspace = block_attr.get_attribute("avLt_LI")
            lidemand = self.vary_demand_stochastically(lidemand, self.li_var/100.0)
            lihot = self.li_hot/100.0 * lidemand
        else:
            lipublicspace = 0
            lidemand = 0
            lihot = 0

        # HEAVY INDUSTRY
        if block_attr.get_attribute("Has_HI"):
            if self.hi_units == "LSQMD":
                floorspace = block_attr.get_attribute("HIFloors") * block_attr.get_attribute("HIAeBldg") * \
                             block_attr.get_attribute("HIestates")
                hidemand = self.hi_demand * floorspace / 1000.0       # [kL/day]
            elif self.hi_units == "LPAXD":
                hidemand = self.hi_demand * block_attr.get_attribute("HIjobs") / 1000.0  # [kL/day]
            else:   # Units = PES
                hidemand = self.hi_demand * self.avg_per_res_capita * block_attr.get_attribute("HIjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            hipublicspace = block_attr.get_attribute("avLt_HI")
            hidemand = self.vary_demand_stochastically(hidemand, self.hi_var/100.0)
            hihot = self.hi_hot/100.0 * hidemand
        else:
            hipublicspace = 0
            hidemand = 0
            hihot = 0

        # Non-Res Irrigation
        total_irrigation_space = compublicspace + orcpublicspace + lipublicspace + hipublicspace
        irrigation_vol = total_irrigation_space / 10000.0 * self.nonres_landscape_vol * 1000.0 / 365.0  # [kL/day]

        # GW and WW factors
        com_propGW = 1.0 - (self.com_ww_bgprop + 100.0) / 100.0 / 2.0
        com_propBW = 1.0 - com_propGW
        ind_propGW = 1.0 - (self.ind_ww_bgprop + 100.0) / 100.0 / 2.0
        ind_propBW = 1.0 - ind_propGW

        block_attr.add_attribute("WD_COM", comdemand)       # Commercial demand [kL/day]
        block_attr.add_attribute("WD_HotCOM", comhot)       # Commercial hot Water [kL/day]
        block_attr.add_attribute("WD_Office", orcdemand)    # Office demand [kL/day]
        block_attr.add_attribute("WD_HotOffice", orchot)    # Office hot water [kL/day]
        block_attr.add_attribute("WD_LI", lidemand)         # Light Industry demand [kL/day]
        block_attr.add_attribute("WD_HotLI", lihot)         # Light industry hot water [kL/day]
        block_attr.add_attribute("WD_HI", hidemand)         # Heavy Industry demand [kL/day]
        block_attr.add_attribute("WD_HotHI", hihot)         # Heavy industry hot water [kL/day]
        block_attr.add_attribute("WD_NRes", comdemand + orcdemand + lidemand + hidemand)    # Total non-res [kL/day]
        block_attr.add_attribute("WD_HotNRes", comhot + orchot + lihot + hihot)
        block_attr.add_attribute("WD_NResIrri", irrigation_vol)  # Total non-res irrigation [kL/day]
        block_attr.add_attribute("WW_ComGrey", (comdemand + orcdemand) * com_propGW)
        block_attr.add_attribute("WW_ComBlack", (comdemand + orcdemand) * com_propBW)
        block_attr.add_attribute("WW_IndGrey", (lidemand + hidemand) * ind_propGW)
        block_attr.add_attribute("WW_IndBlack", (lidemand + hidemand) * ind_propBW)

    def public_spaces_wateruse(self, block_attr):
        """Calculates the public open spaces water use, including mainly the irrigation of open spaces and landmark
        areas."""
        parkspace = block_attr.get_attribute("AGreenOS") * int(self.irrigate_parks)
        landmarkspace = block_attr.get_attribute("MiscAirr") * int(self.irrigate_landmarks)
        refspace = block_attr.get_attribute("REF_av") * int(self.irrigate_reserves)
        block_attr("WD_POSIrri", self.pos_irrigation_vol * 1000 / 365.0 *
                   (parkspace + landmarkspace + refspace) / 10000.0)    # Total OS irrigation [kL/day]
        return True

    def tally_total_block_wateruse(self, block_attr):
        """Scans the water demand attributes and calculates total demands for various sub-categories. Includes losses"""
        total_blk_indoor = block_attr.get_attribute("WD_Indoor") + block_attr.get_attribute("WD_NRes")
        total_irrigation = block_attr.get_attribute("WD_Outdoor") + block_attr.get_attribute("WD_NResIrri") + \
                           block_attr.get_attribute("WD_POSIrri")
        total_blk_hotwater = block_attr.get_attribute("WD_HotVol") + block_attr.get_attribute("WD_HotNRes")
        total_blk_greywater = block_attr.getget_attribute("WW_ResGrey") + block_attr.get_attribute("WW_ComGrey") + \
                              block_attr.get_attribute("WW_IndGrey")
        total_blk_blackwater = block_attr.getget_attribute("WW_ResBlack") + block_attr.get_attribute("WW_ComBlack") + \
                               block_attr.get_attribute("WW_IndBlack")
        total_blk_demand = total_blk_indoor + total_irrigation
        total_blk_ww = total_blk_greywater + total_blk_blackwater

        if self.estimate_waterloss:
            total_losses = self.waterloss_volprop/100.0 * total_blk_demand
        else:
            total_losses = 0.0

        block_attr.add_attribute("Blk_WD", total_blk_demand / 1000.0 * 365.0)   # Total Demand [ML/year]
        block_attr.add_attribute("Blk_WDIrri", total_irrigation / 1000.0 * 365.0)   # Total Irrigation [ML/year]
        block_attr.add_attribute("Blk_WDHot", total_blk_hotwater / 1000.0 * 365.0)  # Total Hot Water [ML/year]
        block_attr.add_attribute("Blk_WW", total_blk_ww / 1000.0 * 365.0)   # Total Block Wastewater [ML/year]
        block_attr.add_attribute("Blk_WWGrey", total_blk_greywater / 1000.0 * 365.0)    # Total greywater [ML/year]
        block_attr.add_attribute("Blk_WWBlack", total_blk_blackwater / 1000.0 * 365.0)  # Total blackwater [ML/year]
        block_attr.add_attribute("Blk_Losses", total_losses / 1000.0 * 365.0)  # Total system losses [ML/year]
        return True

    def vary_demand_stochastically(self, basedemand, varyfactor):
        """Uses a uniform distribution to alter a base demand value by a variation factor [ ] either incrementally
        or decrementally. Returns the varied demand value."""
        if varyfactor == 0:
            return basedemand
        variedDemand = -1
        while variedDemand <= 0:
            variedDemand = basedemand + random.uniform(basedemand * varyfactor * (-1), basedemand * varyfactor)
        return variedDemand

    def retrieve_standards(self, st_name):
        """Retrieves the water flow rates for the respective appliance standard."""
        standard_dict = dict()
        standard_dict["Name"] = st_name
        standard_dict["Shower"] = []
        standard_dict["Kitchen"] = []
        standard_dict["Toilet"] = []
        standard_dict["Laundry"] = []
        standard_dict["Dishwasher"] = []
        standard_dict["RatingCats"] = []

        rootpath = self.activesim.get_program_rootpath()    # Get the program's root path
        f = open(rootpath+"/ancillary/appliances/"+st_name+".cfg", 'r')
        data = []
        for lines in f:
            data.append(lines.rstrip("\n").split(","))
        f.close()
        rating_cats = []
        for i in range(len(data)):      # Scan all data and create the dictionary
            if i == 0:  # Skip the header line
                continue
            if data[i][2] not in rating_cats:
                standard_dict["RatingCats"].append(data[i][2])
            standard_dict[data[i][1]].append(float(data[i][3])*0.5 + float(data[i][4])*0.5)
        print standard_dict
        return standard_dict

    def get_wateruse_custompattern(self, key):
        """Retrieves the _cp custom pattern vector from the given key, the keys are in UBGlobals for reference."""
        return eval("self." + str(key) + "_cp")

    def set_wateruse_custompattern(self, key, patternvector):
        """Sets the current custom pattern _cp of the parameter with the given key to the new patternvector."""
        exec ("self." + str(key) + "_cp = " + str(patternvector))

    def map_pollution_emissions(self):
        pass