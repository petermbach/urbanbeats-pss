# -*- coding: utf-8 -*-
"""
@file   md_infrastructure.pyw
@author Peter M Bach <peterbach@gmail.com>, Natalia Duque <natalia.duquevillarreal@eawag.ch>
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

__author__ = "Peter M. Bach, Natalia Duque"
__copyright__ = "Copyright 2012. Peter M. Bach"

# --- CODE STRUCTURE ---
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import threading
import os
import gc
import tempfile
import numpy as np
from math import *
import sys
# Graph Algorithms
from py_alg_dat.graph import UnDirectedWeightedGraph
from py_alg_dat.graph_vertex import GraphVertex
from py_alg_dat.graph_algorithms import GraphAlgorithms

# Spatial geometry
from shapely.geometry import Polygon, LineString, Point
from random import randint

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
        self.name = "Urban Drainage Infrastructure Generation"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim
        self.scenario = scenario
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # PARAMETER LIST DEFINITION
        self.create_parameter("generate_wastewater", BOOL, "boolean for whether to run wastewater algorithms.")
        self.generate_wastewater = 1

        # (Tab XXX) WASTEWATER DRAINAGE FLOW PATHS [TO DO]
        self.create_parameter("sewer", BOOL, "delineate sewer networks?")
        self.create_parameter("sww_delin_method", STRING, "delineation method to use")
        self.create_parameter("sww_dem_smooth", BOOL, "smooth DEM map before doing sewer delineation?")
        self.create_parameter("sww_dem_passes", DOUBLE, "number of passes for smoothing")
        self.create_parameter("sww_guide_natural", BOOL, "guide sewer delineation using pre-loaded natural feature?")
        self.create_parameter("sww_guide_built", BOOL, "guide sewer delineation using built infrastructure?")
        self.create_parameter("sww_ignore_rivers", BOOL, "ignore river features in the delineation of outlets")
        self.create_parameter("sww_ignore_lakes", BOOL, "ignore lake features in the delineation of outlets")
        self.sewer = 1
        self.sww_delin_method = "D8"
        self.sww_dem_smooth = 0
        self.sww_dem_passes = 1
        self.sww_guide_natural = 0
        self.sww_guide_built = 0
        self.sww_ignore_rivers = 0
        self.sww_ignore_lakes = 0
        #--------------------------------------------------------------------------------------------------------------


    def run_module(self):
        """Runs the infrastructure simulation module."""
        self.notify("Start INFRASTRUCTURE Planning")

        if self.generate_wastewater:

            # 7.3 - Sewer and Water Supply Systems (COMING SOON) [TO DO]
            # Get Map Attributes
            self.map_attr = self.scenario.get_asset_with_name("MapAttributes")
            self.map_attr.add_attribute("HasSWW", 1)
            self.notify("Loading Treatment Infrastructure")
            print("Loading Treatment Infrastructure")
            self.run_wastewater_infrastructure_module()

        else:
            self.map_attr.add_attribute("HasSWW", 0)

        return True

    def run_wastewater_infrastructure_module(self):
        """ Wastewater infrastructure generation module, runs the creation of sewer network connected to current WWTPs
        within the region and then plans decentralisation/centralisation strategies through spatial assessment and
        adaptation strategies.
        """
        self.notify("Wastewater Plan!")

        # # Get Map Attributes
        # self.map_attr = self.scenario.get_asset_with_name("MapAttributes")

        # Get all the Blocks
        self.blocks = self.scenario.get_assets_with_identifier("BlockID")    # returns [ ] of UBVector() objects

        if not self.sewer:
            pass

        sww_blocks = []

        # Step 1 - Determine suitable blocks to place sewer networks.
        # No sewers when Population = 0 and there is no industry (total employees = 0)

        for current_block in self.blocks:

            # SKIP CONDITION 1 - Block has zero status
            current_blockid = current_block.get_attribute("BlockID")
            if current_block.get_attribute("Status") == 0:
                continue

            pop = current_block.get_attribute("Population")
            employees = current_block.get_attribute("TOTALjobs")
            if pop > 1 or employees > 1:
                current_block.add_attribute("HasSWW", 1)
                current_block.add_attribute("HasWWTP", 0)
                current_block.add_attribute("HasCarved", 0)
                current_block.add_attribute("BlockID", current_block.get_attribute("BlockID"))
                sww_blocks.append(current_block)  # Append this block to a list of blocks with a sewer network
            else:
                current_block.add_attribute("HasSWW", 0)
                current_block.add_attribute("HasWWTP", 0)
                current_block.add_attribute("Sww_DownID", 0)
                current_block.add_attribute("HasCarved", 0)

        print(str(len(sww_blocks)) + " BLOCKS WITH SWW ----------------------------------------------------")

        # Step 2 - Delineate the sewer network for the blocks with population or employment greater than 1 person.

        self.delineate_sww_flow_paths(sww_blocks)

        # Step 3 - Get the Minimum spanning Tree as a benchmark for the minimum lenght required to connect all blocks.

        vertices, edges = self.undirected_graph(sww_blocks)
        self.spanning_tree(vertices, edges)

        # Step 4 - Design the generated network with SND.

        # Step 5 - Design the generated network with UWIM.



        return True

    # def delineate_sww_flow_paths(self, blockslist):
    #     """Delineates the sewer network flow paths according to the chosen method and saves the information to the blocks.
    #
    #     :param sww_blocks: a list [] of UBVector instances representing the Blocks
    #     :return: all data is saved to the UBVector instances as new Block data.
    #     """
    #
    #     sww_blocks = []
    #     # Step 1 - Determine suitable blocks to place sewer networks. No sewers in Rivers or Lakes,
    #     # or when Population = 0 and there is no industry (total employees = 0)
    #     for current_block in blockslist:
    #
    #         # SKIP CONDITION 1 - Block has zero status
    #         if current_block.get_attribute("Status") == 0:
    #             continue
    #
    #         # if current_block.get_attribute("HasRiver") or current_block.get_attribute("HasLake"):
    #         #     current_block.add_attribute("HasSWW", 0)
    #         #     current_block.add_attribute("HasWWTP", 0)
    #         #     continue
    #
    #         pop = current_block.get_attribute("Population")
    #         employees = current_block.get_attribute("TOTALjobs")
    #         if pop > 1 or employees > 1:
    #             current_block.add_attribute("HasSWW", 1)
    #             current_block.add_attribute("BlockID", current_block.get_attribute("BlockID"))
    #             sww_blocks.append(current_block)  # Append this block to a list of blocks with a sewer network
    #         else:
    #             current_block.add_attribute("HasSWW", 0)
    #             current_block.add_attribute("HasWWTP", 0)
    #
    #     print(str(len(sww_blocks)) + " BLOCKS WITH SWW ----------------------------------------------------")
    #
    #     # Step 2 - Detect the block with sewer facilities and save them as starting points
    #     treatment = [(125, 6375)]    # (i, j) coordinates of the treatment facilities
    #
    #     wwtps = []
    #     for b in range(len(sww_blocks)):
    #
    #         current_block = sww_blocks[b]
    #
    #         self.detect_treatment(current_block, treatment)
    #         if not current_block.get_attribute("HasWWTP"):
    #             continue
    #         current_blockid = current_block.get_attribute("BlockID")
    #         wwtps.append(current_blockid)
    #         print(wwtps)
    #
    #     to_visit = [b for b in wwtps]
    #
    #     # Step 3 - Run delineation method to sww_blocks
    #     # count = 0
    #
    #     for current_block in sww_blocks:
    #         current_blockid = current_block.get_attribute("BlockID")
    #         if current_blockid not in to_visit:
    #             to_visit.append(current_blockid)
    #
    #     print("lenght to visit: " + str(len(to_visit)))
    #     blocks_checked = []
    #
    #     while to_visit:
    #
    #         current_search = []
    #
    #         current_search.append(to_visit[0])
    #
    #         for b in current_search:
    #
    #             current_block = self.scenario.get_asset_with_name("BlockID" + str(b))
    #             current_blockid = current_block.get_attribute("BlockID")
    #             # print ("current id " + str(current_blockid))
    #
    #             ndz = self.get_sww_neighbours_z(current_block, current_search)
    #             # print ndz
    #             if ndz is None:
    #                 continue
    #
    #
    #             z = current_block.get_attribute("AvgElev")
    #
    #             flow_id, min_zdrop = self.find_upstream_d8(z, ndz)
    #
    #             if flow_id == -9999:                     # if no flowpath has been found
    #
    #                 upstream_id = -9999                  # Block is a possible initial point for a branch of the sewer
    #             else:
    #                 upstream_id = flow_id
    #
    #             # Grab distances / slope between two Block IDs
    #             if flow_id == -9999:
    #                 slope = 0
    #                 dist = 0
    #             else:
    #                 up_block = self.scenario.get_asset_with_name("BlockID" + str(upstream_id))
    #                 dx = up_block.get_attribute("CentreX") - current_block.get_attribute("CentreX")
    #                 dy = up_block.get_attribute("CentreY") - current_block.get_attribute("CentreY")
    #                 dist = float(math.sqrt((dx * dx) + (dy * dy)))
    #                 slope = min_zdrop / dist
    #
    #             # Add attributes
    #             current_block.add_attribute("SwwID", current_blockid)
    #             current_block.add_attribute("Sww_upID", upstream_id)
    #             current_block.add_attribute("Sww_zdrop", min_zdrop)
    #             current_block.add_attribute("Sww_distUP", dist)
    #             current_block.add_attribute("Sww_slope", slope)
    #
    #             # Draw Networks
    #             if upstream_id != -9999 and upstream_id != 0:
    #                 network_link = self.draw_sewer_lines_up(current_block, 1)
    #                 self.scenario.add_asset("SwwID"+str(current_blockid), network_link)
    #
    #                 current_search.append(upstream_id)
    #
    #         for n in current_search:
    #             blocks_checked.append(n)
    #             if n not in to_visit:
    #                 continue
    #             to_visit.pop(to_visit.index(n))
    #
    #     return True

    def delineate_sww_flow_paths(self, sww_blocks):
        """Delineates the sewer network flow paths within the blocks that should have Sewer
            according to the chosen method and saves the information to the blocks.

        :param sww_blocks: a list [] of UBVector instances representing the Blocks
        :return: all data is saved to the UBVector instances as new Block data.
        """

        sinks = []
        river_blocks = []
        lake_ids = []

        sinks_list = self.identify_sinks(sww_blocks)
        # print("SINKS: " + str(len(sinks_list)) + str(sinks_list))

        self.copy_DEM()
        for s in sinks_list:
            self.carving_algorithm(s)

        ids = []
        for i in sww_blocks:
            ids.append(i.get_attribute("BlockID"))
        ids.sort()
        # print(ids)



        # graph = self.undirected_graph_(sww_blocks)
        # MST = self.m_spanning_tree(graph)

        # Step 2 - Detect the block with sewer facilities and save them as starting points
        # treatments = [(125, 6375)]    # (i, j) coordinates of the treatment facilities
        # treat_blocks = self.detect_treatment(sww_blocks, treatments)            # list of treatment facilities

        # Step 3 - Run delineation method to sww_blocks
        blocks_checked = []

        for i in range(len(sww_blocks)):
            current_block = sww_blocks[i]
            current_blockid = current_block.get_attribute("BlockID")
            # print("CURRENT BLOCK >>> " + str(current_blockid))

            # From the list of treatment facilities identify the closest.
            # TP_block= self.identify_closest_treatment_facility(current_block, treat_blocks)

            # Define the direction towards the closest treatment facility
            x1 = current_block.get_attribute("CentreX")
            y1 = current_block.get_attribute("CentreY")
            z1 = current_block.get_attribute("ModAvgElev")
            pt1 = [x1, y1]
            # pt2 = [TP_block.get_attribute("CentreX"), TP_block.get_attribute("CentreY")]
            # direction = self.define_direction(pt1, pt2)
            direction = 0

            cb_info = [current_blockid, x1, y1, z1]

            blocks_checked.append(current_blockid)


            # Get the list of neighbours and their corresponding x, y, z coordinates and direction towards treatment
            if self.sww_guide_natural or self.sww_guide_built:      # If we use natural or built features as a guide, then...
                ndh_info = self.get_sww_modified_neighbours_z(current_block)
                if ndh_info is None:        # If the current block has no natural or built features adjacent...
                    ndh_info = self.get_sww_neighbours_z(current_block)
            else:
                ndh_info = self.get_sww_neighbours_z(current_block)

            # Find the downstream block unless it's a sink

            # print("Neighbours: ", current_blockid, ndh_info[0])


            # # SKIP CONDITION 2 - Block already contains a river
            # if current_block.get_attribute("HasRiver") and not self.sww_ignore_rivers:
            #     flow_id = -9999
            #     river_blocks.append(current_block)
            #
            # # SKIP CONDITION 3 - Block contains a lake
            # if current_block.get_attribute("HasLake") and not self.sww_ignore_lakes:
            #     flow_id = -9999
            #     lake_ids.append(current_blockid)

            flow_id, max_zdrop = self.find_sww_downstream_d8(cb_info, ndh_info, direction)
            # flow_id, max_zdrop = self.find_sww_downstream_d8_TP(cb_info, ndh_info, direction)

            if flow_id == -9999:                        # if no flowpath has been found
                sinks.append(current_blockid)
                downstream_id = -1                      # Block is a possible sink
            else:
                downstream_id = flow_id

            # Grab distances / slope between two Block IDs
            if flow_id == -9999:
                slope = 0
                dist = 0
            else:
                down_block = self.scenario.get_asset_with_name("BlockID" + str(downstream_id))
                dx = current_block.get_attribute("CentreX") - down_block.get_attribute("CentreX")
                dy = current_block.get_attribute("CentreY") - down_block.get_attribute("CentreY")
                dist = float(math.sqrt((dx * dx) + (dy * dy)))
                slope = max_zdrop / dist

            # Add attributes
            current_block.add_attribute("SwwID", current_blockid)
            current_block.set_attribute("Sww_DownID", downstream_id)
            current_block.add_attribute("Sww_zdrop", max_zdrop)
            current_block.add_attribute("Sww_dist", dist)
            current_block.add_attribute("Sww_slope", slope)

            # Draw Networks
            if downstream_id != 0 and downstream_id != -1:
                network_link = self.draw_sewer_lines_down(current_block, 1)
                self.scenario.add_asset("SwwID"+str(current_blockid), network_link)


        # connect the Sinks
        # self.connect_sinks(sinks)
        # print(len(blocks_checked))

        self.delineate_clustered_networks(sww_blocks)

        return True

    def get_sww_neighbours_z(self, curblock):
        """Retrieves the id, x-, y- and z-values of all adjacent blocks within the current block's neighbourhood
           accounting for the presence of drainage infrastructure.

        :param curblock: the current block UBVector() instance
        :return: a list of all the block's neighbours [[BlockID], [X], [Y], [Z], [direction]], None otherwise
        """
        nhd_ids = curblock.get_attribute("Neighbours")
        nhd_info = [[], [], [], []]  # Neighbours [[0=id], [1=x], [2=y], [3=z]]

        for n in nhd_ids:
            nblock = self.scenario.get_asset_with_name("BlockID" + str(n))
            if nblock.get_attribute("HasSWW") and n not in nhd_info[0]:

                x2 = nblock.get_attribute("CentreX")
                y2 = nblock.get_attribute("CentreY")
                z2 = nblock.get_attribute("ModAvgElev")

                nhd_info[0].append(n)
                nhd_info[1].append(x2)
                nhd_info[2].append(y2)
                nhd_info[3].append(z2)

        if len(nhd_info[0]) == 0:
            return None
        else:
            return nhd_info

    def get_extended_neighbours(self, block):
        """Retrieves the id of all the neighbours of the immediate neighbours of a block
           accounting for the presence of drainage infrastructure.

        :param block: the current block UBVector() instance
        :return: a list of all the id of the extended block's neighbours [BlockID], None otherwise
        """
        extended_neighbours = []

        sink_block = self.scenario.get_asset_with_name("BlockID" + str(block))

        nhd = sink_block.get_attribute("Neighbours")

        for n in nhd:
            n_block = self.scenario.get_asset_with_name("BlockID" + str(n))
            for i in n_block.get_attribute("Neighbours"):
                if i in extended_neighbours or i is block or i in nhd:
                    continue
                e_block = self.scenario.get_asset_with_name("BlockID" + str(i))
                if not e_block.get_attribute("HasSWW"):
                    continue
                # if e_block.get_attribute("Sww_DownID") in nhd:
                #     continue

                extended_neighbours.append(i)
        if not extended_neighbours:
            return None

        return extended_neighbours

    def get_sww_modified_neighbours_z(self, curblock):
        """Retrieves the z-values of all adjacent blocks within the current block's neighbourhood accounting for
        the presence of drainage infrastructure or natural features. If we use natural or built features as a guide.

        :param curblock: the current block UBVector() instance
        :return: a list of all the block's neighbours [[BlockID], [X], [Y], [Z], [direction]], None otherwise
        """
        nhd_ids = curblock.get_attribute("Neighbours")
        nhd_info = [[], [], [], []]  # Neighbours [[0=id], [1=x], [2=y], [3=z]]

        # Scan neighbourhood for Blocks with Rivers/Lakes
        for n in nhd_ids:

            nblock = self.scenario.get_asset_with_name("BlockID" + str(n))

            if nblock.get_attribute("HasSWW") and n not in nhd_info[0]:
                x2 = nblock.get_attribute("CentreX")
                y2 = nblock.get_attribute("CentreY")
                z2 = nblock.get_attribute("ModAvgElev")

                if self.sww_guide_natural:
                    if nblock.get_attribute("HasRiver") or nblock.get_attribute("HasLake"):
                        nhd_info[0].append(n)
                        nhd_info[1].append(x2)
                        nhd_info[2].append(y2)
                        nhd_info[3].append(z2)
                if self.sww_guide_built:
                    if nblock.get_attribute("HasSWDrain") and n not in nhd_info[0]:
                        nhd_info[0].append(n)
                        nhd_info[1].append(x2)
                        nhd_info[2].append(y2)
                        nhd_info[3].append(z2)

        print curblock.get_attribute("BlockID"), nhd_info[0]

        if len(nhd_info[0]) == 0:
            return None
        else:
            return nhd_info

    def find_sww_downstream_d8_TP(self, curblock, nhd, direction):
        """Uses the standard D8 method to find the downstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [NHD_Z - Z] and is
        negative if the neighbouring Block has a lower elevation than the central Block.

        :param curblock: id,x,y,z coordinates of the current central Block
        :param nhd: id,x,y,z coordinates of all its neighbours
        :param direction: direction towards closest treatment.
        :return: down_id: block ID that water drains to, min(dz) the lowest elevation difference.
        """

        nhd_z = []     # drop = [[id], [dz]]
        nhd_dir = []
        current_block = self.scenario.get_asset_with_name("BlockID" + str(curblock[0]))
        x1 = curblock[1]
        y1 = curblock[2]
        z1 = curblock[3]
        min_dz = -5
        max_dz = 10
        better = 0

        angle = [pi/8, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4, 2*pi]
        down_id = -9999

        for i in range(len(nhd[0])):
            x2 = nhd[1][i]
            y2 = nhd[2][i]
            z2 = nhd[3][i]
            dz = z1 - z2

            dir = self.define_direction([x1, y1], [x2, y2])
            if dz > better:

                for a in angle:

                    if direction >= 0:                                      # counter-clockwise search

                        if direction <= dir + a and min_dz <= dz < max_dz:
                            down_id = nhd[0][i]
                            better = dz
                            return down_id, better

                        else:
                            down_id = -9999
                            min_dz = 0

                    else:                                                     # clockwise search
                        if direction >= dir - a and min_dz <= dz < max_dz:
                            down_id = nhd[0][i]
                            better = dz
                            return down_id, better

                        else:
                            down_id = -9999
                            min_dz = 0

            if dz == better:
                down_id = nhd[0][i]
                min_dz = 0

        return down_id, better

    def find_sww_downstream_d8(self, curblock, nhd, direction):
        """Uses the standard D8 method to find the downstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [Z-NHD_Z ] and is
        negative if the neighbouring Block has a lower elevation than the central Block.

        :param curblock: id,x,y,z coordinates of the current central Block
        :param nhd: id,x,y,z coordinates of all its neighbours
        :return: down_id: block ID that water drains to, min(dz) the lowest elevation difference.
        """
        z = curblock[3]
        min_elev = 9999
        down_id = None
        dz = 0
        for i in range(len(nhd[3])):
            # dz.append(z - nhd[3][i])  # Calculate the elevation difference
            n = nhd[0][i]
            # if n in blocks_checked:
            #     print(str(n) + " was already checked.. shouldn't be a possible neighbour")
            #     continue

            if nhd[3][i] < z and nhd[3][i] < min_elev:
                down_id = nhd[0][i]
                dz = z - nhd[3][i]
                min_elev = nhd[3][i]
            # elif nhd[3][i] == z:
            #     down_id, dz = self.find_sww_downstream_d8_TP(curblock, nhd, direction)

        if down_id is None:
            down_id = -9999  # Otherwise there is a sink in the current Block
            dz = 0

        # print ("FOR BLOCK: " + str(curblock[0]) + "DOWN ID: " + str(down_id) + " dz: " + str(dz))

        # if max(dz) > 0:  # If there is a drop in elevation - this also means the area cannot be flat!
        #     down_id = nhd[0][dz.index(max(dz))]  # The ID corresponds to the maximum elevation difference
        # else
        # else:
        #     down_id = -9999  # Otherwise there is a sink in the current Block
        return down_id, dz

    def find_upstream_d8(self, curblock, nhd):
        """Uses the standard D8 method to find the upstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [NHD_Z - Z] and is
        positive if the neighbouring Block has a higher elevation than the central Block.

        :param z: elevation of the current central Block
        :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return: up_id: block ID that water drains from, max(dz) the lowest elevation difference.
        """
        z = curblock[3]

        dz = []
        # print nhd_z[1]
        for i in range(len(nhd[3])):
            dz.append(nhd[3][i] - z)  # Calculate the elevation difference

        positives = [x for x in dz if x >= 0]
        negatives = [x for x in dz if x <= 0]
        if positives and min(positives) >= 0:  # If there is a drop in elevation or is flat!
                up_id = nhd[0][dz.index(min(positives))]  # The ID corresponds to the block with minimum elevation difference
                dElev = min(positives)
        elif max(negatives) > (-1):
            up_id = nhd[0][
                dz.index(max(negatives))]  # The ID corresponds to the block with minimum elevation difference
            dElev = max(negatives)
        else:
            up_id = -9999  # Otherwise there is a hill in the current Block
            dElev = 0

        return up_id, dElev

    def draw_sewer_lines_up(self, current_block, flow_type):
        """Creates a link of the sewer network as a UBVector() and returns a line asset.

        :param current_block: current ID of the block that the flow path is being drawn for
        :param flow_type: type of flow path e.g. "Regular pipe"
        :return: UBVector() instance of a network link
        """

        current_id = current_block.get_attribute("BlockID")
        upstream_id = current_block.get_attribute("Sww_DownID")
        upper_block = self.scenario.get_asset_with_name("BlockID"+str(upstream_id))

        print(str(current_id) + " -> " + str(upstream_id))

        x_up = upper_block.get_attribute("CentreX")
        y_up = upper_block.get_attribute("CentreY")
        z_up = upper_block.get_attribute("ModAvgElev")
        up_point = (x_up, y_up, z_up)

        x_down = current_block.get_attribute("CentreX")
        y_down = current_block.get_attribute("CentreY")
        z_down = current_block.get_attribute("ModAvgElev")
        down_point = (x_down, y_down, z_down)

        network_link = ubdata.UBVector((up_point, down_point))
        network_link.determine_geometry((up_point, down_point))
        network_link.add_attribute("SwwID", current_id)
        network_link.add_attribute("UpID", current_id)
        network_link.add_attribute("DownID", upstream_id)
        network_link.add_attribute("Z_up", z_up)
        network_link.add_attribute("Z_down", z_down)
        network_link.add_attribute("Length", current_block.get_attribute("Sww_dist"))
        network_link.add_attribute("Min_zdrop", current_block.get_attribute("Sww_zdrop"))
        network_link.add_attribute("LinkType", flow_type)
        network_link.add_attribute("Slope", current_block.get_attribute("Sww_slope"))
        return network_link

    def draw_sewer_lines_down(self, current_block, flow_type):
        """Creates a link of the sewer network as a UBVector() and returns a line asset.

        :param current_block: current ID of the block that the flow path is being drawn for
        :param flow_type: type of flow path e.g. "Regular pipe"
        :return: UBVector() instance of a network link
        """

        current_id = current_block.get_attribute("BlockID")
        x_up = current_block.get_attribute("CentreX")
        y_up = current_block.get_attribute("CentreY")
        z_up = current_block.get_attribute("ModAvgElev")
        up_point = (x_up, y_up, z_up)

        downstream_id = current_block.get_attribute("Sww_DownID")


        if downstream_id == -1:
            network_link = ubdata.UBVector(up_point)
            network_link.determine_geometry(up_point)
            network_link.add_attribute("SwwID", current_id)
            network_link.add_attribute("UpID", current_id)
            network_link.add_attribute("DownID", -1)
            network_link.add_attribute("Z_up", z_up)
            network_link.add_attribute("Z_down", 0.0)
            network_link.add_attribute("Length", 0.0)
            network_link.add_attribute("Min_zdrop", 0.0)
            network_link.add_attribute("LinkType", flow_type)
            network_link.add_attribute("Slope", 0.0)
        else:

            down_block = self.scenario.get_asset_with_name("BlockID" + str(downstream_id))

            x_down = down_block.get_attribute("CentreX")
            y_down = down_block.get_attribute("CentreY")
            z_down = down_block.get_attribute("ModAvgElev")
            down_point = (x_down, y_down, z_down)

            network_link = ubdata.UBVector((up_point, down_point))
            network_link.determine_geometry((up_point, down_point))
            network_link.add_attribute("SwwID", current_id)
            network_link.add_attribute("UpID", current_id)
            network_link.add_attribute("DownID", downstream_id)
            network_link.add_attribute("Z_up", z_up)
            network_link.add_attribute("Z_down", z_down)
            network_link.add_attribute("Length", current_block.get_attribute("Sww_dist"))
            network_link.add_attribute("Min_zdrop", current_block.get_attribute("Sww_zdrop"))
            network_link.add_attribute("LinkType", flow_type)
            network_link.add_attribute("Slope", current_block.get_attribute("Sww_slope"))

        return network_link

    def detect_treatment(self, blocks_list, treatments):
        """Identifies if there is a treatment facility inside the block

        :param blocks_list: current ID of the block in evaluation
        :param treatments: loaded UBVector() objects of treatment facilities
        :return: list of blocks with WWTP.
        """

        wwtps = []
        for i in range(len(blocks_list)):
            current_block = blocks_list[i]
            if current_block.get_attribute("Status") == 0:
                continue
            coordinates = current_block.get_points()
            coordinates = [(c[0], c[1]) for c in coordinates]
            blockpoly = Polygon(coordinates)

            hastreatment = 0
            for j in range(len(treatments)):
                treat_point = Point(treatments[j])
                if not treat_point.intersects(blockpoly):
                    continue
                hastreatment = 1
            if hastreatment:
                current_block.set_attribute("HasWWTP", 1)
                print("Block " + str(current_block.get_attribute("BlockID")) + " HAS TREATMENT--------------------------------------------")
                wwtps.append(current_block)
            else:
                current_block.set_attribute("HasWWTP", 0)

        if len(wwtps) == 0:
            return None
        else:
            return wwtps

    def identify_closest_treatment_facility(self, current_block, treatments):
        """Identifies the closest treatment facility from the current block

        :param current_block: current ID of the block in evaluation
        :param treatments: list of blocks with treatment facilities
        :return: block with closest treatment.
        """
        if treatments is None:
            print ("No treatment detected")
            pass

        x_b = current_block.get_attribute("CentreX")
        y_b = current_block.get_attribute("CentreY")
        current_block.add_attribute("ClosestTP", 0)
        # z_b = current_block.get_attribute("AvgElev")
        # b_point = (x_b, y_b, z_b)

        distance = 999999999

        for j in range(len(treatments)):

            treat_block = treatments[j]

            x_treat = treat_block.get_attribute("CentreX")
            y_treat = treat_block.get_attribute("CentreY")
            # z_treat = treat_block.get_attribute("AvgElev")
            # treat_point = (x_treat, y_treat, z_treat)

            dx = x_b - x_treat
            dy = y_b - y_treat
            # dz = z_b-z_treat

            dist = float(math.sqrt((dx * dx) + (dy * dy)))
            # slope = (dz) / dist

            if dist >= distance:
                continue

            distance = dist
            closest_treat_id = treat_block.get_attribute("BlockID")
            current_block.set_attribute("ClosestTP", closest_treat_id)
            TP_block = self.scenario.get_asset_with_name("BlockID" + str(closest_treat_id))

        return TP_block

    def identify_closest_river(self, blockslist, current_block):                # [TO DO]
        """Identifies the closest treatment facility from the current block

        :param current_block: current ID of the block in evaluation
        :param treatments: list of blocks with treatment facilities
        :return: block with closest treatment.
        """

        if current_block.get_attribute("HasRiver"):
            return current_block

        river_blocks = []
        for b in blockslist:
            if not b.get_attribute("HasRiver"):
                continue
            river_blocks.append(b)


        if river_blocks is None:
            print ("No rivers detected")
            pass

        x_b = current_block.get_attribute("CentreX")
        y_b = current_block.get_attribute("CentreY")
        # z_b = current_block.get_attribute("AvgElev")
        # b_point = (x_b, y_b, z_b)

        distance = 999999999

        for j in range(len(river_blocks)):

            river_block = river_blocks[j]

            x_treat = river_block.get_attribute("CentreX")
            y_treat = river_block.get_attribute("CentreY")
            # z_treat = treat_block.get_attribute("AvgElev")
            # treat_point = (x_treat, y_treat, z_treat)

            dx = x_b - x_treat
            dy = y_b - y_treat
            # dz = z_b-z_treat

            dist = float(math.sqrt((dx * dx) + (dy * dy)))
            # slope = (dz) / dist

            if dist >= distance:
                continue

            distance = dist
            closest_river_id = river_block.get_attribute("BlockID")
            current_block.add_attribute("ClosestRiver", closest_river_id)
            R_block = self.scenario.get_asset_with_name("BlockID" + str(closest_river_id))

        return R_block

    def define_direction(self, pt1, pt2):
        """Identifies the direction between two points. Is mainly used to get the direction from the centroid
           of current block towards a block containing a treatment, river, point of interest, etc.

        :param pt1: center point of the current block
        :param pt2: reference point representation the block with the treatment facility, river, point of interest,etc.
        :return: direction
        """

        x1 = pt1[0]     # current point
        y1 = pt1[1]

        x2 = pt2[0]     # reference point
        y2 = pt2[1]

        dx = x1 - x2
        dy = y1 - y2

        if dx == 0: a = np.inf
        else: a = dy/dx

        angle = atan(a)
        radians = angle * (pi/180)
        return radians

    def define_distance(self, pt1, pt2):
        """Identifies the distance between two points.

        :param pt1: center point of the current block
        :param pt2: neighbouring block
        :return: distance
        """

        x1 = pt1[0]     # current point
        y1 = pt1[1]

        x2 = pt2[0]     # reference point
        y2 = pt2[1]

        dx = x1 - x2
        dy = y1 - y2

        dist = float(math.sqrt((dx * dx) + (dy * dy)))

        return dist

    def identify_sinks(self, blockslist):
        """ Identify all depressions in the DEM.

        :return: sinks: list of sinks in the DEM
        """

        # blockslist = self.blocks
        sinks = []
        for current_block in blockslist:

            # SKIP CONDITION 1 - Block has zero status
            if current_block.get_attribute("Status") == 0:
                continue

            nhd = current_block.get_attribute("Neighbours")
            if nhd == None:
                print("NO NEIGHBOURS")
                continue
            id = current_block.get_attribute("BlockID")
            z = current_block.get_attribute("AvgElev")
            neighbours_z = self.scenario.retrieve_attribute_value_list("Block", "AvgElev",
                                                                       current_block.get_attribute(
                                                                           "Neighbours"))

            if z >= min(neighbours_z):
                continue
            sinks.append(id)
            # print("SINKS: " + str(sinks))
        return sinks

    def connect_sinks(self, sink_ids):
        """Runs the algorithm for scanning all sink blocks and attempting to find a flowpath beyond them.
        This function may also identify certain sinks as definitive catchment outlets.

        :param blockslist: the list [] of block UBVector instances
        :param sink_ids: a list of BlockIDs where a sink is believe to exist based on the flowpath method.
        :return: adds new assets to the scenario if a flowpath has been found for the sinks
        """
        closest_sink_id = None

        for i in range(len(sink_ids)):
            extended_neighbours = []

            current_sinkid = sink_ids[i]
            sink_block = self.scenario.get_asset_with_name("BlockID"+str(current_sinkid))

            x_b = sink_block.get_attribute("CentreX")
            y_b = sink_block.get_attribute("CentreY")
            z_b = sink_block.get_attribute("ModAvgElev")
            # b_point = (x_b, y_b, z_b)
            # z = current_block.get_attribute("ModAvgElev")
            nhd = sink_block.get_attribute("Neighbours")

            for n in nhd:
                n_block = self.scenario.get_asset_with_name("BlockID" + str(n))
                for i in n_block.get_attribute("Neighbours"):
                    if i in extended_neighbours or i is current_sinkid or i in nhd:
                        continue
                    e_block = self.scenario.get_asset_with_name("BlockID" + str(i))
                    if not e_block.get_attribute("HasSWW"):
                        continue
                    if e_block.get_attribute("Sww_DownID") in nhd:
                        continue

                    extended_neighbours.append(i)

            # print("NHD " + str(nhd) + " Extended: " + str(extended_neighbours))

            minElev = z_b
            distance = 999999999
            lowest = 999999
            for j in range(len(extended_neighbours)):

                n_nhd = extended_neighbours[j]

                if current_sinkid == n_nhd:
                    continue
                nn_block = self.scenario.get_asset_with_name("BlockID" + str(n_nhd))
                x_nBlock = nn_block.get_attribute("CentreX")
                y_nBlock = nn_block.get_attribute("CentreY")
                z_nBlock = nn_block.get_attribute("ModAvgElev")

                if z_nBlock >= minElev:
                    continue

                dx = x_b - x_nBlock
                dy = y_b - y_nBlock
                dz = z_b-z_nBlock

                dist = float(math.sqrt((dx * dx) + (dy * dy)))
                # slope = (dz) / dist

                if dist >= distance:
                    continue

                distance = dist
                minElev = z_nBlock
                closest_sink_id = n_nhd
                lowest = n_nhd

                # current_block.set_attribute("ClosestTP", closest_sink_id)
                # s_block = self.scenario.get_asset_with_name("BlockID" + str(closest_sink_id))

            if lowest != 999999:
                sink_block.set_attribute("Sww_DownID", lowest)  # Overwrite -1 to new ID
                # current_block.set_attribute("h_pond", sink_path)    # If ponding depth > 0, then there was a sink
                network_link = self.draw_sewer_lines_down(sink_block, "Sink")
                self.scenario.add_asset("SwwID" + str(current_sinkid), network_link)
                # print("Imprimiendo sinks... " + str(current_sinkid) + " -> " + str(lowest))
            else:
                sink_block.set_attribute("Sww_DownID", -1)  # signifies that Block is an outlet


            # possible_id_drains = []
            # possible_id_z = []
            # possibility = 0
            # distance = 999999999
            # sink_ids.pop(i)
            # for j in range(len(sink_ids)):
            #
            #     if current_blockid == sink_ids[j]:
            #         continue
            #
            #     sink_nhd = sink_ids[j]
            #     sink_block = self.scenario.get_asset_with_name("BlockID" + str(sink_nhd))
            #     x_sink = sink_block.get_attribute("CentreX")
            #     y_sink = sink_block.get_attribute("CentreY")
            #     z_sink = sink_block.get_attribute("AvgElev")
            #     # treat_point = (x_treat, y_treat, z_treat)
            #
            #     # if z_b - z_sink < 0:
            #     #     continue
            #
            #     dx = x_b - x_sink
            #     dy = y_b - y_sink
            #     # dz = z_b-z_treat
            #
            #     dist = float(math.sqrt((dx * dx) + (dy * dy)))
            #     # slope = (dz) / dist
            #
            #     if dist >= distance:
            #         continue
            #
            #     distance = dist
            #     closest_sink_id = sink_nhd
            #     # current_block.set_attribute("ClosestTP", closest_sink_id)
            #     # s_block = self.scenario.get_asset_with_name("BlockID" + str(closest_sink_id))
            #
            # current_block.set_attribute("Sww_DownID", closest_sink_id)   # Overwrite -1 to new ID
            # # current_block.set_attribute("h_pond", sink_path)    # If ponding depth > 0, then there was a sink
            # network_link = self.draw_sewer_lines_down(current_block, "Sink")
            #
            # self.scenario.add_asset("SwwID" + str(current_blockid), network_link)
        return True

    def copy_DEM(self):
        """ Creates a copy of the average elevation of each block into a new attribute. The copy will be used when the
            DEM information needs to be modified.
        """

        blockslist = self.blocks

        for current_block in blockslist:

            # SKIP CONDITION 1 - Block has zero status
            if current_block.get_attribute("Status") == 0:
                continue

            z = float(current_block.get_attribute("AvgElev"))
            current_block.add_attribute("ModAvgElev", z)
        return True

    def carving_algorithm(self, sink):
        """ The Priority First Search (PFS) algorithm (Sedgewick, 1988) creates an adjusted DEM by removing
            terrain depressions. Starting from the sinks (depressions) the algorithm combines digging and
            filling approaches to reach a cell with lower elevation than the sink.

        :param sink: Blocks with a sink (terrain depression)
        :return:
        """

        priority_queue = [], []
        priority_tree = []
        id = sink

        while id:

            current_block = self.scenario.get_asset_with_name("BlockID" + str(id))
            nhd = current_block.get_attribute("Neighbours")
            elev_s = current_block.get_attribute("ModAvgElev")

            if id in priority_queue[0]:
                priority_queue[1].pop(priority_queue[0].index(id))
                priority_queue[0].pop(priority_queue[0].index(id))

            for i in nhd:
                n_block = self.scenario.get_asset_with_name("BlockID" + str(i))
                # if n_block.get_attribute("HasCarved"):
                #     continue

                elev_n = n_block.get_attribute("ModAvgElev")

                if elev_n is None:
                    #[TO DO]  Check why the elevation is None
                    continue

                dz = elev_n - elev_s

                if i in priority_queue or i in priority_tree:
                    continue

                priority_queue[0].append(i)
                priority_queue[1].append(dz)

            min_dz = 999999
            id_min_dz = id
            for j in range(len(priority_queue[1])):
                dz = priority_queue[1][j]
                n_id = priority_queue[0][j]
                if dz < min_dz:
                    min_dz = dz
                    id_min_dz = n_id

            if min_dz >= 0 and id_min_dz not in priority_tree:
                priority_tree.append(id_min_dz)
                id = id_min_dz
                b = self.scenario.get_asset_with_name("BlockID" + str(id))
                # if b.get_attribute("HasCarved"):
                #     continue
                b.set_attribute("ModAvgElev", elev_s - 0.0001)
                b.add_attribute("HasCarved", 1)
            elif min_dz < 0 and id_min_dz not in priority_tree:
                priority_tree.append(id_min_dz)
                id = None
            else:
                id = None
            #     print(" EXIST IN PRIORITY TREE----------------------------")

        return True

    def undirected_graph(self, swwblocks):
        vertices = {}       # id: x, y, z coordinates
        edges = {}
        counter = 0
        for b in swwblocks:
            v1 = b.get_attribute("BlockID")

            # print ("                      v1", str(b.get_attribute("BlockID")))
            x1 = b.get_attribute("CentreX")
            y1 = b.get_attribute("CentreY")
            z1 = b.get_attribute("ModAvgElev")
            pt1 = [x1, y1]
            if v1 not in vertices.keys():
                vertices[v1] = [x1, y1, z1]


            # List of Neighbours [id], [x], [y], [z]
            neighbours = self.get_sww_neighbours_z(b)
            for i in range(len(neighbours[0])):

                v2 = neighbours[0][i]
                # if (v1, v2)in edges.keys() or (v2, v1) in edges.keys():
                #     print("EDGE ALREADY EXISTS")
                #     continue
                # print("v2", v2)
                x2 = neighbours[1][i]
                y2 = neighbours[2][i]
                z2 = neighbours[3][i]
                pt2 = [x2, y2]
                if v2 not in vertices.keys():
                    vertices[v2] = [x2, y2, z2]

                if (v1, v2) in edges.keys() or (v2, v1) in edges.keys():
                    continue


                lenght = self.define_distance(pt1, pt2)

                slope = -(z2-z1)/lenght

                edges[v1, v2] = z2-z1
                counter += 1
                # print(counter, len(edges))

                link = ubdata.UBVector((pt1, pt2))
                link.determine_geometry((pt1, pt2))
                link.add_attribute("LinkID", counter)
                link.add_attribute("v1", v1)
                link.add_attribute("v2", v2)
                link.add_attribute("Length", lenght)
                self.scenario.add_asset("LinkID" + str(counter), link)

        vertices.keys().sort()

        print ("Printing undirected graph....", len(edges))
        print ([str(e)+"/t" for e in edges])
        print("vertices " + str(vertices))
        return vertices, edges

    def spanning_tree(self, vertices, edges):
        a = vertices.keys()[randint(0, len(vertices.keys()))]  # starting node
        k = None  # Current node
        p = {}  # Dictionary of predecessor nodes
        b = {}  # Weight of an edge (in this case the lenght of the pipe between the centroids of adjacent blocks)

        M = []  # List of neighbours (Block IDs) that have not being visit
        L = []  # List of nodes (block IDs) in the spanning tree

        links = self.scenario.get_assets_with_identifier("LinkID")

        k = a
        p[a] = a

        while k:

            tempK = {}
            L.append(k)
            print("L: ", L)

            for i in edges.keys():
                if k != i[0] and k != i[1]:
                    continue
                if k == i[0]:
                    if i[1] not in M and i[1] not in L:
                        M.append(i[1])
                elif k == i[1]:
                    if i[0] not in M and i[0] not in L:
                        M.append(i[0])

            print ("M: ", M)


            for j in M:

                if (k, j) in edges.keys():
                    lenght = edges[(k, j)] # Weight of an edge (in this case the lenght of the pipe between the centroids of adjacent blocks)
                elif (j, k) in edges.keys():
                    lenght = edges[(j, k)]
                else:
                    continue

                if j not in b.keys():
                    b[j] = lenght
                    p[j] = k
                    tempK[j] = b[j]
                if lenght < b[j]:
                    b[j] = lenght
                    p[j] = k
                    tempK[j] = b[j]
            print("tempK:", tempK)
            if tempK:
                minB = tempK.values().index(min(tempK.values()))
                k = M.pop(M.index(tempK.keys()[minB]))
            else:
                if M:
                    k = M.pop(0)
                else:
                    if len(L) < len(vertices.keys()):

                        for v in vertices.keys():
                            if v not in L:
                                k = v
                                break

                        # randID = randint(0, len(missVert))
                        # k = missVert[randID] #missing blocks to connect

                    else:
                        k = None

        print(p)

        for i in range(len(p.keys())):

            v1 = p.keys()[i]
            v2 = p.values()[i]

            pt1 = vertices[v1]
            pt2 = vertices[v2]

            if v2 in b.keys():
                lenght = b[v2]
            else:
                lenght = 0


            link = ubdata.UBVector((pt1, pt2))
            link.determine_geometry((pt1, pt2))
            link.add_attribute("MST_ID", i)
            link.add_attribute("v1", v1)
            link.add_attribute("v2", v2)
            link.add_attribute("Length", lenght)
            self.scenario.add_asset("MST_ID" + str(i), link)

        return True

    # def undirected_graph_(self, swwblocks):
    #
    #     # Create an empty undirected weighted graph
    #     graph = UnDirectedWeightedGraph(len(swwblocks))
    #     counter = 0
    #     vertices = []
    #     coun = 0
    #
    #     # Create all unweighted vertices of the graph
    #     for b in swwblocks:
    #         v1 = b.get_attribute("BlockID")
    #
    #         if v1 in vertices:
    #             for k in range(len(graph.get_vertices())):
    #                 v = graph.get_vertices()[k]
    #                 if v is None:
    #                     continue
    #                 v_name = v.__getattribute__("vertex_name")
    #                 if v_name == v1:
    #                     vertex1 = graph.get_vertices()[k]
    #                     break
    #         else:
    #             # Create vertex
    #             vertex1 = GraphVertex(graph, v1)
    #             # Add vertex
    #             graph.add_vertex(vertex1)
    #             coun += 1
    #             vertices.append(v1)
    #         # print("V1 " + str(coun) + " : " + str(vertex1))
    #
    #         x1 = b.get_attribute("CentreX")
    #         vertex1.__setattr__("CentreX", x1)
    #         y1 = b.get_attribute("CentreY")
    #         vertex1.__setattr__("CentreY", y1)
    #
    #     # for g in graph.vertices:
    #     #     if g is None:
    #     #         continue
    #     #     print(g.__getattribute__("vertex_name"))
    #     #
    #     # for b in swwblocks:
    #     #     v1 = b.get_attribute("BlockID")
    #
    #
    #         # x1 = b.get_attribute("CentreX")
    #         # vertex1.__setattr__("CentreX", x1)
    #         # y1 = b.get_attribute("CentreY")
    #         # vertex1.__setattr__("CentreY", y1)
    #         # print("x,y : " + str(vertex1))
    #         pt1 = [x1, y1]
    #
    #         # List of Neighbours [id], [x], [y], [z]
    #         neighbours = self.get_sww_neighbours_z(b)
    #         for i in range(len(neighbours[0])):
    #
    #             v2 = neighbours[0][i]
    #
    #             if v2 in vertices:
    #                 for j in range(len(graph.get_vertices())):
    #                     v = graph.get_vertices()[j]
    #                     if v is None:
    #                         continue
    #                     v_name = v.__getattribute__("vertex_name")
    #                     if v_name == v2:
    #                         vertex2 = graph.get_vertices()[j]
    #                         break
    #
    #             else:
    #                 # Create vertex
    #                 vertex2 = GraphVertex(graph, v2)
    #                 # Add vertex
    #                 graph.add_vertex(vertex2)
    #                 vertices.append(v2)
    #                 coun += 1
    #
    #             # print("V2 " + str(coun) + " : " + str(vertex2))
    #
    #             # if graph.get_edge(vertex1, vertex2) or graph.get_edge(vertex2, vertex1):
    #             #     print("edge exists")
    #             #     continue
    #             e = graph.get_edge(vertex1, vertex2)
    #             f = graph.get_edge(vertex2, vertex1)
    #             if e is not None:
    #                 continue
    #             if f is not None:
    #                 continue
    #
    #             x2 = neighbours[1][i]
    #             vertex2.__setattr__("CentreX", x2)
    #             y2 = neighbours[2][i]
    #             vertex2.__setattr__("CentreY", y2)
    #             pt2 = [x2, y2]
    #             lenght = self.define_distance(pt1, pt2)
    #
    #
    #             # Add edges
    #             graph.add_edge(vertex1, vertex2, lenght)  # (A - B, weight)
    #             e = graph.get_edge(vertex1, vertex2)
    #             # print ("-->" + str(e.__str__()))
    #
    #             counter += 1
    #
    #             link = ubdata.UBVector((pt1, pt2))
    #             link.determine_geometry((pt1, pt2))
    #             link.add_attribute("LinkID", counter)
    #             link.add_attribute("v1", v1)
    #             link.add_attribute("v2", v2)
    #             link.add_attribute("Length", lenght)
    #             self.scenario.add_asset("LinkID" + str(counter), link)
    #
    #     print ("Printing undirected graph....", graph.get_number_of_vertices(), graph.get_number_of_edges())
    #     return graph
    #
    # def m_spanning_tree(self, graph):
    #     MST = GraphAlgorithms.prims_algorithm(graph, graph.get_vertex_at_index(0))
    #
    #     for i in range(len(MST.get_edges())):
    #         e = MST.edges.__dict__.items()
    #         print e
    #         vertex1 = e[0]
    #         vertex2 = e[1]
    #         weight = e[2]
    #
    #         print(vertex1, vertex2, weight)
    #
    #
    #     print(str(MST.get_total_weight()))
    #     print(str(MST.get_edges()))
    #     return MST

    def create_block_flow_hashtable(self, swwblocks):
        """Creates a hash table of BlockIDs for quick lookup, this allows the basin delineation algorithm to rapidly
        delineate the sub-catchment

        :param swwlinks: the list of UBVector() instances of all links in the sewer
        :return: a 2D list [ [upstreamID], [downstreamID] ]
        """

        hash_table = [[], []]     # COL#1: BlockID (upstream), COL#2: BlockID (downstream)
        for i in range(len(swwblocks)):
            current_block = swwblocks[i]
            current_id = current_block.get_attribute("BlockID")

            hash_table[0].append(int(current_id))
            hash_table[1].append(int(current_block.get_attribute("Sww_DownID")))    # [ID or -2]
        return hash_table

    def delineate_clustered_networks(self, swwblocks):
        """Delineates sub-basins across the entire blocksmap specified by the collection of blocks in 'swwlinks'.
        Returns the number of sub-basins in the map, but also writes BasinID information to each Block. Delineation is
        carried out by creating a hash table of BlockID and downstream ID.

        Each block is scanned and all its upstream and downstream Block IDs identified, each is also assigned a
        BasinID.

        :return: number of total basins. Also writes the "BasinID" attribute to each Block.
        """
        hash_table = self.create_block_flow_hashtable(swwblocks)    # Start by creating a hash tables
        print(hash_table)

        basin_id = 0    # Set Basin ID to zero, it will start counting up as soon as basins are found

        for i in range(len(swwblocks)):    # Loop  across all Blocks
            current_block = swwblocks[i]

            # Check if the Block is a single-basin Block
            current_id = current_block.get_attribute("BlockID")
            # if hash_table[1][hash_table[0].index(current_id)] == -1 and current_id == hash_table[0][hash_table[0].index(current_id)]:
            #     print("sink")
            # if current_id not in hash_table[1]:                 # If the current Block not downstream of something...
            if hash_table[1][hash_table[0].index(current_id)] == -1:
                current_block.add_attribute("SwwUpstrIDs", [])      # ...then it has NO upstream IDs (empty list)
                if current_id in hash_table[0]:                 # ... if it is in the first column of the hash table
                    if hash_table[0][hash_table[1].index(-1)] == current_id:    # if its second column is -1 (is a sink)
                        self.notify("Found a single sewer basin at SwwID"+str(current_id))
                        basin_id += 1   # Then we have found a single-block Basin
                        current_block.add_attribute("SwwBasinID", basin_id)
                        # print(current_id, current_block.get_attribute("SwwBasinID"))
                        current_block.add_attribute("SwwDownstrIDs", [])
                        current_block.add_attribute("SwwOutlet", 1)
                        continue

            # Search the current Block for its upstream IDs
            upstream_ids = [current_id]         # Otherwise current ID DOES have upstream blocks
            for uid in upstream_ids:             # Begin scanning! Note that upstream_ids will grow in length!
                for j in range(len(hash_table[1])):
                    if uid == hash_table[1][j]:
                        if hash_table[0][j] not in upstream_ids:    # Only want unique upstream_ids!
                            upstream_ids.append(hash_table[0][j])   # Slowly append more IDs to the hash_table

            # Once scan is complete, remove the current Block's ID from the list as it is NOT upstream of itself.
            upstream_ids.remove(current_id)
            self.notify("SwwID"+str(current_id)+" Upstream: "+str(upstream_ids))
            current_block.add_attribute("SwwUpstrIDs", upstream_ids)

            # Repeat the whole process now for the downstream IDs
            downstream_ids = [current_id]
            for uid in downstream_ids:
                for j in range(len(hash_table[0])):
                    if uid == hash_table[0][j]:
                        if hash_table[1][j] not in downstream_ids:
                            downstream_ids.append(hash_table[1][j])

            # Once scan is complete, remove the current Block's ID from the list as it is NOT downstream of itself.
            downstream_ids.remove(current_id)

            # downstream_ids.remove(-2)   # Also remove the -2, which is specified if the Outlet Block is found
            self.notify("SwwID"+str(current_id)+" Downstream: "+str(downstream_ids))
            current_block.add_attribute("SwwDownstrIDs", downstream_ids)

            # Now assign Basin IDs, do this if the current Block has downstream ID -1
            if hash_table[1][hash_table[0].index(current_id)] == -1:    # If the block is an outlet
                # print "Found a basin outlet at BlockID" + str(current_id)
                self.notify("Found a basin outlet at SwwID"+str(current_id))
                basin_id += 1
                current_block.add_attribute("SwwBasinID", basin_id)    # Set the current Basin ID
                # print(current_id, current_block.get_attribute("SwwBasinID"))
                current_block.add_attribute("SwwOutlet", 1)            # Outlet = TRUE at current Block
                for j in upstream_ids:
                    upblock = self.scenario.get_asset_with_name("BlockID"+str(int(j)))
                    upblock.add_attribute("SwwBasinID", basin_id)      # Assign basin ID to all upstream blocks
                    # print(j, upblock.get_attribute("SwwBasinID"))
                    upblock.add_attribute("SwwOutlet", 0)              # Upstream blocks are NOT outlets!


        swwlinks = self.scenario.get_assets_with_identifier("SwwID")

        for l in range(len(swwlinks)):
            swwlink = swwlinks[l]
            swwid = swwlink.get_attribute("DownID")

            block = self.scenario.get_asset_with_name("BlockID"+str(swwid))
            blockID = block.get_attribute("BlockID")
            if block.get_attribute("SwwBasinID") == None:
                print(swwid, "basin None")
            basin = block.get_attribute("SwwBasinID")
            outlet = block.get_attribute("SwwOutlet")
            upList = block.get_attribute("SwwDownstrIDs")
            downList =block.get_attribute("SwwUpstrIDs")
            swwlink.add_attribute("BasinID", block.get_attribute("SwwBasinID"))
            swwlink.add_attribute("Outlet", block.get_attribute("SwwOutlet"))
            swwlink.add_attribute("DownstrIDs", block.get_attribute("SwwDownstrIDs"))
            swwlink.add_attribute("UpstrIDs", block.get_attribute("SwwUpstrIDs"))


        self.notify("Total Basins in the Case Study: "+str(basin_id))
        print("Total Basins in the Case Study: " + str(basin_id))
        return basin_id     # The final count indicates how many basins were found


