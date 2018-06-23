# -*- coding: utf-8 -*-
"""
@file   ubmethods.py
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

@section ABOUT

ubmethods.py contains a collection of top-level functions used throughout the various UrbanBEATS
modules. These functions perform a number of model-specific operations that could also be packaged with the
individual modules, but are better off modularised within this particular script.

Index of Functions + locations of their use:

---------------------------------------------------------------------------------------------------------------
Name                Description                                         Modules used
---------------------------------------------------------------------------------------------------------------
autosize_blocks     determines block size automatically                 delinblocks

---------------------------------------------------------------------------------------------------------------
"""

__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2018. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
import math

# --- URBANBEATS LIBRARY IMPORTS ---


def autosize_blocks(self, width, height):
    """Calculates the recommended Block Size dependent on the size of the case study determined by the input map
    dimensions. Takes width and height and returns block size.

    Rules:
       - Based on experience from simulations, aims to reduce simulation times while providing enough accuracy.
       - Aim to simulate under 500 Blocks.

    :param width: the width of the input map in [m] - xmax - xmin
    :param height: the height of the input map in [m] - ymax - ymin
    :return auto-determined blocksize
    """
    block_limit = 2000   # maximum number of Blocks permissible in the case study
    tot_area = width * height
    ideal_blocksize = math.sqrt(tot_area / float(block_limit))

    print "IdBS:", ideal_blocksize

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
    return blocksize

