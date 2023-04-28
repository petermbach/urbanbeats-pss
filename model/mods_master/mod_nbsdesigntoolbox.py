r"""
@file   mod_nbsdesigntoolbox.py
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

class NbSDesignToolboxSetup(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "NbS Planning and Design"
    catorder = 2
    longname = "Setup NbS Design Toolbox"
    icon = ":/icons/nbs_toolbox.png"

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

        # SIDE MENU CHECKBOXES
        self.create_parameter("bf", BOOL, "Use biofilter?")
        self.create_parameter("wsur", BOOL, "Use constructed wetlands")
        self.create_parameter("roof", BOOL, "Use green roofs?")
        self.create_parameter("wall", BOOL, "Use green walls")
        self.create_parameter("infil", BOOL, "Use infiltration systems")
        self.create_parameter("pb", BOOL, "Use Ponds and Basins")
        self.create_parameter("pp", BOOL, "Use porous pavements")
        self.create_parameter("tank", BOOL, "Use tank system")
        self.create_parameter("retb", BOOL, "Use retarding basin")
        self.create_parameter("sw", BOOL, "Use swales")
        self.bf = 1
        self.wsur = 1
        self.roof = 0
        self.wall = 0
        self.infil = 1
        self.pb = 1
        self.pp = 0
        self.tank = 1
        self.retb = 0
        self.sw = 1

        # MODULE PARAMETERS
        # --- Spatial Planning Options ---
        self.create_parameter("runoff_obj", BOOL, "Runoff reduction objective")
        self.create_parameter("runoff_priority", DOUBLE, "Runoff Priority")
        self.create_parameter("runoff_tar", DOUBLE, "Runfof reduction target")
        self.runoff_obj = 0
        self.runoff_priority = 0    # 0 = High, 1 = Medium, 2 = Low
        self.runoff_tar = 20.0

        self.create_parameter("wq_obj", BOOL, "Pollution load reduction objective")
        self.create_parameter("wq_priority", DOUBLE, "Pollution control priority")
        self.create_parameter("wq_tss_tar", DOUBLE, "Annual TSS load reduction target")
        self.create_parameter("wq_tn_tar", DOUBLE, "Annual TN load reduction target")
        self.create_parameter("wq_tp_tar", DOUBLE, "Annual TP load reduction target")
        self.wq_obj = 0
        self.wq_priority = 0        # 0 = High, 1 = Medium, 2 = Low
        self.wq_tss_tar = 80.0
        self.wq_tn_tar = 45.0
        self.wq_tp_tar = 45.0

        self.create_parameter("rec_obj", BOOL, "Stormwater Harvesting and recycling objective")
        self.create_parameter("rec_priority", DOUBLE, "Stormwater harvesting priority")
        self.create_parameter("rec_tar", DOUBLE, "Volumetric Reliability of stormwater harvesting systems")
        self.rec_obj = 0
        self.rec_priority = 0       # 0 = High, 1 = Medium, 2 = Low
        self.rec_tar = 80.0

        self.create_parameter("consider_overlays", BOOL, "Consider planning overlays as restrictive for BGI")
        self.create_parameter("ovrly_shp", BOOL, "Use an overlay shapefile to restrict areas")
        self.create_parameter("ovrly_suit", BOOL, "Use land use suitability to limit implementation")
        self.create_parameter("allow_pg", BOOL, "Set allowable % of usable space in Parks and Garden Land use")
        self.create_parameter("allow_pg_val", DOUBLE, "Allowable % of parks and garden space for BGI")
        self.create_parameter("prohibit_ref", BOOL, "Allow BGI globally in reserves and floodways?")
        self.create_parameter("prohibit_for", BOOL, "Prohibit BGI globally in forests?")
        self.consider_overlays = 0
        self.ovrly_shp = 0      # [TO DO]
        self.ovrly_suit = 0
        self.allow_pg = 0
        self.allow_pg_val = 100.0
        self.prohibit_ref = 0
        self.prohibit_for = 0

        self.create_parameter("scale_lot", BOOL, "Use BGI at Lot scale?")
        self.create_parameter("scale_street", BOOL, "Use BGI at street/neighbourhood scale?")
        self.create_parameter("scale_region", BOOL, "Use BGI at regional scale?")
        self.create_parameter("lot_rigour", DOUBLE, "Rigour of planning at Lot scale")
        self.create_parameter("street_rigour", DOUBLE, "Rigour of planning at street scale")
        self.create_parameter("basin_rigour", DOUBLE, "Rigour of planning at basin scale?")
        self.scale_lot = 1
        self.scale_street = 1
        self.scale_region = 1
        self.lot_rigour = 4
        self.street_rigour = 4
        self.region_rigour = 4

        # --- Load Existing NbS Assets ---
        # [TO DO] COMING SOON

        # === INDIVIDUAL NATURE BASED SOLUTIONS TECHNOLOGIES FOR PLANNING ==============================================
        # --- BIORERENTION/BIOFILTRATION/RAINGARDENS (Abbr. BF) --------------------------------------------------------
        self.create_parameter("bf_lot", BOOL, "Biofilter on lot scale")
        self.create_parameter("bf_street", BOOL, "Biofilter on street scale")
        self.create_parameter("bf_region", BOOL, "Biofilter at catchment scale")
        self.create_parameter("bf_flow", BOOL, "Biofilter for runoff reduction")
        self.create_parameter("bf_wq", BOOL, "Biofilter for water quality")
        self.create_parameter("bf_rec", BOOL, "Biofilter for recycling and stormwater harvesting")
        self.bf_lot = 1
        self.bf_street = 1
        self.bf_region = 1
        self.bf_flow = 1
        self.bf_wq = 1
        self.bf_rec = 1

        self.create_parameter("bf_permissions", LIST, "A map of possible and not psosible locations")
        self.bf_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 1, "garden": 1}

        self.create_parameter("bfmethod", STRING, "Method for sizing biofilter system")
        self.bfmethod = "CAPTURE"   # or CURVE

        # Capture ratio method
        self.create_parameter("bf_univcapt", BOOL, "Use a universal capture ratio?")
        self.create_parameter("bf_flow_surfAratio", DOUBLE, "Surface area ratio for runoff/universal")
        self.create_parameter("bf_flow_ratiodef", STRING, "Of contributing area (ALL) of imperivous area (IMP)")
        self.create_parameter("bf_wq_surfAratio", DOUBLE, "Surface area ratio for water quality")
        self.create_parameter("bf_wq_ratiodef", STRING, "Of contributing area (ALL) or impervious area (IMP)")
        self.bf_univcapt = 1
        self.bf_flow_surfAratio = 2.0
        self.bf_flow_ratiodef = "ALL"   # or IMP
        self.bf_wq_surfAratio = 2.0
        self.bf_wq_ratiodef = "ALL"     # or IMP

        # Design curve method
        self.create_parameter("bf_dcurvemethod", STRING, "Design Curve method - custom or default database")
        self.create_parameter("bf_dccustombox", STRING, "Path to the file containing the design curve info")
        self.bf_dcurvemethod = "UBEATS"     # or "CUSTOM"
        self.bf_dccustombox = "(load design curve)"

        # BF System characteristics
        self.create_parameter("bf_ed", DOUBLE, "Extended detention depth")
        self.create_parameter("bf_fd", DOUBLE, "Filter depth")
        self.create_parameter("bf_minsize", DOUBLE, "Minimum allowable surface area [m2]")
        self.create_parameter("bf_maxsize", DOUBLE, "Maximum allowable surface area [m2]")
        self.create_parameter("bf_exfil", DOUBLE, "Exfiltration rate [mm/hr]")
        self.bf_ed = 200.0
        self.bf_fd = 400.0
        self.bf_minsize = 0.0
        self.bf_maxsize = 9999999.0
        self.bf_exfil = 0.0

        # BF Life Cycle Characteristics
        self.create_parameter("bf_avglife", DOUBLE, "Avg. System Life")
        self.create_parameter("bf_renewcycle", DOUBLE, "Avg. Renewal Cycle")
        self.bf_avglife = 50
        self.bf_renewcycle = 25

        self.create_parameter("bf_costmethod", STRING, "Cost estimation method for biofilter")
        self.create_parameter("bf_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("bf_tam", DOUBLE, "Total Maintenance Cost")
        self.create_parameter("bf_new", DOUBLE, "Total Renewal Cost")
        self.create_parameter("bf_decom", DOUBLE, "Total Decommissioning Cost")
        self.create_parameter("bf_tam_pct", DOUBLE, "Total Maintenance Cost as % of TAC")
        self.create_parameter("bf_new_pct", DOUBLE, "Total Renewal Cost as % of TAC")
        self.create_parameter("bf_decom_pct", DOUBLE, "Total Decommissioning Cost as % of TAC")
        self.bf_costmethod = "DETAIL"   # or INDIC
        self.bf_tac = 100.0     # per [m2]
        self.bf_tam = 20.0      # per [m2]
        self.bf_new = 80.0      # per [m2]
        self.bf_decom = 90.0    # per [m2]
        self.bf_tam_pct = 20.0  # per [m2]
        self.bf_new_pct = 80.0  # per [m2]
        self.bf_decom_pct = 90.0    # per [m2]
        # ----- END OF BIOFILTER PARAMETERS LIST -----------------------------------------------------------------------

        # --- CONSTRUCTED WETLANDS --- Abbreviation WSUR

        # --- GREEN ROOF SYSTEMS --- Abbreviation ROOF
        # [TO DO] COMING SOON

        # --- GREEN WALLS / LIVING WALLS --- Abbreviation WALL
        # [TO DO] COMING SOON

        # --- INFILTRATION SYSTEMS ---- Abbreviation IF

        # --- PONDS AND SEDIMENTATION BASINS --- Abbreviation PB

        # --- POROUS/PERVIOUS PAVEMENTS --- Abbreviation PP
        # [TO DO] COMING SOON

        # --- RAINWATER / STORMWATER TANKS --- Abbreviation TANK

        # --- RETARDING BASINS / FLOODPLAINS --- Abbreviation RETB
        # [TO DO] COMING SOON

        # --- SWALES --- Abbreviation SW


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

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.notify_progress(0)
        self.initialize_runstate()

        self.notify("Setting up NbS Design Toolbox")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)


        # --- SECTION 1 - (description)
        # --- SECTION 2 - (description)
        # --- SECTION 3 - (description)

        self.notify("Toolbox Setup Complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass