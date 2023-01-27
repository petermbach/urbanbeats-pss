r"""
@file   mod_catchmentdelin.py
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
import model.ublibs.ubdatatypes as ubdata
import model.ublibs.ubspatial as ubspatial

import numpy as np
from shapely.geometry import Polygon, LineString

class DelineateFlowSubCatchments(UBModule):
    """ Delineates water flow paths and sub-catchments across the simulation grid. These flowpaths are topogrpahically
    based but can also be guided by the presence of natural features or input data sets to help the delineation. Finds
    outlets in the simulation grid."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Urban Hydrology"
    catorder = 2
    longname = "Flow Paths & Sub-catchments"
    icon = ":/icons/river_flow.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES
        self.assets = None
        self.griditems = None
        self.meta = None
        self.xllcorner = None
        self.yllcorner = None
        self.assetident = ""
        self.nodata = None
        self.asset_drain_map = []

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.assetcolname = "(select asset collection)"

        self.create_parameter("flowpath_method", STRING, "flowpath method to use")
        self.create_parameter("guide_natural", BOOL, "Use natural features to guide delineation")
        self.create_parameter("guide_built", BOOL, "Use built drainage features to guide delineation")
        self.create_parameter("built_map", STRING, "DataID for the built infrastructure map to use as guide")
        self.create_parameter("ignore_rivers", BOOL, "Ignore rivers in delineation of outlets")
        self.create_parameter("ignore_lakes", BOOL, "Ignore lake features in the delineation of outlets")
        self.flowpath_method = "D8"     # D-inf, D8, LCP
        self.guide_natural = 0
        self.guide_built = 0
        self.built_map = "(select built infrastructure map)"
        self.ignore_rivers = 0
        self.ignore_lakes = 0

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")
            return False

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
            return False

        # Pre-requisite - needs to have at least the elevation mapping done
        if self.meta.get_attribute("mod_topography") != 1:
            self.notify("Cannot start module! No elevation data. Please run the Map Topography module first")
            return False

        # Check if the asset collection already has Flowpath Assets, if yes, remove them
        flowpath_count = 0
        flowpath_assets = self.assets.get_assets_with_identifier("FlowpathID")
        for i in range(len(flowpath_assets)):
            self.assets.remove_asset_by_name(flowpath_assets[i].get_attribute("FlowpathID"))
            flowpath_count += 1
        self.notify("Removed "+str(flowpath_count)+" flowpath assets.")

        # CLEAN THE ATTRIBUTES LIST
        att_schema = ["Outlet", "BasinID", "DownstrIDs", "UpstrIDs", "h_pond", "avg_slope", "max_dz", "downID",
                      "HasDrain"]
        grid_assets = self.assets.get_assets_with_identifier(self.assetident)
        att_reset_count = 0
        for i in range(len(grid_assets)):
            for att in att_schema:
                if grid_assets[i].remove_attribute(att):
                    att_reset_count += 1
        self.notify("Removed "+str(att_reset_count)+" attribute entries.")

        self.meta.add_attribute("mod_catchmentdelin", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")
        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")
        return True

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.notify_progress(0)
        if not self.initialize_runstate():
            self.notify("Module run terminated!")
            return True

        self.notify("Delineating flow paths and sub-catchments")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)

        # --- SECTION 1 - Grab asset information
        self.griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets within the map: "+str(len(self.griditems)))
        self.notify_progress(10)

        # --- SECTION 2 - If built-infrastructure is included to guide the delineation, grab this information first
        if self.guide_built:
            self.find_stormdrains_in_assets()       # Adds the "HasDrain" attribute
        self.notify_progress(40)

        # --- SECTION 3 - Flowpath Delineation
        if self.assetident in ["BlockID", "HexID", "GeohashID"]:        # REGULAR GRID
            self.notify("Regular Grid, running D8/D6 Flowpath Delineation")
            self.assets.add_asset_type("Flowpath", "Line")
            self.regular_grid_flowpath_delineation()
        elif self.assetident in ["PatchID", "ParcelID"]:        # IRREGULAR GRID
            self.notify("Irregular Grid, running graph-based Flowpath Delineation")

        else:
            self.notify("Raster Grid, mapping flow directions")

        self.notify_progress(70)

        # --- SECTION 4 - Sub-catchment Delineation
        if self.assetident in ["BlockID", "HexID", "GeohashID"]:        # REGULAR GRID
            self.notify("Delineating sub-catchments for Regular Grid")
            totalbasins = self.delineate_basin_structures()  # Delineates the sub-catchments
        elif self.assetident in ["PatchID", "ParcelID"]:  # IRREGULAR GRID
            self.notify("Delineating sub-catchments for Irregular Grid")
        else:
            self.notify("Raster Grid, mapping basins")

        self.notify_progress(80)

        self.notify("Flowpath and catchment delineation complete")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def find_stormdrains_in_assets(self):
        """Intersects all Blocks with all loaded infrastructure data and collates a list of simgrid items that contain
        a stormwater/wastewater drainage network that will aid the delineation of flowpaths and sub-catchments."""
        drainmap = self.datalibrary.get_data_with_id(self.built_map)
        filename = drainmap.get_metadata("filename")
        fullpath = drainmap.get_data_file_path() + filename
        self.notify("Loading Drainage Map: "+str(filename))

        drainfeats = ubspatial.import_linear_network(fullpath, "LINES", (self.xllcorner, self.yllcorner))
        self.notify("Total Drainage Features to check: "+str(len(drainfeats)))

        assets_with_drainage_data = []
        for i in range(len(self.griditems)):
            curasset = self.griditems[i]
            curassetid = curasset.get_attribute(self.assetident)
            if curasset.get_attribute("Status") == 0:
                continue
            coordinates = curasset.get_points()
            gridpoly = Polygon([(c[0], c[1]) for c in coordinates])

            hasdrain = 0
            for j in range(len(drainfeats)):
                path = LineString(drainfeats[j].get_points())
                if not path.intersects(gridpoly):
                    continue
                else:
                    hasdrain = 1
                    break       # As soon as one drainage line has been identified, continue
            curasset.add_attribute("HasDrain", hasdrain)
        return True

    def regular_grid_flowpath_delineation(self):
        """Delineates the flow paths according to the chosen method and saves the information to the blocks.

        :return: all data is saved to the UBVector instances as new Asset data.
        """
        sink_ids = []
        river_blocks = []
        lake_ids =[]

        for i in range(len(self.griditems)):
            curasset = self.griditems[i]
            curassetid = curasset.get_attribute(self.assetident)

            # SKIP CONDITION 1 - Zero Status
            if curasset.get_attribute("Status") == 0:
                continue

            # Remember: if the Mapping of Natural Features module has not been run, then HasRiver and HasLake will both
            # be None types and will register as False

            # SKIP CONDITION 2 - Contains a river and we do not ignore it
            if curasset.get_attribute("HasRiver") and not self.ignore_rivers:
                curasset.add_attribute("downID", -2)  # Immediately assign it the -2 value for downID
                curasset.add_attribute("max_dz", 0)
                curasset.add_attribute("avg_slope", 0)
                curasset.add_attribute("h_pond", 0)  # Only for sink blocks will height of ponding h_pond > 0
                river_blocks.append(curasset)
                continue

            # SKIP CONDITION 3 - Contains a lake and we do not ignore it
            if curasset.get_attribute("HasLake") and not self.ignore_lakes:
                curasset.add_attribute("downID", -2)  # Immediately assign it the -2 value for downID
                curasset.add_attribute("max_dz", 0)
                curasset.add_attribute("avg_slope", 0)
                curasset.add_attribute("h_pond", 0)  # Only for sink blocks will height of ponding h_pond > 0
                lake_ids.append(curasset)
                continue

            z = curasset.get_attribute("Elev_Avg")

            # Get the neighbouring elevations. This is either the full neighbourhood if we are not using natural or
            # built features as a guide, or the full neighbourhood if neither features are in adjacent neighbour blocks.
            # Otherwise the neighbour_z array will have only as many options as there are neighbours with natural or
            # built features.
            if self.guide_natural or self.guide_built:      # If we use natural or built features as a guide, then...
                neighbours_z = self.get_modified_neighbours_z(curasset) # ret. [[ID], [Elevation]]
                if neighbours_z is None:        # If the current asset has no natural or built features adjacent...
                    neighbours_z = self.assets.retrieve_attribute_value_list(self.assetident, "Elev_Avg",
                                                                               curasset.get_attribute(
                                                                                   "Neighbours"))
            else:
                neighbours_z = self.assets.retrieve_attribute_value_list(self.assetident, "Elev_Avg",
                                                                           curasset.get_attribute("Neighbours"))
            print(f"Neighbour Z: {neighbours_z}")

            # Find the downstream block unless it's a sink
            # Consider adding future methods into the model, but for now stick to the standard D8/D6
            flow_id, max_zdrop = self.find_downstream_d8(z, neighbours_z)

            if flow_id == -9999:  # if no flowpath has been found
                sink_ids.append(curassetid)
                downstream_id = -1  # Block is a possible sink. if -2 --> block is a catchment outlet
            else:
                downstream_id = flow_id

            # Grab distances / slope between two Block IDs
            if flow_id == -9999:
                avg_slope = 0
            else:
                down_block = self.assets.get_asset_with_name(self.assetident + str(downstream_id))
                dx = curasset.get_attribute("CentreX") - down_block.get_attribute("CentreX")
                dy = curasset.get_attribute("CentreY") - down_block.get_attribute("CentreY")
                dist = float(np.sqrt((dx * dx) + (dy * dy)))
                avg_slope = max_zdrop / dist

            # Add attributes
            curasset.add_attribute("downID", downstream_id)
            curasset.add_attribute("max_dz", max_zdrop)
            curasset.add_attribute("avg_slope", avg_slope)
            curasset.add_attribute("h_pond", 0)  # Only for sink blocks will height of ponding h_pond > 0

            # Draw Networks
            if downstream_id != -1 and downstream_id != 0:
                network_link = self.draw_flow_path(curasset, "Draining", "Centre")
                self.assets.add_asset("FlowpathID" + str(curassetid), network_link)

        # Unblock the Sinks
        self.unblock_sinks(sink_ids, "Centre")

        if self.meta.get_attribute("mod_natural_features"):     # If the natural features module was run...
            self.connect_river_assets(river_blocks)  # [TO DO]
        return True

    def get_modified_neighbours_z(self, curasset):
        """Retrieves the z-values of all adjacent blocks within the current block's neighbourhood accounting for
        the presence of drainage infrastructure or natural features.

        :param curasset: the current block UBVector() instance
        :return: a list of z-values for all the block's neighbours [ [BlockID], [Z-value] ], None otherwise
        """
        nhd = curasset.get_attribute("Neighbours")
        nhd_z = [[], []]
        # Scan neighbourhood for Blocks with Rivers/Lakes
        for n in nhd:
            nblock = self.assets.get_asset_with_name(self.assetident + str(n))
            if self.guide_natural:
                if nblock.get_attribute("HasRiver") or nblock.get_attribute("HasLake"):
                    nhd_z[0].append(n)
                    nhd_z[1].append(nblock.get_attribute("Elev_Avg"))
            if self.guide_built:
                if nblock.get_attribute("HasDrain") and n not in nhd_z[0]:
                    nhd_z[0].append(n)
                    nhd_z[1].append(nblock.get_attribute("Elev_Avg"))
        if len(nhd_z[0]) == 0:
            return None
        else:
            return nhd_z

    def connect_river_assets(self, river_blocks):
        """Scans the blocks for those containing a river system and connects them based on adjacency and river
        rules.

        :param river_blocks: the list () of block UBVector() instances with HasRiver == 1.
        :return: Each block is given a new attribute specifying the Block containing a river that it drains into
        """
        # Connect blocks in logical order, probably based on the linestrings of the river
        pass    # Scan block list, if HasRiver true, then check neighbours, if they have river and river name is
                # identical, connect, otherwise specify -1 as unconnected
        return True # [TO DO]

    def unblock_sinks(self, sink_ids, pt_attribute):
        """Runs the algorithm for scanning all sink blocks and attempting to find a flowpath beyond them.
        This function may also identify certain sinks as definitive catchment outlets.

        :param blockslist: the list [] of block UBVector instances
        :param sink_ids: a list of BlockIDs where a sink is believe to exist based on the flowpath method.
        :return: adds new assets to the scenario if a flowpath has been found for the sinks
        """
        print("Sink IDs", sink_ids)
        for i in range(len(sink_ids)):
            current_sinkid = sink_ids[i]
            self.notify("Attemtping to unblock flow from "+ self.assetident + str(current_sinkid))
            curasset = self.assets.get_asset_with_name(self.assetident + str(current_sinkid))

            if curasset.get_attribute("HasRiver") or curasset.get_attribute("HasLake"):
                # If the Block is a river or lake block, do not attempt to unblock it
                curasset.set_attribute("downID", -2)  # signifies that Block is an outlet
                continue

            z = curasset.get_attribute("Elev_Avg")
            nhd = curasset.get_attribute("Neighbours")
            possible_id_drains = []
            possible_id_z = []
            possibility = 0

            for j in nhd:
                nhd_blk = self.assets.get_asset_with_name(self.assetident+str(j))
                if nhd_blk.get_attribute("Status") == 0:
                    continue    # Continue if nhd block has zero status

                nhd_downid = nhd_blk.get_attribute("downID")
                if nhd_downid not in [current_sinkid, -1] and nhd_downid not in nhd:
                    possible_id_drains.append(j)
                    possible_id_z.append(nhd_blk.get_attribute("Elev_Avg") - z)
                    possibility += 1

            if possibility > 0:
                sink_path = min(possible_id_z)
                sink_to_id = possible_id_drains[possible_id_z.index(sink_path)]

                curasset.set_attribute("downID", sink_to_id)   # Overwrite -1 to new ID
                curasset.set_attribute("h_pond", sink_path)    # If ponding depth > 0, then there was a sink
                network_link = self.draw_flow_path(curasset, "Ponded", pt_attribute)
                self.assets.add_asset("FlowpathID" + str(curasset.get_attribute(self.assetident)), network_link)
            else:
                curasset.set_attribute("downID", -2)   # signifies that Block is an outlet
        return True

    def draw_flow_path(self, curasset, flow_type, pt_attribute):
        """Creates the flowpath geometry and returns a line asset, which can be saved to the scenario.

        :param curasset: current ID of the block that the flowpath is being drawn for
        :param flow_type: type of flowpath e.g. "Regular", "Ponded"
        :param pt_attribute: prefix denoting the centroid X Y attribute name e.g. CentreX for Blocks
        :return: UBVector() instance of a network link
        """
        current_id = curasset.get_attribute(self.assetident)
        downstream_id = curasset.get_attribute("downID")
        down_block = self.assets.get_asset_with_name(self.assetident+str(downstream_id))

        x_up = curasset.get_attribute(pt_attribute+"X")
        y_up = curasset.get_attribute(pt_attribute+"Y")
        z_up = curasset.get_attribute("Elev_Avg")
        up_point = (x_up, y_up, z_up)

        x_down = down_block.get_attribute(pt_attribute+"X")
        y_down = down_block.get_attribute(pt_attribute+"Y")
        z_down = down_block.get_attribute("Elev_Avg")
        down_point = (x_down, y_down, z_down)

        network_link = ubdata.UBVector((up_point, down_point))
        network_link.determine_geometry()
        network_link.add_attribute("FlowpathID", current_id)
        network_link.add_attribute(self.assetident, current_id)
        network_link.add_attribute("DownID", downstream_id)
        network_link.add_attribute("Z_up", z_up)
        network_link.add_attribute("Z_down", z_down)
        network_link.add_attribute("max_zdrop", curasset.get_attribute("max_dz"))
        network_link.add_attribute("LinkType", flow_type)
        network_link.add_attribute("AvgSlope", curasset.get_attribute("avg_slope"))
        network_link.add_attribute("h_pond", curasset.get_attribute("h_pond"))
        return network_link

    def find_downstream_d8(self, z, nhd_z):
        """Uses the standard D8 method to find the downstream neighbouring block. Return the BlockID
        and the delta-Z value of the drop. Elevation difference is calculated as dz = [NHD_Z - Z] and is
        negative if the neighbouring Block has a lower elevation than the central Block.

        :param z: elevation of the current central Block
        :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return: down_id: block ID that water drains to, min(dz) the largest elevation difference.
        """
        dz = []
        for i in range(len(nhd_z[1])):
            dz.append(nhd_z[1][i] - z)     # Calculate the elevation difference
        if min(dz) < 0:    # If there is a drop in elevation - this also means the area cannot be flat!
            down_id = nhd_z[0][dz.index(min(dz))]    # The ID corresponds to the minimum elevation difference
        else:
            down_id = -9999  # Otherwise there is a sink in the current Block
        return down_id, min(dz)

    def delineate_basin_structures(self):
        """Delineates sub-basins across the entire blocksmap specified by the collection of blocks in 'blockslist'.
        Returns the number of sub-basins in the map, but also writes BasinID information to each Block. Delineation is
        carried out by creating a hash table of BlockID and downstream ID.

        Each block is scanned and all its upstream and downstream Block IDs identified, each is also assigned a
        BasinID.

        :param blocklist: the list [] of UBVector() instances that represent Blocks
        :return: number of total basins. Also writes the "BasinID" attribute to each Block.
        """
        hash_table = self.create_flowpath_hashtable()  # Start by creating a hash tables
        basin_id = 0  # Set Basin ID to zero, it will start counting up as soon as basins are found

        for i in range(len(self.griditems)):  # Loop  across all Blocks
            curasset = self.griditems[i]
            if curasset.get_attribute("Status") == 0:
                continue  # Skip if Status = 0

            # Check if the Block is a single-basin Block
            curassetid = curasset.get_attribute(self.assetident)
            if curassetid not in hash_table[1]:  # If the current Block not downstream of something...
                curasset.add_attribute("UpstrIDs", [])  # ...then it has NO upstream IDs (empty list)
                if curassetid in hash_table[0]:  # ... if it is in the first column of the hash table
                    if hash_table[1][hash_table[0].index(curassetid)] == -2:  # if its second column is -2
                        self.notify("Found a single unit basin at "+ self.assetident + str(curassetid))
                        basin_id += 1  # Then we have found a single-block Basin
                        curasset.add_attribute("BasinID", basin_id)
                        curasset.add_attribute("DownstrIDs", [])
                        curasset.add_attribute("Outlet", 1)
                        continue

            # Search the current Block for its upstream IDs
            upstream_ids = [curassetid]  # Otherwise current ID DOES have upstream blocks
            for uid in upstream_ids:  # Begin scanning! Note that upstream_ids will grow in length!
                for j in range(len(hash_table[1])):
                    if uid == hash_table[1][j]:
                        if hash_table[0][j] not in upstream_ids:  # Only want unique upstream_ids!
                            upstream_ids.append(hash_table[0][j])  # Slowly append more IDs to the hash_table

            # Once scan is complete, remove the current Block's ID from the list as it is NOT upstream of itself.
            upstream_ids.remove(curassetid)
            self.notify(self.assetident + str(curassetid) + " Upstream: " + str(upstream_ids))
            curasset.add_attribute("UpstrIDs", upstream_ids)

            # Repeat the whole process now for the downstream IDs
            downstream_ids = [curassetid]
            for uid in downstream_ids:
                for j in range(len(hash_table[0])):
                    if uid == hash_table[0][j]:
                        if hash_table[1][j] not in downstream_ids:
                            downstream_ids.append(hash_table[1][j])

            # Once scan is complete, remove the current Block's ID from the list as it is NOT downstream of itself.
            downstream_ids.remove(curassetid)
            # downstream_ids.remove(-2)   # Also remove the -2, which is specified if the Outlet Block is found
            self.notify(self.assetident + str(curassetid) + " DownstreamL " + str(downstream_ids))
            curasset.add_attribute("DownstrIDs", downstream_ids)

            # Now assign Basin IDs, do this if the current Block has downstream ID -2
            if hash_table[1][hash_table[0].index(curassetid)] == -2:  # If the block is an outlet
                self.notify("Found a basin outlet at " + self.assetident + str(curassetid))
                basin_id += 1
                curasset.add_attribute("BasinID", basin_id)  # Set the current Basin ID
                curasset.add_attribute("Outlet", 1)  # Outlet = TRUE at current Block
                for j in upstream_ids:
                    upblock = self.assets.get_asset_with_name(self.assetident + str(j))
                    upblock.add_attribute("BasinID", basin_id)  # Assign basin ID to all upstream blocks
                    upblock.add_attribute("Outlet", 0)  # Upstream blocks are NOT outlets!

        self.notify("Total Basins in the Case Study: " + str(basin_id))
        print(f"Total Basins in the Case Study: {basin_id}")
        return basin_id  # The final count indicates how many basins were found

    def create_flowpath_hashtable(self):
        """Creates a hash table of AssetIDs for quick lookup, this allows the basin delineation algorithm to rapidly
        delineate the sub-catchment

        :return: a 2D list [ [upstreamID], [downstreamID] ]
        """
        hash_table = [[], []]     # COL#1: ID (upstream), COL#2: ID (downstream)
        for i in range(len(self.griditems)):
            curasset = self.griditems[i]
            curassetid = curasset.get_attribute(self.assetident)
            if curasset.get_attribute("Status") == 0:
                continue
            hash_table[0].append(curassetid)
            hash_table[1].append(curasset.get_attribute("downID"))    # [ID or -2]
        return hash_table

    # FUTURE - [TO DO] - D-inf Code
    def find_downstream_dinf(self, z, nhd_z):
        """Adapted D-infinity method to only direct water in one direction based on the steepest slope
        of the 8 triangular facets surrounding a Block's neighbourhood and a probabilistic choice weighted
        by the propotioning of flow. This is the stochastic option of flowpath delineation for UrbanBEATS
        and ONLY works with the Moore neighbourhood.

        :param z: elevation of the current central Block
        :param nhd_z: :param nhd_z: elevation of all its neighbours and corresponding IDs [[IDs], [Z-values]]
        :return:
        """
        pass    # [TO DO]
        # FROM LEGACY CODE
        # facetdict = {}  # Stores all the information about the 8 facets
        # facetdict["e1"] = ["E", "N", "N", "W", "W", "S", "S", "E"]
        # facetdict["e2"] = ["NE", "NE", "NW", "NW", "SW", "SW", "SE", "SE"]
        # facetdict["ac"] = [0, 1, 1, 2, 2, 3, 3, 4]
        # facetdict["af"] = [1, -1, 1, -1, 1, -1, 1, -1]
        # cardin = {"E": 0, "NE": 1, "N": 2, "NW": 3, "W": 4, "SW": 5, "S": 6, "SE": 7}
        #
        # e0 = currentZ  # CONSTANT PARAMETERS (because of constant block grid and centre point)
        # d1 = blocksize
        # d2 = d1
        # facetangles = [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi, 5 * math.pi / 4, 3 * math.pi / 2,
        #                7 * math.pi / 4]
        #
        # # Re-sort the neighbours matrix based on polar angle
        # sortedneighb = [neighboursZ[3], neighboursZ[4], neighboursZ[0], neighboursZ[5], neighboursZ[2], neighboursZ[7],
        #                 neighboursZ[1], neighboursZ[6]]
        # rmatrix = []
        # smatrix = []
        #
        # for i in range(len(sortedneighb)):  # Calculate slopes of all 8 facets
        #     currentfacet = i
        #
        #     e1 = sortedneighb[
        #         cardin[facetdict["e1"][currentfacet]]]  # e1 elevation:  (1) get cardinal direction from dictionary,
        #     #               (2) get the index from cardin and
        #     e2 = sortedneighb[cardin[facetdict["e2"][currentfacet]]]  # (3) get the value from neighbz
        #
        #     ac = facetdict["ac"][currentfacet]
        #     af = facetdict["af"][currentfacet]
        #
        #     s1 = (e0 - e1) / d1
        #     s2 = (e1 - e2) / d2
        #     r = math.atan(s2 / s1)
        #     s = math.sqrt(math.pow(s1, 2) + math.pow(s2, 2))
        #
        #     if r < 0:
        #         r = 0
        #         s = s1
        #     elif r > math.atan(d2 / d1):
        #         r = math.atan(d2 / d1)
        #         s = (e0 - e2) / math.sqrt(math.pow(d1, 2) + math.pow(d2, 2))
        #
        #     rmatrix.append(r)
        #     smatrix.append(s)
        #
        # # Find the maximum slope and get the angle
        # rmax = max(rmatrix)
        # rg = af * rmax + ac * math.pi / 2.0
        #
        # # Find the facet
        # for i in range(len(facetangles)):
        #     if rg > facetangles[i]:
        #         continue
        #     else:
        #         facet = i - 1
        #         theta1 = facetangles[i - 1]
        #         theta2 = facetangles[i]
        # # Adjust angles based on rg to get proportions
        # alpha1 = rg - theta1
        # alpha2 = theta2 - rg
        # p1 = alpha1 / (alpha1 + alpha2)
        # p2 = alpha2 / (alpha2 + alpha1)
        #
        # print(f"Proportioned Flows: {p1}, {p2}")
        #
        # if rand.random() < p1:
        #     choice = p1
        #     directionfacet = int(theta1 / (math.pi / 4))
        # else:
        #     choice = p2
        #     directionfacet = int(theta2 / (math.pi / 4))
        #
        # print(f"Choice: {choice}")
        #
        # direction = neighboursZ.index(sortedneighb[directionfacet - 1])
        # return direction, max_Zdrop
        return True