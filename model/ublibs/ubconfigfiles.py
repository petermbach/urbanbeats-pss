"""
@file   ubconfigfiles.py
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
"""

__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2019. Peter M. Bach"

import xml.etree.ElementTree as ET

OPTIONSGENERAL = {
    "defaultmodeller": "name",
    "defaultaffil": "affiliation",
    "projectlogstyle": "comprehensive",
    "language": "EN",
    "city": "Melbourne",
    "coordinates": "lattitude longitude [decimal degrees]",
    "defaultpath": "none",
    "tempdir": "none",
    "tempdefault": "1",
    "bodytextcolor": "000000",
    "consoledatestampcolor": "93cbc7",
    "errortextcolor": "000000" }

OPTIONSSIMULATION = {
    "maxiterations": "1000",
    "globaltolerance": "1.00",
    "defaultdecision": "best" }

OPTIONSMAPS = {
    "mapstyle": "OSM",
    "tileserverURL": "none",
    "cachetiles": "0",
    "offline": "0",
    "defaultcoordsys": "WGS_1972_UTM_Zone_55S",
    "customepsg": "32355" }

OPTIONSEXTERNAL = {
    "epanetpath": "none",
    "swmmpath": "none",
    "musicpath": "none"}


def create_default_config_cfg(ubeatsroot):
    """Writes a default options config.cfg file into the UrbanBEATS directory, called when a reset is required or
    the file does not exist in the folder.

    :param ubeatsroot: path to the main folder that UrbanBEATS uses to scan for configurations
    """
    f = open(ubeatsroot + "/config.cfg", 'w')
    f.write('<URBANBEATSCONFIG creator="Peter M. Bach" version="1.0">\n')
    f.write('\t<options>\n')
    f.write('\t\t<general>\n')
    for k in OPTIONSGENERAL.keys():
        f.write("\t\t\t<"+k+" default=\""+str(OPTIONSGENERAL[k])+"\">"+str(OPTIONSGENERAL[k])+"</"+str(k)+">\n")
    f.write('\t\t</general>\n\n')

    f.write('\t\t<simulation>\n')
    for k in OPTIONSSIMULATION.keys():
        f.write("\t\t\t<"+str(k)+" default=\""+str(OPTIONSSIMULATION[k])+"\">"+str(OPTIONSSIMULATION[k]) +
                "</"+str(k)+">\n")
    f.write('\t\t</simulation>\n\n')

    f.write('\t\t<maps>\n')
    for k in OPTIONSMAPS.keys():
        f.write("\t\t\t<"+str(k)+" default=\""+str(OPTIONSMAPS[k])+"\">"+str(OPTIONSMAPS[k])+"</"+str(k)+">\n")
    f.write('\t\t</maps>\n\n')

    f.write('\t\t<external>\n')
    for k in OPTIONSEXTERNAL.keys():
        f.write("\t\t\t<" + str(k) + " default=\"" + str(OPTIONSEXTERNAL[k]) + "\">" + str(OPTIONSEXTERNAL[k]) +
                "</" + str(k) + ">\n")
    f.write('\t\t</external>\n\n')

    f.write('\t</options>\n')
    f.write('</URBANBEATSCONFIG>')
    f.close()

    return True


def create_default_recent_cfg(ubeatsroot):
    """Writes an empty recent.cfg file into the UrbanBEATS directory, called when a reset is required or the file
    does not exist in the folder.

    :param ubeatsroot: path to the main folder that UrbanBEATS uses to scan for recent projects
    """
    root = ET.Element("URBANBEATSRECENT", creator="Peter M. Bach", version="1.0")
    recentprojects = ET.SubElement(root, "recentprojects")
    tree = ET.ElementTree(root)
    tree.write(ubeatsroot+"/recent.cfg")
    return True