# --- PYTHON LIBRARY IMPORTS ---
import threading
import os
import gc
import tempfile
import math

# --- URBANBEATS LIBRARY IMPORTS ---
from model.modules.ubmodule import *
from model.modules.md_delinblocks import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
import model.progref.ubglobals as ubglobals


# --- MODULE CLASS DEFINITION ---
class Sww_Infrastructure(UBModule):
    """ TECHNOLOGY PLANNING AND IMPLEMENTATION MODULE
    Performs the classical spatial allocation of infrastructure algorithm.
    Also performs the implementation depending on the simulation type.
    """
    def __init__(self, activesim, scenario, datalibrary, projectlog, simulationyear):
        UBModule.__init__(self)
        self.name = "sww Infrastructure"
        self.simulationyear = simulationyear

        # CONNECTIONS WITH CORE SIMULATION
        self.activesim = activesim              # active simulation
        self.scenario = scenario                # current scenario
        self.datalibrary = datalibrary          # input data
        self.projectlog = projectlog            # current project

        # PARAMETER LIST DEFINITION
        self.create_parameter("generate_wastewater", BOOL, "boolean for whether to run wastewater algorithms.")
        self.generate_wastewater = 1

        self.map_attr = []
        self.blocks = []

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
        for b in self.blocks:
            print("Current Block", b.get_attribute("BlockID"))
            print(b.get_attribute("MinElev"))
        return True

    def find_upstream_d8(self, z, nhd_z):
        """Uses the standard D8 method to find the upstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [NHD_Z - Z] and is
        positive if the neighbouring Block has a higher elevation than the central Block.

        :param z: elevation of the current central Block
        :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return: up_id: block ID that water drains to, max(dz) the largest elevation difference.
        """
        dz = []
        for i in range(len(nhd_z[1])):
            dz.append(nhd_z[1][i] - z)     # Calculate the elevation difference
        if max(dz) > 0:    # If there is a drop in elevation - this also means the area cannot be flat!
            up_id = nhd_z[0][dz.index(max(dz))]    # The ID corresponds to the maximum elevation difference
        else:
            up_id = -9999  # Otherwise there is a sink in the current Block
        return up_id, max(dz)

    def delineate_sww_flow_paths(self):
        """Delineates the flow paths according to the chosen method and saves the information to the blocks.

        :param blockslist: a list [] of UBVector instances representing the Blocks
        :param map_attr:  the global map attributes object
        :return: all data is saved to the UBVector instances as new Block data.
        """
        sink_ids = []
        river_blocks = []
        lake_ids = []
        wwtp_ids = []

        blockslist = self.blocks

        for i in range(len(blockslist)):
            current_block = blockslist[i]
            current_blockid = current_block.get_attribute("BlockID")

            # SKIP CONDITION 1 - Block has zero status
            if current_block.get_attribute("Status") == 0:
                continue

            # SKIP CONDITION 2 - Block already contains a river
            # if current_block.get_attribute("HasRiver") and not self.ignore_rivers:
            #     current_block.add_attribute("downID", -2)   # Immediately assign it the -2 value for downID
            #     current_block.add_attribute("max_dz", 0)
            #     current_block.add_attribute("avg_slope", 0)
            #     current_block.add_attribute("h_pond", 0)  # Only for sink blocks will height of ponding h_pond > 0
            #     river_blocks.append(current_block)
            #     continue

            # SKIP CONDITION 3 - Block contains a lake
            # if current_block.get_attribute("HasLake") and not self.ignore_lakes:
            #     current_block.add_attribute("downID", -2)  # Immediately assign it the -2 value for downID
            #     current_block.add_attribute("max_dz", 0)
            #     current_block.add_attribute("avg_slope", 0)
            #     current_block.add_attribute("h_pond", 0)  # Only for sink blocks will height of ponding h_pond > 0
            #     lake_ids.append(current_blockid)
            #     continue

            z = current_block.get_attribute("MinElev")

            # Get the neighbouring elevations. This is either the full neighbourhood if we are not using natural or
            # built features as a guide, or the full neighbourhood if neither features are in adjacent neighbour blocks.
            # Otherwise the neighbour_z array will have only as many options as there are neighbours with natural or
            # built features.

            # if self.guide_natural or self.guide_built:      # If we use natural or built features as a guide, then...
            #     neighbours_z = self.get_modified_neighbours_z(current_block)    # Returns [[BlockID], [Elevation]]
            #     if neighbours_z is None:        # If the current block has no natural or built features adjacent...
            #         neighbours_z = self.scenario.retrieve_attribute_value_list("Block", "MinElev",
            #                                                                    current_block.get_attribute(
            #                                                                        "Neighbours"))
            # else:
            neighbours_z = self.scenario.retrieve_attribute_value_list("Block", "MinElev",
                                                                       current_block.get_attribute("Neighbours"))
            print("Neighbour Z: ", neighbours_z)

            # Find the downstream block unless it's a sink
            flow_id, max_zdrop = self.find_upstream_d8(z, neighbours_z)

            # if self.flowpath_method == "D8":
            #     flow_id, max_zdrop = self.find_downstream_d8(z, neighbours_z)
            # elif self.flowpath_method == "DI" and self.neighbourhood == "M":
            #     # Only works for the Moore neighbourhood
            #     flow_id, max_zdrop = self.find_downstream_dinf(z, neighbours_z)
            # else:
            #     self.flowpath_method = "D8"     # Reset to D8 by default
            #     flow_id, max_zdrop = self.find_downstream_d8(z, neighbours_z)

            if flow_id == -9999:     # if no flowpath has been found
                sink_ids.append(current_blockid)
                upstream_id = -1  # Block is a possible sink. if -2 --> block is a catchment outlet
            else:
                upstream_id = flow_id

            # Grab distances / slope between two Block IDs
            if flow_id == -9999:
                avg_slope = 0
            else:
                down_block = self.scenario.get_asset_with_name("BlockID" + str(upstream_id))
                dx = current_block.get_attribute("CentreX") - down_block.get_attribute("CentreX")
                dy = current_block.get_attribute("CentreY") - down_block.get_attribute("CentreY")
                dist = float(math.sqrt((dx * dx) + (dy * dy)))
                avg_slope = max_zdrop / dist

            # Add attributes
            current_block.add_attribute("upID", upstream_id)
            current_block.add_attribute("max_dz", max_zdrop)
            current_block.add_attribute("avg_slope", avg_slope)
            # current_block.add_attribute("h_pond", 0)    # Only for sink blocks will height of ponding h_pond > 0

            # Draw Networks
            # if upstream_id != -1 and upstream_id != 0:
            #     network_link = self.draw_sewer_lines(current_block, 1)
            #     self.scenario.add_asset("FlowID"+str(current_blockid), network_link)

        # Unblock the Sinks
        # self.unblock_sinks(sink_ids)

        # if map_attr.get_attribute("HasRIVER"):
        #     self.connect_river_blocks(river_blocks)   # [TO DO]
        return True
