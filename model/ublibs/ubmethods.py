r"""
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

# --- URBANBEATS LIBRARY IMPORTS ---
from ..progref import ubglobals


def adjust_sample_range(parmin, parmax, parusemed):
    """Adjusts a stochastic sampling based on the input parameters of minimum, maximum and median.

    :param parmin: minimum sampling value of the parameter
    :param parmax: maximum smpling value of the parameter
    :param parusemed: boolean, use the median value?
    :return a list object containing two values representing the sampling range if median = True, returns same values
    """
    if parusemed:
        med = (parmin + parmax) / 2.0
        return [med, med]
    else:
        return [parmin, parmax]


def calculate_slope(z_central, z_neighbours, L_x, L_y, nodatavalue):
    """Calculates the slope based on the ESRI ArcMap Methodology using inputs of the central cell
    and the elevation of its neighbours. Returns the slope in radians and degrees

    :param z_central: elevation of the central cell (in units consistent with the other inputs [e.g. m]
    :param z_neighbours: elevation of neighbours, list() in cardinal directions [N, NE, E, SE, S, SW, W, NW]
    :param L_x: unit length in the x-direction
    :param L_y: unit length in the y-direction
    :param nodatavalue: the nodatavalue if data is not present.
    :return: slope_radians, slope_deg
    """
    # Check if neighbour values are
    if z_central == nodatavalue:
        return nodatavalue, nodatavalue      # No data, so simply return no-datavalue

    # Replace all no-data values in the z_neighbours with the z_central cell
    z = [z_central if z_neighbours[i] == nodatavalue else z_neighbours[i] for i in range(len(z_neighbours))]

    # Calculate slope z is mapped as [N, NE, E, SE, S, SW, W, NW]
    dz_dx = ((z[1] + 2*z[2] + z[3]) - (z[5] + 2*z[6] + z[7]))/(8 * L_x)     #[NE, 2E, SE] - [SW, W, NW]
    dz_dy = ((z[7] + 2 * z[0] + z[1]) - (z[3] + 2 * z[4] + z[5])) / (8 * L_y)   #[NW, 2N, NE] - [SW, 2S, SE]
    slope_rad = math.sqrt(math.pow(dz_dx, 2) + math.pow(dz_dy, 2))
    slope_deg = slope_rad * 57.29578        # 57.29578 = 180 / pi()
    return slope_rad, slope_deg


def calculate_aspect(z_central, z_neighbours, nodatavalue):
    """Calculates the aspect according to ESRI ArcMap algorithm of a neighbourhood of nine cells. Returns the aspect
    as a degree on the compass rose with North being 0/360 deg and moving clockwise.

    :param z_central: elevation of the central cell (in units consistent with the other inputs [e.g. m]
    :param z_neighbours: elevation of neighbours, list() in cardinal directions [N, NE, E, SE, S, SW, W, NW]
    :param nodatavalue: the nodatavalue if data is not present.
    :return: aspect_deg - the aspect in degrees measured from North Being 0 degrees clockwise
    """
    # Check if neighbour values are
    if z_central == nodatavalue:
        return nodatavalue, nodatavalue  # No data, so simply return no-datavalue

    # Replace all no-data values in the z_neighbours with the z_central cell
    z = [z_central if z_neighbours[i] == nodatavalue else z_neighbours[i] for i in range(len(z_neighbours))]

    # Calculate aspect z is mapped as [N, NE, E, SE, S, SW, W, NW]
    dz_dx = ((z[1] + 2 * z[2] + z[3]) - (z[5] + 2 * z[6] + z[7])) / 8  # [NE, 2E, SE] - [SW, W, NW]
    dz_dy = ((z[7] + 2 * z[0] + z[1]) - (z[3] + 2 * z[4] + z[5])) / 8  # [NW, 2N, NE] - [SW, 2S, SE]
    aspect = 57.29578 * math.atan2(dz_dy, -dz_dx)

    if aspect < 0:      # CONVERT TO COMPASS ROSE
        aspect_deg = 90.0 - aspect
    elif aspect > 90:
        aspect_deg = 360.0 - aspect + 90.0
    else:
        aspect_deg = 90.0 - aspect
    return aspect_deg


def calculate_frequency_of_lu_classes(lucdatamatrix, nodatavalue, mask_count):
    """ Tallies the frequency of land use classes within the given Block/Hex. Returns the 'Activity'
    attribute and a list of LUC frequencies.

    :param lucdatamatrix: the two-dimensional matrix extracted from the LU raster UBRaster() object
    :param nodatavalue: the nodata value of the current lucdatamatrix (may differ between data sets)
    :param mask_count: the number of cells not valid within the lucdatamatrix (e.g. corners in hexagonal representation)
    :return a list of all 13 classes and their relative proportion, activity, the total data coverage.
    """
    # Step 1 - Order all data entries into a lit of 13 elements
    # Cats: 'RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA', 'WAT', 'FOR', 'AGR'
    lucprop = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_n_luc = 0     # Counts the total elements of valid land use classes i.e. skips counting NODATA
    matrix_size = 0     # Counts total elements in the 2D array
    for i in range(len(lucdatamatrix)):
        for j in range(len(lucdatamatrix[0])):
            landclass = lucdatamatrix[i, j]     # numpy array
            matrix_size += 1  # Count towards 'activity'
            if int(landclass) == nodatavalue:
                pass
            else:
                matrix_size += 1  # Count towards 'activity'
                lucprop[int(landclass) - 1] += 1
                total_n_luc += 1

    # Step 2 - Convert frequency to proportion
    matrix_size -= mask_count
    if total_n_luc == 0:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0
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


def get_subregions_subset_from_blocks(regiontype, blockslist):
    """Scans the list of Blocks and returns a list set of all names of sub-regions within the map.

    :param regiontype: the attribute name representing the region type: "Region", "Suburb", "PlanZone"
    :param blockslist: the list of UBVector() Block objects
    """
    regions = []
    for b in blockslist:
        if b.get_attribute(regiontype) is None:
            continue
        elif b.get_attribute(regiontype) in regions:
            continue
        else:
            regions.append(b.get_attribute(regiontype))
    return regions


def get_subset_of_blocks_by_region(regiontype, regionname, blockslist):
    """Returns a list of blocks for a particular region type and region name as a list. This list can be scanned
    for attributes."""
    newblockslist = []
    for i in range(len(blockslist)):
        if not blockslist[i].get_attribute("Status") or blockslist[i].get_attribute(regiontype) != regionname:
            continue
        else:
            newblockslist.append(blockslist[i])
    return newblockslist


def get_block_attribute_for_region(regiontype, regionname, blockslist, att_name):
    """Scans the list of Blocks and returns a list of attribute values with the given attribute name for all Blocks
    within a defined region.

    :param regiontype: "Region", "Suburb", "PlanZone"
    :param regionname: The string name of the region
    :param blockslist: the list of UBVector() objects representing the Blocks
    :param att_name: the name of the attribute to scan for
    :return: a list [] of the attribute values for that region
    """
    att_values = []
    for b in blockslist:
        if not b.get_attribute("Status"):
            continue
        if b.get_attribute(regiontype) != regionname:
            continue    # If the Block is not in the designated region, skip
        else:
            att_values.append(b.get_attribute(att_name))
    return att_values


def find_dominant_category(datamatrix, nodatavalue):
    """Finds the dominant category in a data matrix and returns the category name.

    :param datamatrix: the 2D array containing a snippet of the loaded data
    :param nodatavalue: the nodata value of the data set, used if no data is available.
    """
    datavalues = datamatrix.flatten()       # Flatten the 2D matrix
    categories = list(set(datavalues))      # Get the set of unique categories
    freq = np.zeros(len(categories))        # Set up a zeros list for each category
    for i in datavalues:
        freq[int(categories.index(i))] += 1     # Tally up frequencies
    if sum(freq) == 0:          # If everything is zero (i.e. nodata)
        return nodatavalue
    else:
        return categories[freq.tolist().index(max(freq))]    # Could also return nodata!


def get_central_coordinates(ubvec):
    """Returns the CentreX, CentreY of the current ubVector object as a tuple."""
    return (ubvec.get_attribute("CentreX"), ubvec.get_attribute("CentreY"))


def review_filename(fname):
    """Checks the filename for illegal characters, if there are illegal characters, function
    removes them and modifies the filename so that the export function does not crash"""
    for char in ubglobals.NOCHARS:
        if char in fname:
            fname = fname.replace(char, '')
    return fname


def remove_neighbour_from_block(block_vec, neigh_id):
    """Removes the ID 'neigh_id' from the current Block block_vec's Neighbours attribute list. This
    function is called if the Block status is modified to zero over the course of the simulation and
    the Block is essentially removed from the simulation. This prevents the model from calling Blocks
    that do not exist due to the neighbourhood later on.

    :param block_vec: The UBVector() instance of the block, whose attribute Neighbours is to be modified
    :param neigh_id: the ID int() of the Block in the neighbourhood to be removed.
    :return: no return, the Block's "Neighbours" attribute is modified.
    """
    nhd = block_vec.get_attribute("Neighbours")
    try:
        nhd.pop(nhd.index(int(neigh_id)))
    except IndexError:
        return True
    except ValueError:
        return True
    block_vec.change_attribute("Neighbours", nhd)
    return True


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

        # Relocate the centroid into the patch itself so that it is spatially relevant in the case study
        mindist = np.inf
        cj = float(sum(centroidX)) / float(len(centroidX))
        ci = float(sum(centroidY)) / float(len(centroidY))
        centroidfinal = [cj, ci]
        for i in range(len(patchpoints)):
            pp = patchpoints[i]
            dist = pow(pp[0] - ci,2) + pow(pp[1] - cj,2)    # Squared distance
            if dist < mindist:
                mindist = dist
                centroidfinal = pp

        patchdict = {}
        patchdict["PatchID"] = 1
        patchdict["PatchIndices"] = patchpoints
        patchdict["Landuse"] = patchlanduse
        patchdict["Centroid_xy"] = (centroidfinal[0], centroidfinal[1])
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


def extract_data_for_patch_from_map(originXY, input_res, mapXY, map_res, patch, datasquare):
    """Maps data from the datasquare array to the current patch object (UBVector()) based on the origin and map
    coordintaes. The information is then transferred based on the mathematical rule.

    :param originXY:
    :param mapXY:
    :param patch:
    :param datasquare:
    :param transferrule:
    :return:
    """
    offsets = [originXY[0] - mapXY[0], originXY[1] - mapXY[1]]
    resratio = float(input_res / map_res)
    patchpoints = patch.get_attribute("PatchIndices")
    data = []
    for p in patchpoints:
        if input_res == map_res:    # if the resolutions are equal, simply transfer the data
            try:
                data.append(datasquare[p[0], p[1]])     # 1 for 1 data transfer
            except IndexError:
                # print "IndexError:", p[0], p[1]
                pass
        elif input_res < map_res:   # if the original resolution of the patch is finer than the map
            row_loc = int((p[0] * input_res + offsets[1]) / map_res)    # using the y-offset
            col_loc = int((p[1] * input_res + offsets[0]) / map_res)    # using the x-offset
            data.append(datasquare[row_loc, col_loc])
            data.append(datasquare[row_loc, col_loc])
        else:   # if the map resolution is finer than the original patch
            rowmin, rowmax = int(math.ceil(p[0] * resratio)), int(math.ceil((p[0]+1) * resratio))
            colmin, colmax = int(math.ceil(p[1] * resratio)), int(math.ceil((p[1]+1) * resratio))
            data = datasquare[rowmin:rowmax, colmin:colmax].flatten().tolist()
    return data


def normalize_weights(weights_matrix, method):
    """Normalizes the weights within a weights matrix based on the sum of weights. According to a specific method.

    :param weights_matrix: a list of weight scores [ ] of any length.
    :param method: S = sum, normalize 0 to 1, A = average, normalize against average
    :return: a list [ ] of equal length with the normalized weights."""
    if method == "SUM":
        tot = sum(weights_matrix)
        for i in range(len(weights_matrix)):
            weights_matrix[i] = float(weights_matrix[i] / tot)
    elif method == "AVG":
        avg = float(sum(weights_matrix) / len(weights_matrix))
        for i in range(len(weights_matrix)):
            weights_matrix[i] = float(weights_matrix[i] / avg)
    return weights_matrix


def calculate_accessibility_factor(dist, aj):
    """Calculates the accessibility factor Aij for cell i and land use j as a function of distance from the
    cell to the nearest map feature. Depending on the value of aj, a specific equation is used.

    :param dist: the Euclidean distance [m] between cell i's centroid and the nearest feature
    :param aj: the importance for land use j of accessibility to the feature in question
    :return: Aij - the accessibility factor
    """
    try:
        if aj == 0:
            return 0    # No accessibility influence
        if aj > 0:
            return float(aj / (aj + dist))
        else:
            return float(dist / (abs(aj) + dist))
    except ZeroDivisionError:
        print("Zero division!")
        return 0
