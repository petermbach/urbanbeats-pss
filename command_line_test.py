"""
@file   command_line_test.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2018  Peter M. Bach

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
__copyright__ = "Copyright 2018. Peter M. Bach"

# The following script demonstrates how to start an UrbanBEATS simulation from core without
# the GUI. Use this script when testing the core for errors where the GUI closes suddenly.

# PYTHON IMPORTS
import os
import sys
import xml.etree.ElementTree as ET

# URBANBEATS IMPORTS
from model import urbanbeatscore
from model import ubscenarios
from model import ubdatalibrary
from model import ublibs
from model.progref import ubglobals

# --- SECTION 1 - INITIALIZE THE CORE SIMULATION ---

# GET THE ROOT DIRECTORY OF THE URBANBEATS RUNTIME FOR ACCESS TO FOLDERS
UBEATSROOT = os.path.dirname(sys.argv[0])  # Obtains the program's root directory
UBEATSROOT = UBEATSROOT.encode('string-escape')  # To avoid weird bugs e.g. if someone's folder path

# GET THE OPTIONS FROM THE CONFIG FILE config.cfg
UBEATSOPTIONS = {}
options = ET.parse(UBEATSROOT+"/config.cfg")
root = options.getroot()
for section in root.find('options'):
    for child in section:
        UBEATSOPTIONS[child.tag] = child.text

# INSTANTIATE THE NEW SIMULATION CORE
newsimulation = urbanbeatscore.UrbanBeatsSim(UBEATSROOT, UBEATSOPTIONS)

# SETUP SIMULATION DATA
newsimulation.set_project_parameter("name", "My Core Version UrbanBEATS Simulation Project")
newsimulation.set_project_parameter("region", "Melbourne")

try:
    cityindex = ubglobals.CITIES.index("Melbourne")     # Maintaining consistency, use the city name
except ValueError:
    cityindex = len(ubglobals.CITIES) - 1   # If City is not contained in the list, set it to the last item ("Other")

newsimulation.set_project_parameter("city", ubglobals.CITIES[cityindex])
newsimulation.set_project_parameter("modeller", "Peter M. Bach")
newsimulation.set_project_parameter("affiliation", "Monash Eawag")
newsimulation.set_project_parameter("otherpersons", "")
newsimulation.set_project_parameter("synopsis", "This is a test version of an UrbanBEATS Simulation")
newsimulation.set_project_parameter("boundaryshp", "C:/Users/peter/Documents/TempDocs/Files/Upperdandy/Boundary.shp")
newsimulation.set_project_parameter("projectpath", UBEATSOPTIONS["defaultpath"])
newsimulation.set_project_parameter("keepcopy", 0)

# INITIALIZE THE NEW SIMULATION
newsimulation.initialize_simulation("new")

# --- SECTION 2 - ADDING DATA TO THE PROJECT DATA LIBRARY ---

# --- SECTION 3 - SETTING UP A PROJECT SCENARIO ---

# --- SECTION 4 - WORKING WITH AN ACTIVE SCENARIO ---

# --- SECTION 5 - RUNNING SIMULATION ---


