# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutdialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(578, 361)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../ubeatsicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.title_box = QtWidgets.QWidget(AboutDialog)
        self.title_box.setObjectName("title_box")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.title_box)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.title_logo = QtWidgets.QLabel(self.title_box)
        self.title_logo.setMinimumSize(QtCore.QSize(30, 30))
        self.title_logo.setMaximumSize(QtCore.QSize(30, 30))
        self.title_logo.setText("")
        self.title_logo.setPixmap(QtGui.QPixmap(":/icons/Info-icon.png"))
        self.title_logo.setScaledContents(True)
        self.title_logo.setObjectName("title_logo")
        self.horizontalLayout_3.addWidget(self.title_logo)
        self.title = QtWidgets.QLabel(self.title_box)
        self.title.setObjectName("title")
        self.horizontalLayout_3.addWidget(self.title)
        self.verticalLayout_3.addWidget(self.title_box)
        self.about_content = QtWidgets.QWidget(AboutDialog)
        self.about_content.setObjectName("about_content")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.about_content)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.devteam_content = QtWidgets.QWidget(self.about_content)
        self.devteam_content.setObjectName("devteam_content")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.devteam_content)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.devteam_lbl = QtWidgets.QLabel(self.devteam_content)
        self.devteam_lbl.setObjectName("devteam_lbl")
        self.verticalLayout_2.addWidget(self.devteam_lbl)
        self.devteam = QtWidgets.QTextEdit(self.devteam_content)
        self.devteam.setMinimumSize(QtCore.QSize(300, 0))
        self.devteam.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.devteam.setObjectName("devteam")
        self.verticalLayout_2.addWidget(self.devteam)
        self.horizontalLayout_2.addWidget(self.devteam_content)
        self.logo_content = QtWidgets.QWidget(self.about_content)
        self.logo_content.setMinimumSize(QtCore.QSize(0, 0))
        self.logo_content.setObjectName("logo_content")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.logo_content)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.logo_lbl = QtWidgets.QLabel(self.logo_content)
        self.logo_lbl.setObjectName("logo_lbl")
        self.verticalLayout_4.addWidget(self.logo_lbl)
        self.label = QtWidgets.QLabel(self.logo_content)
        self.label.setMinimumSize(QtCore.QSize(200, 135))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/images/images/logosplaceholder.png"))
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_2.addWidget(self.logo_content)
        self.verticalLayout_3.addWidget(self.about_content)
        self.footer = QtWidgets.QWidget(AboutDialog)
        self.footer.setObjectName("footer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.footer)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.footer_content = QtWidgets.QWidget(self.footer)
        self.footer_content.setObjectName("footer_content")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.footer_content)
        self.verticalLayout.setObjectName("verticalLayout")
        self.version_number = QtWidgets.QLabel(self.footer_content)
        self.version_number.setObjectName("version_number")
        self.verticalLayout.addWidget(self.version_number)
        self.communication = QtWidgets.QLabel(self.footer_content)
        self.communication.setObjectName("communication")
        self.verticalLayout.addWidget(self.communication)
        self.copyright = QtWidgets.QLabel(self.footer_content)
        self.copyright.setObjectName("copyright")
        self.verticalLayout.addWidget(self.copyright)
        self.horizontalLayout.addWidget(self.footer_content)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.okbutton = QtWidgets.QPushButton(self.footer)
        self.okbutton.setObjectName("okbutton")
        self.horizontalLayout.addWidget(self.okbutton)
        self.verticalLayout_3.addWidget(self.footer)

        self.retranslateUi(AboutDialog)
        self.okbutton.clicked.connect(AboutDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About UrbanBEATS"))
        self.title.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">About the UrbanBEATS Planning-Support System</span></p></body></html>"))
        self.devteam_lbl.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Development Team</span></p></body></html>"))
        self.devteam.setHtml(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Peter M. Bach (Research &amp; Development Lead)</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Research Support:</span><span style=\" font-size:8pt;\"> Ana Deletic, Max Maurer, </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Kefeng Zhang, Veljko Prodanovic, Martijn Kuller, </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Behzad Jamali, Adam Charette-Castonguay, </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Natalia Duque Villareal, Robert Sitzenfrei, </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">David McCarthy, Manfred Kleidorfer</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Technical Support: </span><span style=\" font-size:8pt;\">Nathan Yam</span></p></body></html>"))
        self.logo_lbl.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Supported by:</span></p></body></html>"))
        self.version_number.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">version 2018-a</span></p></body></html>"))
        self.communication.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"www.urbanbeatsmodel.com\"><span style=\" text-decoration: underline; color:#0000ff;\">www.urbanbeatsmodel.com</span></a> - Contact: <a href=\"mailto:peterbach@gmail.com\"><span style=\" text-decoration: underline; color:#0000ff;\">peterbach@gmail.com</span></a></p></body></html>"))
        self.copyright.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">(C) 2014 Peter M. Bach</p></body></html>"))
        self.okbutton.setText(_translate("AboutDialog", "OK"))
import ubeats_rc
