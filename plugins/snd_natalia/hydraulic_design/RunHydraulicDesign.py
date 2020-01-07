# r"""
# @file RunHydraulicDesign
# @author Natalia Duque
# @section LICENSE
#
# Sewer Networks Design (SND)
# Copyright (C) 2016  CIACUA, Universidad de los Andes, Bogotá, Colombia
#
# This program is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# """
# from plugins.snd_natalia.hydraulic_design.DataHandler import DataHandler
# from plugins.snd_natalia.hydraulic_design.LayoutGraphbuilder import LayoutGraphbuilder
# from plugins.snd_natalia.hydraulic_design.DesignGraphBuilder import DesignGraphBuilder
# import os
#
# class RunHydraulicDesign(object):
#
#     def __init__(self):
#         self.name = " Run hydraulic design"
#
#     @staticmethod
#     def run():
#
#         # File with the solution of the Layout Selection problem
#         file = "..\Files\Results.txt"
#         p = os.path.abspath(file)
#
#
#         # Read the file and create manholes and sections
#         d = DataHandler(p)
#         d.read_file()
#
#         # Generate layout graph
#         lg = LayoutGraphbuilder(d)
#         print(lg.name)
#         lg.build()
#
#         # Generate and solve the hydraulic design graph
#         gb = DesignGraphBuilder(d)
#         print(gb.name)
#         gb.build_and_solve()
#
#
# RunHydraulicDesign.run()
