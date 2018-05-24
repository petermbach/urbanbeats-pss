# -*- coding: utf-8 -*-
"""
@file   ubmodule.py
@author Peter M Bach <peterbach@gmail.com>
@section LICENSE

Urban Biophysical Environments and Technologies Simulator (UrbanBEATS)
Copyright (C) 2012  Peter M. Bach

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


class UBModule(object):
    """Abstract class for the UrbanBEATS module classes. It has the basic structure of an UrbanBEATS module including
    parameter management functions, observer attaching/detaching and other future additions. When creating an
    UrbanBEATS Module, it must inherit from this class in order to gain extensive functionality within the larger
    core."""
    def __init__(self):
        self.__observers = []       # Holds all observers within the runtime (e.g. console, log)
        self.__parameters = {}      # Holds all parameter names and type as dictionary
        # Parameter dictionary has key: 'parameter name' and value [type, description]

    def attach(self, observers):
        """Attaches an observer object to the list of observers in the module.

        :param observers: the observers object that the module should refer to should have updateObserver() method
        :return: True
        """
        for i in observers:
            if not i in self.__observers:
                self.__observers.append(i)
        return True

    def detach(self, observers):
        """Detaches an observer from the module by removing its reference from the observer list.

        :param observers: The observer object to detach
        :return: True
        """
        for i in observers:
            try:
                self.__observers.remove(i)
            except ValueError:
                pass
        return True

    def notify(self, updateMessage):
        """Sends an update message to all observers attached to the current module. This update message is like a
        'print-to-screen' message. Notify is called in the module if you wish to debug or send the user a message during
        module runtime.

        :param updateMessage: message to be sent to all observers, gets converted to a string.
        :return: True
        """
        self.__observers[0].updateObserver(str(updateMessage))
        return True

    def notifyProgress(self, value):
        self.__observers[1].updateObserver(value)

    def createParameter(self, name, type, descript):
        """Creates a new parameter and saves its metadata to the list of parameters of the module self.__parameters.
        Note that when developing the module, each line of .createParameter() should be followed by a definition of
        class attribute with self.name = defaultvalue. This is essential for the get and set parameter functions.

        :param name: single continuous string with no whitespaces representing the parameter name (use underscores _)
        :param type: in ALLCAPS, the type of the parameter, choose from DOUBLE, BOOL, STRING, LISTDOUBLE
        :param descript: A short string description of the parameter value, this is relevant for metadata and
                            development
        :return: True
        """
        self.__parameters[name] = [type, descript]
        return True

    def getParameterType(self, name):
        """Returns the parameter type i.e. DOUBLE, BOOL, STRING, LISTDOUBLE of a given parameter if it exists in the
        module's parameter list.

        :param name: the parameter name as it is written in the module (continuous no whitespace string)
        :return: parameter type if exists, None if non-existent
        """
        try:
            return self.__parameters[name][0]
        except KeyError:
            return None

    def getParameter(self, name):
        """Returns the value of the class' attribute with the parameter name 'name'. We are using the class' internal
        dictionary and are referring to parameter variables through __dict__

        :param name: name of the parameter variable of the inherited class
        :return: value of the parameter variable specified
        """
        return self.__dict__.get(name)

    def setParameter(self, name, value):
        """Sets the paramter 'name' with the value 'value' by looking up the class' attributes for the specific class
        variable self.??? with the name <name>.

        :param name: Parameter name
        :param value: Parameter value, must correspond to the parameter type
        :return: True
        """
        self.__dict__.__setitem__(name, value)
        return True

    def getModuleParameterList(self):
        """Returns the full parameter list of the module. This is useful for obtaining all parameter names for saving
        and loading simulations and other actions where the full parameter metadata is needed.

        :return: self.__parameters dictionary
        """
        return self.__parameters

#KEYWORDS FOR VARIABLES (THIS IS RELEVANT FOR SAVING AND LOADING DATA)
DOUBLE = 'DOUBLE'
BOOL = 'BOOL'
STRING = 'STRING'
LISTDOUBLE = 'LISTDOUBLE'