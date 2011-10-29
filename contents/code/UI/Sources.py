# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Sources.ui'
#
# Created: Fri Sep  3 18:15:11 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Sources(object):
    def setupUi(self, Sources):
        Sources.setObjectName("Sources")
        Sources.resize(593, 431)
        self.verticalLayout = QtGui.QVBoxLayout(Sources)
        self.verticalLayout.setObjectName("verticalLayout")
        self.sourceList = QtGui.QListWidget(Sources)
        self.sourceList.setObjectName("sourceList")
        self.verticalLayout.addWidget(self.sourceList)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.searchButton = QtGui.QPushButton(Sources)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.searchButton.setIcon(icon)
        self.searchButton.setObjectName("searchButton")
        self.horizontalLayout.addWidget(self.searchButton)
        self.addButton = QtGui.QPushButton(Sources)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon1)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout.addWidget(self.addButton)
        self.removeButton = QtGui.QPushButton(Sources)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeButton.setIcon(icon2)
        self.removeButton.setObjectName("removeButton")
        self.horizontalLayout.addWidget(self.removeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(Sources)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.infoTextarea = QtGui.QTextEdit(Sources)
        self.infoTextarea.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoTextarea.sizePolicy().hasHeightForWidth())
        self.infoTextarea.setSizePolicy(sizePolicy)
        self.infoTextarea.setReadOnly(True)
        self.infoTextarea.setObjectName("infoTextarea")
        self.verticalLayout.addWidget(self.infoTextarea)

        self.retranslateUi(Sources)
        QtCore.QMetaObject.connectSlotsByName(Sources)

    def retranslateUi(self, Sources):
        Sources.setWindowTitle(QtGui.QApplication.translate("Sources", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setToolTip(QtGui.QApplication.translate("Sources", "Look for new XML files on the internet", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setText(QtGui.QApplication.translate("Sources", "Search for new source files", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("Sources", "Add XML source file", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("Sources", "Remove selected file", None, QtGui.QApplication.UnicodeUTF8))
        self.infoTextarea.setHtml(QtGui.QApplication.translate("Sources", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Nimbus Sans L\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Here you can manage your files containing the service definitions. If you find a specific service missing, you may find it on my website, where I\'ll provide you with the latest definition files. Just click the &quot;search for new source files&quot; button.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import Icons_rc
