# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'urbanbeatscalibration.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CalibrationViewer(object):
    def setupUi(self, CalibrationViewer):
        CalibrationViewer.setObjectName("CalibrationViewer")
        CalibrationViewer.resize(1300, 680)
        self.horizontalLayout = QtWidgets.QHBoxLayout(CalibrationViewer)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.navigation_widget = QtWidgets.QWidget(CalibrationViewer)
        self.navigation_widget.setObjectName("navigation_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.navigation_widget)
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_frame = QtWidgets.QFrame(self.navigation_widget)
        self.title_frame.setMaximumSize(QtCore.QSize(16777215, 65))
        self.title_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.title_frame.setObjectName("title_frame")
        self.gridLayout = QtWidgets.QGridLayout(self.title_frame)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.gridLayout.setObjectName("gridLayout")
        self.subtitle = QtWidgets.QLabel(self.title_frame)
        self.subtitle.setWordWrap(True)
        self.subtitle.setObjectName("subtitle")
        self.gridLayout.addWidget(self.subtitle, 1, 2, 1, 1)
        self.title = QtWidgets.QLabel(self.title_frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 0, 2, 1, 1)
        self.module_logo = QtWidgets.QLabel(self.title_frame)
        self.module_logo.setMinimumSize(QtCore.QSize(40, 40))
        self.module_logo.setMaximumSize(QtCore.QSize(40, 40))
        self.module_logo.setText("")
        self.module_logo.setPixmap(QtGui.QPixmap(":/icons/chart-search-icon.png"))
        self.module_logo.setScaledContents(True)
        self.module_logo.setObjectName("module_logo")
        self.gridLayout.addWidget(self.module_logo, 0, 0, 3, 1)
        self.verticalLayout.addWidget(self.title_frame)
        self.calibrationSettings = QtWidgets.QWidget(self.navigation_widget)
        self.calibrationSettings.setMinimumSize(QtCore.QSize(350, 0))
        self.calibrationSettings.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.calibrationSettings.setObjectName("calibrationSettings")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.calibrationSettings)
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.calibset_title = QtWidgets.QLabel(self.calibrationSettings)
        self.calibset_title.setObjectName("calibset_title")
        self.verticalLayout_3.addWidget(self.calibset_title)
        self.set_param_lbl = QtWidgets.QLabel(self.calibrationSettings)
        self.set_param_lbl.setObjectName("set_param_lbl")
        self.verticalLayout_3.addWidget(self.set_param_lbl)
        self.set_param_combo = QtWidgets.QComboBox(self.calibrationSettings)
        self.set_param_combo.setObjectName("set_param_combo")
        self.set_param_combo.addItem("")
        self.set_param_combo.addItem("")
        self.set_param_combo.addItem("")
        self.set_param_combo.addItem("")
        self.set_param_combo.addItem("")
        self.set_param_combo.addItem("")
        self.set_param_combo.addItem("")
        self.verticalLayout_3.addWidget(self.set_param_combo)
        self.set_aggregation_combo = QtWidgets.QComboBox(self.calibrationSettings)
        self.set_aggregation_combo.setObjectName("set_aggregation_combo")
        self.set_aggregation_combo.addItem("")
        self.set_aggregation_combo.addItem("")
        self.set_aggregation_combo.addItem("")
        self.set_aggregation_combo.addItem("")
        self.set_aggregation_combo.addItem("")
        self.set_aggregation_combo.addItem("")
        self.verticalLayout_3.addWidget(self.set_aggregation_combo)
        self.set_data_lbl_2 = QtWidgets.QLabel(self.calibrationSettings)
        self.set_data_lbl_2.setObjectName("set_data_lbl_2")
        self.verticalLayout_3.addWidget(self.set_data_lbl_2)
        self.set_gen_lbl = QtWidgets.QLabel(self.calibrationSettings)
        self.set_gen_lbl.setObjectName("set_gen_lbl")
        self.verticalLayout_3.addWidget(self.set_gen_lbl)
        self.set_datasource_combo = QtWidgets.QComboBox(self.calibrationSettings)
        self.set_datasource_combo.setObjectName("set_datasource_combo")
        self.set_datasource_combo.addItem("")
        self.set_datasource_combo.addItem("")
        self.set_datasource_combo.addItem("")
        self.set_datasource_combo.addItem("")
        self.verticalLayout_3.addWidget(self.set_datasource_combo)
        self.set_data_table = QtWidgets.QTableWidget(self.calibrationSettings)
        self.set_data_table.setGridStyle(QtCore.Qt.SolidLine)
        self.set_data_table.setObjectName("set_data_table")
        self.set_data_table.setColumnCount(2)
        self.set_data_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.set_data_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.set_data_table.setHorizontalHeaderItem(1, item)
        self.set_data_table.horizontalHeader().setVisible(True)
        self.set_data_table.verticalHeader().setVisible(False)
        self.verticalLayout_3.addWidget(self.set_data_table)
        self.widget_4 = QtWidgets.QWidget(self.calibrationSettings)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_5.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.set_data_load = QtWidgets.QPushButton(self.widget_4)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/import-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.set_data_load.setIcon(icon)
        self.set_data_load.setObjectName("set_data_load")
        self.horizontalLayout_5.addWidget(self.set_data_load)
        self.set_data_export = QtWidgets.QPushButton(self.widget_4)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/export-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.set_data_export.setIcon(icon1)
        self.set_data_export.setObjectName("set_data_export")
        self.horizontalLayout_5.addWidget(self.set_data_export)
        self.verticalLayout_3.addWidget(self.widget_4)
        self.verticalLayout.addWidget(self.calibrationSettings)
        self.horizontalLayout.addWidget(self.navigation_widget)
        self.widget = QtWidgets.QWidget(CalibrationViewer)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calibrationResults = QtWidgets.QWidget(self.widget)
        self.calibrationResults.setMinimumSize(QtCore.QSize(300, 0))
        self.calibrationResults.setObjectName("calibrationResults")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.calibrationResults)
        self.verticalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.caliboutput_title = QtWidgets.QLabel(self.calibrationResults)
        self.caliboutput_title.setObjectName("caliboutput_title")
        self.verticalLayout_2.addWidget(self.caliboutput_title)
        self.out_box = QtWidgets.QPlainTextEdit(self.calibrationResults)
        self.out_box.setObjectName("out_box")
        self.verticalLayout_2.addWidget(self.out_box)
        self.widget_7 = QtWidgets.QWidget(self.calibrationResults)
        self.widget_7.setObjectName("widget_7")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.widget_7)
        self.horizontalLayout_8.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.out_export = QtWidgets.QPushButton(self.widget_7)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/Reports-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.out_export.setIcon(icon2)
        self.out_export.setObjectName("out_export")
        self.horizontalLayout_8.addWidget(self.out_export)
        self.verticalLayout_2.addWidget(self.widget_7)
        self.set_eval_lbl = QtWidgets.QLabel(self.calibrationResults)
        self.set_eval_lbl.setObjectName("set_eval_lbl")
        self.verticalLayout_2.addWidget(self.set_eval_lbl)
        self.set_eval_nash = QtWidgets.QCheckBox(self.calibrationResults)
        self.set_eval_nash.setObjectName("set_eval_nash")
        self.verticalLayout_2.addWidget(self.set_eval_nash)
        self.set_eval_rmse = QtWidgets.QCheckBox(self.calibrationResults)
        self.set_eval_rmse.setObjectName("set_eval_rmse")
        self.verticalLayout_2.addWidget(self.set_eval_rmse)
        self.set_eval_error = QtWidgets.QCheckBox(self.calibrationResults)
        self.set_eval_error.setObjectName("set_eval_error")
        self.verticalLayout_2.addWidget(self.set_eval_error)
        self.horizontalLayout_2.addWidget(self.calibrationResults)
        self.calibrationWebView = QtWidgets.QWidget(self.widget)
        self.calibrationWebView.setObjectName("calibrationWebView")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.calibrationWebView)
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.calibrationView = QtWebEngineWidgets.QWebEngineView(self.calibrationWebView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibrationView.sizePolicy().hasHeightForWidth())
        self.calibrationView.setSizePolicy(sizePolicy)
        self.calibrationView.setMinimumSize(QtCore.QSize(550, 0))
        self.calibrationView.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.calibrationView.setProperty("url", QtCore.QUrl("about:blank"))
        self.calibrationView.setObjectName("calibrationView")
        self.verticalLayout_4.addWidget(self.calibrationView)
        self.plot_controls_widget = QtWidgets.QWidget(self.calibrationWebView)
        self.plot_controls_widget.setObjectName("plot_controls_widget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.plot_controls_widget)
        self.horizontalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.plottype_lbl = QtWidgets.QLabel(self.plot_controls_widget)
        self.plottype_lbl.setObjectName("plottype_lbl")
        self.horizontalLayout_3.addWidget(self.plottype_lbl)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.plottype_combo = QtWidgets.QComboBox(self.plot_controls_widget)
        self.plottype_combo.setMinimumSize(QtCore.QSize(200, 0))
        self.plottype_combo.setObjectName("plottype_combo")
        self.plottype_combo.addItem("")
        self.plottype_combo.addItem("")
        self.plottype_combo.addItem("")
        self.horizontalLayout_3.addWidget(self.plottype_combo)
        self.set_eval_11line = QtWidgets.QCheckBox(self.plot_controls_widget)
        self.set_eval_11line.setObjectName("set_eval_11line")
        self.horizontalLayout_3.addWidget(self.set_eval_11line)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_4.addWidget(self.plot_controls_widget)
        self.horizontalLayout_2.addWidget(self.calibrationWebView)
        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(CalibrationViewer)
        QtCore.QMetaObject.connectSlotsByName(CalibrationViewer)

    def retranslateUi(self, CalibrationViewer):
        _translate = QtCore.QCoreApplication.translate
        CalibrationViewer.setWindowTitle(_translate("CalibrationViewer", "UrbanBEATS Calibration Viewer"))
        self.subtitle.setText(_translate("CalibrationViewer", "Calibrate Spatial Model Outputs"))
        self.title.setText(_translate("CalibrationViewer", "<html><head/><body><p>Model Calibration Viewer</p></body></html>"))
        self.calibset_title.setText(_translate("CalibrationViewer", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Calibration Settings</span></p></body></html>"))
        self.set_param_lbl.setText(_translate("CalibrationViewer", "Select Parameter and Aggregation Level:"))
        self.set_param_combo.setItemText(0, _translate("CalibrationViewer", "<select parameter to calibrate>"))
        self.set_param_combo.setItemText(1, _translate("CalibrationViewer", "Residential Allotment Count"))
        self.set_param_combo.setItemText(2, _translate("CalibrationViewer", "Residential Dwelling Count"))
        self.set_param_combo.setItemText(3, _translate("CalibrationViewer", "Total Impervious Area"))
        self.set_param_combo.setItemText(4, _translate("CalibrationViewer", "Total Impervious Fraction"))
        self.set_param_combo.setItemText(5, _translate("CalibrationViewer", "Total Residential Roof Area"))
        self.set_param_combo.setItemText(6, _translate("CalibrationViewer", "Water Demand"))
        self.set_aggregation_combo.setItemText(0, _translate("CalibrationViewer", "<select aggregation level>"))
        self.set_aggregation_combo.setItemText(1, _translate("CalibrationViewer", "Case Study Total"))
        self.set_aggregation_combo.setItemText(2, _translate("CalibrationViewer", "Geopolitical"))
        self.set_aggregation_combo.setItemText(3, _translate("CalibrationViewer", "Suburban"))
        self.set_aggregation_combo.setItemText(4, _translate("CalibrationViewer", "Planning Zones"))
        self.set_aggregation_combo.setItemText(5, _translate("CalibrationViewer", "Block by Block"))
        self.set_data_lbl_2.setText(_translate("CalibrationViewer", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Calibration Data</span></p></body></html>"))
        self.set_gen_lbl.setText(_translate("CalibrationViewer", "Create/Select Calibration Data Set:"))
        self.set_datasource_combo.setItemText(0, _translate("CalibrationViewer", "<select data input method or template>"))
        self.set_datasource_combo.setItemText(1, _translate("CalibrationViewer", "User defined..."))
        self.set_datasource_combo.setItemText(2, _translate("CalibrationViewer", "MW MUSIC Guide"))
        self.set_datasource_combo.setItemText(3, _translate("CalibrationViewer", "Sponge Cities Guidelines"))
        self.set_data_table.setSortingEnabled(True)
        item = self.set_data_table.horizontalHeaderItem(0)
        item.setText(_translate("CalibrationViewer", "Region"))
        item = self.set_data_table.horizontalHeaderItem(1)
        item.setText(_translate("CalibrationViewer", "Observed"))
        self.set_data_load.setText(_translate("CalibrationViewer", "Load..."))
        self.set_data_export.setText(_translate("CalibrationViewer", "Export..."))
        self.caliboutput_title.setText(_translate("CalibrationViewer", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Calibration Outputs</span></p></body></html>"))
        self.out_box.setPlainText(_translate("CalibrationViewer", "Results:"))
        self.out_export.setText(_translate("CalibrationViewer", "Save Results..."))
        self.set_eval_lbl.setText(_translate("CalibrationViewer", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Evaluation Statistics:</span></p></body></html>"))
        self.set_eval_nash.setText(_translate("CalibrationViewer", "Nash-Sutcliffe Coefficient"))
        self.set_eval_rmse.setText(_translate("CalibrationViewer", "Root Mean Squared Error"))
        self.set_eval_error.setText(_translate("CalibrationViewer", "Relative Errors"))
        self.plottype_lbl.setText(_translate("CalibrationViewer", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Select Plot Type:</span></p></body></html>"))
        self.plottype_combo.setItemText(0, _translate("CalibrationViewer", "Modelled vs. Observed"))
        self.plottype_combo.setItemText(1, _translate("CalibrationViewer", "Residual Plot"))
        self.plottype_combo.setItemText(2, _translate("CalibrationViewer", "Error Distribution"))
        self.set_eval_11line.setText(_translate("CalibrationViewer", "Display 1:1 Line?"))
from PyQt5 import QtWebEngineWidgets
from . import ubeats_rc
