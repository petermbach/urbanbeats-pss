r"""
@file   lib_delineation/hexgrid.py
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


HEXFACTOR = math.sqrt(3)

def determine_number_of_hexes(map_width, map_height, blocksize, orientation, autosize):
    """ Determines the number of Hexagonal Blocks required for the basic input map dimensions

    :param map_width: horizontal extent of the map [m]
    :param map_height: vertical extent of the map [m]
    :param blocksize: edge length of the hexagon [m]
    :param orientation: orientation of the hexgrid, either "NS"=north-south or "EW"=east-west
    :param autosize: autosize the hexagons?
    :return: total number of hexes, number of hexes wide/tall and the updated hex size (if)
    """
    if autosize:
        pass
        # blocksize = autosize_hexes(map_width, map_height)
    if orientation == "NS":
        blocks_wide = int(math.ceil(map_width/float(1.5*blocksize)))
        blocks_tall = int(math.ceil(map_height/float(blocksize * HEXFACTOR)))
    else:
        blocks_wide = int(math.ceil(map_width / float(blocksize * HEXFACTOR)))
        blocks_tall = int(math.ceil(map_height / float(1.5 * blocksize))) + 1   # One extra based on centroid alignment

    numblocks = blocks_wide * blocks_tall

    return numblocks, blocks_wide, blocks_tall, blocksize


def autosize_hexes(width, height):
    """Calculates the recommended Block Size dependent on the size of the case study, determined by the input map
    dimensions, returns the edge length of the hexagon based on map width and height.

    Rules:

    """
    pass

def create_hex_geometry_ew(x,y,bs, ID, boundary):
    """ Creates the hexagonal Block Face in east-west direction, the polygon of the Block as a UBVector

    :param x: starting x-coordinate (0,0 origin)
    :param y: starting y-coordinate (0,0 origin)
    :param bs: size of the hex
    :param W: height of the map [m]
    :param blocks_wide: number of hex blocks tall
    :param ID: the current ID number to be assigned to the Hex Block
    :param boundary: a shapely polygon object used to test if the hex intersects with it, Also determines whether
    to save the hex or not.
    :return: UBVector object containing BLockID, attributes and geometry
    """
    # Define Hex Points
    #     / 6 \
    #    1     5
    #    |  *  |
    #    2     4
    #     \ 3 /

    # First point is the anchor point - the centroid of the bottom left hex is anchored to the global origin
    h_factor = float('%.5f' % (HEXFACTOR * bs))
    shift_factor = float('%.5f' % (0.5 * h_factor * (y % 2)))
    anchorX = x * h_factor - 0.5*h_factor + shift_factor
    anchorY = y * 1.5 * bs + 0.5 * bs
    h1 = (anchorX, anchorY, 0)
    h2 = (h1[0], h1[1] - bs, 0)
    h3 = (h1[0] + 0.5 * h_factor, h1[1] - 1.5*bs, 0)
    h4 = (h1[0] + h_factor, h1[1] - bs, 0)
    h5 = (h1[0] + h_factor, h1[1], 0)
    h6 = (h1[0] + 0.5 * h_factor, h1[1] + 0.5*bs, 0)

    # Create the Shapely Polygon and test against the boundary to determine active/inactive
    blockpoly = Polygon((h1[:2], h2[:2], h3[:2], h4[:2], h5[:2], h6[:2]))
    if Polygon.intersects(boundary, blockpoly):
        # Define edges (as integers down to the nearest [m])
        e1 = ((int(h2[0]), int(h2[1]), 0), (int(h1[0]), int(h1[1]), 0))     # Left edge (2, 1)
        e2 = ((int(h2[0]), int(h2[1]), 0), (int(h3[0]), int(h3[1]), 0))     # Left bottom (2, 3)
        e3 = ((int(h3[0]), int(h3[1]), 0), (int(h4[0]), int(h4[1]), 0))     # Right bottom (3, 4)
        e4 = ((int(h4[0]), int(h4[1]), 0), (int(h5[0]), int(h5[1]), 0))     # Right edge (4, 5)
        e5 = ((int(h6[0]), int(h6[1]), 0), (int(h5[0]), int(h5[1]), 0))     # Right top (6, 5)
        e6 = ((int(h1[0]), int(h1[1]), 0), (int(h6[0]), int(h6[1]), 0))     # Left top (1, 6)

        # Define the UrbanBEATS Vector Asset
        block_attr = ubdata.UBVector((h1, h2, h3, h4, h5, h6, h1), (e1, e2, e3, e4, e5, e6))
        block_attr.add_attribute("BlockID", int(ID))  # ATTRIBUTE: Block identification

        xcentre = anchorX + 0.5*h_factor
        ycentre = anchorY - 0.5*bs

        xorigin = x * h_factor - 0.5 * h_factor + shift_factor  # Lower left extent X
        yorigin = y * 1.5 * bs - bs     # lower left extent Y

        block_attr.add_attribute("CentreX", xcentre)  # ATTRIBUTE: geographic information
        block_attr.add_attribute("CentreY", ycentre)
        block_attr.add_attribute("OriginX", xorigin)
        block_attr.add_attribute("OriginY", yorigin)
        block_attr.add_attribute("Status", 1)  # Start with Status = 1 by default

        return block_attr
    else:
        # Block not within boundary, do not return anything
        return None


def create_hex_geometry_ns(x, y, bs, H, blocks_tall, ID, boundary):
    """ Creates the Hexagonal Block Face in north-south direction, the polygon of the Block as a UBVector

    :param x: starting x-coordinate (0,0 origin)
    :param y: starting y-coordinate (0,0 origin)
    :param bs: size of the hex
    :param H: height of the map [m]
    :param blocks_tall: number of hex blocks tall
    :param ID: the current ID number to be assigned to the Hex Block
    :param boundary: a shapely polygon object used to test if the hex intersects with it, Also determines whether
    to save the hex or not.
    :return: UBVector object containing BLockID, attributes and geometry
    """
    # Define Hex Points
    #        ___
    #      /5   4\
    #     6   *   3
    #      \1___2/

    # First point is the anchor point - slightly lower than global origin (0,0) shift of y by global map shift
    v_factor = float('%.5f' % (HEXFACTOR * bs))   # distance between parallel edges in a hex (=sqrt(3) x d)
    shift_factor = float('%.5f' % (0.5 * v_factor * (x % 2)))  # in odd column numbers, shift has to be accounted for
    anchorX = x * 1.5 * bs
    anchorY = y * v_factor + (H - blocks_tall*v_factor) + shift_factor
    h1 = (anchorX, anchorY, 0)
    h2 = (h1[0] + bs, h1[1], 0)
    h3 = (h1[0] + 1.5 * bs, h1[1] + 0.5 * v_factor, 0)
    h4 = (h1[0] + bs, h1[1] + v_factor, 0)
    h5 = (h1[0], h1[1] + v_factor, 0)
    h6 = (h1[0] - 0.5 * bs, h1[1] + 0.5 * v_factor, 0)

    # Create the Shapely Polygon and test against the boundary to determine active/inactive
    blockpoly = Polygon((h1[:2], h2[:2], h3[:2], h4[:2], h5[:2], h6[:2]))
    if Polygon.intersects(boundary, blockpoly):
        # Define edges
        e1 = ((int(h1[0]), int(h1[1]), 0), (int(h2[0]), int(h2[1]), 0))     # Bottom edge (1, 2)
        e2 = ((int(h2[0]), int(h2[1]), 0), (int(h3[0]), int(h3[1]), 0))     # Bottom right (2, 3)
        e3 = ((int(h4[0]), int(h4[1]), 0), (int(h3[0]), int(h3[1]), 0))     # Top right (4, 3)
        e4 = ((int(h5[0]), int(h5[1]), 0), (int(h4[0]), int(h4[1]), 0))     # Top edge (5, 4)
        e5 = ((int(h6[0]), int(h6[1]), 0), (int(h5[0]), int(h5[1]), 0))     # Top left (6, 5)
        e6 = ((int(h6[0]), int(h6[1]), 0), (int(h1[0]), int(h1[1]), 0))     # Bottom left (6, 1)

        # Define the UrbanBEATS Vector Asset
        block_attr = ubdata.UBVector((h1, h2, h3, h4, h5, h6, h1), (e1, e2, e3, e4, e5, e6))
        block_attr.add_attribute("BlockID", int(ID))    # ATTRIBUTE: Block identification

        xcentre = anchorX + 0.5*bs
        ycentre = anchorY + 0.5*v_factor

        xorigin = anchorX - 0.5*bs
        yorigin = anchorY

        block_attr.add_attribute("CentreX", xcentre)  # ATTRIBUTE: geographic information
        block_attr.add_attribute("CentreY", ycentre)
        block_attr.add_attribute("OriginX", xorigin)
        block_attr.add_attribute("OriginY", yorigin)
        block_attr.add_attribute("Status", 1)  # Start with Status = 1 by default

        return block_attr
    else:
        # Block not within boundary, do not return anything
        return None