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
        self.create_parameter("wet", BOOL, "Use constructed wetlands")
        self.create_parameter("roof", BOOL, "Use green roofs?")
        self.create_parameter("wall", BOOL, "Use green walls")
        self.create_parameter("infil", BOOL, "Use infiltration systems")
        self.create_parameter("pb", BOOL, "Use Ponds and Basins")
        self.create_parameter("pp", BOOL, "Use porous pavements")
        self.create_parameter("tank", BOOL, "Use tank system")
        self.create_parameter("retb", BOOL, "Use retarding basin")
        self.create_parameter("sw", BOOL, "Use swales")
        self.bf = 1
        self.wet = 1
        self.roof = 0
        self.wall = 0
        self.infil = 1
        self.pb = 1
        self.pp = 0
        self.tank = 1
        self.rbf = 0
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

        # Stormwater Harvesting Settings
        self.create_parameter("rec_method", STRING, "Stormwater harvesting storage sizing method")
        self.create_parameter("rec_raindata", STRING, "Rain data fileID in data library")
        self.create_parameter("rec_petdata", STRING, "PET data fileID in data library")
        self.create_parameter("rec_rainlength", DOUBLE, "Length of rainfall to use")
        self.create_parameter("rec_demmin", DOUBLE, "Minimum allowable demand range of total inflow")
        self.create_parameter("rec_demmax", DOUBLE, "Maximum allowable demand range of total inflow")
        self.create_parameter("rec_strategy", STRING, "Spatial stormwater harvesting strategy")
        self.create_parameter("rec_swhbenefits", BOOL, "Account for benefits of stormwater harvesting on Qty/WQ?")
        self.create_parameter("rec_unitinflow", DOUBLE, "Unit runoff rate [kL/sqm/imparea]")
        self.create_parameter("rec_unitinflowauto", BOOL, "Auto-determine unit runoff rate?")
        self.rec_method = "SB"  # EQ = equation, SB = storage behaviour modelling
        self.rec_raindata = ""
        self.rec_petdata = ""
        self.rec_rainlength = 1
        self.rec_demmin = 10.0
        self.rec_demmax = 100.0
        self.rec_strategy = "A"    # D = downstream, U = upstream, A = all
        self.rec_swhbenefits = 0
        self.rec_unitinflow = 0.545
        self.rec_unitinflowauto = 0

        # Planning Overlays
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

        self.create_parameter("bf_method", STRING, "Method for sizing biofilter system")
        self.bf_method = "CAPTURE"   # or CURVE

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
        self.bf_dccustomfile = "(load design curve)"

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

        # --- CONSTRUCTED WETLANDS --- Abbreviation WET
        self.create_parameter("wet_street", BOOL, "Wetland on street/neighbourhood scale")
        self.create_parameter("wet_region", BOOL, "Wetland at catchment scale")
        self.create_parameter("wet_flow", BOOL, "Wetland for runoff reduction")
        self.create_parameter("wet_wq", BOOL, "Wetland for water quality")
        self.create_parameter("wet_rec", BOOL, "Wetland for recycling and stormwater harvesting")
        self.wet_street = 1
        self.wet_region = 1
        self.wet_flow = 1
        self.wet_wq = 1
        self.wet_rec = 1

        self.create_parameter("wet_permissions", LIST, "A map of possible and not possible locations")
        self.wet_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1}

        self.create_parameter("wet_method", STRING, "Method for sizing wetland system")
        self.wet_method = "CAPTURE"  # or CURVE

        # Capture ratio method
        self.create_parameter("wet_univcapt", BOOL, "Use a universal capture ratio?")
        self.create_parameter("wet_flow_surfAratio", DOUBLE, "Surface area ratio for runoff/universal")
        self.create_parameter("wet_flow_ratiodef", STRING, "Of contributing area (ALL) of imperivous area (IMP)")
        self.create_parameter("wet_wq_surfAratio", DOUBLE, "Surface area ratio for water quality")
        self.create_parameter("wet_wq_ratiodef", STRING, "Of contributing area (ALL) or impervious area (IMP)")
        self.wet_univcapt = 1
        self.wet_flow_surfAratio = 2.0
        self.wet_flow_ratiodef = "ALL"  # or IMP
        self.wet_wq_surfAratio = 2.0
        self.wet_wq_ratiodef = "ALL"  # or IMP

        # Design curve method
        self.create_parameter("wet_dcurvemethod", STRING, "Design Curve method - custom or default database")
        self.create_parameter("wet_dccustombox", STRING, "Path to the file containing the design curve info")
        self.wet_dcurvemethod = "UBEATS"  # or "CUSTOM"
        self.wet_dccustomfile = "(load design curve)"

        # BF System characteristics
        self.create_parameter("wet_spec", DOUBLE, "Extended detention depth")
        self.create_parameter("wet_minsize", DOUBLE, "Minimum allowable surface area [m2]")
        self.create_parameter("wet_maxsize", DOUBLE, "Maximum allowable surface area [m2]")
        self.create_parameter("wet_exfil", DOUBLE, "Exfiltration rate [mm/hr]")
        self.wet_spec = 1       # Has a spec cheat sheet (0.25 - 0.75 X 72hr or 48hr) in that order
        self.wet_minsize = 0.0
        self.wet_maxsize = 9999999.0
        self.wet_exfil = 0.0

        # BF Life Cycle Characteristics
        self.create_parameter("wet_avglife", DOUBLE, "Avg. System Life")
        self.create_parameter("wet_renewcycle", DOUBLE, "Avg. Renewal Cycle")
        self.wet_avglife = 50
        self.wet_renewcycle = 25

        self.create_parameter("wet_costmethod", STRING, "Cost estimation method for biofilter")
        self.create_parameter("wet_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("wet_tam", DOUBLE, "Total Maintenance Cost")
        self.create_parameter("wet_new", DOUBLE, "Total Renewal Cost")
        self.create_parameter("wet_decom", DOUBLE, "Total Decommissioning Cost")
        self.create_parameter("wet_tam_pct", DOUBLE, "Total Maintenance Cost as % of TAC")
        self.create_parameter("wet_new_pct", DOUBLE, "Total Renewal Cost as % of TAC")
        self.create_parameter("wet_decom_pct", DOUBLE, "Total Decommissioning Cost as % of TAC")
        self.wet_costmethod = "DETAIL"  # or INDIC
        self.wet_tac = 100.0  # per [m2]
        self.wet_tam = 20.0  # per [m2]
        self.wet_new = 80.0  # per [m2]
        self.wet_decom = 90.0  # per [m2]
        self.wet_tam_pct = 20.0  # per [m2]
        self.wet_new_pct = 80.0  # per [m2]
        self.wet_decom_pct = 90.0  # per [m2]

        # --- GREEN ROOF SYSTEMS --- Abbreviation ROOF
        # [TO DO] COMING SOON

        # --- GREEN WALLS / LIVING WALLS --- Abbreviation WALL
        # [TO DO] COMING SOON

        # --- INFILTRATION SYSTEMS ---- Abbreviation INFIL
        self.create_parameter("infil_lot", BOOL, "Infiltration system on lot scale")
        self.create_parameter("infil_street", BOOL, "Infiltration system on street scale")
        self.create_parameter("infil_region", BOOL, "Infiltration system at catchment scale")
        self.create_parameter("infil_flow", BOOL, "Infiltration system for runoff reduction")
        self.create_parameter("infil_wq", BOOL, "Infiltration system for water quality")
        self.create_parameter("infil_rec", BOOL, "Infiltration system for recycling and stormwater harvesting")
        self.infil_lot = 1
        self.infil_street = 1
        self.infil_region = 1
        self.infil_flow = 1
        self.infil_wq = 1
        self.infil_rec = 1

        self.create_parameter("infil_permissions", LIST, "A map of possible and not psosible locations")
        self.infil_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 1, "garden": 1}

        self.create_parameter("infil_method", STRING, "Method for sizing Infiltration system system")
        self.infil_method = "CAPTURE"  # or CURVE

        # Capture ratio method
        self.create_parameter("infil_univcapt", BOOL, "Use a universal capture ratio?")
        self.create_parameter("infil_flow_surfAratio", DOUBLE, "Surface area ratio for runoff/universal")
        self.create_parameter("infil_flow_ratiodef", STRING, "Of contributing area (ALL) of imperivous area (IMP)")
        self.create_parameter("infil_wq_surfAratio", DOUBLE, "Surface area ratio for water quality")
        self.create_parameter("infil_wq_ratiodef", STRING, "Of contributing area (ALL) or impervious area (IMP)")
        self.infil_univcapt = 1
        self.infil_flow_surfAratio = 2.0
        self.infil_flow_ratiodef = "ALL"  # or IMP
        self.infil_wq_surfAratio = 2.0
        self.infil_wq_ratiodef = "ALL"  # or IMP

        # Design curve method
        self.create_parameter("infil_dcurvemethod", STRING, "Design Curve method - custom or default database")
        self.create_parameter("infil_dccustombox", STRING, "Path to the file containing the design curve info")
        self.infil_dcurvemethod = "UBEATS"  # or "CUSTOM"
        self.infil_dccustomfile = "(load design curve)"

        # INFIL System characteristics
        self.create_parameter("infil_ed", DOUBLE, "Extended detention depth")
        self.create_parameter("infil_fd", DOUBLE, "Filter depth")
        self.create_parameter("infil_minsize", DOUBLE, "Minimum allowable surface area [m2]")
        self.create_parameter("infil_maxsize", DOUBLE, "Maximum allowable surface area [m2]")
        self.create_parameter("infil_exfil", DOUBLE, "Exfiltration rate [mm/hr]")
        self.infil_ed = 200.0
        self.infil_fd = 400.0
        self.infil_minsize = 0.0
        self.infil_maxsize = 9999999.0
        self.infil_exfil = 3.6

        # INFIL Life Cycle Characteristics
        self.create_parameter("infil_avglife", DOUBLE, "Avg. System Life")
        self.create_parameter("infil_renewcycle", DOUBLE, "Avg. Renewal Cycle")
        self.infil_avglife = 25
        self.infil_renewcycle = 10

        self.create_parameter("infil_costmethod", STRING, "Cost estimation method for Infiltration system")
        self.create_parameter("infil_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("infil_tam", DOUBLE, "Total Maintenance Cost")
        self.create_parameter("infil_new", DOUBLE, "Total Renewal Cost")
        self.create_parameter("infil_decom", DOUBLE, "Total Decommissioning Cost")
        self.create_parameter("infil_tam_pct", DOUBLE, "Total Maintenance Cost as % of TAC")
        self.create_parameter("infil_new_pct", DOUBLE, "Total Renewal Cost as % of TAC")
        self.create_parameter("infil_decom_pct", DOUBLE, "Total Decommissioning Cost as % of TAC")
        self.infil_costmethod = "DETAIL"  # or INDIC
        self.infil_tac = 100.0  # per [m2]
        self.infil_tam = 20.0  # per [m2]
        self.infil_new = 80.0  # per [m2]
        self.infil_decom = 90.0  # per [m2]
        self.infil_tam_pct = 20.0  # per [m2]
        self.infil_new_pct = 80.0  # per [m2]
        self.infil_decom_pct = 90.0  # per [m2]

        # --- PONDS AND SEDIMENTATION BASINS --- Abbreviation PB
        self.create_parameter("pb_lot", BOOL, "Ponds on lot scale")
        self.create_parameter("pb_street", BOOL, "Ponds on street scale")
        self.create_parameter("pb_region", BOOL, "Ponds at catchment scale")
        self.create_parameter("pb_flow", BOOL, "Ponds for runoff reduction")
        self.create_parameter("pb_wq", BOOL, "Ponds for water quality")
        self.create_parameter("pb_rec", BOOL, "Ponds for recycling and stormwater harvesting")
        self.pb_lot = 1
        self.pb_street = 1
        self.pb_region = 1
        self.pb_flow = 1
        self.pb_wq = 1
        self.pb_rec = 1

        self.create_parameter("pb_permissions", LIST, "A map of possible and not psosible locations")
        self.pb_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 1, "garden": 1}

        self.create_parameter("pb_method", STRING, "Method for sizing Ponds system")
        self.pb_method = "CAPTURE"  # or CURVE

        # Capture ratio method
        self.create_parameter("pb_univcapt", BOOL, "Use a universal capture ratio?")
        self.create_parameter("pb_flow_surfAratio", DOUBLE, "Surface area ratio for runoff/universal")
        self.create_parameter("pb_flow_ratiodef", STRING, "Of contributing area (ALL) of imperivous area (IMP)")
        self.create_parameter("pb_wq_surfAratio", DOUBLE, "Surface area ratio for water quality")
        self.create_parameter("pb_wq_ratiodef", STRING, "Of contributing area (ALL) or impervious area (IMP)")
        self.pb_univcapt = 1
        self.pb_flow_surfAratio = 2.0
        self.pb_flow_ratiodef = "ALL"  # or IMP
        self.pb_wq_surfAratio = 2.0
        self.pb_wq_ratiodef = "ALL"  # or IMP

        # Design curve method
        self.create_parameter("pb_dcurvemethod", STRING, "Design Curve method - custom or default database")
        self.create_parameter("pb_dccustombox", STRING, "Path to the file containing the design curve info")
        self.pb_dcurvemethod = "UBEATS"  # or "CUSTOM"
        self.pb_dccustomfile = "(load design curve)"

        # PB System characteristics
        self.create_parameter("pb_spec", DOUBLE, "Specification index")
        self.create_parameter("pb_minsize", DOUBLE, "Minimum allowable surface area [m2]")
        self.create_parameter("pb_maxsize", DOUBLE, "Maximum allowable surface area [m2]")
        self.create_parameter("pb_exfil", DOUBLE, "Exfiltration rate [mm/hr]")
        self.pb_spec = 1
        self.pb_minsize = 0.0
        self.pb_maxsize = 9999999.0
        self.pb_exfil = 3.6

        # PB Life Cycle Characteristics
        self.create_parameter("pb_avglife", DOUBLE, "Avg. System Life")
        self.create_parameter("pb_renewcycle", DOUBLE, "Avg. Renewal Cycle")
        self.pb_avglife = 25
        self.pb_renewcycle = 10

        self.create_parameter("pb_costmethod", STRING, "Cost estimation method for Ponds")
        self.create_parameter("pb_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("pb_tam", DOUBLE, "Total Maintenance Cost")
        self.create_parameter("pb_new", DOUBLE, "Total Renewal Cost")
        self.create_parameter("pb_decom", DOUBLE, "Total Decommissioning Cost")
        self.create_parameter("pb_tam_pct", DOUBLE, "Total Maintenance Cost as % of TAC")
        self.create_parameter("pb_new_pct", DOUBLE, "Total Renewal Cost as % of TAC")
        self.create_parameter("pb_decom_pct", DOUBLE, "Total Decommissioning Cost as % of TAC")
        self.pb_costmethod = "DETAIL"  # or INDIC
        self.pb_tac = 100.0  # per [m2]
        self.pb_tam = 20.0  # per [m2]
        self.pb_new = 80.0  # per [m2]
        self.pb_decom = 90.0  # per [m2]
        self.pb_tam_pct = 20.0  # per [m2]
        self.pb_new_pct = 80.0  # per [m2]
        self.pb_decom_pct = 90.0  # per [m2]

        # --- POROUS/PERVIOUS PAVEMENTS --- Abbreviation PP
        # [TO DO] COMING SOON

        # --- RAINWATER / STORMWATER TANKS --- Abbreviation TANK
        self.create_parameter("tank_lot", BOOL, "Ponds on lot scale")
        self.create_parameter("tank_street", BOOL, "Ponds on street scale")
        self.create_parameter("tank_region", BOOL, "Ponds at catchment scale")
        self.create_parameter("tank_flow", BOOL, "Ponds for runoff reduction")
        self.create_parameter("tank_wq", BOOL, "Ponds for water quality")
        self.create_parameter("tank_rec", BOOL, "Ponds for recycling and stormwater harvesting")
        self.tank_lot = 1
        self.tank_street = 1
        self.tank_region = 1
        self.tank_flow = 0
        self.tank_wq = 0
        self.tank_rec = 1

        self.create_parameter("tank_permissions", LIST, "A map of possible and not psosible locations")
        self.tank_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "garden": 1}

        self.create_parameter("tank_method", STRING, "Method for sizing Ponds system")
        self.tank_method = "CAPTURE"  # or CURVE

        # Capture ratio method
        self.create_parameter("tank_univcapt", BOOL, "Use a universal capture ratio?")
        self.create_parameter("tank_flow_surfAratio", DOUBLE, "Surface area ratio for runoff/universal")
        self.create_parameter("tank_flow_ratiodef", STRING, "Of contributing area (ALL) of imperivous area (IMP)")
        self.create_parameter("tank_wq_surfAratio", DOUBLE, "Surface area ratio for water quality")
        self.create_parameter("tank_wq_ratiodef", STRING, "Of contributing area (ALL) or impervious area (IMP)")
        self.tank_univcapt = 1
        self.tank_flow_surfAratio = 2.0
        self.tank_flow_ratiodef = "ALL"  # or IMP
        self.tank_wq_surfAratio = 2.0
        self.tank_wq_ratiodef = "ALL"  # or IMP

        # Design curve method
        self.create_parameter("tank_dcurvemethod", STRING, "Design Curve method - custom or default database")
        self.create_parameter("tank_dccustombox", STRING, "Path to the file containing the design curve info")
        self.tank_dcurvemethod = "UBEATS"  # or "CUSTOM"
        self.tank_dccustomfile = "(load design curve)"

        # PB System characteristics
        self.create_parameter("tank_maxdepth", DOUBLE, "Maximum Tank Depth [m]")
        self.create_parameter("tank_mindead", DOUBLE, "Minimum Tank Dead Storage Level [m]")
        self.tank_maxdepth = 2
        self.tank_mindead = 0.2

        # PB Life Cycle Characteristics
        self.create_parameter("tank_avglife", DOUBLE, "Avg. System Life")
        self.create_parameter("tank_renewcycle", DOUBLE, "Avg. Renewal Cycle")
        self.tank_avglife = 25
        self.tank_renewcycle = 10

        self.create_parameter("tank_costmethod", STRING, "Cost estimation method for Ponds")
        self.create_parameter("tank_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("tank_tam", DOUBLE, "Total Maintenance Cost")
        self.create_parameter("tank_new", DOUBLE, "Total Renewal Cost")
        self.create_parameter("tank_decom", DOUBLE, "Total Decommissioning Cost")
        self.create_parameter("tank_tam_pct", DOUBLE, "Total Maintenance Cost as % of TAC")
        self.create_parameter("tank_new_pct", DOUBLE, "Total Renewal Cost as % of TAC")
        self.create_parameter("tank_decom_pct", DOUBLE, "Total Decommissioning Cost as % of TAC")
        self.tank_costmethod = "DETAIL"  # or INDIC
        self.tank_tac = 100.0  # per [m2]
        self.tank_tam = 20.0  # per [m2]
        self.tank_new = 80.0  # per [m2]
        self.tank_decom = 90.0  # per [m2]
        self.tank_tam_pct = 20.0  # per [m2]
        self.tank_new_pct = 80.0  # per [m2]
        self.tank_decom_pct = 90.0  # per [m2]

        # --- RETARDING BASINS / FLOODPLAINS --- Abbreviation RETB
        # [TO DO] COMING SOON

        # --- SWALES --- Abbreviation SW
        self.create_parameter("sw_street", BOOL, "Biofilter on street scale")
        self.create_parameter("sw_region", BOOL, "Biofilter at catchment scale")
        self.create_parameter("sw_flow", BOOL, "Biofilter for runoff reduction")
        self.create_parameter("sw_wq", BOOL, "Biofilter for water quality")
        self.sw_street = 1
        self.sw_region = 1
        self.sw_flow = 1
        self.sw_wq = 1

        self.create_parameter("sw_permissions", LIST, "A map of possible and not psosible locations")
        self.sw_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 1}

        self.create_parameter("sw_method", STRING, "Method for sizing biofilter system")
        self.sw_method = "CAPTURE"  # or CURVE

        # Capture ratio method
        self.create_parameter("sw_univcapt", BOOL, "Use a universal capture ratio?")
        self.create_parameter("sw_flow_surfAratio", DOUBLE, "Surface area ratio for runoff/universal")
        self.create_parameter("sw_flow_ratiodef", STRING, "Of contributing area (ALL) of imperivous area (IMP)")
        self.create_parameter("sw_wq_surfAratio", DOUBLE, "Surface area ratio for water quality")
        self.create_parameter("sw_wq_ratiodef", STRING, "Of contributing area (ALL) or impervious area (IMP)")
        self.sw_univcapt = 1
        self.sw_flow_surfAratio = 2.0
        self.sw_flow_ratiodef = "ALL"  # or IMP
        self.sw_wq_surfAratio = 2.0
        self.sw_wq_ratiodef = "ALL"  # or IMP

        # Design curve method
        self.create_parameter("sw_dcurvemethod", STRING, "Design Curve method - custom or default database")
        self.create_parameter("sw_dccustombox", STRING, "Path to the file containing the design curve info")
        self.sw_dcurvemethod = "UBEATS"  # or "CUSTOM"
        self.sw_dccustomfile = "(load design curve)"

        # BF System characteristics
        self.create_parameter("sw_spec", DOUBLE, "Specification for design")
        self.create_parameter("sw_minsize", DOUBLE, "Minimum allowable surface area [m2]")
        self.create_parameter("sw_maxsize", DOUBLE, "Maximum allowable surface area [m2]")
        self.create_parameter("sw_maxlength", DOUBLE, "Maximum allowable length [m]")
        self.create_parameter("sw_exfil", DOUBLE, "Exfiltration rate [mm/hr]")
        self.sw_spec = 0
        self.sw_minsize = 0.0
        self.sw_maxsize = 9999999.0
        self.sw_maxlength = 500
        self.sw_exfil = 0.0

        # BF Life Cycle Characteristics
        self.create_parameter("sw_avglife", DOUBLE, "Avg. System Life")
        self.create_parameter("sw_renewcycle", DOUBLE, "Avg. Renewal Cycle")
        self.sw_avglife = 50
        self.sw_renewcycle = 25

        self.create_parameter("sw_costmethod", STRING, "Cost estimation method for biofilter")
        self.create_parameter("sw_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("sw_tam", DOUBLE, "Total Maintenance Cost")
        self.create_parameter("sw_new", DOUBLE, "Total Renewal Cost")
        self.create_parameter("sw_decom", DOUBLE, "Total Decommissioning Cost")
        self.create_parameter("sw_tam_pct", DOUBLE, "Total Maintenance Cost as % of TAC")
        self.create_parameter("sw_new_pct", DOUBLE, "Total Renewal Cost as % of TAC")
        self.create_parameter("sw_decom_pct", DOUBLE, "Total Decommissioning Cost as % of TAC")
        self.sw_costmethod = "DETAIL"  # or INDIC
        self.sw_tac = 100.0  # per [m2]
        self.sw_tam = 20.0  # per [m2]
        self.sw_new = 80.0  # per [m2]
        self.sw_decom = 90.0  # per [m2]
        self.sw_tam_pct = 20.0  # per [m2]
        self.sw_new_pct = 80.0  # per [m2]
        self.sw_decom_pct = 90.0  # per [m2]

        # ADVANCED PARAMETERS DEFINITION
        self.userTech = {}
        self.technames = ["BF", "WET", "ROOF", "WALL", "INFIL", "PB", "PP", "TANK", "RBF", "SW"]
        self.scalenames = ["lot", "street", "region"]


    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")

        # METADATA CHECK - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
        self.meta.add_attribute("mod_mapregions", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        # PRE-REQUISITES CHECK - need to have a few modules run
        if self.meta.get_attribute("mod_urbanformgen") != 1:
            self.notify("Cannot start module! Data on Urban Form is missing! Please generate urban form first")
            return False
        elif self.meta.get_attribute("mod_waterdemand") != 1 and self.rec_obj:
            self.notify("To do stormwater harvesting, water demand needs to be known! Please run this module first!")
            return False

        # CLEAN THE ATTRIBUTES LIST
        att_schema = [

        ]

        grid_assets = self.assets.get_assets_with_identifier(self.assetident)
        att_reset_count = 0
        for i in range(len(grid_assets)):
            for att in att_schema:
                if grid_assets[i].remove_attribute(att):
                    att_reset_count += 1
        self.notify("Removed "+str(att_reset_count)+" attribute entries")
        # Also need to remove the asset collection WSUD [TO DO] Whatever that will look like!

        self.meta.add_attribute("mod_nbsdesigntoolbox", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")
        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")
        return True

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.notify_progress(0)
        if not self.initialize_runstate():
            self.notify("Module run terminated")
            return True

        self.notify("Setting up NbS Design Toolbox")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 0 - GRAB ASSET INFORMATION ---
        self.griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets making up the case study area: "+str(len(self.griditems)))
        total_assets = len(self.griditems)
        progress_counter = 0
        self.notify_progress(10)
        geomtype = self.meta.get_attribute("Geometry")

        # --- SECTION 1 - CALCULATE GLOBAL VARIABLES FOR PLANNING OF NBS RELATED TO TARGETS
        # Get targets for design
        self.system_tarQ = self.runoff_obj * self.runoff_tar
        self.system_tarTSS = self.wq_obj * self.wq_tss_tar
        self.system_tarTN = self.wq_obj * self.wq_tn_tar
        self.system_tarTP = self.wq_obj * self.wq_tp_tar
        self.system_rec = self.rec_obj * self.rec_tar
        self.targetsvector = [self.system_tarQ, self.system_tarTSS, self.system_tarTP,
                              self.system_tarTN, self.system_rec]
        self.notify("Targets to meet Qty, TSS, TP, TN, Rel%: "+str(self.targetsvector))

        # Calculate system depths
        self.sysdepths = {"TANK": self.tank_maxdepth - self.tank_mindead, "WET": self.wet_spec, "PB": self.pb_spec}

        # Create Technologies shortlist
        self.compile_user_techlist()
        self.notify("Using technologies: "+str(self.userTech))
        self.notify_progress(20)

        # --- SECTION 2 - DESIGN AREAS FOR DIFFERENT SURFACE AREA BASED DESIGNS







        self.notify("Toolbox Setup Complete for Simulation Grid")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def compile_user_techlist(self):
        """Compiles a dictionary of the technologies the user should use and at what scales these different techs should
        be used. Results are presented as a dictionary, self.userTech, which is instantiated at the start as {} and
        updated here to reflect the new parameters."""
        self.userTech = {}
        for j in self.technames:
            if eval("self."+j.lower()+" == 1"):
                self.userTech[j] = {}       # Each scale will have a dictionary
                for k in range(len(self.scalenames)):
                    k_scale = self.scalenames[k]
                    try:
                        if eval("self."+str(j.lower())+"_"+str(k_scale)+" == 1"):
                            self.userTech[j][k_scale] = 1       # {"BF": {"lot": 1, "street": 1, "region": 1}, etc.}
                        else:
                            self.userTech[j][k_scale] = 0
                    except NameError:
                        pass
                    except AttributeError:
                        pass
        return True
