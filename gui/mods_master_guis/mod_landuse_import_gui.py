# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mod_landuse_import_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Map_Landuse(object):
    def setupUi(self, Map_Landuse):
        Map_Landuse.setObjectName("Map_Landuse")
        Map_Landuse.resize(741, 599)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/region.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Map_Landuse.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Map_Landuse)
        self.gridLayout.setObjectName("gridLayout")
        self.buttons_widget = QtWidgets.QWidget(Map_Landuse)
        self.buttons_widget.setObjectName("buttons_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.buttons_widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ok_button = QtWidgets.QPushButton(self.buttons_widget)
        self.ok_button.setMinimumSize(QtCore.QSize(90, 0))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ok_button.setIcon(icon1)
        self.ok_button.setObjectName("ok_button")
        self.horizontalLayout.addWidget(self.ok_button)
        self.close_button = QtWidgets.QPushButton(self.buttons_widget)
        self.close_button.setMinimumSize(QtCore.QSize(90, 0))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/delete-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.close_button.setIcon(icon2)
        self.close_button.setObjectName("close_button")
        self.horizontalLayout.addWidget(self.close_button)
        self.help_button = QtWidgets.QPushButton(self.buttons_widget)
        self.help_button.setMinimumSize(QtCore.QSize(90, 0))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/Help-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon3)
        self.help_button.setObjectName("help_button")
        self.horizontalLayout.addWidget(self.help_button)
        self.gridLayout.addWidget(self.buttons_widget, 4, 0, 1, 2)
        self.frame = QtWidgets.QFrame(Map_Landuse)
        self.frame.setMinimumSize(QtCore.QSize(200, 0))
        self.frame.setMaximumSize(QtCore.QSize(200, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.description = QtWidgets.QTextBrowser(self.frame)
        self.description.setMinimumSize(QtCore.QSize(200, 0))
        self.description.setMaximumSize(QtCore.QSize(200, 16777215))
        self.description.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.description.setFrameShadow(QtWidgets.QFrame.Plain)
        self.description.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.description.setObjectName("description")
        self.verticalLayout_6.addWidget(self.description)
        self.img = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img.sizePolicy().hasHeightForWidth())
        self.img.setSizePolicy(sizePolicy)
        self.img.setMinimumSize(QtCore.QSize(200, 120))
        self.img.setMaximumSize(QtCore.QSize(200, 120))
        self.img.setText("")
        self.img.setPixmap(QtGui.QPixmap(":/mod_imgs/module_imgs/mod_landuse_import.jpg"))
        self.img.setObjectName("img")
        self.verticalLayout_6.addWidget(self.img)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(Map_Landuse)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 2)
        self.widget = QtWidgets.QWidget(Map_Landuse)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.progressbar = QtWidgets.QProgressBar(self.widget)
        self.progressbar.setMinimumSize(QtCore.QSize(0, 16))
        self.progressbar.setMaximumSize(QtCore.QSize(16777215, 16))
        self.progressbar.setProperty("value", 0)
        self.progressbar.setTextVisible(False)
        self.progressbar.setOrientation(QtCore.Qt.Horizontal)
        self.progressbar.setInvertedAppearance(False)
        self.progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressbar.setObjectName("progressbar")
        self.horizontalLayout_2.addWidget(self.progressbar)
        self.run_button = QtWidgets.QPushButton(self.widget)
        self.run_button.setMinimumSize(QtCore.QSize(90, 0))
        self.run_button.setMaximumSize(QtCore.QSize(90, 16777215))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/Play-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.run_button.setIcon(icon4)
        self.run_button.setObjectName("run_button")
        self.horizontalLayout_2.addWidget(self.run_button)
        self.gridLayout.addWidget(self.widget, 2, 0, 1, 2)
        self.parameters = QtWidgets.QWidget(Map_Landuse)
        self.parameters.setObjectName("parameters")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.parameters)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtWidgets.QLabel(self.parameters)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.assetcol_title = QtWidgets.QLabel(self.parameters)
        self.assetcol_title.setObjectName("assetcol_title")
        self.verticalLayout.addWidget(self.assetcol_title)
        self.gridname_box = QtWidgets.QWidget(self.parameters)
        self.gridname_box.setObjectName("gridname_box")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.gridname_box)
        self.gridLayout_7.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.assetcol_combo = QtWidgets.QComboBox(self.gridname_box)
        self.assetcol_combo.setObjectName("assetcol_combo")
        self.assetcol_combo.addItem("")
        self.gridLayout_7.addWidget(self.assetcol_combo, 0, 1, 1, 1)
        self.assetcol_lbl = QtWidgets.QLabel(self.gridname_box)
        self.assetcol_lbl.setMinimumSize(QtCore.QSize(100, 0))
        self.assetcol_lbl.setMaximumSize(QtCore.QSize(100, 16777215))
        self.assetcol_lbl.setObjectName("assetcol_lbl")
        self.gridLayout_7.addWidget(self.assetcol_lbl, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.gridname_box)
        self.lumap_lbl = QtWidgets.QLabel(self.parameters)
        self.lumap_lbl.setObjectName("lumap_lbl")
        self.verticalLayout.addWidget(self.lumap_lbl)
        self.lumap_widget = QtWidgets.QWidget(self.parameters)
        self.lumap_widget.setObjectName("lumap_widget")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.lumap_widget)
        self.gridLayout_8.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.lu_combo = QtWidgets.QComboBox(self.lumap_widget)
        self.lu_combo.setObjectName("lu_combo")
        self.gridLayout_8.addWidget(self.lu_combo, 0, 1, 1, 2)
        self.lu_lbl = QtWidgets.QLabel(self.lumap_widget)
        self.lu_lbl.setObjectName("lu_lbl")
        self.gridLayout_8.addWidget(self.lu_lbl, 0, 0, 1, 1)
        self.luattr_lbl = QtWidgets.QLabel(self.lumap_widget)
        self.luattr_lbl.setObjectName("luattr_lbl")
        self.gridLayout_8.addWidget(self.luattr_lbl, 1, 0, 1, 1)
        self.luattr_combo = QtWidgets.QComboBox(self.lumap_widget)
        self.luattr_combo.setObjectName("luattr_combo")
        self.luattr_combo.addItem("")
        self.gridLayout_8.addWidget(self.luattr_combo, 1, 1, 1, 2)
        self.verticalLayout.addWidget(self.lumap_widget)
        self.lureclass_title = QtWidgets.QLabel(self.parameters)
        self.lureclass_title.setObjectName("lureclass_title")
        self.verticalLayout.addWidget(self.lureclass_title)
        self.lureclass_check = QtWidgets.QCheckBox(self.parameters)
        self.lureclass_check.setObjectName("lureclass_check")
        self.verticalLayout.addWidget(self.lureclass_check)
        self.lureclass_table = QtWidgets.QTableWidget(self.parameters)
        self.lureclass_table.setMinimumSize(QtCore.QSize(0, 150))
        self.lureclass_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.lureclass_table.setAlternatingRowColors(False)
        self.lureclass_table.setShowGrid(True)
        self.lureclass_table.setGridStyle(QtCore.Qt.SolidLine)
        self.lureclass_table.setRowCount(16)
        self.lureclass_table.setObjectName("lureclass_table")
        self.lureclass_table.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.lureclass_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lureclass_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lureclass_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.lureclass_table.setItem(0, 1, item)
        self.lureclass_table.horizontalHeader().setVisible(True)
        self.lureclass_table.horizontalHeader().setCascadingSectionResizes(False)
        self.lureclass_table.horizontalHeader().setDefaultSectionSize(190)
        self.lureclass_table.horizontalHeader().setSortIndicatorShown(False)
        self.lureclass_table.horizontalHeader().setStretchLastSection(True)
        self.lureclass_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.lureclass_table)
        self.lureclass_widget = QtWidgets.QWidget(self.parameters)
        self.lureclass_widget.setObjectName("lureclass_widget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.lureclass_widget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.lureclass_save_button = QtWidgets.QPushButton(self.lureclass_widget)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/Actions-document-save-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lureclass_save_button.setIcon(icon5)
        self.lureclass_save_button.setObjectName("lureclass_save_button")
        self.horizontalLayout_3.addWidget(self.lureclass_save_button)
        self.lureclass_load_button = QtWidgets.QPushButton(self.lureclass_widget)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/folder-open-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lureclass_load_button.setIcon(icon6)
        self.lureclass_load_button.setObjectName("lureclass_load_button")
        self.horizontalLayout_3.addWidget(self.lureclass_load_button)
        self.lureclass_reset_button = QtWidgets.QPushButton(self.lureclass_widget)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/Refresh-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lureclass_reset_button.setIcon(icon7)
        self.lureclass_reset_button.setObjectName("lureclass_reset_button")
        self.horizontalLayout_3.addWidget(self.lureclass_reset_button)
        self.verticalLayout.addWidget(self.lureclass_widget)
        self.luoptions_lbl = QtWidgets.QLabel(self.parameters)
        self.luoptions_lbl.setObjectName("luoptions_lbl")
        self.verticalLayout.addWidget(self.luoptions_lbl)
        self.luoptions_widget = QtWidgets.QWidget(self.parameters)
        self.luoptions_widget.setObjectName("luoptions_widget")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.luoptions_widget)
        self.gridLayout_9.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.single_landuse_check = QtWidgets.QCheckBox(self.luoptions_widget)
        self.single_landuse_check.setObjectName("single_landuse_check")
        self.gridLayout_9.addWidget(self.single_landuse_check, 1, 0, 1, 2)
        self.patchdelin_check = QtWidgets.QCheckBox(self.luoptions_widget)
        self.patchdelin_check.setObjectName("patchdelin_check")
        self.gridLayout_9.addWidget(self.patchdelin_check, 3, 0, 1, 2)
        self.spatialmetrics_check = QtWidgets.QCheckBox(self.luoptions_widget)
        self.spatialmetrics_check.setObjectName("spatialmetrics_check")
        self.gridLayout_9.addWidget(self.spatialmetrics_check, 4, 0, 1, 2)
        self.verticalLayout.addWidget(self.luoptions_widget)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.line = QtWidgets.QFrame(self.parameters)
        self.line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.gridLayout.addWidget(self.parameters, 0, 1, 1, 1)
        self.line_3 = QtWidgets.QFrame(Map_Landuse)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 3, 0, 1, 2)

        self.retranslateUi(Map_Landuse)
        self.close_button.clicked.connect(Map_Landuse.reject)
        QtCore.QMetaObject.connectSlotsByName(Map_Landuse)

    def retranslateUi(self, Map_Landuse):
        _translate = QtCore.QCoreApplication.translate
        Map_Landuse.setWindowTitle(_translate("Map_Landuse", "Map Land Use to Simulation"))
        self.ok_button.setWhatsThis(_translate("Map_Landuse", "<html><head/><body><p>Resets all parameters of this module in the current \'scenario time step\' to the default values.</p></body></html>"))
        self.ok_button.setText(_translate("Map_Landuse", "OK"))
        self.close_button.setText(_translate("Map_Landuse", "Close"))
        self.help_button.setText(_translate("Map_Landuse", "Help"))
        self.description.setHtml(_translate("Map_Landuse", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">Map Land Use to Simulation Grid</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Map land use information to the simulation grid based on the input land use map. Uses the 16-category UrbanBEATS classification system. Input land use can be either in raster or shapefile format. Also calculates spatial metrics on a cell-by-cell basis for mixed land use representations.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Pre-requisites: A pre-defined Simulation Grid</span></p></body></html>"))
        self.run_button.setText(_translate("Map_Landuse", "Run"))
        self.title.setText(_translate("Map_Landuse", "<html><head/><body><p><span style=\" font-size:9pt; font-weight:600;\">SETTINGS</span></p></body></html>"))
        self.assetcol_title.setText(_translate("Map_Landuse", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Target Asset Collection</span></p></body></html>"))
        self.assetcol_combo.setItemText(0, _translate("Map_Landuse", "(select asset collection)"))
        self.assetcol_lbl.setWhatsThis(_translate("Map_Landuse", "Width of the square cell in the city grid in metres"))
        self.assetcol_lbl.setText(_translate("Map_Landuse", "Select collection:"))
        self.lumap_lbl.setText(_translate("Map_Landuse", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Select Land Use Map</span></p></body></html>"))
        self.lu_lbl.setText(_translate("Map_Landuse", "<html><head/><body><p>Select Land Use Map:</p></body></html>"))
        self.luattr_lbl.setText(_translate("Map_Landuse", "<html><head/><body><p>Attribute:</p></body></html>"))
        self.luattr_combo.setItemText(0, _translate("Map_Landuse", "(select attribute containing classification)"))
        self.lureclass_title.setText(_translate("Map_Landuse", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Land Use Reclassification</span></p></body></html>"))
        self.lureclass_check.setText(_translate("Map_Landuse", "Reclassify input map to UrbanBEATS Land Use Classification"))
        self.lureclass_table.setSortingEnabled(True)
        item = self.lureclass_table.verticalHeaderItem(0)
        item.setText(_translate("Map_Landuse", "1"))
        item = self.lureclass_table.horizontalHeaderItem(0)
        item.setText(_translate("Map_Landuse", "Source Classification"))
        item = self.lureclass_table.horizontalHeaderItem(1)
        item.setText(_translate("Map_Landuse", "UrbanBEATS Classification"))
        __sortingEnabled = self.lureclass_table.isSortingEnabled()
        self.lureclass_table.setSortingEnabled(False)
        self.lureclass_table.setSortingEnabled(__sortingEnabled)
        self.lureclass_save_button.setText(_translate("Map_Landuse", "Save..."))
        self.lureclass_load_button.setText(_translate("Map_Landuse", "Load..."))
        self.lureclass_reset_button.setText(_translate("Map_Landuse", "Reset"))
        self.luoptions_lbl.setText(_translate("Map_Landuse", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Mapping Options (Squares/Hexagons/Geohash Grids only)</span></p></body></html>"))
        self.single_landuse_check.setToolTip(_translate("Map_Landuse", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.single_landuse_check.setText(_translate("Map_Landuse", "Use only single land use per grid cell (dominant category)"))
        self.patchdelin_check.setToolTip(_translate("Map_Landuse", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.patchdelin_check.setText(_translate("Map_Landuse", "Delineate Land Use Patches (patch size and approx. centroid)"))
        self.spatialmetrics_check.setToolTip(_translate("Map_Landuse", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.spatialmetrics_check.setText(_translate("Map_Landuse", "Calculate Spatial Indices per spatial unit (e.g. Shannon Metrics)"))
from .. import ubeats_rc