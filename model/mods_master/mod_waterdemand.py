r"""
@file   mod_waterdemand.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2017-2022  Peter M. Bach

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
__copyright__ = "Copyright 2017-2022. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
from model.ubmodule import *
import random

class WaterDemandMapping(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Water Management"
    catorder = 1
    longname = "Water Demand Mapping"
    icon = ":/icons/hand-washing.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES
        self.assets = None
        self.meta = None
        self.xllcorner = None
        self.yllcorner = None
        self.assetident = ""
        self.populationmap = None
        self.nodata = None

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.assetcolname = "(select asset collection)"

        # -- RESIDENTIAL WATER USE --
        self.create_parameter("residential_method", STRING, "Method for determinining residential water use.")
        self.residential_method = "EUA"  # EUA = end use analysis, DQI = direct flow input

        self.flowrates = {}  # Initialize these variables, used in the EUA method
        self.baserating = 0

        # END USE ANALYSIS
        self.create_parameter("res_standard", STRING, "The water appliances standard to use in calculations.")
        self.res_standard = "AS6400"
        self.create_parameter("res_baseefficiency", DOUBLE, "The base level efficiency to use at simulation begin.")
        self.res_baseefficiency = 0.0  # Dependent on standard, represents the index of the water flow rates table.

        self.create_parameter("res_kitchen_fq", DOUBLE, "Frequency of kitchen water use.")
        self.create_parameter("res_kitchen_dur", DOUBLE, "Duration of kitchen water use.")
        self.create_parameter("res_kitchen_hot", DOUBLE, "Proportion of kitchen water from hot water")
        self.create_parameter("res_kitchen_var", DOUBLE, "Stochastic variation in kitchen water use")
        self.create_parameter("res_kitchen_ffp", STRING, "Minimum Fit for purpose water source for kitchen use.")
        self.res_kitchen_fq = 2.0
        self.res_kitchen_dur = 10.0
        self.res_kitchen_hot = 30.0
        self.res_kitchen_var = 0.0
        self.res_kitchen_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_shower_fq", DOUBLE, "Frequency of shower water use.")
        self.create_parameter("res_shower_dur", DOUBLE, "Duration of shower water use.")
        self.create_parameter("res_shower_hot", DOUBLE, "Proportion of shower water from hot water")
        self.create_parameter("res_shower_var", DOUBLE, "Stochastic variation in shower water use")
        self.create_parameter("res_shower_ffp", STRING, "Minimum Fit for purpose water source for shower use.")
        self.res_shower_fq = 2.0
        self.res_shower_dur = 5.0
        self.res_shower_hot = 60.0
        self.res_shower_var = 0.0
        self.res_shower_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_toilet_fq", DOUBLE, "Frequency of toilet water use.")
        self.create_parameter("res_toilet_hot", DOUBLE, "Proportion of toilet water from hot water")
        self.create_parameter("res_toilet_var", DOUBLE, "Stochastic variation in toilet water use")
        self.create_parameter("res_toilet_ffp", STRING, "Minimum Fit for purpose water source for toilet use.")
        self.res_toilet_fq = 2.0
        self.res_toilet_hot = 0.0
        self.res_toilet_var = 0.0
        self.res_toilet_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_laundry_fq", DOUBLE, "Frequency of laundry water use.")
        self.create_parameter("res_laundry_hot", DOUBLE, "Proportion of laundry water from hot water")
        self.create_parameter("res_laundry_var", DOUBLE, "Stochastic variation in laundry water use")
        self.create_parameter("res_laundry_ffp", STRING, "Minimum Fit for purpose water source for laundry use.")
        self.res_laundry_fq = 2.0
        self.res_laundry_hot = 50.0
        self.res_laundry_var = 0.0
        self.res_laundry_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.create_parameter("res_dishwasher_fq", DOUBLE, "Frequency of dishwasher water use.")
        self.create_parameter("res_dishwasher_hot", DOUBLE, "Proportion of dishwasher water from hot water")
        self.create_parameter("res_dishwasher_var", DOUBLE, "Stochastic variation in dishwasher water use")
        self.create_parameter("res_dishwasher_ffp", STRING, "Minimum Fit for purpose water source for dishwasher use.")
        self.res_dishwasher_fq = 1.0
        self.res_dishwasher_hot = 50.0
        self.res_dishwasher_var = 0.0
        self.res_dishwasher_ffp = "PO"  # PO = potable, NP = non-potable, RW = rainwater, GW = greywater, SW = storm

        self.kitchendem = 0  # Placeholders for the base unit demand (for kitchen/shower/toilet, it's per capita)
        self.showerdem = 0  # for laundry and dishwasher it's per household.
        self.toiletdem = 0
        self.laundrydem = 0
        self.dishwasherdem = 0
        self.avg_per_res_capita = 0  # Average per capita use

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
        self.res_dailyindoor_bgprop = 0.0  # default = 0 which is 50-50

        # -- NON-RESIDENTIAL WATER USE --
        self.create_parameter("com_demand", DOUBLE, "Commercial water demand value")
        self.create_parameter("com_var", DOUBLE, "Variation in commercial water demand")
        self.create_parameter("com_units", STRING, "Units for commercial water demands")
        self.create_parameter("com_hot", DOUBLE, "Proportion of hot water for commercial water demand")
        self.com_demand = 40.0
        self.com_var = 10.0
        self.com_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
        self.com_hot = 20.0

        self.create_parameter("office_demand", DOUBLE, "Office water demand value")
        self.create_parameter("office_var", DOUBLE, "Variation in office water demand")
        self.create_parameter("office_units", STRING, "Units for office water demands")
        self.create_parameter("office_hot", DOUBLE, "Proportion of hot water for office water demand")
        self.office_demand = 40.0
        self.office_var = 10.0
        self.office_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
        self.office_hot = 20.0

        self.create_parameter("li_demand", DOUBLE, "Light Industry water demand value")
        self.create_parameter("li_var", DOUBLE, "Variation in Light Industry water demand")
        self.create_parameter("li_units", STRING, "Units for Light Industry water demands")
        self.create_parameter("li_hot", DOUBLE, "Proportion of hot water for Light Industry water demand")
        self.li_demand = 40.0
        self.li_var = 10.0
        self.li_units = "LSQMD"  # LSQMD = L/sqm/day and LPAXD = L/persons/day, PES = Population equivalents
        self.li_hot = 20.0

        self.create_parameter("hi_demand", DOUBLE, "Heavy Industry water demand value")
        self.create_parameter("hi_var", DOUBLE, "Variation in Heavy Industry water demand")
        self.create_parameter("hi_units", STRING, "Units for Heavy Industry water demands")
        self.create_parameter("hi_hot", DOUBLE, "Proportion of hot water for Heavy Industry water demand")
        self.hi_demand = 40.0
        self.hi_var = 10.0
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
        self.create_parameter("loss_pat", STRING, "Diurnal pattern for Water Losses")
        self.estimate_waterloss = 1
        self.waterloss_volprop = 10.0
        self.loss_pat = "CDP"  # Either CDP or INV = inverse, which is generated

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
        self.sdd = SDD
        self.cdp = CDP
        self.oht = OHT
        self.ahc = AHC

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
        self.meta.add_attribute("mod_mapregions", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

        # PER-REQUISITES CHECK - needs to have a few modules run
        if self.meta.get_attribute("mod_urbanformgen") != 1:
            self.notify("Cannot start module! Asset collection has no urban form information yet.")
            return False

        # CLEAN THE ATTRIBUTES LIST
        att_schema = ["WD_HHKitchen", "WD_HHShower", "WD_HHToilet", "WD_HHLaundry", "WD_HHDish", "WD_HHIndoor",
                      "WD_HHHot", "HH_GreyW", "HH_BlackW", "WD_Indoor", "WD_HotVol", "WW_ResGrey", "WW_ResBlack",
                      "WD_HHNonPot", "WD_HHGarden", "WD_Outdoor", "WD_COM", "WD_HotCOM", "WD_Office", "WD_HotOffice",
                      "WD_LI", "WD_HotLI", "WD_HI", "WD_HotHI", "WD_NRes", "WD_HotNRes", "WD_NResIrri", "WW_ComGrey",
                      "WW_ComBlack", "WW_IndGrey", "WW_IndBlack", "WD_POSIrri", "Blk_WD", "Blk_WDIrri", "Blk_WDHot",
                      "Blk_WW", "Blk_WWGrey", "Blk_WWBlack", "Blk_Losses"]

        grid_assets = self.assets.get_assets_with_identifier(self.assetident)
        att_reset_count = 0
        for i in range(len(grid_assets)):
            for att in att_schema:
                if grid_assets[i].remove_attribute(att):
                    att_reset_count += 1
        self.notify("Removed "+str(att_reset_count)+" attribute entries")

        self.meta.add_attribute("mod_waterdemand", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")
        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")
        return True

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.notify_progress(0)
        if not self.initialize_runstate():
            self.notify("Module run terminated!")
            return True

        self.notify("Calculating water consumption and wastewater generation over the simulation grid.")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 1 - Get asset information
        self.griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets within the map: "+str(len(self.griditems)))
        total_assets = len(self.griditems)
        progress_counter = 0
        self.notify_progress(10)

        # --- SECTION 2 - Calculate water demands
        if self.residential_method == "EUA":
            self.flowrates = self.retrieve_standards(self.res_standard)  # Get the flowrates from the standards
            self.baserating = self.res_baseefficiency  # The index to look up
            self.res_endusebasedemands()  # Initialize the calculation of base end use demands
        self.initialize_per_capita_residential_use()  # As a statistic and also for non-residential stuff.

        for i in range(len(self.griditems)):

            # PROGRESS NOTIFIER
            progress_counter += 1
            if progress_counter > total_assets / 4:
                self.notify_progress(40)
            elif progress_counter > total_assets / 2:
                self.notify_progress(60)
            elif progress_counter > total_assets / 4 * 3:
                self.notify_progress(80)

            block_attr = self.griditems[i]
            currentID = block_attr.get_attribute("BlockID")

            if block_attr.get_attribute("Status") == 0:
                continue

            self.map_water_consumption(block_attr)

        # SAVE PATTERN DATA INTO MAP ATTRIBUTES
        self.notify_progress(90)
        self.notify("Saving off diurnal patterns.")

        categories = DIURNAL_CATS
        if self.loss_pat == "CDP":
            self.meta.add_attribute("DP_losses", CDP)  # Add constant pattern for losses
        else:
            self.meta.add_attribute("DP_losses", "INV")  # Invert the pattern when it is time to
        for cat in DIURNAL_CATS:
            if eval("self." + cat + "_pat") == "SDD":
                self.meta.add_attribute("dp_" + cat, SDD)
            elif eval("self." + cat + "_pat") == "CDP":
                self.meta.add_attribute("dp_" + cat, CDP)
            elif eval("self." + cat + "_pat") == "OHT":
                self.meta.add_attribute("dp_" + cat, OHT)
            elif eval("self." + cat + "_pat") == "AHC":
                self.meta.add_attribute("dp_" + cat, AHC)
            else:
                self.meta.add_attribute("dp_" + cat, eval("self." + cat + "_cp"))

        self.notify("Mapping of water demands complete.")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
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
        self.kitchendem = self.res_kitchen_fq * self.res_kitchen_dur * self.flowrates["Kitchen"][int(self.baserating)]
        self.showerdem = self.res_shower_fq * self.res_shower_dur * self.flowrates["Shower"][int(self.baserating)]
        self.toiletdem = self.res_toilet_fq * self.flowrates["Toilet"][int(self.baserating)]
        self.laundrydem = self.res_laundry_fq * self.flowrates["Laundry"][int(self.baserating)]
        self.dishwasherdem = self.res_dishwasher_fq * self.flowrates["Dishwasher"][int(self.baserating)]
        return True

    def initialize_per_capita_residential_use(self):
        """Calculates a quick per capita water use [L/day] based on the selected residential method."""
        if self.residential_method == "EUA":
            avg_occup = self.meta.get_attribute("AvgOccup")
            self.avg_per_res_capita = self.kitchendem + self.showerdem + self.toiletdem + \
                                      float(self.laundrydem / avg_occup) + float(self.dishwasherdem / avg_occup)
        else:
            self.avg_per_res_capita = self.res_dailyindoor_vol
        self.meta.add_attribute("AvgPerCapWaterUse", self.avg_per_res_capita)
        self.notify("The Average Per Capita Water Use is: " + str(self.avg_per_res_capita) + " L/day")
        return True

    def res_enduseanalysis(self, block_attr):
        """Conducts end use analysis for residential districts. Returns the flow rates for all demand sub-components.
        in a dictionary that can be queries. Demands returned are daily values except for irrigation, which is annual.
        """
        print("Entering End Use Analysis")
        if block_attr.get_attribute("HasHouses") or block_attr.get_attribute("HasFlats"):
            # RESIDENTIAL INDOOR WATER DEMANDS
            if block_attr.get_attribute("HasHouses"):
                occup = block_attr.get_attribute("HouseOccup")
                qty = block_attr.get_attribute("ResHouses")  # The total number of houses for up-scaling
            else:
                occup = block_attr.get_attribute("HDROccup")
                qty = block_attr.get_attribute("HDRFlats")  # The total number of units for up-scaling

            # Get base demands and scale to household level
            kitchendem = self.kitchendem * occup
            showerdem = self.showerdem * occup
            toiletdem = self.toiletdem * occup
            laundrydem = self.laundrydem
            dishwasherdem = self.dishwasherdem

            # Vary Demands
            kitchendemF = self.vary_demand_stochastically(kitchendem, self.res_kitchen_var / 100.0)
            showerdemF = self.vary_demand_stochastically(showerdem, self.res_shower_var / 100.0)
            toiletdemF = self.vary_demand_stochastically(toiletdem, self.res_toilet_var / 100.0)
            laundrydemF = self.vary_demand_stochastically(laundrydem, self.res_laundry_var / 100.0)
            dishwasherdemF = self.vary_demand_stochastically(dishwasherdem, self.res_dishwasher_var / 100.0)

            indoor_demands = [kitchendemF, showerdemF, toiletdemF, laundrydemF, dishwasherdemF]
            hotwater_ratios = [self.res_kitchen_hot / 100.0, self.res_shower_hot / 100.0, self.res_toilet_hot / 100.0,
                               self.res_laundry_hot / 100.0, self.res_dishwasher_hot / 100.0]
            # hotwater_volumes = indoor_demands X hotwater_ratios
            hotwater_volumes = [a * b for a, b in zip(indoor_demands, hotwater_ratios)]

            # Up-scale to Block Level
            blk_demands = [i * qty for i in indoor_demands]  # up-scale
            blk_hotwater = [i * qty for i in hotwater_volumes]

            # Work out Wastewater volumes by making boolean vectors
            gw = [int(self.res_kitchen_wwq == "G"), int(self.res_shower_wwq == "G"), int(self.res_toilet_wwq == "G"),
                  int(self.res_laundry_wwq == "G"), int(self.res_dishwasher_wwq == "G")]
            bw = [int(self.res_kitchen_wwq == "B"), int(self.res_shower_wwq == "B"), int(self.res_toilet_wwq == "B"),
                  int(self.res_laundry_wwq == "B"), int(self.res_dishwasher_wwq == "B")]

            # Write the information in terms of the single House level and the Block Level
            block_attr.add_attribute("WD_HHKitchen", indoor_demands[0])  # Household Kitchen use [L/hh/day]
            block_attr.add_attribute("WD_HHShower", indoor_demands[1])  # Household Shower use [L/hh/day]
            block_attr.add_attribute("WD_HHToilet", indoor_demands[2])  # Household Toilet use [L/hh/day]
            block_attr.add_attribute("WD_HHLaundry", indoor_demands[3])  # Household Laundry use [L/hh/day]
            block_attr.add_attribute("WD_HHDish", indoor_demands[4])  # Household Dishwasher [L/hh/day]
            block_attr.add_attribute("WD_HHIndoor", sum(indoor_demands))  # Total Household Use [L/hh/day]
            block_attr.add_attribute("WD_HHHot", sum(hotwater_volumes))  # Total Household Hot Water [L/hh/day]
            block_attr.add_attribute("HH_GreyW", sum([a * b for a, b in zip(gw, indoor_demands)]))  # [L/hh/day]
            block_attr.add_attribute("HH_BlackW", sum([a * b for a, b in zip(bw, indoor_demands)]))  # [L/hh/day]

            block_attr.add_attribute("WD_Indoor", sum(blk_demands) / 1000.0)  # Total Block Indoor use [kL/day]
            block_attr.add_attribute("WD_HotVol", sum(blk_hotwater) / 1000.0)  # Total Block Hot Water [kL/day]
            block_attr.add_attribute("WW_ResGrey", sum([a * b for a, b in zip(gw, blk_demands)]) / 1000.0)  # [kL/day]
            block_attr.add_attribute("WW_ResBlack", sum([a * b for a, b in zip(bw, blk_demands)]) / 1000.0)  # [kL/day]

            self.meta.add_attribute("WD_RES_Method", "EUA")
        else:  # If no residential, then simply set all attributes to zero
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
            volHHF = self.vary_demand_stochastically(volHH, self.res_dailyindoor_var / 100.0)  # Add variation
            volHot = volHHF * self.res_dailyindoor_hot / 100.0  # Work out hot water and non-potable water
            volNp = volHHF * self.res_dailyindoor_np / 100.0

            # Work out greywater/blackwater proportions
            propGW = 1.0 - (self.res_dailyindoor_bgprop + 100.0) / 100.0 / 2.0
            propBW = 1.0 - propGW

            # Create attributes, up-scale at the same time.
            block_attr.add_attribute("WD_HHIndoor", volHHF)  # Household Indoor Water use [L/hh/day]
            block_attr.add_attribute("WD_HHHot", volHot)  # Household Indoor hot water [L/hh/day]
            block_attr.add_attribute("WD_HHNonPot", volNp)  # Household non-potable use [L/hh/day]
            block_attr.add_attribute("HH_GreyW", volHHF * propGW)  # HH Greywater [L/hh/day]
            block_attr.add_attribute("HH_BlackW", volHHF * propBW)  # HH Blackwater [L/hh/day]

            block_attr.add_attribute("WD_Indoor", volHHF * qty / 1000.0)  # Block Indoor Residential use [kL/day]
            block_attr.add_attribute("WD_HotVol", volHot * qty / 1000.0)  # Block Indoor Res Hot water use [kL/day]
            block_attr.add_attribute("WD_NonPotable", volNp * qty / 1000.0)  # Block Res Nonpotable use [kL/day]
            block_attr.add_attribute("WW_ResGrey", volHHF * qty * propGW / 1000.0)  # Block Res Greywater [kL/day]
            block_attr.add_attribute("WW_ResBlack", volHHF * qty * propBW / 1000.0)  # Block Res Blackwater [kL/day]

            self.meta.add_attribute("WD_RES_Method", "DQI")
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
        print("Entering Irrigation Analysis")
        if block_attr.get_attribute("HasHouses") or block_attr.get_attribute("HasFlats"):
            if block_attr.get_attribute("HasHouses"):
                garden = block_attr.get_attribute("ResGarden")
                qty = block_attr.get_attribute("ResAllots")  # The total number of houses for up-scaling
            else:
                garden = block_attr.get_attribute("HDRGarden")
                qty = 1  # If it's apartments, we don't sub-divide the garden space

            gardenVolHH = self.res_outdoor_vol * garden * 100.0 / 365.0  # Convert [ML/ha/year] to [L/day]
            block_attr.add_attribute("WD_HHGarden", gardenVolHH)  # Household garden irrigation [L/hh/day]
            block_attr.add_attribute("WD_Outdoor", gardenVolHH * qty / 1000.0)  # Block Residential Irrigation [kL/day]
        else:
            block_attr.add_attribute("WD_HHGarden", 0.0)
            block_attr.add_attribute("WD_Outdoor", 0.0)
        return True

    def nonres_waterdemands(self, block_attr):
        """Calculates non-residential water demands for commercial, industrial, offices land uses based on the unit
        flow rate or Population Equivalents method, which assumes water demands per floor space or employee."""
        # COMMERCIAL AREAS
        print("Entering Non-Res Analysis")
        if block_attr.get_attribute("Has_COM"):
            if self.com_units == "LSQMD":
                floorspace = block_attr.get_attribute("COMFloors") * block_attr.get_attribute("COMAeBldg") * \
                             block_attr.get_attribute("COMestates")
                comdemand = self.com_demand * floorspace / 1000.0  # [kL/day]
            elif self.com_units == "LPAXD":
                comdemand = self.com_demand * block_attr.get_attribute("COMjobs") / 1000.0  # [kL/day]
            else:  # Units = PES
                comdemand = self.com_demand * self.avg_per_res_capita * block_attr.get_attribute("COMjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            compublicspace = block_attr.get_attribute("avLt_COM")
            comdemand = self.vary_demand_stochastically(comdemand, self.com_var / 100.0)
            comhot = self.com_hot / 100.0 * comdemand
        else:
            compublicspace = 0
            comdemand = 0
            comhot = 0

        # OFFICES
        if block_attr.get_attribute("Has_ORC"):
            if self.office_units == "LSQMD":
                floorspace = block_attr.get_attribute("ORCFloors") * block_attr.get_attribute("ORCAeBldg") * \
                             block_attr.get_attribute("ORCestates")
                orcdemand = self.office_demand * floorspace / 1000.0  # [kL/day]
            elif self.office_units == "LPAXD":
                orcdemand = self.office_demand * block_attr.get_attribute("ORCjobs") / 1000.0  # [kL/day]
            else:  # Units = PES
                orcdemand = self.office_demand * self.avg_per_res_capita * block_attr.get_attribute("ORCjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            orcpublicspace = block_attr.get_attribute("avLt_ORC")
            orcdemand = self.vary_demand_stochastically(orcdemand, self.office_var / 100.0)
            orchot = self.office_hot / 100.0 * orcdemand
        else:
            orcpublicspace = 0
            orcdemand = 0
            orchot = 0

        # LIGHT INDUSTRY
        if block_attr.get_attribute("Has_LI"):
            if self.li_units == "LSQMD":
                floorspace = block_attr.get_attribute("LIFloors") * block_attr.get_attribute("LIAeBldg") * \
                             block_attr.get_attribute("LIestates")
                lidemand = self.li_demand * floorspace / 1000.0  # [kL/day]
            elif self.li_units == "LPAXD":
                lidemand = self.li_demand * block_attr.get_attribute("LIjobs") / 1000.0  # [kL/day]
            else:  # Units = PES
                lidemand = self.li_demand * self.avg_per_res_capita * block_attr.get_attribute("LIjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            lipublicspace = block_attr.get_attribute("avLt_LI")
            lidemand = self.vary_demand_stochastically(lidemand, self.li_var / 100.0)
            lihot = self.li_hot / 100.0 * lidemand
        else:
            lipublicspace = 0
            lidemand = 0
            lihot = 0

        # HEAVY INDUSTRY
        if block_attr.get_attribute("Has_HI"):
            if self.hi_units == "LSQMD":
                floorspace = block_attr.get_attribute("HIFloors") * block_attr.get_attribute("HIAeBldg") * \
                             block_attr.get_attribute("HIestates")
                hidemand = self.hi_demand * floorspace / 1000.0  # [kL/day]
            elif self.hi_units == "LPAXD":
                hidemand = self.hi_demand * block_attr.get_attribute("HIjobs") / 1000.0  # [kL/day]
            else:  # Units = PES
                hidemand = self.hi_demand * self.avg_per_res_capita * block_attr.get_attribute("HIjobs") / 1000.0
                # It is equal to the (PE Factor) x (the average residential per capita use) x (total employed)

            hipublicspace = block_attr.get_attribute("avLt_HI")
            hidemand = self.vary_demand_stochastically(hidemand, self.hi_var / 100.0)
            hihot = self.hi_hot / 100.0 * hidemand
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

        block_attr.add_attribute("WD_COM", comdemand)  # Commercial demand [kL/day]
        block_attr.add_attribute("WD_HotCOM", comhot)  # Commercial hot Water [kL/day]
        block_attr.add_attribute("WD_Office", orcdemand)  # Office demand [kL/day]
        block_attr.add_attribute("WD_HotOffice", orchot)  # Office hot water [kL/day]
        block_attr.add_attribute("WD_LI", lidemand)  # Light Industry demand [kL/day]
        block_attr.add_attribute("WD_HotLI", lihot)  # Light industry hot water [kL/day]
        block_attr.add_attribute("WD_HI", hidemand)  # Heavy Industry demand [kL/day]
        block_attr.add_attribute("WD_HotHI", hihot)  # Heavy industry hot water [kL/day]
        block_attr.add_attribute("WD_NRes", comdemand + orcdemand + lidemand + hidemand)  # Total non-res [kL/day]
        block_attr.add_attribute("WD_HotNRes", comhot + orchot + lihot + hihot)
        block_attr.add_attribute("WD_NResIrri", irrigation_vol)  # Total non-res irrigation [kL/day]
        block_attr.add_attribute("WW_ComGrey", (comdemand + orcdemand) * com_propGW)
        block_attr.add_attribute("WW_ComBlack", (comdemand + orcdemand) * com_propBW)
        block_attr.add_attribute("WW_IndGrey", (lidemand + hidemand) * ind_propGW)
        block_attr.add_attribute("WW_IndBlack", (lidemand + hidemand) * ind_propBW)

    def public_spaces_wateruse(self, block_attr):
        """Calculates the public open spaces water use, including mainly the irrigation of open spaces and landmark
        areas."""
        print("Entering Public Space Water Use")
        parkspace = block_attr.get_attribute("AGreenOS") * int(self.irrigate_parks)
        landmarkspace = block_attr.get_attribute("MiscAirr") * int(self.irrigate_landmarks)
        refspace = block_attr.get_attribute("REF_av") * int(self.irrigate_reserves)
        block_attr.add_attribute("WD_POSIrri", self.pos_irrigation_vol * 1000 / 365.0 *
                                 (parkspace + landmarkspace + refspace) / 10000.0)  # Total OS irrigation [kL/day]
        return True

    def tally_total_block_wateruse(self, block_attr):
        """Scans the water demand attributes and calculates total demands for various sub-categories. Includes losses"""
        print("Getting total water use.")
        total_blk_indoor = block_attr.get_attribute("WD_Indoor") + block_attr.get_attribute("WD_NRes")
        total_irrigation = block_attr.get_attribute("WD_Outdoor") + block_attr.get_attribute("WD_NResIrri") + \
                           block_attr.get_attribute("WD_POSIrri")
        total_blk_hotwater = block_attr.get_attribute("WD_HotVol") + block_attr.get_attribute("WD_HotNRes")
        total_blk_greywater = block_attr.get_attribute("WW_ResGrey") + block_attr.get_attribute("WW_ComGrey") + \
                              block_attr.get_attribute("WW_IndGrey")
        total_blk_blackwater = block_attr.get_attribute("WW_ResBlack") + block_attr.get_attribute("WW_ComBlack") + \
                               block_attr.get_attribute("WW_IndBlack")
        total_blk_demand = total_blk_indoor + total_irrigation
        total_blk_ww = total_blk_greywater + total_blk_blackwater

        if self.estimate_waterloss:
            total_losses = self.waterloss_volprop / 100.0 * total_blk_demand
        else:
            total_losses = 0.0

        block_attr.add_attribute("Blk_WD", total_blk_demand / 1000.0 * 365.0)  # Total Demand [ML/year]
        block_attr.add_attribute("Blk_WDIrri", total_irrigation / 1000.0 * 365.0)  # Total Irrigation [ML/year]
        block_attr.add_attribute("Blk_WDHot", total_blk_hotwater / 1000.0 * 365.0)  # Total Hot Water [ML/year]
        block_attr.add_attribute("Blk_WW", total_blk_ww / 1000.0 * 365.0)  # Total Block Wastewater [ML/year]
        block_attr.add_attribute("Blk_WWGrey", total_blk_greywater / 1000.0 * 365.0)  # Total greywater [ML/year]
        block_attr.add_attribute("Blk_WWBlack", total_blk_blackwater / 1000.0 * 365.0)  # Total blackwater [ML/year]
        block_attr.add_attribute("Blk_Losses", total_losses / 1000.0 * 365.0)  # Total system losses [ML/year]
        return True

    def vary_demand_stochastically(self, basedemand, varyfactor):
        """Uses a uniform distribution to alter a base demand value by a variation factor [ ] either incrementally
        or decrementally. Returns the varied demand value."""
        if varyfactor == 0 or basedemand == 0:  # If either are zero, don't even try! You'll risk infinite loop!
            return basedemand
        variedDemand = -1
        while variedDemand <= 0:
            variedDemand = basedemand + random.uniform(basedemand * varyfactor * (-1), basedemand * varyfactor)
        return variedDemand

    def retrieve_standards(self, st_name):
        """Retrieves the water flow rates for the respective appliance standard."""
        if st_name == "Others...":
            return {"Name": "Others...", "RatingCats": ["none"]}

        standard_dict = dict()
        standard_dict["Name"] = st_name
        standard_dict["Shower"] = []
        standard_dict["Kitchen"] = []
        standard_dict["Toilet"] = []
        standard_dict["Laundry"] = []
        standard_dict["Dishwasher"] = []
        standard_dict["RatingCats"] = []

        rootpath = self.activesim.get_program_rootpath()  # Get the program's root path
        f = open(rootpath + "/ancillary/appliances/" + st_name + ".cfg", 'r')
        data = []
        for lines in f:
            data.append(lines.rstrip("\n").split(","))
        f.close()
        for i in range(len(data)):  # Scan all data and create the dictionary
            if i == 0:  # Skip the header line
                continue
            if data[i][2] not in standard_dict["RatingCats"]:
                standard_dict["RatingCats"].append(data[i][2])
            standard_dict[data[i][1]].append(float(data[i][3]) * 0.5 + float(data[i][4]) * 0.5)
        return standard_dict

    def get_wateruse_custompattern(self, key):
        """Retrieves the _cp custom pattern vector from the given key."""
        return eval("self." + str(key) + "_cp")

    def set_wateruse_custompattern(self, key, patternvector):
        """Sets the current custom pattern _cp of the parameter with the given key to the new patternvector."""
        exec("self." + str(key) + "_cp = " + str(patternvector))

    def create_day_time_series(self, demandcomponents):
        """Creates a 24-hour time series for the given demand components, returns a single aggregate time series
        object.

        :param demandcomponents: a list of all demand components to use in the time series creation
        :return: UBTimeSeries() object
        """
        pass  # [TO DO]

    def create_weekly_time_series(self, demandcomponents):
        pass  # [TO DO]

    def create_annual_time_series(self, demandcomponents):
        pass  # [TO DO]

    def get_peak_daily_demand(self, tseries, units):
        """Returns the peak flow rate for a given time series 'tseries' in the given units.

        :param tseries: the input time-series, a UBTimeSeries() object
        :param units: "L", "m3" or "L/sec" or "m3/sec"
        :return: single value in the corresponding units from the given time series
        """
        pass  # [TO DO]

# WATER-RELATED ELEMENTS
RESSTANDARDS = ["AS6400", "Others..."]
FFP = ["PO", "NP", "RW", "SW", "GW"]    # Fit for purpose water qualities
DPS = ["SDD", "CDP", "OHT", "AHC", "USER"]    # Types of diurnal patterns

# Diurnal Patterns
# SDD = STANDARD DAILY DIURNAL PATTERN SCALING FACTORS
SDD = [0.3, 0.3, 0.3, 0.3, 0.5, 1.0, 1.5, 1.5, 1.3, 1.0, 1.0, 1.5, 1.5, 1.2, 1.0, 1.0, 1.0, 1.3, 1.3, 0.8,
       0.8, 0.5, 0.5, 0.5]

# CDP = CONSTANT DAILY DIURNAL PATTERN SCALING FACTORS
CDP = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
       1.0, 1.0, 1.0, 1.0]

# OHT = OFFICE HOURS TRAPEZOIDAL DIURNAL PATTERN SCALING FACTORS
OHT = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.0, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5,
       0.0, 0.0, 0.0, 0.0]

# AHC = AFTER HOURS CONSTANT DIURNAL PATTERN
AHC = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
       2.0, 2.0, 2.0, 2.0]

DIURNAL_CATS = ["res_kitchen", "res_shower", "res_toilet", "res_laundry", "res_dishwasher", "res_outdoor",
                "res_dailyindoor", "com", "ind", "nonres_landscape", "pos_irrigation"]

DIURNAL_LABELS = ["Kitchen", "Shower", "Toilet", "Laundry", "Dishwasher", "Garden",
                  "Residential Indoor", "Commercial and Offices", "Industries", "Non-residential Outdoor",
                  "Public Irrigation"]
