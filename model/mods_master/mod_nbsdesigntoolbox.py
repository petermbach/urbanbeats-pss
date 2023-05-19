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
import numpy as np
import pandas
import pandas as pd
import datetime as dt
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
        self.wq_obj = 1
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
        self.wet_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 0, "garden": 0}

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
        # ADVANCED
        self.wet_sysdepth = [0.25, 0.5, 0.75, 0.25, 0.5, 0.75]
        self.wet_dettime = [72, 72, 72, 48, 48, 48]

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
        # ADVANCED
        self.pb_sysdepth = [0.25, 0.5, 0.75, 1.00, 1.25]

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
        self.tank_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 0, "garden": 1}

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
        self.sw_permissions = {"PG": 1, "REF": 1, "FOR": 1, "AGR": 1, "UND": 1, "nstrip": 1, "garden": 1}

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
        self.system_tarQ = 0        # Final system target Flow
        self.system_tarTSS = 0      # TSS
        self.system_tarTN = 0       # TN
        self.system_tarTP = 0       # TP
        self.system_tarREC = 0      # Recycling/Stormwater harvesting
        self.targetsvector = [0, 0, 0, 0, 0]    # All targets Q, TSS, TN, TP, REC put together
        self.sysdepths = {}     # Initialize system acceptable depths
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
        att_schema = {"LOT_Avail": 0.0, "ST_Avail": 0.0, "REG_Avail": 0.0, "NBS_Divers": 0.0, "NBS_Types": int(0),
                      "NBS_DesLOT": int(0), "NBS_DesST": int(0), "NBS_DesREG": int(0), "NBS_DesTOT": int(0),
                      "NBS_Flex": 0.0, "MaxImpQTY": 0.0, "MaxImpWQ": 0.0, "MaxScale": "", "MaxSysType": "",
                      "MaxADesign": 0.0, "MaxSFact": 0.0}

        grid_assets = self.assets.get_assets_with_identifier(self.assetident)
        att_reset_count = 0
        for i in range(len(grid_assets)):
            for att in att_schema.keys():
                if grid_assets[i].remove_attribute(att):
                    att_reset_count += 1
        self.notify("Removed "+str(att_reset_count)+" attribute entries")
        # Also need to remove the asset collection WSUD [TO DO] Whatever that will look like!

        # INITIALIZE THE ATTRIBUTES LIST
        for i in range(len(grid_assets)):
            for att in att_schema.keys():
                grid_assets[i].add_attribute(att, att_schema[att])

        self.meta.add_attribute("mod_nbsdesigntoolbox", 1)
        self.meta.add_attribute("mod_dt_nbsdesigntoolbox", str(dt.datetime.now().isoformat().split(".")[0]))  # Last run
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
        self.notify_progress(5)
        geomtype = self.meta.get_attribute("Geometry")

        # --- SECTION 1 - CALCULATE GLOBAL VARIABLES FOR PLANNING OF NBS RELATED TO TARGETS
        # Get targets for design
        self.system_tarQ = self.runoff_obj * self.runoff_tar
        self.system_tarTSS = self.wq_obj * self.wq_tss_tar
        self.system_tarTN = self.wq_obj * self.wq_tn_tar
        self.system_tarTP = self.wq_obj * self.wq_tp_tar
        self.system_tarREC = self.rec_obj * self.rec_tar
        self.targetsvector = [self.system_tarQ, self.system_tarTSS, self.system_tarTP,
                              self.system_tarTN, self.system_tarREC]
        self.notify("Targets to meet Qty, TSS, TP, TN, Rel%: "+str(self.targetsvector))

        # Calculate system depths [m]
        self.sysdepths = {"TANK": self.tank_maxdepth - self.tank_mindead,
                          "WET": self.wet_sysdepth[self.wet_spec],
                          "PB": self.pb_sysdepth[self.pb_spec]}

        # Create Technologies shortlist
        self.compile_user_techlist()
        self.notify("Using technologies: "+str(self.userTech))
        self.notify_progress(10)

        # --- SECTION 2a - DESIGN AREAS FOR DIFFERENT SURFACE AREA BASED DESIGNS
        self.notify("Getting system designs")       # Loop across each system type and get the design requirements
        nbsdesignrules = {}     # Containing sizing ratios [%]
        for tech in self.userTech.keys():       # e.g. BF
            if tech in ["TANK"]:
                continue    # Skip raintank systems
            if eval("self."+tech.lower()+"_method") == "CAPTURE":     # Capture ratio method
                if eval("self."+tech.lower()+"_univcapt"):      # Universal capture method?
                    nbsdesignrules[tech] = [eval("self."+tech.lower()+"_flow_surfAratio") *
                                            eval("self."+tech.lower()+"_flow") * self.runoff_obj,
                                            eval("self."+tech.lower()+"_flow_ratiodef"),
                                            eval("self."+tech.lower()+"_flow_surfAratio") *
                                            eval("self."+tech.lower()+"_wq") * self.wq_obj,
                                            eval("self."+tech.lower()+"_flow_ratiodef")]
                else:
                    nbsdesignrules[tech] = [eval("self."+tech.lower()+"_flow_surfAratio") *
                                            eval("self."+tech.lower()+"_flow") * self.runoff_obj,
                                            eval("self."+tech.lower()+"_flow_ratiodef"),
                                            eval("self."+tech.lower()+"_wq_surfAratio") *
                                            eval("self."+tech.lower()+"_wq") * self.wq_obj,
                                            eval("self."+tech.lower()+"_wq_ratiodef")]
            else:   # METHOD IS DESIGN CURVE
                pass    # [TO DO] DESIGN CURVE METHOD
                # if self.bf_curvemethod == "UBEATS":      # Design curve method
                #     design_data = self.get_design_curve_data("BF")
                # else:
                #     design_data = self.read_custom_dcv()
                #     # Load deisgn curve
                #     # Read data from it
                # nbsdesignrules["BF"] = design_data
        self.notify(nbsdesignrules)

        # --- SECTION 2b - Load and prepare climate data for storage-behaviour model
        if self.rec_obj:
            pass    # [ TO DO ]
            # Initialize meteorological data vectors: load rainfall and evaporation files, create scaling factors for
            # PET data.
            self.notify("Loading climate")
            self.load_rescale_climate_data()

        # --- SECTION 3 - Loop through simulation assets and determine locations for suitable NbS Tech ---
        # Define design increments - this is where we now start working with numpy arrays and pandas dataframes
        lot_incr = np.linspace(0, 1, int(self.lot_rigour) + 1)
        street_incr = np.linspace(0, 1, int(self.street_rigour) + 1)
        region_incr = np.linspace(0, 1, int(self.region_rigour) + 1)

        # Get the technologies used at each scale
        lot_tech = [key for key in self.userTech.keys() if self.userTech[key]["lot"]]
        street_tech = [key for key in self.userTech.keys() if self.userTech[key]["street"]]
        region_tech = [key for key in self.userTech.keys() if self.userTech[key]["region"]]
        self.notify("Lot-scale Technologies List: "+str(lot_tech)+" at increments of "+str(lot_incr))
        self.notify("Street-scale Technologies List: "+str(street_tech)+" at increments of "+str(street_incr))
        self.notify("Regional-scale Technologies List: "+str(region_tech)+" at increments of "+str(region_incr))
        self.notify_progress(20)

        # Initialize the Pandas Data Frame of all options for the case study
        self.notify("Now assessing NbS Opportunities across the simulation grid")
        nbsdatabase = []
        for i in range(len(self.griditems)):
            # PROGRESS NOTIFIER
            progress_counter += 1
            if progress_counter > total_assets / 4:
                self.notify_progress(40)
            elif progress_counter > total_assets / 2:
                self.notify_progress(60)
            elif progress_counter > total_assets / 4 * 3:
                self.notify_progress(80)


            curasset = self.griditems[i]
            if curasset.get_attribute("Status") == 0:
                continue

            curID = curasset.get_attribute(self.assetident)
            self.notify("Currently assessing "+str(self.assetident)+str(curID))

            # --- (a) Assess Lot Opportunities
            # for land uses: RES, HDR, LI, HI, COM
            if self.scale_lot and len(lot_tech) != 0:   # Then do lot-scale tech
                lot_options = self.assess_lot_opportunities(lot_tech, lot_incr, curasset, curID, nbsdesignrules)
                for opt in range(len(lot_options)):
                    nbsdatabase.append(lot_options[opt])

            # --- (b) Assess Street/Neighbourhood Opportunities
            # to be put in street-sides or in parklands
            if self.scale_street and len(street_tech) != 0:     # Then do street
                st_options = self.assess_street_opportunities(street_tech, street_incr, curasset, curID, nbsdesignrules)
                for opt in range(len(st_options)):
                    nbsdatabase.append(st_options[opt])

            # --- (c) Assess Regional Opportunities
            # to be used in parklands generally across multiple drainage units
            if self.scale_region and len(region_tech) != 0:     # Then do region
                re_options = self.assess_region_opportunities(region_tech, region_incr, curasset, curID, nbsdesignrules)
                for opt in range(len(re_options)):
                    nbsdatabase.append(re_options[opt])

        # --- SECTION 4 - Consolidation the NbS Database and clean-up
        self.notify("Total number of NbS designs generated: "+str(len(nbsdatabase)))
        self.notify("Consolidating design information to simulation grid")

        # Instantiate Pandas Database
        df = pandas.DataFrame(data=nbsdatabase)

        # Write performance indicators
        # (0) Total available space for NbS
        # KPIs:
        for i in range(len(self.griditems)):
            curasset = self.griditems[i]

            # (1) System diversity - total number and types of different possible NbS solutions
            designs = df[df["AssetID"] == curasset.get_attribute(self.assetident)]  # All designs for this current ID
            if designs.shape[0] == 0:
                continue    # Skip, all values will be zero anyway based on default setup

            assettypenum = len(designs["SysType"].value_counts())
            assettypenames = designs["SysType"].value_counts().index.to_list()
            assettypenames.sort()

            curasset.add_attribute("NBS_Divers", assettypenum)
            curasset.add_attribute("NBS_Types", assettypenames)

            # (2) System flexibility - total number of designs made, possible designs weighted to the increment
            totalnumdesigns = designs.shape[0]
            lotdesigns = designs[designs["Scale"].str.contains("L_")]
            lotluctypes = len(lotdesigns.value_counts().index.to_list())
            if lotluctypes == 0:
                lotflex = 0
            else:
                lotflex = float(lotdesigns.shape[0])/float(len(lotdesigns.value_counts().index.to_list()))/self.lot_rigour
            streetdesigns = designs[designs["Scale"].str.contains("STREET")]
            streetflex = float(streetdesigns.shape[0])/self.street_rigour
            regdesigns = designs[designs["Scale"].str.contains("REGION")]
            regflex = float(regdesigns.shape[0])/self.region_rigour
            asset_flex = (lotflex + streetflex + regflex)

            curasset.add_attribute("NBS_DesLOT", lotdesigns.shape[0])
            curasset.add_attribute("NBS_DesST", streetdesigns.shape[0])
            curasset.add_attribute("NBS_DesREG", regdesigns.shape[0])
            curasset.add_attribute("NBS_DesTOT", totalnumdesigns)
            curasset.add_attribute("NBS_Flex", asset_flex)

            # (3) Maximum achievable service
            max_serve = designs[designs["WQImpServed"] == designs["WQImpServed"].max()].iloc[0].to_list()

            curasset.add_attribute("MaxImpQTY", max_serve[6])
            curasset.add_attribute("MaxImpWQ", max_serve[7])
            curasset.add_attribute("MaxScale", max_serve[1])
            curasset.add_attribute("MaxSysType", max_serve[2])
            curasset.add_attribute("MaxADesign", max_serve[3])
            curasset.add_attribute("MaxSFact", max_serve[4])

            # - Draw the catchment as a treatment map [Maybe TO DO]

        self.notify("Toolbox Setup Complete for Simulation Grid")
        self.notify_progress(90)
        self.notify("Exporting NbS Database to Projects Folder")
        filepath = self.activesim.get_project_path() + "/collections/"
        fullname = filepath + "/" + str(self.assetcolname) + "_NbS_tbox.udb"
        df.to_pickle(fullname)
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def retrieve_design_curve_data(self, techtype, flow, tss, tn, tp):
        """Goes into the UrbanBEATS custom design curve database to retrieve surface area requirement for flow, tss, tn,
        tp targets specified.
        """
        basepath = self.activesim.get_program_rootpath()+"/ancillary/nbscurves/"
        if techtype in ["BF", "INFIL"]:
            # Then we want extended detention depth and filter depth EDD and FD
            edd = round(self.bf_ed/1000.0, 1)
            fd = round(self.bf_fd/1000.0, 1)
            exfil = self.bf_exfil
            filename = basepath + techtype + "-EDD"+str(edd)+"m-FD"+str(fd)+"m-DC.dcv"
        elif techtype in ["PB"]:
            # Then we want mean depth, e.g. 0.25m Mean Depth, Outflow via Overflow Weir
            pass
        elif techtype in ["WET"]:
            # Then we want extended detention depth and detention time, e.g. 250mm Ext. Detention Depth, 72hr detention
            pass
        else:
            pass

    def assess_lot_opportunities(self, techlist, techincr, curasset, curID, nbsdesignrules):
        """Assess all possible NBS Opportunities at the Lot scale i.e., RES, COM, LI, HI for the current asset
        passed to the function.
        """
        techdesigns = []    # list of tech

        # Step 1 - Check if there are lot-stuff to work with!
        hasHouses = curasset.get_attribute("HasHouses")        # LOW DENSITY RESIDENTIAL LAND USE
        if hasHouses is None:
            hasHouses, num_houses, res_avail_sp, Alot, Aimpres = 0, 0, 0, 0, 0
        else:
            num_allots = curasset.get_attribute("ResAllots")
            res_avail_sp = curasset.get_attribute("avLt_RES")
            Alot = curasset.get_attribute("ResLotArea")
            Aimpres = curasset.get_attribute("ResLotEIA")

        hasFlats = curasset.get_attribute("HasFlats")          # HIGH-DENSITY RESIDENTIAL LAND USE
        if hasFlats is None:
            hasFlats, num_hdr, hdr_avail_sp, Ahdr, Aimphdr = 0,0,0,0,0
        else:
            num_hdr = 1
            hdr_avail_sp = curasset.get_attribute("av_HDRes")
            Ahdr = curasset.get_attribute("HDR_TIA")+curasset.get_attribute("HDRGarden")
            Aimphdr = curasset.get_attribute("HDR_EIA")

        hasLI = curasset.get_attribute("Has_LI")
        if hasLI is None:
            hasLI, num_estatesLI, li_avail_sp, Ali, Aimpli = 0, 0, 0, 0, 0
        else:
            num_estatesLI = curasset.get_attribute("LIestates")
            li_avail_sp = curasset.get_attribute("avLt_LI")
            Ali = curasset.get_attribute("LIAestate")
            Aimpli = curasset.get_attribute("LIAeEIA")

        hasHI = curasset.get_attribute("Has_HI")
        if hasHI is None:
            hasHI, numestatesHI, hi_avail_sp, Ahi, Aimphi = 0, 0, 0, 0, 0
        else:
            num_estatesHI = curasset.get_attribute("HIestates")
            hi_avail_sp = curasset.get_attribute("avLt_HI")
            Ahi = curasset.get_attribute("HIAestate")
            Aimphi = curasset.get_attribute("HIAeEIA")

        hasCOM = curasset.get_attribute("Has_COM")
        if hasCOM is None:
            hasCOM, num_estatesCOM, com_avail_sp, Acom, Aimpcom = 0, 0, 0, 0, 0
        else:
            num_estatesCOM = curasset.get_attribute("COMestates")
            com_avail_sp = curasset.get_attribute("avLt_COM")
            Acom = curasset.get_attribute("COMAestate")
            Aimpcom = curasset.get_attribute("COMAeEIA")

        # SKIP CONDITION #1 - no units to build in
        if sum([hasHouses, hasFlats, hasLI, hasHI, hasCOM]) == 0:
            # .notify(self.assetident+str(curID)+" has no applicable lots or estates for systems, skipping")
            return techdesigns  # Empty list

        # SKIP CONDITION #2 - no available space to build on
        if sum([res_avail_sp, hdr_avail_sp, li_avail_sp, hi_avail_sp, com_avail_sp]) < 0.0001:
            # self.notify(self.assetident + str(curID) + " has no available space for systems, skipping")
            return techdesigns     # Empty list

        # KPIs - write total available space
        curasset.add_attribute("LOT_Avail", sum([num_allots*res_avail_sp, hdr_avail_sp, li_avail_sp*num_estatesLI,
                                                 hi_avail_sp*num_estatesHI, com_avail_sp*num_estatesCOM]))

        # INCORPORATE ANY FURTHER INFORMATION LIKE SOIL INFILTRATION
        pass

        # SIZE THE REQUIRED STORAGE VOLUME FOR POTABLE SUPPLY SUBSTITUTION
        # [TO DO]

        # DESIGN THE TECHNOLOGIES NOW FOR THEIR APPLICATIONS
        for tech in techlist:
            if tech in ["TANK"]:
                continue

            # LOOKUP TECHNOLOGY PARAMETERS TO GENERIC VARIABLES
            minsize = eval("self." + tech.lower() + "_minsize")
            maxsize = eval("self." + tech.lower() + "_maxsize")
            rules = nbsdesignrules[tech]    # [psysFLOW, ratiodefFLOW, psysWQ, ratiodefWQ]
            exfil = eval("self."+tech.lower()+"_exfil")
            flow = eval("self."+tech.lower()+"_flow")
            wq = eval("self."+tech.lower()+"_wq")

            res_options = self.design_lot_scale_surface_area_system(Alot, Aimpres, res_avail_sp, minsize,
                                                                    maxsize, rules, exfil, flow, wq, techincr, curID,
                                                                    num_allots, tech, "L_RES")
            [techdesigns.append(option) for option in res_options]

            hdr_options = self.design_lot_scale_surface_area_system(Ahdr, Aimphdr, hdr_avail_sp, minsize,
                                                                    maxsize, rules, exfil, flow, wq, techincr, curID,
                                                                    num_hdr, tech, "L_HDR")
            [techdesigns.append(option) for option in hdr_options]

            li_options = self.design_lot_scale_surface_area_system(Ali, Aimpli, li_avail_sp, minsize,
                                                                   maxsize, rules, exfil, flow, wq, techincr, curID,
                                                                   num_estatesLI, tech, "L_LI")
            [techdesigns.append(option) for option in li_options]

            hi_options = self.design_lot_scale_surface_area_system(Ahi, Aimphi, hi_avail_sp, minsize,
                                                                   maxsize, rules, exfil, flow, wq, techincr, curID,
                                                                   num_estatesHI, tech, "L_HI")
            [techdesigns.append(option) for option in hi_options]

            com_options = self.design_lot_scale_surface_area_system(Acom, Aimpcom, com_avail_sp, minsize,
                                                                    maxsize, rules, exfil, flow, wq, techincr, curID,
                                                                    num_estatesCOM, tech, "L_COM")
            [techdesigns.append(option) for option in com_options]

        return techdesigns

    def design_lot_scale_surface_area_system(self, Alot, Aimp, avsp, minsize, maxsize, rules, exfil,
                                             flow, wq, incr, curid, qtyunits, tech, scaleabbr):
        """Basic algorithm for sizing system by ratios for flow or water quality objectives. Rule of thumb sizing for
        any surface area based system.
        """
        # STEP 1 - GET DESIGN AREA
        A_system = 0    # initialize
        if self.runoff_obj:     # If we designing for runoff or using universal capture
            if rules[1] == "ALL":
                A_system = max(A_system, rules[0]/100.0 * Alot, minsize)
            else:
                A_system = max(A_system, rules[0]/100.0 * Aimp, minsize)
        if self.wq_obj:    # if water quality and we using different capture ratios...
            if rules[3] == "ALL":
                A_system = max(A_system, rules[2]/100.0 * Alot, minsize)
            else:
                A_system = max(A_system, rules[2]/100.0 * Aimp, minsize)    # if the area is bigger, replace...

        if A_system == 0 or A_system > maxsize:
            return []

        # STEP 2 - GET ADDITIONAL AREA
        if tech in ["BF", "INFIL"]:     # Infiltrating systems
            if exfil > 180:
                setback = 1.0
            elif exfil > 36:
                setback = 2.0
            elif exfil > 3.6:
                setback = 4.0
            else:
                setback = 5.0

            A_required = np.power((np.sqrt(A_system) + 2 * setback), 2)
            scale_fact = A_required/A_system
        elif tech in ["WET", "PB"]:     # Basin Systems
            scale_fact = 1.3
            A_required = A_system * scale_fact
        else:
            A_required = 0

        # STEP 3 - Does it fit?
        options = []
        if A_required < avsp and A_required != 0:       # if there is space and the area is not zero...
            # YES - setup database
            for i in range(len(incr)):
                if incr[i] == 0:
                    continue
                option = {"AssetID": curid, "Scale": scaleabbr, "SysType": tech, "A_design": A_system,
                          "scale_fact": scale_fact, "Qty": int(qtyunits*incr[i]),
                          "QtyImpServed": self.runoff_obj * flow * Aimp * int(qtyunits*incr[i]),
                          "WQImpServed": self.wq_obj * wq * Aimp * int(qtyunits*incr[i]),
                          "DesignIncr": incr[i]
                          }
                options.append(option)
        return options

    def assess_street_opportunities(self, techlist, techincr, curasset, curID, nbsdesignrules):
        """Basic algorithm for sizing system by ratios for flow or water quality objectives. Rule of thumb sizing for
                any surface area based system.
                """
        techdesigns = []  # list of tech

        # Step 1 - Check if there are lot-stuff to work with!
        catchment = curasset.get_attribute("Area") * curasset.get_attribute("Activity")
        catchimp = curasset.get_attribute("Blk_TIA")

        street_space = sum([curasset.get_attribute("avSt_RES"), curasset.get_attribute("avSt_LI"),
                            curasset.get_attribute("avSt_HI"), curasset.get_attribute("avSt_COM"),
                            curasset.get_attribute("avSt_ORC")])
        und_space = curasset.get_attribute("UND_av")
        pg_space = curasset.get_attribute("PG_av")
        ref_space = curasset.get_attribute("REF_av")
        svu_space = curasset.get_attribute("SVU_avSW")
        rd_space = curasset.get_attribute("RD_av")

        # SKIP CONDITION #1 - no units to build in
        if sum([street_space, und_space, pg_space, ref_space, svu_space, rd_space]) <= 0.0001:
            # self.notify(self.assetident + str(curID) + " has noavailable space for systems, skipping")
            return techdesigns  # Empty list

        # SKIP CONDITION #2 - no available space to build on
        if catchimp == 0:
            # self.notify(self.assetident + str(curID) + " has no local impervious to serve, skipping")
            return techdesigns  # Empty list

        # KPI 0 - write available space
        curasset.add_attribute("ST_Avail", sum([und_space, pg_space, ref_space, svu_space, rd_space]))

        # INCORPORATE ANY FURTHER INFORMATION LIKE SOIL INFILTRATION
        pass

        # SIZE THE REQUIRED STORAGE VOLUME FOR POTABLE SUPPLY SUBSTITUTION
        # [TO DO]

        # DESIGN THE TECHNOLOGIES NOW FOR THEIR APPLICATIONS
        for tech in techlist:
            if tech in ["TANK"]:
                continue

            # LOOKUP TECHNOLOGY PARAMETERS TO GENERIC VARIABLES
            minsize = eval("self." + tech.lower() + "_minsize")
            maxsize = eval("self." + tech.lower() + "_maxsize")
            rules = nbsdesignrules[tech]  # [psysFLOW, ratiodefFLOW, psysWQ, ratiodefWQ]
            exfil = eval("self." + tech.lower() + "_exfil")
            flow = eval("self." + tech.lower() + "_flow")
            wq = eval("self." + tech.lower() + "_wq")

            # Get permissions
            tp = eval("self." + tech.lower() + "_permissions")  # permissions
            avail_space = street_space * tp["nstrip"] + und_space * tp["UND"] + \
                          pg_space * tp["PG"] + ref_space * tp["REF"] + svu_space + rd_space

            street_options = self.design_surface_area_system(catchment, catchimp, avail_space, minsize,
                                                             maxsize, rules, exfil, flow, wq, techincr, curID,
                                                             tech, "STREET")
            [techdesigns.append(option) for option in street_options]

        return techdesigns

    def design_surface_area_system(self, catchment, catchimp, avsp, minsize, maxsize, rules, exfil,
                                   flow, wq, techincr, curid, tech, scaleabbr):
        """Basic algorithm for sizing system by ratios for flow or water quality objectives. Rule of thumb sizing for
        any surface area based system.
        """
        options = []
        for incr in techincr:
            if incr == 0:
                continue

            # STEP 1 - GET DESIGN AREA
            A_system = 0  # initialize
            if self.runoff_obj:
                if rules[1] == "ALL":
                    A_system = max(A_system, rules[0] / 100.0 * catchment*incr, minsize)
                else:
                    A_system = max(A_system, rules[0] / 100.0 * catchimp*incr, minsize)
            if self.wq_obj:
                if rules[3] == "ALL":
                    A_system = max(A_system, rules[2] / 100.0 * catchment*incr, minsize)
                else:
                    A_system = max(A_system, rules[2] / 100.0 * catchimp*incr, minsize)

            if A_system > maxsize:
                return []

            # STEP 2 - GET ADDITIONAL AREA
            if tech in ["BF", "INFIL"]:  # Infiltrating systems
                if exfil > 180:
                    setback = 1.0
                elif exfil > 36:
                    setback = 2.0
                elif exfil > 3.6:
                    setback = 4.0
                else:
                    setback = 5.0

                A_required = np.power((np.sqrt(A_system) + 2 * setback), 2)
                scale_fact = A_required / A_system
            elif tech in ["WET", "PB"]:  # Basin Systems
                scale_fact = 1.3
                A_required = A_system * scale_fact
            else:
                A_required = 0

            # STEP 3 - Does it fit?
            if A_required < avsp and A_required != 0:  # if there is space and the area is not zero...
                # YES - setup database
                option = {"AssetID": curid, "Scale": scaleabbr, "SysType": tech, "A_design": A_system,
                          "scale_fact": scale_fact, "Qty": 1,
                          "QtyImpServed": self.runoff_obj * flow * catchimp * incr,
                          "WQImpServed": self.wq_obj * wq * catchimp * incr,
                          "DesignIncr": incr
                          }
                options.append(option)

        return options

    def assess_region_opportunities(self, techlist, techinr, curasset, curID, nbsdesignrules):
        """Basic algorithm for sizing system by ratios for flow or water quality objectives at the regional scale.
        Rule of thumb sizing for any surface area based system.
                        """
        techdesigns = []  # list of tech

        # Step 1 - Check if there are lot-stuff to work with! Upstream!
        upstreamids = curasset.get_attribute("UpstrIDs")
        if len(upstreamids) == 0:
            # self.notify("AssetID"+str(curID)+" has no upstream areas, skipping!")
            return []

        upstrareas = self.assets.retrieve_attribute_value_list(self.assetident, "Blk_TIA", upstreamids)
        upstreamimp = sum(upstrareas[1])

        if upstreamimp == 0:
            # self.notify("No upstream impervious area to design for, skipping")
            return []

        upstrcatch = self.assets.retrieve_attribute_value_list(self.assetident, "Area", upstreamids)
        upstractivity = self.assets.retrieve_attribute_value_list(self.assetident, "Activity", upstreamids)
        upstrcatcharea = 0
        for i in range(len(upstrcatch[0])):
            upstrcatcharea += (upstrcatch[1][i] * upstractivity[1][i])

        und_space = curasset.get_attribute("UND_av")
        pg_space = curasset.get_attribute("PG_av")
        ref_space = curasset.get_attribute("REF_av")
        svu_space = curasset.get_attribute("SVU_avSW")
        if sum([und_space, pg_space, ref_space, svu_space]) <= 0.0001:
            # self.notify("No available space for systems, skipping.")
            return []

        # KPI 0 - write available space at regional scale
        curasset.add_attribute("REG_Avail", sum([und_space, pg_space, ref_space, svu_space]))

        # INCORPORATE ANY FURTHER INFORMATION LIKE SOIL INFILTRATION
        pass

        # SIZE THE REQUIRED STORAGE VOLUME FOR POTABLE SUPPLY SUBSTITUTION
        # [TO DO]

        # DESIGN THE TECHNOLOGIES NOW FOR THEIR APPLICATIONS
        for tech in techlist:
            if tech in ["TANK"]:
                continue

            # LOOKUP TECHNOLOGY PARAMETERS TO GENERIC VARIABLES
            minsize = eval("self." + tech.lower() + "_minsize")
            maxsize = eval("self." + tech.lower() + "_maxsize")
            rules = nbsdesignrules[tech]  # [psysFLOW, ratiodefFLOW, psysWQ, ratiodefWQ]
            exfil = eval("self." + tech.lower() + "_exfil")
            flow = eval("self." + tech.lower() + "_flow")
            wq = eval("self." + tech.lower() + "_wq")

            # Get permissions
            tp = eval("self." + tech.lower() + "_permissions")  # permissions
            avail_space = und_space * tp["UND"] + pg_space * tp["PG"] + ref_space * tp["REF"] + svu_space
            region_options = self.design_surface_area_system(upstrcatcharea, upstreamimp, avail_space, minsize,
                                                             maxsize, rules, exfil, flow, wq, techinr, curID,
                                                             tech, "REGION")
            [techdesigns.append(option) for option in region_options]

        return techdesigns

    def load_rescale_climate_data(self):
        pass    # [ TO DO ]
        return True

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
                        self.userTech[j][k_scale] = 0
                    except AttributeError:
                        self.userTech[j][k_scale] = 0
        return True