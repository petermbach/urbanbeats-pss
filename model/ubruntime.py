r"""
@file   ubruntime.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2017-2022  Peter M. Bach

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
__copyright__ = "Copyright 2017-2022. Peter M. Bach"

# --- CODE STRUCTURE ---
#       (1) ...
# --- --- --- --- --- ---

# --- PYTHON LIBRARY IMPORTS ---
import threading
import gc

# --- URBANBEATS LIBRARY IMPORTS ---
from .progref import ubglobals


# --- SCENARIO CLASS DEFINITION ---
class UrbanBeatsRuntime(threading.Thread):
    """A runtime class, designed to execute a single module based on its data. This runtime gets started in a separate
    thread."""
    def __init__(self, simulation, datalibrary, projectlog):
        threading.Thread.__init__(self)
        self.__observers = []
        self.__progressbar = None           # The active progress bar to use
        self.__active_module = None
        self.simulation = simulation        # The CORE (UrbanBEATSSim)
        self.datalibrary = datalibrary      # The active data library instance
        self.projectlog = projectlog        # The active log
        self.projectpath = simulation.get_project_path()
        self.runstate = False

    def define_active_module(self, module_obj):
        self.__active_module = module_obj

    def attach_observers(self, observers):
        """Assigns an array of observers to the Scenario's self.__observers variable."""
        self.__observers = observers

    def attach_progressbar(self, observer):
        """Assigns an array of progressbar observers to the Scenario's self.__progressbar variable."""
        self.__progressbars = observer

    def update_observers(self, message):
        """Sends the message to all observers contained in the core's observer list."""
        for observer in self.__observers:
            observer.update_observer(str(message))

    def update_runtime_progress(self, value):
        """Sends the value to the progress bar(s)."""
        self.__progressbar.update_progress(int(value))

    def reinitialize(self):
        """Reinitializes the thread, resets the assets, edges and point lists and runs a garbage collection."""
        if self.ident is not None:
            threading.Thread.__init__(self)
        else:
            pass
        return False

    def run(self):
        """Overrides the thread.run() function, called when thread.start() is used."""
        self.runstate = True        # Used later on to reset the thread
        self.__active_module.attach_console(self.__observers)
        self.__active_module.attach_progressbar(self.__progressbars)
        self.__active_module.run_module()