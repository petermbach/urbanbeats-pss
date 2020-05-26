r"""
@file   md_bgsplanning.py
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
from .ubmodule import *


# --- MODULE CLASS DEFINITION ---
class BlueGreenSystemsPlanning(UBModule):
    """ BLUE-GREEN SYSTEMS MODULE
    Undertakes an impact assessment of the current scenario based on the
    various impacts labelled. The model performs various assessments and outputs
    useful indicators showing the before-after situations of different scenarios
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "Blue-Green Systems Planning Module"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        ###################
        ## GENERAL SETUP ##
        ###################
        # --- Planning Objectives for BGS ---
        self.create_parameter("obj_run", BOOL, "Plan for runoff volume reduction?")
        self.create_parameter("obj_run_priority", DOUBLE, "Priority level of runoff reduction")
        self.create_parameter("obj_run_target", DOUBLE, "Target for runoff reduction to achieve")
        self.create_parameter("obj_run_service", DOUBLE, "Service level for runoff reduction to achieve")
        self.create_parameter("obj_run_redund", DOUBLE, "Allowable service redundancey for runoff volume reduction")
        self.obj_run = 0
        self.obj_run_priority = 1.0
        self.obj_run_target = 20.0
        self.obj_run_service = 50.0
        self.obj_run_redund = 0.0

        self.create_parameter("obj_wq", BOOL, "Plan for pollution load reduction?")
        self.create_parameter("obj_wq_priority", DOUBLE, "Priority level of pollution reduction")
        self.create_parameter("obj_wq_target_tss", DOUBLE, "Target for pollution reduction to achieve")
        self.create_parameter("obj_wq_target_tn", DOUBLE, "Target for pollution reduction to achieve")
        self.create_parameter("obj_wq_target_tp", DOUBLE, "Target for pollution reduction to achieve")
        self.create_parameter("obj_wq_service", DOUBLE, "Service level for pollution reduction to achieve")
        self.create_parameter("obj_wq_redund", DOUBLE, "Allowable service redundancey for pollution load reduction")
        self.obj_wq = 0
        self.obj_wq_priority = 1.0
        self.obj_wq_target_tss = 80.0
        self.obj_wq_target_tn = 45.0
        self.obj_wq_target_tp = 45.0
        self.obj_wq_service = 30.0
        self.obj_wq_redund = 0.0

        self.create_parameter("obj_rec", BOOL, "Plan for potable water reduction i.e. recycling?")
        self.create_parameter("obj_rec_priority", DOUBLE, "Priority level of runoff reduction")
        self.create_parameter("obj_rec_target", DOUBLE, "Target for runoff reduction to achieve")
        self.create_parameter("obj_rec_service", DOUBLE, "Service level for runoff reduction to achieve")
        self.create_parameter("obj_rec_redund", DOUBLE, "Allowable service redundancey for runoff volume reduction")
        self.obj_rec = 0
        self.obj_rec_priority = 1.0
        self.obj_rec_target = 20.0
        self.obj_rec_service = 50.0
        self.obj_rec_redund = 0.0

        self.create_parameter("obj_amen", BOOL, "Plan for potable water reduction i.e. recycling?")
        self.create_parameter("obj_amen_priority", DOUBLE, "Priority level of runoff reduction")
        self.create_parameter("obj_amen_target_green", DOUBLE, "Target for runoff reduction to achieve")
        self.create_parameter("obj_amen_target_andor", BOOL, "Service level for runoff reduction to achieve")
        self.create_parameter("obj_amen_target_blue", DOUBLE, "Service level for runoff reduction to achieve")
        self.create_parameter("obj_amen_service", DOUBLE, "Service level for runoff reduction to achieve")
        self.create_parameter("obj_amen_redund", DOUBLE, "Allowable service redundancey for runoff volume reduction")
        self.obj_amen = 0
        self.obj_amen_priority = 1.0
        self.obj_amen_target_green = 100.0
        self.obj_amen_target_andor = 0
        self.obj_amen_target_blue = 100.0
        self.obj_amen_service = 100
        self.obj_amen_redund = 0.0

        # --- Spatial Planning Rules ---
        self.create_parameter("service_res", BOOL, "Service in residential dwellings?")
        self.create_parameter("service_hdr", BOOL, "Service in high-density apartment areas?")
        self.create_parameter("service_com", BOOL, "Service in commercial zones?")
        self.create_parameter("service_li", BOOL, "Service in light industry areas?")
        self.create_parameter("service_hi", BOOL, "Service in heavy industry areas?")
        self.service_res = 1
        self.service_hdr = 1
        self.service_com = 1
        self.service_li = 1
        self.service_hi = 1

        self.create_parameter("overlays", BOOL, "Consider planning overlays?")
        self.overlays = 0

        self.create_parameter("limit_pg_use", BOOL, "Limit use of parks and gardens?")
        self.create_parameter("limit_pg", DOUBLE, "Percentage of allowable space")
        self.create_parameter("limit_ref", BOOL, "Prohibit use of systems in reserves and floodways")
        self.create_parameter("limit_for", BOOL, "Prohibit use of systems in forested areas")
        self.limit_pg_use = 0
        self.limit_pg = 50.0
        self.limit_ref = 0
        self.limit_for = 0

        # --- Existing Assets ---

        # --- Select Technologies ---
        self.create_parameter("use_BIOF", BOOL, "Bioretention systems, raingardens")
        self.create_parameter("use_WSUR", BOOL, "Surface constructed wetlands")
        self.create_parameter("use_EVAP", BOOL, "Evaporation basins")
        self.create_parameter("use_INFS", BOOL, "Infiltration systems and trenches")
        self.create_parameter("use_POND", BOOL, "Ponds and sedimentation basins")
        self.create_parameter("use_SWAL", BOOL, "Swales")
        self.create_parameter("use_ROOF", BOOL, "Green Roofs")
        self.create_parameter("use_WALL", BOOL, "Green Wall")
        self.create_parameter("use_PAVE", BOOL, "Porous and pervious pavements")
        self.create_parameter("use_TANK", BOOL, "Rainwater and Stormwater Tanks")
        self.create_parameter("use_BASN", BOOL, "Retarding Basin")
        self.create_parameter("use_FILT", BOOL, "Sand and Gravel Filters or French Drains")
        self.create_parameter("use_DISC", BOOL, "Impervious surface disconnection")
        self.create_parameter("use_BANK", BOOL, "Riverbank restoration")
        self.use_BIOF = 0
        self.use_WSUR = 0
        self.use_EVAP = 0
        self.use_INFS = 0
        self.use_POND = 0
        self.use_SWAL = 0
        self.use_ROOF = 0
        self.use_WALL = 0
        self.use_PAVE = 0
        self.use_TANK = 0
        self.use_BASN = 0
        self.use_FILT = 0
        self.use_DISC = 0
        self.use_BANK = 0

        # --- Simulation Settings ---
        self.create_parameter("planning_algorithm", STRING, "Select the planning algorithm method")
        self.planning_algorithm = "Bach2020"

        self.create_parameter("scale_lot", BOOL, "Plan systems at the lot scale?")
        self.create_parameter("scale_lot_rig", DOUBLE, "Rigour of lot-scale systems planning, combinatorics")
        self.scale_lot = 1
        self.scale_lot_rig = 4

        self.create_parameter("scale_street", BOOL, "Plan systems at the street scale?")
        self.create_parameter("scale_street_rig", DOUBLE, "Rigour of street-scale systems planning, combinatorics")
        self.scale_street = 1
        self.scale_street_rig = 4

        self.create_parameter("scale_region", BOOL, "Plan regional systems")
        self.create_parameter("scale_region_rig", DOUBLE, "Rigour of regional systems planning, combinatorics")
        self.scale_region = 1
        self.scale_region_rig = 4

        self.create_parameter("scale_preference", BOOL, "Define a scale preference?")
        self.create_parameter("scale_preference_score", DOUBLE, "Scale preference score")
        self.scale_preference = 0
        self.scale_preference_score = 3     # 1 = 4-1-1, 2 = 3-2-1, 3 = 2-2-2, 4 = 1-2-3, 5 = 1-1-4 small-med-large

        self.scale_lot_w = 2        # Advanced - weights assigned to all scales based on scale-preference score
        self.scale_street_w = 2
        self.scale_region_w = 2

        # --- Life Cycle Costing ---
        # --- Implementation Rules ---

        ########################
        ## TECHNOLOGIES SETUP ##
        ########################
        # --- BIORETENTION SYSTEMS / RAINGARDENS ---
        # Scales, Applications and Permissions
        self.create_parameter("biof_scales", LISTDOUBLE, "Scales of biofilter use")
        self.create_parameter("biof_objs", LISTDOUBLE, "Objectives for biofilters")
        self.create_parameter("biof_permissions", LISTDOUBLE, "Permissible locations for biofilters")
        self.biof_scales = [0, 0, 0]    # [Lot, Street, Regional]
        self.biof_objs = [0, 0, 0, 0, 0]    # [FLOW, POLLUTE, RECYCLE, AMENITY, ECO]
        self.biof_permissions = [1, 1, 1, 1, 1, 1]  # [PG, REF, FOR, AGR, NS, GARDEN]

        # Design Specs
        self.create_parameter("biof_curveoption", STRING, "Design curve option")
        self.create_parameter("biof_curvepath", STRING, "Filepath to custom curve")
        self.create_parameter("biof_minsize", DOUBLE, "Minimum allowable system size")
        self.create_parameter("biof_maxsize", DOUBLE, "Maximum allowable system size")
        self.create_parameter("biof_exfil", STRING, "Exfiltration rate from system")
        self.biof_curveoption = "UBDB"  # UBDB = UrbanBEATS Database, CUST = Custom
        self.biof_curvepath = "(path to design curve .dcv)"
        self.biof_minsize = 0.0
        self.biof_maxsize = 100000.0
        self.biof_exfil = "0"

        # Unique Design Specs for system
        self.create_parameter("biof_edd", STRING, "Extended detention depth")
        self.create_parameter("biof_fd", STRING, "Filter depth of biofilter")
        self.biof_edd = "0"
        self.biof_fd = "200"

        # Life Cycle Costing
        self.create_parameter("biof_lifespan", DOUBLE, "Life span of system [years]")
        self.create_parameter("biof_renewalcycle", DOUBLE, "Renewal cycle for biofilter [years]")
        self.biof_lifespan = 50
        self.biof_renewalcycle = 10

        self.create_parameter("biof_lccmethod", STRING, "LCC Costing Method")
        self.create_parameter("biof_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("biof_tam", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("biof_rc", DOUBLE, "Total renewal cost")
        self.create_parameter("biof_dc", DOUBLE, "Total decomissioning cost")
        self.create_parameter("biof_tacindic", DOUBLE, "Indicative Total Acquisition Cost")
        self.create_parameter("biof_tamindic", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("biof_rcindic", DOUBLE, "Total renewal cost")
        self.create_parameter("biof_dcindic", DOUBLE, "Total decomissioning cost")
        self.biof_lccmethod = "DIRECT"
        self.biof_tac = 0.00
        self.biof_tam = 0.00
        self.biof_rc = 0.00
        self.biof_dc = 0.00
        self.biof_tacindic = 0.00
        self.biof_tamindic = 0.00
        self.biof_rcindic = 0.00
        self.biof_dcindic = 0.00

        # --- CONSTRUCTED WETLANDS ---
        # Scales, Applications and Permissions
        self.create_parameter("wsur_scales", LISTDOUBLE, "Scales of wetland use")
        self.create_parameter("wsur_objs", LISTDOUBLE, "Objectives for wetlands")
        self.create_parameter("wsur_permissions", LISTDOUBLE, "Permissible locations for wetlands")
        self.wsur_scales = [0, 0, 0]  # [Lot, Street, Regional]
        self.wsur_objs = [0, 0, 0, 0, 0]  # [FLOW, POLLUTE, RECYCLE, AMENITY, ECO]
        self.wsur_permissions = [1, 1, 1, 1, 1, 1]  # [PG, REF, FOR, AGR, NS, GARDEN]

        # Design Specs
        self.create_parameter("wsur_curveoption", STRING, "Design curve option")
        self.create_parameter("wsur_curvepath", STRING, "Filepath to custom curve")
        self.create_parameter("wsur_minsize", DOUBLE, "Minimum allowable system size")
        self.create_parameter("wsur_maxsize", DOUBLE, "Maximum allowable system size")
        self.create_parameter("wsur_exfil", STRING, "Exfiltration rate from system")
        self.wsur_curveoption = "UBDB"  # UBDB = UrbanBEATS Database, CUST = Custom
        self.wsur_curvepath = "(path to design curve .dcv)"
        self.wsur_minsize = 0.0
        self.wsur_maxsize = 100000.0
        self.wsur_exfil = "0"

        # Unique Design Specs for system
        self.create_parameter("wsur_edd_dt", STRING, "Extended detention depth")
        self.wsur_edd_dt = "250mm 72hr"

        # Life Cycle Costing
        self.create_parameter("wsur_lifespan", DOUBLE, "Life span of system [years]")
        self.create_parameter("wsur_renewalcycle", DOUBLE, "Renewal cycle for wetland [years]")
        self.wsur_lifespan = 50
        self.wsur_renewalcycle = 10

        self.create_parameter("wsur_lccmethod", STRING, "LCC Costing Method")
        self.create_parameter("wsur_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("wsur_tam", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("wsur_rc", DOUBLE, "Total renewal cost")
        self.create_parameter("wsur_dc", DOUBLE, "Total decomissioning cost")
        self.create_parameter("wsur_tacindic", DOUBLE, "Indicative Total Acquisition Cost")
        self.create_parameter("wsur_tamindic", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("wsur_rcindic", DOUBLE, "Total renewal cost")
        self.create_parameter("wsur_dcindic", DOUBLE, "Total decomissioning cost")
        self.wsur_lccmethod = "DIRECT"
        self.wsur_tac = 0.00
        self.wsur_tam = 0.00
        self.wsur_rc = 0.00
        self.wsur_dc = 0.00
        self.wsur_tacindic = 0.00
        self.wsur_tamindic = 0.00
        self.wsur_rcindic = 0.00
        self.wsur_dcindic = 0.00

        # --- Evaporation Fields ---
        # --- Green Roof Systems ---
        # --- Green Walls / Living Walls ---

        # --- INFILTRATION SYSTEMS ---
        # Scales, Applications and Permissions
        self.create_parameter("infs_scales", LISTDOUBLE, "Scales of infiltration system use")
        self.create_parameter("infs_objs", LISTDOUBLE, "Objectives for infiltration systems")
        self.create_parameter("infs_permissions", LISTDOUBLE, "Permissible locations for infiltration systems")
        self.infs_scales = [0, 0, 0]  # [Lot, Street, Regional]
        self.infs_objs = [0, 0, 0, 0, 0]  # [FLOW, POLLUTE, RECYCLE, AMENITY, ECO]
        self.infs_permissions = [1, 1, 1, 1, 1, 1]  # [PG, REF, FOR, AGR, NS, GARDEN]

        # Design Specs
        self.create_parameter("infs_curveoption", STRING, "Design curve option")
        self.create_parameter("infs_curvepath", STRING, "Filepath to custom curve")
        self.create_parameter("infs_minsize", DOUBLE, "Minimum allowable system size")
        self.create_parameter("infs_maxsize", DOUBLE, "Maximum allowable system size")
        self.create_parameter("infs_exfil", STRING, "Exfiltration rate from system")
        self.infs_curveoption = "UBDB"  # UBDB = UrbanBEATS Database, CUST = Custom
        self.infs_curvepath = "(path to design curve .dcv)"
        self.infs_minsize = 0.0
        self.infs_maxsize = 100000.0
        self.infs_exfil = "0"

        # Unique Design Specs for system
        self.create_parameter("infs_edd", STRING, "Extended detention depth")
        self.create_parameter("infs_fd", STRING, "Filter depth of infiltration system")
        self.infs_edd = "100"
        self.infs_fd = "200"

        # Life Cycle Costing
        self.create_parameter("infs_lifespan", DOUBLE, "Life span of system [years]")
        self.create_parameter("infs_renewalcycle", DOUBLE, "Renewal cycle for infiltration system [years]")
        self.infs_lifespan = 50
        self.infs_renewalcycle = 10

        self.create_parameter("infs_lccmethod", STRING, "LCC Costing Method")
        self.create_parameter("infs_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("infs_tam", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("infs_rc", DOUBLE, "Total renewal cost")
        self.create_parameter("infs_dc", DOUBLE, "Total decomissioning cost")
        self.create_parameter("infs_tacindic", DOUBLE, "Indicative Total Acquisition Cost")
        self.create_parameter("infs_tamindic", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("infs_rcindic", DOUBLE, "Total renewal cost")
        self.create_parameter("infs_dcindic", DOUBLE, "Total decomissioning cost")
        self.infs_lccmethod = "DIRECT"
        self.infs_tac = 0.00
        self.infs_tam = 0.00
        self.infs_rc = 0.00
        self.infs_dc = 0.00
        self.infs_tacindic = 0.00
        self.infs_tamindic = 0.00
        self.infs_rcindic = 0.00
        self.infs_dcindic = 0.00

        # --- PONDS / SEDIMENTATION BASINS ---
        # Scales, Applications and Permissions
        self.create_parameter("pond_scales", LISTDOUBLE, "Scales of pond use")
        self.create_parameter("pond_objs", LISTDOUBLE, "Objectives for ponds")
        self.create_parameter("pond_permissions", LISTDOUBLE, "Permissible locations for ponds")
        self.pond_scales = [0, 0, 0]  # [Lot, Street, Regional]
        self.pond_objs = [0, 0, 0, 0, 0]  # [FLOW, POLLUTE, RECYCLE, AMENITY, ECO]
        self.pond_permissions = [1, 1, 1, 1, 1, 1]  # [PG, REF, FOR, AGR, NS, GARDEN]

        # Design Specs
        self.create_parameter("pond_curveoption", STRING, "Design curve option")
        self.create_parameter("pond_curvepath", STRING, "Filepath to custom curve")
        self.create_parameter("pond_minsize", DOUBLE, "Minimum allowable system size")
        self.create_parameter("pond_maxsize", DOUBLE, "Maximum allowable system size")
        self.create_parameter("pond_exfil", STRING, "Exfiltration rate from system")
        self.pond_curveoption = "UBDB"  # UBDB = UrbanBEATS Database, CUST = Custom
        self.pond_curvepath = "(path to design curve .dcv)"
        self.pond_minsize = 0.0
        self.pond_maxsize = 100000.0
        self.pond_exfil = "0"

        # Unique Design Specs for system
        self.create_parameter("pond_md", STRING, "Extended detention depth")
        self.pond_md = "1.25"

        # Life Cycle Costing
        self.create_parameter("pond_lifespan", DOUBLE, "Life span of system [years]")
        self.create_parameter("pond_renewalcycle", DOUBLE, "Renewal cycle for pond [years]")
        self.pond_lifespan = 50
        self.pond_renewalcycle = 10

        self.create_parameter("pond_lccmethod", STRING, "LCC Costing Method")
        self.create_parameter("pond_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("pond_tam", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("pond_rc", DOUBLE, "Total renewal cost")
        self.create_parameter("pond_dc", DOUBLE, "Total decomissioning cost")
        self.create_parameter("pond_tacindic", DOUBLE, "Indicative Total Acquisition Cost")
        self.create_parameter("pond_tamindic", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("pond_rcindic", DOUBLE, "Total renewal cost")
        self.create_parameter("pond_dcindic", DOUBLE, "Total decomissioning cost")
        self.pond_lccmethod = "DIRECT"
        self.pond_tac = 0.00
        self.pond_tam = 0.00
        self.pond_rc = 0.00
        self.pond_dc = 0.00
        self.pond_tacindic = 0.00
        self.pond_tamindic = 0.00
        self.pond_rcindic = 0.00
        self.pond_dcindic = 0.00

        # --- Porous / Pervious Pavements ---

        # --- RAINWATER / STORMWATER TANKS ---
        # Scales, Applications and Permissions
        self.create_parameter("tank_scales", LISTDOUBLE, "Scales of tank use")
        self.create_parameter("tank_objs", LISTDOUBLE, "Objectives for tanks")
        self.create_parameter("tank_permissions", LISTDOUBLE, "Permissible locations for tanks")
        self.tank_scales = [0, 0, 0]  # [Lot, Street, Regional]
        self.tank_objs = [0, 0, 0, 0, 0]  # [FLOW, POLLUTE, RECYCLE, AMENITY, ECO]
        self.tank_permissions = [1, 1, 1, 1, 1, 1]  # [PG, REF, FOR, AGR, NS, GARDEN]

        # Design Specs
        self.create_parameter("tank_curveoption", STRING, "Design curve option")
        self.create_parameter("tank_curvepath", STRING, "Filepath to custom curve")
        self.tank_curveoption = "UBDB"  # UBDB = UrbanBEATS Database, CUST = Custom
        self.tank_curvepath = "(path to design curve .dcv)"

        # Unique Design Specs for system
        self.create_parameter("tank_maxdepth", DOUBLE, "Maximum tank depth [m]")
        self.create_parameter("tank_mindead", DOUBLE, "Minimum dead storage [m]")
        self.create_parameter("tank_maxvol", DOUBLE, "Maximum storage volume [kL]")
        self.tank_maxdepth = 2.0
        self.tank_mindead = 0.2
        self.tank_maxvol = 100

        # Life Cycle Costing
        self.create_parameter("tank_lifespan", DOUBLE, "Life span of system [years]")
        self.create_parameter("tank_renewalcycle", DOUBLE, "Renewal cycle for tank [years]")
        self.tank_lifespan = 50
        self.tank_renewalcycle = 10

        self.create_parameter("tank_lccmethod", STRING, "LCC Costing Method")
        self.create_parameter("tank_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("tank_tam", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("tank_rc", DOUBLE, "Total renewal cost")
        self.create_parameter("tank_dc", DOUBLE, "Total decomissioning cost")
        self.create_parameter("tank_tacindic", DOUBLE, "Indicative Total Acquisition Cost")
        self.create_parameter("tank_tamindic", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("tank_rcindic", DOUBLE, "Total renewal cost")
        self.create_parameter("tank_dcindic", DOUBLE, "Total decomissioning cost")
        self.tank_lccmethod = "DIRECT"
        self.tank_tac = 0.00
        self.tank_tam = 0.00
        self.tank_rc = 0.00
        self.tank_dc = 0.00
        self.tank_tacindic = 0.00
        self.tank_tamindic = 0.00
        self.tank_rcindic = 0.00
        self.tank_dcindic = 0.00

        # --- Retarding Basins ---
        # --- Sand / Gravel Filters (French Drains) ---

        # --- SWALES ---
        # Scales, Applications and Permissions
        self.create_parameter("swal_scales", LISTDOUBLE, "Scales of swale use")
        self.create_parameter("swal_objs", LISTDOUBLE, "Objectives for swales")
        self.create_parameter("swal_permissions", LISTDOUBLE, "Permissible locations for swales")
        self.swal_scales = [0, 0, 0]  # [Lot, Street, Regional]
        self.swal_objs = [0, 0, 0, 0, 0]  # [FLOW, POLLUTE, RECYCLE, AMENITY, ECO]
        self.swal_permissions = [1, 1, 1, 1, 1, 1]  # [PG, REF, FOR, AGR, NS, GARDEN]

        # Design Specs
        self.create_parameter("swal_curveoption", STRING, "Design curve option")
        self.create_parameter("swal_curvepath", STRING, "Filepath to custom curve")
        self.create_parameter("swal_minsize", DOUBLE, "Minimum allowable system size")
        self.create_parameter("swal_maxsize", DOUBLE, "Maximum allowable system size")
        self.create_parameter("swal_exfil", STRING, "Exfiltration rate from system")
        self.swal_curveoption = "UBDB"  # UBDB = UrbanBEATS Database, CUST = Custom
        self.swal_curvepath = "(path to design curve .dcv)"
        self.swal_minsize = 0.0
        self.swal_maxsize = 100000.0
        self.swal_exfil = "0"

        # Unique Design Specs for system
        self.create_parameter("swal_spec", STRING, "Designspec for Swale")
        self.swal_spec = "1perc_0.5mveg"

        # Life Cycle Costing
        self.create_parameter("swal_lifespan", DOUBLE, "Life span of system [years]")
        self.create_parameter("swal_renewalcycle", DOUBLE, "Renewal cycle for swale [years]")
        self.swal_lifespan = 50
        self.swal_renewalcycle = 10

        self.create_parameter("swal_lccmethod", STRING, "LCC Costing Method")
        self.create_parameter("swal_tac", DOUBLE, "Total Acquisition Cost")
        self.create_parameter("swal_tam", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("swal_rc", DOUBLE, "Total renewal cost")
        self.create_parameter("swal_dc", DOUBLE, "Total decomissioning cost")
        self.create_parameter("swal_tacindic", DOUBLE, "Indicative Total Acquisition Cost")
        self.create_parameter("swal_tamindic", DOUBLE, "Total Annual Maintenance Cost")
        self.create_parameter("swal_rcindic", DOUBLE, "Total renewal cost")
        self.create_parameter("swal_dcindic", DOUBLE, "Total decomissioning cost")
        self.swal_lccmethod = "DIRECT"
        self.swal_tac = 0.00
        self.swal_tam = 0.00
        self.swal_rc = 0.00
        self.swal_dc = 0.00
        self.swal_tacindic = 0.00
        self.swal_tamindic = 0.00
        self.swal_rcindic = 0.00
        self.swal_dcindic = 0.00

        ##############################
        ## Preferences & Evaluation ##
        ##############################
        # --- Define Technology Preference Scores ---

        # --- Evaluation, Ranking and Selection ---

    def run(self):
        pass
