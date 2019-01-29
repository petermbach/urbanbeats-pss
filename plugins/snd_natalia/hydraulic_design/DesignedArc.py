"""
:author duquevna
"""
# import Hydraulic_Design


class DesignedArc(object):

    def __init__(self, id, dn_up, dn_down, ls_section, arc_cost, diameter, flow, slope, length, normal_depth, angle,
                 radius, area, speed, tau, froude):
        """"
        Constructor Method: Designed Arc (Hydraulic Design Problem)
        :param dn_up
        :param dn_down
        :param ls_section
        :param arc_cost
        :param diameter
        :param slope
        :param length
        :param normal_depth
        :param angle
        :param radius
        :param area
        :param speed
        :param tau
        :param froude
        :param flow
        """
        # ATTRIBUTES DECLARATION ---------------------------------------------------------------------------------------
        self.name = "DesignArc"
        self.id = id

        # LAYOUT SECTION PROPERTIES
        self.dn_up = dn_up					# Upstream design node
        self.dn_down = dn_down 				# Downstream design node
        self.ls_section = ls_section        # Parental layout section (i,j)
        self.arc_cost = arc_cost	 		# Construction cost of the design arc
        self.diameter = diameter

        # List of hydraulic properties to be calculated for each pipe
        self.slope = slope					# Slope
        self.length = length				# Length
        self.fillingRatio = normal_depth / self.dn_down.diameter   # Filling ratio
        self.normal_depth = normal_depth				# Normal depth
        self.angle = angle					# Angle
        self.area = area					# Area
        self.radius = radius				# Hydraulic radius
        self.speed = speed					# Speed
        self.tau = tau						# Shear stress on the walls on the pipe
        self.froude = froude				# Froude number
        self.flow = flow				    # Flow rate
        # END OF ATTRIBUTES DECLARATION---------------------------------------------------------------------------------

    def __str__(self):
        """ Print design arc properties"""
        text = ("Designed Section: \n" + str(self.ls_section) +
                " : " + " d = " + str(self.diameter) + " , z = (" + str(self.dn_up.z) + "," +
                str(self.dn_down.z) + " )" + " cost: " + str(self.arc_cost) + " Qd:" + str(self.flow))

        # text = str(self.ls_section)
        return text
