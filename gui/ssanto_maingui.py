# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ssanto_maingui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SSANTOMain(object):
    def setupUi(self, SSANTOMain):
        SSANTOMain.setObjectName("SSANTOMain")
        SSANTOMain.resize(1349, 667)
        SSANTOMain.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        SSANTOMain.setAutoFillBackground(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(SSANTOMain)
        self.verticalLayout.setObjectName("verticalLayout")
        self.centralwidget = QtWidgets.QWidget(SSANTOMain)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(250, 270, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(SSANTOMain)
        self.statusbar.setMaximumSize(QtCore.QSize(16777215, 20))
        self.statusbar.setObjectName("statusbar")
        self.verticalLayout.addWidget(self.statusbar)
        self.statusbar1 = QtWidgets.QStatusBar(SSANTOMain)
        self.statusbar1.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.statusbar1.setObjectName("statusbar1")
        self.toolBar = QtWidgets.QToolBar(SSANTOMain)
        self.toolBar.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.toolBar.setObjectName("toolBar")
        self.actionNew_Scenario = QtWidgets.QAction(SSANTOMain)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/new-file-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew_Scenario.setIcon(icon)
        self.actionNew_Scenario.setObjectName("actionNew_Scenario")
        self.actionNew_Scenario_2 = QtWidgets.QAction(SSANTOMain)
        self.actionNew_Scenario_2.setObjectName("actionNew_Scenario_2")
        self.toolBar.addAction(self.actionNew_Scenario)
        self.toolBar.addSeparator()

        self.retranslateUi(SSANTOMain)
        QtCore.QMetaObject.connectSlotsByName(SSANTOMain)

    def retranslateUi(self, SSANTOMain):
        _translate = QtCore.QCoreApplication.translate
        SSANTOMain.setWindowTitle(_translate("SSANTOMain", "SSANTO"))
        self.pushButton.setText(_translate("SSANTOMain", "Slap Martijn"))
        self.toolBar.setWindowTitle(_translate("SSANTOMain", "toolBar"))
        self.actionNew_Scenario.setText(_translate("SSANTOMain", "New Scenario"))
        self.actionNew_Scenario_2.setText(_translate("SSANTOMain", "New Scenario"))
from . import ubeats_rc
