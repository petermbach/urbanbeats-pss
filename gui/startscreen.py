# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'startscreen.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StartDialog(object):
    def setupUi(self, StartDialog):
        StartDialog.setObjectName("StartDialog")
        StartDialog.resize(600, 640)
        StartDialog.setMinimumSize(QtCore.QSize(600, 640))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../ubeatsicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        StartDialog.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(StartDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.MainWidget = QtWidgets.QWidget(StartDialog)
        self.MainWidget.setMinimumSize(QtCore.QSize(550, 0))
        self.MainWidget.setObjectName("MainWidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.MainWidget)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.title = QtWidgets.QWidget(self.MainWidget)
        self.title.setObjectName("title")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.title)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.title_text = QtWidgets.QLabel(self.title)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.title_text.setFont(font)
        self.title_text.setObjectName("title_text")
        self.verticalLayout_6.addWidget(self.title_text)
        self.verticalLayout_5.addWidget(self.title)
        self.subtitle = QtWidgets.QWidget(self.MainWidget)
        self.subtitle.setObjectName("subtitle")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.subtitle)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.subtitle_text = QtWidgets.QLabel(self.subtitle)
        self.subtitle_text.setObjectName("subtitle_text")
        self.verticalLayout_7.addWidget(self.subtitle_text)
        self.verticalLayout_5.addWidget(self.subtitle)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.NewProject_Widget = QtWidgets.QWidget(self.MainWidget)
        self.NewProject_Widget.setObjectName("NewProject_Widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.NewProject_Widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.NewProject_button = QtWidgets.QPushButton(self.NewProject_Widget)
        self.NewProject_button.setMinimumSize(QtCore.QSize(80, 80))
        self.NewProject_button.setMaximumSize(QtCore.QSize(80, 80))
        self.NewProject_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/new-file-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.NewProject_button.setIcon(icon1)
        self.NewProject_button.setIconSize(QtCore.QSize(50, 50))
        self.NewProject_button.setObjectName("NewProject_button")
        self.horizontalLayout_2.addWidget(self.NewProject_button)
        self.NewProject_description = QtWidgets.QFrame(self.NewProject_Widget)
        self.NewProject_description.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.NewProject_description.setFrameShadow(QtWidgets.QFrame.Raised)
        self.NewProject_description.setObjectName("NewProject_description")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.NewProject_description)
        self.verticalLayout.setObjectName("verticalLayout")
        self.NewProject_lbl = QtWidgets.QLabel(self.NewProject_description)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.NewProject_lbl.setFont(font)
        self.NewProject_lbl.setObjectName("NewProject_lbl")
        self.verticalLayout.addWidget(self.NewProject_lbl)
        self.NewProject_lbl2 = QtWidgets.QLabel(self.NewProject_description)
        self.NewProject_lbl2.setObjectName("NewProject_lbl2")
        self.verticalLayout.addWidget(self.NewProject_lbl2)
        self.NewProject_lbl3 = QtWidgets.QLabel(self.NewProject_description)
        self.NewProject_lbl3.setObjectName("NewProject_lbl3")
        self.verticalLayout.addWidget(self.NewProject_lbl3)
        self.horizontalLayout_2.addWidget(self.NewProject_description)
        self.verticalLayout_5.addWidget(self.NewProject_Widget)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem2)
        self.OpenProject_Widget = QtWidgets.QWidget(self.MainWidget)
        self.OpenProject_Widget.setObjectName("OpenProject_Widget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.OpenProject_Widget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.OpenProject_button = QtWidgets.QPushButton(self.OpenProject_Widget)
        self.OpenProject_button.setMinimumSize(QtCore.QSize(80, 80))
        self.OpenProject_button.setMaximumSize(QtCore.QSize(80, 80))
        self.OpenProject_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/open-file-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.OpenProject_button.setIcon(icon2)
        self.OpenProject_button.setIconSize(QtCore.QSize(50, 50))
        self.OpenProject_button.setObjectName("OpenProject_button")
        self.horizontalLayout_3.addWidget(self.OpenProject_button)
        self.OpenProject_description = QtWidgets.QFrame(self.OpenProject_Widget)
        self.OpenProject_description.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.OpenProject_description.setFrameShadow(QtWidgets.QFrame.Raised)
        self.OpenProject_description.setObjectName("OpenProject_description")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.OpenProject_description)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.OpenProject_lbl = QtWidgets.QLabel(self.OpenProject_description)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.OpenProject_lbl.setFont(font)
        self.OpenProject_lbl.setObjectName("OpenProject_lbl")
        self.verticalLayout_2.addWidget(self.OpenProject_lbl)
        self.OpenProject_lbl2 = QtWidgets.QLabel(self.OpenProject_description)
        self.OpenProject_lbl2.setObjectName("OpenProject_lbl2")
        self.verticalLayout_2.addWidget(self.OpenProject_lbl2)
        self.OpenProject_lbl3 = QtWidgets.QLabel(self.OpenProject_description)
        self.OpenProject_lbl3.setObjectName("OpenProject_lbl3")
        self.verticalLayout_2.addWidget(self.OpenProject_lbl3)
        self.horizontalLayout_3.addWidget(self.OpenProject_description)
        self.verticalLayout_5.addWidget(self.OpenProject_Widget)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem3)
        self.ImportProject_Widget = QtWidgets.QWidget(self.MainWidget)
        self.ImportProject_Widget.setObjectName("ImportProject_Widget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.ImportProject_Widget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ImportProject_button = QtWidgets.QPushButton(self.ImportProject_Widget)
        self.ImportProject_button.setMinimumSize(QtCore.QSize(80, 80))
        self.ImportProject_button.setMaximumSize(QtCore.QSize(80, 80))
        self.ImportProject_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/import-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ImportProject_button.setIcon(icon3)
        self.ImportProject_button.setIconSize(QtCore.QSize(50, 50))
        self.ImportProject_button.setObjectName("ImportProject_button")
        self.horizontalLayout_4.addWidget(self.ImportProject_button)
        self.ImportProject_description = QtWidgets.QFrame(self.ImportProject_Widget)
        self.ImportProject_description.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ImportProject_description.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ImportProject_description.setObjectName("ImportProject_description")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.ImportProject_description)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ImportProject_lbl = QtWidgets.QLabel(self.ImportProject_description)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.ImportProject_lbl.setFont(font)
        self.ImportProject_lbl.setObjectName("ImportProject_lbl")
        self.verticalLayout_3.addWidget(self.ImportProject_lbl)
        self.ImportProject_lbl2 = QtWidgets.QLabel(self.ImportProject_description)
        self.ImportProject_lbl2.setObjectName("ImportProject_lbl2")
        self.verticalLayout_3.addWidget(self.ImportProject_lbl2)
        self.ImportProject_lbl3 = QtWidgets.QLabel(self.ImportProject_description)
        self.ImportProject_lbl3.setObjectName("ImportProject_lbl3")
        self.verticalLayout_3.addWidget(self.ImportProject_lbl3)
        self.horizontalLayout_4.addWidget(self.ImportProject_description)
        self.verticalLayout_5.addWidget(self.ImportProject_Widget)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem4)
        self.VisitWeb_Widget = QtWidgets.QWidget(self.MainWidget)
        self.VisitWeb_Widget.setObjectName("VisitWeb_Widget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.VisitWeb_Widget)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.VisitWeb_button = QtWidgets.QPushButton(self.VisitWeb_Widget)
        self.VisitWeb_button.setMinimumSize(QtCore.QSize(80, 80))
        self.VisitWeb_button.setMaximumSize(QtCore.QSize(80, 80))
        self.VisitWeb_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/Categories-applications-internet-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.VisitWeb_button.setIcon(icon4)
        self.VisitWeb_button.setIconSize(QtCore.QSize(50, 50))
        self.VisitWeb_button.setObjectName("VisitWeb_button")
        self.horizontalLayout_5.addWidget(self.VisitWeb_button)
        self.VisitWeb_description = QtWidgets.QFrame(self.VisitWeb_Widget)
        self.VisitWeb_description.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.VisitWeb_description.setFrameShadow(QtWidgets.QFrame.Raised)
        self.VisitWeb_description.setObjectName("VisitWeb_description")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.VisitWeb_description)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.VisitWeb_lbl = QtWidgets.QLabel(self.VisitWeb_description)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.VisitWeb_lbl.setFont(font)
        self.VisitWeb_lbl.setObjectName("VisitWeb_lbl")
        self.verticalLayout_4.addWidget(self.VisitWeb_lbl)
        self.VisitWeb_lbl3 = QtWidgets.QLabel(self.VisitWeb_description)
        self.VisitWeb_lbl3.setObjectName("VisitWeb_lbl3")
        self.verticalLayout_4.addWidget(self.VisitWeb_lbl3)
        self.VisitWeb_lbl2 = QtWidgets.QLabel(self.VisitWeb_description)
        self.VisitWeb_lbl2.setObjectName("VisitWeb_lbl2")
        self.verticalLayout_4.addWidget(self.VisitWeb_lbl2)
        self.horizontalLayout_5.addWidget(self.VisitWeb_description)
        self.verticalLayout_5.addWidget(self.VisitWeb_Widget)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem5)
        self.Others_Widget = QtWidgets.QWidget(self.MainWidget)
        self.Others_Widget.setObjectName("Others_Widget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.Others_Widget)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.OptionsButton = QtWidgets.QPushButton(self.Others_Widget)
        self.OptionsButton.setMinimumSize(QtCore.QSize(0, 40))
        self.OptionsButton.setMaximumSize(QtCore.QSize(16777215, 40))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/Settings-icon (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.OptionsButton.setIcon(icon5)
        self.OptionsButton.setIconSize(QtCore.QSize(28, 28))
        self.OptionsButton.setObjectName("OptionsButton")
        self.horizontalLayout_6.addWidget(self.OptionsButton)
        self.HelpButton = QtWidgets.QPushButton(self.Others_Widget)
        self.HelpButton.setMinimumSize(QtCore.QSize(0, 40))
        self.HelpButton.setMaximumSize(QtCore.QSize(16777215, 40))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/Info-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.HelpButton.setIcon(icon6)
        self.HelpButton.setIconSize(QtCore.QSize(28, 28))
        self.HelpButton.setObjectName("HelpButton")
        self.horizontalLayout_6.addWidget(self.HelpButton)
        self.QuitButton = QtWidgets.QPushButton(self.Others_Widget)
        self.QuitButton.setMinimumSize(QtCore.QSize(0, 40))
        self.QuitButton.setMaximumSize(QtCore.QSize(16777215, 40))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/Sign-Shutdown-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.QuitButton.setIcon(icon7)
        self.QuitButton.setIconSize(QtCore.QSize(28, 28))
        self.QuitButton.setObjectName("QuitButton")
        self.horizontalLayout_6.addWidget(self.QuitButton)
        self.verticalLayout_5.addWidget(self.Others_Widget)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem6)
        self.copyright = QtWidgets.QLabel(self.MainWidget)
        self.copyright.setObjectName("copyright")
        self.verticalLayout_5.addWidget(self.copyright)
        self.horizontalLayout.addWidget(self.MainWidget)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem7)

        self.retranslateUi(StartDialog)
        QtCore.QMetaObject.connectSlotsByName(StartDialog)

    def retranslateUi(self, StartDialog):
        _translate = QtCore.QCoreApplication.translate
        StartDialog.setWindowTitle(_translate("StartDialog", "Getting Started..."))
        self.title_text.setText(_translate("StartDialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Welcome to the UrbanBEATS Planning-Support System</span></p></body></html>"))
        self.subtitle_text.setText(_translate("StartDialog", "<html><head/><body><p>Select an option to get started...</p></body></html>"))
        self.NewProject_lbl.setText(_translate("StartDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:12pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Begin a New Project (Setup Wizard) ...</span></p></body></html>"))
        self.NewProject_lbl2.setText(_translate("StartDialog", "Start a new project from scratch, customize simulation type, add"))
        self.NewProject_lbl3.setText(_translate("StartDialog", "data and explore your urban environment."))
        self.OpenProject_lbl.setText(_translate("StartDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:12pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Open an Existing Project Folder ...</span></p></body></html>"))
        self.OpenProject_lbl2.setText(_translate("StartDialog", "Continue from where you left off in a different simulation, update"))
        self.OpenProject_lbl3.setText(_translate("StartDialog", "parameters and discover new insights."))
        self.ImportProject_lbl.setText(_translate("StartDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:12pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Import a Project ...</span></p></body></html>"))
        self.ImportProject_lbl2.setText(_translate("StartDialog", "Import a project into UrbanBEATS from a file or"))
        self.ImportProject_lbl3.setText(_translate("StartDialog", "from UrbanBEATS online."))
        self.VisitWeb_lbl.setText(_translate("StartDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:12pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Visit UrbanBEATSModel.com</span></p></body></html>"))
        self.VisitWeb_lbl3.setText(_translate("StartDialog", "Keep yourself up to date with the latest developments. Learn"))
        self.VisitWeb_lbl2.setText(_translate("StartDialog", "more about the model with the online Wiki."))
        self.OptionsButton.setText(_translate("StartDialog", "Options"))
        self.HelpButton.setText(_translate("StartDialog", "Help"))
        self.QuitButton.setText(_translate("StartDialog", "Quit"))
        self.copyright.setText(_translate("StartDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">(C) 2012 - Peter M. Bach</span></p></body></html>"))

import ubeats_rc