r"""
@file   mod_population.py
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

class MapLandUseToSimGrid(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 3
    longname = "Land Use Mapping"
    icon = ":/icons/region.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # MODULE PARAMETERS
        self.create_parameter("gridname", STRING, "Name of the simulation grid, unique identifier used")
        self.create_parameter("boundaryname", STRING, "Name of the boundary the grid is based upon")
        self.create_parameter("geometry_type", STRING, "name of the geometry type the grid should use")
        self.gridname = "My_urbanbeats_grid"
        self.boundaryname = "(select simulation boundary)"
        self.geometry_type = "SQUARES"  # SQUARES, HEXAGONS, VECTORPATCH, RASTER

        # Geometry Type: Square Blocks
        self.create_parameter("blocksize", DOUBLE, "Size of the square blocks")
        self.create_parameter("blocksize_auto", BOOL, "Determine the block size automatically?")
        self.blocksize = 500    # [m]
        self.blocksize_auto = 0

        # Geometry Type: Hexagonal Blocks
        self.create_parameter("hexsize", DOUBLE, "Edge length of a single hexagonal block")
        self.create_parameter("hexsize_auto", BOOL, "Auto-determine the hexagonal edge length?")
        self.create_parameter("hex_orientation", STRING, "Orientation of the hexagonal block")
        self.hexsize = 300  # [m]
        self.hexsize_auto = 0
        self.hex_orientation = "NS"     # NS = north-south, EW = east-west

        # Geometry Type: Patch/Irregular Block
        self.create_parameter("patchzonemap", STRING, "The zoning map that patch delineation is based on")
        self.create_parameter("disgrid_use", BOOL, "Use a discretization grid for the patch delineatioN?")
        self.create_parameter("disgrid_length", DOUBLE, "Edge length of the discretization grid")
        self.create_parameter("disgrid_auto", BOOL, "Auto-determine the size of the discretization grid?")
        self.patchzonemap = "(select zoning map for patch delineation)"
        self.disgrid_use = 0
        self.disgrid_length = 500   # [m]
        self.disgrid_auto = 0

        # Geometry Type: Raster/Fishnet
        self.create_parameter("rastersize", DOUBLE, "Resolution of the raster grid")
        self.create_parameter("nodatavalue", DOUBLE, "Identifier for the NODATAVALUE")
        self.create_parameter("generate_fishnet", BOOL, "Generate a fishnet of the raster?")
        self.rastersize = 30    # [m]
        self.nodatavalue = -9999
        self.generate_fishnet = 0

        # NON-VISIBLE PARAMETERS (ADVANCED SETTINGS)
        # None

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders.

        :return: True upon successful completion.
        """
        self.notify("Mapping Regions to Simulation for "+self.boundaryname)

        # --- SECTION 1 - Preparation for creating the simulation grid based on the boundary map


        # --- SECTION 2 - Create the grid


        # --- SECTION 3 - Identify neighbours


        # --- SECTION 4 - Generate maps/shapes

        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass