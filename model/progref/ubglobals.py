r"""
@file   ubglobals.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2012  Peter M. Bach

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
__copyright__ = "Copyright 2012. Peter M. Bach"

# --- GENERAL ---
NOCHARS = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "!"]    # Illegal characters for filenames
URBANBEATSLOGOCOLORHEX = ["#346FAC", "#CF7328", "#8EBA52"]  # BLUE, ORANGE, GREEN as on the UB Logo

# --- LANGUAGE ---
LANGUAGECOMBO = ["DE", "EN", "ES", "FR", "PO", "CN", "JP"]      # Abbreviations for foreign languages used

# --- LOCATION & MAPS ---
MAPSTYLES = ["CARTODBPOS", "CARTODARK", "ESRI", "OTM", "TONER", "TERRAIN", "WATERCOLOR"]

# --- MODEL SETTING ---
DECISIONS = ["best", "random", "none"]
MODULENAMES = ["SPATIAL", "CLIMATE", "URBDEV", "URBDYN", "URBPLAN", "MAP", "INFRA", "BGS",
               "CYCLE", "MICRO", "FLOOD", "ECON"]

# NATURAL ELEMENTS
SOILDICTIONARY = [180, 36, 3.6, 0.36] #mm/hr - 1=sand, 2=sandy clay, 3=medium clay, 4=heavy clay
SOILCLASSES = ["Sand", "Sandy Clay", "Medium Clay", "Heavy Clay"]
SOILABBREVIATIONS = ["S", "SC", "MC", "HC"]

LANDCOVERMATERIALS = ["AS", "CO", "DG"]  # AS = asphalt, CO = concrete, DG = bare dirt ground
TREETYPES = ["RB", "RN", "TB", "TN", "OB", "ON"]
        # Explanation of tree types: R = round, T = tall, O = open, B = broad leaves, N = needle leaves

# LAND USE AND PLANNING ELEMENTS
LANDUSEABBR = ['RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA', 'WAT', 'FOR', 'AGR']
LANDUSENAMES = ['Residential', 'Commercial', 'Offices Res Mix', 'Light Industry', 'Heavy Industry',
                'Civic', 'Service and Utility', 'Road', 'Transport', 'Parks and Gardens', 'Reserves and Floodway',
                'Undeveloped', 'Unclassified', 'Water', 'Forest', 'Agriculture']
ACTIVELANDUSEABBR = ['RES', 'COM', 'IND', 'ORC']
ACTIVELANDUSENAMES = ["Residential", "Commercial", "Industrial", "Mixed Development"]
UM_LUCABBRS = ['RES', 'COM', 'ORC', 'IND', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA', 'WAT', 'FOR', 'AGR']
UM_LUCNAMES = ['Residential', 'Commercial', 'Offices Res Mix', 'Industrial', 'Civic', 'Service and Utility',
               'Road', 'Transport', 'Parks and Gardens', 'Reserves and Floodway', 'Undeveloped', 'Unclassified',
               'Water', 'Forest', 'Agriculture']

PLANTYPES = ["Suburbia", "European", "Megacity"]
PLANPARAMSET = ["Custom", "Melbourne"]

VPOT = ["S", "M"]       # Forms of the land use potential equation S = standard, M = modified

COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]      # Compass directions, also neighbourhoods


VALUE_SCALE_METHODS = ["L", "Q", "C", "IQ", "IC", "S", "M"]

PATCHFLOWMETHODS = ["MIN", "DIST", "MAX"]   # Patch flow path delineation methods

WSUD_NAMES = ["BIOF", "WSUR", "EVAP", "INFS", "POND", "SWAL", "ROOF", "WALL", "PAVE", "TANK", "BASN", "FILT",
              "DISC", "BANK"]       # Abbreviations for all BGS systems

# --- ASSET IDENTIFIERS ---
ASSET_IDENTIFIERS = {"Block": "The most basic building block of the city in UrbanBEATS, the square cell containing all"
                              "relevant geodata",
                     "Patch": "An area of uniform land use at the sub-grid level delineated using the Block grid as"
                              "a baseline, represented either by its centroid or as a full polygon.",
                     "BlockCentre": "Centroid of a Block, simply for reference and distance calculations",
                     "Flow": "The link between two Blocks representing the water flow directions.",
                     "FlowP": "The link between two Patches representing the water flow directions.",
                     "OSLink": "The link between open space and other land uses representing the distance between them",
                     "OSNet": "The link between open space land uses representing interconnectivity of spaces",
                     "UrbanCell": "The cell at 50m or 100m resolution on which the urban modelling and cellular "
                                  "automata is conducted is run. UrbanCells are aggregated to Blocks later on.",
                     "Basin": "The collection of Blocks or Patches that make up the urban catchment.",
                     "Locality": "Location of a civic, transport, landmark or other urban facility of interest in"
                                 "the modelling.",
                     "MapAttributes": "Global attributes of the simulation map that all modules are working on."
                     }

TILESERVERS = {
    "CARTODBPOS": """var mapstyle = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
subdomains: 'abcd',
maxZoom: 19
});""",
    "CARTODARK": """var mapstyle = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
subdomains: 'abcd',
maxZoom: 19
});""",
    "ESRI": """var mapstyle= L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});""",
    "OTM": """var mapstyle = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
maxZoom: 17, attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});""",
    "TONER": """var mapstyle= L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.{ext}', {
attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
subdomains: 'abcd', minZoom: 0, maxZoom: 20, ext: 'png'
});""",
    "TERRAIN": """var mapstyle= L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.{ext}', {
attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
subdomains: 'abcd', minZoom: 0, maxZoom: 18,ext: 'png'
});""",
    "WATERCOLOR": """var mapstyle = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}', {
attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
subdomains: 'abcd', minZoom: 1, maxZoom: 16, ext: 'jpg'
});"""
    }