# -*- coding: utf-8 -*-
"""
@file   ubscenarios.py
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


# --- SCENARIO CLASS DEFINITION ---
class UrbanBeatsScenario(object):
    """The static parent class that contains the basic definition of the
    scenario for UrbanBEATS simulations. Other scenario classes inherit from
    this class and define the type of scenario (i.e. static, dynamic, benchmark)
    """
    def __init__(self):
        self.__scenarioname = ""
        self.__scenariotype = ""
        self.__scenariopath = ""

        self.__mapdata = [] # a list of map data to be used, holds the data references.
        self.__modulesetup = [] # a boolean list of which modules are active and which are not.

    def run(self):
        pass
