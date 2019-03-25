r"""
@file   urbanbeatscore.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2018  Peter M. Bach

This program is free software: you can redistribute it and/or modify
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

__author__ = "Peter M. Bach"
__copyright__ = "Copyright 2018. Peter M. Bach"

# --- CODE STRUCTURE ---
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import random
import os
import xml.etree.ElementTree as xmlElementTree

# --- URBANBEATS LIBRARY IMPORTS ---
import model.ubdatalibrary as ubdatalibrary
import model.ubscenarios as ubscenarios
import model.ublibs.ubspatial as ubspatial
import model.modules.md_decisionanalysis as md_decisionanalysis
import model.modules.md_climatesetup as md_climatesetup
import model.modules.md_delinblocks as md_delinblocks
import model.modules.md_impactassess as md_impactassess
import model.modules.md_perfassess as md_perfassess
import model.modules.md_regulation as md_regulation
import model.modules.md_socioecon as md_socioecon
import model.modules.md_spatialmapping as md_spatialmapping
import model.modules.md_infrastructure as md_infrastructure
import model.modules.md_urbandev as md_urbandev
import model.modules.md_urbplanbb as md_urbplanbb


# --- URBANBEATS SIMULATION CLASS DEFINITION ---
class UrbanBeatsSim(object):
    """The simulation class for UrbanBEATS, which contains all the information
    about scenarios, models, and other items. Contains the project info, reference
    to all modules, simulation settings and status of the current workflow.
    """
    def __init__(self, rootpath, options, parent=None):
        """Initialization for the class allowing the model to set up the simulation
        and required modules.

        :param rootpath: the root path of the UrbanBEATS Model containing the ancillary folder
        :param options: a dictionary of global options. The core of the model uses only several of these options including
                        ["maxiterations"] ...
        """
        random.seed()  # Seed the random numbers

        # Initialize variables
        self.__rootpath = rootpath          # the root path for UrbanBEATS' runtime
        self.__global_options = options     # global model options
        self.__runtime_method = "SF"
        self.__runtime_progress = 0         # virtual progress bar
        self.__parent = parent
        # SF = Single Scenario, Full Simulation,
        # AF = All scenarios, full sim,
        # SP = single scenario, performance only

        #Initialize paths
        self.emptyBlockPath = self.__rootpath+"/ancillary/emptyblockmap.shp"
        self.emptySysPath = self.__rootpath+"/ancillary/emptysystemmap.shp"

        #Observer, Status and Filename
        self.__observers = []   # Observers of the current simulation

        self.__project_saved = 0    # BOOL - has the project been saved?
        self.__simulation_completed = 0 # BOOL - has the simulation completed run?
        self.__projectpath = ""     # Project Path. Starts blank, is then replaced.

        # Project Parameters
        self.__project_info = {
            "name": "New UrbanBEATS Project",
            "date": "",
            "region": "",
            "city": self.__global_options["city"],
            "modeller": self.__global_options["defaultmodeller"],
            "affiliation": self.__global_options["defaultaffil"],
            "otherpersons": "none",
            "synopsis": "no synopsis",
            "boundaryshp": "no file selected",
            "logstyle": self.__global_options["projectlogstyle"],
            "projectpath": self.__global_options["defaultpath"],
            "keepcopy": 0,
            "project_coord_sys": self.__global_options["defaultcoordsys"],
            "project_epsg": self.__global_options["customepsg"]
        }

        self.__boundaryinfo = {}

        self.__datalibrary = None   # initialize the data library
        self.__projectlog = None    # initialize the project log
        self.__scenarios = {}       # initialize the scenarios
        self.__activescenario = None

    # INITIALIZATION METHODS
    def initialize_simulation(self, condition):
        """Performs a full initialization of the project simulation, creates
        a folder for holding relevant data and results.

        :return: None
        """
        if condition == "new":  # for starting a new project
            self.setup_project_folder_structure()   # Creates all the folders

            # Create a new data library
            datalib = ubdatalibrary.UrbanBeatsDataLibrary(self.__projectpath,
                                                          self.get_project_parameter("keepcopy"))
            self.set_data_library(datalib)

            # Create a new project log
            projectlog = UrbanBeatsLog(self.__projectpath)
            self.set_project_log(projectlog)
        elif condition == "open":   # for opening a project
            # Folder structure is already present
            self.__projectpath = self.get_project_parameter("projectpath")+"/"+self.get_project_parameter("name")

            # Create new data library
            datalib = ubdatalibrary.UrbanBeatsDataLibrary(self.__projectpath,
                                                          self.get_project_parameter("keepcopy"))
            datalib.setup_library_from_xml()
            self.set_data_library(datalib)

            # Create a new project log
            projectlog = UrbanBeatsLog(self.__projectpath)
            self.set_project_log(projectlog)    # Go through existing project logs and update or add log info [TO DO]

            # Go through scenarios and add the scenarios to the scenario manager
            scenariofiles = os.listdir(self.get_project_parameter("projectpath")+"/"+self.get_project_parameter("name")
                                       + "/scenarios/")
            for sf in scenariofiles:
                if ".xml" not in sf:
                    continue
                else:
                    self.create_new_scenario()
                    self.__activescenario.setup_scenario_from_xml(sf)
                    self.add_new_scenario(self.__activescenario)

        elif condition == "import": # for importing a project
            pass    # [TO DO]

        # Regardless of mode, all of them should now load the boundary map and get the details
        self.update_project_boundaryinfo()

    def register_observer(self, observerobj):
        """Adds an observer references by observerobj to the self.__observers array. This uses the Observer design
        pattern."""
        self.__observers.append(observerobj)

    def get_program_rootpath(self):
        """Returns the root path of the program."""
        return self.__rootpath

    def load_project_info_xml(self, projectpath):
        """Loads the project's info.xml file and writes the information into the simulation core."""
        try:
            projinfo = xmlElementTree.parse(projectpath + "/info.xml")
        except IOError:
            return False
        print(projectpath + "/info.xml")
        root = projinfo.getroot()
        projdict = {}
        projdata = root.find('projectinfo')
        for child in projdata:
            projdict[child.tag] = child.text
        for k in projdict.keys():
            self.set_project_parameter(k, type(self.get_project_parameter(k))(projdict[k]))
        return True

    def update_project_boundaryinfo(self):
        """Loads the boundary map shapefile, obtains coordinates of the bounding polygon and spatial
        stats including simulation area, extents, etc. Information is saved to self.__boundaryinfo."""
        boundaryshp = self.get_project_parameter("boundaryshp")
        coordinates, mapstats = ubspatial.get_bounding_polygon(boundaryshp, "native", self.__rootpath,
                                                               defaultepsg=self.__project_info["project_epsg"])
        self.__boundaryinfo = mapstats.copy()
        self.__boundaryinfo["coordinates"] = coordinates
        return True

    def get_project_boundary_info(self, param):
        """Retrieves spatial boundary information for the current project from the self.__boundarinfo variable.

        :param param: the name of the key of self.__boundaryinfo.
        :return: value if key is existent, None if not.
        """
        if param == "all":
            return self.__boundaryinfo
        if param == "mapextents":
            return self.__boundaryinfo["xmin"], self.__boundaryinfo["xmax"], \
                   self.__boundaryinfo["ymin"], self.__boundaryinfo["ymax"]
        try:
            return self.__boundaryinfo[param]
        except KeyError:
            return None

    def setup_project_folder_structure(self):
        """Sets up the base folder structure of the project based on the specified path. The folder
        structure contains several fundamental fodlers including 'datalib' and 'output' and one
        folder for each scenario in the simulation. It also will contain several .xml files, which
        are written in separate methods."""
        projectpath = self.get_project_parameter("projectpath")
        projectname = self.get_project_parameter("name")
        namecounter = 0
        projectnewname = projectname.rstrip(" ")    # Cull whitespaces at the end of the name
        while os.path.isdir(projectpath+"/"+projectnewname):
            namecounter += 1
            projectnewname = projectname+"_"+str(namecounter)
        self.set_project_parameter("name", projectnewname)
        os.makedirs(projectpath+"/"+projectnewname)
        os.makedirs(projectpath+"/"+projectnewname+"/datalib")
        os.makedirs(projectpath+"/"+projectnewname+"/scenarios")
        os.makedirs(projectpath+"/"+projectnewname+"/output")
        self.write_project_info_file()
        self.__projectpath = projectpath+"/"+projectnewname

    def write_project_info_file(self):
        """Writes the info.xml file, which contains the project's metadata to the project folder
        for faster loading and setting up of the interface on the next simulation."""
        # write project info XML
        projectpath = self.get_project_parameter("projectpath")
        projectname = self.get_project_parameter("name")
        fullpath = projectpath+"/"+projectname
        f = open(projectpath+"/"+projectname+"/info.xml", 'w')
        f.write('<URBANBEATSPROJECTCONFIG creator="Peter M. Bach" version="1.0">\n')
        f.write('\t<projectinfo>\n')
        projinfo = self.get_all_project_info()
        for item in projinfo.keys():
            f.write("\t\t<"+str(item)+">"+str(projinfo[item])+"</"+str(item)+">\n")
        f.write("\t</projectinfo>\n")
        f.write('</URBANBEATSPROJECTCONFIG>')
        f.close()

    # PROJECT PARAMETER SETTINGS

    # SCENARIO MANAGEMENT
    def create_new_scenario(self):
        """Creates a new scenario object and sets it as the active scenario."""
        newscenario = ubscenarios.UrbanBeatsScenario(self, self.__datalibrary, self.__projectlog)
        self.__activescenario = newscenario     # Set the active scenario's name
        print("Created")

    def add_new_scenario(self, scenario_object):
        """Adds a new scenario to the simulation by creating a UrbanBeatsScenario() instance and initializing
        it."""
        if scenario_object.get_metadata("name") not in self.__scenarios.keys():
            self.__scenarios[scenario_object.get_metadata("name")] = scenario_object
            return True
        else:
            return False    # Cannot have two scenarios of the same name!

    def set_active_scenario(self, scenario_name):
        """Sets the current active scenario to the scenario with the name "name"."""
        try:
            self.__activescenario = self.__scenarios[scenario_name]
        except KeyError:
            self.__activescenario = None

    def get_active_scenario(self):
        """Returns the active scenario in the core simulation."""
        return self.__activescenario

    def get_scenario_names(self):
        """Returns all scenario names"""
        return self.__scenarios.keys()

    def get_scenario_by_name(self, scenario_name):
        """Returns the scenario with the specified name."""
        try:
            return self.__scenarios[scenario_name]
        except KeyError:
            return None

    def check_for_existing_scenario_by_name(self, scenario_name):
        """Returns True if the scenario exists, false if the scenario doesn't already exist by name

        :return True: scenario exists in simulation, False: scenario does not exist."""
        if scenario_name in self.__scenarios.keys():
            return True
        else:
            return False

    def delete_scenario(self, scenario_name):
        """Removes the scenario with the given scenario name from the simulation core."""
        if self.__activescenario.get_metadata("name") == scenario_name:
            self.__activescenario = None            # Set the active scenario to None
        try:
            self.__scenarios.pop(scenario_name)     # Pop the scenario with the key 'scenario_name'
        except KeyError:
            pass
        self.__datalibrary.remove_all_reference_to_scenario("name")  # Remove all references to scenario
        self.delete_scenario_files(scenario_name)

    def delete_scenario_files(self, scenario_name):
        """Removes the file within the project folder containing the scenario."""
        pass    # [TO DO]

    # GETTERS AND SETTERS
    def get_all_project_info(self):
        """Returns the full project information"""
        return self.__project_info

    def get_num_scenarios(self):
        """Returns the total number of scenarios currently in the project."""
        return len(self.__scenarios)

    def get_num_datasets(self):
        """Returns a single integer indicating the number of data files in the library."""
        return self.__datalibrary.get_num_datafiles()

    def get_project_parameter(self, parname):
        """Get project info either as a whole dictionary or based on individual
        attributes.

        :parname attribute: specific attribute of the project info dictionary, if
                "ALL" is specified, method returns entire dictionary.
        :return: dictionary entry or entire dictionary self.__project_info
        """
        if parname == "ALL":
            return self.__project_info
        try:
            return self.__project_info[parname]
        except KeyError:
            return None

    def set_project_parameter(self, parname, value):
        """Sets a project parameter.

        :param parname: name of the parameter, contained in the keys of self.__project_info
        :param value: value of the parameter to be set
        """
        self.__project_info[parname] = value

    def get_project_path(self):
        """Returns the path of the current project. The path should never be modifiable.

        :return: self.__projectpath as string
        """
        return self.__projectpath

    def get_global_options(self, attribute):
        """Get the global options for the model. If a specific attribute is specified
        then method returns that particular attribute instead.

        :param attribute: specific attribute of option in the dictionary. If
                "ALL" is specified, returns whole dictionary instead.
        :return: self.__global_options or a specific entry of this dictionary.
        """
        if attribute == "ALL":
            return self.__global_options
        else:
            try:
                return self.__global_options[attribute]
            except KeyError:
                return None

    def set_data_library(self, datalib):
        """Sets the active data library using the object datalib of type UrbanBeatsDataLibrary()"""
        self.__datalibrary = datalib

    def get_data_library(self):
        """Returns the active data library of type UrbanBeatsDataLibrary()"""
        return self.__datalibrary

    def import_data_from_project(self, projectpath):
        """Imports and fills in the active data library using data from another project."""
        pass    #[TO DO]

    def import_archive_file(self, uba_filename):
        """Imports data from a data archive file into the active project's data archive."""
        pass    #[TO DO]

    def set_project_log(self, projectlog):
        """Sets the active project log using the object projectlog of type UrbanBeatsLog()"""
        self.__projectlog = projectlog

    def get_project_log(self):
        """Returns the active project log of type UrbanBeatsLog()"""
        return self.__projectlog

    def update_observers(self, message):
        """Sends the message to all observers contained in the core's observer list."""
        for observer in self.__observers:
            observer.update_observer(str(message))

    def update_runtime_progress(self, value):
        """Can be called by the active_scenario to update the progress."""
        self.__runtime_progress = value
        self.__parent and self.__parent.update_progress(self.__runtime_progress)

    def run(self):
        """Runs the UrbanBEATS Simulation based on the active scenario, data library, project
        info and other information."""
        if self.get_active_scenario() is None:
            self.update_observers("No active scenario selected!")
            return
        self.__parent and self.__parent.enable_disable_run_controls(0)
        if self.__runtime_method == "SF":
            active_scenario = self.get_active_scenario()        # Get the active scenario
            self.update_runtime_progress(0)                     # Reset progress bar
            if active_scenario.runstate:                        # If active scenario has been run, reinitialize it
                self.__parent and self.__parent.initialize_output_console()
                while active_scenario.reinitialize():
                    pass
            active_scenario.attach_observers(self.__observers)      # Attach the observers
            scenario_name = active_scenario.get_metadata("name")    # Get the name and report
            self.update_observers("Running Scenario: " + str(scenario_name))
            # active_scenario.start()     # Start the active scenario thread      # Start the thread
            active_scenario.run_scenario()

        elif self.__runtime_method == "AF":
            pass    # TO DO - ALL SCENARIOS FULL SIMULATION AT ONCE.
        elif self.__runtime_method == "SP":
            pass    # TO DO - Single Scenario - Performance ONLY

    def on_thread_finished(self):
        """Called when the scenario has finished running. It updates the observes with the scenario finished message.
        and re-enables the run controls."""
        self.update_observers("Scenario Finished")
        self.__parent and self.__parent.enable_disable_run_controls(1)

    def check_runtime_state(self):
        """Returns the current runtime progress value."""
        return self.__runtime_progress


class UrbanBeatsLog(object):
    """Class for logging the UrbanBEATS workflow, the log manages the history of the project
    as well as the current modelling session and is essential for tracking changes made throughout the
    workflow."""
    def __init__(self, projectpath):
        """Contains two main variables: one that contains the project's history, one that contains the
        current session's log."""
        self.__ublogger = []
        self.__ublogsession = []

    def write_to_log(self, message):
        """Probably the most commonly called function, writes a log entry and saves it to the log array"""
        logstring = ""

    def initialize_session(self):
        """Writes a title string to the log to indicate the start of a new session."""
        logstring = ""

    def save_log(self):
        """Saves the current complete log history to the log file in the project folder"""
        pass

    def load_log_history(self):
        """Loads the project log, reads the entire history."""
        pass

    def export_log(self, filepath):
        """Exports the log to an external file on the harddrive that the user can reader later on."""
        pass


