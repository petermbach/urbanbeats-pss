# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'metadatadialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MetadataDialog(object):
    def setupUi(self, MetadataDialog):
        MetadataDialog.setObjectName("MetadataDialog")
        MetadataDialog.resize(569, 392)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../ubeatsicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MetadataDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(MetadataDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.header = QtWidgets.QWidget(MetadataDialog)
        self.header.setObjectName("header")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.header)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.title_logo = QtWidgets.QLabel(self.header)
        self.title_logo.setMinimumSize(QtCore.QSize(30, 30))
        self.title_logo.setMaximumSize(QtCore.QSize(30, 30))
        self.title_logo.setText("")
        self.title_logo.setPixmap(QtGui.QPixmap(":/icons/map-icon.png"))
        self.title_logo.setScaledContents(True)
        self.title_logo.setObjectName("title_logo")
        self.gridLayout_2.addWidget(self.title_logo, 0, 0, 1, 1)
        self.title = QtWidgets.QLabel(self.header)
        self.title.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.gridLayout_2.addWidget(self.title, 0, 1, 1, 1)
        self.subtitle = QtWidgets.QLabel(self.header)
        self.subtitle.setObjectName("subtitle")
        self.gridLayout_2.addWidget(self.subtitle, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.header)
        self.metadataView = QtWidgets.QTextEdit(MetadataDialog)
        self.metadataView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.metadataView.setObjectName("metadataView")
        self.verticalLayout.addWidget(self.metadataView)
        self.footer = QtWidgets.QWidget(MetadataDialog)
        self.footer.setMinimumSize(QtCore.QSize(0, 38))
        self.footer.setMaximumSize(QtCore.QSize(16777215, 38))
        self.footer.setObjectName("footer")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.footer)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.done_button = QtWidgets.QPushButton(self.footer)
        self.done_button.setObjectName("done_button")
        self.horizontalLayout_2.addWidget(self.done_button)
        self.verticalLayout.addWidget(self.footer)

        self.retranslateUi(MetadataDialog)
        QtCore.QMetaObject.connectSlotsByName(MetadataDialog)
        MetadataDialog.setTabOrder(self.metadataView, self.done_button)

    def retranslateUi(self, MetadataDialog):
        _translate = QtCore.QCoreApplication.translate
        MetadataDialog.setWindowTitle(_translate("MetadataDialog", "Project Log"))
        self.title.setText(_translate("MetadataDialog", "Metadata"))
        self.subtitle.setText(_translate("MetadataDialog", "Further information on data set"))
        self.metadataView.setHtml(_translate("MetadataDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">&lt;none&gt;</span></p></body></html>"))
        self.done_button.setText(_translate("MetadataDialog", "Done"))

import ubeats_rc
