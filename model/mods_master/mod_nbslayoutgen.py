r"""
@file  mod_nbslayoutgen.py
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
import datetime as dt
import pandas as pd

class NbSLayoutGeneration(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "NbS Planning and Design"
    catorder = 3
    longname = "NbS Scheme Generation"
    icon = ":/icons/nbs_layout.png"

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

        # Service Level Settings
        self.create_parameter("runoff_service", DOUBLE, "Service level for runoff objective")
        self.create_parameter("wq_service", DOUBLE, "Service level for pollution maangement service")
        self.create_parameter("rec_service", DOUBLE, "Service level for stormwater harvesting service")
        self.create_parameter("service_luc", BOOL, "Apply services levels to specific land use types?")
        self.create_parameter("service_res", BOOL, "Residential dwellings")
        self.create_parameter("service_hdr", BOOL, "High-density residential")
        self.create_parameter("service_com", BOOL, "Commercial land use")
        self.create_parameter("service_li", BOOL, "Light industry service")
        self.create_parameter("service_hi", BOOL, "Heavy industry service")
        self.create_parameter("redundancy", DOUBLE, "Allowable level of service redundancy [%]")
        self.runoff_service = 30.0
        self.wq_service = 80.0
        self.rec_service = 30.0
        self.service_luc = 0
        self.service_res = 1
        self.service_hdr = 1
        self.service_com = 0
        self.service_li = 0
        self.service_hi = 0
        self.redundancy = 25.0

        self.create_parameter("search_method", STRING, "Search method for the Monte Carlo")
        self.create_parameter("maxiter", DOUBLE, "Maximum number of Monte Carlo Iterations")
        self.create_parameter("numstrats", DOUBLE, "Final number of strategies to select")
        self.create_parameter("selectstrat", STRING, "Selection strategy for options")
        self.create_parameter("selectmethod", STRING, "Ranking/Selection method")
        self.search_method = "UNTARGET"     # UNTARGET = for loop, # TARGET = while loop
        self.maxiter = 1000
        self.numstrats = 10
        self.selectstrat = "TOP"    # TOP = top-scoring options, RAND = probability weighted random
        self.selectmethod = "RANK"  # RANK = ranking top options, CONF = confidence interval based

        # EVALUATION TAB
        self.create_parameter("scalepref", BOOL, "Assign a scale preference?")
        self.create_parameter("scaleweight", DOUBLE, "Weighting of scales solutions")
        self.create_parameter("techpref", BOOL, "Assign a technology preference?")
        self.create_parameter("techprefmatrixfile", STRING, "The MCA matrix file")
        self.create_parameter("techprefmatrixdef", BOOL, "Use UrbanBEATS' default MCA matrix")
        self.create_parameter("tech_incl", BOOL, "Include technical criteria")
        self.create_parameter("env_incl", BOOL, "Include environmental criteria")
        self.create_parameter("econ_incl", BOOL, "Include economic criteria")
        self.create_parameter("soc_incl", BOOL, "Include social criteria")
        self.create_parameter("tech_w", DOUBLE, "Weighting for technical criteria")
        self.create_parameter("env_w", DOUBLE, "Weighting for environmental criteria")
        self.create_parameter("econ_w", DOUBLE, "Weighting for economic criteria")
        self.create_parameter("soc_w", DOUBLE, "Weighting for socail criteria")
        self.scalepref = 0
        self.scaleweight = 2    # [1,3] 1= lot, 3 = end of pipe
        self.techpref = 0
        self.techprefmatrixfile = "(load custom matrix)"
        self.techprefmatrixdef = 1
        self.tech_incl = 1
        self.env_incl = 1
        self.econ_incl = 1
        self.soc_incl = 1
        self.tech_w = 2
        self.env_w = 2
        self.econ_w = 2
        self.soc_w = 2

        self.create_parameter("scoringstrat", STRING, "Scoring method")
        self.create_parameter("scoringmethod", STRING, "Method of tallying scores,e.g., weighted-sum")
        self.create_parameter("includestoch", BOOL, "Include stochastic noise?")
        self.create_parameter("multifunction_bonus", DOUBLE, "Multi-functionality bonus?")
        self.scoringstrat = "NP"   # NP = service-based no penalty, LP = linear penalty, EP = exponential penalty
        self.scoringmethod = "WSM"  # WSM = weighted-sum, WPM = weighted-product
        self.includestoch = 0
        self.multifunction_bonus = 10.0

        # ADVANCED PARAMETERS
        self.griditems = []
        self.nbsdf = None

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")
            return False

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
            return False

        # PRE-REQUISITES CHECK - need to have a few modules run and a database exist
        if self.meta.get_attribute("mod_nbsdesigntoolbox") != 1:
            self.notify("Cannot start module! No data on possible nature-based solutions generated!")
            return False

        # CLEAN THE ATTRIBUTES LIST
        att_schema = {

        }

        grid_assets = self.assets.get_assets_with_identifier(self.assetident)
        att_reset_count = 0
        for i in range(len(grid_assets)):
            for att in att_schema.keys():
                if grid_assets[i].remove_attribute(att):
                    att_reset_count += 1
        self.notify("Removed "+str(att_reset_count)+" attribute entries")
        # Also need to remove the asset collection NBS Shapefile layouts

        # INITIALIZE THE ATTRIBUTES LIST
        for i in range(len(grid_assets)):
            for att in att_schema.keys():
                grid_assets[i].add_attribute(att, att_schema[att])

        self.meta.add_attribute("mod_nbslayoutgen", 1)
        self.meta.add_attribute("mod_dt_nbslayoutgen", str(dt.datetime.now().isoformat().split(".")[0]))  # Last run
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

        self.notify("Generating NbS Layouts for the Simulation Grid")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 0 - GRAB ASSET INFORMATION AND NBS DATABASE ---
        self.griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets making up the case study area: "+str(len(self.griditems)))
        total_assets = len(self.griditems)
        progress_counter = 0

        projectpath = self.activesim.get_project_path()
        self.nbsdf = pd.read_pickle(projectpath+"/collections/"+self.assetcolname+"_NbS_tbox.udb")
        print(self.nbsdf.head(10))
        self.notify("A total of "+str(self.nbsdf.shape[0])+" NbS designs identified across case study")

        self.notify_progress(10)

        # --- SECTION 1 - Construct In-Block Options first
        for i in range(len(self.griditems)):
            curasset = self.griditems[i]
            # cursys = self.nbsdf[]


        # --- SECTION 2 - Monte Carlo Loop



        # --- SECTION 3 - Filtering of solutions and export of Top Ranks


        self.notify("NbS Layout Generation Complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass