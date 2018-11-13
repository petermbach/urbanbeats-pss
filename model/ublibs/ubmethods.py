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
Name                                    Description                                         Modules used
---------------------------------------------------------------------------------------------------------------
autosize_blocks                         determines block size automatically                 delinblocks
calculate_frequency_of_lu_classes       tallies frequency of land use classes               delinblocks
calculate_metric_richness               calculates the richness of categories               delinblocks
calculate_metric_shannon                calcualtes Shannon Spatial Indices                  delinblocks
review_filename                          reviews standard file naming for illegal characters delinblocks
patchdelin_landscape_patch_delineation  main patch delineation function                     delinblocks
patchdelin_grid_scan                    scans the input grid for a patch                    delinblocks
patchdelin_find_next_start              finds the next scan start position in a grid        delinblocks
patchdelin_obtain_patch_from_indices    obtains patch from indices specified                delinblocks
---------------------------------------------------------------------------------------------------------------
"""

__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2018. Peter M. Bach"

# --- PYTHON LIBRARY IMPORTS ---
import math
import numpy as np
from ..progref import ubglobals
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
    block_limit = 2000   # maximum number of Blocks permissible in the case study - Make an option in future.
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
    return blocksize        # because of data resolution, etc.


def calculate_frequency_of_lu_classes(lucdatamatrix):
    """ Tallies the frequency of land use classes within the given Block/Hex. Returns the 'Activity'
    attribute and a list of LUC frequencies.

    :param lucdatamatrix: the two-dimensional matrix extracted from the LU raster UBRaster() object
    :return a list of all 13 classes and their relative proportion, activity, the total data coverage.
    """
    # Step 1 - Order all data entries into a lit of 13 elements
    # Categories: 'RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA'
    lucprop = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_n_luc = 0     # Counts the total elements of valid land use classes i.e. skips counting NODATA
    matrix_size = 0     # Counts total elements in the 2D array
    for i in range(len(lucdatamatrix)):
        for j in range(len(lucdatamatrix[0])):
            matrix_size += 1
            landclass = lucdatamatrix[i, j]     # numpy array
            if int(landclass) == -9999:
                pass
            else:
                lucprop[int(landclass) - 1] += 1
                total_n_luc += 1

    # Step 2 - Convert frequency to proportion
    if total_n_luc == 0:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0
    for i in range(len(lucprop)):
        lucprop[i] = float(lucprop[i]) / float(total_n_luc)
    activity = float(total_n_luc) / float(matrix_size)
    return lucprop, activity


def calculate_metric_richness(landclassprop):
    """Calculates the Richness metric, which is simply the total number of unique categories in the provided
    land use proportions list

    :param landclassprop: A list [] specifying the relative proportions of land use categories. Sum = 1
    :return: the richness index
    """
    richness = 0
    for i in landclassprop:
        if i != 0:
            richness += 1
    return richness


def calculate_metric_shannon(landclassprop, richness):
    """Calculates the Shannon diversity, dominance and evenness indices based on the proportion of different land
    use classes and the richness.

    :param landclassprop: A list [] specifying the relative proportions of land use categories. Sum = 1
    :param richness: the richness index, which is the number of unique land use classes in the area
    :return: shandiv (Diversity index), shandom (Dominance index) and shaneven (Evenness index)
    """
    if richness == 0:
        return 0, 0, 0

    # Shannon Diversity Index (Shannon, 1948) - measures diversity in categorical data, the information entropy of
    # the distribution: H = -sum(pi ln(pi))
    shandiv = 0
    for sdiv in landclassprop:
        if sdiv != 0:
            shandiv += sdiv * math.log(sdiv)
    shandiv = -1 * shandiv

    # Shannon Dominance Index: The degree to which a single class dominates in the area, 0 = evenness
    shandom = math.log(richness) - shandiv

    # Shannon Evenness Index: Similar to dominance, the level of evenness among the land classes
    if richness == 1:
        shaneven = 1
    else:
        shaneven = shandiv / math.log(richness)
    return shandiv, shandom, shaneven


def review_filename(fname):
    """Checks the filename for illegal characters, if there are illegal characters, function
    removes them and modifies the filename so that the export function does not crash"""
    for char in ubglobals.NOCHARS:
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
        patchdict["Centroid_xy"] = (float(sum(centroidX))/float(len(centroidX)),
                                 float(sum(centroidY))/float(len(centroidY)))
        patchdict["AspRatio"] = float(max(centroidX) - min(centroidX) + 1) / float(max(centroidY) - min(centroidY)+1)
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

        if irow == -1 and jcol == -1:  # Check whether delineation has completed
            finished_sign = 1
            continue

        # Step 2: Conduct Grid Scan from irow, jcol
        statusmatrix[irow, jcol] = 1            # mark out this position on the status matrix
        patchdict = patchdelin_grid_scan(landuse, irow, jcol, statusmatrix)  # Run the grid-scan algorithm

        # Step 3: Update status matrix with new data from the patchdictionary and process patch data
        patch_id_counter += 1
        patchdict["PatchID"] = patch_id_counter

        for pt in patchdict["PatchIndices"]:
            statusmatrix[pt[0], pt[1]] = 1      # Set those cells equal to 1 showing that they've been scanned and used

        patches.append(patchdict)
    # Once the loop finishes, return the list of patch dictionaries created from the while loop to the main program
    return patches


def patchdelin_grid_scan(landusematrix, irow, jcol, statusmatrix):
    """Conducts the grid_scan algorithm to find the exact continuous patch within the landuse matrix.
    Returns a full patch dictionary.

    :param landusematrix: the 2D matrix containing the land use data
    :param irow: the starting row index
    :param icol: the starting column index
    :param statusmatrix: the zeros status matrix, marking out inaccessible rows/columns
    :return: a patch dictionary containing all patch data
    """
    current_lu = landusematrix[irow, jcol]   # Define the current land use
    scanmatrix = np.zeros([len(landusematrix), len(landusematrix[0])])
    scanmatrix[irow, jcol] = 1
    patch_area_previous = 0
    patch_area_current = -9999   # Need to go through the loop multiple times

    while patch_area_current != patch_area_previous:
        patch_area_previous = patch_area_current

        for i in range(len(scanmatrix)):
            for j in range(len(scanmatrix[0])):
                # Check if current cell's value is identical to current_ca_lu
                if statusmatrix[i, j] == 1 or landusematrix[i, j] != current_lu:
                    # position already marked in status matrix OR land use at position not the current category
                    continue

                # Get Cell's Neighbourhood
                if j == 0:    # x-axis neighbours
                    dx = [0, 1]  # if we have first column then only forward
                elif j == (len(scanmatrix[0]) - 1):
                    dx = [-1, 0]  # if we have last column then only backward
                else:
                    dx = [-1, 0, 1]  # otherwise allow both
                if i == 0:    # y-axis neighbours
                    dy = [0, 1]  # if we have top row, only move down
                elif i == (len(scanmatrix) - 1):
                    dy = [-1, 0]  # if we have bottom row, only move up
                else:
                    dy = [-1, 0, 1]  # otherwise allow both

                # Transfer Function - obtain the total sum of neighbours
                total_neighbour_sum = 0
                total_neighbour_count = 0
                for a in dy:        # dy --> rows
                    for b in dx:    # dx --> columns
                        total_neighbour_count += 1
                        total_neighbour_sum += scanmatrix[(i + a), (j + b)]

                # Determine if the cell belongs to the patch or not
                if total_neighbour_sum >= 1:    # meaning there is at least one neighbour adjacent and part of patch
                    scanmatrix[i, j] = 1    # mark it in the array for the next iteration
                    # if (i, j) not in patchpoints:
                    #     patchpoints.append((i, j))
                    #     centroidX.append(j)
                    #     centroidY.append(i)
                else:
                    scanmatrix[i, j] = 0

        patch_area_current = 0
        for i in range(len(scanmatrix)):
            patch_area_current += sum(scanmatrix[i])
        # Update the current patch size, if the patch is still being scanned, it should grow
        # if the patch has finished being delineated, then the algorithm should terminate

    # No PatchID yet, main loop will allocate it
    patchpoints = []        # Grab all patch points and the centroid point
    centroidX = []          # and calculate size of the patch.
    centroidY = []
    for i in range(len(scanmatrix)):
        for j in range(len(scanmatrix[0])):
            if scanmatrix[i, j] == 1:
                patchpoints.append((i, j))
                centroidX.append(j)
                centroidY.append(i)

    patchdict = {}
    patchdict["PatchIndices"] = patchpoints
    patchdict["Landuse"] = current_lu

    # CENTROID OF THE PATCH - 3 methods - unsure as to which one is really superior...
    # METHOD 1 - Using the xmin/xmax, ymin/ymax mid-points - simple and fast, but probably most inaccurate as it is not
    # ---------- necessarily a true reflection of how to calculate a centroid
    # patchdict["Centroid_xy"] = ((max(centroidX)+min(centroidX))/2.0, (max(centroidY) + min(centroidY))/2.0)

    # METHOD 2 - Taking the median of all X-coordinates and Y-coordinates, fairly good a capturing centroids of patches
    # ---------- and fast. Also considers the data spread for distorted shapes.
    patchdict["Centroid_xy"] = (np.median(centroidX), np.median(centroidY))

    # METHOD 3 - Calculating the average X and average Y-coordinate from all of the patch's points, both internal and
    # ---------- external. Not as fast, but still pretty accurate.
    # patchdict["Centroid_xy"] = ((float(sum(centroidX))/float(len(centroidX))),
    #                             (float(sum(centroidY))/float(len(centroidY))))
    
    patchdict["AspRatio"] = float(max(centroidX) - min(centroidX) + 1) / float(max(centroidY) - min(centroidY)+1)
    patchdict["PatchSize"] = len(patchpoints)   # Simply the number of cells, need to multiply by unit area
    return patchdict


def patchdelin_find_next_start(statusmatrix):
    """Searches for the next starting position in the status matrix, which gradually fills all zeros.
    If no zeros exist in the status matrix, function returns -1.

    :param statusmatrix: a 2D array of zeroes corresponding to the size of the landusematrix
    """
    for irow in range(len(statusmatrix)):    # for rows
        for jcol in range(len(statusmatrix[0])):  # for columns
            if statusmatrix[irow, jcol] == 0:
                return irow, jcol
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
    return True