r"""
@file   mod_topography.py
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
import sys
from shapely.geometry import Polygon
import rasterio
import rasterio.features
import numpy as np

from model.ubmodule import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubdatatypes as ubdata

# --- LIBRARY SETTINGS ---
np.set_printoptions(threshold=sys.maxsize, linewidth=5000)      # Numpy Print Options -- FOR DEBUG


class MapTopographyToSimGrid(UBModule):
    """ Generates the simulation grid upon which many assessments will be based. This SimGrid will provide details on
    geometry and also neighbourhood information."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 5
    longname = "Map Topography"
    icon = ":/icons/topography.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES HOLDING IMPORTANT REFERENCES TO SIMULATION - SET AT INITIALIZATION
        self.assets = None  # If used as one-off on-the-fly modelling, then scenario is None
        self.meta = None  # Simulation metadata contained in assets, this variable will hold it
        self.xllcorner = None
        self.yllcorner = None
        self.assetident = ""
        self.elevationmap = None
        self.nodata = None
        self.maxiter = 5    # The maximum number of iterations a while loop will take to course correct assets

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.create_parameter("elevmapdataid", STRING, "Name of the elevation map to load for mapping")
        self.assetcolname = "(select asset collection)"
        self.elevmapdataid = "(no elevation maps in project)"

        self.create_parameter("nodatatask", STRING, "What should be done if nodata value mapped?")
        self.nodatatask = "STATUS"      # STATUS = Set status to zero, INTERP = interpolate

        self.create_parameter("demsmooth", BOOL, "Perform smoothing on the DEM?")
        self.create_parameter("dempasses", DOUBLE, "Number of passes to perform smoothing for")
        self.demsmooth = 0
        self.dempasses = 1

        self.create_parameter("demstats", BOOL, "Calculate statistics for coarse grid DEMs?")
        self.create_parameter("demminmax", BOOL, "Indicate lowest elevation point on the map?")
        self.create_parameter("slope", BOOL, "Calculate slope?")
        self.create_parameter("aspect", BOOL, "Calculate aspect?")
        self.demstats = 0
        self.demminmax = 0
        self.slope = 0
        self.aspect = 0

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error! Missing Asset Collection!")

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection Missing Metadata")
        self.meta.add_attribute("mod_topography", 1)    # This denotes that the module will be run
        self.assetident = self.meta.get_attribute("AssetIdent")     # Get the geometry type before starting!

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

        # If the asset collection does not yet have a localities asset, create one...

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Topography data to Simulation")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        # --- SECTION 1 - Get the elevation map data to be mapped
        elevmap = self.datalibrary.get_data_with_id(self.elevmapdataid)
        fullpath = elevmap.get_data_file_path() + elevmap.get_metadata("filename")
        self.notify("Loading Elevation Map: "+str(elevmap.get_metadata("filename")))

        self.elevationmap = rasterio.open(fullpath)     # Variable assignment
        self.nodata = self.elevationmap.nodata

        # Program Notifications
        self.notify("Raster Shape: "+str(self.elevationmap.shape))
        self.notify(str(self.elevationmap.bounds))
        self.notify("Nodata Value: "+str(self.nodata))
        self.notify("Raster Resolution: "+str(self.elevationmap.res))
        self.notify_progress(20)

        # --- SECTION 2 - Begin mapping the data based on geometry type - calculate relevant stats if needed
        self.notify("Mapping elevation data to simulation grid")
        griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets to map data to: "+str(len(griditems)))

        # TRACKER VARIABLES
        if self.demminmax:
            lowest_elev = [9999, 0]         # Tracking the lowest and highest elevation points [elev, ID]
            highest_elev = [-9999, 0]
            # Create the asset collection Localities...

        exceptions = []     # To hold asset exceptions where no data was found
        for i in range(len(griditems)):     # Loop across all polygon assets
            # Get the asset object
            asset = griditems[i]
            assetid = asset.get_attribute(self.assetident)
            self.notify("Currently Mapping: " + str(self.assetident) + str(assetid))

            mdata = ubspatial.retrieve_raster_data_from_mask(self.elevationmap, asset, self.xllcorner, self.yllcorner)
            if mdata is None:
                self.notify(self.assetident + str(assetid) + " does not fall within the bounds, skipping.")
                asset.add_attribute("Elev_Avg", float(self.nodata))
                asset.add_attribute("Elev_Min", float(self.nodata))
                asset.add_attribute("Elev_Max", float(self.nodata))
                if self.nodatatask == "STATUS":
                    asset.add_attribute("Status", 0)
                else:
                    exceptions.append(asset)
                continue

            # Write the basic extracted data to the attributes list
            if len(mdata) == 0:       # If no data leftover, assign cells as self.nodata
                asset.add_attribute("Elev_Avg", self.nodata)
                asset.add_attribute("Elev_Min", self.nodata)
                asset.add_attribute("Elev_Max", self.nodata)
                if self.nodatatask == "STATUS":
                    asset.add_attribute("Status", 0)
                else:
                    exceptions.append(asset)
                continue
            else:       # Calculate metrics and transfer elevation to asset
                asset.add_attribute("Elev_Avg", float(mdata.mean()))
                asset.add_attribute("Elev_Min", float(mdata.min()))
                asset.add_attribute("Elev_Max", float(mdata.max()))

            # Work out some map-wide stats
            if self.demminmax:
                if mdata.mean() < lowest_elev[0]:
                    lowest_elev = [mdata.mean(), assetid]
                if mdata.mean() > highest_elev[0]:
                    highest_elev = [mdata.mean(), assetid]

        if self.demminmax:
            self.notify("Lowest elevation in ID"+str(lowest_elev[1])+": "+str(lowest_elev[0])+"m")
            self.notify("Highest elevation in ID" + str(highest_elev[1]) + ": " + str(highest_elev[0]) + "m")

        self.notify_progress(70)

        # Interpolate missing items
        if self.nodatatask == "INTERP":
            self.interpolate_missing_elevations(exceptions)

        self.notify_progress(80)

        # --- SECTION 3 - Perform DEM Smoothing if requested
        if self.demsmooth:
            for i in range(int(self.dempasses)):
                self.notify("Performing Smoothing Pass #"+str(i+1))
                self.perform_dem_smoothing(griditems)

        self.notify_progress(90)

        # --- SECTION 4 - Calculate slope and aspect
        self.notify("Determining slope and aspect")




        self.notify("Mapping of elevation data to simulation grid complete")
        self.notify_progress(100)  # Must notify of 100% progress if the 'close' button is to be renabled.
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def interpolate_missing_elevations(self, exceptions):
        """Interpolates the missing elevation data from its neighbours, iterating maximum number of times."""
        iterations = 0
        remove_from_list = []
        while iterations < self.maxiter:
            for a in exceptions:
                nhd = a.get_attribute("Neighbours")
                avg, min, max = self.get_neighbourhood_elevations(nhd)
                avg = np.delete(avg, np.where(avg == self.nodata))
                min = np.delete(min, np.where(min == self.nodata))
                max = np.delete(max, np.where(max == self.nodata))
                if len(avg) == 0:
                    continue
                a.add_attribute("Elev_Avg", avg.mean())
                a.add_attribute("Elev_Min", min.mean())
                a.add_attribute("Elev_Max", max.mean())
                remove_from_list.append(a)

            # Loop complete, remove all identified exceptions with data now from exceptions list
            [exceptions.pop(exceptions.index(e)) for e in remove_from_list]
            remove_from_list = []       # Reset for next while-loop iterations
            if len(exceptions) == 0:    # If all exceptions have been addressed, break
                return True
            else:
                iterations += 1         # Else continue iterations

        # Loop through remaining exceptions and assign Status 0
        for a in exceptions:
            a.add_attribute("Status", 0)
        return

    def get_neighbourhood_elevations(self, nhd):
        """Returns min, max and avg elevation of all neighbours in the input list"""
        elev_avg, elev_min, elev_max = [], [], []
        for i in range(len(nhd)):
            asset = self.assets.get_asset_with_name(self.assetident+str(nhd[i]))
            elev_avg.append(asset.get_attribute("Elev_Avg"))
            elev_min.append(asset.get_attribute("Elev_Min"))
            elev_max.append(asset.get_attribute("Elev_Max"))
        return np.array(elev_avg), np.array(elev_min), np.array(elev_max)

    def perform_dem_smoothing(self, assets):
        """Runs through all items in the assets list and calculates average elevation from it and
        neighbourhood to smooth the DEM."""
        update = []
        for i in range(len(assets)):
            curasset = assets[i]
            avg = curasset.get_attribute("Elev_Avg")
            min = curasset.get_attribute("Elev_Min")
            max = curasset.get_attribute("Elev_Max")

            if avg == -9999 or curasset.get_attribute("Status") == 0:
                continue

            avglist, minlist, maxlist = self.get_neighbourhood_elevations(curasset.get_attribute("Neighbours"))
            avglist = np.delete(avglist, np.where(avglist == self.nodata))
            avglist = avglist.tolist()
            avglist = np.array(avglist.append(avg))

            minlist = np.delete(minlist, np.where(minlist == self.nodata))
            minlist = minlist.tolist()
            minlist = np.array(minlist.append(min))

            maxlist = np.delete(maxlist, np.where(maxlist == self.nodata))
            maxlist = maxlist.tolist()
            maxlist = np.array(maxlist.append(max))

            print(avglist, minlist, maxlist)
            update.append([curasset, avglist.mean(), minlist.mean(), maxlist.mean()])

        for i in range(len(update)):
            update[i][0].add_attribute("Elev_Avg", update[i][1])
            update[i][0].add_attribute("Elev_Min", update[i][2])
            update[i][0].add_attribute("Elev_Max", update[i][3])

    def calculate_asset_slope_and_aspect(self):
        pass
