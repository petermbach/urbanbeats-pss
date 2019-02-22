# -*- coding: utf-8 -*-
"""
@file   main.pyw
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
NOCHARS = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]    # Illegal characters for filenames

# --- LANGUAGE ---
LANGUAGECOMBO = ["DE", "EN", "ES", "FR", "PO", "CN", "JP"]      # Abbreviations for foreign languages used

# --- DATA LIBRARY ---
DATACATEGORIES = ["Spatial Data", "Time Series Data", "Qualitative Data"]       # Naming convention for data categories

SPATIALDATA = ["Boundaries", "Built Infrastructure", "Elevation", "Employment", "Land Use",
               "Locality Maps", "Overlays", "Population", "Soil", "Water Bodies"]   # Naming conventions for Spatial

SUBDATASETS = {"Boundaries": ["Geopolitical", "Suburban", "Catchment"],
               "Population": ["Count", "Density"],
               "Soil": ["Classification", "Infiltration Rate"],
               "Employment": ["Count", "Density"],
               "Overlays": ["Planning", "Groundwater", "Environmental", "Heritage", "Regulatory"],
               "Water Bodies": ["Rivers", "Lakes"],
               "Built Infrastructure": ["Rail Network", "Road Network", "Water Network", "WSUD"]
               }    # Naming convention for sub-categories of spatial data

TEMPORALDATA = ["Rainfall", "Evapotranspiration", "Solar Radiation", "Temperature"] # Naming convention

# SHAPEFILEEXT
# If we are dealing with a shapefile, need to copy all possible files across, file formats
# available at: https://www.loc.gov/preservation/digital/formats/fdd/fdd000280.shtml
SHAPEFILEEXT = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain",
                                ".aih", ".ixs", ".mxs", ".atx", ".shp.xml", ".cpg", ".qix"]

# --- LOCATION & MAPS ---
COORDINATESYSTEMS = ["GDA", "UTM", "Other"]     # Short-form abbreviation for key coordinate system types

CITIES = ["Adelaide", "Brisbane", "Innsbruck", "Melbourne", "Nanjing", "Perth",
                  "SanFrancisco", "Sydney", "Zurich", "Other"]      # Spelling and naming for cities
MAPSTYLES = ["CARTO", "ESRI", "OSM", "TONER", "TERRAIN"]

COORDINATES = {"Adelaide": [-34.9285, 138.6007],
                "Brisbane": [-27.4698, 153.0251],
                "Innsbruck": [47.2692, 11.4041],
                "Melbourne": [-37.8136, 144.9631],
                "Nanjing": [32.0603, 118.7969],
                "Perth": [-31.9505, 115.8605],
                "SanFrancisco": [37.7749, -122.4194],
                "Sydney": [-33.8688, 151.2093],
                "Zurich": [47.3769, 8.5417]
               }

TILESERVERS = {
    "CARTO": """var mapstyle= L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
subdomains: 'abcd',
maxZoom: 19
});""",
    "ESRI": """var mapstyle= L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});""",
    "OSM": """var mapstyle= L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
maxZoom: 19, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});""",
    "TONER": """var mapstyle= L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.{ext}', {
attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
subdomains: 'abcd',
minZoom: 0,
maxZoom: 20,
ext: 'png'
});""",
    "TERRAIN": """var mapstyle= L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.{ext}', {
attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
subdomains: 'abcd',
minZoom: 0,
maxZoom: 18,
ext: 'png'
});"""
    }

# --- MODEL SETTING ---
DECISIONS = ["best", "random", "none"]
MODULENAMES = ["SPATIAL", "CLIMATE", "URBDEV", "URBPLAN", "SOCIO", "MAP", "REG", "INFRA", "PERF", "IMPACT", "DECISION"]

# NATURAL ELEMENTS
SOILDICTIONARY = [180, 36, 3.6, 0.36] #mm/hr - 1=sand, 2=sandy clay, 3=medium clay, 4=heavy clay
LANDCOVERMATERIALS = ["AS", "CO", "DG"]  # AS = asphalt, CO = concrete, DG = bare dirt ground
TREETYPES = ["RB", "RN", "TB", "TN", "OB", "ON"]
        # Explanation of tree types: R = round, T = tall, O = open, B = broad leaves, N = needle leaves

# LAND USE AND PLANNING ELEMENTS
LANDUSEABBR = ['RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA', 'WAT', 'FOR', 'AGR']
LANDUSENAMES = ['Residential', 'Commercial', 'Offices Res Mix', 'Light Industry', 'Heavy Industry',
                'Civic', 'Service and Utility', 'Road', 'Transport', 'Parks and Gardens', 'Reserves and Floodway',
                'Undeveloped', 'Unclassified', 'Water', 'Forest', 'Agriculture']

PLANTYPES = ["Suburbia", "European", "Megacity"]
PLANPARAMSET = ["Custom", "Melbourne"]
UNDEVSTATES = ['GF', 'BF', 'AG']

# WATER-RELATED ELEMENTS
RESSTANDARDS = ["AS6400", "Others..."]
FFP = ["PO", "NP", "RW", "SW", "GW"]    # Fit for purpose water qualities
DPS = ["SDD", "CDP", "OHT", "AHC", "USER"]    # Types of diurnal patterns
# Diurnal Patterns
# SDD = STANDARD DAILY DIURNAL PATTERN SCALING FACTORS
SDD = [0.3, 0.3, 0.3, 0.3, 0.5, 1.0, 1.5, 1.5, 1.3, 1.0, 1.0, 1.5, 1.5, 1.2, 1.0, 1.0, 1.0, 1.3, 1.3, 0.8,
       0.8, 0.5, 0.5, 0.5]

# CDP = CONSATNT DAILY DIURNAL PATTERN SCALING FACTORS
CDP = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
       1.0, 1.0, 1.0, 1.0]

# OHT = OFFICE HOURS TRAPEZOIDAL DIURNAL PATTERN SCALING FACTORS
OHT = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.0, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5,
       0.0, 0.0, 0.0, 0.0]

# AHC = AFTER HOURS CONSTANT DIURNAL PATTERN
AHC = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
       2.0, 2.0, 2.0, 2.0]

DIURNAL_CATS = ["res_kitchen", "res_shower", "res_toilet", "res_laundry", "res_dishwasher", "res_outdoor",
                "res_dailyindoor", "com", "ind", "nonres_landscape", "pos_irrigation"]

DIURNAL_LABELS = ["Kitchen", "Shower", "Toilet", "Laundry", "Dishwasher", "Garden",
                  "Residential Indoor", "Commercial and Offices", "Industries", "Non-residential Outdoor",
                  "Public Irrigation"]

# --- ASSET IDENTIFIERS ---
ASSET_IDENTIFIERS = {"Block": "The most basic building block of the city in UrbanBEATS, the square cell containing all"
                              "relevant geodata",
                     "Patch": "An area of uniform land use at the sub-grid level delineated using the Block grid as"
                              "a baseline, represented either by its centroid or as a full polygon.",
                     "BlockCentre": "Centroid of a Block, simply for reference and distance calculations",
                     "Flow": "The link between two Blocks representing the water flow directions.",
                     "FlowP": "The link between two Patches representing the water flow directions.",
                     "OSLink": "The link between open space and other land uses representing distance between",
                     "OSNet": "The link between open space land uses representing interconnectivity of spaces",
                     "UrbanCell": "The cell at 50m or 100m resolution on which the urban modelling and cellular "
                                  "automata is conducted is run. UrbanCells are aggregated to Blocks later on.",
                     "Basin": "The collection of Blocks or Patches that make up the urban catchment.",
                     "Locality": "Location of a civic, transport, landmark or other urban facility of interest in"
                                 "the modelling.",
                     "MapAttributes": "Global attributes of the simulation map that all modules are working on."
                     }
