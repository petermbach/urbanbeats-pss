# -*- coding: utf-8 -*-
"""
@file   main.pyw
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
__copyright__ = "Copyright 2012. Peter M. Bach"


class ValueScale(object):
    """Holds the information on value vs. criterion. The object can be queried by the program to rapidly obtain a
    value scale between two specific numbers."""
    def __init__(self, x_scale, y_scale):
        """Takes two lists of inputs, a series of x-values on the x-axis and a series of y-values on the y-axis that
        represent the value scale from 0 to 1 preferably.

        :param x_scale: A tuple of x-values ()
        :param y_scale: A tuple of y-values, i.e. the value/utility ()
        """
        self.__xdata = x_scale
        self.__ydata = y_scale

    def return_value_scale(self, x, option="continuous", returntype="value"):
        """Returns the utility/value of this value-scale function based on the input x-value. First determines
        bracket within which x is located and then calculates through interpolation.

        :param x: the input x-value for which the utility wants to be known
        :param option: default is continuous. If continuous, returns the value scale linearly interpolated. If the
                        option is discrete e.g. a classification, returns the closest value scale possible
        :param returntype: default is 'value', function will return a single y value for the input x, sometimes, users
                        want the bracketing values instead so the function will return two tuples (x1, y1), (x2, y2).
        :return: A value of utility corresponding to the y-scale.
        """
        if option == "continuous":
            if x < self.__xdata[0]:     # Check limits xmin/xmax
                if returntype == "value":
                    return self.__ydata[0]
                elif returntype == "bracket":
                    return (x, self.__ydata[0]), (x, self.__ydata[0])
            elif x > self.__xdata[len(self.__xdata)-1]:
                if returntype == "value":
                    return self.__ydata[len(self.__ydata)-1]
                elif returntype == "bracket":
                    return (x, self.__ydata[len(self.__ydata)-1]), (x, self.__ydata[len(self.__ydata)-1])

            for i in range(len(self.__xdata)-1):
                if self.__xdata[i] < x < self.__xdata[i+1]:       # Greater than current, but less than next
                    x1, x2 = self.__xdata[i:i+2]        # Bracket found, set x1, x2, y1, y2
                    y1, y2 = self.__ydata[i:i+2]
                    if returntype == "value":
                        return float(y1 + (x - x1) * ((y2 - y1)/(x2 - x1)))     # do the linear interpolation
                    elif returntype == "bracket":
                        return (x1, y1), (x2, y2)
                else:
                    continue
        elif option == "discrete":
            try:        # Try to find the classification in the x-data
                return self.__ydata[self.__xdata.index(x)]
            except ValueError:
                return 0.0
        return True
