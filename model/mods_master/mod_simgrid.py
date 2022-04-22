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

    def __init__(self, activesim, asset_collection, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.asset_collection = asset_collection   # If used as one-off on-the-fly modelling, then scenario is None
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

        # Geometry Type: Geohash Grid
        self.create_parameter("geohash_lvl", DOUBLE, "Level of resolution for the geohash")
        self.geohash_lvl = 7

        # NON-VISIBLE PARAMETERS (ADVANCED SETTINGS)
        # None

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.notify("Running SimGrid Creation for "+self.boundaryname)
        self.notify_progress(0)

        # --- SECTION 1 - Preparation for creating the simulation grid based on the boundary map
        boundarydict = self.activesim.get_project_boundary_by_name(self.boundaryname)
        xmin, xmax, ymin, ymax = boundarydict["xmin"], boundarydict["xmax"], boundarydict["ymin"], boundarydict["ymax"]
        mapwidth = xmax - xmin
        mapheight = ymax - ymin

        self.notify("Map Width [km] = "+str(mapwidth/1000.0))
        self.notify("Map Height [km] = "+str(mapheight/1000.0))
        self.notify("Extent Area WxH [km2] = "+str(mapwidth * mapheight / 1000000.0))
        self.notify("--- === ---")

        self.map_attr = ubdata.UBComponent()        # Global Map Attributes if they do not yet exist
        self.map_attr.add_attribute("xllcorner", xmin)
        self.map_attr.add_attribute("yllcorner", ymin)
        self.map_attr.add_attribute("mod_simgrid", 1)
        self.scenario.add_asset("MapAttributes", self.map_attr)

        # Get boundary shifted to (0,0) origin
        boundarygeom_z0 = []
        for coords in boundarydict["coordinates"]:
            boundarygeom_z0.append((coords[0] - xmin, coords[1] - ymin))
        boundarypoly = Polygon(boundarygeom_z0)

        # --- SECTION 2 - Create the grid
        self.notify("Creating Simulation Grid")
        self.notify_progress(20)

        if self.geometry_type == "SQUARES":
            self.create_square_blocks(boundarypoly)
        elif self.geometry_type == "HEXAGONS":
            self.create_hexagonal_blocks()
        elif self.geometry_type == "VECTORPATCH":
            self.create_vectorpatches()
        elif self.geometry_type == "RASTER":
            self.create_rastermap()
        else:
            self.notify("Error, no geometry type specified")
            return True

        self.notify("Finished SimGrid Creation")
        self.notify_progress(100)
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    # === SQUARE GRID ===
    def create_square_blocks(self, mapwidth, mapheight, boundarypoly):
        """Generates the assets representing a Square Grid of Blocks based on the input boundary polygon
        and parameters."""
        # PREPARATION
        numblocks, blocks_wide, blocks_tall, final_bs = \
            determine_number_of_squares(mapwidth, mapheight, self.blocksize, self.blocksize_auto)
        blockarea = pow(final_bs, 2)
        self.map_attr.add_attribute("Geometry", self.geometry_type)
        self.map_attr.add_attribute("NumBlocks", numblocks)
        self.map_attr.add_attribute("BlocksWide", blocks_wide)
        self.map_attr.add_attribute("BlocksTall", blocks_tall)
        self.map_attr.add_attribute("BlockArea", blockarea)
        self.map_attr.add_attribute("Neigh_Type", "Moore")    # 8-neighbour Moore Neighbourhood

        self.notify("Map dimensions: W="+str(blocks_wide)+" H="+str(blocks_tall)+" [block elements]")
        self.notify("Total number of Blocks: "+str(numblocks)+" @ "+str(final_bs)+"m")
        self.notify_progress(30)

        # GENERATE THE BLOCKS MAP
        blockIDcount = 1
        blockslist = []
        for y in range(blocks_tall):
            for x in range(blocks_wide):
                # STEP 1 - Create the Block Geometry
                current_block = create_block_geometry(x, y, final_bs, boundarypoly)
                self.scenario.add_asset("BlockID"+str(blockIDcount), current_block)
                blockslist.append(current_block)
                blockIDcount += 1

        self.notify_progress(50)

        # FIND NEIGHBOURHOOD - MOORE NEIGHBOURHOOD (Cardinal and Ordinal Directions)
        directional_factors = [blocks_wide, blocks_wide + 1, 1, -blocks_wide + 1,
                               -blocks_wide, -blocks_wide - 1, -1, blocks_wide - 1]
        direction_names = ["NHD_N", "NHD_NE", "NHD_E", "NHD_SE", "NHD_S", "NHD_SW", "NHD_W", "NHD_NW"]

        for i in range(len(blockslist)):        # ID and Geometric Scanning for all 8 neighbours
            curblock_id = blockslist[i].get_attribute("BlockID")
            if curblock_id % blocks_wide == 0:   # Right edge
                exceptions = ["NHD_NE", "NHD_E", "NHD_SE"]
                [blockslist[i].add_attribute(exceptions[j], 0) for j in exceptions]  # e.g. add_attribute("NHD_E", 0)
            elif curblock_id % blocks_wide == 1:  # Left edge
                exceptions = ["NHD_NW", "NHD_W", "NHD_SW"]
                [blockslist[i].add_attribute(exceptions[j], 0) for j in exceptions]
            else:
                exceptions = []

            for d in range(len(direction_names)):
                if direction_names[d] in exceptions:
                    continue
                nhdID = curblock_id + directional_factors[d]
                if self.scenario.get_asset_with_name("BlockID"+str(nhdID)) is None:
                    blockslist[i].add_attribute(direction_names[d], 0)
                else:
                    blockslist[i].add_attribute(direction_names[d], nhdID)

        self.notify_progress(80)
        # END OF FUNCTION

    # === HEXAGONAL GRID ===
    def create_hexagonal_blocks(self):
        pass

    # === PATCH GRID ===
    def create_vectorpatches(self):
        pass

    # === RASTER GRID ===
    def create_rastermap(self):
        pass


# ==========================================
# STATIC FUNCTIONS
# ==========================================
def determine_number_of_squares(map_width, map_height, blocksize, autosize):
    """ Determines the number of Blocks required for the basic map

    :param map_width: horizontal extent of the map [m]
    :param map_height: vertical extents of the map [m]
    :param blocksize: size of the square block [m]
    :param autosize: autosize the blocks?
    :return:
    """
    if autosize:    # Autosize blocks?
        blocksize = autosize_blocks(map_width, map_height)

    blocks_wide = int(math.ceil(map_width/float(blocksize)))
    blocks_tall = int(math.ceil(map_height/float(blocksize)))
    numblocks = blocks_wide * blocks_tall

    return numblocks, blocks_wide, blocks_tall, blocksize


def autosize_blocks(width, height):
    """Calculates the recommended Block Size dependent on the size of the case study determined by the input map
    dimensions. Takes width and height and returns block size.

    Rules:
       - Based on experience from simulations, aims to reduce simulation times while providing enough accuracy.
       - Aim to simulate under 500 Blocks.

    :param width: the width of the input map in [m] - xmax - xmin
    :param height: the height of the input map in [m] - ymax - ymin
    :return auto-determined blocksize
    """
    block_limit = 2000   # maximum number of Blocks permissible in the case study - Make an option in future.
    tot_area = width * height
    ideal_blocksize = math.sqrt(tot_area / float(block_limit))

    print(f"IdBS: {ideal_blocksize}")

    if ideal_blocksize <= 200:       # If less than 200m, size to 200m x 200m as minimum
        blocksize = 200
    elif ideal_blocksize <= 500:
        blocksize = 500
    elif ideal_blocksize <= 1000:
        blocksize = 1000
    elif ideal_blocksize <= 2000:
        blocksize = 2000
    else:
        blocksize = 5000    # Maximum Block Size will be 5000m x 5000m, we cannot simply afford to go higher
    return blocksize        # because of data resolution, etc.


def create_block_geometry(x, y, bs, ID, boundary):
    """Creates the Rectangular Block Face, the polygon of the block as a UBVector

    :param x: The starting x coordinate (on 0,0 origin)
    :param y: The starting y coordinate (on 0,0 origin)
    :param bs: Block size [m]
    :param ID: the current ID number to be assigned to the Block
    :param boundary: A Shapely polygon object, used to test if the block face intersects
    with it. Also determines whether to save the Block or not.
    :return: UBVector object containing the BlockID, attribute and geometry
    """
    # Define points
    n1 = (x * bs, y * bs, 0)        # Bottom left (x, y, z)
    n2 = ((x + 1) * bs, y * bs, 0)    # Bottom right
    n3 = ((x + 1) * bs, (y + 1) * bs, 0)   # Top right
    n4 = (x * bs, (y + 1) * bs, 0)    # Top left

    # Create the Shapely Polygon and test against the boundary to determine active/inactive.
    blockpoly = Polygon((n1[:2], n2[:2], n3[:2], n4[:2]))
    if Polygon.intersects(boundary, blockpoly):
        # Define edges
        e1 = (n1, n2)   # Bottom left to bottom right
        e2 = (n2, n3)   # Bottom right to top right
        e3 = (n4, n3)   # Top right to top left
        e4 = (n1, n4)   # Top left to bottom left

        # Define the UrbanBEATS Vector Asset
        block_attr = ubdata.UBVector((n1, n2, n3, n4, n1), (e1, e2, e3, e4))
        block_attr.add_attribute("BlockID", int(ID))    # ATTRIBUTE: Block Identification

        xcentre = x * bs + 0.5 * bs
        ycentre = y * bs + 0.5 * bs

        block_attr.add_attribute("CentreX", xcentre)    # ATTRIBUTE: geographic information
        block_attr.add_attribute("CentreY", ycentre)
        block_attr.add_attribute("OriginX", n1[0])
        block_attr.add_attribute("OriginY", n1[1])
        block_attr.add_attribute("Status", 1)           # Start with Status = 1 by default

        return block_attr
    else:
        # Block not within boundary, do not return anything
        return None

