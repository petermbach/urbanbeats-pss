# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'md_delinblocksgui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Delinblocks_Dialog(object):
    def setupUi(self, Delinblocks_Dialog):
        Delinblocks_Dialog.setObjectName("Delinblocks_Dialog")
        Delinblocks_Dialog.resize(780, 500)
        self.verticalLayout = QtWidgets.QVBoxLayout(Delinblocks_Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_frame = QtWidgets.QFrame(Delinblocks_Dialog)
        self.title_frame.setMaximumSize(QtCore.QSize(16777215, 65))
        self.title_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.title_frame.setObjectName("title_frame")
        self.gridLayout = QtWidgets.QGridLayout(self.title_frame)
        self.gridLayout.setObjectName("gridLayout")
        self.module_logo = QtWidgets.QLabel(self.title_frame)
        self.module_logo.setMinimumSize(QtCore.QSize(40, 40))
        self.module_logo.setMaximumSize(QtCore.QSize(40, 40))
        self.module_logo.setText("")
        self.module_logo.setPixmap(QtGui.QPixmap(":/images/images/md_spatial.png"))
        self.module_logo.setObjectName("module_logo")
        self.gridLayout.addWidget(self.module_logo, 0, 0, 3, 1)
        self.title = QtWidgets.QLabel(self.title_frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 0, 2, 1, 1)
        self.subtitle = QtWidgets.QLabel(self.title_frame)
        self.subtitle.setWordWrap(False)
        self.subtitle.setObjectName("subtitle")
        self.gridLayout.addWidget(self.subtitle, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.title_frame)
        self.title_line = QtWidgets.QFrame(Delinblocks_Dialog)
        self.title_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.title_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.title_line.setObjectName("title_line")
        self.verticalLayout.addWidget(self.title_line)
        self.module_widget = QtWidgets.QWidget(Delinblocks_Dialog)
        self.module_widget.setObjectName("module_widget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.module_widget)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.sidebar_widget = QtWidgets.QWidget(self.module_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidebar_widget.sizePolicy().hasHeightForWidth())
        self.sidebar_widget.setSizePolicy(sizePolicy)
        self.sidebar_widget.setMinimumSize(QtCore.QSize(0, 0))
        self.sidebar_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.sidebar_widget.setObjectName("sidebar_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.sidebar_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sidebar_title = QtWidgets.QLabel(self.sidebar_widget)
        self.sidebar_title.setObjectName("sidebar_title")
        self.verticalLayout_2.addWidget(self.sidebar_title)
        self.year_combo = QtWidgets.QComboBox(self.sidebar_widget)
        self.year_combo.setMinimumSize(QtCore.QSize(100, 0))
        self.year_combo.setObjectName("year_combo")
        self.year_combo.addItem("")
        self.verticalLayout_2.addWidget(self.year_combo)
        self.autofillButton = QtWidgets.QPushButton(self.sidebar_widget)
        self.autofillButton.setObjectName("autofillButton")
        self.verticalLayout_2.addWidget(self.autofillButton)
        self.same_params = QtWidgets.QCheckBox(self.sidebar_widget)
        self.same_params.setObjectName("same_params")
        self.verticalLayout_2.addWidget(self.same_params)
        self.sidebar_line = QtWidgets.QFrame(self.sidebar_widget)
        self.sidebar_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.sidebar_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.sidebar_line.setObjectName("sidebar_line")
        self.verticalLayout_2.addWidget(self.sidebar_line)
        self.module_img = QtWidgets.QLabel(self.sidebar_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.module_img.sizePolicy().hasHeightForWidth())
        self.module_img.setSizePolicy(sizePolicy)
        self.module_img.setMinimumSize(QtCore.QSize(140, 100))
        self.module_img.setMaximumSize(QtCore.QSize(140, 100))
        self.module_img.setText("")
        self.module_img.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_pic.png"))
        self.module_img.setObjectName("module_img")
        self.verticalLayout_2.addWidget(self.module_img)
        self.description = QtWidgets.QTextBrowser(self.sidebar_widget)
        self.description.setMinimumSize(QtCore.QSize(140, 0))
        self.description.setMaximumSize(QtCore.QSize(140, 16777215))
        self.description.setObjectName("description")
        self.verticalLayout_2.addWidget(self.description)
        self.horizontalLayout_6.addWidget(self.sidebar_widget)
        self.parameters = QtWidgets.QTabWidget(self.module_widget)
        self.parameters.setObjectName("parameters")
        self.geometry_tab = QtWidgets.QWidget()
        self.geometry_tab.setObjectName("geometry_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.geometry_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.geometry_scrollArea = QtWidgets.QScrollArea(self.geometry_tab)
        self.geometry_scrollArea.setWidgetResizable(True)
        self.geometry_scrollArea.setObjectName("geometry_scrollArea")
        self.geometry_contents = QtWidgets.QWidget()
        self.geometry_contents.setGeometry(QtCore.QRect(0, 0, 537, 623))
        self.geometry_contents.setObjectName("geometry_contents")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.geometry_contents)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.essential_lbl = QtWidgets.QLabel(self.geometry_contents)
        self.essential_lbl.setObjectName("essential_lbl")
        self.verticalLayout_14.addWidget(self.essential_lbl)
        self.div1_1 = QtWidgets.QFrame(self.geometry_contents)
        self.div1_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.div1_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div1_1.setObjectName("div1_1")
        self.verticalLayout_14.addWidget(self.div1_1)
        self.descr2 = QtWidgets.QLabel(self.geometry_contents)
        self.descr2.setWordWrap(True)
        self.descr2.setObjectName("descr2")
        self.verticalLayout_14.addWidget(self.descr2)
        self.datasets = QtWidgets.QWidget(self.geometry_contents)
        self.datasets.setObjectName("datasets")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.datasets)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.pop_combo = QtWidgets.QComboBox(self.datasets)
        self.pop_combo.setObjectName("pop_combo")
        self.gridLayout_6.addWidget(self.pop_combo, 2, 1, 1, 1)
        self.lu_lbl = QtWidgets.QLabel(self.datasets)
        self.lu_lbl.setObjectName("lu_lbl")
        self.gridLayout_6.addWidget(self.lu_lbl, 1, 0, 1, 1)
        self.pop_fromurbandev = QtWidgets.QCheckBox(self.datasets)
        self.pop_fromurbandev.setObjectName("pop_fromurbandev")
        self.gridLayout_6.addWidget(self.pop_fromurbandev, 2, 2, 1, 1)
        self.lu_combo = QtWidgets.QComboBox(self.datasets)
        self.lu_combo.setObjectName("lu_combo")
        self.gridLayout_6.addWidget(self.lu_combo, 1, 1, 1, 1)
        self.lu_fromurbandev = QtWidgets.QCheckBox(self.datasets)
        self.lu_fromurbandev.setObjectName("lu_fromurbandev")
        self.gridLayout_6.addWidget(self.lu_fromurbandev, 1, 2, 1, 1)
        self.elev_combo = QtWidgets.QComboBox(self.datasets)
        self.elev_combo.setObjectName("elev_combo")
        self.gridLayout_6.addWidget(self.elev_combo, 3, 1, 1, 1)
        self.elev_lbl = QtWidgets.QLabel(self.datasets)
        self.elev_lbl.setObjectName("elev_lbl")
        self.gridLayout_6.addWidget(self.elev_lbl, 3, 0, 1, 1)
        self.pop_lbl = QtWidgets.QLabel(self.datasets)
        self.pop_lbl.setObjectName("pop_lbl")
        self.gridLayout_6.addWidget(self.pop_lbl, 2, 0, 1, 1)
        self.verticalLayout_14.addWidget(self.datasets)
        self.geometry_title = QtWidgets.QLabel(self.geometry_contents)
        self.geometry_title.setObjectName("geometry_title")
        self.verticalLayout_14.addWidget(self.geometry_title)
        self.div1_2 = QtWidgets.QFrame(self.geometry_contents)
        self.div1_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.div1_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div1_2.setObjectName("div1_2")
        self.verticalLayout_14.addWidget(self.div1_2)
        self.geometry_lbl1 = QtWidgets.QLabel(self.geometry_contents)
        self.geometry_lbl1.setWordWrap(True)
        self.geometry_lbl1.setObjectName("geometry_lbl1")
        self.verticalLayout_14.addWidget(self.geometry_lbl1)
        self.geometry_widget = QtWidgets.QWidget(self.geometry_contents)
        self.geometry_widget.setObjectName("geometry_widget")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.geometry_widget)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.rep_lbl = QtWidgets.QLabel(self.geometry_widget)
        self.rep_lbl.setObjectName("rep_lbl")
        self.horizontalLayout_7.addWidget(self.rep_lbl)
        self.rep_combo = QtWidgets.QComboBox(self.geometry_widget)
        self.rep_combo.setMinimumSize(QtCore.QSize(0, 0))
        self.rep_combo.setIconSize(QtCore.QSize(30, 30))
        self.rep_combo.setObjectName("rep_combo")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/images/md_spatial_block.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rep_combo.addItem(icon, "")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/images/md_spatial_hex.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rep_combo.addItem(icon1, "")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/images/md_spatial_patch.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rep_combo.addItem(icon2, "")
        self.horizontalLayout_7.addWidget(self.rep_combo)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.verticalLayout_14.addWidget(self.geometry_widget)
        self.rep_stack = QtWidgets.QStackedWidget(self.geometry_contents)
        self.rep_stack.setObjectName("rep_stack")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.blockrep_title = QtWidgets.QLabel(self.page)
        self.blockrep_title.setObjectName("blockrep_title")
        self.verticalLayout_9.addWidget(self.blockrep_title)
        self.resolution_widget = QtWidgets.QWidget(self.page)
        self.resolution_widget.setObjectName("resolution_widget")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.resolution_widget)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.resolution_lbl_2 = QtWidgets.QLabel(self.resolution_widget)
        self.resolution_lbl_2.setObjectName("resolution_lbl_2")
        self.horizontalLayout_11.addWidget(self.resolution_lbl_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem1)
        self.resolution_spin = QtWidgets.QSpinBox(self.resolution_widget)
        self.resolution_spin.setMinimumSize(QtCore.QSize(100, 0))
        self.resolution_spin.setMinimum(200)
        self.resolution_spin.setMaximum(5000)
        self.resolution_spin.setSingleStep(50)
        self.resolution_spin.setProperty("value", 500)
        self.resolution_spin.setObjectName("resolution_spin")
        self.horizontalLayout_11.addWidget(self.resolution_spin)
        self.resolution_auto = QtWidgets.QCheckBox(self.resolution_widget)
        self.resolution_auto.setObjectName("resolution_auto")
        self.horizontalLayout_11.addWidget(self.resolution_auto)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem2)
        self.verticalLayout_9.addWidget(self.resolution_widget)
        self.neighbourhood_title = QtWidgets.QLabel(self.page)
        self.neighbourhood_title.setObjectName("neighbourhood_title")
        self.verticalLayout_9.addWidget(self.neighbourhood_title)
        self.neighbourhood_lbl = QtWidgets.QLabel(self.page)
        self.neighbourhood_lbl.setWordWrap(True)
        self.neighbourhood_lbl.setObjectName("neighbourhood_lbl")
        self.verticalLayout_9.addWidget(self.neighbourhood_lbl)
        self.blocknhd_widget = QtWidgets.QWidget(self.page)
        self.blocknhd_widget.setObjectName("blocknhd_widget")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.blocknhd_widget)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.img_moore = QtWidgets.QLabel(self.blocknhd_widget)
        self.img_moore.setMinimumSize(QtCore.QSize(50, 50))
        self.img_moore.setMaximumSize(QtCore.QSize(50, 50))
        self.img_moore.setText("")
        self.img_moore.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_moore.png"))
        self.img_moore.setObjectName("img_moore")
        self.horizontalLayout_9.addWidget(self.img_moore)
        self.radio_moore = QtWidgets.QRadioButton(self.blocknhd_widget)
        self.radio_moore.setEnabled(True)
        self.radio_moore.setWhatsThis("")
        self.radio_moore.setCheckable(True)
        self.radio_moore.setObjectName("radio_moore")
        self.horizontalLayout_9.addWidget(self.radio_moore)
        self.img_vonNeu = QtWidgets.QLabel(self.blocknhd_widget)
        self.img_vonNeu.setMinimumSize(QtCore.QSize(50, 50))
        self.img_vonNeu.setMaximumSize(QtCore.QSize(50, 50))
        self.img_vonNeu.setText("")
        self.img_vonNeu.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_vNeumann.png"))
        self.img_vonNeu.setObjectName("img_vonNeu")
        self.horizontalLayout_9.addWidget(self.img_vonNeu)
        self.radio_vonNeu = QtWidgets.QRadioButton(self.blocknhd_widget)
        self.radio_vonNeu.setWhatsThis("")
        self.radio_vonNeu.setChecked(False)
        self.radio_vonNeu.setObjectName("radio_vonNeu")
        self.horizontalLayout_9.addWidget(self.radio_vonNeu)
        self.verticalLayout_9.addWidget(self.blocknhd_widget)
        self.geooptions_lbl = QtWidgets.QLabel(self.page)
        self.geooptions_lbl.setObjectName("geooptions_lbl")
        self.verticalLayout_9.addWidget(self.geooptions_lbl)
        self.spatialindices_check = QtWidgets.QCheckBox(self.page)
        self.spatialindices_check.setObjectName("spatialindices_check")
        self.verticalLayout_9.addWidget(self.spatialindices_check)
        self.patchdelin_check = QtWidgets.QCheckBox(self.page)
        self.patchdelin_check.setObjectName("patchdelin_check")
        self.verticalLayout_9.addWidget(self.patchdelin_check)
        self.rep_stack.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.hexrep_title = QtWidgets.QLabel(self.page_2)
        self.hexrep_title.setEnabled(False)
        self.hexrep_title.setObjectName("hexrep_title")
        self.verticalLayout_11.addWidget(self.hexrep_title)
        self.hexresolution_widget = QtWidgets.QWidget(self.page_2)
        self.hexresolution_widget.setObjectName("hexresolution_widget")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.hexresolution_widget)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.hexsize_lbl = QtWidgets.QLabel(self.hexresolution_widget)
        self.hexsize_lbl.setEnabled(False)
        self.hexsize_lbl.setObjectName("hexsize_lbl")
        self.horizontalLayout_12.addWidget(self.hexsize_lbl)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem3)
        self.hexsize_spin = QtWidgets.QSpinBox(self.hexresolution_widget)
        self.hexsize_spin.setEnabled(False)
        self.hexsize_spin.setMinimumSize(QtCore.QSize(100, 0))
        self.hexsize_spin.setMinimum(200)
        self.hexsize_spin.setMaximum(5000)
        self.hexsize_spin.setSingleStep(50)
        self.hexsize_spin.setProperty("value", 500)
        self.hexsize_spin.setObjectName("hexsize_spin")
        self.horizontalLayout_12.addWidget(self.hexsize_spin)
        self.hexsize_auto = QtWidgets.QCheckBox(self.hexresolution_widget)
        self.hexsize_auto.setEnabled(False)
        self.hexsize_auto.setObjectName("hexsize_auto")
        self.horizontalLayout_12.addWidget(self.hexsize_auto)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem4)
        self.verticalLayout_11.addWidget(self.hexresolution_widget)
        self.hex_neighbour_title = QtWidgets.QLabel(self.page_2)
        self.hex_neighbour_title.setEnabled(False)
        self.hex_neighbour_title.setObjectName("hex_neighbour_title")
        self.verticalLayout_11.addWidget(self.hex_neighbour_title)
        self.hex_neighbour_lbl = QtWidgets.QLabel(self.page_2)
        self.hex_neighbour_lbl.setEnabled(False)
        self.hex_neighbour_lbl.setWordWrap(True)
        self.hex_neighbour_lbl.setObjectName("hex_neighbour_lbl")
        self.verticalLayout_11.addWidget(self.hex_neighbour_lbl)
        self.hexnhd_widget = QtWidgets.QWidget(self.page_2)
        self.hexnhd_widget.setObjectName("hexnhd_widget")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.hexnhd_widget)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.img_hex1 = QtWidgets.QLabel(self.hexnhd_widget)
        self.img_hex1.setEnabled(False)
        self.img_hex1.setMinimumSize(QtCore.QSize(50, 50))
        self.img_hex1.setMaximumSize(QtCore.QSize(50, 50))
        self.img_hex1.setText("")
        self.img_hex1.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_moore.png"))
        self.img_hex1.setObjectName("img_hex1")
        self.horizontalLayout_10.addWidget(self.img_hex1)
        self.radio_hexn1 = QtWidgets.QRadioButton(self.hexnhd_widget)
        self.radio_hexn1.setEnabled(False)
        self.radio_hexn1.setWhatsThis("")
        self.radio_hexn1.setCheckable(True)
        self.radio_hexn1.setObjectName("radio_hexn1")
        self.horizontalLayout_10.addWidget(self.radio_hexn1)
        self.img_hex2 = QtWidgets.QLabel(self.hexnhd_widget)
        self.img_hex2.setEnabled(False)
        self.img_hex2.setMinimumSize(QtCore.QSize(50, 50))
        self.img_hex2.setMaximumSize(QtCore.QSize(50, 50))
        self.img_hex2.setText("")
        self.img_hex2.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_vNeumann.png"))
        self.img_hex2.setObjectName("img_hex2")
        self.horizontalLayout_10.addWidget(self.img_hex2)
        self.radio_hexn2 = QtWidgets.QRadioButton(self.hexnhd_widget)
        self.radio_hexn2.setEnabled(False)
        self.radio_hexn2.setWhatsThis("")
        self.radio_hexn2.setChecked(False)
        self.radio_hexn2.setObjectName("radio_hexn2")
        self.horizontalLayout_10.addWidget(self.radio_hexn2)
        self.verticalLayout_11.addWidget(self.hexnhd_widget)
        self.hexoptions_lbl = QtWidgets.QLabel(self.page_2)
        self.hexoptions_lbl.setEnabled(False)
        self.hexoptions_lbl.setObjectName("hexoptions_lbl")
        self.verticalLayout_11.addWidget(self.hexoptions_lbl)
        self.rep_stack.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.page_3)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.vector_title = QtWidgets.QLabel(self.page_3)
        self.vector_title.setEnabled(False)
        self.vector_title.setObjectName("vector_title")
        self.verticalLayout_15.addWidget(self.vector_title)
        self.vectorgrid_widget = QtWidgets.QWidget(self.page_3)
        self.vectorgrid_widget.setObjectName("vectorgrid_widget")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.vectorgrid_widget)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.vectorgrid_lbl = QtWidgets.QLabel(self.vectorgrid_widget)
        self.vectorgrid_lbl.setEnabled(False)
        self.vectorgrid_lbl.setObjectName("vectorgrid_lbl")
        self.horizontalLayout_13.addWidget(self.vectorgrid_lbl)
        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem5)
        self.vectorgrid_spin = QtWidgets.QSpinBox(self.vectorgrid_widget)
        self.vectorgrid_spin.setEnabled(False)
        self.vectorgrid_spin.setMinimumSize(QtCore.QSize(100, 0))
        self.vectorgrid_spin.setMinimum(200)
        self.vectorgrid_spin.setMaximum(5000)
        self.vectorgrid_spin.setSingleStep(50)
        self.vectorgrid_spin.setProperty("value", 500)
        self.vectorgrid_spin.setObjectName("vectorgrid_spin")
        self.horizontalLayout_13.addWidget(self.vectorgrid_spin)
        self.vectorgrid_auto = QtWidgets.QCheckBox(self.vectorgrid_widget)
        self.vectorgrid_auto.setEnabled(False)
        self.vectorgrid_auto.setObjectName("vectorgrid_auto")
        self.horizontalLayout_13.addWidget(self.vectorgrid_auto)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem6)
        self.verticalLayout_15.addWidget(self.vectorgrid_widget)
        self.vectornhd_title = QtWidgets.QLabel(self.page_3)
        self.vectornhd_title.setEnabled(False)
        self.vectornhd_title.setObjectName("vectornhd_title")
        self.verticalLayout_15.addWidget(self.vectornhd_title)
        self.vectornhd_lbl = QtWidgets.QLabel(self.page_3)
        self.vectornhd_lbl.setEnabled(False)
        self.vectornhd_lbl.setWordWrap(True)
        self.vectornhd_lbl.setObjectName("vectornhd_lbl")
        self.verticalLayout_15.addWidget(self.vectornhd_lbl)
        self.vectornhd_widget = QtWidgets.QWidget(self.page_3)
        self.vectornhd_widget.setObjectName("vectornhd_widget")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.vectornhd_widget)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.img_borders = QtWidgets.QLabel(self.vectornhd_widget)
        self.img_borders.setEnabled(False)
        self.img_borders.setMinimumSize(QtCore.QSize(50, 50))
        self.img_borders.setMaximumSize(QtCore.QSize(50, 50))
        self.img_borders.setText("")
        self.img_borders.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_patchedges.png"))
        self.img_borders.setObjectName("img_borders")
        self.horizontalLayout_14.addWidget(self.img_borders)
        self.radio_borders = QtWidgets.QRadioButton(self.vectornhd_widget)
        self.radio_borders.setEnabled(False)
        self.radio_borders.setWhatsThis("")
        self.radio_borders.setCheckable(True)
        self.radio_borders.setObjectName("radio_borders")
        self.horizontalLayout_14.addWidget(self.radio_borders)
        self.img_radius = QtWidgets.QLabel(self.vectornhd_widget)
        self.img_radius.setEnabled(False)
        self.img_radius.setMinimumSize(QtCore.QSize(50, 50))
        self.img_radius.setMaximumSize(QtCore.QSize(50, 50))
        self.img_radius.setText("")
        self.img_radius.setPixmap(QtGui.QPixmap(":/images/images/md_spatial_patchradius.png"))
        self.img_radius.setObjectName("img_radius")
        self.horizontalLayout_14.addWidget(self.img_radius)
        self.radio_radius = QtWidgets.QRadioButton(self.vectornhd_widget)
        self.radio_radius.setEnabled(False)
        self.radio_radius.setWhatsThis("")
        self.radio_radius.setChecked(False)
        self.radio_radius.setObjectName("radio_radius")
        self.horizontalLayout_14.addWidget(self.radio_radius)
        self.verticalLayout_15.addWidget(self.vectornhd_widget)
        self.vectoroptions_lbl = QtWidgets.QLabel(self.page_3)
        self.vectoroptions_lbl.setEnabled(False)
        self.vectoroptions_lbl.setObjectName("vectoroptions_lbl")
        self.verticalLayout_15.addWidget(self.vectoroptions_lbl)
        self.rep_stack.addWidget(self.page_3)
        self.verticalLayout_14.addWidget(self.rep_stack)
        self.verticalLayout_5.addLayout(self.verticalLayout_14)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem7)
        self.geometry_scrollArea.setWidget(self.geometry_contents)
        self.verticalLayout_3.addWidget(self.geometry_scrollArea)
        self.parameters.addTab(self.geometry_tab, "")
        self.context_tab = QtWidgets.QWidget()
        self.context_tab.setObjectName("context_tab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.context_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.connectivity_scrollArea = QtWidgets.QScrollArea(self.context_tab)
        self.connectivity_scrollArea.setWidgetResizable(True)
        self.connectivity_scrollArea.setObjectName("connectivity_scrollArea")
        self.connectivity_contents = QtWidgets.QWidget()
        self.connectivity_contents.setGeometry(QtCore.QRect(0, 0, 538, 623))
        self.connectivity_contents.setObjectName("connectivity_contents")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.connectivity_contents)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.geography_title = QtWidgets.QLabel(self.connectivity_contents)
        self.geography_title.setObjectName("geography_title")
        self.verticalLayout_16.addWidget(self.geography_title)
        self.div2_1 = QtWidgets.QFrame(self.connectivity_contents)
        self.div2_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.div2_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div2_1.setObjectName("div2_1")
        self.verticalLayout_16.addWidget(self.div2_1)
        self.geography_lbl = QtWidgets.QLabel(self.connectivity_contents)
        self.geography_lbl.setWordWrap(True)
        self.geography_lbl.setObjectName("geography_lbl")
        self.verticalLayout_16.addWidget(self.geography_lbl)
        self.boundary_widget = QtWidgets.QWidget(self.connectivity_contents)
        self.boundary_widget.setObjectName("boundary_widget")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.boundary_widget)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.geopolitical_lbl = QtWidgets.QLabel(self.boundary_widget)
        self.geopolitical_lbl.setObjectName("geopolitical_lbl")
        self.gridLayout_9.addWidget(self.geopolitical_lbl, 3, 0, 1, 1)
        self.suburb_combo = QtWidgets.QComboBox(self.boundary_widget)
        self.suburb_combo.setObjectName("suburb_combo")
        self.suburb_combo.addItem("")
        self.gridLayout_9.addWidget(self.suburb_combo, 4, 1, 1, 1)
        self.suburb_check = QtWidgets.QCheckBox(self.boundary_widget)
        self.suburb_check.setObjectName("suburb_check")
        self.gridLayout_9.addWidget(self.suburb_check, 4, 0, 1, 1)
        self.geopolitical_combo = QtWidgets.QComboBox(self.boundary_widget)
        self.geopolitical_combo.setObjectName("geopolitical_combo")
        self.geopolitical_combo.addItem("")
        self.gridLayout_9.addWidget(self.geopolitical_combo, 1, 1, 1, 1)
        self.geopolitical_line = QtWidgets.QLineEdit(self.boundary_widget)
        self.geopolitical_line.setObjectName("geopolitical_line")
        self.gridLayout_9.addWidget(self.geopolitical_line, 3, 1, 1, 1)
        self.suburb_line = QtWidgets.QLineEdit(self.boundary_widget)
        self.suburb_line.setObjectName("suburb_line")
        self.gridLayout_9.addWidget(self.suburb_line, 7, 1, 1, 1)
        self.suburb_lbl_2 = QtWidgets.QLabel(self.boundary_widget)
        self.suburb_lbl_2.setObjectName("suburb_lbl_2")
        self.gridLayout_9.addWidget(self.suburb_lbl_2, 7, 0, 1, 1)
        self.geopolitical_check = QtWidgets.QCheckBox(self.boundary_widget)
        self.geopolitical_check.setObjectName("geopolitical_check")
        self.gridLayout_9.addWidget(self.geopolitical_check, 1, 0, 1, 1)
        self.planzone_combo = QtWidgets.QComboBox(self.boundary_widget)
        self.planzone_combo.setObjectName("planzone_combo")
        self.planzone_combo.addItem("")
        self.gridLayout_9.addWidget(self.planzone_combo, 8, 1, 1, 1)
        self.planzone_check = QtWidgets.QCheckBox(self.boundary_widget)
        self.planzone_check.setObjectName("planzone_check")
        self.gridLayout_9.addWidget(self.planzone_check, 8, 0, 1, 1)
        self.planzone_lbl = QtWidgets.QLabel(self.boundary_widget)
        self.planzone_lbl.setObjectName("planzone_lbl")
        self.gridLayout_9.addWidget(self.planzone_lbl, 9, 0, 1, 1)
        self.planzone_line = QtWidgets.QLineEdit(self.boundary_widget)
        self.planzone_line.setObjectName("planzone_line")
        self.gridLayout_9.addWidget(self.planzone_line, 9, 1, 1, 1)
        self.verticalLayout_16.addWidget(self.boundary_widget)
        self.cbd_lbl = QtWidgets.QLabel(self.connectivity_contents)
        self.cbd_lbl.setObjectName("cbd_lbl")
        self.verticalLayout_16.addWidget(self.cbd_lbl)
        self.div2_2 = QtWidgets.QFrame(self.connectivity_contents)
        self.div2_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.div2_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div2_2.setObjectName("div2_2")
        self.verticalLayout_16.addWidget(self.div2_2)
        self.considergeo_check = QtWidgets.QCheckBox(self.connectivity_contents)
        self.considergeo_check.setWhatsThis("")
        self.considergeo_check.setObjectName("considergeo_check")
        self.verticalLayout_16.addWidget(self.considergeo_check)
        self.region_widget = QtWidgets.QWidget(self.connectivity_contents)
        self.region_widget.setObjectName("region_widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.region_widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.city_combo = QtWidgets.QComboBox(self.region_widget)
        self.city_combo.setObjectName("city_combo")
        self.city_combo.addItem("")
        self.gridLayout_2.addWidget(self.city_combo, 2, 2, 1, 1)
        self.cbdlat_box = QtWidgets.QLineEdit(self.region_widget)
        self.cbdlat_box.setObjectName("cbdlat_box")
        self.gridLayout_2.addWidget(self.cbdlat_box, 7, 2, 1, 1)
        self.cbdmark_check = QtWidgets.QCheckBox(self.region_widget)
        self.cbdmark_check.setObjectName("cbdmark_check")
        self.gridLayout_2.addWidget(self.cbdmark_check, 8, 2, 1, 1)
        self.cbdlong_box = QtWidgets.QLineEdit(self.region_widget)
        self.cbdlong_box.setObjectName("cbdlong_box")
        self.gridLayout_2.addWidget(self.cbdlong_box, 4, 2, 1, 1)
        self.cbdoption_lbl = QtWidgets.QLabel(self.region_widget)
        self.cbdoption_lbl.setObjectName("cbdoption_lbl")
        self.gridLayout_2.addWidget(self.cbdoption_lbl, 1, 1, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem8, 2, 0, 1, 1)
        self.cbdknown_radio = QtWidgets.QRadioButton(self.region_widget)
        self.cbdknown_radio.setObjectName("cbdknown_radio")
        self.gridLayout_2.addWidget(self.cbdknown_radio, 2, 1, 1, 1)
        self.cbdmanual_radio = QtWidgets.QRadioButton(self.region_widget)
        self.cbdmanual_radio.setObjectName("cbdmanual_radio")
        self.gridLayout_2.addWidget(self.cbdmanual_radio, 4, 1, 1, 1)
        self.cbdlat_lbl = QtWidgets.QLabel(self.region_widget)
        self.cbdlat_lbl.setObjectName("cbdlat_lbl")
        self.gridLayout_2.addWidget(self.cbdlat_lbl, 7, 3, 1, 1)
        self.cbdlong_lbl = QtWidgets.QLabel(self.region_widget)
        self.cbdlong_lbl.setObjectName("cbdlong_lbl")
        self.gridLayout_2.addWidget(self.cbdlong_lbl, 4, 3, 1, 1)
        self.verticalLayout_16.addWidget(self.region_widget)
        self.osnet_title = QtWidgets.QLabel(self.connectivity_contents)
        self.osnet_title.setObjectName("osnet_title")
        self.verticalLayout_16.addWidget(self.osnet_title)
        self.div2_3 = QtWidgets.QFrame(self.connectivity_contents)
        self.div2_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.div2_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div2_3.setObjectName("div2_3")
        self.verticalLayout_16.addWidget(self.div2_3)
        self.osnet_descr = QtWidgets.QLabel(self.connectivity_contents)
        self.osnet_descr.setWordWrap(True)
        self.osnet_descr.setObjectName("osnet_descr")
        self.verticalLayout_16.addWidget(self.osnet_descr)
        self.osnet_widget = QtWidgets.QWidget(self.connectivity_contents)
        self.osnet_widget.setObjectName("osnet_widget")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.osnet_widget)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.osnet_accessibility_check = QtWidgets.QCheckBox(self.osnet_widget)
        self.osnet_accessibility_check.setObjectName("osnet_accessibility_check")
        self.gridLayout_14.addWidget(self.osnet_accessibility_check, 1, 0, 1, 1)
        self.osnet_spacenet_check = QtWidgets.QCheckBox(self.osnet_widget)
        self.osnet_spacenet_check.setObjectName("osnet_spacenet_check")
        self.gridLayout_14.addWidget(self.osnet_spacenet_check, 2, 0, 1, 1)
        self.verticalLayout_16.addWidget(self.osnet_widget)
        self.verticalLayout_6.addLayout(self.verticalLayout_16)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem9)
        self.connectivity_scrollArea.setWidget(self.connectivity_contents)
        self.verticalLayout_4.addWidget(self.connectivity_scrollArea)
        self.parameters.addTab(self.context_tab, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.connectivity_scrollArea_2 = QtWidgets.QScrollArea(self.tab)
        self.connectivity_scrollArea_2.setWidgetResizable(True)
        self.connectivity_scrollArea_2.setObjectName("connectivity_scrollArea_2")
        self.connectivity_contents_2 = QtWidgets.QWidget()
        self.connectivity_contents_2.setGeometry(QtCore.QRect(0, 0, 537, 829))
        self.connectivity_contents_2.setObjectName("connectivity_contents_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.connectivity_contents_2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout()
        self.verticalLayout_17.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.proximity_lbl = QtWidgets.QLabel(self.connectivity_contents_2)
        self.proximity_lbl.setObjectName("proximity_lbl")
        self.verticalLayout_17.addWidget(self.proximity_lbl)
        self.div3_1 = QtWidgets.QFrame(self.connectivity_contents_2)
        self.div3_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.div3_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div3_1.setObjectName("div3_1")
        self.verticalLayout_17.addWidget(self.div3_1)
        self.proximity_lbl_2 = QtWidgets.QLabel(self.connectivity_contents_2)
        self.proximity_lbl_2.setWordWrap(True)
        self.proximity_lbl_2.setObjectName("proximity_lbl_2")
        self.verticalLayout_17.addWidget(self.proximity_lbl_2)
        self.proximity_widget = QtWidgets.QWidget(self.connectivity_contents_2)
        self.proximity_widget.setObjectName("proximity_widget")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.proximity_widget)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.rivers_check = QtWidgets.QCheckBox(self.proximity_widget)
        self.rivers_check.setObjectName("rivers_check")
        self.gridLayout_10.addWidget(self.rivers_check, 1, 0, 1, 1)
        self.lakes_check = QtWidgets.QCheckBox(self.proximity_widget)
        self.lakes_check.setObjectName("lakes_check")
        self.gridLayout_10.addWidget(self.lakes_check, 3, 0, 1, 1)
        self.lakes_combo = QtWidgets.QComboBox(self.proximity_widget)
        self.lakes_combo.setObjectName("lakes_combo")
        self.lakes_combo.addItem("")
        self.gridLayout_10.addWidget(self.lakes_combo, 3, 1, 1, 1)
        self.lakes_attname = QtWidgets.QLineEdit(self.proximity_widget)
        self.lakes_attname.setObjectName("lakes_attname")
        self.gridLayout_10.addWidget(self.lakes_attname, 4, 1, 1, 1)
        self.waterbody_distance_check = QtWidgets.QCheckBox(self.proximity_widget)
        self.waterbody_distance_check.setObjectName("waterbody_distance_check")
        self.gridLayout_10.addWidget(self.waterbody_distance_check, 8, 0, 1, 1)
        self.rivers_attname = QtWidgets.QLineEdit(self.proximity_widget)
        self.rivers_attname.setObjectName("rivers_attname")
        self.gridLayout_10.addWidget(self.rivers_attname, 2, 1, 1, 1)
        self.rivers_combo = QtWidgets.QComboBox(self.proximity_widget)
        self.rivers_combo.setObjectName("rivers_combo")
        self.rivers_combo.addItem("")
        self.gridLayout_10.addWidget(self.rivers_combo, 1, 1, 1, 1)
        self.verticalLayout_17.addWidget(self.proximity_widget)
        self.waterinfra_lbl = QtWidgets.QLabel(self.connectivity_contents_2)
        self.waterinfra_lbl.setObjectName("waterinfra_lbl")
        self.verticalLayout_17.addWidget(self.waterinfra_lbl)
        self.div3_2 = QtWidgets.QFrame(self.connectivity_contents_2)
        self.div3_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.div3_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div3_2.setObjectName("div3_2")
        self.verticalLayout_17.addWidget(self.div3_2)
        self.waterinfra_lbl2 = QtWidgets.QLabel(self.connectivity_contents_2)
        self.waterinfra_lbl2.setWordWrap(True)
        self.waterinfra_lbl2.setObjectName("waterinfra_lbl2")
        self.verticalLayout_17.addWidget(self.waterinfra_lbl2)
        self.infrastructure_widget = QtWidgets.QWidget(self.connectivity_contents_2)
        self.infrastructure_widget.setObjectName("infrastructure_widget")
        self.formLayout = QtWidgets.QFormLayout(self.infrastructure_widget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.sewer_check = QtWidgets.QCheckBox(self.infrastructure_widget)
        self.sewer_check.setEnabled(False)
        self.sewer_check.setObjectName("sewer_check")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.sewer_check)
        self.sewer_combo = QtWidgets.QComboBox(self.infrastructure_widget)
        self.sewer_combo.setEnabled(False)
        self.sewer_combo.setObjectName("sewer_combo")
        self.sewer_combo.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sewer_combo)
        self.supply_check = QtWidgets.QCheckBox(self.infrastructure_widget)
        self.supply_check.setEnabled(False)
        self.supply_check.setObjectName("supply_check")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.supply_check)
        self.supply_combo = QtWidgets.QComboBox(self.infrastructure_widget)
        self.supply_combo.setEnabled(False)
        self.supply_combo.setObjectName("supply_combo")
        self.supply_combo.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.supply_combo)
        self.storm_check = QtWidgets.QCheckBox(self.infrastructure_widget)
        self.storm_check.setObjectName("storm_check")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.storm_check)
        self.storm_combo = QtWidgets.QComboBox(self.infrastructure_widget)
        self.storm_combo.setObjectName("storm_combo")
        self.storm_combo.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.storm_combo)
        self.verticalLayout_17.addWidget(self.infrastructure_widget)
        self.connectivity_title = QtWidgets.QLabel(self.connectivity_contents_2)
        self.connectivity_title.setObjectName("connectivity_title")
        self.verticalLayout_17.addWidget(self.connectivity_title)
        self.div3_3 = QtWidgets.QFrame(self.connectivity_contents_2)
        self.div3_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.div3_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.div3_3.setObjectName("div3_3")
        self.verticalLayout_17.addWidget(self.div3_3)
        self.flowpath_check = QtWidgets.QCheckBox(self.connectivity_contents_2)
        self.flowpath_check.setObjectName("flowpath_check")
        self.verticalLayout_17.addWidget(self.flowpath_check)
        self.flowpath_widget = QtWidgets.QWidget(self.connectivity_contents_2)
        self.flowpath_widget.setObjectName("flowpath_widget")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.flowpath_widget)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.flowpath_lbl = QtWidgets.QLabel(self.flowpath_widget)
        self.flowpath_lbl.setObjectName("flowpath_lbl")
        self.gridLayout_11.addWidget(self.flowpath_lbl, 1, 0, 1, 1)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_11.addItem(spacerItem10, 1, 2, 1, 1)
        self.demsmooth_check = QtWidgets.QCheckBox(self.flowpath_widget)
        self.demsmooth_check.setObjectName("demsmooth_check")
        self.gridLayout_11.addWidget(self.demsmooth_check, 2, 1, 1, 1)
        self.flowpath_combo = QtWidgets.QComboBox(self.flowpath_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.flowpath_combo.sizePolicy().hasHeightForWidth())
        self.flowpath_combo.setSizePolicy(sizePolicy)
        self.flowpath_combo.setObjectName("flowpath_combo")
        self.flowpath_combo.addItem("")
        self.flowpath_combo.addItem("")
        self.gridLayout_11.addWidget(self.flowpath_combo, 1, 1, 1, 1)
        self.demsmooth_spin = QtWidgets.QSpinBox(self.flowpath_widget)
        self.demsmooth_spin.setMinimum(1)
        self.demsmooth_spin.setMaximum(2)
        self.demsmooth_spin.setObjectName("demsmooth_spin")
        self.gridLayout_11.addWidget(self.demsmooth_spin, 2, 2, 1, 1)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_11.addItem(spacerItem11, 2, 3, 1, 1)
        self.connectivity_lbl = QtWidgets.QLabel(self.flowpath_widget)
        self.connectivity_lbl.setWordWrap(True)
        self.connectivity_lbl.setObjectName("connectivity_lbl")
        self.gridLayout_11.addWidget(self.connectivity_lbl, 0, 0, 1, 4)
        self.verticalLayout_17.addWidget(self.flowpath_widget)
        self.flowpath_guide_widget = QtWidgets.QWidget(self.connectivity_contents_2)
        self.flowpath_guide_widget.setObjectName("flowpath_guide_widget")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.flowpath_guide_widget)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.infrastructure_check = QtWidgets.QCheckBox(self.flowpath_guide_widget)
        self.infrastructure_check.setObjectName("infrastructure_check")
        self.gridLayout_12.addWidget(self.infrastructure_check, 2, 0, 1, 1)
        self.flowpath_lbl2 = QtWidgets.QLabel(self.flowpath_guide_widget)
        self.flowpath_lbl2.setObjectName("flowpath_lbl2")
        self.gridLayout_12.addWidget(self.flowpath_lbl2, 0, 0, 1, 1)
        self.natfeature_check = QtWidgets.QCheckBox(self.flowpath_guide_widget)
        self.natfeature_check.setObjectName("natfeature_check")
        self.gridLayout_12.addWidget(self.natfeature_check, 1, 0, 1, 1)
        self.verticalLayout_17.addWidget(self.flowpath_guide_widget)
        self.flowpath_guide_widget_3 = QtWidgets.QWidget(self.connectivity_contents_2)
        self.flowpath_guide_widget_3.setObjectName("flowpath_guide_widget_3")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.flowpath_guide_widget_3)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.ignore_lakes_check = QtWidgets.QCheckBox(self.flowpath_guide_widget_3)
        self.ignore_lakes_check.setObjectName("ignore_lakes_check")
        self.gridLayout_15.addWidget(self.ignore_lakes_check, 2, 0, 1, 1)
        self.outlet_title = QtWidgets.QLabel(self.flowpath_guide_widget_3)
        self.outlet_title.setObjectName("outlet_title")
        self.gridLayout_15.addWidget(self.outlet_title, 0, 0, 1, 1)
        self.ignore_rivers_check = QtWidgets.QCheckBox(self.flowpath_guide_widget_3)
        self.ignore_rivers_check.setObjectName("ignore_rivers_check")
        self.gridLayout_15.addWidget(self.ignore_rivers_check, 1, 0, 1, 1)
        self.verticalLayout_17.addWidget(self.flowpath_guide_widget_3)
        self.flowpath_guide_widget_4 = QtWidgets.QWidget(self.connectivity_contents_2)
        self.flowpath_guide_widget_4.setObjectName("flowpath_guide_widget_4")
        self.gridLayout_16 = QtWidgets.QGridLayout(self.flowpath_guide_widget_4)
        self.gridLayout_16.setObjectName("gridLayout_16")
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_16.addItem(spacerItem12, 3, 4, 1, 1)
        self.patchflow_title = QtWidgets.QLabel(self.flowpath_guide_widget_4)
        self.patchflow_title.setObjectName("patchflow_title")
        self.gridLayout_16.addWidget(self.patchflow_title, 0, 0, 1, 5)
        self.patchflow_delin = QtWidgets.QCheckBox(self.flowpath_guide_widget_4)
        self.patchflow_delin.setObjectName("patchflow_delin")
        self.gridLayout_16.addWidget(self.patchflow_delin, 1, 0, 1, 4)
        self.patchflow_searchradius_spin = QtWidgets.QDoubleSpinBox(self.flowpath_guide_widget_4)
        self.patchflow_searchradius_spin.setDecimals(1)
        self.patchflow_searchradius_spin.setMaximum(2000.0)
        self.patchflow_searchradius_spin.setProperty("value", 500.0)
        self.patchflow_searchradius_spin.setObjectName("patchflow_searchradius_spin")
        self.gridLayout_16.addWidget(self.patchflow_searchradius_spin, 3, 2, 1, 1)
        self.patchflow_searchradius_auto = QtWidgets.QCheckBox(self.flowpath_guide_widget_4)
        self.patchflow_searchradius_auto.setObjectName("patchflow_searchradius_auto")
        self.gridLayout_16.addWidget(self.patchflow_searchradius_auto, 3, 3, 1, 1)
        spacerItem13 = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_16.addItem(spacerItem13, 3, 0, 1, 1)
        self.patchflow_searchradius_lbl = QtWidgets.QLabel(self.flowpath_guide_widget_4)
        self.patchflow_searchradius_lbl.setObjectName("patchflow_searchradius_lbl")
        self.gridLayout_16.addWidget(self.patchflow_searchradius_lbl, 3, 1, 1, 1)
        self.patchflow_method_lbl = QtWidgets.QLabel(self.flowpath_guide_widget_4)
        self.patchflow_method_lbl.setObjectName("patchflow_method_lbl")
        self.gridLayout_16.addWidget(self.patchflow_method_lbl, 2, 1, 1, 1)
        self.patchflow_method_combo = QtWidgets.QComboBox(self.flowpath_guide_widget_4)
        self.patchflow_method_combo.setObjectName("patchflow_method_combo")
        self.patchflow_method_combo.addItem("")
        self.patchflow_method_combo.addItem("")
        self.patchflow_method_combo.addItem("")
        self.gridLayout_16.addWidget(self.patchflow_method_combo, 2, 2, 1, 2)
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_16.addItem(spacerItem14, 2, 4, 1, 1)
        self.verticalLayout_17.addWidget(self.flowpath_guide_widget_4)
        self.verticalLayout_7.addLayout(self.verticalLayout_17)
        spacerItem15 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem15)
        self.connectivity_scrollArea_2.setWidget(self.connectivity_contents_2)
        self.verticalLayout_8.addWidget(self.connectivity_scrollArea_2)
        self.parameters.addTab(self.tab, "")
        self.horizontalLayout_6.addWidget(self.parameters)
        self.verticalLayout.addWidget(self.module_widget)
        self.footer = QtWidgets.QWidget(Delinblocks_Dialog)
        self.footer.setMinimumSize(QtCore.QSize(0, 40))
        self.footer.setMaximumSize(QtCore.QSize(16777215, 40))
        self.footer.setObjectName("footer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.footer)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.footer_lbl = QtWidgets.QLabel(self.footer)
        self.footer_lbl.setObjectName("footer_lbl")
        self.horizontalLayout.addWidget(self.footer_lbl)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.footer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.reset_button = QtWidgets.QPushButton(self.footer)
        self.reset_button.setObjectName("reset_button")
        self.horizontalLayout.addWidget(self.reset_button)
        self.help_button = QtWidgets.QPushButton(self.footer)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/Help-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon3)
        self.help_button.setObjectName("help_button")
        self.horizontalLayout.addWidget(self.help_button)
        self.verticalLayout.addWidget(self.footer)

        self.retranslateUi(Delinblocks_Dialog)
        self.parameters.setCurrentIndex(0)
        self.rep_stack.setCurrentIndex(0)
        self.flowpath_combo.setCurrentIndex(1)
        self.buttonBox.accepted.connect(Delinblocks_Dialog.accept)
        self.buttonBox.rejected.connect(Delinblocks_Dialog.reject)
        self.rep_combo.currentIndexChanged['int'].connect(self.rep_stack.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(Delinblocks_Dialog)
        Delinblocks_Dialog.setTabOrder(self.year_combo, self.same_params)
        Delinblocks_Dialog.setTabOrder(self.same_params, self.description)
        Delinblocks_Dialog.setTabOrder(self.description, self.parameters)
        Delinblocks_Dialog.setTabOrder(self.parameters, self.geometry_scrollArea)
        Delinblocks_Dialog.setTabOrder(self.geometry_scrollArea, self.rep_combo)
        Delinblocks_Dialog.setTabOrder(self.rep_combo, self.buttonBox)
        Delinblocks_Dialog.setTabOrder(self.buttonBox, self.help_button)

    def retranslateUi(self, Delinblocks_Dialog):
        _translate = QtCore.QCoreApplication.translate
        Delinblocks_Dialog.setWindowTitle(_translate("Delinblocks_Dialog", "Spatial Delineation Module"))
        self.title.setText(_translate("Delinblocks_Dialog", "Spatial Setup"))
        self.subtitle.setText(_translate("Delinblocks_Dialog", "Determine geometric representation, establish spatial connectivity and define how to process input data."))
        self.sidebar_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">SCENARIO TIME STEP</span></p></body></html>"))
        self.year_combo.setItemText(0, _translate("Delinblocks_Dialog", "<startyear>"))
        self.autofillButton.setText(_translate("Delinblocks_Dialog", "Autofill from previous"))
        self.same_params.setText(_translate("Delinblocks_Dialog", "Same Parameters"))
        self.description.setHtml(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">A simplified spatial representation of the urban environment. In this module, settings are made to the geometry that is used to represent the urban information, spatial connectivity and geography.</span></p></body></html>"))
        self.essential_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">ESSENTIAL SPATIAL DATA SETS</span></p></body></html>"))
        self.descr2.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p>Select the corresponding maps for the current scenario\'s time step (in static and benchmark scenarios, there are no time steps).</p></body></html>"))
        self.lu_lbl.setText(_translate("Delinblocks_Dialog", "Land Use Map:"))
        self.pop_fromurbandev.setText(_translate("Delinblocks_Dialog", "from urban development"))
        self.lu_fromurbandev.setText(_translate("Delinblocks_Dialog", "from urban development"))
        self.elev_lbl.setText(_translate("Delinblocks_Dialog", "Elevation:"))
        self.pop_lbl.setText(_translate("Delinblocks_Dialog", "Population:"))
        self.geometry_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">SPATIAL GEOMETRY</span></p></body></html>"))
        self.geometry_lbl1.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p>Setup rules for delineation of the raw data into UrbanBEATS\' vector files. There are three possible representations with the default being UrbanBEATS\' classical Block representation.</p></body></html>"))
        self.rep_lbl.setWhatsThis(_translate("Delinblocks_Dialog", "Width of the square cell in the city grid in metres"))
        self.rep_lbl.setText(_translate("Delinblocks_Dialog", "Select Geometry for Simulation: "))
        self.rep_combo.setItemText(0, _translate("Delinblocks_Dialog", "Block-based Representation"))
        self.rep_combo.setItemText(1, _translate("Delinblocks_Dialog", "Hex-based Representation"))
        self.rep_combo.setItemText(2, _translate("Delinblocks_Dialog", "Vector-based Patch Representation"))
        self.blockrep_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Customize Block-based Representation</span></p></body></html>"))
        self.resolution_lbl_2.setWhatsThis(_translate("Delinblocks_Dialog", "Width of the square cell in the city grid in metres"))
        self.resolution_lbl_2.setText(_translate("Delinblocks_Dialog", "Size of Block:"))
        self.resolution_spin.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Width of the square cell in the city grid in metres</span></p></body></html>"))
        self.resolution_spin.setSuffix(_translate("Delinblocks_Dialog", " metres"))
        self.resolution_auto.setToolTip(_translate("Delinblocks_Dialog", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.resolution_auto.setText(_translate("Delinblocks_Dialog", "Auto-determine"))
        self.neighbourhood_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Block Neighbourhood Rule</span></p></body></html>"))
        self.neighbourhood_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p>Choose from two common neighbourhood types, Moore (i.e. 8 cardinal directions) or Von Neumann (i.e. North, South, East and West directions).</p></body></html>"))
        self.radio_moore.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Moore, all eight neighbours around the central block.</span></p></body></html>"))
        self.radio_moore.setText(_translate("Delinblocks_Dialog", "Moore"))
        self.radio_vonNeu.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Von Neumann, four cardinal directions on either side of the central block.</span></p></body></html>"))
        self.radio_vonNeu.setText(_translate("Delinblocks_Dialog", "Von Neumann"))
        self.geooptions_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Further Options</span></p></body></html>"))
        self.spatialindices_check.setToolTip(_translate("Delinblocks_Dialog", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.spatialindices_check.setText(_translate("Delinblocks_Dialog", "Calculate Spatial Indices (e.g. richness, diversity, dominance)"))
        self.patchdelin_check.setToolTip(_translate("Delinblocks_Dialog", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.patchdelin_check.setText(_translate("Delinblocks_Dialog", "Delineate Land Use Patches (conceptual)"))
        self.hexrep_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Hex-based Grid Representation - Customize (COMING SOON)</span></p></body></html>"))
        self.hexsize_lbl.setWhatsThis(_translate("Delinblocks_Dialog", "Width of the square cell in the city grid in metres"))
        self.hexsize_lbl.setText(_translate("Delinblocks_Dialog", "Size of a Hexagon:"))
        self.hexsize_spin.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Width of the square cell in the city grid in metres</span></p></body></html>"))
        self.hexsize_spin.setSuffix(_translate("Delinblocks_Dialog", " metres"))
        self.hexsize_auto.setToolTip(_translate("Delinblocks_Dialog", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.hexsize_auto.setText(_translate("Delinblocks_Dialog", "Auto-determine"))
        self.hex_neighbour_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Hex Neighbourhood Rule</span></p></body></html>"))
        self.hex_neighbour_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p>Choose from two common neighbourhood types, Moore (i.e. 8 cardinal directions) or Von Neumann (i.e. North, South, East and West directions).</p></body></html>"))
        self.radio_hexn1.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Moore, all eight neighbours around the central block.</span></p></body></html>"))
        self.radio_hexn1.setText(_translate("Delinblocks_Dialog", "Neighbourhood 1"))
        self.radio_hexn2.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Von Neumann, four cardinal directions on either side of the central block.</span></p></body></html>"))
        self.radio_hexn2.setText(_translate("Delinblocks_Dialog", "Neighbourhood 2"))
        self.hexoptions_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Further Options</span></p></body></html>"))
        self.vector_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Customize Vector-based Patch Representation (COMING SOON)</span></p></body></html>"))
        self.vectorgrid_lbl.setWhatsThis(_translate("Delinblocks_Dialog", "Width of the square cell in the city grid in metres"))
        self.vectorgrid_lbl.setText(_translate("Delinblocks_Dialog", "Discretization Grid Size:"))
        self.vectorgrid_spin.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Width of the square cell in the city grid in metres</span></p></body></html>"))
        self.vectorgrid_spin.setSuffix(_translate("Delinblocks_Dialog", " metres"))
        self.vectorgrid_auto.setToolTip(_translate("Delinblocks_Dialog", "An automatic algorithm that determines a suitable block size based on the map for computational efficiency."))
        self.vectorgrid_auto.setText(_translate("Delinblocks_Dialog", "Auto-determine"))
        self.vectornhd_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Patch Neighbourhood Rule</span></p></body></html>"))
        self.vectornhd_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p>Choose which neighbourhood rule to use, Border Edges (all adjacent patches that share a common edge), or a scan radius (all patches whose centroids are within a given radius of the current patch)</p></body></html>"))
        self.radio_borders.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Moore, all eight neighbours around the central block.</span></p></body></html>"))
        self.radio_borders.setText(_translate("Delinblocks_Dialog", "Border Edges"))
        self.radio_radius.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Von Neumann, four cardinal directions on either side of the central block.</span></p></body></html>"))
        self.radio_radius.setText(_translate("Delinblocks_Dialog", "Scan Radius"))
        self.vectoroptions_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Further Options</span></p></body></html>"))
        self.parameters.setTabText(self.parameters.indexOf(self.geometry_tab), _translate("Delinblocks_Dialog", "Basic Setup"))
        self.geography_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">JURISDICTIONAL, SUBURBAN AND PLANNING BOUNDARIES</span></p></body></html>"))
        self.geography_lbl.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p></body></html>"))
        self.geography_lbl.setText(_translate("Delinblocks_Dialog", "Include jurisdictional boundaries of municipalities or provide suburban subdivision in the delineation to provide regional context information."))
        self.geopolitical_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p align=\"right\">Map Attribute Label Name:</p></body></html>"))
        self.suburb_combo.setItemText(0, _translate("Delinblocks_Dialog", "(no map selected)"))
        self.suburb_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.suburb_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.suburb_check.setText(_translate("Delinblocks_Dialog", "Suburban Boundaries"))
        self.geopolitical_combo.setItemText(0, _translate("Delinblocks_Dialog", "(no map selected)"))
        self.geopolitical_line.setToolTip(_translate("Delinblocks_Dialog", "Units of decimal degrees"))
        self.suburb_line.setToolTip(_translate("Delinblocks_Dialog", "Units of decimal degrees."))
        self.suburb_lbl_2.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p align=\"right\">Map Attribute Label Name:</p></body></html>"))
        self.geopolitical_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.geopolitical_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.geopolitical_check.setText(_translate("Delinblocks_Dialog", "Jurisdictional Boundaries"))
        self.planzone_combo.setItemText(0, _translate("Delinblocks_Dialog", "(no map selected)"))
        self.planzone_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.planzone_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.planzone_check.setText(_translate("Delinblocks_Dialog", "Planning Zones"))
        self.planzone_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p align=\"right\">Map Attribute Label Name:</p></body></html>"))
        self.planzone_line.setToolTip(_translate("Delinblocks_Dialog", "Units of decimal degrees."))
        self.cbd_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">CENTRAL BUSINESS DISTRICT</span></p></body></html>"))
        self.considergeo_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will have the model to calculate distance from CBD (based on a selected city using its central point of reference)."))
        self.considergeo_check.setText(_translate("Delinblocks_Dialog", "Consider location of nearest Central Business District in Simulation"))
        self.city_combo.setItemText(0, _translate("Delinblocks_Dialog", "(default city of project)"))
        self.cbdlat_box.setToolTip(_translate("Delinblocks_Dialog", "Units of decimal degrees."))
        self.cbdmark_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.cbdmark_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.cbdmark_check.setText(_translate("Delinblocks_Dialog", "Mark this location on output map"))
        self.cbdlong_box.setToolTip(_translate("Delinblocks_Dialog", "Units of decimal degrees"))
        self.cbdoption_lbl.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p></body></html>"))
        self.cbdoption_lbl.setText(_translate("Delinblocks_Dialog", "Select an option for determining CBD Location:"))
        self.cbdknown_radio.setToolTip(_translate("Delinblocks_Dialog", "Choose the nearest city if your case study is within its metropolitan region."))
        self.cbdknown_radio.setText(_translate("Delinblocks_Dialog", "Select from a list of known locations"))
        self.cbdmanual_radio.setToolTip(_translate("Delinblocks_Dialog", "Enter the coordinates of your city\'s CBD manually. Use decimal degrees."))
        self.cbdmanual_radio.setText(_translate("Delinblocks_Dialog", "Manually enter coordinates of CBD"))
        self.cbdlat_lbl.setText(_translate("Delinblocks_Dialog", "lat."))
        self.cbdlong_lbl.setText(_translate("Delinblocks_Dialog", "long."))
        self.osnet_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">OPEN SPACE NETWORK</span></p></body></html>"))
        self.osnet_descr.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>"))
        self.osnet_descr.setText(_translate("Delinblocks_Dialog", "Access to open space has a significant impact on urban liveability, connectivity between open spaces is important for habitat provision and recreation. Customize how these are considered:"))
        self.osnet_accessibility_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.osnet_accessibility_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Applies a weighted average smoothing filter over the DEM layer. </span></p></body></html>"))
        self.osnet_accessibility_check.setText(_translate("Delinblocks_Dialog", "Calculate accessibility to open spaces in urban morphology"))
        self.osnet_spacenet_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.osnet_spacenet_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Applies a weighted average smoothing filter over the DEM layer. </span></p></body></html>"))
        self.osnet_spacenet_check.setText(_translate("Delinblocks_Dialog", "Delineate open space network and determine connectivity"))
        self.parameters.setTabText(self.parameters.indexOf(self.context_tab), _translate("Delinblocks_Dialog", "Urban Space"))
        self.proximity_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">MAJOR WATER FEATURES</span></p></body></html>"))
        self.proximity_lbl_2.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p></body></html>"))
        self.proximity_lbl_2.setText(_translate("Delinblocks_Dialog", "Customise whether UrbanBEATS should  load and link major surface water features with the Blocks map."))
        self.rivers_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.rivers_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.rivers_check.setText(_translate("Delinblocks_Dialog", "Rivers and Creeks"))
        self.lakes_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.lakes_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.lakes_check.setText(_translate("Delinblocks_Dialog", "Ponds and Lakes"))
        self.lakes_combo.setItemText(0, _translate("Delinblocks_Dialog", "(no map selected)"))
        self.lakes_attname.setText(_translate("Delinblocks_Dialog", "<water body identifier field name>"))
        self.waterbody_distance_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.waterbody_distance_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.waterbody_distance_check.setText(_translate("Delinblocks_Dialog", "Calculate distance to closest water body"))
        self.rivers_attname.setText(_translate("Delinblocks_Dialog", "<water body identifier field name>"))
        self.rivers_combo.setItemText(0, _translate("Delinblocks_Dialog", "(no map selected)"))
        self.waterinfra_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">BUILT WATER INFRASTRUCTURE</span></p></body></html>"))
        self.waterinfra_lbl2.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p></body></html>"))
        self.waterinfra_lbl2.setText(_translate("Delinblocks_Dialog", "Include pre-existing water infrastructure into the simulation for coupling or retrofitting."))
        self.sewer_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.sewer_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Applies a weighted average smoothing filter over the DEM layer. </span></p></body></html>"))
        self.sewer_check.setText(_translate("Delinblocks_Dialog", "Sewer Network (coming soon)"))
        self.sewer_combo.setItemText(0, _translate("Delinblocks_Dialog", "(none)"))
        self.supply_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.supply_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Applies a weighted average smoothing filter over the DEM layer. </span></p></body></html>"))
        self.supply_check.setText(_translate("Delinblocks_Dialog", "Water Supply Network (coming soon)"))
        self.supply_combo.setItemText(0, _translate("Delinblocks_Dialog", "(none)"))
        self.storm_check.setToolTip(_translate("Delinblocks_Dialog", "Checking this box will produce a CBD point on the \"block centres\" output map."))
        self.storm_check.setWhatsThis(_translate("Delinblocks_Dialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet."))
        self.storm_check.setText(_translate("Delinblocks_Dialog", "Stormwater Drainage Infrastructure"))
        self.storm_combo.setItemText(0, _translate("Delinblocks_Dialog", "(none)"))
        self.connectivity_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">DRAINAGE FLOW PATHS</span></p></body></html>"))
        self.flowpath_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.flowpath_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If available, then the program will bias the flow directions towards Blocks with natural features e.g. a river, creek or lake. This will only happen if the above option to include a river or lake feature has been enabled and a map has been specified.</p></body></html>"))
        self.flowpath_check.setText(_translate("Delinblocks_Dialog", "Delineate stormwater drainage flowpaths and sub-basins across the case study"))
        self.flowpath_lbl.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>"))
        self.flowpath_lbl.setText(_translate("Delinblocks_Dialog", "Flowpath Method:"))
        self.demsmooth_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.demsmooth_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Applies a weighted average smoothing filter over the DEM layer. </span></p></body></html>"))
        self.demsmooth_check.setText(_translate("Delinblocks_Dialog", "DEM Smoothing (select no. of passes)"))
        self.flowpath_combo.setItemText(0, _translate("Delinblocks_Dialog", "Adapted version of D-infinity (Tarboton, 1997)"))
        self.flowpath_combo.setItemText(1, _translate("Delinblocks_Dialog", "D8 (O\'Callaghan & Mark, 1984)"))
        self.demsmooth_spin.setToolTip(_translate("Delinblocks_Dialog", "Select the number of times the smoothing algorithm should be applied. A higher number will lead to a much smoother map, but can result in possible issues with finding flow paths."))
        self.connectivity_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p>Select and customise methodology for identifying water drainage paths across Blocks.</p></body></html>"))
        self.infrastructure_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.infrastructure_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If available, then the program will bias the flow directions towards Blocks with built stormwater draingae infrastructure e.g. channelized drains and pipe network. This will only happen if the above option to include stormwater infrastruture has been enabled and a map has been specified.</p></body></html>"))
        self.infrastructure_check.setText(_translate("Delinblocks_Dialog", "Use stormwater drainage infrastructure as a guide for flow path delineation"))
        self.flowpath_lbl2.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>"))
        self.flowpath_lbl2.setText(_translate("Delinblocks_Dialog", "Flow Path Guides:"))
        self.natfeature_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.natfeature_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If available, then the program will bias the flow directions towards Blocks with natural features e.g. a river, creek or lake. This will only happen if the above option to include a river or lake feature has been enabled and a map has been specified.</p></body></html>"))
        self.natfeature_check.setText(_translate("Delinblocks_Dialog", "Use natural water features as a guide for flow path delineation"))
        self.ignore_lakes_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.ignore_lakes_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ignores lake features in the landscape. This means that delineation continues until the lowest elevation point has been detected. Select this option if the lakes you have included are not major drainage outlets e.g. a large lake vs. a retarding basin. If the lake features regularly spill downstream, then check this option to ensure that the catchment delineation continues beyond the lake.</p></body></html>"))
        self.ignore_lakes_check.setText(_translate("Delinblocks_Dialog", "Ignore Lake features when determining catchment outlets"))
        self.outlet_title.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>"))
        self.outlet_title.setText(_translate("Delinblocks_Dialog", "Catchment Outlets:"))
        self.ignore_rivers_check.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.ignore_rivers_check.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ignores river features in the landscape. This means that delineation continues until the lowest elevation point has been detected. Select this option if your river features do not directly determine the catchment e.g. you are including a creek in the catchment, but do not want to subdivide the catchment based on inflow points to the creek.</p></body></html>"))
        self.ignore_rivers_check.setText(_translate("Delinblocks_Dialog", "Ignore River features when determining catchment outlets"))
        self.patchflow_title.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>"))
        self.patchflow_title.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">Patch Flowpaths</span></p></body></html>"))
        self.patchflow_delin.setToolTip(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Correction proceeds as follows:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.</span></p></body></html>"))
        self.patchflow_delin.setWhatsThis(_translate("Delinblocks_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ignores river features in the landscape. This means that delineation continues until the lowest elevation point has been detected. Select this option if your river features do not directly determine the catchment e.g. you are including a creek in the catchment, but do not want to subdivide the catchment based on inflow points to the creek.</p></body></html>"))
        self.patchflow_delin.setText(_translate("Delinblocks_Dialog", "Delineate Patch Natural Drainage Flowpaths"))
        self.patchflow_searchradius_spin.setSuffix(_translate("Delinblocks_Dialog", " m"))
        self.patchflow_searchradius_auto.setText(_translate("Delinblocks_Dialog", "Auto-determine"))
        self.patchflow_searchradius_lbl.setText(_translate("Delinblocks_Dialog", "Search Radius:"))
        self.patchflow_method_lbl.setText(_translate("Delinblocks_Dialog", "Delineation Method:"))
        self.patchflow_method_combo.setItemText(0, _translate("Delinblocks_Dialog", "Minimum dz Drop"))
        self.patchflow_method_combo.setItemText(1, _translate("Delinblocks_Dialog", "Shortest Distance dz Drop"))
        self.patchflow_method_combo.setItemText(2, _translate("Delinblocks_Dialog", "Steepest dz Drop"))
        self.parameters.setTabText(self.parameters.indexOf(self.tab), _translate("Delinblocks_Dialog", "Water Context"))
        self.footer_lbl.setText(_translate("Delinblocks_Dialog", "<html><head/><body><p><span style=\" font-style:italic;\">UrbanBEATS - md_delinblocks module</span></p></body></html>"))
        self.reset_button.setWhatsThis(_translate("Delinblocks_Dialog", "<html><head/><body><p>Resets all parameters of this module in the current \'scenario time step\' to the default values.</p></body></html>"))
        self.reset_button.setText(_translate("Delinblocks_Dialog", "Reset..."))
        self.help_button.setText(_translate("Delinblocks_Dialog", "Help"))
from . import ubeats_rc
