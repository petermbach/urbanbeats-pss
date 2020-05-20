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
        # --- Bioretention Systems / Raingardens ---
        self.create_parameter()

    def run(self):
        pass
