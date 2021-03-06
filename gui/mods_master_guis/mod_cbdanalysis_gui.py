# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mod_cbdanalysis_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UrbanCentralityGui(object):
    def setupUi(self, UrbanCentralityGui):
        UrbanCentralityGui.setObjectName("UrbanCentralityGui")
        UrbanCentralityGui.resize(634, 639)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/City_icon_(Noun_Project).svg.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UrbanCentralityGui.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(UrbanCentralityGui)
        self.gridLayout.setObjectName("gridLayout")
        self.buttons_widget = QtWidgets.QWidget(UrbanCentralityGui)
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
        self.frame = QtWidgets.QFrame(UrbanCentralityGui)
        self.frame.setMinimumSize(QtCore.QSize(200, 0))
        self.frame.setMaximumSize(QtCore.QSize(200, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.UrbanCentrality = QtWidgets.QTextBrowser(self.frame)
        self.UrbanCentrality.setMinimumSize(QtCore.QSize(200, 0))
        self.UrbanCentrality.setMaximumSize(QtCore.QSize(200, 16777215))
        self.UrbanCentrality.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.UrbanCentrality.setFrameShadow(QtWidgets.QFrame.Plain)
        self.UrbanCentrality.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.UrbanCentrality.setObjectName("UrbanCentrality")
        self.verticalLayout_6.addWidget(self.UrbanCentrality)
        self.img = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img.sizePolicy().hasHeightForWidth())
        self.img.setSizePolicy(sizePolicy)
        self.img.setMinimumSize(QtCore.QSize(200, 120))
        self.img.setMaximumSize(QtCore.QSize(200, 120))
        self.img.setText("")
        self.img.setPixmap(QtGui.QPixmap(":/mod_imgs/module_imgs/mod_urbancentrality.jpg"))
        self.img.setObjectName("img")
        self.verticalLayout_6.addWidget(self.img)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(UrbanCentralityGui)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 2)
        self.widget = QtWidgets.QWidget(UrbanCentralityGui)
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
        self.parameters = QtWidgets.QWidget(UrbanCentralityGui)
        self.parameters.setObjectName("parameters")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.parameters)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtWidgets.QLabel(self.parameters)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.asset_col_title = QtWidgets.QLabel(self.parameters)
        self.asset_col_title.setObjectName("asset_col_title")
        self.verticalLayout.addWidget(self.asset_col_title)
        self.gridname_widget = QtWidgets.QWidget(self.parameters)
        self.gridname_widget.setObjectName("gridname_widget")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.gridname_widget)
        self.gridLayout_7.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.assetcol_combo = QtWidgets.QComboBox(self.gridname_widget)
        self.assetcol_combo.setObjectName("assetcol_combo")
        self.assetcol_combo.addItem("")
        self.gridLayout_7.addWidget(self.assetcol_combo, 0, 1, 1, 1)
        self.gridname_lbl = QtWidgets.QLabel(self.gridname_widget)
        self.gridname_lbl.setMinimumSize(QtCore.QSize(100, 0))
        self.gridname_lbl.setMaximumSize(QtCore.QSize(100, 16777215))
        self.gridname_lbl.setObjectName("gridname_lbl")
        self.gridLayout_7.addWidget(self.gridname_lbl, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.gridname_widget)
        self.cbd_title = QtWidgets.QLabel(self.parameters)
        self.cbd_title.setObjectName("cbd_title")
        self.verticalLayout.addWidget(self.cbd_title)
        self.descr = QtWidgets.QLabel(self.parameters)
        self.descr.setMinimumSize(QtCore.QSize(0, 0))
        self.descr.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.descr.setWordWrap(True)
        self.descr.setObjectName("descr")
        self.verticalLayout.addWidget(self.descr)
        self.define_cbd_widget = QtWidgets.QWidget(self.parameters)
        self.define_cbd_widget.setObjectName("define_cbd_widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.define_cbd_widget)
        self.gridLayout_2.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cbdlong_lbl = QtWidgets.QLabel(self.define_cbd_widget)
        self.cbdlong_lbl.setObjectName("cbdlong_lbl")
        self.gridLayout_2.addWidget(self.cbdlong_lbl, 7, 3, 1, 1)
        self.cbdlat_box = QtWidgets.QLineEdit(self.define_cbd_widget)
        self.cbdlat_box.setMinimumSize(QtCore.QSize(100, 0))
        self.cbdlat_box.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cbdlat_box.setObjectName("cbdlat_box")
        self.gridLayout_2.addWidget(self.cbdlat_box, 7, 1, 1, 1)
        self.cbdlat_lbl = QtWidgets.QLabel(self.define_cbd_widget)
        self.cbdlat_lbl.setObjectName("cbdlat_lbl")
        self.gridLayout_2.addWidget(self.cbdlat_lbl, 7, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 2, 0, 1, 1)
        self.cbdname_lbl = QtWidgets.QLabel(self.define_cbd_widget)
        self.cbdname_lbl.setObjectName("cbdname_lbl")
        self.gridLayout_2.addWidget(self.cbdname_lbl, 5, 0, 1, 1)
        self.cbdlong_box = QtWidgets.QLineEdit(self.define_cbd_widget)
        self.cbdlong_box.setMinimumSize(QtCore.QSize(100, 0))
        self.cbdlong_box.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cbdlong_box.setObjectName("cbdlong_box")
        self.gridLayout_2.addWidget(self.cbdlong_box, 7, 4, 1, 1)
        self.cbdname_line = QtWidgets.QLineEdit(self.define_cbd_widget)
        self.cbdname_line.setObjectName("cbdname_line")
        self.gridLayout_2.addWidget(self.cbdname_line, 5, 1, 1, 4)
        self.cbdmanual_radio = QtWidgets.QRadioButton(self.define_cbd_widget)
        self.cbdmanual_radio.setObjectName("cbdmanual_radio")
        self.gridLayout_2.addWidget(self.cbdmanual_radio, 4, 0, 1, 5)
        self.city_combo = QtWidgets.QComboBox(self.define_cbd_widget)
        self.city_combo.setObjectName("city_combo")
        self.city_combo.addItem("")
        self.gridLayout_2.addWidget(self.city_combo, 3, 1, 1, 4)
        self.country_combo = QtWidgets.QComboBox(self.define_cbd_widget)
        self.country_combo.setObjectName("country_combo")
        self.country_combo.addItem("")
        self.gridLayout_2.addWidget(self.country_combo, 2, 1, 1, 4)
        self.cbdknown_radio = QtWidgets.QRadioButton(self.define_cbd_widget)
        self.cbdknown_radio.setObjectName("cbdknown_radio")
        self.gridLayout_2.addWidget(self.cbdknown_radio, 1, 0, 1, 5)
        spacerItem2 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 3, 0, 1, 1)
        self.verticalLayout.addWidget(self.define_cbd_widget)
        self.widget_3 = QtWidgets.QWidget(self.parameters)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.add = QtWidgets.QPushButton(self.widget_3)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/add-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add.setIcon(icon5)
        self.add.setObjectName("add")
        self.horizontalLayout_3.addWidget(self.add)
        self.remove = QtWidgets.QPushButton(self.widget_3)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove.setIcon(icon6)
        self.remove.setObjectName("remove")
        self.horizontalLayout_3.addWidget(self.remove)
        self.reset = QtWidgets.QPushButton(self.widget_3)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/Refresh-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reset.setIcon(icon7)
        self.reset.setObjectName("reset")
        self.horizontalLayout_3.addWidget(self.reset)
        self.verticalLayout.addWidget(self.widget_3)
        self.urbanareas_table = QtWidgets.QTableWidget(self.parameters)
        self.urbanareas_table.setFrameShape(QtWidgets.QFrame.Box)
        self.urbanareas_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.urbanareas_table.setProperty("showDropIndicator", False)
        self.urbanareas_table.setDragDropOverwriteMode(False)
        self.urbanareas_table.setAlternatingRowColors(False)
        self.urbanareas_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.urbanareas_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.urbanareas_table.setRowCount(1)
        self.urbanareas_table.setObjectName("urbanareas_table")
        self.urbanareas_table.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.urbanareas_table.setItem(0, 2, item)
        self.urbanareas_table.horizontalHeader().setVisible(True)
        self.urbanareas_table.horizontalHeader().setCascadingSectionResizes(False)
        self.urbanareas_table.horizontalHeader().setDefaultSectionSize(120)
        self.urbanareas_table.horizontalHeader().setHighlightSections(False)
        self.urbanareas_table.horizontalHeader().setMinimumSectionSize(50)
        self.urbanareas_table.horizontalHeader().setStretchLastSection(True)
        self.urbanareas_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.urbanareas_table)
        self.distance_widget = QtWidgets.QWidget(self.parameters)
        self.distance_widget.setObjectName("distance_widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.distance_widget)
        self.gridLayout_3.setContentsMargins(0, 0, -1, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.ignore_distance_spin = QtWidgets.QDoubleSpinBox(self.distance_widget)
        self.ignore_distance_spin.setDecimals(1)
        self.ignore_distance_spin.setMinimum(-1.0)
        self.ignore_distance_spin.setMaximum(200.0)
        self.ignore_distance_spin.setProperty("value", 50.0)
        self.ignore_distance_spin.setObjectName("ignore_distance_spin")
        self.gridLayout_3.addWidget(self.ignore_distance_spin, 1, 1, 1, 1)
        self.ignore_distance_check = QtWidgets.QCheckBox(self.distance_widget)
        self.ignore_distance_check.setObjectName("ignore_distance_check")
        self.gridLayout_3.addWidget(self.ignore_distance_check, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.distance_widget)
        self.construct_gradient_check = QtWidgets.QCheckBox(self.parameters)
        self.construct_gradient_check.setObjectName("construct_gradient_check")
        self.verticalLayout.addWidget(self.construct_gradient_check)
        self.generate_map_check = QtWidgets.QCheckBox(self.parameters)
        self.generate_map_check.setObjectName("generate_map_check")
        self.verticalLayout.addWidget(self.generate_map_check)
        self.line = QtWidgets.QFrame(self.parameters)
        self.line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.gridLayout.addWidget(self.parameters, 0, 1, 1, 1)
        self.line_3 = QtWidgets.QFrame(UrbanCentralityGui)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 3, 0, 1, 2)

        self.retranslateUi(UrbanCentralityGui)
        self.close_button.clicked.connect(UrbanCentralityGui.reject)
        QtCore.QMetaObject.connectSlotsByName(UrbanCentralityGui)
        UrbanCentralityGui.setTabOrder(self.UrbanCentrality, self.assetcol_combo)
        UrbanCentralityGui.setTabOrder(self.assetcol_combo, self.cbdknown_radio)
        UrbanCentralityGui.setTabOrder(self.cbdknown_radio, self.country_combo)
        UrbanCentralityGui.setTabOrder(self.country_combo, self.city_combo)
        UrbanCentralityGui.setTabOrder(self.city_combo, self.cbdmanual_radio)
        UrbanCentralityGui.setTabOrder(self.cbdmanual_radio, self.cbdname_line)
        UrbanCentralityGui.setTabOrder(self.cbdname_line, self.cbdlat_box)
        UrbanCentralityGui.setTabOrder(self.cbdlat_box, self.cbdlong_box)
        UrbanCentralityGui.setTabOrder(self.cbdlong_box, self.add)
        UrbanCentralityGui.setTabOrder(self.add, self.remove)
        UrbanCentralityGui.setTabOrder(self.remove, self.reset)
        UrbanCentralityGui.setTabOrder(self.reset, self.urbanareas_table)
        UrbanCentralityGui.setTabOrder(self.urbanareas_table, self.ignore_distance_check)
        UrbanCentralityGui.setTabOrder(self.ignore_distance_check, self.ignore_distance_spin)
        UrbanCentralityGui.setTabOrder(self.ignore_distance_spin, self.construct_gradient_check)
        UrbanCentralityGui.setTabOrder(self.construct_gradient_check, self.generate_map_check)
        UrbanCentralityGui.setTabOrder(self.generate_map_check, self.run_button)
        UrbanCentralityGui.setTabOrder(self.run_button, self.ok_button)
        UrbanCentralityGui.setTabOrder(self.ok_button, self.close_button)
        UrbanCentralityGui.setTabOrder(self.close_button, self.help_button)

    def retranslateUi(self, UrbanCentralityGui):
        _translate = QtCore.QCoreApplication.translate
        UrbanCentralityGui.setWindowTitle(_translate("UrbanCentralityGui", "Urban Centrality Analysis"))
        self.ok_button.setWhatsThis(_translate("UrbanCentralityGui", "<html><head/><body><p>Resets all parameters of this module in the current \'scenario time step\' to the default values.</p></body></html>"))
        self.ok_button.setText(_translate("UrbanCentralityGui", "OK"))
        self.close_button.setText(_translate("UrbanCentralityGui", "Close"))
        self.help_button.setText(_translate("UrbanCentralityGui", "Help"))
        self.UrbanCentrality.setHtml(_translate("UrbanCentralityGui", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">Urban Centrality Analysis</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Maps out distances of every simulation grid cell to the nearest urban centre as indicated by the user. Allows identification of monocentric or multi-centric nature of the case study. Say, for example, that several key activity districts are planned around your case study. This analysis reveals which sections of the case study will likely cluster around which activity district.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Pre-requisites: Pre-defined simulation grid, population mapping</span></p></body></html>"))
        self.run_button.setText(_translate("UrbanCentralityGui", "Run"))
        self.title.setText(_translate("UrbanCentralityGui", "<html><head/><body><p><span style=\" font-size:9pt; font-weight:600;\">SETTINGS</span></p></body></html>"))
        self.asset_col_title.setText(_translate("UrbanCentralityGui", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Target Asset Collection</span></p></body></html>"))
        self.assetcol_combo.setItemText(0, _translate("UrbanCentralityGui", "(select asset collection)"))
        self.gridname_lbl.setWhatsThis(_translate("UrbanCentralityGui", "Width of the square cell in the city grid in metres"))
        self.gridname_lbl.setText(_translate("UrbanCentralityGui", "Select collection:"))
        self.cbd_title.setText(_translate("UrbanCentralityGui", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Parameters for Urban Centrality Analysis</span></p></body></html>"))
        self.descr.setWhatsThis(_translate("UrbanCentralityGui", "Width of the square cell in the city grid in metres"))
        self.descr.setText(_translate("UrbanCentralityGui", "Create a list of key districts to be used in mapping, enter details and add them to the table."))
        self.cbdlong_lbl.setText(_translate("UrbanCentralityGui", "<html><head/><body><p>Longitude (X):</p></body></html>"))
        self.cbdlat_box.setToolTip(_translate("UrbanCentralityGui", "Units of decimal degrees"))
        self.cbdlat_lbl.setText(_translate("UrbanCentralityGui", "<html><head/><body><p align=\"right\">Latitude (Y):</p></body></html>"))
        self.cbdname_lbl.setText(_translate("UrbanCentralityGui", "<html><head/><body><p align=\"right\">Name:</p></body></html>"))
        self.cbdlong_box.setToolTip(_translate("UrbanCentralityGui", "Units of decimal degrees."))
        self.cbdname_line.setToolTip(_translate("UrbanCentralityGui", "Units of decimal degrees"))
        self.cbdmanual_radio.setToolTip(_translate("UrbanCentralityGui", "Enter the coordinates of your city\'s CBD manually. Use decimal degrees."))
        self.cbdmanual_radio.setText(_translate("UrbanCentralityGui", "Manually define an activity district"))
        self.city_combo.setItemText(0, _translate("UrbanCentralityGui", "(select city)"))
        self.country_combo.setItemText(0, _translate("UrbanCentralityGui", "(select country)"))
        self.cbdknown_radio.setToolTip(_translate("UrbanCentralityGui", "Choose the nearest city if your case study is within its metropolitan region."))
        self.cbdknown_radio.setText(_translate("UrbanCentralityGui", "Select from known list of cities based on country"))
        self.add.setToolTip(_translate("UrbanCentralityGui", "<html><head/><body><p>Add boundary to the list</p></body></html>"))
        self.add.setText(_translate("UrbanCentralityGui", "Add"))
        self.remove.setToolTip(_translate("UrbanCentralityGui", "<html><head/><body><p>Remove selected table entry from the list</p></body></html>"))
        self.remove.setText(_translate("UrbanCentralityGui", "Remove"))
        self.reset.setToolTip(_translate("UrbanCentralityGui", "<html><head/><body><p>Remove selected table entry from the list</p></body></html>"))
        self.reset.setText(_translate("UrbanCentralityGui", "Reset"))
        self.urbanareas_table.setSortingEnabled(True)
        item = self.urbanareas_table.horizontalHeaderItem(0)
        item.setText(_translate("UrbanCentralityGui", "Name"))
        item = self.urbanareas_table.horizontalHeaderItem(1)
        item.setText(_translate("UrbanCentralityGui", "X-coord (Long.)"))
        item = self.urbanareas_table.horizontalHeaderItem(2)
        item.setText(_translate("UrbanCentralityGui", "Y-coord (Lat.)"))
        __sortingEnabled = self.urbanareas_table.isSortingEnabled()
        self.urbanareas_table.setSortingEnabled(False)
        item = self.urbanareas_table.item(0, 0)
        item.setText(_translate("UrbanCentralityGui", "Zurich"))
        item = self.urbanareas_table.item(0, 1)
        item.setText(_translate("UrbanCentralityGui", "11.111"))
        item = self.urbanareas_table.item(0, 2)
        item.setText(_translate("UrbanCentralityGui", "11.111"))
        self.urbanareas_table.setSortingEnabled(__sortingEnabled)
        self.ignore_distance_spin.setSuffix(_translate("UrbanCentralityGui", " km"))
        self.ignore_distance_check.setToolTip(_translate("UrbanCentralityGui", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.ignore_distance_check.setWhatsThis(_translate("UrbanCentralityGui", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.ignore_distance_check.setText(_translate("UrbanCentralityGui", "Ignore areas beyond a specific distance from urban centre"))
        self.construct_gradient_check.setToolTip(_translate("UrbanCentralityGui", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.construct_gradient_check.setWhatsThis(_translate("UrbanCentralityGui", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.construct_gradient_check.setText(_translate("UrbanCentralityGui", "Construct urban-rural population gradients"))
        self.generate_map_check.setToolTip(_translate("UrbanCentralityGui", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.generate_map_check.setWhatsThis(_translate("UrbanCentralityGui", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.generate_map_check.setText(_translate("UrbanCentralityGui", "Generate proximity map of designated urban centres"))
from .. import ubeats_rc
