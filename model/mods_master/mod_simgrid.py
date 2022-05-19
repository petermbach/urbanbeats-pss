r"""
@file   mod_simgrid.py
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
from shapely.geometry import Polygon, LineString, Point
from osgeo import ogr, osr
from geolib import geohash as gh
import math

from model.ubmodule import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubmethods as ubmethods
import model.ublibs.ubdatatypes as ubdata
import model.progref.ubglobals as ubglobals


class CreateSimGrid(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # --- MODULE'S BASIC METADATA ---
    type = "master"
    catname = "Spatial Representation"
    catorder = 1
    longname = "Create Simulation Grid"
    icon = ":/icons/Data-Grid-icon.png"
    prerequisites = []

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES HOLDING IMPORTANT REFERENCES TO SIMULATION - SET AT INITIALIZATION
        self.assets = None  # If used as one-off on-the-fly modelling, then scenario is None
        self.meta = None    # Simulation metadata contained in assets, this variable will hold it
        self.boundarydata = None    # The active boundary's dictionary data
        self.boundarypoly = None    # The Polygon() object of the simulation boundary

        self.mapwidth = None        # Map Geometry
        self.mapheight = None
        self.extents = None
        self.assetident = ""
        self.hexfactor = math.sqrt(3)

        # MODULE PARAMETERS
        self.create_parameter("gridname", STRING, "Name of the simulation grid, unique identifier used")
        self.create_parameter("boundaryname", STRING, "Name of the boundary the grid is based upon")
        self.create_parameter("geometry_type", STRING, "name of the geometry type the grid should use")
        self.gridname = "My_urbanbeats_grid"
        self.boundaryname = "(select simulation boundary)"
        self.geometry_type = "SQUARES"  # SQUARES, HEXAGONS, VECTORPATCH, RASTER

        # (1) Geometry Type: Square Blocks
        self.create_parameter("blocksize", DOUBLE, "Size of the square blocks")
        self.create_parameter("blocksize_auto", BOOL, "Determine the block size automatically?")
        self.blocksize = 500    # [m]
        self.blocksize_auto = 0

        # (2) Geometry Type: Hexagonal Blocks
        self.create_parameter("hexsize", DOUBLE, "Edge length of a single hexagonal block")
        self.create_parameter("hexsize_auto", BOOL, "Auto-determine the hexagonal edge length?")
        self.create_parameter("hex_orientation", STRING, "Orientation of the hexagonal block")
        self.hexsize = 300  # [m]
        self.hexsize_auto = 0
        self.hex_orientation = "NS"     # NS = north-south, EW = east-west

        # (3) Geometry Type: Patch/Irregular Block
        self.create_parameter("patchzonemap", STRING, "The zoning map that patch delineation is based on")
        self.create_parameter("disgrid_type", BOOL, "Use a discretization grid for the patch delineatioN?")
        self.create_parameter("disgrid_length", DOUBLE, "Edge length of the discretization grid")
        self.create_parameter("disgrid_auto", BOOL, "Auto-determine the size of the discretization grid?")
        self.create_parameter("disgrid_map", STRING, "The map for discretization")
        self.patchzonemap = "(select zoning map for patch delineation)"
        self.disgrid_type = "GRID"    # GRID, BOUND, NONE
        self.disgrid_length = 500   # [m]
        self.disgrid_auto = 0
        self.disgrid_map = "(select boundary for discretization)"

        # (4) Geometry Type: Raster/Fishnet
        self.create_parameter("rastersize", DOUBLE, "Resolution of the raster grid")
        self.create_parameter("nodatavalue", DOUBLE, "Identifier for the NODATAVALUE")
        self.create_parameter("generate_fishnet", BOOL, "Generate a fishnet of the raster?")
        self.rastersize = 30    # [m]
        self.nodatavalue = -9999
        self.generate_fishnet = 0

        # (5) Geometry Type: Geohash Grid
        self.create_parameter("geohash_lvl", DOUBLE, "Level of resolution for the geohash")
        self.geohash_lvl = 7

        # (6) Geometry Type: Parcels
        self.create_parameter("parcel_map", STRING, "Parcel Map to base the grid on")
        self.parcel_map = "(select parcel map)"

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.boundarydata = self.activesim.get_project_boundary_by_name(self.boundaryname)

        # Get the asset collection, if it doesn't yet exist, create it.
        self.assets = self.activesim.get_asset_collection_by_name(self.gridname)
        if self.assets is None:
            self.assets = ubdata.UBCollection(self.gridname, "Standalone")
            self.activesim.add_asset_collection_to_project(self.assets)
        else:
            self.assets.reset_assets()

        # Metadata check - Any module that creates a new asset collection should do this check
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:  # If there is currently no 'meta' object in the asset collection, make one
            self.meta = ubdata.UBComponent()  # Global Map Attributes if they do not yet exist
            self.assets.add_asset_type("Metadata", "-")
            self.assets.add_asset("meta", self.meta)  # Metadata info will now be stored as 'meta'
        self.meta.add_attribute("mod_simgrid", 1)  # This denotes that the module is going to be run
        return True

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Running SimGrid Creation for "+self.boundaryname)
        self.notify("--- === ---")
        self.notify_progress(0)

        # --- SECTION 1 - Preparation for creating the simulation grid based on the boundary map
        xmin, xmax, ymin, ymax = self.boundarydata["xmin"], self.boundarydata["xmax"], \
                                 self.boundarydata["ymin"], self.boundarydata["ymax"]
        self.extents = [xmin, xmax, ymin, ymax]
        self.mapwidth = xmax - xmin
        self.mapheight = ymax - ymin

        self.meta.add_attribute("xllcorner", xmin)
        self.meta.add_attribute("yllcorner", ymin)
        self.meta.add_attribute("mapwidth", self.mapwidth)
        self.meta.add_attribute("mapheight", self.mapheight)

        self.notify("Map Width [km] = "+str(self.mapwidth/1000.0))
        self.notify("Map Height [km] = "+str(self.mapheight/1000.0))
        self.notify("Extent Area WxH [km2] = "+str(self.mapwidth * self.mapheight / 1000000.0))

        # Get boundary shifted to (0,0) origin
        boundarygeom_z0 = []
        for coords in self.boundarydata["coordinates"]:
            boundarygeom_z0.append((coords[0] - xmin, coords[1] - ymin))
        self.boundarypoly = Polygon(boundarygeom_z0)

        # --- SECTION 2 - Create the grid - PROGRESS 20%
        self.notify("Creating Simulation Grid")
        self.notify_progress(20)

        if self.geometry_type == "SQUARES":
            self.assetident = "BlockID"
            self.create_square_simgrid()
        elif self.geometry_type == "HEXAGONS":
            self.assetident = "HexID"
            self.create_hexagon_simgrid()
        elif self.geometry_type == "VECTORPATCH":
            self.assetident = "PatchID"
            self.create_patch_simgrid()
        elif self.geometry_type == "RASTER":
            self.assetident = "CellID"
            self.create_raster_simgrid()
        elif self.geometry_type == "GEOHASH":
            self.assetident = "GeohashID"
            self.create_geohash_simgrid()
        elif self.geometry_type == "PARCEL":
            self.assetident = "ParcelID"
            self.create_parcel_simgrid()
        else:
            self.notify("Error, no geometry type specified")    # Should technically NEVER GET TO HERE
            return True

        self.notify("Finished SimGrid Creation")
        self.meta.add_attribute("AssetIdent", self.assetident)  # Write the final identifier to the metadata
        self.notify_progress(100)    # Must notify of 100% progress if the 'close' button is to be renabled.
        return True

    def create_square_simgrid(self):
        """Creates a simulation grid of square blocks of user-defined size. Determines the neighbourhood of this grid
        and creates the network representation of connections based on shared edges."""

        # DETERMINE BLOCK SIZE & NUMBER OF BLOCKS
        if self.blocksize_auto:  # Autosize blocks?
            block_limit = 2000
            ideal_blocksize = math.sqrt((self.mapwidth * self.mapheight) / float(block_limit))
            self.notify("Auto-determine Blocks - ideal number: "+str(ideal_blocksize))

            if ideal_blocksize <= 100:
                final_bs = 100
            elif ideal_blocksize <= 200:  # If less than 200m, size to 200m x 200m as minimum
                final_bs = 200
            elif ideal_blocksize <= 500:
                final_bs = 500
            elif ideal_blocksize <= 1000:
                final_bs = 1000
            elif ideal_blocksize <= 2000:
                final_bs = 2000
            else:
                final_bs = 5000  # Maximum Block Size will be 5000m x 5000m, we cannot simply afford to go higher
        else:
            final_bs = self.blocksize

        blocks_wide = int(math.ceil(self.mapwidth / float(final_bs)))
        blocks_tall = int(math.ceil(self.mapheight / float(final_bs)))
        numblocks = blocks_wide * blocks_tall
        blockarea = pow(final_bs, 2)

        # Update Metadata
        self.meta.add_attribute("Geometry", self.geometry_type)
        self.meta.add_attribute("BlockSize", final_bs)
        self.meta.add_attribute("NumBlocks", numblocks)
        self.meta.add_attribute("BlocksWide", blocks_wide)
        self.meta.add_attribute("BlocksTall", blocks_tall)
        self.meta.add_attribute("BlockArea", blockarea)

        self.notify("Map dimensions: W="+str(blocks_wide)+" H="+str(blocks_tall)+" [Block elements]")
        self.notify("Total number of Blocks: "+str(numblocks)+" @ "+str(final_bs)+"m")

        self.notify_progress(40)    # PROGRESS 40%

        # GENERATE THE BLOCKS MAP
        self.notify("Creating Block Geometry")
        self.assets.add_asset_type("Block", "Polygon")
        blockIDcount = 1
        blockslist = []
        for y in range(blocks_tall):
            for x in range(blocks_wide):
                # CREATE THE BLOCK GEOMETRY
                self.notify("Current Block ID: "+str(blockIDcount))
                current_block = self.generate_block_geometry(x, y, blockIDcount)
                if current_block is None:
                    blockIDcount += 1
                    continue

                self.assets.add_asset("BlockID"+str(blockIDcount), current_block)
                blockslist.append(current_block)
                blockIDcount += 1

        self.notify_progress(60)    # PROGRESS 60%

        # FIND NEIGHBOURHOOD - MOORE NEIGHBOURHOOD (Cardinal and Ordinal Directions)
        self.notify("Identifying Block Neighbourhood")
        directional_factors = [blocks_wide, blocks_wide + 1, 1, -blocks_wide + 1,
                               -blocks_wide, -blocks_wide - 1, -1, blocks_wide - 1]
        direction_names = ["NHD_N", "NHD_NE", "NHD_E", "NHD_SE", "NHD_S", "NHD_SW", "NHD_W", "NHD_NW"]

        for i in range(len(blockslist)):        # ID and Geometric Scanning for all 8 neighbours
            neighbourhood_ids = []
            curblock_id = blockslist[i].get_attribute("BlockID")
            if curblock_id % blocks_wide == 0:   # Right edge
                exceptions = ["NHD_NE", "NHD_E", "NHD_SE"]
                [blockslist[i].add_attribute(exc, 0) for exc in exceptions]  # e.g. add_attribute("NHD_E", 0)
            elif curblock_id % blocks_wide == 1:  # Left edge
                exceptions = ["NHD_NW", "NHD_W", "NHD_SW"]
                [blockslist[i].add_attribute(exc, 0) for exc in exceptions]
            else:
                exceptions = []

            for d in range(len(direction_names)):
                if direction_names[d] in exceptions:
                    continue
                nhd_id = curblock_id + directional_factors[d]
                if self.assets.get_asset_with_name("BlockID"+str(nhd_id)) is None:
                    blockslist[i].add_attribute(direction_names[d], 0)
                else:
                    blockslist[i].add_attribute(direction_names[d], nhd_id)
                    neighbourhood_ids.append(nhd_id)

            blockslist[i].add_attribute("Neighbours", neighbourhood_ids)
            blockslist[i].add_attribute("Neighb_num", len(neighbourhood_ids))

        self.notify_progress(80)    # PROGRESS 80%

        # GENERATE CENTROIDS AND NEIGHBOURHOOD NETWORK - NETWORK IS N,S,W,E directions
        self.notify("Generating Block Centroids and Network")
        self.assets.add_asset_type("Centroid", "Point")
        for i in range(len(blockslist)):
            self.generate_centroid(blockslist[i])

        self.notify_progress(90)    # PROGRESS 90%
        self.assets.add_asset_type("Network", "Line")
        self.generate_block_network(blockslist)
        return True

    def generate_block_geometry(self, x, y, idnum):
        """Creates the Rectangular Block Face, the polygon of the block as a UBVector() object that intersects with the
        simulation boundary.

        :param x: The starting x coordinate (on 0,0 origin)
        :param y: The starting y coordinate (on 0,0 origin)
        :param idnum: the current ID number to be assigned to the Block
        :return: UBVector object containing the BlockID, attribute and geometry
        """
        bs = self.meta.get_attribute("BlockSize")

        # Define points
        n1 = (x * bs, y * bs, 0)  # Bottom left (x, y, z)
        n2 = ((x + 1) * bs, y * bs, 0)  # Bottom right
        n3 = ((x + 1) * bs, (y + 1) * bs, 0)  # Top right
        n4 = (x * bs, (y + 1) * bs, 0)  # Top left

        # Create the Shapely Polygon and test against the boundary to determine active/inactive.
        blockpoly = Polygon((n1[:2], n2[:2], n3[:2], n4[:2]))
        if Polygon.intersects(self.boundarypoly, blockpoly):    # Define edges
            e1 = (n1, n2)  # Bottom left to bottom right
            e2 = (n2, n3)  # Bottom right to top right
            e3 = (n4, n3)  # Top right to top left
            e4 = (n1, n4)  # Top left to bottom left

            # Define the UrbanBEATS Vector Asset
            block_attr = ubdata.UBVector((n1, n2, n3, n4, n1), (e1, e2, e3, e4))
            block_attr.add_attribute("BlockID", int(idnum))  # ATTRIBUTE: Block Identification

            xcentre = x * bs + 0.5 * bs
            ycentre = y * bs + 0.5 * bs

            block_attr.add_attribute("CentreX", xcentre)  # ATTRIBUTE: geographic information
            block_attr.add_attribute("CentreY", ycentre)
            block_attr.add_attribute("OriginX", n1[0])
            block_attr.add_attribute("OriginY", n1[1])
            block_attr.add_attribute("Status", 1)  # Start with Status = 1 by default
            return block_attr
        else:   # Block not within boundary, do not return anything
            return None

    def generate_block_network(self, blockslist):
        """Generates the neighbourhood network for the block centroids and saves the links to the asset collection."""
        networklist = []
        networkIDcount = 1
        for i in range(len(blockslist)):
            curblock = blockslist[i]
            curblockID = curblock.get_attribute(self.assetident)
            for nhd in ["NHD_N", "NHD_E", "NHD_S", "NHD_W"]:        # Only the north-south-east-west neighbours
                nhd_blockID = curblock.get_attribute(nhd)
                if nhd_blockID == 0:
                    continue
                if str(nhd_blockID)+","+str(curblockID) not in networklist:
                    p1 = (curblock.get_attribute("CentreX"), curblock.get_attribute("CentreY"))
                    nhd_block = self.assets.get_asset_with_name(self.assetident+str(nhd_blockID))
                    p2 = (nhd_block.get_attribute("CentreX"), nhd_block.get_attribute("CentreY"))

                    # Asset creation
                    line = ubdata.UBVector((p1, p2))
                    line.add_attribute("NetworkID", networkIDcount)
                    line.add_attribute("Node1", curblockID)
                    line.add_attribute("Node2", nhd_blockID)
                    self.assets.add_asset("NetworkID"+str(networkIDcount), line)

                    networklist.append(str(curblockID)+","+str(nhd_blockID))
                    networkIDcount += 1
                else:
                    continue
        self.notify("Total number of links generated: "+str(len(networklist)))
        return True

    def create_hexagon_simgrid(self):
        """Creates a simulation grid of hexagonal blocks of user-defined size. Determines the neighbourhood of this grid
        and creates the network representation of connections based on shared edges."""
        # AUTO SIZE HEXAGONS?
        if self.hexsize_auto:
            block_limit = 2000
            ideal_blocksize = math.sqrt(((self.mapwidth * self.mapheight)/float(block_limit))*2.0/(3.0*self.hexfactor))
            self.notify("Auto-determine Hexes - ideal number: " + str(ideal_blocksize))

            if ideal_blocksize <= 200:
                final_bs = 200
            elif ideal_blocksize <= 300:  # If less than 200m, size to 200m x 200m as minimum
                final_bs = 300
            elif ideal_blocksize <= 500:
                final_bs = 500
            elif ideal_blocksize <= 1000:
                final_bs = 1000
            elif ideal_blocksize <= 2000:
                final_bs = 2000
            else:
                final_bs = 5000  # Maximum Block Size will be 5000m x 5000m, we cannot simply afford to go higher
        else:
            final_bs = self.hexsize

        # DETERMINE NUMBER OF HEXES
        if self.hex_orientation == "NS":
            blocks_wide = int(math.ceil(self.mapwidth / float(1.5 * self.hexsize)))
            blocks_tall = int(math.ceil(self.mapheight / float(self.hexsize * self.hexfactor)))
        else:
            blocks_wide = int(math.ceil(self.mapwidth / float(self.hexsize * self.hexfactor)))
            blocks_tall = int(math.ceil(self.mapheight / float(1.5 * self.hexsize))) + 1  # +1 based on centroid align

        numhexes = blocks_wide * blocks_tall
        hexarea = pow(final_bs, 2) * 0.5 * 3 * self.hexfactor

        # Update Metadata
        self.meta.add_attribute("Geometry", self.geometry_type)
        self.meta.add_attribute("HexOrient", self.hex_orientation)
        self.meta.add_attribute("HexSize", final_bs)
        self.meta.add_attribute("NumHexes", numhexes)
        self.meta.add_attribute("HexWide", blocks_wide)
        self.meta.add_attribute("HexTall", blocks_tall)
        self.meta.add_attribute("HexArea", hexarea)

        self.notify("Map dimensions: W=" + str(blocks_wide) + " H=" + str(blocks_tall) + " [Block elements]")
        self.notify("Total number of Hexes: " + str(numhexes) + " @ " + str(final_bs) + "m")

        self.notify_progress(40)  # PROGRESS 40%

        # GENERATE THE HEX MAP
        self.notify("Creating Hex Geometry")
        self.assets.add_asset_type("Hex", "Polygon")
        hexIDcount = 1
        hexlist = []
        for y in range(blocks_tall):
            for x in range(blocks_wide):
                # CREATE THE HEX GEOMETRY
                self.notify("Current Hex ID: " + str(hexIDcount))
                if self.hex_orientation == "EW":
                    current_hex = self.generate_hex_geometry_ew(x, y, hexIDcount)
                else:
                    current_hex = self.generate_hex_geometry_ns(x, y, hexIDcount)
                if current_hex is None:
                    hexIDcount += 1
                    continue

                self.assets.add_asset("HexID" + str(hexIDcount), current_hex)
                hexlist.append(current_hex)
                hexIDcount += 1

        self.notify_progress(60)  # PROGRESS 60%

        # FIND NEIGHBOURHOOD - HEX ISOTROPIC NEIGHBOURHOOD (six directions)
        self.notify("Identifying Hex Neighbourhood")
        directions = [+1, -1, blocks_wide, -blocks_wide, blocks_wide+1, -blocks_wide+1, blocks_wide-1, -blocks_wide-1]    # Need geometry checking

        for i in range(len(hexlist)):
            neighbourhood_ids = []      # Holds all nhd_ids
            curhex_id = hexlist[i].get_attribute("HexID")
            # Get neighbours that always apply
            for j in range(len(directions)):   # For IDs that might be neighbours, check geometry
                check_id = int(curhex_id + directions[j])
                if self.assets.get_asset_with_name("HexID" + str(check_id)) is None:
                    continue
                if hexlist[i].shares_geometry(self.assets.get_asset_with_name("HexID"+str(check_id)), "edges", "all"):
                    neighbourhood_ids.append(check_id)

            hexlist[i].add_attribute("Neighbours", neighbourhood_ids)
            hexlist[i].add_attribute("Neighb_num", len(neighbourhood_ids))

        # GENERATE HEX CENTROIDS AND NEIGHBOURHOOD NETWORK - Network is isotropic in 6 directions
        self.notify("Generating Hex Centroids and Network")
        self.assets.add_asset_type("Centroid", "Point")
        for i in range(len(hexlist)):
            self.generate_centroid(hexlist[i])

        self.notify_progress(90)    # PROGRESS 90%
        self.assets.add_asset_type("Network", "Line")
        self.generate_shared_edge_network(hexlist)
        return True

    def generate_hex_geometry_ew(self, x, y, hexidnum):
        """ Creates the hexagonal Block Face in east-west direction, the polygon of the Hex as a UBVector

        :param x: starting x-coordinate (0,0 origin)
        :param y: starting y-coordinate (0,0 origin)
        :param hexidnum: the current ID number to be assigned to the Hex Block
        :return: UBVector object containing BLockID, attributes and geometry
        """
        # Define Hex Points     First point is the anchor point - the centroid of the bottom
        #     / 6 \             left hex is anchored to the global origin
        #    1     5
        #    |  *  |
        #    2     4
        #     \ 3 /

        hs = self.meta.get_attribute("HexSize")

        h_factor = float('%.5f' % (self.hexfactor * hs))
        shift_factor = float('%.5f' % (0.5 * h_factor * (y % 2)))
        anchorX = x * h_factor - 0.5 * h_factor + shift_factor
        anchorY = y * 1.5 * hs + 0.5 * hs
        h1 = (anchorX, anchorY, 0)
        h2 = (h1[0], h1[1] - hs, 0)
        h3 = (h1[0] + 0.5 * h_factor, h1[1] - 1.5 * hs, 0)
        h4 = (h1[0] + h_factor, h1[1] - hs, 0)
        h5 = (h1[0] + h_factor, h1[1], 0)
        h6 = (h1[0] + 0.5 * h_factor, h1[1] + 0.5 * hs, 0)

        # Create the Shapely Polygon and test against the boundary to determine active/inactive
        blockpoly = Polygon((h1[:2], h2[:2], h3[:2], h4[:2], h5[:2], h6[:2]))
        if Polygon.intersects(self.boundarypoly, blockpoly):
            # Define edges (as integers down to the nearest [m])
            e1 = ((int(h2[0]), int(h2[1]), 0), (int(h1[0]), int(h1[1]), 0))  # Left edge (2, 1)
            e2 = ((int(h2[0]), int(h2[1]), 0), (int(h3[0]), int(h3[1]), 0))  # Left bottom (2, 3)
            e3 = ((int(h3[0]), int(h3[1]), 0), (int(h4[0]), int(h4[1]), 0))  # Right bottom (3, 4)
            e4 = ((int(h4[0]), int(h4[1]), 0), (int(h5[0]), int(h5[1]), 0))  # Right edge (4, 5)
            e5 = ((int(h6[0]), int(h6[1]), 0), (int(h5[0]), int(h5[1]), 0))  # Right top (6, 5)
            e6 = ((int(h1[0]), int(h1[1]), 0), (int(h6[0]), int(h6[1]), 0))  # Left top (1, 6)

            # Define the UrbanBEATS Vector Asset
            hex_attr = ubdata.UBVector((h1, h2, h3, h4, h5, h6, h1), (e1, e2, e3, e4, e5, e6))
            hex_attr.add_attribute("HexID", int(hexidnum))  # ATTRIBUTE: Block identification

            xcentre = anchorX + 0.5 * h_factor
            ycentre = anchorY - 0.5 * hs

            xorigin = x * h_factor - 0.5 * h_factor + shift_factor  # Lower left extent X
            yorigin = y * 1.5 * hs - hs  # lower left extent Y

            hex_attr.add_attribute("CentreX", xcentre)  # ATTRIBUTE: geographic information
            hex_attr.add_attribute("CentreY", ycentre)
            hex_attr.add_attribute("OriginX", xorigin)
            hex_attr.add_attribute("OriginY", yorigin)
            hex_attr.add_attribute("Status", 1)  # Start with Status = 1 by default

            return hex_attr
        else:
            return None     # Hex not within boundary, do not return anything

    def generate_hex_geometry_ns(self, x, y, hexidnum):
        """ Creates the Hexagonal Block Face in north-south direction, the polygon of the Block as a UBVector

        :param x: starting x-coordinate (0,0 origin)
        :param y: starting y-coordinate (0,0 origin)
        :param hexidnum: the current ID number to be assigned to the Hex Block
        :return: UBVector object containing BLockID, attributes and geometry
        """
        # Define Hex Points     First point is the anchor point - slightly lower than
        #        ___            global origin (0,0) shift of y by global map shift
        #      /5   4\
        #     6   *   3
        #      \1___2/

        hs = self.meta.get_attribute("HexSize")
        hex_tall = self.meta.get_attribute("HexTall")

        v_factor = float('%.5f' % (self.hexfactor * hs))  # distance between parallel edges in a hex (=sqrt(3) x d)
        shift_factor = float(
            '%.5f' % (0.5 * v_factor * (x % 2)))  # in odd column numbers, shift has to be accounted for
        anchorX = x * 1.5 * hs
        anchorY = y * v_factor + (self.mapheight - hex_tall * v_factor) + shift_factor
        h1 = (anchorX, anchorY, 0)
        h2 = (h1[0] + hs, h1[1], 0)
        h3 = (h1[0] + 1.5 * hs, h1[1] + 0.5 * v_factor, 0)
        h4 = (h1[0] + hs, h1[1] + v_factor, 0)
        h5 = (h1[0], h1[1] + v_factor, 0)
        h6 = (h1[0] - 0.5 * hs, h1[1] + 0.5 * v_factor, 0)

        # Create the Shapely Polygon and test against the boundary to determine active/inactive
        hexpoly = Polygon((h1[:2], h2[:2], h3[:2], h4[:2], h5[:2], h6[:2]))
        if Polygon.intersects(self.boundarypoly, hexpoly):
            # Define edges
            e1 = ((int(h1[0]), int(h1[1]), 0), (int(h2[0]), int(h2[1]), 0))  # Bottom edge (1, 2)
            e2 = ((int(h2[0]), int(h2[1]), 0), (int(h3[0]), int(h3[1]), 0))  # Bottom right (2, 3)
            e3 = ((int(h4[0]), int(h4[1]), 0), (int(h3[0]), int(h3[1]), 0))  # Top right (4, 3)
            e4 = ((int(h5[0]), int(h5[1]), 0), (int(h4[0]), int(h4[1]), 0))  # Top edge (5, 4)
            e5 = ((int(h6[0]), int(h6[1]), 0), (int(h5[0]), int(h5[1]), 0))  # Top left (6, 5)
            e6 = ((int(h6[0]), int(h6[1]), 0), (int(h1[0]), int(h1[1]), 0))  # Bottom left (6, 1)

            # Define the UrbanBEATS Vector Asset
            hex_attr = ubdata.UBVector((h1, h2, h3, h4, h5, h6, h1), (e1, e2, e3, e4, e5, e6))
            hex_attr.add_attribute("HexID", int(hexidnum))  # ATTRIBUTE: Block identification

            xcentre = anchorX + 0.5 * hs
            ycentre = anchorY + 0.5 * v_factor

            xorigin = anchorX - 0.5 * hs
            yorigin = anchorY

            hex_attr.add_attribute("CentreX", xcentre)  # ATTRIBUTE: geographic information
            hex_attr.add_attribute("CentreY", ycentre)
            hex_attr.add_attribute("OriginX", xorigin)
            hex_attr.add_attribute("OriginY", yorigin)
            hex_attr.add_attribute("Status", 1)  # Start with Status = 1 by default

            return hex_attr
        else:
            return None     # Hex not within boundary, do not return anything

    def generate_centroid(self, asset_attr):
        asset_id = asset_attr.get_attribute(self.assetident)
        cp = ubdata.UBVector([(asset_attr.get_attribute("CentreX"), asset_attr.get_attribute("CentreY"))])
        cp.add_attribute(self.assetident, asset_attr.get_attribute(self.assetident))
        cp.add_attribute("CoordX", asset_attr.get_attribute("CentreX"))
        cp.add_attribute("CoordY", asset_attr.get_attribute("CentreY"))
        cp.add_attribute("Status", asset_attr.get_attribute("Status"))
        self.assets.add_asset("CentroidID" + str(asset_id), cp)
        return True

    def generate_shared_edge_network(self, assets):
        """Generates a network based on the shared edges. This applies to hexes, patches and parcels as their
        neighbourhood information is contained in a list of IDs that are confirmed to have shared edges."""
        networklist = []
        networkIDcount = 1
        for i in range(len(assets)):
            curasset = assets[i]
            curassetID = curasset.get_attribute(self.assetident)
            for nhd in curasset.get_attribute("Neighbours"):
                if str(nhd)+","+str(curassetID) not in networklist:
                    p1 = (curasset.get_attribute("CentreX"), curasset.get_attribute("CentreY"))
                    nhd_asset = self.assets.get_asset_with_name(self.assetident+str(nhd))
                    p2 = (nhd_asset.get_attribute("CentreX"), nhd_asset.get_attribute("CentreY"))

                    # Asset creation
                    line = ubdata.UBVector((p1, p2))
                    line.add_attribute("NetworkID", networkIDcount)
                    line.add_attribute("Node1", curassetID)
                    line.add_attribute("Node2", nhd)
                    self.assets.add_asset("NetworkID"+str(networkIDcount), line)
                    networklist.append(str(curassetID)+","+str(nhd))
                    networkIDcount += 1
                else:
                    continue
        self.notify("Total number of links generated: "+str(len(networklist)))
        return True

    def find_neighbours_by_geometry(self, curasset, assetlist):
        """Performs the neighbourhood scan based on shared edges or points."""
        nhd = []
        for i in range(len(assetlist)):
            cur_id = curasset.get_attribute(self.assetident)
            comp_id = assetlist[i].get_attribute(self.assetident)
            if cur_id == comp_id or assetlist[i].get_attribute("Status") == 0:
                continue    # Identical IDs or no status? Skip
            if Polygon.intersection(Polygon(curasset.get_points()), Polygon(assetlist[i].get_points())).length > 0.0:
                # If the length of the intersection is not 0 (i.e. shared edges)
                nhd.append(comp_id)
        return nhd

    def create_patch_simgrid(self):
        """Creates a simulation grid of patches based on an input land use map and a pre-defined discretization grid.
        Determines the neighbourhood of this grid and creates the network representation of connections based on shared
        edges, i.e. dirichlet tesselation."""
        # Load all parcels into the model - shapefile
        patchmap = self.datalibrary.get_data_with_id(self.patchzonemap)
        fullpath = patchmap.get_data_file_path() + patchmap.get_metadata("filename")
        raw_patches = ubspatial.import_polygonal_map(fullpath, "native",
                                                     "Patches", (self.meta.get_attribute("xllcorner"),
                                                                 self.meta.get_attribute("yllcorner")))
        self.notify("Raw number of patches in data file: "+str(len(raw_patches)))
        self.notify_progress(40)    # Progress 40%

        # Load / Create the discretization grid, if none, simply assign parcels IDs and move on
        self.assets.add_asset_type("Patch", "Polygon")
        self.assets.add_asset_type("Centroid", "Point")

        if self.disgrid_type == "GRID":
            patchlist = self.delineate_patches_by_grid(raw_patches)
        elif self.disgrid_type == "BOUND":
            patchlist = self.delineate_patches_by_bounds(raw_patches)
        else:   # NONE
            patchlist = self.delineate_patches_as_raw(raw_patches)

        self.notify("Identified in total: "+str(len(patchlist))+" patches")
        self.notify_progress(60)    # Progress 60%

        # Identify Neighbourhoods
        for i in range(len(patchlist)):
            self.notify("Scanning Neighbourhood for PatchID"+str(patchlist[i].get_attribute("PatchID")))
            nhd = self.find_neighbours_by_geometry(patchlist[i], patchlist)
            patchlist[i].add_attribute("Neighbours", nhd)
            patchlist[i].add_attribute("Neighb_num", len(nhd))

        # Construct Dirichlet
        self.notify_progress(80)
        self.notify("Constructing Dirichlet Network")
        self.assets.add_asset_type("Network", "Line")
        self.generate_shared_edge_network(patchlist)
        return True

    def delineate_patches_by_grid(self, raw_patches):
        pass

    def delineate_patches_by_bounds(self, raw_patches):
        boundmap = self.datalibrary.get_data_with_id(self.disgrid_map)
        fullpath = boundmap.get_data_file_path() + boundmap.get_metadata("filename")
        bounddata = ubspatial.import_polygonal_map(fullpath, "native", "Bounds", (self.meta.get_attribute("xllcorner"),
                                                                                  self.meta.get_attribute("yllcorner")))

        # Intersect the bounds with the active simulation boundary map - filters out only the bound polygons within the
        # project simulation boundary
        bound_isects = []
        for i in range(len(bounddata)):
            poly = Polygon(bounddata[i].get_points())
            isect = Polygon.intersection(poly, self.boundarypoly)
            if isect.area > 0:
                if isect.geom_type == "Polygon":
                    bound_isects.append(isect)
                elif isect.geom_type == "MultiPolygon":
                    [bound_isects.append(p) for p in isect.geoms]

        self.notify("Total number of intersections: "+str(len(bound_isects)))
        self.notify_progress(50)        # Progress 50%

        # Now intersect each item in the patch collection with each bound_intersect
        patchlist = []
        patchIDcount = 1
        for i in range(len(bound_isects)):
            self.notify("Bounds #"+str(i+1)+" of "+str(len(bound_isects)))
            for j in range(len(raw_patches)):
                patches_to_scan = []
                intersection = Polygon.intersection(bound_isects[i], Polygon(raw_patches[j].get_points()))
                if intersection.area == 0:
                    continue
                else:   # Found a patch, create UBVector
                    if intersection.geom_type == "MultiPolygon":
                        [patches_to_scan.append(item) for item in intersection.geoms]
                    elif intersection.geom_type == "Polygon":
                        patches_to_scan.append(intersection)
                    for curpatch in patches_to_scan:
                        self.notify("   Current PatchID "+str(patchIDcount))
                        coords = curpatch.exterior.coords.xy
                        points = [(coords[0][p], coords[1][p]) for p in range(len(coords[0]))]
                        edges = [(points[p], points[p+1]) for p in range(len(points)-1)]
                        rp = curpatch.representative_point()
                        patch_attr = ubdata.UBVector(points, edges)
                        patch_attr.add_attribute("PatchID", patchIDcount)
                        patch_attr.add_attribute("CentreX", rp.x)
                        patch_attr.add_attribute("CentreY", rp.y)
                        patch_attr.add_attribute("Area", curpatch.area)
                        patch_attr.add_attribute("Status", 1)
                        self.assets.add_asset("PatchID"+str(patchIDcount), patch_attr)

                        cen_attr = ubdata.UBVector([(rp.x, rp.y)])
                        cen_attr.add_attribute("CentroidID", patchIDcount)
                        cen_attr.add_attribute("CentreX", rp.x)
                        cen_attr.add_attribute("CentreY", rp.y)
                        cen_attr.add_attribute("Area", curpatch.area)
                        cen_attr.add_attribute("Status", 1)
                        self.assets.add_asset("CentroidID"+str(patchIDcount), cen_attr)

                        patchIDcount += 1
                        patchlist.append(patch_attr)
        return patchlist

    def delineate_patches_as_raw(self, raw_patches):
        pass

    def create_raster_simgrid(self):
        """Creates a simulation grid of raster cells, represented by points with x,y coordinates, allowing easy export
        to GeoTiff or ASCII later on. Determines the neighbourhood of this grid and creates the network representation
        of connections based on shared edges (north, south, east west)."""
        blocks_wide = int(math.ceil(self.mapwidth / float(self.rastersize)))
        blocks_tall = int(math.ceil(self.mapheight / float(self.rastersize)))
        numcells = blocks_wide * blocks_tall
        cellarea = pow(self.rastersize, 2)

        # Update Metadata
        self.meta.add_attribute("Geometry", self.geometry_type)
        self.meta.add_attribute("Cellsize", self.rastersize)
        self.meta.add_attribute("NumCells", numcells)
        self.meta.add_attribute("Columns", blocks_wide)
        self.meta.add_attribute("Rows", blocks_tall)
        self.meta.add_attribute("Cellarea", cellarea)
        self.meta.add_attribute("HasFishnet", self.generate_fishnet)

        self.notify("Map dimensions: W=" + str(blocks_wide) + " H=" + str(blocks_tall) + " [Raster elements]")
        self.notify("Total number of Blocks: " + str(numcells) + " @ " + str(self.rastersize) + "m")

        self.notify_progress(40)  # PROGRESS 40%

        # GENERATE RASTER CELLS
        self.notify("Creating raster points")
        self.assets.add_asset_type("Cell", "Point")
        if self.generate_fishnet:
            self.assets.add_asset_type("Fish", "Polygon")
        cellIDcount = 1
        cellslist = []

        for y in range(blocks_tall):
            self.notify("Row #"+str(y))
            for x in range(blocks_wide):
                cell, fish = self.generate_raster_cell(x, y, cellIDcount)
                self.assets.add_asset("CellID"+str(cellIDcount), cell)
                if fish is not None:
                    self.assets.add_asset("FishID"+str(cellIDcount), fish)
                cellIDcount += 1

        self.notify_progress(95)
        # RASTER NEIGHBOURHOOD IS DONE ON THE FLY
        return True

    def generate_raster_cell(self, x, y, idnum):
        """Generates the centroid of the raster cell, if fishnet is active, also generates the fishnet."""
        res = self.rastersize
        cellX = x * res + 0.5 * res
        cellY = y * res + 0.5 * res

        attr = ubdata.UBVector([(cellX, cellY)])
        attr.add_attribute("CellID", int(idnum))
        attr.add_attribute("Row", y)
        attr.add_attribute("Col", x)
        attr.add_attribute("X", cellX)
        attr.add_attribute("Y", cellY)
        attr.add_attribute("Status", 1)
        if Point(cellX, cellY).within(self.boundarypoly):
            attr.add_attribute("NoData", 0)
        else:
            attr.add_attribute("NoData", self.nodatavalue)

        if self.generate_fishnet:
            n1 = (x * res, y * res)          # same as for square blocks
            n2 = ((x+1) * res, y * res)
            n3 = ((x+1) * res, (y+1) * res)
            n4 = (x * res, (y+1) * res)

            fish_attr = ubdata.UBVector((n1, n2, n3, n4, n1),
                                        ((n1, n2), (n2, n3), (n3, n4), (n4, n1)))
            fish_attr.add_attribute("FishID", int(idnum))
            attr.add_attribute("Row", y)
            attr.add_attribute("Col", x)
            fish_attr.add_attribute("X", cellX)
            fish_attr.add_attribute("Y", cellY)
            fish_attr.add_attribute("Status", 1)
            fish_attr.add_attribute("NoData", attr.get_attribute("NoData"))
        else:
            fish_attr = None
        return attr, fish_attr

    def create_geohash_simgrid(self):
        """Creates a simulation grid of geohash cells of user-defined level. Determines the neighbourhood of this grid
        and creates the network representation of connections based on shared edges. Geohashes are assigned their
        unique ID rather than a numerical ID."""

        # Geohashes work with EPSG 4326, so need to project on the fly...
        to_gcs = ubspatial.create_coordtrans(self.activesim.get_project_epsg(), 4326)

        # Get the boundary as WGS1984 EPSG4326 - in Shapely Polygon format
        boundaryring = ogr.Geometry(ogr.wkbLinearRing)
        for coords in self.boundarydata["coordinates"]:     # 'coordinates are in X and Y order' (projected)
            boundaryring.AddPoint(coords[0], coords[1])     # the ring is also created x and y
        boundarypoly = ogr.Geometry(ogr.wkbPolygon)
        boundarypoly.AddGeometry(boundaryring)
        boundarypoly.Transform(to_gcs)                      # becomes Lat, Long (y, x)
        boundaryring = boundarypoly.GetGeometryRef(0)
        points = boundaryring.GetPointCount()
        coordinates = []
        for i in range(points):
            coordinates.append((boundaryring.GetX(i), boundaryring.GetY(i)))        # x represents 'lat'
        geohash_boundary = Polygon(coordinates)
        rep_point = geohash_boundary.representative_point()
        print(rep_point)
        start_geohash = gh.encode(rep_point.x, rep_point.y, int(self.geohash_lvl))

        self.notify_progress(40)    # PROGRESS 40%

        # Set up stacks
        checked_geohashes = set()
        checked_geohashes.add(start_geohash)
        geohash_stack = set()
        geohash_stack.add(start_geohash)
        geohashlist = []
        geohashlist.append(start_geohash)

        # Update Metadata
        self.meta.add_attribute("Geometry", self.geometry_type)
        self.meta.add_attribute("GeohashLvl", self.geohash_lvl)
        self.meta.add_attribute("GeohashXres", GEOHASH_RES[self.geohash_lvl][0])
        self.meta.add_attribute("GeohashYres", GEOHASH_RES[self.geohash_lvl][1])
        self.meta.add_attribute("GeohashArea", GEOHASH_RES[self.geohash_lvl][0] * GEOHASH_RES[self.geohash_lvl][1])
        self.meta.add_attribute("CentroidGH", start_geohash)

        # Add the centroid GH as a UBVector to the Assets
        self.notify_progress(50)  # PROGRESS 50%
        self.assets.add_asset_type("Geohash", "Polygon")        # We do polygons and centroid simultaneously
        self.assets.add_asset_type("Centroid", "Point")

        point = Point(gh.decode(start_geohash))
        ubpoint, ubpoly = self.convert_gh_to_ubvector(point, start_geohash)
        self.assets.add_asset("CentroidID"+start_geohash, ubpoint)
        self.assets.add_asset("GeohashID"+start_geohash, ubpoly)

        # Now scan for all geohashes within the boundary, creating UBVectors as we go
        while len(geohash_stack) > 0:
            current_gh = geohash_stack.pop()
            self.notify("Current Geohash: "+str(current_gh))
            nhd = gh.neighbours(current_gh)
            for n in nhd:
                point = Point(gh.decode(n))
                poly = self.get_geohash_polygon(n)
                if n not in checked_geohashes and geohash_boundary.intersects(poly):
                    geohashlist.append(n)
                    geohash_stack.add(n)
                    checked_geohashes.add(n)

                    ubpoint, ubpoly = self.convert_gh_to_ubvector(point, n)
                    self.assets.add_asset("CentroidID" + n, ubpoint)
                    self.assets.add_asset("GeohashID" + n, ubpoly)

        self.meta.add_attribute("NumGeohashes", len(geohashlist))
        self.notify("Total Geohashes found: "+str(len(geohashlist)))
        self.notify_progress(70)    # PROGRESS 70%

        # GRAB GEOHASH NEIGHBOURS
        nhd_directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'se', 'nw']
        for g in geohashlist:
            hasdir = []
            neighbours = []
            gh_attr = self.assets.get_asset_with_name("GeohashID"+g)
            nhd = gh.neighbours(g)._asdict()
            for n in nhd.keys():
                if self.assets.get_asset_with_name("GeohashID"+nhd[n]) is None:
                    gh_attr.add_attribute("NHD_"+n.upper(), 0)
                    continue
                else:
                    gh_attr.add_attribute("NHD_"+n.upper(), nhd[n])
                    hasdir.append(n)
                    neighbours.append(nhd[n])
            gh_attr.add_attribute("Neighbours", neighbours)
            gh_attr.add_attribute("Neighb_num", len(neighbours))

        # DRAW GEOHASH NETWORK
        self.notify_progress(90)
        ubgeohashlist = self.assets.get_assets_with_identifier("GeohashID")
        self.assets.add_asset_type("Network", "Line")
        self.generate_block_network(ubgeohashlist)
        return True

    def convert_gh_to_ubvector(self, geom, geohash_id):
        """Converts a decoded geohash coordinate array to the UBVector() object by first reprojecting it from
        EPSG 4326 to the project's EPSG and then creating the UBVector geometry."""
        to_projectepsg = ubspatial.create_coordtrans(4326, self.activesim.get_project_epsg())

        # Set up the point UBVector() of type Centroid
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.AddPoint(geom.x, geom.y)
        pt.Transform(to_projectepsg)
        ubpoint = ubdata.UBVector([(pt.GetX() - self.extents[0], pt.GetY() - self.extents[2])])
        ubpoint.add_attribute("GeohashID", geohash_id)
        ubpoint.add_attribute("Status", 1)
        ubpoint.add_attribute("CentreX", pt.GetX() - self.extents[0])
        ubpoint.add_attribute("CentreY", pt.GetY() - self.extents[2])

        # Set up the UBVector() of type Geohash
        ring = ogr.Geometry(ogr.wkbLinearRing)
        poly = ogr.Geometry(ogr.wkbPolygon)
        coords = self.get_geohash_polygon(geohash_id).exterior.coords.xy

        for i in range(len(coords[0])):
            ring.AddPoint(coords[0][i], coords[1][i])
        poly.AddGeometry(ring)
        poly.Transform(to_projectepsg)
        ring = poly.GetGeometryRef(0)
        coordinates = []
        for p in range(ring.GetPointCount()):
            coordinates.append((ring.GetPoint(p)[0] - self.extents[0], ring.GetPoint(p)[1] - self.extents[2]))
        edges = [(coordinates[i], coordinates[i+1]) for i in range(4)]
        ubpoly = ubdata.UBVector(coordinates, edges)
        ubpoly.add_attribute("GeohashID", geohash_id)
        ubpoly.add_attribute("Status", 1)
        ubpoly.add_attribute("CentreX", pt.GetX() - self.extents[0])
        ubpoly.add_attribute("CentreY", pt.GetY() - self.extents[2])
        return ubpoint, ubpoly

    def get_geohash_polygon(self, geohash_id):
        """Returns the geohash polygon for the specified ID."""
        bounds = gh.bounds(geohash_id)
        p1 = (bounds.sw.lat, bounds.sw.lon)
        p2 = (bounds.ne.lat, bounds.sw.lon)
        p3 = (bounds.ne.lat, bounds.ne.lon)
        p4 = (bounds.sw.lat, bounds.ne.lon)
        return Polygon([p1, p2, p3, p4, p1])

    def create_parcel_simgrid(self):
        """Creates a simulation grid of parcels by loading in a pre-defined parcel map. Determines the neighbourhood of
        this delineation and creates the network representation of connections based on shared edges i.e., dirichlet
        tesselation."""
        # Open the parcels data set and grab features controlled to (0,0 origin).
        parcelmap = self.datalibrary.get_data_with_id(self.parcel_map)
        fullpath = parcelmap.get_data_file_path() + parcelmap.get_metadata("filename")
        parcels = ubspatial.import_polygonal_map(fullpath, "native", "Parcels", (self.meta.get_attribute("xllcorner"),
                                                                                 self.meta.get_attribute("yllcorner")))

        self.notify_progress(40)

        # For each parcel in the map... check if within the boundary polygon, if yes, assign ID and data, save
        parcellist = []
        parcelIDcount = 1
        self.assets.add_asset_type("Parcel", "Polygon")
        self.assets.add_asset_type("Centroid", "Point")

        for i in range(len(parcels)):
            points = parcels[i].get_points()
            # print(points)
            parcelpoly = Polygon(points)
            if Polygon.intersects(self.boundarypoly, parcelpoly):
                self.notify("Current ParcelID"+str(parcelIDcount))
                # Make a Clean UBVector Polygon ParcelID
                edges = [(points[i], points[i+1]) for i in range(len(points)-1)]
                rp = parcelpoly.representative_point()

                parcel_attr = ubdata.UBVector(parcels[i].get_points(), edges)
                parcel_attr.add_attribute("ParcelID", parcelIDcount)
                parcel_attr.add_attribute("CentreX", rp.x)
                parcel_attr.add_attribute("CentreY", rp.y)
                parcel_attr.add_attribute("Area", parcelpoly.area)
                parcel_attr.add_attribute("Status", 1)
                self.assets.add_asset("ParcelID"+str(parcelIDcount), parcel_attr)

                # Make the UBVector Point CentroidID
                cen_attr = ubdata.UBVector([(rp.x, rp.y)])
                cen_attr.add_attribute("ParcelID", parcelIDcount)
                cen_attr.add_attribute("CentreX", rp.x)
                cen_attr.add_attribute("CentreY", rp.y)
                cen_attr.add_attribute("Area", parcelpoly.area)
                cen_attr.add_attribute("Status", 1)
                self.assets.add_asset("CentroidID" + str(parcelIDcount), cen_attr)

                parcelIDcount += 1
                parcellist.append(parcel_attr)
            else:
                print("No intersect, continuing")

        # DETERMINE NEIGHBOURS OF PARCELS BY SHARED EDGES
        self.notify_progress(60)
        self.notify("Determining neighbourhoods")
        for i in range(len(parcellist)):
            self.notify("Scanning Neighbourhood for ParcelID"+str(parcellist[i].get_attribute("ParcelID")))
            nhd = self.find_neighbours_by_geometry(parcellist[i], parcellist)
            parcellist[i].add_attribute("Neighbours", nhd)
            parcellist[i].add_attribute("Neighb_num", len(nhd))

        # DRAW THE DIRICHLET NETWORK
        self.notify_progress(80)
        self.notify("Constructing Dirichlet Network")
        self.assets.add_asset_type("Network", "Line")
        self.generate_shared_edge_network(parcellist)
        return True

# GEOHASH RESOLUTION: Different x and y resolutions based on levels 5 to 8 - coarse than 5 or finer than 8 not possible
# Source: elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html
GEOHASH_RES = {5: (4900.0, 4900.0), 6: (1200, 609.4), 7: (152.9, 152.4), 8: (38.2, 19)}