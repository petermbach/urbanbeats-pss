# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ssanto_maingui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SSANTOMain(object):
    def setupUi(self, SSANTOMain):
        SSANTOMain.setObjectName("SSANTOMain")
        SSANTOMain.resize(1348, 659)
        self.menubar = QtWidgets.QMenuBar(SSANTOMain)
        self.menubar.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy)
        self.menubar.setMinimumSize(QtCore.QSize(0, 0))
        self.menubar.setMaximumSize(QtCore.QSize(1330, 20))
        self.menubar.setAutoFillBackground(False)
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuArmageddon = QtWidgets.QMenu(self.menubar)
        self.menuArmageddon.setObjectName("menuArmageddon")
        self.toolBar = QtWidgets.QToolBar(SSANTOMain)
        self.toolBar.setMaximumSize(QtCore.QSize(16777215, 34))
        self.toolBar.setMovable(True)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
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
        self.actionNew_Scenario = QtWidgets.QAction(SSANTOMain)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/new-file-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew_Scenario.setIcon(icon)
        self.actionNew_Scenario.setObjectName("actionNew_Scenario")
        self.actionNew_Scenario_2 = QtWidgets.QAction(SSANTOMain)
        self.actionNew_Scenario_2.setObjectName("actionNew_Scenario_2")
        self.menuFile.addAction(self.actionNew_Scenario)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuArmageddon.menuAction())
        self.toolBar.addAction(self.actionNew_Scenario)

        self.retranslateUi(SSANTOMain)
        QtCore.QMetaObject.connectSlotsByName(SSANTOMain)

    def retranslateUi(self, SSANTOMain):
        _translate = QtCore.QCoreApplication.translate
        SSANTOMain.setWindowTitle(_translate("SSANTOMain", "SSANTO"))
        self.menuFile.setTitle(_translate("SSANTOMain", "File"))
        self.menuEdit.setTitle(_translate("SSANTOMain", "Edit"))
        self.menuArmageddon.setTitle(_translate("SSANTOMain", "Armageddon"))
        self.toolBar.setWindowTitle(_translate("SSANTOMain", "toolBar"))
        self.pushButton.setText(_translate("SSANTOMain", "Slap Martijn"))
        self.actionNew_Scenario.setText(_translate("SSANTOMain", "New Scenario"))
        self.actionNew_Scenario_2.setText(_translate("SSANTOMain", "New Scenario"))

import ubeats_rc
