# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\newscenario.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewScenarioDialog(object):
    def setupUi(self, NewScenarioDialog):
        NewScenarioDialog.setObjectName("NewScenarioDialog")
        NewScenarioDialog.resize(518, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\../../../../../ubeatsicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        NewScenarioDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(NewScenarioDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_widget = QtWidgets.QWidget(NewScenarioDialog)
        self.title_widget.setObjectName("title_widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.title_widget)
        self.gridLayout_3.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.title_logo = QtWidgets.QLabel(self.title_widget)
        self.title_logo.setMinimumSize(QtCore.QSize(30, 30))
        self.title_logo.setMaximumSize(QtCore.QSize(30, 30))
        self.title_logo.setText("")
        self.title_logo.setPixmap(QtGui.QPixmap(":/icons/Map-icon (1).png"))
        self.title_logo.setScaledContents(True)
        self.title_logo.setObjectName("title_logo")
        self.gridLayout_3.addWidget(self.title_logo, 0, 0, 1, 1)
        self.title = QtWidgets.QLabel(self.title_widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.gridLayout_3.addWidget(self.title, 0, 1, 1, 1)
        self.subtitle = QtWidgets.QLabel(self.title_widget)
        self.subtitle.setObjectName("subtitle")
        self.gridLayout_3.addWidget(self.subtitle, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.title_widget)
        self.name_widget = QtWidgets.QWidget(NewScenarioDialog)
        self.name_widget.setObjectName("name_widget")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.name_widget)
        self.gridLayout_8.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.name_box = QtWidgets.QLineEdit(self.name_widget)
        self.name_box.setEnabled(True)
        self.name_box.setReadOnly(False)
        self.name_box.setObjectName("name_box")
        self.gridLayout_8.addWidget(self.name_box, 0, 1, 1, 1)
        self.name_lbl = QtWidgets.QLabel(self.name_widget)
        self.name_lbl.setObjectName("name_lbl")
        self.gridLayout_8.addWidget(self.name_lbl, 0, 0, 1, 1)
        self.boundary_lbl = QtWidgets.QLabel(self.name_widget)
        self.boundary_lbl.setObjectName("boundary_lbl")
        self.gridLayout_8.addWidget(self.boundary_lbl, 1, 0, 1, 1)
        self.boundary_combo = QtWidgets.QComboBox(self.name_widget)
        self.boundary_combo.setObjectName("boundary_combo")
        self.boundary_combo.addItem("")
        self.gridLayout_8.addWidget(self.boundary_combo, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.name_widget)
        self.setup_widget = QtWidgets.QTabWidget(NewScenarioDialog)
        self.setup_widget.setObjectName("setup_widget")
        self.narrative_tab = QtWidgets.QWidget()
        self.narrative_tab.setObjectName("narrative_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.narrative_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QtWidgets.QWidget(self.narrative_tab)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.narrative_icon = QtWidgets.QLabel(self.widget)
        self.narrative_icon.setMinimumSize(QtCore.QSize(16, 16))
        self.narrative_icon.setMaximumSize(QtCore.QSize(16, 16))
        self.narrative_icon.setText("")
        self.narrative_icon.setPixmap(QtGui.QPixmap(":/icons/pages-brown-icon.png"))
        self.narrative_icon.setScaledContents(True)
        self.narrative_icon.setObjectName("narrative_icon")
        self.horizontalLayout.addWidget(self.narrative_icon)
        self.narrative_lbl = QtWidgets.QLabel(self.widget)
        self.narrative_lbl.setScaledContents(False)
        self.narrative_lbl.setObjectName("narrative_lbl")
        self.horizontalLayout.addWidget(self.narrative_lbl)
        self.verticalLayout_2.addWidget(self.widget)
        self.narrative_box = QtWidgets.QPlainTextEdit(self.narrative_tab)
        self.narrative_box.setMinimumSize(QtCore.QSize(0, 100))
        self.narrative_box.setDocumentTitle("")
        self.narrative_box.setObjectName("narrative_box")
        self.verticalLayout_2.addWidget(self.narrative_box)
        self.metadata_widget = QtWidgets.QWidget(self.narrative_tab)
        self.metadata_widget.setObjectName("metadata_widget")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.metadata_widget)
        self.gridLayout_6.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_6.setSpacing(6)
        self.gridLayout_6.setObjectName("gridLayout_6")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 0, 4, 1, 1)
        self.naming_check = QtWidgets.QCheckBox(self.metadata_widget)
        self.naming_check.setObjectName("naming_check")
        self.gridLayout_6.addWidget(self.naming_check, 2, 3, 1, 2)
        self.simyear_lbl = QtWidgets.QLabel(self.metadata_widget)
        self.simyear_lbl.setMinimumSize(QtCore.QSize(120, 0))
        self.simyear_lbl.setObjectName("simyear_lbl")
        self.gridLayout_6.addWidget(self.simyear_lbl, 0, 1, 1, 1)
        self.naming_line = QtWidgets.QLineEdit(self.metadata_widget)
        self.naming_line.setEnabled(True)
        self.naming_line.setReadOnly(False)
        self.naming_line.setObjectName("naming_line")
        self.gridLayout_6.addWidget(self.naming_line, 1, 3, 1, 2)
        self.startyear_spin = QtWidgets.QSpinBox(self.metadata_widget)
        self.startyear_spin.setMinimumSize(QtCore.QSize(75, 0))
        self.startyear_spin.setMinimum(1900)
        self.startyear_spin.setMaximum(2500)
        self.startyear_spin.setProperty("value", 2018)
        self.startyear_spin.setObjectName("startyear_spin")
        self.gridLayout_6.addWidget(self.startyear_spin, 0, 3, 1, 1)
        self.naming_lbl = QtWidgets.QLabel(self.metadata_widget)
        self.naming_lbl.setObjectName("naming_lbl")
        self.gridLayout_6.addWidget(self.naming_lbl, 1, 1, 1, 1)
        self.simyear_icon = QtWidgets.QLabel(self.metadata_widget)
        self.simyear_icon.setMinimumSize(QtCore.QSize(16, 16))
        self.simyear_icon.setMaximumSize(QtCore.QSize(16, 16))
        self.simyear_icon.setText("")
        self.simyear_icon.setPixmap(QtGui.QPixmap(":/icons/55191-clock-symbol-of-circular-shape.png"))
        self.simyear_icon.setScaledContents(True)
        self.simyear_icon.setObjectName("simyear_icon")
        self.gridLayout_6.addWidget(self.simyear_icon, 0, 0, 1, 1)
        self.naming_icon = QtWidgets.QLabel(self.metadata_widget)
        self.naming_icon.setMinimumSize(QtCore.QSize(16, 16))
        self.naming_icon.setMaximumSize(QtCore.QSize(16, 16))
        self.naming_icon.setText("")
        self.naming_icon.setPixmap(QtGui.QPixmap(":/icons/Reports-icon.png"))
        self.naming_icon.setScaledContents(True)
        self.naming_icon.setObjectName("naming_icon")
        self.gridLayout_6.addWidget(self.naming_icon, 1, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.metadata_widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/Settings-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setup_widget.addTab(self.narrative_tab, icon1, "")
        self.data_tab = QtWidgets.QWidget()
        self.data_tab.setObjectName("data_tab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.data_tab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.datalibrary = QtWidgets.QWidget(self.data_tab)
        self.datalibrary.setObjectName("datalibrary")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.datalibrary)
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.datalibrary_tree = QtWidgets.QTreeWidget(self.datalibrary)
        self.datalibrary_tree.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.datalibrary_tree.setObjectName("datalibrary_tree")
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.datalibrary_tree.headerItem().setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.datalibrary_tree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_0 = QtWidgets.QTreeWidgetItem(self.datalibrary_tree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_0 = QtWidgets.QTreeWidgetItem(self.datalibrary_tree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.verticalLayout_4.addWidget(self.datalibrary_tree)
        self.horizontalLayout_4.addWidget(self.datalibrary)
        self.scenariodata = QtWidgets.QWidget(self.data_tab)
        self.scenariodata.setMinimumSize(QtCore.QSize(200, 0))
        self.scenariodata.setMaximumSize(QtCore.QSize(200, 16777215))
        self.scenariodata.setObjectName("scenariodata")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scenariodata)
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scenariodata_tree = QtWidgets.QTreeWidget(self.scenariodata)
        self.scenariodata_tree.setObjectName("scenariodata_tree")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.scenariodata_tree.headerItem().setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.scenariodata_tree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.scenariodata_tree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.scenariodata_tree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.verticalLayout_3.addWidget(self.scenariodata_tree)
        self.add_to_button = QtWidgets.QPushButton(self.scenariodata)
        self.add_to_button.setObjectName("add_to_button")
        self.verticalLayout_3.addWidget(self.add_to_button)
        self.remove_from_button = QtWidgets.QPushButton(self.scenariodata)
        self.remove_from_button.setObjectName("remove_from_button")
        self.verticalLayout_3.addWidget(self.remove_from_button)
        self.horizontalLayout_4.addWidget(self.scenariodata)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/Misc-Database-3-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setup_widget.addTab(self.data_tab, icon2, "")
        self.verticalLayout.addWidget(self.setup_widget)
        self.footer = QtWidgets.QWidget(NewScenarioDialog)
        self.footer.setMinimumSize(QtCore.QSize(0, 38))
        self.footer.setMaximumSize(QtCore.QSize(16777215, 38))
        self.footer.setObjectName("footer")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.footer)
        self.horizontalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.create_button = QtWidgets.QToolButton(self.footer)
        self.create_button.setMinimumSize(QtCore.QSize(75, 20))
        self.create_button.setObjectName("create_button")
        self.horizontalLayout_2.addWidget(self.create_button)
        self.clear_button = QtWidgets.QToolButton(self.footer)
        self.clear_button.setMinimumSize(QtCore.QSize(75, 0))
        self.clear_button.setObjectName("clear_button")
        self.horizontalLayout_2.addWidget(self.clear_button)
        self.cancel_button = QtWidgets.QPushButton(self.footer)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.verticalLayout.addWidget(self.footer)

        self.retranslateUi(NewScenarioDialog)
        self.setup_widget.setCurrentIndex(0)
        self.cancel_button.clicked.connect(NewScenarioDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewScenarioDialog)
        NewScenarioDialog.setTabOrder(self.name_box, self.datalibrary_tree)
        NewScenarioDialog.setTabOrder(self.datalibrary_tree, self.scenariodata_tree)
        NewScenarioDialog.setTabOrder(self.scenariodata_tree, self.add_to_button)
        NewScenarioDialog.setTabOrder(self.add_to_button, self.remove_from_button)
        NewScenarioDialog.setTabOrder(self.remove_from_button, self.create_button)
        NewScenarioDialog.setTabOrder(self.create_button, self.clear_button)
        NewScenarioDialog.setTabOrder(self.clear_button, self.cancel_button)

    def retranslateUi(self, NewScenarioDialog):
        _translate = QtCore.QCoreApplication.translate
        NewScenarioDialog.setWindowTitle(_translate("NewScenarioDialog", "Add Data..."))
        self.title.setText(_translate("NewScenarioDialog", "Create New Scenario"))
        self.subtitle.setText(_translate("NewScenarioDialog", "Customize key details for the new scenario"))
        self.name_box.setText(_translate("NewScenarioDialog", "(enter scenario name)"))
        self.name_lbl.setWhatsThis(_translate("NewScenarioDialog", "Rainfall time series, obtain data from weather station or climate authority of your city. Time series should be in rainfall depth and have units millimetres."))
        self.name_lbl.setText(_translate("NewScenarioDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Scenario Name:</span></p></body></html>"))
        self.boundary_lbl.setWhatsThis(_translate("NewScenarioDialog", "Rainfall time series, obtain data from weather station or climate authority of your city. Time series should be in rainfall depth and have units millimetres."))
        self.boundary_lbl.setText(_translate("NewScenarioDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Simulation Boundary:</span></p></body></html>"))
        self.boundary_combo.setItemText(0, _translate("NewScenarioDialog", "(select simulation boundary)"))
        self.narrative_lbl.setWhatsThis(_translate("NewScenarioDialog", "Rainfall time series, obtain data from weather station or climate authority of your city. Time series should be in rainfall depth and have units millimetres."))
        self.narrative_lbl.setText(_translate("NewScenarioDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Scenario Description / Narrative</span></p></body></html>"))
        self.narrative_box.setPlainText(_translate("NewScenarioDialog", "(enter scenario description)"))
        self.naming_check.setText(_translate("NewScenarioDialog", "Use scenario name (spaces become underscores)"))
        self.simyear_lbl.setWhatsThis(_translate("NewScenarioDialog", "Rainfall time series, obtain data from weather station or climate authority of your city. Time series should be in rainfall depth and have units millimetres."))
        self.simyear_lbl.setText(_translate("NewScenarioDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Simulation Year:</span></p></body></html>"))
        self.naming_line.setText(_translate("NewScenarioDialog", "(enter a naming convention for outputs)"))
        self.naming_lbl.setWhatsThis(_translate("NewScenarioDialog", "Rainfall time series, obtain data from weather station or climate authority of your city. Time series should be in rainfall depth and have units millimetres."))
        self.naming_lbl.setText(_translate("NewScenarioDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Base Filename:</span></p></body></html>"))
        self.setup_widget.setTabText(self.setup_widget.indexOf(self.narrative_tab), _translate("NewScenarioDialog", "General Info"))
        self.datalibrary_tree.headerItem().setText(0, _translate("NewScenarioDialog", "Project Data Library"))
        __sortingEnabled = self.datalibrary_tree.isSortingEnabled()
        self.datalibrary_tree.setSortingEnabled(False)
        self.datalibrary_tree.topLevelItem(0).setText(0, _translate("NewScenarioDialog", "Spatial Data"))
        self.datalibrary_tree.topLevelItem(0).child(0).setText(0, _translate("NewScenarioDialog", "Boundaries"))
        self.datalibrary_tree.topLevelItem(0).child(0).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(1).setText(0, _translate("NewScenarioDialog", "Built Infrastructure"))
        self.datalibrary_tree.topLevelItem(0).child(1).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(2).setText(0, _translate("NewScenarioDialog", "Elevation"))
        self.datalibrary_tree.topLevelItem(0).child(2).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(3).setText(0, _translate("NewScenarioDialog", "Employment"))
        self.datalibrary_tree.topLevelItem(0).child(3).child(0).setText(0, _translate("NewScenarioDialog", "<none>"))
        self.datalibrary_tree.topLevelItem(0).child(4).setText(0, _translate("NewScenarioDialog", "Land Use"))
        self.datalibrary_tree.topLevelItem(0).child(4).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(5).setText(0, _translate("NewScenarioDialog", "Locality Maps"))
        self.datalibrary_tree.topLevelItem(0).child(5).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(6).setText(0, _translate("NewScenarioDialog", "Overlays"))
        self.datalibrary_tree.topLevelItem(0).child(6).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(7).setText(0, _translate("NewScenarioDialog", "Population"))
        self.datalibrary_tree.topLevelItem(0).child(7).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(8).setText(0, _translate("NewScenarioDialog", "Soil"))
        self.datalibrary_tree.topLevelItem(0).child(8).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(0).child(9).setText(0, _translate("NewScenarioDialog", "Water Bodies"))
        self.datalibrary_tree.topLevelItem(0).child(9).child(0).setText(0, _translate("NewScenarioDialog", "<none>"))
        self.datalibrary_tree.topLevelItem(1).setText(0, _translate("NewScenarioDialog", "Time Series Data"))
        self.datalibrary_tree.topLevelItem(1).child(0).setText(0, _translate("NewScenarioDialog", "Rainfall"))
        self.datalibrary_tree.topLevelItem(1).child(0).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(1).child(1).setText(0, _translate("NewScenarioDialog", "Evapotranspiration"))
        self.datalibrary_tree.topLevelItem(1).child(1).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(1).child(2).setText(0, _translate("NewScenarioDialog", "Solar Radiation"))
        self.datalibrary_tree.topLevelItem(1).child(2).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(1).child(3).setText(0, _translate("NewScenarioDialog", "Temperature"))
        self.datalibrary_tree.topLevelItem(1).child(3).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.topLevelItem(2).setText(0, _translate("NewScenarioDialog", "Qualitative Data"))
        self.datalibrary_tree.topLevelItem(2).child(0).setText(0, _translate("NewScenarioDialog", "<no data>"))
        self.datalibrary_tree.setSortingEnabled(__sortingEnabled)
        self.scenariodata_tree.headerItem().setText(0, _translate("NewScenarioDialog", "Scenario Data Set"))
        __sortingEnabled = self.scenariodata_tree.isSortingEnabled()
        self.scenariodata_tree.setSortingEnabled(False)
        self.scenariodata_tree.topLevelItem(0).setText(0, _translate("NewScenarioDialog", "Spatial Data"))
        self.scenariodata_tree.topLevelItem(0).child(0).setText(0, _translate("NewScenarioDialog", "<none>"))
        self.scenariodata_tree.topLevelItem(1).setText(0, _translate("NewScenarioDialog", "Temporal Data"))
        self.scenariodata_tree.topLevelItem(1).child(0).setText(0, _translate("NewScenarioDialog", "<none>"))
        self.scenariodata_tree.topLevelItem(2).setText(0, _translate("NewScenarioDialog", "Qualitative Data"))
        self.scenariodata_tree.topLevelItem(2).child(0).setText(0, _translate("NewScenarioDialog", "<none>"))
        self.scenariodata_tree.setSortingEnabled(__sortingEnabled)
        self.add_to_button.setText(_translate("NewScenarioDialog", ">> Add to Scenario"))
        self.remove_from_button.setText(_translate("NewScenarioDialog", "<< Remove from Scenario"))
        self.setup_widget.setTabText(self.setup_widget.indexOf(self.data_tab), _translate("NewScenarioDialog", "Scenario Base Data Set"))
        self.create_button.setText(_translate("NewScenarioDialog", "Create"))
        self.clear_button.setText(_translate("NewScenarioDialog", "Clear"))
        self.cancel_button.setText(_translate("NewScenarioDialog", "Cancel"))
from . import ubeats_rc
