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

    This is called when the program resets the interface. It sets the display state to "default"

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


def generate_leaflet_boundary_map(coordinates, mapstats, projectdata, tileserver, rootpath):
    """Generates html text for a boundary shapefile on the leaflet display and adds some basic map data to this. The
    function is called when the program needs a map of the 'boundary'. It sels the map's displaystate to 'boundary'.

    :param coordinates: latitudes and longitudes array (format: [[lat, lng], [lat, lng]])
    :param mapstats: dictionary of map stats
    :return: html code for the initial leaflet map.
    """
    centroid = mapstats["centroid"]
    leafletpath = rootpath + "/libs/leaflet/"

    popupinfo = ""
    popupinfo += "<h4>"+str(projectdata["region"])+", "+str(projectdata["city"])+"</h4><hr />"
    popupinfo += "<strong>LOCATION: </strong> Lat "+str(mapstats["centroid"][0])+", Long "+str(mapstats["centroid"][1])+"<br />"
    popupinfo += "<strong>STUDY AREA: </strong>" + str(round(mapstats["area"],2)) + " km<sup>2</sup> <br />"
    popupinfo += "<strong>EXTENTS: </strong><br /> x<sub>min/max</sub>: "+str(mapstats["xmin"]) + " | "+str(mapstats["xmax"])+"<br />"
    popupinfo += "y<sub>min/max</sub>: "+str(mapstats["ymin"]) + " | "+str(mapstats["ymax"])+"<br />"

    leaflethtml = """<!DOCTYPE html>
            <html>
            <head>
            <link rel="stylesheet" href="file:///""" + leafletpath + """leaflet.css" />
            <script src="file:///""" + leafletpath + """leaflet.js"></script>
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
            center: [""" + str(centroid[0]) + ", " + str(centroid[1]) + """],
            zoom: 12
            });""" + tileserver + """
            mapstyle.addTo(map);
            var latlngs = """+ str(coordinates) + """;
            var polygon = L.polygon(latlngs, {color: 'blue'}).addTo(map);
            var popUpContent = " """+popupinfo+""" ";
            polygon.bindPopup(popUpContent).openPopup();
            map.fitBounds(polygon.getBounds());
            </script>
            </body>
            </html>"""
    return leaflethtml

