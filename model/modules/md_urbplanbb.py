r"""
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
import random, math

# --- URBANBEATS LIBRARY IMPORTS ---
from .ubmodule import *
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
        self.min_allot_width = float(10.0)  # minimum width of an allotment = 10m if exceeded, then will build doubles
        self.res_parcel_W = 200.0   # Default width of a residential parcel
        self.res_parcel_D = 100.0   # Default depth of a residential parcel
        self.houseLUIthresh = [3.0, 5.4]  # house min and max threshold for LUI
        self.aptLUIthresh = [3.7, 6.5]  # walk-up apartment min and max threshold for LUI
        self.highLUIthresh = [5.9, 8.0]  # high-rise apartments min and max threshold for LUI
        self.resLUIdict = {}

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

        # GLOBAL PARAMETERS
        self.res_fp = []            # Frontage sampling ranges are used in residential
        self.res_ns = []            # and non-residential functions.
        self.res_lane = []
        self.setback_f = []
        self.setback_s = []
        self.nres_fp = []
        self.nres_ns = []
        self.nres_lane = []

    def run_module(self):
        """Runs the urban planning module simulation."""
        self.notify("Start Urban Planning!")

        # prev_map_attr = self.activesim.getAssetWithName("PrevMapAttributes")  # DYNAMICS [TO DO]

        map_attr = self.scenario.get_asset_with_name("MapAttributes")

        # MAIN RUN CONDITION: CHECK THAT ALL PRIOR DATA ARE INCLUDED
        truth_matrix = []
        truth_matrix.append(bool(map_attr.get_attribute("HasLUC")))
        truth_matrix.append(bool(map_attr.get_attribute("HasPOP")))
        if False in truth_matrix:
            map_attr.change_attribute("HasURBANFORM", 0)    # Change the condition for urban planning
            self.notify("Urban Planning Terminating Prematurely: Not enough data!")
            return  # Break the module pre-maturely

        # SECTION 1 - Get all global map attributes and prepare parameters
        # 1.1 MAP ATTRIBUTES
        block_size = map_attr.get_attribute("BlockSize")    # size of blocks
        Atblock = block_size * block_size                   # Total area of one block

        # 1.2 PREPARE SAMPLING PARAMETERS RANGES
        # If parameter range median boxes were checked, adjust these parameters to reflect that
        # Residential/Non-residential setbacks and local streets
        self.setback_f = ubmethods.adjust_sample_range(self.setback_f_min, self.setback_f_max, self.setback_f_med)
        self.setback_s = ubmethods.adjust_sample_range(self.setback_s_min, self.setback_s_max, self.setback_s_med)
        self.res_fp = ubmethods.adjust_sample_range(self.res_fpwmin, self.res_fpwmax, self.res_fpmed)
        self.res_ns = ubmethods.adjust_sample_range(self.res_nswmin, self.res_nswmax, self.res_nsmed)
        self.res_lane = ubmethods.adjust_sample_range(self.res_lanemin, self.res_lanemax, self.res_lanemed)
        self.nres_fp = ubmethods.adjust_sample_range(self.nres_fpwmin, self.nres_fpwmax, self.nres_fpmed)
        self.nres_ns = ubmethods.adjust_sample_range(self.nres_nswmin, self.nres_nswmax, self.nres_nsmed)
        self.nres_lane = ubmethods.adjust_sample_range(self.nres_lanemin, self.nres_lanemax, self.nres_lanemed)

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
        # Initialize residential planning dictionary
        self.initialize_lui_dictionary()

        self.notify("Begin Urban Planning!")
        blockslist = self.scenario.get_assets_with_identifier("BlockID")

        # SECTION 2 - LOOP ACROSS BLOCKS AND APPLY URBAN PLANNING RULES
        for i in range(len(blockslist)):
            # Initialize tally variables for the Block
            blk_tia = 0  # Total Block Impervious Area
            blk_roof = 0  # Total Block Roof Area
            blk_eia = 0  # Total Block effective impervious area
            blk_avspace = 0  # Total available space for decentralised water infrastructure

            block_attr = blockslist[i]
            currentID = block_attr.get_attribute("BlockID")

            self.notify("Now Developing BlockID" + str(currentID))

            # Skip Condition 1: Block is not active
            if block_attr.get_attribute("Status") == 0:
                # block_attr.add_attribute("TOTALjobs", 0)
                # block_attr.add_attribute("Blk_TIA", -9999)      # Default no-data value
                # block_attr.add_attribute("Blk_EIF", -9999)
                # block_attr.add_attribute("Blk_TIF", -9999)
                # block_attr.add_attribute("Blk_RoofsA", -9999)
                continue

            if block_attr.get_attribute("Active") == 0:
                self.notify("BlockID" + str(currentID) + " is not active, moving to next ID")
                block_attr.change_attribute("Status", 0)
                block_attr.add_attribute("TOTALjobs", 0)
                block_attr.add_attribute("Blk_TIA", -9999)  # Default no-data value
                block_attr.add_attribute("Blk_EIF", -9999)
                block_attr.add_attribute("Blk_TIF", -9999)
                block_attr.add_attribute("Blk_RoofsA", -9999)
                nhd = block_attr.get_attribute("Neighbours")
                for n in nhd:
                    ubmethods.remove_neighbour_from_block(self.scenario.get_asset_with_name("BlockID"+str(n)),
                                                          currentID)
                continue

            # Determine whether to update the Block at all using Dynamics Parameters
            # if int(prev_map_attr.getAttribute("Impl_cycle")) == 0:    #Is this implementation cycle?
            #     prevAttList = self.activesim.getAssetWithName("PrevID"+str(currentID))
            #     if self.keepBlockDataCheck(block_attr, prevAttList):        #NO = check block for update
            #         self.notify("Changes in Block are below threshold levels, transferring data")
            #         self.transferBlockAttributes(block_attr, prevAttList)
            #         continue        #If Block does not need to be developed, skip it
            # COPIED OVER FROM LEGACY VERSION [DYNAMICS TO DO]

            # Get Active Area
            activity = block_attr.get_attribute("Active")
            Aactive = activity * Atblock

            # 2.1 - UNCLASSIFIED LAND ---------------------
            # Allocate unclassified area to the rest of the Block's LUC distribution
            A_unc = block_attr.get_attribute("pLU_NA") * Aactive
            A_park = block_attr.get_attribute("pLU_PG") * Aactive
            A_ref = block_attr.get_attribute("pLU_REF") * Aactive
            A_rd = block_attr.get_attribute("pLU_RD") * Aactive

            if A_unc != 0:      # If there is unclassified area in the Block, then....
                unc_area_subdivide = self.plan_unclassified(A_unc, A_park, A_ref, A_rd, Atblock)
                undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = unc_area_subdivide
            else:       # Otherwise just set extra areas to zero
                undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = 0, 0, 0, 0, 0, 0, 0

            block_attr.add_attribute("MiscAtot", otherarea)
            block_attr.add_attribute("MiscAimp", otherimp)
            block_attr.add_attribute("MiscAirr", irrigateextra)

            if self.unc_custom:     # Using a custom threshold?
                block_attr.add_attribute("MiscThresh", self.unc_customthresh)
            else:
                block_attr.add_attribute("MiscThresh", 999.9)   # If not, make unrealistically high

            blk_tia += otherimp     # Add areas to cumulative variables
            blk_eia += otherimp
            blk_roof += 0
            blk_avspace += 0

            # 2.2 - UNDEVELOPED LAND ---------------------
            # Determine the state of the area's undeveloped land if possible
            considerCBD = map_attr.get_attribute("considerCBD")
            A_und = block_attr.get_attribute("pLU_UND") * Aactive + undevextra

            if A_und != 0:
                undtype = self.determine_undev_type(block_attr, considerCBD)
            else:
                undtype = str("NA")     # If no undeveloped land

            block_attr.add_attribute("UND_Type", undtype)
            block_attr.add_attribute("UND_av", float(A_und*self.und_allowdev))

            blk_tia += 0            # Update cumulative variables
            blk_eia += 0
            blk_roof += 0
            blk_avspace += float(A_und*self.und_allowdev)

            # 2.3 - OPEN SPACES ---------------------
            A_park += pgextra       # Add the extra park and reserve areas from unclassified land
            A_ref += refextra
            A_svu = block_attr.get_attribute("pLU_SVU") * Aactive

            # 2.3.1 - Parks & Gardens or Squares
            parkratio = float(self.pg_greengrey_ratio + 10.0) / 20.0
            sqratio = 1 - parkratio
            sqarea = A_park * sqratio
            greenarea = A_park * parkratio
            avail_space = greenarea * self.pg_nonrec_space / 100.0

            block_attr.add_attribute("OpenSpace", A_park + A_ref)
            block_attr.add_attribute("AGreenOS", greenarea)
            block_attr.add_attribute("ASquare", sqarea)
            block_attr.add_attribute("PG_av", avail_space)

            blk_tia += sqarea           # Update cumulative variables
            blk_eia += sqarea
            blk_roof += 0
            blk_avspace += avail_space

            # [TO DO] There are parameters for different park facilities, include this in future.

            # 2.3.2 - Reserves & Floodways
            avail_ref = A_ref * self.ref_usable_percent / 100.0
            block_attr.add_attribute("REF_av", avail_ref)

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

            block_attr.add_attribute("ANonW_Util", Asvu_others)
            block_attr.add_attribute("SVU_avWS", float(Asvu_water * svu_props[0]))
            block_attr.add_attribute("SVU_avWW", float(Asvu_water * svu_props[1]))
            block_attr.add_attribute("SVU_avSW", float(Asvu_water * svu_props[2]))
            block_attr.add_attribute("SVU_avOTH", Asvu_water * (1.0 - sum(svu_props)))
            # Attributes includes available space (av) for water supply (WS), wastewater (WW), stormwater (SW) or
            # miscellaneous water-related applications (OTH)

            blk_tia += 0
            blk_eia += 0
            blk_roof += 0
            blk_avspace += Asvu_water

            # 2.4 - ROADS ---------------------
            A_rd += rdextra     # Add the extra road from unclassified land to total road area

            # [TO DO] Work out proportion of roads in each Block and use this to determine area proportion for
            # Major arterials and highway typologies

            # MAJOR ARTERIALS
            # Buffer - sample and multiply by the boolean
            rd_buffer = round(random.uniform(float(ma_buffer[0]), float(ma_buffer[1])), 1) * int(self.ma_buffer)

            # Footpath - sample and multiply by the boolean
            rd_fpath = round(random.uniform(float(ma_fpath[0]), float(ma_fpath[1])), 1) * int(self.ma_fpath)

            # Nature strip - sample and multiply by the boolean
            rd_nstrip = round(random.uniform(float(ma_nstrip[0]), float(ma_nstrip[1])), 1) * int(self.ma_nstrip)

            # Side street - sample and multiply by the boolean and the number of lanes
            rd_sidestreet = round(random.uniform(float(ma_sidestreet[0]), float(ma_sidestreet[1])), 1) * \
                            int(self.ma_sidestreet) * self.ma_sidestreet_lanes

            # Bicycle lanes - sample and multiply by the boolean and the number of lanes
            rd_bicycle = round(random.uniform(float(ma_bicycle[0]), float(ma_bicycle[1])), 1) * \
                         int(self.ma_bicycle) * self.ma_bicycle_lanes

            # Determine the total width of bicycle and sidestreet lanes
            if self.ma_bicycle_shared:      # If the bicycle and side street share the same space...
                rd_street_edge = max(rd_sidestreet, rd_bicycle)     # The larger of the two
            else:                           # else...
                rd_street_edge = rd_sidestreet + rd_bicycle         # The sum of the two

            # Travel Lane - sample and multiply by boolean and number of lanes
            rd_travellane = round(random.uniform(float(ma_travellane[0]), float(ma_travellane[1])), 1) * \
                            int(self.ma_travellane) * self.ma_travellane_lanes

            # Central Buffer - sample and multiply by boolean
            rd_centralbuff = round(random.uniform(float(ma_centralbuffer[0]), float(ma_centralbuffer[1])), 1) * \
                             int(self.ma_centralbuffer)

            arterial_imp = [rd_fpath, rd_street_edge, rd_travellane]
            arterial_perv = [rd_buffer, rd_nstrip]

            if self.pt_centralbuffer:       # Is there at-grade public transport in the central buffer?
                arterial_imp.append(self.pt_impervious / 100.0 * rd_centralbuff)
                arterial_perv.append((1 - self.pt_impervious / 100.0) * rd_centralbuff)

            # Incorporate open spaces as buffers
            park_buffer = 0     # By default: Use the buffer area defined for the roads
            if self.ma_openspacebuffer:
                if (A_park + A_ref) >= 0.5 * A_rd:      # if total open space is greater than half the road area
                    # Then the rd_buffer parameter is set to zero because the parks are used instead
                    park_buffer = 1
                    arterial_perv[0] = 0

            total_width = (sum(arterial_imp) + sum(arterial_perv)) * 2.0
            Aimp_rd = float(sum(arterial_imp) * 2.0 / total_width) * A_rd

            if self.ma_median_reserved:
                av_spRD = float(sum(arterial_perv[:len(arterial_perv)-1]) * 2.0 / total_width) * A_rd
            else:
                av_spRD = float(sum(arterial_perv) * 2.0 / total_width) * A_rd

            # HIGHWAYS AND FREEWAYS [TO DO]

            block_attr.add_attribute("RoadTIA", Aimp_rd)
            block_attr.add_attribute("ParkBuffer", park_buffer)
            block_attr.add_attribute("RD_av", av_spRD)

            # Add to cumulative area variables
            blk_tia += Aimp_rd
            blk_eia += Aimp_rd
            blk_roof += 0
            blk_avspace += av_spRD

            # 2.5 - RESIDENTIAL AREAS  ---------------------
            map_attr.add_attribute("AvgOccup", self.occup_avg)      # Used in later modules! Needs a baseline
            ResPop = block_attr.get_attribute("Population")          # Retrieve population count
            A_res = block_attr.get_attribute("pLU_RES") * Aactive    # Retrieve active area
            minHouse = self.person_space * self.occup_avg * 4       # Work out the minimum house size
            if A_res >= minHouse and ResPop > self.occup_flat_avg:
                resdict = self.build_residential(block_attr, map_attr, A_res)

                # Transfer res_dict attributes to output vector
                block_attr.add_attribute("HasRes", 1)

                if resdict["TypeHouse"] == 1:
                    block_attr.add_attribute("HasHouses", 1)
                    block_attr.add_attribute("ResARoad", resdict["Aroad"])
                    block_attr.add_attribute("ResANstrip", resdict["Anstrip"])
                    block_attr.add_attribute("ResAFpath", resdict["Afpath"])
                    block_attr.add_attribute("HouseOccup", resdict["HouseOccup"])
                    block_attr.add_attribute("ResParcels", resdict["ResParcels"])
                    block_attr.add_attribute("ResFrontT", resdict["TotalFrontage"])
                    block_attr.add_attribute("avSt_RES", resdict["avSt_RES"])
                    block_attr.add_attribute("WResNstrip", resdict["WResNstrip"])
                    block_attr.add_attribute("ResAllots", resdict["ResAllots"])
                    block_attr.add_attribute("ResDWpLot", resdict["ResDWpLot"])
                    block_attr.add_attribute("ResHouses", resdict["ResHouses"])
                    block_attr.add_attribute("ResLotArea", resdict["ResLotArea"])
                    block_attr.add_attribute("ResRoof", resdict["ResRoof"])
                    block_attr.add_attribute("avLt_RES", resdict["avLt_RES"])
                    block_attr.add_attribute("ResHFloors", resdict["ResHFloors"])
                    block_attr.add_attribute("ResLotTIA", resdict["ResLotTIA"])
                    block_attr.add_attribute("ResLotEIA", resdict["ResLotEIA"])
                    block_attr.add_attribute("ResGarden", resdict["ResGarden"])
                    block_attr.add_attribute("ResRoofCon", resdict["ResRoofCon"])
                    block_attr.add_attribute("ResLotALS", resdict["ResLotALS"])
                    block_attr.add_attribute("ResLotARS", resdict["ResLotARS"])

                    if resdict["TotalFrontage"] == 0:
                        frontageTIF = 0
                    else:
                        frontageTIF = 1 - (resdict["avSt_RES"] / resdict["TotalFrontage"])

                    # Add to cumulative area variables
                    blk_tia += (resdict["ResLotTIA"] * resdict["ResAllots"]) + \
                               frontageTIF * resdict["TotalFrontage"]
                    blk_eia += (resdict["ResLotEIA"] * resdict["ResAllots"]) + \
                               0.9 * frontageTIF * resdict["TotalFrontage"]
                    blk_roof += (resdict["ResRoof"] * resdict["ResAllots"])
                    blk_avspace += (resdict["avLt_RES"] * resdict["ResAllots"]) + resdict["avSt_RES"]

                if resdict["TypeApt"] == 1:
                    block_attr.add_attribute("HasFlats", 1)
                    block_attr.add_attribute("avSt_RES", 0)
                    block_attr.add_attribute("HDRFlats", resdict["HDRFlats"])
                    block_attr.add_attribute("HDRRoofA", resdict["HDRRoofA"])
                    block_attr.add_attribute("HDROccup", resdict["HDROccup"])
                    block_attr.add_attribute("HDR_TIA", resdict["HDR_TIA"])
                    block_attr.add_attribute("HDR_EIA", resdict["HDR_EIA"])
                    block_attr.add_attribute("HDRFloors", resdict["HDRFloors"])
                    block_attr.add_attribute("av_HDRes", resdict["av_HDRes"])
                    block_attr.add_attribute("HDRGarden", resdict["HDRGarden"])
                    block_attr.add_attribute("HDRCarPark", resdict["HDRCarPark"])

                    # Add to cumulative area variables
                    blk_tia += resdict["HDR_TIA"]
                    blk_eia += resdict["HDR_EIA"]
                    blk_roof += resdict["HDRRoofA"]
                    blk_avspace += resdict["av_HDRes"]

            else:
                block_attr.add_attribute("HasRes", 1)       # There IS residential space,BUT
                block_attr.add_attribute("HasHouses", 0)    # No houses
                block_attr.add_attribute("HasFlats", 0)     # No flats
                block_attr.add_attribute("avSt_RES", A_res)  # becomes street-scape area available

                # Add to cumulative area variables
                blk_tia += 0
                blk_eia += 0
                blk_roof += 0
                blk_avspace += A_res

            # 2.6 - NON-RESIDENTIAL AREAS  ---------------------
            A_civ = block_attr.get_attribute("pLU_CIV") * Aactive
            A_tr = block_attr.get_attribute("pLU_TR") * Aactive
            extraCom = 0  # Additional commercial land area (if facilities are not to be considered)
            extraInd = 0  # Additional industrial land area (and if specific facilities are not selected)

            A_li = block_attr.get_attribute("pLU_LI") * Aactive + extraInd + Asvu_others
            A_hi = block_attr.get_attribute("pLU_HI") * Aactive
            A_com = block_attr.get_attribute("pLU_COM") * Aactive + extraCom
            A_orc = block_attr.get_attribute("pLU_ORC") * Aactive

            # Sample frontage information and create vector to store this
            Wfp = round(random.uniform(float(self.nres_fp[0]), float(self.nres_fp[1])), 1)
            Wns = round(random.uniform(float(self.nres_ns[0]), float(self.nres_ns[1])), 1)
            Wrd = round(random.uniform(float(self.nres_lane[0]), float(self.nres_lane[1])), 1)
            frontage = [Wfp, Wns, Wrd]

            totalblockemployed = 0

            if A_li != 0:
                indLI_dict = self.build_nonres_area(block_attr, map_attr, A_li, "LI", frontage)
                if indLI_dict["Has_LI"] == 1:
                    block_attr.add_attribute("Has_LI", 1)
                    # Transfer attributes from indLI dictionary
                    block_attr.add_attribute("LIjobs", indLI_dict["TotalBlockEmployed"])
                    block_attr.add_attribute("LIestates", indLI_dict["Estates"])
                    block_attr.add_attribute("LIAeRoad", indLI_dict["Aroad"])
                    block_attr.add_attribute("LIAeNstrip", indLI_dict["Anstrip"])
                    block_attr.add_attribute("LIAeFpath", indLI_dict["Afpath"])
                    block_attr.add_attribute("LIAestate", indLI_dict["Aestate"])
                    block_attr.add_attribute("avSt_LI", indLI_dict["av_St"])
                    block_attr.add_attribute("LIAfront", indLI_dict["Afrontage"])
                    block_attr.add_attribute("LIAfrEIA", indLI_dict["FrontageEIA"])
                    block_attr.add_attribute("LIAestate", indLI_dict["Aestate"])
                    block_attr.add_attribute("LIAeBldg", indLI_dict["EstateBuildingArea"])
                    block_attr.add_attribute("LIFloors", indLI_dict["Floors"])
                    block_attr.add_attribute("LIAeLoad", indLI_dict["Outdoorloadbay"])
                    block_attr.add_attribute("LIAeCPark", indLI_dict["Outdoorcarpark"])  # TOTAL OUTDOOR VISIBLE CARPARK
                    block_attr.add_attribute("avLt_LI", indLI_dict["EstateGreenArea"])
                    block_attr.add_attribute("LIAeLgrey", indLI_dict["Alandscape"] - indLI_dict["EstateGreenArea"])
                    block_attr.add_attribute("LIAeEIA", indLI_dict["EstateEffectiveImpervious"])
                    block_attr.add_attribute("LIAeTIA", indLI_dict["EstateImperviousArea"])

                    # Add to cumulative area variables
                    totalblockemployed += indLI_dict["TotalBlockEmployed"]
                    blk_tia += indLI_dict["Estates"] * (indLI_dict["EstateImperviousArea"] + indLI_dict["FrontageEIA"])
                    blk_eia += indLI_dict["Estates"] * (
                                indLI_dict["EstateEffectiveImpervious"] + 0.9 * indLI_dict["FrontageEIA"])
                    blk_roof += indLI_dict["Estates"] * indLI_dict["EstateBuildingArea"]
                    blk_avspace += indLI_dict["Estates"] * (indLI_dict["EstateGreenArea"] + indLI_dict["av_St"])

            if A_hi != 0:
                indHI_dict = self.build_nonres_area(block_attr, map_attr, A_hi, "HI", frontage)
                if indHI_dict["Has_HI"] == 1:
                    block_attr.add_attribute("Has_HI", 1)
                    # Transfer attributes from indHI dictionary
                    block_attr.add_attribute("HIjobs", indHI_dict["TotalBlockEmployed"])
                    block_attr.add_attribute("HIestates", indHI_dict["Estates"])
                    block_attr.add_attribute("HIAeRoad", indHI_dict["Aroad"])
                    block_attr.add_attribute("HIAeNstrip", indHI_dict["Anstrip"])
                    block_attr.add_attribute("HIAeFpath", indHI_dict["Afpath"])
                    block_attr.add_attribute("HIAestate", indHI_dict["Aestate"])
                    block_attr.add_attribute("avSt_HI", indHI_dict["av_St"])
                    block_attr.add_attribute("HIAfront", indHI_dict["Afrontage"])
                    block_attr.add_attribute("HIAfrEIA", indHI_dict["FrontageEIA"])
                    block_attr.add_attribute("HIAestate", indHI_dict["Aestate"])
                    block_attr.add_attribute("HIAeBldg", indHI_dict["EstateBuildingArea"])
                    block_attr.add_attribute("HIFloors", indHI_dict["Floors"])
                    block_attr.add_attribute("HIAeLoad", indHI_dict["Outdoorloadbay"])
                    block_attr.add_attribute("HIAeCPark", indHI_dict["Outdoorcarpark"])  # TOTAL OUTDOOR VISIBLE CARPARK
                    block_attr.add_attribute("avLt_HI", indHI_dict["EstateGreenArea"])
                    block_attr.add_attribute("HIAeLgrey", indHI_dict["Alandscape"] - indHI_dict["EstateGreenArea"])
                    block_attr.add_attribute("HIAeEIA", indHI_dict["EstateEffectiveImpervious"])
                    block_attr.add_attribute("HIAeTIA", indHI_dict["EstateImperviousArea"])

                    # Add to cumulative area variables
                    totalblockemployed += indHI_dict["TotalBlockEmployed"]
                    blk_tia += indHI_dict["Estates"] * (indHI_dict["EstateImperviousArea"] + indHI_dict["FrontageEIA"])
                    blk_eia += indHI_dict["Estates"] * (
                                indHI_dict["EstateEffectiveImpervious"] + 0.9 * indHI_dict["FrontageEIA"])
                    blk_roof += indHI_dict["Estates"] * indHI_dict["EstateBuildingArea"]
                    blk_avspace += indHI_dict["Estates"] * (indHI_dict["EstateGreenArea"] + indHI_dict["av_St"])

            if A_com != 0:
                com_dict = self.build_nonres_area(block_attr, map_attr, A_com, "COM", frontage)
                if com_dict["Has_COM"] == 1:
                    block_attr.add_attribute("Has_COM", 1)
                    # Transfer attributes from COM dictionary
                    block_attr.add_attribute("COMjobs", com_dict["TotalBlockEmployed"])
                    block_attr.add_attribute("COMestates", com_dict["Estates"])
                    block_attr.add_attribute("COMAeRoad", com_dict["Aroad"])
                    block_attr.add_attribute("COMAeNstrip", com_dict["Anstrip"])
                    block_attr.add_attribute("COMAeFpath", com_dict["Afpath"])
                    block_attr.add_attribute("COMAestate", com_dict["Aestate"])
                    block_attr.add_attribute("avSt_COM", com_dict["av_St"])
                    block_attr.add_attribute("COMAfront", com_dict["Afrontage"])
                    block_attr.add_attribute("COMAfrEIA", com_dict["FrontageEIA"])
                    block_attr.add_attribute("COMAestate", com_dict["Aestate"])
                    block_attr.add_attribute("COMAeBldg", com_dict["EstateBuildingArea"])
                    block_attr.add_attribute("COMFloors", com_dict["Floors"])
                    block_attr.add_attribute("COMAeLoad", com_dict["Outdoorloadbay"])
                    block_attr.add_attribute("COMAeCPark", com_dict["Outdoorcarpark"])  # TOTAL OUTDOOR VISIBLE CARPARK
                    block_attr.add_attribute("avLt_COM", com_dict["EstateGreenArea"])
                    block_attr.add_attribute("COMAeLgrey", com_dict["Alandscape"] - com_dict["EstateGreenArea"])
                    block_attr.add_attribute("COMAeEIA", com_dict["EstateEffectiveImpervious"])
                    block_attr.add_attribute("COMAeTIA", com_dict["EstateImperviousArea"])

                    # Add to cumulative area variables
                    totalblockemployed += com_dict["TotalBlockEmployed"]
                    blk_tia += com_dict["Estates"] * (com_dict["EstateImperviousArea"] + com_dict["FrontageEIA"])
                    blk_eia += com_dict["Estates"] * (
                                com_dict["EstateEffectiveImpervious"] + 0.9 * com_dict["FrontageEIA"])
                    blk_roof += com_dict["Estates"] * com_dict["EstateBuildingArea"]
                    blk_avspace += com_dict["Estates"] * (com_dict["EstateGreenArea"] + com_dict["av_St"])

            if A_orc != 0:
                orc_dict = self.build_nonres_area(block_attr, map_attr, A_orc, "ORC", frontage)
                if orc_dict["Has_ORC"] == 1:
                    block_attr.add_attribute("Has_ORC", 1)
                    # Transfer attributes from Offices dictionary
                    block_attr.add_attribute("ORCjobs", orc_dict["TotalBlockEmployed"])
                    block_attr.add_attribute("ORCestates", orc_dict["Estates"])
                    block_attr.add_attribute("ORCAeRoad", orc_dict["Aroad"])
                    block_attr.add_attribute("ORCAeNstrip", orc_dict["Anstrip"])
                    block_attr.add_attribute("ORCAeFpath", orc_dict["Afpath"])
                    block_attr.add_attribute("ORCAestate", orc_dict["Aestate"])
                    block_attr.add_attribute("avSt_ORC", orc_dict["av_St"])
                    block_attr.add_attribute("ORCAfront", orc_dict["Afrontage"])
                    block_attr.add_attribute("ORCAfrEIA", orc_dict["FrontageEIA"])
                    block_attr.add_attribute("ORCAestate", orc_dict["Aestate"])
                    block_attr.add_attribute("ORCAeBldg", orc_dict["EstateBuildingArea"])
                    block_attr.add_attribute("ORCFloors", orc_dict["Floors"])
                    block_attr.add_attribute("ORCAeLoad", orc_dict["Outdoorloadbay"])
                    block_attr.add_attribute("ORCAeCPark", orc_dict["Outdoorcarpark"])  # TOTAL OUTDOOR VISIBLE CARPARK
                    block_attr.add_attribute("avLt_ORC", orc_dict["EstateGreenArea"])
                    block_attr.add_attribute("ORCAeLgrey", orc_dict["Alandscape"] - orc_dict["EstateGreenArea"])
                    block_attr.add_attribute("ORCAeEIA", orc_dict["EstateEffectiveImpervious"])
                    block_attr.add_attribute("ORCAeTIA", orc_dict["EstateImperviousArea"])

                    # Add to cumulative area variables
                    totalblockemployed += orc_dict["TotalBlockEmployed"]
                    blk_tia += orc_dict["Estates"] * (orc_dict["EstateImperviousArea"] + orc_dict["FrontageEIA"])
                    blk_eia += orc_dict["Estates"] * (
                                orc_dict["EstateEffectiveImpervious"] + 0.9 * orc_dict["FrontageEIA"])
                    blk_roof += orc_dict["Estates"] * orc_dict["EstateBuildingArea"]
                    blk_avspace += orc_dict["Estates"] * (orc_dict["EstateGreenArea"] + orc_dict["av_St"])

            # 2.7 - TALLY UP TOTAL LAND AREAS FOR GENERAL PROPERTIES  ---------------------
            block_attr.change_attribute("TOTALjobs", totalblockemployed)
            block_attr.add_attribute("Blk_TIA", blk_tia)
            block_attr.add_attribute("Blk_EIA", blk_eia)

            blk_eif = blk_eia / Aactive
            block_attr.add_attribute("Blk_EIF", blk_eif)

            blk_tif = blk_tia / Aactive
            block_attr.add_attribute("Blk_TIF", blk_tif)

            block_attr.add_attribute("Blk_RoofsA", blk_roof)
            # END OF BLOCK LOOP

        # Add new attributes to Map Attributes for later use
        map_attr.add_attribute("UndevAllow", self.und_allowdev)
        # map_attr.add_attribute("")  # All the road median restrictions

        self.notify("End of Urban Planning Module")

    # MODULE SUB-FUNCTIONS -----------------
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
        # Check whether threshold exceeded
        if self.unc_customthresh and A_unc >= (Atblock*self.unc_customthresh/100.0):  # CASE 1: Treat land as its own
            unc_Aimp = A_unc * self.unc_customimp / 100.0
            unc_Aperv = A_unc - unc_Aimp
            if self.unc_landirrigate:
                irrigateextra = unc_Aperv   # Add area to public irrigation requirements if user says so
            else:
                irrigateextra = 0

            otherarea = A_unc
            otherimp = unc_Aimp
            undevextra, pgextra, refextra, rdextra = 0, 0, 0, 0    # Set all other types of areas to zero
        elif self.unc_merge and (A_park + A_ref + A_rd) > 0:
            weights = [self.unc_pgmerge * float(self.unc_pgmerge_w) * bool(A_park > 0),
                       self.unc_refmerge * float(self.unc_refmerge_w) * bool(A_ref > 0),
                       self.unc_rdmerge * float(self.unc_rdmerge_w) * bool(A_rd > 0)]

            if sum(weights) == 0:       # Proportion the land based on the weights if there are weights
                undevextra = A_unc
                otherarea, otherimp, pgextra, refextra, rdextra, irrigateextra = 0, 0, 0, 0, 0, 0
            else:
                finaldiv = []
                for i in weights:
                    # Tally up division of areas
                    finaldiv.append(A_unc * i/sum(weights))
                pgextra = finaldiv[0]
                refextra = finaldiv[1]
                rdextra = finaldiv[2]
                undevextra, otherarea, otherimp, irrigateextra = 0, 0, 0, 0
        else:
            undevextra = A_unc
            pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = 0, 0, 0, 0, 0, 0

        return [undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra]

    def determine_undev_type(self, current_attributes, considerCBD):
        """ Determines the state of undeveloped land of the current block based on city centre distance.

        :param current_attributes: current UBVector() object with attributes
        :param considerCBD: boolean of 1 (yes CBD was considered) or 0 (no CBD was not considered).
        :return: a string corresponding to the type of undeveloped land."""

        # DEVELOPER'S NOTE: [TO DO] I want to revise this algorithm because it may not apply in other cases. This will
        # be on the future to do list.

        if self.und_state == "M":       # If the user manually determined this...
            return self.und_type_manual
        elif considerCBD == 0:          # If the CBD was not considered, then sprawl distance cannot be calculated
            return self.undtypeDefault
        else:                           # Otherwise, figure out based on CBD location
            distCBD = current_attributes.get_attribute("CBDdist")/1000   #convert to km

            if self.cityarchetype == "MC":       #Monocentric City Case
                BFdist = float(self.und_BFtoGF)/100 * float(self.citysprawl)  #from 0 to BFdist --> BF
                GFdist = float(self.und_BFtoAG)/100 * float(self.citysprawl)  #from BFdist to GFdist --> GF
                                                                              #>GFdist --> AG
            else:       #Polycentric City Case - MAD = Main Activity District (10km), CBD = Central Business District
                MAD_sprawl = self.citysprawl - self.CBD_MAD_dist
                BFdist = self.CBD_MAD_dist + MAD_sprawl*self.und_BFtoGF/100
                GFdist = self.CBD_MAD_dist + MAD_sprawl*self.und_BFtoAG/100

            if distCBD <= BFdist:       #Brownfield
                undtype = "BF"
            elif distCBD <= GFdist and self.considerGF: #Greenfield
                undtype = "GF"
            elif distCBD > GFdist and self.considerAG:  #Agriculture
                undtype = "AG"
            elif distCBD > GFdist and self.considerGF:  #Greenfield because AG not considered
                undtype = "GF"
            else:
                undtype = "BF"  #Brownfield because GF and AG not considered
        return undtype

    def build_residential(self, block_attr, map_attr, A_res):
        """Builds residential urban form - either houses or apartments depending on the
        density of the population on the land available.

        :param block_attr: the UBVector() containing all Block attributes of the current block
        :param map_attr: the global map attributes UBVector()
        :param A_res: The area of residentail land to build on
        :return: a dictionary containing all residential parameters for that block.
        """
        # Step 1 - Determine Typology
        popBlock = block_attr.get_attribute("Population")
        Afloor = self.person_space * popBlock
        farblock = Afloor / A_res  # Calculate FAR
        # self.notify( "FARBlock"+str( farblock ))

        blockratios = self.retrieve_residential_ratios(farblock)     # Get planning ratios
        restype = self.retrieve_res_type(blockratios[0])

        if restype[0] == "HighRise":    # If we are dealing with high-rise apartments, recalculate stuff
            hdr_person_space = float(self.flat_area_max) / float(self.occup_flat_avg)
            Afloor = hdr_person_space * popBlock
            farblock = Afloor / A_res
            blockratios = self.retrieve_residential_ratios(farblock)
            restype = self.retrieve_res_type(blockratios[0])

        if "House" in restype:  # Design houses by default
            resdict = self.design_residential_houses(A_res, popBlock)
            resdict["TypeApt"] = 0
        elif "Apartment" in restype or "HighRise" in restype:  # Design apartments
            resdict = self.design_residential_apartments(block_attr, map_attr, A_res, popBlock, blockratios, Afloor)
            resdict["TypeHouse"] = 0
        else:
            resdict = {}
        return resdict

    def design_residential_houses(self, A_res, pop):
        """All necessary urban planning calculations for residential dwellings urban form.

        :param A_res: area of residential land use
        :param pop: population to accommodate
        :return: a dictionary object containing all relevant parameters."""
        resdict = dict()
        resdict["TypeHouse"] = 1

        # Sample parameters from specified ranges
        occupmin = self.occup_flat_avg      # Absolute min taken as that for an apartment. House should have more
        occupmax = self.occup_max           # Absolute max

        occup = 0  # initialize to enter the loop
        while occup < occupmin or occup > occupmax or occup == 0:
            occup = random.normalvariate(self.occup_avg, self.occup_avg / 10)
        self.notify("Block occupancy: " + str(occup))

        resdict["HouseOccup"] = occup

        Wfp = round(random.uniform(float(self.res_fp[0]), float(self.res_fp[1])), 1)
        Wns = round(random.uniform(float(self.res_ns[0]), float(self.res_ns[1])), 1)
        Wrd = round(random.uniform(float(self.res_lane[0]), float(self.res_lane[1])), 1)
        Wfrontage = Wfp + Wns + Wrd

        # Step 2: Subdivide Area
        Ndwunits = float(int((((pop / occup) / 2.0) + 1))) * 2.0    # make even, /2, + 1, truncate, x2
        district_L = A_res / self.res_parcel_D      # default typology depth = 100m
        parcels = max(float(int(district_L / self.res_parcel_W)), 1.0)      # default typology width = 200m
        Wparcel = district_L / parcels
        Aparcel = Wparcel * self.res_parcel_D  # Area of one parcel
        Afrontage = (district_L * Wfrontage * 2) + ((parcels * 2) * Wfrontage * (self.res_parcel_D - 2 * Wfrontage))
        Afpath = Afrontage * float(Wfp / Wfrontage)
        Anstrip = Afrontage * float(Wns / Wfrontage)
        Aroad = Afrontage - Afpath - Anstrip

        resdict["Afpath"] = Afpath          # For WHOLE district
        resdict["Anstrip"] = Anstrip        # For WHOLE district
        resdict["Aroad"] = Aroad            # For WHOLE district
        resdict["AvgParcel"] = Aparcel      # In general for the district

        Dlot = (self.res_parcel_D - 2 * Wfrontage) / 2.0  # Depth of one allotment
        Aca = A_res - Afrontage

        if Aca < self.min_allot_width * Dlot:  # Construction area should be large enough such that a single allotment
            # containing all buildings satisfies all width requirements.
            self.notify("Too much area taken up for frontage, removing frontage to clear up construction area!")
            Aca = A_res

            Afrontage = 0.00
            # Set the frontage equal to zero for this block, this will occur because areas are too small

            # Dlot = Aca/float(self.min_allot_width) #Constrain the depth to satisfy minimum width requirements
            Dlot = 40.0  # Constrain to 40m deep

            resdict["Afpath"] = 0.00        # For WHOLE district
            resdict["Anstrip"] = 0.00       # For WHOLE district
            resdict["Aroad"] = 0.00         # For WHOLE district

        AfrontagePerv = Afrontage * (float(Wns) / float(Wfrontage))

        resdict["ResParcels"] = parcels
        resdict["TotalFrontage"] = Afrontage
        resdict["avSt_RES"] = AfrontagePerv
        resdict["WResNstrip"] = Wns

        # Step 2b: Determine how many houses on one allotment based on advanced parameter "min Allotment Width"
        Wlot = 0.0
        DWperLot = 0.0
        Nallotments = 0.0
        while Wlot < self.min_allot_width:
            DWperLot += 1.0
            Nallotments = Ndwunits / DWperLot
            Alot = Aca / Nallotments
            Wlot = Alot / Dlot
            print(f"{Wlot}, {self.min_allot_width} dwellings per lot: {DWperLot}, {Ndwunits}, {Nallotments}, {Alot}")
            # self.notify(str(DWperLot)+str(Nallotments)+str(Alot)+str(Wlot))

        self.notify("For this block, we need " + str(DWperLot) + " dwellings on each allotment")

        resdict["ResAllots"] = Nallotments
        resdict["ResDWpLot"] = DWperLot
        resdict["ResHouses"] = Ndwunits

        fsetback = round(random.uniform(self.setback_f[0], self.setback_f[1]), 1)
        ssetback = round(random.uniform(self.setback_s[0], self.setback_s[1]), 1)

        # Step 3: Subdivide ONE Lot
        res_parking_area = self.carports_max * 2.6 * 4.9  # ADDITIONAL COVERAGE ON SITE
        if self.garage_incl:
            Agarage = res_parking_area
            Aparking = res_parking_area * 0.5
        else:
            Agarage = 0
            Aparking = res_parking_area

        if self.patio_covered:
            Acover = self.patio_area_max
            Apatio = 0
        else:
            Acover = 0
            Apatio = self.patio_area_max

        Alotfloor = DWperLot * (occup * self.person_space * (1.0 + self.extra_comm_area / 100.0) + Agarage + Acover)
        farlot = Alotfloor / Alot
        lotratios = self.retrieve_residential_ratios(farlot)
        Als = lotratios[3] * Alot
        Ars = lotratios[4] * Alot
        Apave = fsetback * self.w_driveway_min + Apatio + Aparking  # DRIVEWAY + PATIO + PARKING

        resdict["ResDriveway"] = fsetback * self.w_driveway_min

        # Determine if need more floors
        floors = 1
        Aba = Alotfloor
        while (Aba + Apave + Als) > Alot:
            # self.notify( "Need more than "+str(floors)+str(" floor(s)!"))
            floors += 1
            Aba = Alotfloor / floors

        # Retry #1 - Als set to Ars
        if floors > self.floor_num_max:
            Als = Ars  # set the remaining garden space to recreational space
            floors = 1  # Reset floors to 1
            Aba = Alotfloor  # Reset building area to equal Gross Floor Area
            while (Aba + Apave + Als) > Alot:  # Try again
                self.notify("Even with less garden, need more than " + str(floors) + str("floor(s)!"))
                floors += 1
                Aba = Alotfloor / floors

        # Retry #2 - fsetback becomes ssetback (i.e. reduces paved driveway area further)
        if floors > self.floor_num_max:
            Apave -= (fsetback - ssetback) * self.w_driveway_min
            # REDUCED DRIVEWAY + PATIO + either half of PARKING or NONE
            floors = 1
            Aba = Alotfloor
            while (Aba + Apave + Als) > Alot:
                self.notify("Even with less garden, less driveway, need more than " + str(floors) + str("floor(s)!"))
                floors += 1
                Aba = Alotfloor / floors

        # Retry #3 - Remove setback completely (i.e. can be compensated with external paving later)
        if floors > self.floor_num_max:
            Apave -= ssetback * self.w_driveway_min  # i.e. PATIO + Parking
            floors = 1
            Aba = Alotfloor
            while (Aba + Apave + Als) > Alot:
                self.notify("Even with less garden, no driveway, need more than " + str(floors) + str("floor(s)!"))
                floors += 1
                Aba = Alotfloor / floors

        # Retry #4 - Remove Carpark Paving
        if floors > self.floor_num_max:
            if Agarage == 0:
                Apave -= Aparking / 2.0  # DRIVEWAY + PATIO + half of PARKING since no garage!
            else:
                Apave -= Aparking  # DRIVEWAY + PATIO
            floors = 1
            Aba = Alotfloor
            while (Aba + Apave + Als) > Alot:
                self.notify("Even with less garden and less carpark paving and no driveway, need more than " + str(
                    floors) + "floor(s)!")
                floors += 1
                Aba = Alotfloor / floors

        # Last Resort - exceed floor limit
        if floors > self.floor_num_max:
            self.notify("Floor Limit Exceeded! Cannot plan within bounds, continuing!")
            pass

        Aba = Alotfloor / floors
        Dbuilding = Aba / (Wlot - 2 * ssetback)
        Apa = ssetback * Dbuilding * 2
        Apave = max(Apave, 0)  # Make sure paved area is non-negative!

        # WSUD SPACE = Lot area - Building - Recreation - Paving - Planning Req.
        av_LOT = max(Alot - Ars - Aba - Apave - Apa, 0)

        # Calculate Imperviousness, etc. write to residential dictionary
        resdict["ResLotArea"] = Alot
        resdict["ResRoof"] = Aba
        resdict["avLt_RES"] = av_LOT
        resdict["ResHFloors"] = floors
        resdict["Apaving"] = Apave

        # Determine Roof Connectivity
        roofconnect = self.roof_connected
        connectivity = ["Direct", "Disconnect"]
        if roofconnect == "Vary":
            roofconnect = connectivity[int(random.randint(0, 100) <= self.roof_dced_p)]
        if roofconnect == "Direct":
            AroofEff = Aba
        elif roofconnect == "Disconnect":
            AroofEff = 0

        resdict["ResRoofCon"] = roofconnect

        AimpLot = Aba + Apave
        AConnectedImp = (AroofEff + Apave) * (1.0 - float(self.imperv_prop_dced / 100))
        Agarden = max(Alot - AimpLot, 0)

        resdict["ResLotTIA"] = AimpLot
        resdict["ResLotEIA"] = AConnectedImp
        resdict["ResGarden"] = Agarden
        resdict["ResLotALS"] = Als
        resdict["ResLotARS"] = Ars
        return resdict

    def design_residential_apartments(self, block_attr, map_attr, A_res, pop, ratios, Afloor):
        """Lays out the specified residential area with high density apartments for a given population
        and ratios for the block. Algorithm works within floor constraints, but ignores these if the site
        cannot be laid out properly.
        """
        resdict = dict()
        resdict["TypeApt"] = 1

        # Step 2: Subdivide Area
        Apa = math.sqrt(A_res) * 2 * self.setback_HDR_avg + (
                    math.sqrt(A_res) - self.setback_HDR_avg) * 2 * self.setback_HDR_avg
        A_res_adj = A_res - Apa         # minus Planning Area Apa
        Aos = ratios[2] * A_res_adj     # min required open space area (outdoor + 1/2 indoor) (within A_res_adj)
        Als = ratios[3] * A_res_adj     # min required liveability space area (within Aos)
        Ars = ratios[4] * A_res_adj     # min required recreation space area (within Als)

        # Step 3: Work out N units and car parking + indoor/outdoor spaces
        Naptunits = float(int(pop / self.occup_flat_avg + 1))  # round up (using integer conversion/truncation)
        Ncparksmin = ratios[5] * Naptunits  # min required carparks, based on OCR (within Ncparksmax)
        Ncparksmax = ratios[6] * Naptunits  # max required carparks, based on TCR
        cpMin = Ncparksmin * 2.6 * 4.9
        cpMax = Ncparksmax * 2.6 * 4.9

        AextraIndoor = float(self.commspace_indoor) / 100 * Afloor
        AextraOutdoor = float(self.commspace_outdoor) / 100 * Afloor

        resdict["HDRFlats"] = Naptunits

        if AextraOutdoor < Aos:
            # self.notify( "User-defined Outdoor space requirements are less than minimum suggested, scaling down...")
            Aos = AextraOutdoor
            Als = AextraOutdoor * (Als / Aos)
            Ars = AextraOutdoor * (Ars / Aos)

        pPG = block_attr.get_attribute("pLU_PG")
        pactive = block_attr.get_attribute("Active")
        Ablock = map_attr.get_attribute("BlockSize") * map_attr.get_attribute("BlockSize")
        Apg = pPG * pactive * Ablock * float(int(self.park_OSR))

        # Step 4a: Work out Building Footprint using OSR
        Aoutdoor = max(Aos - 0.5 * AextraIndoor - Apg, 0)  # if indoor space is much greater, Aoutdoor becomes negative
        if Aoutdoor == 0:  # if there is no outdoor space, then ls and rs spaces on-site are zero
            Als_site = 0
            Ars_site = 0
        else:
            Als_site = Als
            Ars_site = Ars

        Aca = A_res_adj - Aoutdoor

        Nfloors = float(int(((Afloor + AextraIndoor) / Aca) + 1))
        if Nfloors < self.floor_num_HDRmax:
            # self.notify( "Try #1 - HDR residential design OK, floors not exceeded")

            # Step 5: Layout Urban Form
            Aba = (Afloor + AextraIndoor) / Nfloors
            Aouts = A_res - Apa - Aba
            Aon_rs = max(Ars_site - Apg, 0)
            av_RESHDR = max(Als_site - Aon_rs, 0)  # Available WSUD Space for residential district

            Aparking = self.calculate_parking_area(Aouts, Als_site, cpMin, cpMax)
            Aimp = Aba + Aparking
            Aeff = Aimp * float(1 - self.imperv_prop_dced / 100)
            Agarden = A_res - Aba - Aparking

            # Calculate Imperviousness, etc., write to residential dictionary
            resdict["HDRRoofA"] = Aba
            resdict["HDROccup"] = self.occup_flat_avg
            resdict["HDR_TIA"] = Aimp
            resdict["HDR_EIA"] = Aeff
            resdict["HDRFloors"] = Nfloors
            resdict["av_HDRes"] = av_RESHDR
            resdict["HDRGarden"] = Agarden
            resdict["HDRCarPark"] = Aparking
            return resdict
        else:
            pass
            # self.notify( "Exceeded floors, executing 2nd method" )

        # Step 4b: Work out Building Footprint using LSR
        Aoutdoor = max(Als - Apg, 0)
        if Aoutdoor == 0:
            Als_site = 0  # on-site
            Ars_site = 0  # on-site
        else:
            Als_site = Als
            Ars_site = Ars

        Aca = A_res_adj - Aoutdoor
        Nfloors = float(int(((Afloor + AextraIndoor) / Aca) + 1))
        if Nfloors < self.floor_num_HDRmax:
            # self.notify( "Try #2 - HDR residential design OK, floors not exceeded" )
            # Step 5: Layout Urban Form
            Aba = (Afloor + AextraIndoor) / Nfloors
            Aouts = A_res - Apa - Aba
            Aon_rs = max(Ars_site - Apg, 0)
            av_RESHDR = max(Als_site - Aon_rs, 0)  # Available WSUD Space for residential district

            Aparking = self.calculate_parking_area(Aouts, Als_site, cpMin, cpMax)
            Aimp = Aba + Aparking
            Aeff = Aimp * float(1 - self.imperv_prop_dced / 100.0)
            Agarden = A_res - Aba - Aparking

            # Calculate Imperviousness, etc., write to residential dictionary
            resdict["HDRRoofA"] = Aba
            resdict["HDROccup"] = self.occup_flat_avg
            resdict["HDR_TIA"] = Aimp
            resdict["HDR_EIA"] = Aeff
            resdict["HDRFloors"] = Nfloors
            resdict["av_HDRes"] = av_RESHDR
            resdict["HDRGarden"] = Agarden
            resdict["HDRCarPark"] = Aparking
            return resdict
        else:
            pass
            # self.notify( "Exceeded floors, executing 3rd method, ignoring floor limit" )

        # Step 4c: Work out Building Footprint using OSR, ignoring floor limit
        Aoutdoor = max(Aos - 0.5 * AextraIndoor - Apg, 0)
        if Aoutdoor == 0:
            Als_site = 0
            Ars_site = 0
        else:
            Als_site = Als
            Ars_site = Ars

        Aca = A_res_adj - Aoutdoor
        Nfloors = float(int(((Afloor + AextraIndoor) / Aca) + 1))
        # self.notify( "Try #3 - HDR average floors determined as: "+str(Nfloors))

        # Step 5: Layout Urban Form
        Aba = (Afloor + AextraIndoor) / Nfloors
        Aouts = A_res - Apa - Aba
        Aon_rs = max(Ars_site - Apg, 0)
        av_RESHDR = max(Als_site - Aon_rs, 0)

        Aparking = self.calculate_parking_area(Aouts, Als_site, cpMin, cpMax)
        Aimp = Aba + Aparking
        Aeff = Aimp * float(1 - self.imperv_prop_dced / 100)
        Agarden = A_res - Aba - Aparking

        # Calculate Imperviousness, etc., write to residential dictionary
        resdict["HDRRoofA"] = Aba
        resdict["HDROccup"] = self.occup_flat_avg
        resdict["HDR_TIA"] = Aimp
        resdict["HDR_EIA"] = Aeff
        resdict["HDRFloors"] = Nfloors
        resdict["av_HDRes"] = av_RESHDR
        resdict["HDRGarden"] = Agarden
        resdict["HDRCarPark"] = Aparking
        return resdict

    def calculate_parking_area(self, Aout, Alive, cpMin, cpMax):
        """Determines the total outdoor parking space on the HDR site based on OSR's remaining
        available space, using information about parking requirements, liveability space and
        inputs.

        :param Aout: Outdoor space = Land Area - PlanningArea - Building Area
        :param Alive: Liveability space on-site = LSR x LA or zero if all area is leveraged by park
        :param cpMin: minimum area required for car parks
        :param cpMax: maximum area required for car parks
        :return: Aparking - area of parking outside
        """
        if self.parking_HDR == "Vary":
            park_options = ["On", "Off", "Var"]
            choice = random.randint(0, 2)
            self.parking_HDR = park_options[choice]

        if self.parking_HDR == "On":
            avail_Parking = max(Aout - Alive, 0)
            if avail_Parking < cpMin:
                Aparking = avail_Parking
            elif avail_Parking < cpMax:
                Aparking = avail_Parking
            elif avail_Parking > cpMax:
                Aparking = avail_Parking - cpMax
        elif self.parking_HDR == "Off" or self.parking_HDR == "Var":
            Aparking = 0
        else:
            Aparking = 0
        return Aparking

    def retrieve_res_type(self, lui):
        """Retrieves the residence type for the specified lui, if the type is between two options, both are returned

        :param lui: input land use intensity
        :return: [Type1, Type2], if only one type, then Type2 = 0
        """
        if lui == -9999:
            return ["HighRise", 0]
        if lui < self.aptLUIthresh[0]:
            return ["House", 0]
        elif lui > self.aptLUIthresh[0] and lui < self.houseLUIthresh[1]:
            return ["House", "Apartment"]
        elif lui < self.aptLUIthresh[1] and lui > self.houseLUIthresh[1]:
            return ["Apartment", 0]
        elif lui > self.highLUIthresh[0] and lui < self.aptLUIthresh[1]:
            return ["Apartment", "HighRise"]
        elif lui < self.highLUIthresh[0] and lui > self.aptLUIthresh[1]:
            return ["HighRise", 0]
        else:
            return ["HighRise", 0]

    def retrieve_residential_ratios(self, far):
        """Retrieves the land use intensity (LUI) and other planning ratios from the lookup dictionary.

        :param far: the floor-area-ratio of the current Block.
        :return: a list containing [LUI, FAR, OSR, LSR, RSR, OCR, TCR]
        """
        # Lookup the dictionary based on the FAR input
        mindex = 0  # counter for while loop
        found = 0
        while mindex < len(self.resLUIdict["FAR"]):
            if far < self.resLUIdict["FAR"][mindex]:  # will want to take the higher FAR
                far = self.resLUIdict["FAR"][mindex]
                mindex = len(self.resLUIdict["FAR"])
                found = 1
            else:
                mindex += 1

        if found == 0:  # means that FAR > FAR[LUI8.0)
            return [-9999, far, 0, 0, 0, 0, 0]  # returns the -9999 not found case for LUI

        if found == 1:
            # get LUI and others
            dictindex = self.resLUIdict["FAR"].index(far)
            return [self.resLUIdict["LUI"][dictindex], far, self.resLUIdict["OSR"][dictindex],
                    self.resLUIdict["LSR"][dictindex], self.resLUIdict["RSR"][dictindex],
                    self.resLUIdict["OCR"][dictindex], self.resLUIdict["TCR"][dictindex]]

    def build_nonres_area(self, block_attr, map_attr, Aluc, type, frontage):
        """Function to build non-residential urban form (LI, HI, COM, ORC) based on the typology of estates and plot
        ratios and the provision of sufficient space for building, carparks, service/loading bay and landscaping.

        :param block_attr: The UBVector() object containing the current Block's attributes
        :param map_attr: The global Map Attributes UBVector() instance
        :param Aluc: Area of land use in question
        :param type: Type of the land use (LI, HI, COM, ORC)
        :param frontage: frontage parameters determined for current Block.
        :return: a dictionary containing non-residential attributes
        """
        nresdict = dict()
        # Note: Auto-setback
        # The formula to calculate auto-setback = H/2 + 1.5m based on Monash Council's Documents
        # This, however, relates more predominantly to facilities in close proximity to residential
        # neighbourhoods. As a means to an end, however, this formula can be used within reason here.
        # H will be taken as 3m and the formula is used only to building up to floors = 5 --> 9m setback
        # which corresponds to roughly the average setback value of commercial areas in the technology
        # precinct. The problem with using this is that the site is treated as a square. As a result,
        # the setback will only be applied on two faces of the site (since the site is expected to adjoin
        # other neighbouring sites. This is up for future revision.

        # Determine frontage info
        laneW = float(frontage[2])
        nstrip = float(frontage[1])
        fpath = float(frontage[0])
        Wfrontage = laneW + nstrip + fpath

        # STEP 1: Determine employment in the area
        employed = self.determine_employment(self.employment_mode, block_attr, map_attr, Aluc, type)
        nresdict["TotalBlockEmployed"] = employed

        # self.notify( "Employed + Dens"+str(employed))

        employmentDens = employed / (Aluc / 10000.0)  # Employment density [jobs/ha]

        # self.notify( employmentDens )

        # STEP 2: Subdivide the area and allocate employment
        if type == "LI" or type == "HI":
            blockthresh = round(random.uniform(self.ind_subd_min, self.ind_subd_max), 1)
        elif type == "ORC" or type == "COM":
            blockthresh = round(random.uniform(self.com_subd_min, self.com_subd_max), 1)

        estates = float(max(int(Aluc / (blockthresh * 10000.0)), 1))
        Aestate = Aluc / float(estates)
        Westate = math.sqrt(Aestate)
        Afrontage = Westate * Wfrontage + Wfrontage * (Westate - Wfrontage)
        Afpath = Afrontage * float(fpath / Wfrontage)
        Anstrip = Afrontage * float(nstrip / Wfrontage)
        Aroad = Afrontage - Afpath - Anstrip

        Aca = max(Aestate - Afrontage, 0)

        employed = employmentDens * (Aestate / 10000)

        nresdict["Afrontage"] = Afrontage
        nresdict["Afpath"] = Afpath
        nresdict["Anstrip"] = Anstrip
        nresdict["Aroad"] = Aroad
        nresdict["av_St"] = (nstrip / (laneW + nstrip + fpath)) * Afrontage
        nresdict["FrontageEIA"] = nresdict["Afrontage"] - nresdict["av_St"]
        nresdict["SiteArea"] = Aluc
        nresdict["Estates"] = estates
        nresdict["Aestate"] = Aestate
        nresdict["DevelopableArea"] = Aca
        nresdict["EstateEmployed"] = employed

        if Aca == 0:  # If the area is not substantial enough to build on, return an empty dictionary
            # self.notify( "Block's ", type, " area is not substantial enough to build on, not doing anything else"
            nresdict["Has_" + str(type)] = 0
            return nresdict
        nresdict["Has_" + str(type)] = 1

        # STEP 3: Determine building area, height, plot ratio balance for ONE estate
        Afloor = self.nonres_far[type] * employed  # Step 3a: Calculate total floor area

        if type == "LI" or type == "HI":  # Step 3b: Determine maximum building footprint
            Afootprintmax = float(self.maxplotratio_ind) / 100 * Aca
        elif type == "COM":
            Afootprintmax = float(self.maxplotratio_com) / 100 * Aca
        else:  # type = "ORC", plot ratio rules do not apply, but instead setback rules, taken on 2 faces
            Afootprintmax = Aca - 2.0 * math.sqrt(Aca) * max(
                float(self.nres_minfsetback) * float(not self.nres_setback_auto), 2.0)
            # Site area - (setback area, which is either minimum specified or 2meters if auto is enabled)
            # NOTE - need to go measure the setbacks for high-rise areas in the city just to make sure 2m is ok

        # self.notify( "Calculating Floors: "+str(Afloor)+", "+str(Afootprintmax)+", "+str(Afloor/Afootprintmax + 1 ))
        if Afootprintmax == 0:
            nresdict["Has_" + str(type)] = 0
            return nresdict

        num_floors = float(int(Afloor / Afootprintmax + 1))  # Step 3c: Calculate number of floors, either 1 or more

        # self.notify( "Num _Floors "+str(num_floors) )

        if num_floors <= self.nres_maxfloors or self.nres_nolimit_floors:
            # If floors do not exceed max or aren't of concern
            pass
            # self.notify( "Number of floors not exceeded, proceeding to lay out site")
            # We have Afloor calculated from start and the number of floors in num_floors rounded up
        elif type == "ORC":  # else if floors are exceeded, but the type is ORC then that's fine too
            pass
            # self.notify( "Number of floors exceeded but this is for High-rise offices in a major district")
            # We have Afloor calculated from start and the number of floors in num_floors rounded up
        else:
            # self.notify( "Number of floors exceeded, increasing building footprint"  )  # setback taken on two faces
            Afootprintmaxadj = max(
                Aca - 2.0 * math.sqrt(Aca) * max(self.nres_minfsetback * float(not (self.nres_setback_auto)), 2.0), 0)
            if Afootprintmaxadj != 0:
                num_floors = float(int(Afloor / Afootprintmaxadj + 1))
            else:
                num_floors = 0  # becomes zero if there is no building, treat the site as a yard
            if num_floors <= self.nres_maxfloors:
                pass
                # self.notify( "Newly adjusted building footprint is ok" )
                # We have Afloor and the adjusted num_floors
            else:
                # self.notify( "Even ignoring plot ratio, floors exceeded, readjusting employment density" )
                # Recalculate building footprint based on plot ratio and recalculate employees
                # Use maximum floors and maximum building size within limits of plot ratio
                num_floors = self.nres_maxfloors
                Afloor = Afootprintmax * num_floors  # total floor area is now building footself.notify( * max number of floors
                employednew = float(
                    int(Afloor / self.nonres_far[type] + 1))  # employed now calculated from new floor area
                employeddiscrepancy = employed - employednew
                self.notify("Site was adjusted for total employment: "+str(employeddiscrepancy)+" jobs were removed.")
                employed = employednew      # set new employed as the default employment

            # Tally up information
        # self.notify( "After num_floors: "+str(num_floors))

        # STEP 4: Lay out site and determine parking and loading bay requirements
        if num_floors == 0:
            Afootprintfinal = 0
        else:
            Afootprintfinal = Afloor / float(num_floors)

        nresdict["EstateBuildingArea"] = Afootprintfinal
        nresdict["Floors"] = float(num_floors)
        nresdict["TotalEstateFloorArea"] = Afloor

        # Progress: We have site area, building placed on site. Now we need to determine remaining area

        # Step 4a: Loading bay requirements
        Aloadingbay = Afloor / 100.0 * self.loadingbay_A

        # Step 4b: Car Parking requirements
        if type == "LI" or type == "HI":
            Acarpark = self.carpark_ind * employed * self.carpark_Wmin * self.carpark_Dmin
        elif type == "COM" or type == "ORC":
            Acarpark = self.carpark_com * Afloor / 100 * self.carpark_Wmin * self.carpark_Dmin

        # self.notify( "Car parking: "+str(Acarpark))

        nresdict["Aloadingbay"] = Aloadingbay
        nresdict["TotalAcarpark"] = Acarpark

        # Step 4c: Try to fit carpark and loading bay on-site, otherwise stack
        minsetback = max(not (self.nres_setback_auto) * self.nres_minfsetback,
                         (num_floors / 2 + 1.5) * self.nres_setback_auto * float(bool(num_floors <= 5)), 2.0)
        # setback determined as follows: if not automatic, uses the minimum specified, if automatic and below 5 floors,
        # uses the formula, if automatic but above 5 floors, uses 2m by default.

        setbackArea = math.sqrt(Aestate) * minsetback * 2 - minsetback * minsetback  # take setback area on two faces
        Asite_remain = Aca - Afootprintfinal - setbackArea
        if (Asite_remain - Acarpark - Aloadingbay) > 0:
            # Case 1: It all fits, hooray! --> Alandscape = setback area + remaining area
            Alandscape = (Asite_remain - Acarpark - Aloadingbay) + setbackArea
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorloadbay"] = Aloadingbay
            nresdict["Outdoorcarpark"] = Acarpark
        elif (Asite_remain - Aloadingbay) > 0:
            # Case 2: Loading bay fits, but carpark does not entirely --> that's ok, Alandscape = setback area
            Alandscape = setbackArea
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorloadbay"] = Aloadingbay
            nresdict["Outdoorcarpark"] = Asite_remain - Aloadingbay
        elif Asite_remain > 0:
            # Case 3: Loading bay does not fit --> use setback area to fit, Alandscape = remaining setback
            Aloadingbay = min(Aloadingbay, Asite_remain + setbackArea)  # remaining site area + setback area intrusion
            Alandscape = max(Asite_remain + setbackArea - Aloadingbay, 0)  # The rest of the area
            nresdict["Outdoorloadbay"] = Aloadingbay
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorcarpark"] = 0
        else:
            # Case 4: Loading bay does not fit even in setback area --> assume it is covered, no landscaping, but check
            # setback
            # self.notify( "WARNING, SETBACK AREA NOT PROVIDED" )
            revisedSetback = Aca - Afootprintfinal
            # self.notify( "Revised Setback: "+str(revisedSetback))
            Alandscape = max(revisedSetback, 0)
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorloadbay"] = 0
            nresdict["Outdoorcarpark"] = 0

        # STEP 5: Landscaping
        if self.lscape_hsbalance == -1:
            prop_Soft = 0
            prop_Hard = 1
        elif self.lscape_hsbalance == 1:
            prop_Soft = 1
            prop_Hard = 0
        else:
            prop_Soft = 0.5
            prop_Hard = 0.5

        Aimpaddition = prop_Hard * Alandscape
        Agreen = prop_Soft * Alandscape

        # Tally up all land surface cover information
        Aimp_total = Aca - Alandscape + Aimpaddition
        Aimp_connected = (1 - self.lscape_impdced / 100) * Aimp_total

        nresdict["EstateGreenArea"] = Agreen
        nresdict["EstateImperviousArea"] = Aimp_total
        nresdict["EstateEffectiveImpervious"] = Aimp_connected
        return nresdict

    def determine_employment(self, method, block_attr, map_attr, Aluc, type):
        """Determines the employment of the block based on the selected method. Calls
        some alternative functions for scaling or other aspects.

        :param method: The method selected by the user for determining employment
        :param block_attr: UBVector() instance of current Block attributes
        :param map_attr: UBVector() instance of global Map Attributes
        :param Aluc: Area of the land use
        :param type: type of the non-residential land use
        :return: The total employment for the Block's current non-res land use
        """
        if method == "I" and map_attr.get_attribute("include_employment") == 1:
            # Condition required to do this: there has to be data on employment input
            employed = block_attr.get_attribute("TOTALjobs")  # total employment for Block
            # Scale this value based on the hypothetical area and employee distribution

        elif method == "S":
            employed = 0  # Global employment/Total Non-res Built-up Area = block employed
            # Do something to tally up total employment and density for the map

        elif method == "D":
            if type == "LI" or type == "HI":
                employed = self.ind_edist * Aluc / 10000.0
            elif type == "COM":
                employed = self.com_edist * Aluc / 10000.0
            elif type == "ORC":
                employed = self.orc_edist * Aluc / 10000.0
            else:
                self.notify("Something's wrong here...")
        return employed

    def scale_employment(self, block_attr, employed, Aluc):
        pass
        # Scales the employed value down based on Aluc, used for "S" and "D" methods
        return employed

    def initialize_lui_dictionary(self):
        """Loads and initializes the LUI values for residential development. These are contained in the
        project's ancillary folder. The data is saved to the global variable self.resLUIdict."""
        f = open(self.activesim.get_program_rootpath()+"/ancillary/reslui.cfg", 'r')

        # ratio tables for residential district planning (from Time-Saver Standards)
        data = []
        for lines in f:                     # Transfer the data
            data.append((lines.replace("\n", "")).split(","))
        f.close()
        cols = data[0]      # Grab the keys for the dictionary from the first column
        for k in cols:
            self.resLUIdict[str(k)] = []

        data.pop(0)     # Remove the first column
        for i in range(len(data)):       # Now scan all lines and transfer data to dictionary
            for c in range(len(cols)):
                self.resLUIdict[str(cols[c])].append(float(data[i][c]))  # The i-th row and c-th column
        return True
