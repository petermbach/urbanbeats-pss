r"""
@file   mapping_leaflet.pyw
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

import osgeo.osr as osr
import osgeo.ogr as ogr
import numpy as np


def generate_initial_leaflet_map(coordinates, tileserver, rootpath):
    """Generates html text for the initial leaflet map to be displayed on the main interface.
        At the time of development, the online paths were: https://unpkg.com/leaflet@1.3.1/dist/leaflet.css"
   integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==
    and
        https://unpkg.com/leaflet@1.3.1/dist/leaflet.js"
   integrity="sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw=="
   crossorigin=""

    This is called when the program resets the interface. It sets the display state to "default". Function updates
    the default.html file in the program's temporary directory so that it can be loaded.

    :param coordinates: list of two elements representing latitude and longitude, to be used as centre point of map
    :param resolution: the pixel resolution of the map, list of two elements W x H
    :return: html code for the initial leaflet map.
    """

    leafletpath = "file:///"+ rootpath + "/libs/leaflet/"
    # leafletpath = "https://unpkg.com/leaflet@1.6.0/dist/"
    leaflethtml = f"""<!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" href=\""""+leafletpath+"""leaflet.css" />
        <script src=\""""+leafletpath+"""leaflet.js"></script>
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
    # print(leaflethtml)
    return leaflethtml


def generate_leaflet_boundaries(filename, boundarydata, activeboundaryname, projectdata, centroid, epsg, tilemapserver,
                                rootpath):
    """Generates html text for the boundaries within boundarydata and colours the activeboundary name differently"""
    leafletpath = rootpath + "/libs/leaflet/"

    # Project data
    centroid_pt = ogr.Geometry(ogr.wkbPoint)
    centroid_pt.AddPoint(centroid[0], centroid[1])
    coordtrans = create_coord_transformation_leaflet(int(epsg))
    centroid_pt.Transform(coordtrans)
    centroidXY = (centroid_pt.GetX(), centroid_pt.GetY())       # REMEMBER: reverse X and Y in leaflet plotting
    print("Saving Leaflet file")
    # Start writing the HTML file
    f = open(filename, 'w')
    # f = open("C:/Users/peter/Documents/boundarytest.html", 'w')   #Debug Line
    f.write(f"""<!DOCTYPE html>
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
            center: [""" + str(centroidXY[0]) + ", " + str(centroidXY[1]) + """],
            zoom: 12
            });""" + tilemapserver + """
            mapstyle.addTo(map);"""+"\n")

    # Time to generate boundaries
    polyIDs = 0
    polygonVarnames = []
    for i in boundarydata.keys():
        curname = i
        popuptext = generate_boundary_popupinfo(curname, boundarydata[curname], projectdata)
        leaflet_coordinates = convert_polygon_to_leaflet_projection(boundarydata[curname]["coordinates"],
                                                                    boundarydata[curname]["inputEPSG"])
        if curname == activeboundaryname:
            color = 'red'
        else:
            color = 'blue'
        polyname, leafletpolygontext = generate_leaflet_polygon_text(polyIDs, leaflet_coordinates, popuptext, color)
        polygonVarnames.append(polyname)
        polyIDs += 1
        f.write(leafletpolygontext+"\n")

    #             map.fitBounds(polygon.getBounds());
    #

    f.write(f"""</script>
            </body>
            </html>""")
    f.close()

def generate_leaflet_polygon_text(poly_id, coordinates, popupinfo, color):
    """Generates a leaflet polygon and returns the HTML text and polygon name"""
    polygon_name = "polygon"+str(poly_id)

    # START OF JS WRAPPER
    leaflettext = "var latlngs"+str(poly_id)+" = "+str(coordinates)+";\n"
    leaflettext += "var "+str(polygon_name)+" = L.polygon(latlngs"+str(poly_id)+", {color: '"+str(color)+"'}).addTo(map);\n"
    leaflettext += 'var popupContent'+str(poly_id)+'="'+popupinfo+'";\n'
    leaflettext += polygon_name+".bindPopup(popupContent"+str(poly_id)+");\n"
    return polygon_name, leaflettext

def generate_boundary_popupinfo(name, boundarydata, projectdata):
    """Generates all the information to be placed into a popup window and writes this as leaflet code for the script."""
    popupinfo = "<h4>"+str(name)+"</h4>"
    popupinfo +="<h5>" + str(projectdata["region"]) + ", " + str(projectdata["city"]) + "</h5><hr />"
    popupinfo +="<strong>PROJECTION: </strong>"+str(boundarydata["coordsysname"])+"<br />"
    popupinfo +="<strong>LOCATION: </strong> X = "+str(boundarydata["centroid"][0])+\
                "| Y = "+str(boundarydata["centroid"][1])+"<br />"
    popupinfo +="<strong> STUDY AREA: </strong>" + str(round(boundarydata["area"], 2))+ " km<sup>2</sup> <br />"
    popupinfo +="<strong> EXTENTS: </strong><br />"
    popupinfo +="     x<sub>min/max</sub> (left/right): "+\
                str(boundarydata["xmin"])+" | "+str(boundarydata["xmax"])+"<br />"
    popupinfo +="     y<sub>min/max</sub> (bottom/top): "\
                +str(boundarydata["ymin"])+" | "+str(boundarydata["ymax"])+"<br />"
    return popupinfo

def create_coord_transformation_leaflet(inputEPSG):
    """Creates the coordinate transformation variable for the leaflet map, uses OSR library. The leaflet
    EPSG code is 4326, which is WGS84, geographic coordinate system.

    :param inputEPSG: the input EPSG code, format int(), specifying the EPSG of the input map. Can use get_epsg()
    :return: osr.CoordinateTransformation() object
    """
    inSpatial = osr.SpatialReference()
    inSpatial.ImportFromEPSG(inputEPSG)

    outSpatial = osr.SpatialReference()
    outSpatial.ImportFromEPSG(4326)

    coordTrans = osr.CoordinateTransformation(inSpatial, outSpatial)
    return coordTrans


def convert_polygon_to_leaflet_projection(coordinates, inputEPSG):
    """Converts an input list of coordinates based on the given shape to leaflet coordinates using the inputEPSG and
    leaflet's EPSG: 4326"""
    if inputEPSG == 4326:       # If the projection is already the same, return the same coordinates
        return [[coordinates[pt][0], coordinates[pt][1]] for pt in coordinates]

    coordtrans = create_coord_transformation_leaflet(inputEPSG)

    # Make the polygon object
    poly = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for pt in coordinates:
        ring.AddPoint(pt[0], pt[1])
    poly.AddGeometry(ring)

    # Project and return the polygon coordinates
    coordinates_pj = []
    poly.Transform(coordtrans)
    ring = poly.GetGeometryRef(0)
    for pt in range(ring.GetPointCount()):
        coordinates_pj.append([ring.GetPoint(pt)[0], ring.GetPoint(pt)[1]])
    return coordinates_pj


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

