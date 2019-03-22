# coding=utf-8
r"""
@file DesignNode
@author Natalia Duque
@section LICENSE

Sewer Networks Design (SND)
Copyright (C) 2016  CIACUA, Universidad de los Andes, Bogotá, Colombia

This program is a free software: you can redistribute it and/or modify
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
from numpy import round, infty


class DesignNode(object):

    def __init__(self, node_id, ls_node, diameter, elevation, arcs_in):
        """
        Constructor Method: Design Node
        :param node_id 			node general id
        :param ls_node     	    manhole id
        :param diameter   	    diameter of design node
        :param elevation 	    elevation of the design node
        :param arcs_in 		    list of arcs coming into the design node
        """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "DesignNode"

        self.id = node_id                   # Design Node id
        self.ls_node = ls_node              # Layout node: Manhole holding the design node
        self.x = ls_node.my_manhole.coordinate_x
        self.y = ls_node.my_manhole.coordinate_y

        self.diameter = diameter            # Diameter
        self.z = round(elevation, decimals=4, out=None)       # Elevation
        self.yNormal = 0.0                  # Normal depth

        # CONNECTIVITY
        self.dArcs_in = arcs_in             # design arcs coming in
        self.dArcs_out = 0                  # design arcs going out

        # BELLMAN-FORD PARAMETERS
        self.Vi = infty                     # Cumulative cost starts in positive infinity
        self.Pj = None                      # Predecessor node for the shortest path
        if arcs_in == -1:                   # Cumulative cost for the outfall is 0
            self.Vi = 0
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------



    def __str__(self):
        """ Print Design Node properties """
        return "DN: " + self.id + "= (" + self.diameter + " , " + self.z + ") " + self.dArcs_in
