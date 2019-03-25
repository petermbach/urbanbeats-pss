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

# --- URBANBEATS LIBRARY IMPORTS ---
from model.modules.ubmodule import *


# --- MODULE CLASS DEFINITION ---
class ImpactAssess(UBModule):
    """ IMPACT ASSESSMENT MODULE
    Undertakes an impact assessment of the current scenario based on the
    various impacts labelled. The model performs various assessments and outputs
    useful indicators showing the before-after situations of different scenarios
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "Impact Assessment Module"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        self.create_parameter("dummy", BOOL, "dummy parameter for testing")
        self.dummy = 0

    def run(self):
        pass
