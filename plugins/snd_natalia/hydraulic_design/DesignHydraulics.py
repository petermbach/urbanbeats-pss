# r"""
# @file DesignHydraulics
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
# # import HydraulicDesign as hd
# import numpy as np
# from plugins.snd_natalia.utilities.Rounder import rounder
# from plugins.snd_natalia.utilities.Global import roughness, nu
#
#
# class DesignHydraulics:
#
#     def __init__(self):
#         """
#         Constructor Method
#         """
#
#         # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
#         self.name = "DesignHydraulics"
#
#         self.max_filling_ratio = 0.0    # Maximum filling ratio
#         self.theta = 0.0                # Theta angle
#         self.yn = 0.0                   # Normal depth
#         self.y = 0.0                    # Flow depth
#         self.area = 0.0                 # Flow area
#         self.perimeter = 0.0            # Wetted perimeter
#         self.T = 0.0                    # Top width
#         self.radius = 0.0               # Hydraulic radius
#         self.speed = 0.0                # Flow speed
#         self.tau = 0.0                  # Wall shear stress
#         self.Fr = 0.0                   # Froude's number
#         self.flowRate = 0.0             # Flow rate
#         self.pu = 0.0                   # Potential energy
#         self.cost = 0.0                 # Construction costs of a single pipe (section)
#         # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------
#
#     """ CALCULATE HYDRAULIC PARAMETERS """
#     def maximum_filling_ratio(self, diameter):
#         """ Calculate maximum filling ratio based on pipe's diameter
#         :return max_filling_ratio
#         """
#         # max_filling_rate=0.80
#         self.max_filling_ratio = 0.85 				# Maximum filling ratio in general
#         if diameter <= 0.6:
#             self.max_filling_ratio = 0.7
#         elif 0.30 < diameter <= 0.45:
#             self.max_filling_ratio = 0.7
#         elif 0.45 < diameter <= 0.9:
#             self.max_filling_ratio = 0.75
#         return self.max_filling_ratio
#
#     def calculate_theta(self, diameter):
#         """ Calculate flow angle """
#         y = self.maximum_filling_ratio(diameter) * diameter
#         alpha = np.arcsin((2 * y - diameter) / diameter)
#         self.theta = np.pi + 2 * alpha
#
#     def calculate_theta_yn(self, diameter, yn):
#         """ Calculate flow angle for the normal depth """
#         alpha = np.arcsin((2 * yn - diameter) / diameter)
#         self.theta = np.pi + 2 * alpha
#
#     def calculate_flow_area(self, diameter):
#         """ Calculate flow area """
#         self.area = np.power(diameter, 2) / 8 * (self.theta - np.sin(self.theta))
#
#     def calculate_wetted_perimeter(self, diameter):
#         """ Calculate wetted perimeter """
#         self.perimeter = self.theta * diameter / 2
#
#     def calculate_top_width(self, diameter, y):
#         """  Calculate top width """
#         self.T = (diameter * np.cos(np.arcsin((2 * y - diameter) / diameter)))
#
#     def calculate_hydraulic_radius(self, diameter):
#         """ Calculate hydraulic radius """
#         self.radius = diameter / 4 * (1 - np.sin(self.theta) / self.theta)
#
#     def calculate_tau(self, slope):
#         """ Calculate shear stress on the walls of the pipe """
#         self.tau = 9.81 * 1000 * self.radius * slope
#
#     def calculate_speed(self, slope):
#         """ Calculate flow speed either with Darcy-Weisbach equation or Manning's equation """
#         # self.speed = rounder(np.power(self.radius, 0.66666666666667) * np.power( slope, 0.5)*(1/roughness))
#         self.speed = -2 * np.sqrt(
#             8 * 9.81 * self.radius * slope) * np.log10(roughness/(14.8 * self.radius)+(
#                     rounder((2.51 * nu)/(4 * self.radius * np.sqrt(8 * 9.81 * self.radius * slope)))))
#
#     def calculate_froude_number(self):
#         """ Calculate Froude number """
#         self.Fr = rounder(self.speed / np.power((9.81 * self.area / self.T), 0.5))
#
#     def calculate_flow_rate(self):
#         """ Calculate real flow rate
#         :return flow    real flow rate in the pipe
#         """
#         self.flowRate = self.area * self.speed
#         return self.flowRate
#
#     def calculate_normal_depth(self, diameter, design_q, slope):
#         """ Calculate normal depth
#         :return yn Normal flow depth
#         """
#         yni = 0.0
#         ynf = diameter * self.maximum_filling_ratio(diameter)
#         yn = (ynf + yni)/2
#
#         while np.abs(yni-ynf) > 0.000001:
#             self.calculate_theta_yn(diameter, yn)
#             self.calculate_flow_area(diameter)
#             self.calculate_hydraulic_radius(diameter)
#             self.calculate_speed(slope)
#             flow = self.calculate_flow_rate()
#             if flow > design_q:
#                 ynf = yn
#             else:
#                 yni = yn
#             yn = (ynf + yni)/2
#
#         # Update attributes with real flow rate
#         self.calculate_theta_yn(diameter, yn)
#         self.calculate_flow_area(diameter)
#         self.calculate_wetted_perimeter(diameter)
#         self.calculate_hydraulic_radius(diameter)
#         self.calculate_top_width(diameter, yn)
#         self.calculate_speed(slope)
#         self.calculate_tau(slope)
#         self.calculate_froude_number()
#         self.calculate_flow_rate()
#         return yn
#
#     """ GET LAST VALUE OF HYDRAULIC PARAMETERS """
#     def get_theta(self):
#         return self.theta
#
#     def get_yn(self):
#         return self.yn
#
#     def get_perimeter(self):
#         return self.perimeter
#
#     def get_area(self):
#         return self.area
#
#     def get_radius(self):
#         return self.radius
#
#     def get_top_width(self):
#         return self.T
#
#     def get_speed(self):
#         return self.speed
#
#     def get_tau(self):
#         return self.tau
#
#     def get_froude(self):
#         return self.Fr
#
#     def get_flow_rate(self):
#         return self.flowRate
#
#     def get_pu(self, z_i, z_j):
#         self.pu = self.flowRate * (z_i - z_j)
#         return self.pu
#
#     """ RUN HYDRAULICS """
#     def run_hydraulics(self, diameter, slope):
#         """ Calculate hydraulic properties
#         :param diameter pipe's diameter
#         :param slope pipe's slope
#         :return flow
#         """
#         self.calculate_theta(diameter)
#         self.calculate_flow_area(diameter)
#         self.calculate_hydraulic_radius(diameter)
#         self.calculate_speed(slope)
#         return self.calculate_flow_rate()
#
#     def check_constraints(self, diameter):
#         """ Check hydraulic constraints
#         :param diameter pipe's diameter
#         :return check boolean
#         """
#         check = True
#
#         # Check maximum speed
#         if roughness > 0.0001:
#             if self.speed > 5:
#                 check = False
#         else:
#             if self.speed > 10:
#                 check = False
#
#         # Check minimum speed and minimum shear stress constraints
#         if diameter >= 0.45 and self.tau <= 2:
#             check = False
#
#         # Check minimum shear stress constraints
#         elif diameter < 0.45 and self.speed <= 0.75:
#             check = False
#
#         # Check maximum filling ration when shear stress < 2
#         elif self.yn / diameter <= 0.1 and self.tau < 2:
#             check = False
#
#         # Check Froude's number and filling rate for quasi-critical flow (0.7 < Fr > 1.5)
#         if 0.7 < self.Fr < 1.5 and self.yn / diameter > 0.8:
#             check = False
#
#         return check
#
#     """ PHYSICAL CHARACTERISTICS AND COSTS FUNCTION """
#     def get_wall_thickness(self, diameter):
#         """ Calculate wall thickness of the pipe
#         :param diameter pipe's diameter
#         :return thickness wallThickness
#         """
#         # Smooth materials (eg. PVC)
#         # Source: "Manuales tecnicos PAVCO Novaloc/Novafort"
#         if roughness < 0.00005:
#             thickness = 0.0869 * np.power(diameter, 0.935)
#
#         # Rough materials (eg. concrete)
#         # Source: http:#www.tubosgm.com/tubo_concretoref_jm.htm
#         else:
#             thickness = 0.1 * np.power(diameter, 0.68)
#         return thickness
#
#     def get_cost(self, diameter, length, up_depth, down_depth):
#         """ Calculate construction costs for a single pipe
#         :param diameter pipe's diameter
#         :param length pipe's length
#         :param up_depth Upstream depth
#         :param down_depth Downstream depth
#         :return cost Construction cost of the section
#         """
#         b = 0.2  # Side width from the wall of the pipe in meters(m) to the end of the ditch
#         e = self.get_wall_thickness(diameter)  # Wall thickness
#
#         # Calculate average depth and excavation volume
#         av_depth = (0.15 + diameter + 2 * e + (up_depth + down_depth) * 0.5)  # Average depth
#         volume = av_depth * (2 * b + diameter) * length  # Excavation volume
#
#         # Calculate the construction cost for a single section (pipe) according to Navarro, I. (2009)
#         dmm = diameter * 1000  # Enter diameter in millimetres
#         self.cost = 1.32 * (9579.31 * length * np.power(dmm, 0.5737) + 1163.77 * np.power(volume, 1.31))
#         return self.cost
