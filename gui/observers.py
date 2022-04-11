r"""
@file   main.pyw
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

from PyQt5 import QtCore, QtGui, QtWidgets


class ConsoleObserver(QtCore.QObject):
    """Defines the observer class that will work with the console window in
    UrbanBEATS' main window."""

    updateConsole = QtCore.pyqtSignal(str, name="updateConsole")

    def update_observer(self, textmessage):
        """Emits <updateConsole> signal"""
        self.updateConsole.emit(textmessage)


class ProgressBarObserver(QtCore.QObject):
    """Defines the observer class that will work with the progress bar in the
    UrbanBEATS Main Window."""

    updateProgress = QtCore.pyqtSignal(int, name="updateProgressBar")

    def update_progress(self, value):
        """Emits <updateProgress> signal"""
        self.updateProgress.emit(value)
