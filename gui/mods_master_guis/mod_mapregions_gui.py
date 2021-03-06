# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mod_mapregions_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Map_Regions(object):
    def setupUi(self, Map_Regions):
        Map_Regions.setObjectName("Map_Regions")
        Map_Regions.resize(693, 560)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/admin_border.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Map_Regions.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Map_Regions)
        self.gridLayout.setObjectName("gridLayout")
        self.buttons_widget = QtWidgets.QWidget(Map_Regions)
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
        self.frame = QtWidgets.QFrame(Map_Regions)
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
        self.img.setPixmap(QtGui.QPixmap(":/mod_imgs/module_imgs/mod_mapregions.jpg"))
        self.img.setObjectName("img")
        self.verticalLayout_6.addWidget(self.img)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(Map_Regions)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 2)
        self.widget = QtWidgets.QWidget(Map_Regions)
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
        self.parameters = QtWidgets.QWidget(Map_Regions)
        self.parameters.setObjectName("parameters")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.parameters)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtWidgets.QLabel(self.parameters)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.grid_id = QtWidgets.QLabel(self.parameters)
        self.grid_id.setObjectName("grid_id")
        self.verticalLayout.addWidget(self.grid_id)
        self.gridname_box = QtWidgets.QWidget(self.parameters)
        self.gridname_box.setObjectName("gridname_box")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.gridname_box)
        self.gridLayout_7.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.assetcol_combo = QtWidgets.QComboBox(self.gridname_box)
        self.assetcol_combo.setObjectName("assetcol_combo")
        self.assetcol_combo.addItem("")
        self.gridLayout_7.addWidget(self.assetcol_combo, 0, 1, 1, 1)
        self.assetcol_name = QtWidgets.QLabel(self.gridname_box)
        self.assetcol_name.setMinimumSize(QtCore.QSize(100, 0))
        self.assetcol_name.setMaximumSize(QtCore.QSize(100, 16777215))
        self.assetcol_name.setObjectName("assetcol_name")
        self.gridLayout_7.addWidget(self.assetcol_name, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.gridname_box)
        self.boundarydata_title = QtWidgets.QLabel(self.parameters)
        self.boundarydata_title.setObjectName("boundarydata_title")
        self.verticalLayout.addWidget(self.boundarydata_title)
        self.boundarydata_descr = QtWidgets.QLabel(self.parameters)
        self.boundarydata_descr.setMinimumSize(QtCore.QSize(0, 0))
        self.boundarydata_descr.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.boundarydata_descr.setObjectName("boundarydata_descr")
        self.verticalLayout.addWidget(self.boundarydata_descr)
        self.boundarydata_widget = QtWidgets.QWidget(self.parameters)
        self.boundarydata_widget.setObjectName("boundarydata_widget")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.boundarydata_widget)
        self.gridLayout_8.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.simgrid_label_line = QtWidgets.QLineEdit(self.boundarydata_widget)
        self.simgrid_label_line.setText("")
        self.simgrid_label_line.setObjectName("simgrid_label_line")
        self.gridLayout_8.addWidget(self.simgrid_label_line, 3, 1, 1, 1)
        self.boundarydataname_lbl = QtWidgets.QLabel(self.boundarydata_widget)
        self.boundarydataname_lbl.setMinimumSize(QtCore.QSize(100, 0))
        self.boundarydataname_lbl.setMaximumSize(QtCore.QSize(100, 16777215))
        self.boundarydataname_lbl.setObjectName("boundarydataname_lbl")
        self.gridLayout_8.addWidget(self.boundarydataname_lbl, 1, 0, 1, 1)
        self.boundaryatt_lbl = QtWidgets.QLabel(self.boundarydata_widget)
        self.boundaryatt_lbl.setObjectName("boundaryatt_lbl")
        self.gridLayout_8.addWidget(self.boundaryatt_lbl, 2, 0, 1, 1)
        self.boundarycat_lbl = QtWidgets.QLabel(self.boundarydata_widget)
        self.boundarycat_lbl.setMinimumSize(QtCore.QSize(100, 0))
        self.boundarycat_lbl.setMaximumSize(QtCore.QSize(100, 16777215))
        self.boundarycat_lbl.setObjectName("boundarycat_lbl")
        self.gridLayout_8.addWidget(self.boundarycat_lbl, 0, 0, 1, 1)
        self.boundaryatt_combo = QtWidgets.QComboBox(self.boundarydata_widget)
        self.boundaryatt_combo.setObjectName("boundaryatt_combo")
        self.boundaryatt_combo.addItem("")
        self.gridLayout_8.addWidget(self.boundaryatt_combo, 2, 1, 1, 1)
        self.boundarycat_combo = QtWidgets.QComboBox(self.boundarydata_widget)
        self.boundarycat_combo.setObjectName("boundarycat_combo")
        self.boundarycat_combo.addItem("")
        self.boundarycat_combo.addItem(icon, "")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/Simpleicons_Places_building.svg.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.boundarycat_combo.addItem(icon5, "")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/Very-Basic-Design-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.boundarycat_combo.addItem(icon6, "")
        self.gridLayout_8.addWidget(self.boundarycat_combo, 0, 1, 1, 1)
        self.simgrid_label_lbl = QtWidgets.QLabel(self.boundarydata_widget)
        self.simgrid_label_lbl.setObjectName("simgrid_label_lbl")
        self.gridLayout_8.addWidget(self.simgrid_label_lbl, 3, 0, 1, 1)
        self.boundary_combo = QtWidgets.QComboBox(self.boundarydata_widget)
        self.boundary_combo.setObjectName("boundary_combo")
        self.boundary_combo.addItem("")
        self.gridLayout_8.addWidget(self.boundary_combo, 1, 1, 1, 1)
        self.stakeholder_check = QtWidgets.QCheckBox(self.boundarydata_widget)
        self.stakeholder_check.setObjectName("stakeholder_check")
        self.gridLayout_8.addWidget(self.stakeholder_check, 4, 1, 1, 1)
        self.verticalLayout.addWidget(self.boundarydata_widget)
        self.widget_2 = QtWidgets.QWidget(self.parameters)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.add = QtWidgets.QPushButton(self.widget_2)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/add-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add.setIcon(icon7)
        self.add.setObjectName("add")
        self.horizontalLayout_3.addWidget(self.add)
        self.remove = QtWidgets.QPushButton(self.widget_2)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove.setIcon(icon8)
        self.remove.setObjectName("remove")
        self.horizontalLayout_3.addWidget(self.remove)
        self.reset = QtWidgets.QPushButton(self.widget_2)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/Refresh-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reset.setIcon(icon9)
        self.reset.setObjectName("reset")
        self.horizontalLayout_3.addWidget(self.reset)
        self.verticalLayout.addWidget(self.widget_2)
        self.boundarytable = QtWidgets.QTableWidget(self.parameters)
        self.boundarytable.setFrameShape(QtWidgets.QFrame.Box)
        self.boundarytable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.boundarytable.setProperty("showDropIndicator", False)
        self.boundarytable.setDragDropOverwriteMode(False)
        self.boundarytable.setAlternatingRowColors(False)
        self.boundarytable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.boundarytable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.boundarytable.setRowCount(3)
        self.boundarytable.setObjectName("boundarytable")
        self.boundarytable.setColumnCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/owl.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon10)
        self.boundarytable.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.boundarytable.setItem(0, 3, item)
        self.boundarytable.horizontalHeader().setVisible(True)
        self.boundarytable.horizontalHeader().setCascadingSectionResizes(False)
        self.boundarytable.horizontalHeader().setDefaultSectionSize(120)
        self.boundarytable.horizontalHeader().setHighlightSections(False)
        self.boundarytable.horizontalHeader().setMinimumSectionSize(50)
        self.boundarytable.horizontalHeader().setStretchLastSection(True)
        self.boundarytable.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.boundarytable)
        self.line = QtWidgets.QFrame(self.parameters)
        self.line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.gridLayout.addWidget(self.parameters, 0, 1, 1, 1)
        self.line_3 = QtWidgets.QFrame(Map_Regions)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 3, 0, 1, 2)

        self.retranslateUi(Map_Regions)
        self.close_button.clicked.connect(Map_Regions.reject)
        QtCore.QMetaObject.connectSlotsByName(Map_Regions)
        Map_Regions.setTabOrder(self.description, self.assetcol_combo)
        Map_Regions.setTabOrder(self.assetcol_combo, self.boundarycat_combo)
        Map_Regions.setTabOrder(self.boundarycat_combo, self.boundary_combo)
        Map_Regions.setTabOrder(self.boundary_combo, self.boundaryatt_combo)
        Map_Regions.setTabOrder(self.boundaryatt_combo, self.simgrid_label_line)
        Map_Regions.setTabOrder(self.simgrid_label_line, self.stakeholder_check)
        Map_Regions.setTabOrder(self.stakeholder_check, self.add)
        Map_Regions.setTabOrder(self.add, self.remove)
        Map_Regions.setTabOrder(self.remove, self.reset)
        Map_Regions.setTabOrder(self.reset, self.boundarytable)
        Map_Regions.setTabOrder(self.boundarytable, self.run_button)
        Map_Regions.setTabOrder(self.run_button, self.ok_button)
        Map_Regions.setTabOrder(self.ok_button, self.close_button)
        Map_Regions.setTabOrder(self.close_button, self.help_button)

    def retranslateUi(self, Map_Regions):
        _translate = QtCore.QCoreApplication.translate
        Map_Regions.setWindowTitle(_translate("Map_Regions", "Map Regions to Simulation"))
        self.ok_button.setWhatsThis(_translate("Map_Regions", "<html><head/><body><p>Resets all parameters of this module in the current \'scenario time step\' to the default values.</p></body></html>"))
        self.ok_button.setText(_translate("Map_Regions", "OK"))
        self.close_button.setText(_translate("Map_Regions", "Close"))
        self.help_button.setText(_translate("Map_Regions", "Help"))
        self.description.setHtml(_translate("Map_Regions", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">Map Boundaries</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Map key jurisdictional, suburban or planning boundaries onto the simulation, regions can be classed as municipal, suburban, neighbourhood or user-defined planning zones. This enables aggregation of simulation output in later stages by larger districts.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Add multiple boundaries into the table below to be mapped at once to the simulation grid.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Pre-requisites: A pre-defined Simulation Grid</span></p></body></html>"))
        self.run_button.setText(_translate("Map_Regions", "Run"))
        self.title.setText(_translate("Map_Regions", "<html><head/><body><p><span style=\" font-size:9pt; font-weight:600;\">SETTINGS</span></p></body></html>"))
        self.grid_id.setText(_translate("Map_Regions", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Target Asset Collection</span></p></body></html>"))
        self.assetcol_combo.setItemText(0, _translate("Map_Regions", "(select asset collection)"))
        self.assetcol_name.setWhatsThis(_translate("Map_Regions", "Width of the square cell in the city grid in metres"))
        self.assetcol_name.setText(_translate("Map_Regions", "Select collection:"))
        self.boundarydata_title.setText(_translate("Map_Regions", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Select Boundary Data Sets</span></p></body></html>"))
        self.boundarydata_descr.setWhatsThis(_translate("Map_Regions", "Width of the square cell in the city grid in metres"))
        self.boundarydata_descr.setText(_translate("Map_Regions", "Add all boundary data sets you would like to map"))
        self.boundarydataname_lbl.setWhatsThis(_translate("Map_Regions", "Width of the square cell in the city grid in metres"))
        self.boundarydataname_lbl.setText(_translate("Map_Regions", "Data Set Name:"))
        self.boundaryatt_lbl.setText(_translate("Map_Regions", "<html><head/><body><p align=\"right\">Attribute Label Name:</p></body></html>"))
        self.boundarycat_lbl.setWhatsThis(_translate("Map_Regions", "Width of the square cell in the city grid in metres"))
        self.boundarycat_lbl.setText(_translate("Map_Regions", "Boundary Category:"))
        self.boundaryatt_combo.setItemText(0, _translate("Map_Regions", "(select Attribute Name for Labelling)"))
        self.boundarycat_combo.setItemText(0, _translate("Map_Regions", "(select Boundary category)"))
        self.boundarycat_combo.setItemText(1, _translate("Map_Regions", "Jurisdictional Boundaries"))
        self.boundarycat_combo.setItemText(2, _translate("Map_Regions", "Suburban Boundaries"))
        self.boundarycat_combo.setItemText(3, _translate("Map_Regions", "Planning Boundaries"))
        self.simgrid_label_lbl.setText(_translate("Map_Regions", "<html><head/><body><p>Simulation Grid Label:</p></body></html>"))
        self.boundary_combo.setItemText(0, _translate("Map_Regions", "(select Map)"))
        self.stakeholder_check.setText(_translate("Map_Regions", "Designate as Project Stakeholders?"))
        self.add.setToolTip(_translate("Map_Regions", "<html><head/><body><p>Add boundary to the list</p></body></html>"))
        self.add.setText(_translate("Map_Regions", "Add"))
        self.remove.setToolTip(_translate("Map_Regions", "<html><head/><body><p>Remove selected table entry from the list</p></body></html>"))
        self.remove.setText(_translate("Map_Regions", "Remove"))
        self.reset.setToolTip(_translate("Map_Regions", "<html><head/><body><p>Remove selected table entry from the list</p></body></html>"))
        self.reset.setText(_translate("Map_Regions", "Reset"))
        self.boundarytable.setSortingEnabled(True)
        item = self.boundarytable.horizontalHeaderItem(0)
        item.setText(_translate("Map_Regions", "Category Label"))
        item = self.boundarytable.horizontalHeaderItem(1)
        item.setText(_translate("Map_Regions", "Stakeholder"))
        item = self.boundarytable.horizontalHeaderItem(2)
        item.setText(_translate("Map_Regions", "Data Set Name"))
        item = self.boundarytable.horizontalHeaderItem(3)
        item.setText(_translate("Map_Regions", "Attribute"))
        __sortingEnabled = self.boundarytable.isSortingEnabled()
        self.boundarytable.setSortingEnabled(False)
        item = self.boundarytable.item(0, 0)
        item.setText(_translate("Map_Regions", "Label"))
        item = self.boundarytable.item(0, 2)
        item.setText(_translate("Map_Regions", "BLabla.txt"))
        item = self.boundarytable.item(0, 3)
        item.setText(_translate("Map_Regions", "Name"))
        self.boundarytable.setSortingEnabled(__sortingEnabled)
from .. import ubeats_rc
