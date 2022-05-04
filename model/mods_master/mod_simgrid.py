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
        self.create_parameter("disgrid_use", BOOL, "Use a discretization grid for the patch delineatioN?")
        self.create_parameter("disgrid_length", DOUBLE, "Edge length of the discretization grid")
        self.create_parameter("disgrid_auto", BOOL, "Auto-determine the size of the discretization grid?")
        self.patchzonemap = "(select zoning map for patch delineation)"
        self.disgrid_use = 0
        self.disgrid_length = 500   # [m]
        self.disgrid_auto = 0

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

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.boundarydata = self.activesim.get_project_boundary_by_name(self.boundaryname)

        # Get the asset collection, if it doesn't yet exist, create it.
        self.assets = self.activesim.get_asset_collection_by_name(self.gridname)
        if self.assets is None:
            self.assets = ubdata.UBCollection(self.gridname, "Standalone")
            self.activesim.add_asset_collection_to_project(self.assets)

        # Metadata check - Any module that creates a new asset collection should do this check
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:  # If there is currently no 'meta' object in the asset collection, make one
            self.meta = ubdata.UBComponent()  # Global Map Attributes if they do not yet exist
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
            self.create_square_simgrid()
        elif self.geometry_type == "HEXAGONS":
            self.create_hexagon_simgrid()
        elif self.geometry_type == "VECTORPATCH":
            self.create_patch_simgrid()
        elif self.geometry_type == "RASTER":
            self.create_raster_simgrid()
        elif self.geometry_type == "GEOHASH":
            self.create_geohash_simgrid()
        elif self.geometry_type == "PARCEL":
            self.create_parcel_simgrid()
        else:
            self.notify("Error, no geometry type specified")    # Should technically NEVER GET TO HERE
            return True

        self.notify("Finished SimGrid Creation")
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

        self.notify_progress(80)    # PROGRESS 80%

        # GENERATE CENTROIDS AND NEIGHBOURHOOD NETWORK - NETWORK IS N,S,W,E directions
        self.notify("Generating Block Centroids and Network")
        # current_block_cp = self.generate_block_centroid(current_block)
        # self.assets.add_asset("CentroidID" + str(blockIDcount), current_block_cp)

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

    def generate_block_centroids(self, block_attr):
        """Generates the centroid Point() for the block Vector passed to it, returns the UBVector() object."""
        return True

    def generate_block_network(self, blockslist):
        """Generates the neighbourhood network for the block centroids and saves the links to the asset collection."""
        pass
        return True

    def create_hexagon_simgrid(self):
        pass
        return True

    def create_patch_simgrid(self):
        pass
        return True

    def create_raster_simgrid(self):
        pass
        return True

    def create_geohash_simgrid(self):
        pass
        return True

    def create_parcel_simgrid(self):
        pass
        return True
