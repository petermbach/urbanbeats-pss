# r"""
# @file DesignGraphBuilder
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
# from numpy import power, infty, array
# from plugins.snd_natalia.utilities.Rounder import rounder
# from plugins.snd_natalia.hydraulic_design.LayoutNode import LayoutNode
# from plugins.snd_natalia.hydraulic_design.DesignNode import DesignNode
# from plugins.snd_natalia.hydraulic_design.DesignedArc import DesignedArc
# from plugins.snd_natalia.hydraulic_design.DesignHydraulics import DesignHydraulics
# from plugins.snd_natalia.utilities.Global import elevation_change, commercial_diameters, Arrow3D
# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
#
#
# class DesignGraphBuilder(object):
#
#     def __init__(self, dh):
#         """
#         Constructor Method: Design Graphbuilder Class (hydraulic design problem)
#         """
#         # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
#         self.name = "Design GraphBuilder"
#
#         # Instance of other Classes. They let you have access to all the methods and attributes of that class.
#         self.dh = dh                # Instance of the Class DataHandler.
#         self.ls_Node = LayoutNode   # Instance of the Class LayoutNode.
#
#         self.pending_LS_Node = []   # List of pending layout nodes to visit (evaluate)
#         self.designedArcs = []      # List of design arcs
#         self.solution = []          # List of the arcs that belong to the Shortest Path
#         self.hydraulics = DesignHydraulics()  # instance of Design hydraulics class
#
#         # No. possible invert elevations (depths) between the excavation limits within a manhole
#         # self.numPossibleDepths = int((max_depth - min_depth) * elevation_change) + 1
#
#     #  END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------
#
#     def build_and_solve(self):
#         """ Run all the functions to solve the hydraulics design problem """
#         print("Nodes generation...")
#         self.generate_nodes()
#         print("Design graph generation...")
#         self.generate_design_graph()
#         print("Get solution...")
#         return self.get_solution()
#
#     def generate_nodes(self):
#         """ Generate design nodes for each layout node """
#         for mh in self.dh.manholes:  # loop over the manholes
#             arc_in = 0  # assign 0 arcs coming into the current manhole (except the outfall)
#
#             if mh == self.dh.manholes[-1]:
#                 arc_in = -1     # assign -1 arcs coming into the outfall
#
#             # Loop over the layout nodes in each manhole
#             for ln in mh.layout_nodes:
#                 # print (type(ln), ln.id)
#
#                 id_design_node = 0  # id of the design node in the current layout node
#                 step = 1.0 / elevation_change
#
#                 # Loop in Z, the invert elevation of the pipes
#                 # z = ln.upper_bound
#
#                 for diam in commercial_diameters:
#
#                     z = ln.upper_bound-diam
#
#                     while ln.lower_bound < z <= ln.upper_bound:
#                         self.dh.nodeID += 1
#                         node_ini = DesignNode(self.dh.nodeID, ln, diam, z, arc_in)
#                         ln.nodes.append(node_ini)
#                         id_design_node += 1
#                         # print("Ln: ", node_ini.ls_Node.id, " id:", node_ini.id, " Diam: ", diam, "Z: ", z)
#                         z = z - step
#
#                 # print("M: " + str(mh.id) + " Ln: " + str(ln.id) + " arc_in: " + str(arc_in) +
#                 #       " No.Nodes: " + str(len(ln.get_design_nodes())) +
#                 #       " Total nodes: " + str(self.dh.nodeID))
#
#     def generate_design_graph(self):
#         """*
#         Method that generates the arcs of the Graph Build the graph for the
#         hydraulic design problem and solve the shortest path simultaneously
#         """
#         counter_feasible_arcs = 0   # Counter for the number of feasible alternatives
#         count = 0
#         id_arc = 0
#
#         # Starts at the last manhole (outfall)
#         last_m = self.dh.manholes[-1]
#
#         for ls_Node in last_m.layout_nodes:
#
#             self.pending_LS_Node.append(ls_Node)
#             while self.pending_LS_Node:
#                 # print("pending: " + str([p.id for p in self.pending_LS_Node]))
#
#                 ls_node_down = self.pending_LS_Node[0]
#                 self.pending_LS_Node.remove(ls_node_down)
#                 sections_in = ls_node_down.layoutSections_in
#                 # print("Evaluating :"+ lsNodeDown.id)
#                 # print("LS: " + str(lsNodeDown.id) + " feasible: " +
#                 #       str(counterFeasibleArcs) + " out of: " + str(count))
#
#                 for section in sections_in:
#                     ls_node_up = section.lsNode_Up
#                     self.pending_LS_Node.append(ls_node_up)
#                     # print("--> " + lsNodeUp)
#
#                     for down in ls_node_down.nodes:
#                         if down is None and down.dArcs_in != 0:
#                             continue
#
#                         for up in ls_node_up.nodes:
#                             # print(lsNodeDown.id, down.id, " -> ", lsNodeUp.id, up.id)
#
#                             if up is None:
#                                 continue
#
#                             z_up = up.z
#                             z_down = down.z
#
#                             d_up = up.diameter
#                             d_down = down.diameter
#
#                             if ls_node_up.type == "I" and d_up != d_down:
#                                 continue
#
#                             if d_down < d_up:  # Check the increment of the downstream diameters
#                                 continue
#
#                             count += 1
#                             m_up = ls_node_up.my_manhole
#                             x_up = m_up.coordinate_x
#                             y_up = m_up.coordinate_y
#
#                             # m_down = ls_node_down.my_manhole
#                             x_down = ls_node_down.my_manhole.coordinate_x
#                             y_down = ls_node_down.my_manhole.coordinate_y
#
#                             # Calculate the distance between the upstream and downstream design nodes
#                             a = power(x_down - x_up, 2)
#                             b = power(y_down - y_up, 2)
#                             pythagoras = rounder(power(a + b, 0.5))
#
#                             # Calculate the real length of the pipes
#                             a2 = power(rounder((z_up - z_down)), 2)
#                             b2 = power(pythagoras, 2)
#                             pipe_length = rounder(power(a2 + b2, 0.5))
#                             slope = rounder(float(z_up - z_down) / pythagoras)          # Calculate "positive" slope
#
#                             if slope <= 0:       # Check if the slope is gravity driven
#                                 continue
#
#                             # print("From: "+ down + "\t To:" + up)
#                             depth_up = ls_node_up.upper_bound + 1.2 - z_up-d_down
#                             depth_down = ls_node_down.upper_bound + 1.2 - z_down-d_down
#                             hs = True
#
#                             # print("DNodeUp: "+up+" DNodeDown: "+down)
#                             cost = self.hydraulics.get_cost(d_down, pythagoras, depth_up, depth_down)
#
#                             if down.Vi + cost < up.Vi and hs:
#
#                                 q = section.lsSection_FlowRate
#                                 if q == 0:
#                                     continue
#
#                                 # Calculate the capacity of the pipe
#                                 # flow rate with a maximum filling ratio
#                                 flow = self.hydraulics.run_hydraulics(d_down, slope)
#
#                                 if flow >= q:
#                                     down.yNormal = self.hydraulics.calculate_normal_depth(d_down, q, slope)
#
#                                     if self.hydraulics.check_constraints(d_down):
#
#                                         # print(str(count) + "diam:" + str(d_down) + "slope: " + str(slope) +
#                                         #       " flow: " + str(flow) + " speed:" + str(self.hydraulics.get_speed()))
#
#                                         counter_feasible_arcs += 1
#
#                                         up.dArcs_in += 1
#                                         down.dArcs_out += 1
#
#                                         up.Vi = down.Vi + cost
#                                         up.Pj = down
#                                         # print(m_down.id, down.Vi, cost, " -> ", m_up.id, up.Vi)
#
#                                         d_arc = DesignedArc(id_arc, up, down, section, cost, d_down, q, slope,
#                                                             pipe_length,
#                                                             self.hydraulics.get_yn(),
#                                                             self.hydraulics.get_theta(),
#                                                             self.hydraulics.get_radius(),
#                                                             self.hydraulics.get_area(),
#                                                             self.hydraulics.get_speed(),
#                                                             self.hydraulics.get_tau(),
#                                                             self.hydraulics.get_froude())
#                                         id_arc += 1
#                                         self.designedArcs.append(d_arc)
#
#         print("FINISHED: There are " + str(counter_feasible_arcs) + " feasible arcs out of: " + str(count))
#
#     def get_solution(self):
#         """Get the shortest path from all the external nodes towards the outfall"""
#         self.solution = []
#         # Loop in Manholes
#         for m in self.dh.manholes:
#             list_ls_nodes = m.layout_nodes
#             # Loop in Layout Nodes of each Manhole
#             for ls_node in list_ls_nodes:
#                 # Start from each external (initial) node towards the outfall
#                 if ls_node.type != "I":
#                     continue
#
#                 min_cost = infty
#                 min_cost_node = None
#                 # Get the minimum cost node (from the hydraulic design problem)
#                 for current_node in ls_node.nodes:
#                     if current_node is None:
#                         continue
#                     cumulative_cost = current_node.Vi
#
#                     # Update minimum cost node and minimum cost
#                     if cumulative_cost > min_cost:
#                         continue
#                     min_cost = cumulative_cost
#                     min_cost_node = current_node
#
#                 # Get all the parental nodes that belong to the shortest path
#                 if min_cost_node is None:
#                     continue
#                 current_node = min_cost_node
#                 parent_node = current_node.Pj
#
#                 while parent_node is not None:
#                     # print(current_node.ls_node.id, " -> ", parent_node.ls_node.id)
#
#                     for arc1 in self.designedArcs:
#                         up = arc1.dn_up
#                         down = arc1.dn_down
#                         if current_node == up and parent_node == down and arc1 not in self.solution:
#                             self.solution.append(arc1)
#                             # print(str(up.ls_node.id) + " -> " + str(down.ls_node.id))     # DEBUG
#                     current_node = parent_node
#                     parent_node = parent_node.Pj
#
#         i = 0
#         while i < len(self.solution):
#             j = i+1     # Increment j by one step, so we avoid checking the exact same arcs.
#             arc1 = self.solution[i]
#             while j < len(self.solution):
#                 arc2 = self.solution[j]
#
#                 if arc1.id == arc2.id:  # The loop will not enter here as long as j = i+1, but it's here for clarity.
#                     j += 1
#                     continue
#
#                 # if arc1.ls_section.parent_section == arc2.ls_section.parent_section:
#                 if [int(arc1.dn_up.ls_node.id), int(arc1.dn_down.ls_node.id)] == \
#                         [int(arc2.dn_up.ls_node.id), int(arc2.dn_down.ls_node.id)]:
#
#                     if arc1.dn_up.z >= arc2.dn_up.z:
#                         self.solution.remove(arc1)
#                         i -= 1
#                         break
#                     else:
#                         self.solution.remove(arc2)
#                         j -= 1
#                 j += 1
#             i += 1
#
#         print("SOLUTION...")
#         print(len(self.solution))
#
#         fig = plt.figure()
#         ax = fig.add_subplot(111, projection='3d')
#
#         for sol in self.solution:
#             print str(sol)
#
#             # print([(str(sol.dn_up.ls_node) + " " + str(sol.dn_down.ls_node) + "\n") for sol in new_l])
#
#             x1 = [sol.dn_up.x, sol.dn_down.x]
#             y1 = [sol.dn_up.y, sol.dn_down.y]
#             z1 = [sol.dn_up.z, sol.dn_down.z]
#             ax.plot(x1, y1, z1, marker='4')
#
#         ax.set_xlabel('X')
#         ax.set_ylabel('Y')
#         ax.set_zlabel('Z')
#         plt.show()
#
