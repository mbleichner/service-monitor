# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/Sources.ui'
#
# Created: Thu Nov  3 19:04:39 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Sources(object):
    def setupUi(self, Sources):
        Sources.setObjectName(_fromUtf8("Sources"))
        Sources.resize(604, 435)
        self.verticalLayout_5 = QtGui.QVBoxLayout(Sources)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.sourceList = QtGui.QListWidget(Sources)
        self.sourceList.setObjectName(_fromUtf8("sourceList"))
        self.verticalLayout_5.addWidget(self.sourceList)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.searchButton = QtGui.QPushButton(Sources)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/search.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.searchButton.setIcon(icon)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.horizontalLayout.addWidget(self.searchButton)
        self.addButton = QtGui.QPushButton(Sources)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon1)
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.horizontalLayout.addWidget(self.addButton)
        self.removeButton = QtGui.QPushButton(Sources)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeButton.setIcon(icon2)
        self.removeButton.setObjectName(_fromUtf8("removeButton"))
        self.horizontalLayout.addWidget(self.removeButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(Sources)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_5.addWidget(self.line)
        self.infoTextarea = QtGui.QTextEdit(Sources)
        self.infoTextarea.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoTextarea.sizePolicy().hasHeightForWidth())
        self.infoTextarea.setSizePolicy(sizePolicy)
        self.infoTextarea.setReadOnly(True)
        self.infoTextarea.setHtml(_fromUtf8("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>"))
        self.infoTextarea.setObjectName(_fromUtf8("infoTextarea"))
        self.verticalLayout_5.addWidget(self.infoTextarea)
        self.line_2 = QtGui.QFrame(Sources)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout_5.addWidget(self.line_2)
        self.helpTabWidget = QtGui.QTabWidget(Sources)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.helpTabWidget.sizePolicy().hasHeightForWidth())
        self.helpTabWidget.setSizePolicy(sizePolicy)
        self.helpTabWidget.setMinimumSize(QtCore.QSize(0, 110))
        self.helpTabWidget.setObjectName(_fromUtf8("helpTabWidget"))
        self.help = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.help.sizePolicy().hasHeightForWidth())
        self.help.setSizePolicy(sizePolicy)
        self.help.setObjectName(_fromUtf8("help"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.help)
        self.verticalLayout_2.setMargin(10)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.help)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/help.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.helpTabWidget.addTab(self.help, icon3, _fromUtf8(""))
        self.verticalLayout_5.addWidget(self.helpTabWidget)

        self.retranslateUi(Sources)
        self.helpTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Sources)

    def retranslateUi(self, Sources):
        Sources.setWindowTitle(QtGui.QApplication.translate("Sources", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setToolTip(QtGui.QApplication.translate("Sources", "Look for new XML files on the internet", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setText(QtGui.QApplication.translate("Sources", "Search for new source files", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("Sources", "Add XML source file", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("Sources", "Remove selected file", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Sources", "This list holds files containing service definitions. You can search www.documentroot.net\n"
"for updated definitions and then include them in the applet, so you can immediately\n"
"use them.", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
