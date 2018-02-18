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

def generate_initial_leaflet_map(coordinates, tileserver, rootpath):
    """Generates html text for the initial leafelet map to be displayed on the main interface.
        At the time of development, the online paths were: https://unpkg.com/leaflet@1.3.1/dist/leaflet.css"
   integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==
    and
        https://unpkg.com/leaflet@1.3.1/dist/leaflet.js"
   integrity="sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw=="
   crossorigin=""

    :param coordinates: list of two elements representing latitude and longitude, to be used as centre point of map
    :param resolution: the pixel resolution of the map, list of two elements W x H
    :return: html code for the initial leaflet map.
    """

    leafletpath = rootpath + "/libs/leaflet/"
    leaflethtml = """<!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" href="file:///"""+leafletpath+"""leaflet.css" />
        <script src="file:///"""+leafletpath+"""leaflet.js"></script>
        <style>
        html, body, #map {
        height: 100%;
        width: 100%;
        }
        body {
        padding: 0;
        margin: 0;
        }
        </style>
        </head>
        <body>
        <div id="map"></div>
        <script type="text/javascript">
        var map = L.map('map', {
        center: ["""+str(coordinates[0])+", "+str(coordinates[1])+"""],
        zoom: 12
        });"""+tileserver+"""
        mapstyle.addTo(map);
        </script>
        </body>
        </html>"""
    return leaflethtml


