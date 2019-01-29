"""
:author duquevna
"""
from HydraulicDesign.DataHandler import DataHandler
from HydraulicDesign.LayoutGraphbuilder import LayoutGraphbuilder
from HydraulicDesign.DesignGraphBuilder import DesignGraphBuilder


class RunHydraulicDesign(object):

    def __init__(self):
        self.name = " Run hydraulic design"

    @staticmethod
    def run():

        # File with the solution of the Layout Selection problem
        p = r"C:\Users\duquevna\polybox\010_PhD\01_Python\SND_PY\Files\Resultados4.txt"

        # Read the file and create manholes and sections
        d = DataHandler(p)
        d.read_file()

        # Generate layout graph
        lg = LayoutGraphbuilder(d)
        print(lg.name)
        lg.build()

        # Generate and solve the hydraulic design graph
        gb = DesignGraphBuilder(d)
        print(gb.name)
        gb.build_and_solve()


RunHydraulicDesign.run()
