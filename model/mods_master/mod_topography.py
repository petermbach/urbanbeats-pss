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
__copyright__ = "Copyright 2022. Peter M. Bach"

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
        self.cellsize = None    # (x, y)
        self.bounds = None      # (left, bottom, right, top)
        self.nodata = None

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
        self.elevationmap = rasterio.open(fullpath)
        self.cellsize = self.elevationmap.res
        self.bounds = self.elevationmap.bounds
        self.nodata = self.elevationmap.nodata
        self.notify("Raster Shape: "+str(self.elevationmap.shape))
        self.notify(str(self.bounds))
        self.notify("Nodata Value: "+str(self.nodata))
        self.notify("Raster Resolution: "+str(self.cellsize))
        self.notify_progress(20)

        # --- SECTION 2 - Begin mapping the data based on geometry type - calculate relevant stats if needed
        self.notify("Mapping elevation data to simulation grid")
        griditems = self.assets.get_assets_with_identifier(self.assetident)
        self.notify("Total assets to map data to: "+str(len(griditems)))

        # TRACKER VARIABLES
        if self.demminmax:
            lowest_elev = -9999         # Tracking the lowest and highest elevation points
            highest_elev = -9999
            # Create the asset collection Localities...

        for i in range(len(griditems)):     # Loop across all polygon assets
            # Get the asset object
            asset = griditems[i]
            assetid = asset.get_attribute(self.assetident)
            self.notify("Currently Mapping: " + str(self.assetident) + str(assetid))

            # Get two bounds: one for the local bounds of the polygon and one for indexing the raster data in the PRJCS
            assetpts = asset.get_points()       # Get its geometry at (0,0) origin
            assetpoly = Polygon(assetpts)       # Make a shapely polygon to figure out bounds
            maskoffsets = [assetpoly.bounds[0], assetpoly.bounds[1]]    # Offsets for the local mask
            assetbounds = [assetpoly.bounds[0]+self.xllcorner, assetpoly.bounds[1]+self.yllcorner,
                           assetpoly.bounds[2]+self.xllcorner, assetpoly.bounds[3]+self.yllcorner]  # Spatial bounds

            # Identify the raster extents and extract the data matrix
            llindex = self.elevationmap.index(assetbounds[0], assetbounds[1])
            urindex = self.elevationmap.index(assetbounds[2], assetbounds[3])
            datamatrix = self.elevationmap.read(1)[
                         min(llindex[0], urindex[0]):max(llindex[0], urindex[0])+1,
                         min(llindex[1], urindex[1]):max(llindex[1], urindex[1])+1]     # max index + 1 (inclusive)

            if 0 in datamatrix.shape:       # If the raster matrix has neither height nor width, skip
                self.notify(self.assetident+str(assetid)+" does not fall within the bounds of the raster, skipping.")
                asset.add_attribute("Elev_Avg", float(self.nodata))
                asset.add_attribute("Elev_Min", float(self.nodata))
                asset.add_attribute("Elev_Max", float(self.nodata))
                continue

            # Create the mask polygon that will be used to mask over the raster extract
            # Offset from 0,0 origin is always the first point
            maskpts = []   # Create maskpts... this is done as fully written out for loop because the UBVector has Z
            for pt in range(len(assetpts)):
                x = assetpts[pt][0]
                y = assetpts[pt][1]
                maskpts.append((float((x - maskoffsets[0]) / self.cellsize[0]),
                               float((y - maskoffsets[1]) / self.cellsize[1])))

            # Rasterize the polygon to the datamatrix shape
            maskrio = rasterio.features.rasterize([Polygon(maskpts)], out_shape=datamatrix.shape)
            maskrio = np.flip(maskrio, 0)       # Flip the shape because row/col read from top left, not bottom left
            maskeddata = np.ma.masked_array(datamatrix, mask=1-maskrio)     # Apply the mask: 1-maskrio flips booleans
            extractdata = maskeddata.compressed()   # Compress the 2D array to a 1D list
            extractdata = np.delete(extractdata, np.where(extractdata == self.nodata))  # Remove nodata values

            if len(extractdata) == 0:       # If no data leftover, assign cells as self.nodata
                asset.add_attribute("Elev_Avg", self.nodata)
                asset.add_attribute("Elev_Min", self.nodata)
                asset.add_attribute("Elev_Max", self.nodata)
            else:       # Calculate metrics and transfer elevation to asset
                asset.add_attribute("Elev_Avg", float(extractdata.mean()))
                asset.add_attribute("Elev_Min", float(extractdata.mean()))
                asset.add_attribute("Elev_Max", float(extractdata.mean()))

        self.notify_progress(80)

        # --- SECTION 3 - Perform DEM Smoothing if requested


        self.notify_progress(90)

        # --- SECTION 4 - Calculate slope and aspect


        self.notify("Mapping of elevation data to simulation grid complete")
        self.notify_progress(100)  # Must notify of 100% progress if the 'close' button is to be renabled.
        return True

    # ==========================================
    # OTHER MODULE METHODS
    # ==========================================
    def method_example(self):
        pass