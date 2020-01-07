# r"""
# @file Global
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
# from math import pow
# from matplotlib.patches import FancyArrowPatch
# from mpl_toolkits.mplot3d import proj3d
#
# """
# GLOBAL VARIABLES
# """
# # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
#
# # PIPES INTERNAL ROUGHNESS
# #   Absolute roughness ks    -> pvc: 0.0000015, concrete: 0.0003
# #   Manning's n coefficient  -> pvc: , concrete:
# roughness = 0.0000015
#
# # KINEMATIC VISCOSITY OF WATER
# nu = round(1.14 / pow(10, 6), 8)
#
# # ELEVATION CHANGE
# # Depth delta between possible invert elevations of the pipes (100 cm or 10 dm in one meter)
# # A smaller elevation change implies a more precise design but increases the computational time.
# elevation_change = 10
#
# # EXCAVATION LIMITS
# min_depth = 1.2         # Minimum excavation depth
# max_depth = 5           # Maximum excavation depth
#
# # LIST OF COMMERCIAL PIPE DIAMETERS
# # commercial_diameters = (0.2, 0.35, 0.45, 0.6, 0.8, 1.2, 1.55, 1.8)  # TUNJA 1
# # commercial_diameters = (0.2, 0.35, 0.45, 0.6, 0.8, 1.2, 1.55, 1.8)  # TUNJA 2
# # commercial_diameters =  (0.2, 0.25, 0.3, 0.35, 0.38, 0.4,0.45, 0.5, 0.53, 0.6, 0.7, 0.80,
# #  0.9, 1, 1.05, 1.20, 1.35, 1.4, 1.5 ,1.6,1.8, 2, 2.2, 2.4) #TUNJA 3 y 4
# # TUNJA 5 y 6
# commercial_diameters = (0.2, 0.38, 0.4, 0.5, 0.65, 0.80, 0.9, 1.05, 1.20, 1.3, 1.55, 1.6, 1.8, 2.2)
#
# # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------
#
#
# class Arrow3D(FancyArrowPatch):
#     def __init__(self, xs, ys, zs, *args, **kwargs):
#         FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
#         self._verts3d = xs, ys, zs
#
#     def draw(self, renderer):
#         xs3d, ys3d, zs3d = self._verts3d
#         xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
#         self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
#         FancyArrowPatch.draw(self, renderer)
