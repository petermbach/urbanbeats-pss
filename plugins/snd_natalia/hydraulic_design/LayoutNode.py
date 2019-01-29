"""
:author duquevna
"""
import HydraulicDesign.DataHandler as dataHandler
from Utilities.Global import min_depth, max_depth


class LayoutNode(object):

    def __init__(self, id_layout_node, n_type, n_manhole):
        """
        Constructor Method: Layout_Node Class
        :param id_layout_node
        :param n_type
        :param n_manhole
        """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "Layout_Node"
        self.id = id_layout_node        # Layout_Node id
        self.type = n_type              # Layout_Node type
        self.my_manhole = n_manhole     # Parental manhole
        self.checked = 0

        self.layoutSections_in = []     # Array of Layout sections coming in from layout node
        self.layoutSections_out = []    # Array of Layout sections going out from layout node

        # Define excavation limits
        self.upper_bound = n_manhole.coordinate_z - min_depth   # Upper excavation limit
        self.lower_bound = n_manhole.coordinate_z - max_depth   # Lower excavation limit

        self.dh = dataHandler           # Attribute of the class DataHandler
        # Create vector of Design_Nodes
        # The size of the vector is given by all the combinations of commercial pipe diameters
        # and possible invert elevations (nodes per manhole)
        # dh.commercial_diameters.length * dh.numPossibleDepths
        self.nodes = []  # Vector of Design_Nodes that belong to this Layout node
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def __str__(self):
        """ Print design node properties """
        return "Layout Node: " + str(self.id)
        # return "Layout Node: " + str(self.id) + " My Manhole: " + str(self.my_manhole) + " Type: " + str(self.type)
