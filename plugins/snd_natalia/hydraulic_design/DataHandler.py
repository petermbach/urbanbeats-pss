# coding=utf-8
"""
@file DataHandler
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
from plugins.snd_natalia.hydraulic_design import Manhole, Section
import os.path as path


class DataHandler(object):

    def __init__(self, path):
        """
        Constructor Method: Data Handler Class
        This method manages the input data for the Manholes (id, x, y, z) and Sections (connectivity between manholes)
        :param data
        """

        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Data Handler"

        # INPUT FILE
        self.path = path                # Path for the input data file as a String

        # DESIGN PARAMETERS
        self.manholes = []               # List of manholes
        self.sections = []               # List of sections (pipes)
        self.num_manholes = 0            # Number of manholes in the network
        self.num_sections = 0            # Number of pipes in the network

        # MANHOLES PROPERTIES
        self.id = 0   # Manhole id
        self.x = 0.0  # x coordinate of node
        self.y = 0.0  # y coordinate of node
        self.z = 0.0  # z coordinate of node

        # NODES PROPERTIES
        self.nodeID = 0  # unique (design)node identification number starting in 0
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def read_file(self):
        """ Read input file and create the sections and manholes of the network.
        :exception  "The path does not exist or could not be opened"
        """
        f = None
        try:
            path.exists(self.path)               # Check if the path exists
            f = open(self.path, "r") 	            # Get input file
        except KeyError:
            print ("The path does not exist or could not be opened")

        if f is None:
            print("File is None")
        else:
            line = f.readline()                         # read first line

            # MANHOLES
            num_manholes = 0
            if line:
                line_strings = line.split(" ")          # split lines in a line_strings list
                num_manholes = int(line_strings[1])     # Read the number of manholes in the network

            for i in range(num_manholes):               # Read the input data for all the manholes (id, x, y, z)
                line = f.readline()                     # read next line
                if line is None:
                    continue
                line_strings = line.split(" ")
                m_id = int(line_strings[0]) - 1         # Get id if manhole ID starts in 1
                # m_id = int(line_strings[0])           # Get id if manhole ID starts in 0

                # Get coordinates
                x = float(line_strings[1])
                y = float(line_strings[2])
                z = float(line_strings[3])

                # Create new manhole
                m = Manhole.Manhole(m_id, x, y, z)
                self.manholes.append(m)
                # print(m.get_id())

            # SECTIONS
            line = f.readline()                         # read next line
            num_sections = 0
            if line:
                line_strings = line.split(" ")
                num_sections = int(line_strings[1])      # Read the number of sections in the network

            id_section = 0
            # Read the input data for all the sections (id_up, id_down, type, Qd)
            for i in range(num_sections):

                line = f.readline()  # read next line

                if line is None:
                    continue
                line_strings = line.split(" ")
                # Get id if manhole ID starts in 0
                # id_up = int(line_strings[0])
                # id_down = int(line_strings[1])
                # Get id if manhole ID starts in 1
                # if id_up == 1:
                id_up = int(line_strings[0]) - 1
                id_down = int(line_strings[1]) - 1
                #
                # else:
                # System.out.println("The manholes id should start in 0 or 1")

                # Categorical variable 'I' for initial(external) pipes
                # and 'C' for non initial (internal) pipes
                p_type = line_strings[2]

                # Save the design flow rate for each section (pipe)
                qd = float(line_strings[3])

                # Create new pipe section
                new_section = Section.Section(id_section, id_up, id_down, p_type, qd)

                self.sections.append(new_section)
                self.manholes[id_up].sections_out.append(new_section)
                id_section += 1

                # print(new_section.get_upstream_manhole(), new_section.get_downstream_manhole())
