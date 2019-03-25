r"""
@file Section
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


class Section(object):
    def __init__(self, id_section, new_manhole_up, new_manhole_down, n_type, n_qd):
        """
        Constructor method
        Section Class
        :param new_manhole_up
        :param new_manhole_down
        :param n_type
        :param n_qd
        """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Section"

        self.id_section = id_section                 # Id of the Section
        self.upstream_manhole = new_manhole_up       # Id of the upstream manhole
        self.downstream_manhole = new_manhole_down   # Id of the downstream manhole
        self.section_type = n_type                   # Type of the section (pipe): 'I' external and 'C' Internal pipes
        self.section_flow_rate = n_qd                # Flow rate in the section
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def __str__(self):
        """ Print section characteristics """
        return "Section: " + self.upstream_manhole + "->" + self.downstream_manhole + " Type: " + self.section_type
