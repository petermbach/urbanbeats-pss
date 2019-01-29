"""
:author duquevna
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
