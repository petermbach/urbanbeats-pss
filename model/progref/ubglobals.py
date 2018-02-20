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

# --- LANGUAGE ---
LANGUAGECOMBO = ["DE", "EN", "ES", "FR", "PO", "CN", "JP"]

# --- DATA LIBRARY ---
DATACATEGORIES = ["Spatial Data", "Time Series Data", "Qualitative Data"]
SPATIALDATA = ["Boundaries", "Built Infrastructure", "Elevation", "Employment", "Land Use",
               "Locality Maps", "Overlays", "Population", "Soil", "Water Bodies"]
SUBDATASETS = {"Boundaries": ["Geopolitical", "Suburban", "Catchment"],
               "Population": ["Count", "Density"],
               "Soil": ["Classification", "Infiltration Rate"],
               "Employment": ["Count", "Density"],
               "Overlays": ["Planning", "Groundwater", "Environmental", "Heritage", "Regulatory"],
               "Water Bodies": ["Rivers", "Lakes"],
               "Built Infrastructure": ["Rail Network", "Road Network", "Water Network", "WSUD"]
               }
TEMPORALDATA = ["Rainfall", "Evapotranspiration", "Solar Radiation", "Temperature"]

# SHAPEFILEEXT
# If we are dealing with a shapefile, need to copy all possible files across, file formats
# available at: https://www.loc.gov/preservation/digital/formats/fdd/fdd000280.shtml
SHAPEFILEEXT = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain",
                                ".aih", ".ixs", ".mxs", ".atx", ".shp.xml", ".cpg", ".qix"]

# --- LOCATION & MAPS ---
COORDINATESYSTEMS = ["GDA", "UTM", "Other"]

CITIES = ["Adelaide", "Brisbane", "Innsbruck", "Melbourne", "Nanjing", "Perth",
                  "SanFrancisco", "Sydney", "Zurich", "Other"]
MAPSTYLES = ["CARTO", "ESRI", "OSM", "TONER", "TERRAIN"]

COORDINATES = {"Adelaide": [-34.9285, 138.6007],
                "Brisbane": [-27.4698, 153.0251],
                "Innsbruck": [47.2692, 11.4041],
                "Melbourne": [-37.8136, 144.9631],
                "Nanjing": [32.0603, 118.7969],
                "Perth": [-31.9505, 115.8605],
                "SanFrancisco": [37.7749, 122.4194],
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
