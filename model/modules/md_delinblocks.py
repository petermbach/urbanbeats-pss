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
import model.ublibs.ubdatatypes as ubdata


# --- MODULE CLASS DEFINITION ---
class DelinBlocks():
    """ DELINEATION - SPATIAL SETUP MODULE
    Loads the spatial maps into the model core and processes them either into
    Blocks or Patch representation for all other modules to use. Also performs
    spatial connectivity analysis and prepares all input data in a ready-to-use
    format.
    """

    def __init__(self):
        self.name = "Delineation and Spatial Setup Module"
        pass

    def run(self):
        pass
