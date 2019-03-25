r"""
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
from shapely.geometry import Polygon, LineString, Point
from random import randint

# --- URBANBEATS LIBRARY IMPORTS ---
from model.modules.ubmodule import *
from model.modules.md_delinblocks import *
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
        # for b in self.blocks:
        #     print "Current Block", b.get_attribute("BlockID")
        #     print b.get_attribute("AvgElev")
        self.delineate_sww_flow_paths(self.blocks)

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

    def delineate_sww_flow_paths(self, blockslist):
        """Delineates the sewer network flow paths according to the chosen method and saves the information to the blocks.

        :param sww_blocks: a list [] of UBVector instances representing the Blocks
        :return: all data is saved to the UBVector instances as new Block data.
        """
        if not self.sewer:
            pass

        sww_blocks = []
        # Step 1 - Determine suitable blocks to place sewer networks.
        # No sewers when Population = 0 and there is no industry (total employees = 0)

        for current_block in blockslist:

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

        sinks = []
        river_blocks = []
        lake_ids = []

        sinks_list = self.identify_sinks(sww_blocks)
        print("SINKS: " + str(len(sinks_list)) + str(sinks_list))

        self.copy_DEM()
        for s in sinks_list:
            self.pfs_algorithm(s)

        ids = []
        for i in sww_blocks:
            ids.append(i.get_attribute("BlockID"))
        ids.sort()
        print(ids)


        # Step 2 - Detect the block with sewer facilities and save them as starting points
        # treatments = [(125, 6375)]    # (i, j) coordinates of the treatment facilities
        # treat_blocks = self.detect_treatment(sww_blocks, treatments)            # list of treatment facilities

        # Step 3 - Run delineation method to sww_blocks
        blocks_checked = []

        for i in range(len(sww_blocks)):
            current_block = sww_blocks[i]
            current_blockid = current_block.get_attribute("BlockID")
            print("CURRENT BLOCK >>> " + str(current_blockid))

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

            print("Neighbours: ", current_blockid, ndh_info[0])


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
            if downstream_id != -1 and downstream_id != 0:
                network_link = self.draw_sewer_lines_down(current_block, 1)
                self.scenario.add_asset("SwwID"+str(current_blockid), network_link)

        # connect the Sinks
        self.connect_sinks(sinks)
        print(len(blocks_checked))

        return True

    def get_sww_neighbours_z(self, curblock):
        """Retrieves the z-values of all adjacent blocks within the current block's neighbourhood accounting for
        the presence of drainage infrastructure or natural features.

        :param curblock: the current block UBVector() instance
        :return: a list of all the block's neighbours [[BlockID], [X], [Y], [Z], [direction]], None otherwise
        """
        nhd_ids = curblock.get_attribute("Neighbours")
        # print nhd_ids
        nhd_info = [[], [], [], []]  # Neighbours [[0=id], [1=x], [2=y], [3=z]]

        # Scan neighbourhood for Blocks with Rivers/Lakes

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

        # print curblock.get_attribute("BlockID"), nhd_info[0]

        if len(nhd_info[0]) == 0:
            return None
        else:
            return nhd_info

    def get_sww_modified_neighbours_z(self, curblock):
        """Retrieves the z-values of all adjacent blocks within the current block's neighbourhood accounting for
        the presence of drainage infrastructure or natural features.

        :param curblock: the current block UBVector() instance
        :return: a list of all the block's neighbours [[BlockID], [X], [Y], [Z], [direction]], None otherwise
        """
        nhd_ids = curblock.get_attribute("Neighbours")
        print(nhd_ids)
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

        print(curblock.get_attribute("BlockID"), nhd_info[0])

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
        min_elev = 99999
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

        print("FOR BLOCK: " + str(curblock[0]) + "DOWN ID: " + str(down_id) + " dz: " + str(dz))

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
        network_link.add_attribute("BlockID", current_id)
        network_link.add_attribute("FlowID", upstream_id)
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
        downstream_id = current_block.get_attribute("Sww_DownID")
        down_block = self.scenario.get_asset_with_name("BlockID"+str(downstream_id))

        # print(str(current_id) + " -> " + str(downstream_id))

        x_up = current_block.get_attribute("CentreX")
        y_up = current_block.get_attribute("CentreY")
        z_up = current_block.get_attribute("ModAvgElev")
        up_point = (x_up, y_up, z_up)

        x_down = down_block.get_attribute("CentreX")
        y_down = down_block.get_attribute("CentreY")
        z_down = down_block.get_attribute("ModAvgElev")
        down_point = (x_down, y_down, z_down)

        network_link = ubdata.UBVector((up_point, down_point))
        network_link.determine_geometry((up_point, down_point))
        network_link.add_attribute("SwwID", current_id)
        network_link.add_attribute("BlockID", current_id)
        network_link.add_attribute("FlowID", downstream_id)
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
            print("No treatment detected")
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

    def identify_closest_river(self, blockslist, current_block):
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
            print("No rivers detected")
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

            print("NHD " + str(nhd) +" Extended: " + str(extended_neighbours))

            minElev = z_b
            distance = 999999999
            lowest=999999
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
                print("Imprimiendo sinks... " + str(current_sinkid) + " -> " + str(lowest))
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

    def identify_sinks(self,blockslist):
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

    def pfs_algorithm(self, sink):
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
                    print("why is elev_n None?????")
                    continue

                dz = elev_n - elev_s

                if i in priority_queue or i in priority_tree:
                    continue

                priority_queue[0].append(i)
                priority_queue[1].append(dz)

            min_dz = 999999
            # id_min_dz = id
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
                b.set_attribute("ModAvgElev", elev_s - 0.0001)
                b.add_attribute("HasCarved", 1)
            elif min_dz < 0 and id_min_dz not in priority_tree:
                priority_tree.append(id_min_dz)
                id = None
            else:
                id = None
            #     print(" EXIST IN PRIORITY TREE----------------------------")

        return True
