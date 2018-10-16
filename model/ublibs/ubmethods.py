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
import numpy as np

# --- URBANBEATS LIBRARY IMPORTS ---


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


def reviewFileName(fname):
    """Checks the filename for illegal characters, if there are illegal characters, function
    removes them and modifies the filename so that the export function does not crash"""
    illegal_char = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_char:
        if char in fname:
            fname = fname.replace(char, '')
    return fname


def patchdelin_landscape_patch_delineation(landuse, nodatavalue):
    """Performs the patch analysis and returns a full dictionary of the patches found, their properties and
    the rough position of the patch centroid.

    :param landuse: a square matrix of the landscape's land use classification
    :return patches, contains all patches
    """
    # Test condition for delineation:
    # LU Types: [0, 'RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA']
    landusetypes = []
    landusecount = 0
    landusetypes = landuse.flatten()    # Flatten the 2D array to a single 1D list
    landusetypes, landusecounts = np.unique(landusetypes, return_counts=True)   # Get all unique values + frequency
    if nodatavalue in landusetypes:     # Calculate richness
        richness = len(landusetypes) - 1
    else:
        richness = len(landusetypes)
    for e in range(len(landusetypes)):      # Count the number of non-nodata values
        if landusetypes[e] == nodatavalue:
            continue
        else:
            landusecount += landusecounts[e]

    if richness == 0:
        return []
    elif richness == 1:     # A single patch in the Block
        # Create a single patch dictionary of the Block
        patchpoints = []    # (i, j) coordinates of the landuse matrix belonging to the patch
        patchlanduse = 0
        centroidX = []
        centroidY = []
        for i in range(len(landuse)):
            for j in range(len(landuse[i])):
                if landuse[i, j] == nodatavalue:
                    continue
                patchpoints.append((i, j))
                centroidX.append(j)     # X along columns j, Y along rows i!
                centroidY.append(i)
                patchlanduse = int(landuse[i, j])

        patchdict = {}
        patchdict["PatchID"] = 1
        patchdict["PatchIndices"] = patchpoints
        patchdict["Landuse"] = patchlanduse
        patchdict["Centroid"] = (float(sum(centroidX))/float(len(centroidX)),
                                 float(sum(centroidY))/float(len(centroidY)))
        patchdict["AspectRatio"] = float(max(centroidX) - min(centroidX) + 1) / float(max(centroidY) - min(centroidY)+1)
        patchdict["PatchSize"] = len(patchpoints)
        return [patchdict]
    else:
        # Multiple patches in the block, hence do the delineation
        pass    # Code continues below

    patches = []    # Initialize container for all patches
    patch_id_counter = 0    # Initialize the patchID counter
    finished_sign = 0   # Notifies the while loop once all sections of the landusematrix have been allocated

    # Generate Status Matrix
    statusmatrix = np.zeros((len(landuse), len(landuse[0])))
    while finished_sign == 0:
        # Step 1: Find the start position and note the coordinate
        irow, jcol = patchdelin_find_next_start(statusmatrix)   # Returns positions in matrix if point found, else -1

        if irow == -1:  # Check whether delineation has completed
            finished_sign = 1
            continue

        # Step 2: Conduct Grid Scan from irow, jcol
        statusmatrix[irow, jcol] = 1            # mark out this position on the status matrix
        patchdict = patchdelin_grids_scan(landuse, irow, jcol, statusmatrix)  # Run the grid-scan algorithm

        # Step 3: Update status matrix with new data from the patchdictionary and process patch data
        patch_id_counter += 1
        patchdict["PatchID"] = patch_id_counter

        for pt in patchdict["PatchIndices"]:
            statusmatrix[pt[0], pt[1]] = 1      # Set those cells equal to 1 showing that they've been scanned and used

        patches.append(patchdict)
    # Once the loop finishes, return the list of patch dictionaries created from the while loop to the main program
    return patches


def patchdelin_grid_scan(landusematrix, irow, icol, statusmatrix):
    """Conducts the grid_scan algorithm to find the exact continuous patch within the landuse matrix.
    Returns a full patch dictionary.

    :param landusematrix: the 2D matrix containing the land use data
    :param irow: the starting row index
    :param icol: the starting column index
    :param statusmatrix: the zeros status matrix, marking out inaccessible rows/columns
    :return: a patch dictionary containing all patch data
    """
    current_lu = landusematrix[irow, jcol]   # Define the current land use
    i = len(landusematrix)
    j = len(landusematrix[0])

    scanmatrix = np.zeros([i, j])
    scanmatrix[irow, icol] = 1

    patchpoints = []
    centroidX = []
    centroidY = []

    for irow in range(len(scanmatrix)):
        for jcol in range(len(scanmatrix[0])):
            # Check if current cell's value is identical to current_ca_lu
            if statusmatrix[irow, jcol] == 1 or landusematrix[irow, jcol] != current_lu:
                # position already marked in status matrix OR land use at position not the current category
                continue

            # Get Cell's Neighbourhood
            if jcol == 0:    # x-axis neighbours
                dx = [0, 1]  # if we have first column then only forward
            elif jcol == (len(scanmatrix[0]) - 1):
                dx = [-1, 0]  # if we have last column then only backward
            else:
                dx = [-1, 0, 1]  # otherwise allow both
            if irow == 0:    # y-axis neighbours
                dy = [0, 1]  # if we have top row, only move down
            elif irow == (len(scanmatrix[0]) - 1):
                dy = [-1, 0]  # if we have bottom row, only move up
            else:
                dy = [-1, 0, 1]  # otherwise allow both

            # Transfer Function - obtain the total sum of neighbours
            total_neighbour_sum = 0
            for a in dy:        # dy --> rows
                for b in dx:    # dx --> columns
                    total_neighbour_sum += scanmatrix[(irow + a), (jcol + b)]

            # Determine if the cell belongs to the patch or not
            if total_neighbour_sum >= 1:    # meaning there is at least one neighbour adjacent and part of patch
                scanmatrix[irow, jcol] = 1    # mark it in the array for the next iteration
                patchpoints.append((irow, jcol))
                centroidX.append(jcol)
                centroidY.append(irow)
            else:
                scanmatrix[irow, jcol] = 0

    # No PatchID yet, main loop will allocate it
    patchdict = {}
    patchdict["PatchIndices"] = patchpoints
    patchdict["Landuse"] = current_lu
    patchdict["Centroid"] = (float(sum(centroidX))/float(len(centroidX)),
                         float(sum(centroidY))/float(len(centroidY)))
    patchdict["AspectRatio"] = float(max(centroidX) - min(centroidX) + 1) / float(max(centroidY) - min(centroidY)+1)
    patchdict["PatchSize"] = len(patchpoints)   # Simply the number of cells, need to multiply by resolution
    return patchdict


def patchdelin_find_next_start(statusmatrix):
    """Searches for the next starting position in the status matrix, which gradually fills all zeros.
    If no zeros exist in the status matrix, function returns -1.

    :param statusmatrix: a 2D array of zeroes corresponding to the size of the landusematrix
    """
    point_found = 0
    for irow in range(len(statusmatrix)):    # for rows
        for jcol in range(len(statusmatrix[0])):  # for columns
            if point_found == 1:
                break
            if statusmatrix[irow, jcol] == 0:
                point_found = 1
                return irow, jcol
    if point_found == 0:
        return -1, -1   # -1st row and -1st column signals that all areas have been searched


def patchdelin_obtain_patch_from_indices(datamatrix, dataresolution, indices, originalresolution):
    """Returns an array of data points within a matrix of resolution A, corresponding to indices/coordinates
    specified by a list at a given resolution B. This is used when, for example, obtaining elevation data
    for a given land use patch or other data patch when the data sets are not at the same resolution or used
    in a different module. Land use patches are delineated using landscape_patch_delineation() in this script.

    :param datamatrix: a numpy array of i rows and j columns containing the data to be extracted
    :param dataresolution: resolution of the datamatrix [m]
    :param indices: the indices provided from landscape_patch_delineation for Patch ID x
    :param originalresolution: the original resolution of the patch's source data [m]
    :return: a list of data points from the datamatrix corresponding to the similar positions of the indices
    """
    if originalresolution <= dataresolution:
        scalefactor = float(originalresolution) / float(dataresolution)
        # Obtain patches using duplicate rule




    else:   # data resolution < original resolution - multiple cells per index
        pass
        # Do something with indices...




