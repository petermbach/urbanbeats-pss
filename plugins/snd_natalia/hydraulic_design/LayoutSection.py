# coding=utf-8
"""
@file LayoutSection
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


class LayoutSection(object):

    def __init__(self, ls_node_up, ls_node__down, parent_sec, n_type, n_qd):
        """
        Construction Method: Layout Section Class
        :param ls_node_up
        :param ls_node__down
        :param parent_sec
        :param n_type
        :param n_qd
        """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Layout_Section"

        self.lsNode_Up = ls_node_up                 # Upstream layout node
        self.lsNode_Down = ls_node__down       # Downstream layout node
        self.lsNode_type = n_type                   # Pipe type (External or Internal)
        self.lsSection_FlowRate = n_qd              # Design flow rate for the hydraulic design
        self.parent_section = parent_sec            # Parental section (pipe)
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def __str__(self):
        """  Print Layout section properties """
        # return "Layout Section: " + str(self.lsNode_Up.id) + " -> " + str(self.lsNode_Down.id) + \
        #        " Type: " + str(self.lsNode_type)
        return "(" + str(self.lsNode_Up.id) + ", " + str(self.lsNode_Down.id) + ", " + str(self.lsNode_type) + ")"
