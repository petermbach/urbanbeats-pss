# -*- coding: utf-8 -*-
"""
@file   urbanbeatscore.py
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
import time
import os
import sys


# --- URBANBEATS LIBRARY IMPORTS ---
import modules.md_decisionanalysis
import modules.md_climatesetup
import modules.md_delinblocks
import modules.md_impactassess
import modules.md_perfassess
import modules.md_regulation
import modules.md_socioecon
import modules.md_spatialmapping
import modules.md_techplacement
import modules.md_urbandev
import modules.md_urbplanbb


# --- URBANBEATS SIMULATION CLASS DEFINITION ---
class UrbanBeatsSim(threading.Thread):
    """The simulation class for UrbanBEATS, which contains all the information
    about scenarios, models, and other items. Contains the project info, reference
    to all modules, simulation settings and status of the current workflow.
    """
    def __init__(self, rootpath, options):
        """Initialization for the class allowing the model to set up the simulation
        and required modules.

        :param rootpath: the root path of the UrbanBEATS Model containing the ancillary folder
        :param options: a dictionary of global options. The core of the model uses only several of these options including
                        ["maxiterations"] ...
        """
        threading.Thread.__init__(self)

        # Initialize variables
        self.__rootpath = rootpath          # the root path for UrbanBEATS' runtime
        self.__global_options = options     # global model options

        #Initialize paths
        self.emptyBlockPath = self.__rootpath+"/ancillary/emptyblockmap.shp"
        self.emptySysPath = self.__rootpath+"/ancillary/emptysystemmap.shp"

        #Observer, Status and Filename
        self.__observers = []   # Observers of the current simulation

        self.__project_saved = 0    # BOOL - has the project been saved?
        self.__simulation_completed = 0 # BOOL - has the simulation completed run?
        self.__projectpath = "" # Project Path. Starts blank, is then replaced.

        # Project Parameters
        self.__project_info = {
            "name": "<enter name>",
            "date": "",
            "region": "",
            "city": self.__global_options["city"],
            "modeller": self.__global_options["defaultmodeller"],
            "affiliation": self.__global_options["defaultaffil"],
            "otherpersons": "<none>",
            "synopsis": "<no synopsis>",
            "boundaryshp": "<none>",
            "logstyle": self.__global_options["projectlogstyle"],
            "projectpath": self.__global_options["defaultpath"],
            "keepcopy": 0
        }

        self.__datalibrary = None   # initialize the data library
        self.__projectlog = None    # initialize the project log
        self.__scenarios = []       # initialize the scenarios

    # INITIALIZATION METHODS
    def initialize_simulation(self):
        """Performs a full initialization of the project simulation, creates
        a folder for holding relevant data and results.

        :return: None
        """
        pass

    # PROJECT PARAMETER SETTINGS


    # SCENARIO MANAGEMENT
    def add_new_scenario(self, params):
        pass

    def delete_scenario(self, name):
        pass

    # GETTERS AND SETTERS
    def get_project_parameter(self, parname):
        """Get project info either as a whole dictionary or based on individual
        attributes.

        :parname attribute: specific attribute of the project info dictionary, if
                "ALL" is specified, method returns entire dictionary.
        :return: dictionary entry or entire dictionary self.__project_info
        """
        if parname == "ALL":
            return self.__project_info
        try:
            return self.__project_info[parname]
        except KeyError:
            return None

    def set_project_parameter(self, parname, value):
        self.__project_info[parname] = value

    def get_project_path(self):
        """Returns the path of the current project.

        :return: self.__projectpath as string
        """
        return self.__projectpath

    def set_project_path(self):
        """Sets the active project directory."""
        self.__projectpath = self.get_project_parameter("projectpath")

    def get_global_options(self, attribute):
        """Get the global options for the model. If a specific attribute is specified
        then method returns that particular attribute instead.

        :param attribute: specific attribute of option in the dictionary. If
                "ALL" is specified, returns whole dictionary instead.
        :return: self.__global_options or a specific entry of this dictionary.
        """
        if attribute == "ALL":
            return self.__global_options
        else:
            try:
                return self.__global_options[attribute]
            except KeyError:
                return None


class UrbanBeatsLog(object):
    """Class for logging the UrbanBEATS workflow, the log manages the history of the project
    as well as the current modelling session and is essential for tracking changes made throughout the
    workflow."""
    def __init__(self):
        """Contains two main variables: one that contains the project's history, one that contains the
        current session's log."""
        self.__ublogger = []
        self.__ublogsession = []

    def write_to_log(self, message):
        """Probably the most commonly called function, writes a log entry and saves it to the log array"""
        logstring = ""

    def initialize_session(self):
        """Writes a title string to the log to indicate the start of a new session."""
        logstring = ""

    def save_log(self):
        """Saves the current complete log history to the log file in the project folder"""
        pass

    def load_log_history(self):
        """Loads the project log, reads the entire history."""
        pass

    def export_log(self, filepath):
        """Exports the log to an external file on the harddrive that the user can reader later on."""
        pass


