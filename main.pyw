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

# --- CODE STRUCTURE ---
#       1.) CORE LIBRARY IMPORTS
#       2.) URBANBEATS LIBRARY IMPORTS
#       3.) GUI IMPORTS
#       4.) MAIN GUI FUNCTION
#       5.) CONSOLE OBSERVER
#       6.) START SCREEN LAUNCH
# --- --- --- --- --- --- --- --- --- --- ---


# --- CORE LIBRARY IMPORTS ---
import sys, os, time, random, webbrowser, subprocess


# --- URBANBEATS LIBRARY IMPORTS ---


# --- GUI IMPORTS ---
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit
from urbanbeatsmaingui import Ui_MainWindow
from startscreen import Ui_StartDialog

# --- MAIN GUI FUNCTION ---
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)





# --- CONSOLTE OBSERVER ---




# --- START SCREEN LAUNCH ---
class StartScreenLaunch(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_StartDialog()
        self.ui.setupUi(self)


# --- MAIN PROGRAM RUNTIME ---
if __name__ == "__main__":

    #--- OBTAIN AND STORE PATH DATA FOR PROGRAM ---
    UBEATSROOT = os.path.dirname(sys.argv[0])  # Obtains the program's root directory
    UBEATSROOT = UBEATSROOT.encode('string-escape')  # To avoid weird bugs e.g. if someone's folder path

    print UBEATSROOT
    # contains escape characters e.g. \testing or \newSoftware

    random.seed()

    # Someone is launching this directly
    # Create the QApplication
    app = QtWidgets.QApplication(sys.argv)

    splash_matrix = ["1", "2", "3", "4", "5"]
    # Splash Screen
    splash_pix = QtGui.QPixmap("media/splashscreen" + splash_matrix[random.randint(0, 4)] + ".png")
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Simulate something that takes time
    time.sleep(3)

    # Main Window
    main_window = MainWindow()
    main_window.showMaximized()
    splash.finish(main_window)

    # Enter the main loop
    start_screen = StartScreenLaunch()
    #main_window.setOptionsFromConfig(UBEATSROOT)
    #QtCore.QObject.connect(start_screen, QtCore.SIGNAL("startupOpen"), main_window.openExistingProject)
    #QtCore.QObject.connect(start_screen, QtCore.SIGNAL("startupNew"), main_window.beginNewProjectDialog)
    start_screen.exec_()

    sys.exit(app.exec_())
