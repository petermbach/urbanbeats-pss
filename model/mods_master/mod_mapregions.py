r"""
@file   mod_mapregions.py
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
from shapely.geometry import Polygon

from model.ubmodule import *
import model.ublibs.ubspatial as ubspatial
import model.ublibs.ubdatatypes as ubdata

class MapRegionsToSimGrid(UBModule):
    """ Imports and maps a land use map onto the simulation grid. Allows reclassification of the input land use to the
    UrbanBEATS classification system."""

    # MODULE'S BASIC METADATA
    type = "master"
    catname = "Spatial Representation"
    catorder = 2
    longname = "Map Regions"
    icon = ":/icons/admin_border.png"

    def __init__(self, activesim, datalibrary, projectlog):
        UBModule.__init__(self)
        self.activesim = activesim
        self.scenario = None
        self.datalibrary = datalibrary
        self.projectlog = projectlog

        # KEY GUIDING VARIABLES
        self.assets = None
        self.meta = None
        self.xllcorner = None
        self.yllcorner = None
        self.assetident = ""
        self.nodata = None

        # MODULE PARAMETERS
        self.create_parameter("assetcolname", STRING, "Name of the asset collection to use")
        self.assetcolname = "(select asset collection)"

        self.create_parameter("boundaries_to_map", LIST, "Collection of boundaries to map.")
        self.boundaries_to_map = []

    def add_boundary_to_map(self, label, dset, attname, stakeholder):
        """Adds details for a simulation boundary to map to the simulation grid. Creates a dictionary object based on
        the key few tables: category (classifier of the boundary), dset (the data set ID from the datalibrary),
        attname (the attribute name from which to obtain the names) and label (the unique label used to distinguish)."""
        self.boundaries_to_map.append({"label": label, "datafile": dset,
                                       "attname": attname, "stakeholder": stakeholder})
        return True

    def reset_boundaries_to_map(self):
        self.boundaries_to_map = []

    def set_module_data_library(self, datalib):
        self.datalibrary = datalib

    def initialize_runstate(self):
        """Initializes the key global variables so that the program knows what the current asset collection is to write
        to and what the active simulation boundary is. This is done the first thing the model starts."""
        self.assets = self.activesim.get_asset_collection_by_name(self.assetcolname)
        if self.assets is None:
            self.notify("Fatal Error Missing Asset Collection")

        # Metadata Check - need to make sure we have access to the metadata
        self.meta = self.assets.get_asset_with_name("meta")
        if self.meta is None:
            self.notify("Fatal Error! Asset Collection missing Metadata")
        self.meta.add_attribute("mod_mapregions", 1)
        self.assetident = self.meta.get_attribute("AssetIdent")

        self.xllcorner = self.meta.get_attribute("xllcorner")
        self.yllcorner = self.meta.get_attribute("yllcorner")

        add_stakeholder_data_type = 0
        for d in self.boundaries_to_map:
            if d["stakeholder"]:
                self.assets.add_asset_type("Stakeholder", "Social")
                break       # If at least one boundary to map will also be mapped for stakeholders, add this data type

    def run_module(self):
        """ The main algorithm for the module, links with the active simulation, its data library and output folders."""
        self.initialize_runstate()

        self.notify("Mapping Regions to the Simulation Grid")
        self.notify("--- === ---")
        self.notify("Geometry Type: " + self.assetident)
        self.notify_progress(0)

        boundary_datarefs = self.datalibrary.get_dataref_array("spatial", ["Boundaries"])

        # LOOP ACROSS DICTIONARIES, LOAD THE SHAPEFILE AND MAP TO THE SIMULATION GRID
        griditems = self.assets.get_assets_with_identifier(self.assetident)

        # METADATA
        self.notify("Total assets to map data to: "+str(len(griditems)))
        self.notify_progress(10)    # 20 to 100% progress spaced out depending on number of boundaries...
        current_progress = 10
        progress_increment = 80.0 / float(len(self.boundaries_to_map))

        stakeholders = self.assets.get_assets_with_identifier("Stakeholder")
        stakeholderIDcount = len(stakeholders)+1      # Start the stakeholder ID count

        for i in range(len(self.boundaries_to_map)):
            stakeholderlist = []
            boundary = self.boundaries_to_map[i]
            self.notify("Mapping current boundary: "+str(boundary["label"]))

            dataidindex = boundary_datarefs[0].index(boundary['datafile'])       # Get the Data Library ID
            dataid = boundary_datarefs[1][dataidindex]
            dataref = self.datalibrary.get_data_with_id(dataid)             # Get the Data reference
            fullpath = dataref.get_data_file_path() + dataref.get_metadata("filename")

            boundaryfeats = ubspatial.import_polygonal_map(fullpath, "native", "Boundary",
                                                           (self.xllcorner, self.yllcorner))

            self.notify("Total features in "+str(boundary["datafile"])+": "+str(len(boundaryfeats)))

            for a in range(len(griditems)):
                if griditems[a].get_attribute("Status") == 0:
                    continue

                cur_asset = griditems[a]
                assetpts = cur_asset.get_points()
                assetpoly = Polygon([c[:2] for c in assetpts])

                intersectarea = 0
                intersectname = ""
                for b in boundaryfeats:
                    feat = Polygon(b.get_points())
                    if not feat.intersects(assetpoly):
                        continue
                    newisectarea = feat.intersection(assetpoly).area
                    if newisectarea > intersectarea:
                        intersectarea = newisectarea
                        intersectname = str(b.get_attribute(boundary["attname"]))

                if intersectname != "" and intersectarea > 0:
                    cur_asset.add_attribute(boundary["label"], intersectname)
                    if intersectname not in stakeholderlist:
                        stakeholderlist.append(intersectname)
                else:
                    cur_asset.add_attribute(boundary["label"], "Unassigned")

            # Create Stakeholders if yes - generate the UBStakeholder() objects and save to asset collection
            if boundary["stakeholder"]:
                if boundary["label"][:2] == "J_":       # Figure out stakeholder type
                    stype = "Jurisdictional"
                elif boundary["label"][:2] == "S_":
                    stype = "Suburban"
                else:
                    stype = "Other"

                for b in boundaryfeats:
                    if b.get_attribute(boundary["attname"]) in stakeholderlist:
                        sh_object = ubdata.UBStakeholder(b.get_attribute(boundary["attname"]),
                                                         type=stype, location=Polygon(b.get_points()))
                        stakeholderlist.pop(stakeholderlist.index(b.get_attribute(boundary["attname"])))
                    self.assets.add_asset("StakeholderID"+str(stakeholderIDcount), sh_object)
                    stakeholderIDcount += 1

            # Close the loop with PROGRESS UPDATE
            self.notify("Completed Mapping: " + str(boundary["label"]))
            current_progress += progress_increment
            self.notify_progress(int(current_progress))

        self.notify("Mapping of regions to simulation grid complete")
        self.notify_progress(100)
        return True