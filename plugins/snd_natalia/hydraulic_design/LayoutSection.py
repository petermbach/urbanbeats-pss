"""
:author duquevna
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
