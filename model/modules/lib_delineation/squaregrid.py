r"""
@file   lib_delineation/squaregrid.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2018  Peter M. Bach

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
__copyright__ = "Copyright 2018. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
import math
from shapely.geometry import Polygon, LineString

import model.ublibs.ubdatatypes as ubdata

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

