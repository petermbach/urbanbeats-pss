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
import math
from shapely.geometry import Polygon, LineString

# --- URBANBEATS LIBRARY IMPORTS ---
from ubmodule import *
from md_delinblocks import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
import model.progref.ubglobals as ubglobals


# --- MODULE CLASS DEFINITION ---
class Infrastructure(UBModule):
    """ TECHNOLOGY PLANNING AND IMPLEMENTATION MODULE
    Performs the classical spatial allocation of infrastructure algorithm.
    Also performs the implementation depending on the simulation type.
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "Technology Placement Module for UrbanBEATS"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        self.create_parameter("generate_wastewater", BOOL, "boolean for whether to run wastewater algorithms.")
        self.generate_wastewater = 1

    def run_module(self):
        """Runs the infrastructure simulation module."""
        self.notify("Start INFRASTRUCTURE Planning")

        if self.generate_wastewater:
            self.run_wastewater_infrastructure_module()

        return True

    def run_wastewater_infrastructure_module(self):
        """ Wastewater infrastructure generation module, runs the creation of sewer network connected to current WWTPs
        within the region and then plans decentralisation/centralisation strategies through spatial assessment and
        adaptation strategies.
        """
        self.notify("Wastewater Plan!")

        # Get Map Attributes
        self.map_attr = self.scenario.get_asset_with_name("MapAttributes")

        # Get all the Blocks
        self.blocks = self.scenario.get_assets_with_identifier("BlockID")    # returns [ ] of UBVector() objects
        # for b in self.blocks:
        #     print "Current Block", b.get_attribute("BlockID")
        #     print b.get_attribute("MinElev")
        self.delineate_sww_flow_paths(self.blocks)

        return True


    def delineate_sww_flow_paths(self, blockslist):
        """Delineates the sewer network flow paths according to the chosen method and saves the information to the blocks.

        :param sww_blocks: a list [] of UBVector instances representing the Blocks
        :return: all data is saved to the UBVector instances as new Block data.
        """

        sww_blocks = []
        # Step 1 - Determine suitable blocks to place sewer networks. No sewers in Rivers or Lakes,
        # or when Population = 0 and there is no industry (total employees = 0)
        for b in blockslist:
            if b.get_attribute("HasRiver") or b.get_attribute("HasLake"):
                continue

            pop = b.get_attribute("Population")
            employees = b.get_attribute("Population")
            if pop > 0 or employees > 0:
                b.add_attribute("Sww_loc", b.get_attribute("BlockID"))
                sww_blocks.append(b)  # Append this block to a list of blocks with a sewer network

        # Step 2 - Run delineation method to sww_blocks
        sink_ids = []
        for i in range(len(sww_blocks)):
            current_block = sww_blocks[i]
            current_blockid = current_block.get_attribute("BlockID")

            # SKIP CONDITION 1 - Block has zero status
            if current_block.get_attribute("Status") == 0:
                continue

            z = current_block.get_attribute("AvElev")

            # Get the neighbouring elevations. This is either the full neighbourhood if we are not using natural or
            # built features as a guide, or the full neighbourhood if neither features are in adjacent neighbour blocks.
            # Otherwise the neighbour_z array will have only as many options as there are neighbours with natural or
            # built features.

            # if self.guide_built:      # If we use natural or built features as a guide, then...
            #     neighbours_z = self.get_modified_neighbours_z(current_block)    # Returns [[BlockID], [Elevation]]
            #     if neighbours_z is None:        # If the current block has no natural or built features adjacent...
            #         neighbours_z = self.scenario.retrieve_attribute_value_list("Block", "MinElev",
            #                                                                    current_block.get_attribute(
            #                                                                        "Neighbours"))
            # else:
            neighbours_z = self.scenario.retrieve_attribute_value_list("Block", "AvElev",
                                                                       current_block.get_attribute("Neighbours"))
            print "Neighbour Z: ", neighbours_z

            # Find the upstream block unless it's a sink
            flow_id, min_zdrop = self.find_upstream_d8(z, neighbours_z)

            if flow_id == -9999:                    # if no flowpath has been found
                sink_ids.append(current_blockid)
                upstream_id = -1                    # Block is a possible sink. if -2 --> block is a catchment outlet
            else:
                upstream_id = flow_id

            # Grab distances / slope between two Block IDs
            if flow_id == -9999:
                avg_slope = 0
            else:
                up_block = self.scenario.get_asset_with_name("BlockID" + str(upstream_id))
                dx = up_block.get_attribute("CentreX") - current_block.get_attribute("CentreX")
                dy = up_block.get_attribute("CentreY") - current_block.get_attribute("CentreY")
                dist = float(math.sqrt((dx * dx) + (dy * dy)))
                avg_slope = min_zdrop / dist

            # Add attributes
            current_block.add_attribute("Sww_upID", upstream_id)
            current_block.add_attribute("Sww_min_dz", min_zdrop)
            current_block.add_attribute("Sww_distUP", dist)
            current_block.add_attribute("Sww_avg_slope", avg_slope)

            # Draw Networks
            if upstream_id != -1 and upstream_id != 0:
                network_link = self.draw_sewer_lines(current_block, 1)
                self.scenario.add_asset("FlowID"+str(current_blockid), network_link)

        return True

    def find_upstream_d8(self, z, nhd_z):
        """Uses the standard D8 method to find the upstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [NHD_Z - Z] and is
        positive if the neighbouring Block has a higher elevation than the central Block.

        :param z: elevation of the current central Block
        :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return: up_id: block ID that water drains from, max(dz) the lowest elevation difference.
        """
        dz = []
        for i in range(len(nhd_z[1])):
            dz.append(nhd_z[1][i] - z)  # Calculate the elevation difference
        if min(dz) > 0:  # If there is a drop in elevation - this also means the area cannot be flat!
            up_id = nhd_z[0][dz.index(min(dz))]  # The ID corresponds to the maximum elevation difference
        else:
            up_id = -9999  # Otherwise there is a sink in the current Block
        return up_id, min(dz)

    def draw_sewer_lines(self, current_block, flow_type):
        """Creates a link of the sewer network as a UBVector() and returns a line asset.

        :param current_block: current ID of the block that the flow path is being drawn for
        :param flow_type: type of flow path e.g. "Regular pipe"
        :return: UBVector() instance of a network link
        """
        current_id = current_block.get_attribute("BlockID")
        upstream_id = current_block.get_attribute("Sww_upID")
        upper_block = self.scenario.get_asset_with_name("BlockID"+str(upstream_id))

        x_up = upper_block.get_attribute("CentreX")
        y_up = upper_block.get_attribute("CentreY")
        z_up = upper_block.get_attribute("AvElev")
        up_point = (x_up, y_up, z_up)

        x_down = current_block.get_attribute("CentreX")
        y_down = current_block.get_attribute("CentreY")
        z_down = current_block.get_attribute("AvElev")
        down_point = (x_down, y_down, z_down)

        network_link = ubdata.UBVector((up_point, down_point))
        network_link.determine_geometry((up_point, down_point))
        network_link.add_attribute("SwwID", current_id)
        network_link.add_attribute("Sww_BlockID", current_id)
        network_link.add_attribute("Sww_UpstreamID", upstream_id)
        network_link.add_attribute("Z_up", z_up)
        network_link.add_attribute("Z_down", z_down)
        network_link.add_attribute("Min_zdrop", current_block.get_attribute("Sww_min_dz"))
        network_link.add_attribute("LinkType", flow_type)
        network_link.add_attribute("AvgSlope", current_block.get_attribute("Sww_avg_slope"))
        return network_link