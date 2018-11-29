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
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
import model.progref.ubglobals as ubglobals


# --- MODULE CLASS DEFINITION ---
class UrbanPlanning(UBModule):
    """ URBAN FORM PLANNING AND ABSTRACTION MODULE
    Creates and abstraction and procedural generation of the urban form
    for further analysis in later modules.
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "Urban Planning Module for UrbanBEATS"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # INPUT PARAMETER LIST
        # Planning Templates
        self.create_parameter("plan_type", STRING, "Dominant planning typology")
        self.create_parameter("plan_template", STRING, "Option for setting planning parameters")
        self.create_parameter("plan_paramset", STRING, "Default parameter set to use")
        self.create_parameter("plan_paramfile", STRING, "Filename of loaded parameter set")
        self.plan_type = "Suburbia"   # Suburbia, European, Megacity
        self.plan_template = "PREDEF"   # PREDEF = pre-defined, PRELOAD = pre-filled
        self.plan_paramset = "Custom"   # Custom or Melbourne
        self.plan_paramfile = ""

        # Additional Data Sets
        self.create_parameter("emp_map", STRING, "Data reference ID for using an employment map")
        self.create_parameter("emp_fud", BOOL, "Obtain employment from the urban development module?")
        self.create_parameter("local_map", STRING, "Data reference ID for the locality map")
        self.create_parameter("local_attref", STRING, "The attribute name that contains the keys for features.")
        self.create_parameter("roadnet_map", STRING, "Data reference ID for using a road network map")
        self.create_parameter("roadnet_attref", STRING, "Data reference ID for the attribute name for road type")
        self.emp_map = ""
        self.emp_fud = 0
        self.local_map = ""
        self.local_attref = ""
        self.roadnet_map = ""
        self.roadnet_attref = ""

        # General City Structure
        self.create_parameter("cityarchetype", STRING, "")
        self.create_parameter("citysprawl", DOUBLE, "")
        self.cityarchetype = "MC"  # MC = monocentric, PC = polycentric
        self.citysprawl = float(50.0)  # km - approximate urban sprawl radius from main CBD

        # Decision Variables for Block Dynamics
        self.create_parameter("lucredev", BOOL, "")
        self.create_parameter("popredev", BOOL, "")
        self.create_parameter("lucredev_thresh", DOUBLE, "")
        self.create_parameter("popredev_thresh", DOUBLE, "")
        self.create_parameter("noredev", BOOL, "")
        self.lucredev = 0
        self.popredev = 0
        self.lucredev_thresh = float(50.0)  # % threshold required for redevelopment to take place
        self.popredev_thresh = float(50.0)  # % threshold required for redevelopment to take place
        self.noredev = 1  # DO NOT REDEVELOP - if checked = True, then all the above parameters no longer used

        # RESIDENTIAL PARAMETERS
        # (includes all residential land uses of varying density)
        # Planning Parameters
        self.create_parameter("occup_avg", DOUBLE, "Average occupancy [pax per house]")
        self.create_parameter("occup_max", DOUBLE, "Maximum occupancy [pax per house]")
        self.create_parameter("person_space", DOUBLE, "Floor space per person [sqm]")
        self.create_parameter("extra_comm_area", DOUBLE, "% of extra communal area")
        self.create_parameter("avg_allot_depth", DOUBLE, "Average depth of a residential allotment [m]")
        self.create_parameter("allot_depth_default", BOOL, "Use the default allotment depth?")
        self.create_parameter("floor_num_max", DOUBLE, "Maximum number of floors")
        self.create_parameter("patio_area_max", DOUBLE, "maximum patio area [sqm] - assumed impervious")
        self.create_parameter("patio_covered", BOOL, "Is the patio covered by a roof?")
        self.create_parameter("carports_max", DOUBLE, "Maximum number of car ports")
        self.create_parameter("garage_incl", BOOL, "Include a garage? Changes open ground area to roof area")
        self.create_parameter("w_driveway_min", DOUBLE, "minimum driveway width [m]")
        self.occup_avg = float(2.67)
        self.occup_max = float(5.0)
        self.person_space = float(84.0)
        self.extra_comm_area = float(10.0)
        self.avg_allot_depth = float(40.0)
        self.allot_depth_default = int(1)
        self.floor_num_max = 2.0
        self.patio_area_max = float(2.0)
        self.patio_covered = 0
        self.carports_max = 2
        self.garage_incl = 0
        self.w_driveway_min = float(2.6)

        self.create_parameter("setback_f_min", DOUBLE, "Minimum front setback")
        self.create_parameter("setback_f_max", DOUBLE, "Maximum front setback")
        self.create_parameter("setback_s_min", DOUBLE, "Minimum side setback, applies to the rear as well")
        self.create_parameter("setback_s_max", DOUBLE, "Maximum side setback, applies to the rear as well")
        self.create_parameter("setback_f_med", BOOL, "Use the median front setback?")
        self.create_parameter("setback_s_med", BOOL, "Use the median side setback?")
        self.setback_f_min = float(2.0)
        self.setback_f_max = float(9.0)
        self.setback_s_min = float(1.0)
        self.setback_s_max = float(2.0)
        self.setback_f_med = 0
        self.setback_s_med = 0

        self.create_parameter("occup_flat_avg", DOUBLE, "Average occupancy of an apartment [pax per apartment]")
        self.create_parameter("flat_area_max", DOUBLE, "Maximum apartment size")
        self.create_parameter("commspace_indoor", DOUBLE, "Indoor communal space, % of total floor space")
        self.create_parameter("commspace_outdoor", DOUBLE, "Outdoor communal space, % of total floor space")
        self.create_parameter("floor_num_HDRmax", DOUBLE, "Maximum number of floors of high-rise apartments")
        self.create_parameter("setback_HDR_avg", DOUBLE, "Average setback for HDR site [m]")
        self.create_parameter("parking_HDR", STRING, "Scheme for parking on HDR site")
        self.create_parameter("park_OSR", BOOL, "Leverage nearby parks to fulfill outdoor open space requirements?")
        self.occup_flat_avg = float(1.5)
        self.flat_area_max = float(90.0)
        self.commspace_indoor = float(10.0)
        self.commspace_outdoor = float(5.0)
        self.floor_num_HDRmax = float(10.0)
        self.setback_HDR_avg = float(1.0)
        self.parking_HDR = "On"  # On = On-site, Off = Off-site, Var = Vary, NA = None
        self.park_OSR = 0

        self.create_parameter("res_fpwmin", DOUBLE, "Minimum footpath width in residential street")
        self.create_parameter("res_nswmin", DOUBLE, "Minimum nature strip width in residential street")
        self.create_parameter("res_fpwmax", DOUBLE, "Maximum footpath width in residential street")
        self.create_parameter("res_nswmax", DOUBLE, "Maximum nature strip width in residential street")
        self.create_parameter("res_lanemin", DOUBLE, "Minimum Road lane width in residential streets")
        self.create_parameter("res_lanemax", DOUBLE, "Maximum road lane width in residential streets")
        self.create_parameter("res_fpmed", BOOL, "Use the median footpath width?")
        self.create_parameter("res_nsmed", BOOL, "Use the median nature strip width?")
        self.create_parameter("res_lanemed", BOOL, "Use the median road lane width in residential streets?")
        self.res_fpwmin = 1.0
        self.res_nswmin = 1.0
        self.res_fpwmax = 3.0
        self.res_nswmax = 3.0
        self.res_lanemin = 3.0
        self.res_lanemax = 5.0
        self.res_fpmed = 0
        self.res_nsmed = 0
        self.res_lanemed = 0

        self.create_parameter("define_drainage_rule", BOOL, "Define a spatial rule fro allotment stormwater drainage?")
        self.create_parameter("roof_connected", STRING, "How is the roof connected")
        self.create_parameter("roof_dced_p", DOUBLE, "% of roof disconnection level")
        self.create_parameter("imperv_prop_dced", DOUBLE, "% of ground impervious area disconnected")
        self.define_drainage_rule = 1
        self.roof_connected = "Direct"  # Direct/Disconnected/Varied?
        self.roof_dced_p = 50
        self.imperv_prop_dced = 10

        # Advanced Parameters
        self.min_allot_width = float(
            10.0)  # minimum width of an allotment = 10m if exceeded, then will build double allotments
        self.houseLUIthresh = [3.0, 5.4]  # house min and max threshold for LUI
        self.aptLUIthresh = [3.7, 6.5]  # walk-up apartment min and max threshold for LUI
        self.highLUIthresh = [5.9, 8.0]  # high-rise apartments min and max threshold for LUI

        self.resLUIdict = {}  # ratio tables for residential distict planning (from Time-Saver Standards)
        self.resLUIdict["LUI"] = [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6,
                                  4.7, 4.8, 4.9,
                                  5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6,
                                  6.7, 6.8, 6.9, 7.0, 7.1,
                                  7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0]
        self.resLUIdict["FAR"] = [0.100, 0.107, 0.115, 0.123, 0.132, 0.141, 0.152, 0.162, 0.174, 0.187, 0.200, 0.214,
                                  0.230, 0.246,
                                  0.264, 0.283, 0.303, 0.325, 0.348, 0.373, 0.400, 0.429, 0.459, 0.492, 0.528, 0.566,
                                  0.606, 0.650, 0.696,
                                  0.746, 0.800, 0.857, 0.919, 0.985, 1.060, 1.130, 1.210, 1.300, 1.390, 1.490, 1.600,
                                  1.720, 1.840,
                                  1.970, 2.110, 2.260, 2.420, 2.600, 2.790, 2.990, 3.200]
        self.resLUIdict["OSR"] = [0.80, 0.80, 0.79, 0.79, 0.78, 0.78, 0.78, 0.77, 0.77, 0.77, 0.76, 0.76, 0.75, 0.75,
                                  0.74, 0.74, 0.73,
                                  0.73, 0.73, 0.72, 0.72, 0.72, 0.72, 0.71, 0.71, 0.71, 0.70, 0.70, 0.69, 0.69, 0.68,
                                  0.68, 0.68, 0.68, 0.68,
                                  0.67, 0.67, 0.67, 0.68, 0.68, 0.68, 0.68, 0.69, 0.70, 0.71, 0.72, 0.75, 0.76, 0.81,
                                  0.83, 0.86]
        self.resLUIdict["LSR"] = [0.65, 0.62, 0.60, 0.58, 0.55, 0.54, 0.53, 0.53, 0.52, 0.52, 0.52, 0.51, 0.51, 0.49,
                                  0.48, 0.48, 0.46,
                                  0.46, 0.45, 0.45, 0.44, 0.43, 0.42, 0.41, 0.41, 0.40, 0.40, 0.40, 0.40, 0.40, 0.40,
                                  0.40, 0.40, 0.40, 0.40, 0.41,
                                  0.41, 0.42, 0.42, 0.43, 0.43, 0.45, 0.46, 0.47, 0.49, 0.50, 0.51, 0.52, 0.56, 0.57,
                                  0.61]
        self.resLUIdict["RSR"] = [0.025, 0.026, 0.026, 0.028, 0.029, 0.030, 0.030, 0.032, 0.033, 0.036, 0.036, 0.039,
                                  0.039, 0.039,
                                  0.042, 0.042, 0.046, 0.046, 0.049, 0.052, 0.052, 0.055, 0.056, 0.059, 0.062, 0.062,
                                  0.065, 0.065, 0.070, 0.075,
                                  0.080, 0.080, 0.083, 0.085, 0.085, 0.090, 0.097, 0.104, 0.104, 0.104, 0.112, 0.115,
                                  0.115, 0.118, 0.127, 0.136,
                                  0.145, 0.145, 0.145, 0.150, 0.160]
        self.resLUIdict["OCR"] = [2.00, 1.90, 1.90, 1.80, 1.70, 1.70, 1.60, 1.60, 1.50, 1.50, 1.40, 1.40, 1.40, 1.30,
                                  1.30, 1.20, 1.20, 1.20,
                                  1.10, 1.10, 1.10, 1.00, 1.00, 0.99, 0.96, 0.93, 0.90, 0.87, 0.84, 0.82, 0.79, 0.77,
                                  0.74, 0.72, 0.70, 0.68, 0.66, 0.64,
                                  0.62, 0.60, 0.58, 0.57, 0.56, 0.54, 0.52, 0.50, 0.49, 0.47, 0.46, 0.45, 0.44]
        self.resLUIdict["TCR"] = [2.20, 2.10, 2.10, 2.00, 1.90, 1.90, 1.80, 1.80, 1.70, 1.70, 1.60, 1.60, 1.50, 1.50,
                                  1.50, 1.40, 1.40, 1.30,
                                  1.30, 1.30, 1.20, 1.20, 1.20, 1.10, 1.10, 1.10, 1.00, 1.00, 0.99, 0.96, 0.83, 0.90,
                                  0.85, 0.85, 0.83, 0.81, 0.79, 0.77,
                                  0.75, 0.73, 0.71, 0.69, 0.67, 0.65, 0.63, 0.61, 0.60, 0.58, 0.56, 0.55, 0.54]

        # NON-RESIDENTIAL PARAMETERS
        # (includes Trade, Office/Rescom, Light Industry, Heavy Industry, Education, Health & Comm, Serv & Util)
        # Commercial & Industrial Zones :: Employment Details
        self.create_parameter("employment_mode", STRING, "How should the employment be calculated?")
        self.create_parameter("ind_edist", DOUBLE, "Suggest the industrial employment distribution in employees/ha")
        self.create_parameter("com_edist", DOUBLE, "Suggests the commercial employment distribution in employees/ha")
        self.create_parameter("orc_edist", DOUBLE, "Suggests the office employment distribution")
        self.create_parameter("employment_total", DOUBLE, "")
        self.employment_mode = "D"  # I = input, D = distribution, S = single
        self.ind_edist = float(100.0)  # used only in employment mode D
        self.com_edist = float(100.0)  # used only in employment mode D
        self.orc_edist = float(400.0)  # used only in employment mode D
        self.employment_total = float(200.0)  # used only in employment mode S

        self.create_parameter("ind_subd_min", DOUBLE, "")
        self.create_parameter("ind_subd_max", DOUBLE, "")
        self.create_parameter("com_subd_min", DOUBLE, "")
        self.create_parameter("com_subd_max", DOUBLE, "")
        self.create_parameter("nres_minfsetback", DOUBLE, "")
        self.create_parameter("nres_setback_auto", BOOL, "")
        self.ind_subd_min = float(4.0)
        self.ind_subd_max = float(6.0)
        self.com_subd_min = float(2.0)
        self.com_subd_max = float(4.0)
        self.nres_minfsetback = float(2.0)
        self.nres_setback_auto = 0

        self.create_parameter("maxplotratio_ind", DOUBLE, "")
        self.create_parameter("maxplotratio_com", DOUBLE, "")
        self.create_parameter("nres_maxfloors", DOUBLE, "")
        self.create_parameter("nres_nolimit_floors", BOOL, "")
        self.maxplotratio_ind = float(60.0)
        self.maxplotratio_com = float(50.0)
        self.nres_maxfloors = float(4.0)
        self.nres_nolimit_floors = 0

        self.create_parameter("carpark_Wmin", DOUBLE, "")
        self.create_parameter("carpark_Dmin", DOUBLE, "")
        self.create_parameter("carpark_imp", DOUBLE, "")
        self.create_parameter("carpark_ind", DOUBLE, "")
        self.create_parameter("carpark_com", DOUBLE, "")
        self.create_parameter("loadingbay_A", DOUBLE, "")
        self.carpark_Wmin = float(2.6)
        self.carpark_Dmin = float(4.6)
        self.carpark_imp = float(100.0)
        self.carpark_ind = float(1.0)
        self.carpark_com = float(2.0)
        self.loadingbay_A = float(27.0)

        self.create_parameter("lscape_hsbalance", DOUBLE, "")
        self.create_parameter("lscape_impdced", DOUBLE, "")
        self.lscape_hsbalance = 1
        self.lscape_impdced = float(10.0)

        self.create_parameter("nres_fpwmin", DOUBLE, "")
        self.create_parameter("nres_nswmin", DOUBLE, "")
        self.create_parameter("nres_fpwmax", DOUBLE, "")
        self.create_parameter("nres_nswmax", DOUBLE, "")
        self.create_parameter("nres_fpmed", BOOL, "")
        self.create_parameter("nres_nsmed", BOOL, "")
        self.create_parameter("nres_lanemin", DOUBLE, "")
        self.create_parameter("nres_lanemax", DOUBLE, "")
        self.create_parameter("nres_lanemed", DOUBLE, "")
        self.nres_fpwmin = 1.0
        self.nres_nswmin = 1.0
        self.nres_fpwmax = 3.0
        self.nres_nswmax = 3.0
        self.nres_fpmed = 0
        self.nres_nsmed = 0
        self.nres_lanemin = 3.0
        self.nres_lanemax = 5.0
        self.nres_lanemed = 0

        # Civic Facilities
        self.create_parameter("civic_explicit", BOOL, "")
        self.create_parameter("civ_cemetery", BOOL, "")
        self.create_parameter("civ_cityhall", BOOL, "")
        self.create_parameter("civ_school", BOOL, "")
        self.create_parameter("civ_uni", BOOL, "")
        self.create_parameter("civ_lib", BOOL, "")
        self.create_parameter("civ_hospital", BOOL, "")
        self.create_parameter("civ_clinic", BOOL, "")
        self.create_parameter("civ_police", BOOL, "")
        self.create_parameter("civ_fire", BOOL, "")
        self.create_parameter("civ_jail", BOOL, "")
        self.create_parameter("civ_worship", BOOL, "")
        self.create_parameter("civ_leisure", BOOL, "")
        self.create_parameter("civ_museum", BOOL, "")
        self.create_parameter("civ_stadium", BOOL, "")
        self.create_parameter("civ_racing", BOOL, "")
        self.create_parameter("civ_zoo", BOOL, "")
        self.civic_explicit = 0
        self.civ_cemetery = 0
        self.civ_cityhall = 0
        self.civ_school = 0
        self.civ_uni = 0
        self.civ_lib = 0
        self.civ_hospital = 0
        self.civ_clinic = 0
        self.civ_police = 0
        self.civ_fire = 0
        self.civ_jail = 0
        self.civ_worship = 0
        self.civ_leisure = 0
        self.civ_museum = 0
        self.civ_zoo = 0
        self.civ_stadium = 0
        self.civ_racing = 0

        # Advanced Parameters
        self.nonres_far = {}
        self.nonres_far["LI"] = 70.0
        self.nonres_far["HI"] = 150.0
        self.nonres_far["COM"] = 220.0
        self.nonres_far["ORC"] = 110.0

        # TRANSPORT PARAMETERS
        self.create_parameter("ma_buffer", BOOL, "")
        self.create_parameter("ma_fpath", BOOL, "")
        self.create_parameter("ma_nstrip", BOOL, "")
        self.create_parameter("ma_sidestreet", BOOL, "")
        self.create_parameter("ma_bicycle", BOOL, "")
        self.create_parameter("ma_travellane", BOOL, "")
        self.create_parameter("ma_centralbuffer", BOOL, "")
        self.ma_buffer = 0
        self.ma_fpath = 1
        self.ma_nstrip = 1
        self.ma_sidestreet = 0
        self.ma_bicycle = 0
        self.ma_travellane = 1
        self.ma_centralbuffer = 1

        self.create_parameter("ma_buffer_wmin", DOUBLE, "")
        self.create_parameter("ma_buffer_wmax", DOUBLE, "")
        self.create_parameter("ma_fpath_wmin", DOUBLE, "")
        self.create_parameter("ma_fpath_wmax", DOUBLE, "")
        self.create_parameter("ma_nstrip_wmin", DOUBLE, "")
        self.create_parameter("ma_nstrip_wmax", DOUBLE, "")
        self.create_parameter("ma_sidestreet_wmin", DOUBLE, "")
        self.create_parameter("ma_sidestreet_wmax", DOUBLE, "")
        self.create_parameter("ma_bicycle_wmin", DOUBLE, "")
        self.create_parameter("ma_bicycle_wmax", DOUBLE, "")
        self.create_parameter("ma_travellane_wmin", DOUBLE, "")
        self.create_parameter("ma_travellane_wmax", DOUBLE, "")
        self.create_parameter("ma_centralbuffer_wmin", DOUBLE, "")
        self.create_parameter("ma_centralbuffer_wmax", DOUBLE, "")
        self.ma_buffer_wmin = 1.0
        self.ma_buffer_wmax = 1.0
        self.ma_fpath_wmin = 1.0
        self.ma_fpath_wmax = 3.0
        self.ma_nstrip_wmin = 1.0
        self.ma_nstrip_wmax = 2.0
        self.ma_sidestreet_wmin = 0.0
        self.ma_sidestreet_wmax = 0.0
        self.ma_bicycle_wmin = 0.0
        self.ma_bicycle_wmax = 0.0
        self.ma_travellane_wmin = 5.0
        self.ma_travellane_wmax = 10.0
        self.ma_centralbuffer_wmin = 2.0
        self.ma_centralbuffer_wmax = 5.0

        self.create_parameter("ma_buffer_median", BOOL, "")
        self.create_parameter("ma_fpath_median", BOOL, "")
        self.create_parameter("ma_nstrip_median", BOOL, "")
        self.create_parameter("ma_sidestreet_median", BOOL, "")
        self.create_parameter("ma_bicycle_median", BOOL, "")
        self.create_parameter("ma_travellane_median", BOOL, "")
        self.create_parameter("ma_centralbuffer_median", BOOL, "")
        self.ma_buffer_median = 0
        self.ma_fpath_median = 0
        self.ma_nstrip_median = 0
        self.ma_sidestreet_median = 0
        self.ma_bicycle_median = 0
        self.ma_travellane_median = 0
        self.ma_centralbuffer_median = 0

        self.create_parameter("ma_sidestreet_lanes", DOUBLE, "")
        self.create_parameter("ma_bicycle_lanes", DOUBLE, "")
        self.create_parameter("ma_bicycle_shared", BOOL, "")
        self.create_parameter("ma_travellane_lanes", DOUBLE, "")
        self.ma_sidestreet_lanes = 0
        self.ma_bicycle_lanes = 0
        self.ma_bicycle_shared = 0
        self.ma_travellane_lanes = 2

        self.create_parameter("pt_centralbuffer", BOOL, "")
        self.create_parameter("pt_impervious", DOUBLE, "")
        self.create_parameter("ma_median_reserved", BOOL, "")
        self.create_parameter("ma_openspacebuffer", BOOL, "")
        self.pt_centralbuffer = 0
        self.pt_impervious = 0
        self.ma_median_reserved = 0
        self.ma_openspacebuffer = 0

        self.create_parameter("hwy_different_check", BOOL, "")
        self.create_parameter("hwy_verge_check", BOOL, "")
        self.create_parameter("hwy_service_check", BOOL, "")
        self.create_parameter("hwy_travellane_check", BOOL, "")
        self.create_parameter("hwy_centralbuffer_check", BOOL, "")
        self.hwy_different_check = 0
        self.hwy_verge_check = 1
        self.hwy_service_check = 1
        self.hwy_travellane_check = 1
        self.hwy_centralbuffer_check = 1

        self.create_parameter("hwy_verge_wmin", DOUBLE, "")
        self.create_parameter("hwy_verge_wmax", DOUBLE, "")
        self.create_parameter("hwy_service_wmin", DOUBLE, "")
        self.create_parameter("hwy_service_wmax", DOUBLE, "")
        self.create_parameter("hwy_travellane_wmin", DOUBLE, "")
        self.create_parameter("hwy_travellane_wmax", DOUBLE, "")
        self.create_parameter("hwy_centralbuffer_wmin", DOUBLE, "")
        self.create_parameter("hwy_centralbuffer_wmax", DOUBLE, "")
        self.hwy_verge_wmin = 1.0
        self.hwy_verge_wmax = 3.0
        self.hwy_service_wmin = 1.0
        self.hwy_service_wmax = 1.0
        self.hwy_travellane_wmin = 5.0
        self.hwy_travellane_wmax = 10.0
        self.hwy_centralbuffer_wmin = 2.0
        self.hwy_centralbuffer_wmax = 5.0

        self.create_parameter("hwy_verge_median", BOOL, "")
        self.create_parameter("hwy_service_median", BOOL, "")
        self.create_parameter("hwy_travellane_median", BOOL, "")
        self.create_parameter("hwy_centralbuffer_median", BOOL, "")
        self.hwy_verge_median = 0
        self.hwy_service_median = 0
        self.hwy_travellane_median = 0
        self.hwy_centralbuffer_median = 0

        self.create_parameter("hwy_service_lanes", DOUBLE, "")
        self.create_parameter("hwy_travellane_lanes", DOUBLE, "")
        self.create_parameter("hwy_median_reserved", BOOL, "")
        self.create_parameter("hwy_openspacebuffer", BOOL, "")
        self.hwy_service_lanes = 1
        self.hwy_travellane_lanes = 3
        self.hwy_median_reserved = 0
        self.hwy_openspacebuffer = 0

        self.create_parameter("consider_transport", BOOL, "")
        self.create_parameter("trans_airport", BOOL, "")
        self.create_parameter("trans_seaport", BOOL, "")
        self.create_parameter("trans_busdepot", BOOL, "")
        self.create_parameter("trans_railterminal", BOOL, "")
        self.consider_transport = 0
        self.trans_airport = 0
        self.trans_seaport = 0
        self.trans_busdepot = 0
        self.trans_railterminal = 0

        # OPEN SPACE PARAMETERS
        # (includes Parks & Garden, Reserves & Floodways)
        # Parks, Squares & Gardens :: General
        self.create_parameter("pg_greengrey_ratio", DOUBLE, "")
        self.create_parameter("pg_nonrec_space", DOUBLE, "")
        self.create_parameter("pg_fac_restaurant", BOOL, "")
        self.create_parameter("pg_fac_fitness", BOOL, "")
        self.create_parameter("pg_fac_bbq", BOOL, "")
        self.create_parameter("pg_fac_sports", BOOL, "")
        self.pg_greengrey_ratio = float(10.0)
        self.pg_nonrec_space = float(40.0)  # % of space in park not used for anything else
        self.pg_fac_restaurant = 0
        self.pg_fac_fitness = 0
        self.pg_fac_bbq = 0
        self.pg_fac_sports = 0

        self.create_parameter("ref_usable", BOOL, "")
        self.create_parameter("ref_usable_percent", DOUBLE, "")
        self.create_parameter("svu_water", DOUBLE, "")
        self.create_parameter("svu4supply", BOOL, "")
        self.create_parameter("svu4waste", BOOL, "")
        self.create_parameter("svu4storm", BOOL, "")
        self.create_parameter("svu4supply_prop", DOUBLE, "")
        self.create_parameter("svu4waste_prop", DOUBLE, "")
        self.create_parameter("svu4storm_prop", DOUBLE, "")
        self.ref_usable = 1
        self.ref_usable_percent = float(100.0)
        self.svu_water = float(50.0)
        self.svu4supply = 1
        self.svu4waste = 1
        self.svu4storm = 1
        self.svu4supply_prop = float(30.0)
        self.svu4waste_prop = float(30.0)
        self.svu4storm_prop = float(40.0)

        # OTHER LAND USES
        # (includes Unclassified and Undeveloped)
        # Unclassified Land
        self.create_parameter("unc_merge", BOOL, "")
        self.create_parameter("unc_pgmerge", BOOL, "")
        self.create_parameter("unc_pgmerge_w", DOUBLE, "")
        self.create_parameter("unc_refmerge", BOOL, "")
        self.create_parameter("unc_refmerge_w", DOUBLE, "")
        self.create_parameter("unc_rdmerge", BOOL, "")
        self.create_parameter("unc_rdmerge_w", DOUBLE, "")
        self.create_parameter("unc_custom", BOOL, "")
        self.create_parameter("unc_customthresh", DOUBLE, "")
        self.create_parameter("unc_customimp", DOUBLE, "")
        self.create_parameter("unc_landirrigate", BOOL, "")
        self.unc_merge = 0  # Merge unclassified land?
        self.unc_pgmerge = 0
        self.unc_pgmerge_w = float(0.0)
        self.unc_refmerge = 0
        self.unc_refmerge_w = float(0.0)
        self.unc_rdmerge = 0
        self.unc_rdmerge_w = float(0.0)
        self.unc_custom = 0
        self.unc_customthresh = float(50.0)
        self.unc_customimp = float(50.0)
        self.unc_landirrigate = 0

        # Undeveloped Land
        self.create_parameter("und_state", STRING, "")
        self.create_parameter("und_type_manual", STRING, "")
        self.create_parameter("und_allowdev", BOOL, "")
        self.und_state = "M"  # M = manual, A = Auto
        self.und_type_manual = "GF"  # GF = Greenfield, BF = Brownfield, AG = Agriculture
        self.und_allowdev = 0  # Allow developent for large water infrastructure?

        # ADVANCED PARAMETERS
        self.und_BFtoGF = 50.0  # Threshold distance % between Brownfield and Greenfield
        self.und_BFtoAG = 90.0  # Threshold distance % between Brownfield and Agriculture
        self.undtypeDefault = "BF"
        self.considerGF = 1  # Even consider Greenfield?
        self.considerAG = 1  # Even consider Agriculture areas in model?
        self.CBD_MAD_dist = 10.0  # km - approximate distance between main CBD and major activity districts
        # ------------------------------------------
        # END OF INPUT PARAMETER LIST

    def run_module(self):
        """Runs the urban planning module simulation."""
        self.notify("Start Urban Planning!")

        # prev_map_attr = self.activesim.getAssetWithName("PrevMapAttributes")  # DYNAMICS [TO DO]

        map_attr = self.scenario.get_asset_with_name("MapAttributes")

        # SECTION 1 - Get all global map attributes and prepare parameters
        # 1.1 MAP ATTRIBUTES
        blocks_num = map_attr.get_attribute("NumBlocks")
        block_size = map_attr.get_attribute("BlockSize")    # size of blocks
        Atblock = block_size * block_size                   # Total area of one block

        # 1.2 PREPARE SAMPLING PARAMETERS RANGES
        # If parameter range median boxes were checked, adjust these parameters to reflect that
        # Residential/Non-residential setbacks and local streets
        setback_f = ubmethods.adjust_sample_range(self.setback_f_min, self.setback_f_max, self.setback_f_med)
        setback_s = ubmethods.adjust_sample_range(self.setback_s_min, self.setback_s_max, self.setback_s_med)
        res_fp = ubmethods.adjust_sample_range(self.res_fpwmin, self.res_fpwmax, self.res_fpmed)
        res_ns = ubmethods.adjust_sample_range(self.res_nswmin, self.res_nswmax, self.res_nsmed)
        res_lane = ubmethods.adjust_sample_range(self.res_lanemin, self.res_lanemax, self.res_lanemed)
        nres_fp = ubmethods.adjust_sample_range(self.nres_fpwmin, self.nres_fpwmax, self.nres_fpmed)
        nres_ns = ubmethods.adjust_sample_range(self.nres_nswmin, self.nres_nswmax, self.nres_nsmed)
        nres_lane = ubmethods.adjust_sample_range(self.nres_lanemin, self.nres_lanemax, self.nres_lanemed)

        # Major Arterials
        ma_buffer = ubmethods.adjust_sample_range(self.ma_buffer_wmin, self.ma_buffer_wmax, self.ma_buffer_median)
        ma_fpath = ubmethods.adjust_sample_range(self.ma_fpath_wmin, self.ma_fpath_wmax, self.ma_fpath_median)
        ma_nstrip = ubmethods.adjust_sample_range(self.ma_nstrip_wmin, self.ma_nstrip_wmax, self.ma_nstrip_median)
        ma_sidestreet = ubmethods.adjust_sample_range(self.ma_sidestreet_wmin, self.ma_sidestreet_wmax,
                                                      self.ma_sidestreet_median)
        ma_bicycle = ubmethods.adjust_sample_range(self.ma_bicycle_wmin, self.ma_bicycle_wmax, self.ma_bicycle_median)
        ma_travellane = ubmethods.adjust_sample_range(self.ma_travellane_wmin, self.ma_travellane_wmax,
                                                      self.ma_travellane_median)
        ma_centralbuffer = ubmethods.adjust_sample_range(self.ma_centralbuffer_wmin, self.ma_centralbuffer_wmax,
                                                         self.ma_centralbuffer_median)
        # Highways
        hwy_verge = ubmethods.adjust_sample_range(self.hwy_verge_wmin, self.hwy_verge_wmax, self.hwy_verge_median)
        hwy_service = ubmethods.adjust_sample_range(self.hwy_service_wmin, self.hwy_service_wmax,
                                                    self.hwy_service_median)
        hwy_travellane = ubmethods.adjust_sample_range(self.hwy_travellane_wmin, self.hwy_travellane_wmax,
                                                       self.hwy_travellane_median)
        hwy_centralbuffer = ubmethods.adjust_sample_range(self.hwy_centralbuffer_wmin, self.hwy_centralbuffer_wmax,
                                                          self.hwy_centralbuffer_median)

        self.notify("Begin Urban Planning!")
        blockslist = self.scenario.get_assets_with_identifier("BlockID")

        # SECTION 2 - LOOP ACROSS BLOCKS AND APPLY URBAN PLANNING RULES
        for i in range(len(blockslist)):
            # Initialize tally variables for the Block
            blk_tia = 0  # Total Block Impervious Area
            blk_roof = 0  # Total Block Roof Area
            blk_eia = 0  # Total Block effective impervious area
            blk_avspace = 0  # Total available space for decentralised water infrastructure

            currentAttList = blockslist[i]
            currentID = currentAttList.get_attribute("BlockID")

            self.notify("Now Developing BlockID" + str(currentID))

            # Skip Condition 1: Block is not active
            if currentAttList.get_attribute("Status") == 0:
                self.notify("BlockID"+str(currentID)+" is not active, moving to next ID")
                currentAttList.add_attribute("Blk_TIA", -9999)
                currentAttList.add_attribute("Blk_EIF", -9999)
                currentAttList.add_attribute("Blk_TIF", -9999)
                currentAttList.add_attribute("Blk_RoofsA", -9999)
                continue

            # Determine whether to update the Block at all using Dynamics Parameters
            # if int(prev_map_attr.getAttribute("Impl_cycle")) == 0:    #Is this implementation cycle?
            #     prevAttList = self.activesim.getAssetWithName("PrevID"+str(currentID))
            #     if self.keepBlockDataCheck(currentAttList, prevAttList):        #NO = check block for update
            #         self.notify("Changes in Block are below threshold levels, transferring data")
            #         self.transferBlockAttributes(currentAttList, prevAttList)
            #         continue        #If Block does not need to be developed, skip it
            # COPIED OVER FROM LEGACY VERSION [DYNAMICS TO DO]

            # Get Active Area
            activity = currentAttList.get_attribute("Active")
            Aactive = activity * Atblock

            # 2.1 - UNCLASSIFIED LAND ---------------------
            # Allocate unclassified area to the rest of the Block's LUC distribution
            A_unc = currentAttList.get_attribute("pLU_NA") * Aactive
            A_park = currentAttList.get_attribute("pLU_PG") * Aactive
            A_ref = currentAttList.get_attribute("pLU_REF") * Aactive
            A_rd = currentAttList.get_attribute("pLU_RD") * Aactive

            if A_unc != 0:      # If there is unclassified area in the Block, then....
                unc_area_subdivide = self.planUnclassified(A_unc, A_park, A_ref, A_rd, Atblock)
                undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = unc_area_subdivide
            else:       # Otherwise just set extra areas to zero
                undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = 0, 0, 0, 0, 0, 0, 0

            currentAttList.add_attribute("MiscAtot", otherarea)
            currentAttList.add_attribute("MiscAimp", otherimp)

            if self.unc_custom:     # Using a custom threshold?
                currentAttList.add_attribute("MiscThresh", self.unc_customthresh)
            else:
                currentAttList.add_attribute("MiscThresh", 999.9)   # If not, make unrealistically high

            blk_tia += otherimp     # Add areas to cumulative variables
            blk_eia += otherimp
            blk_roof += 0
            blk_avspace += 0

            # 2.2 - UNDEVELOPED LAND ---------------------
            # Determine the state of the area's undeveloped land if possible
            considerCBD = map_attr.get_attribute("considerCBD")
            A_und = currentAttList.get_attribute("pLU_UND") * Aactive + undevextra

            if A_und != 0:
                undtype = self.determine_undev_type(currentAttList, considerCBD)
            else:
                undtype = str("NA")     # If no undeveloped land

            currentAttList.add_attribute("UND_Type", undtype)
            currentAttList.add_attribute("UND_av", float(A_und*self.und_allowdev))

            blk_tia += 0            # Update cumulative variables
            blk_eia += 0
            blk_roof += 0
            blk_avspace += float(A_und*self.und_allowdev)

            # 2.3 - OPEN SPACES ---------------------
            A_park += pgextra       # Add the extra park and reserve areas from unclassified land
            A_ref += refextra
            A_svu = currentAttList.get_attribute("pLU_SVU") * Aactive

            # 2.3.1 - Parks & Gardens or Squares
            parkratio = float(self.pg_greengrey_ratio + 10.0) / 20.0
            sqratio = 1 - parkratio
            sqarea = A_park * sqratio
            greenarea = A_park * parkratio
            avail_space = greenarea * self.pg_nonrec_space / 100.0

            currentAttList.add_attribute("OpenSpace", A_park + A_ref)
            currentAttList.add_attribute("AGreenOS", greenarea)
            currentAttList.add_attribute("ASquare", sqarea)
            currentAttList.add_attribute("PG_av", avail_space)

            blk_tia += sqarea           # Update cumulative variables
            blk_eia += sqarea
            blk_roof += 0
            blk_avspace += avail_space

            # 2.3.2 - Reserves & Floodways
            avail_ref = A_ref * self.ref_usable_percent / 100.0
            currentAttList.add_attribute("REF_av", avail_ref)

            blk_tia += 0                # Update cumulative variables
            blk_eia += 0
            blk_roof += 0
            blk_avspace += avail_ref

            # 2.3.3 - Services & Utilities
            Asvu_water = float(A_svu) * float(self.svu_water) / 100.0
            Asvu_others = A_svu - Asvu_water

            svu_props = [self.svu4supply_prop * self.svu4supply,
                         self.svu4waste_prop * self.svu4waste,
                         self.svu4storm_prop * self.svu4storm]

            if sum(svu_props) > 100:
                # If for some reason the sums of percentages does not equal 100, normalize!
                svu_props = [svu/sum(svu_props) for svu in svu_props]
            else:
                svu_props = [svu / 100.0 for svu in svu_props]  # Otherwise just divide by 100

            currentAttList.add_attribute("ANonW_Util", Asvu_others)
            currentAttList.add_attribute("SVU_avWS", float(Asvu_water * svu_props[0]))
            currentAttList.add_attribute("SVU_avWW", float(Asvu_water * svu_props[1]))
            currentAttList.add_attribute("SVU_avSW", float(Asvu_water * svu_props[2]))
            currentAttList.add_attribute("SVU_avOTH", Asvu_water * (1.0 - sum(svu_props)))
            # Attributes includes available space (av) for water supply (WS), wastewater (WW), stormwater (SW) or
            # miscellaneous water-related applications (OTH)

            blk_tia += 0
            blk_eia += 0
            blk_roof += 0
            blk_avspace += Asvu_water

            # 2.4 - ROADS ---------------------
            A_rd += rdextra     # Add the extra road from unclassified land to total road area
            pass

            # 2.5 - RESIDENTIAL AREAS  ---------------------



            # 2.6 - NON-RESIDENTIAL AREAS  ---------------------


            # 2.7 - TALLY UP TOTAL LAND AREAS FOR GENERAL PROPERTIES  ---------------------



            # END OF BLOCK LOOP

        # Add new attributes to Map Attributes for later use
        map_attr.add_attribute("UndevAllow", self.und_allowdev)
        # map_attr.add_attribute("")  # All the road median restrictions

        self.notify("End of Urban Planning Module")
        print "DONE"

    def plan_unclassified(self, A_unc, A_park, A_ref, A_rd, Atblock):
        """ Proportions the unclassified area A_unc into other areas of land uses including parks,
        reserves, roads.

        :param A_unc: Area of unclassified land of the current block
        :param A_park: Area of park land of the current block
        :param A_ref: Area of reserve and floodway land of the current block
        :param A_rd: Area of road of the current block
        :param Atblock: Total area of the block active in the simulation.
        :return: list() containing extra undeveloped area, extra area for parks, reserves, roads, additional area
        and irrigation and impervious areas
        """
        pass

    def determine_undev_type(self, current_attributes, considerCBD):
        """ Determines the state of undeveloped land of the current block based on city centre distance.

        :param current_attributes: current UBVector() object with attributes
        :param considerCBD: boolean of 1 (yes CBD was considered) or 0 (no CBD was not considered).
        :return: a string corresponding to the type of undeveloped land."""
        pass




