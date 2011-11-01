# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/Settings.ui'
#
# Created: Tue Nov  1 23:11:07 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(514, 441)
        self.verticalLayout = QtGui.QVBoxLayout(Settings)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(Settings)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.variableTable = QtGui.QTableWidget(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.variableTable.sizePolicy().hasHeightForWidth())
        self.variableTable.setSizePolicy(sizePolicy)
        self.variableTable.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.variableTable.setRowCount(0)
        self.variableTable.setObjectName(_fromUtf8("variableTable"))
        self.variableTable.setColumnCount(2)
        self.variableTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.variableTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.variableTable.setHorizontalHeaderItem(1, item)
        self.variableTable.horizontalHeader().setCascadingSectionResizes(False)
        self.variableTable.horizontalHeader().setDefaultSectionSize(130)
        self.variableTable.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.variableTable, 0, 0, 3, 1)
        self.addButton = QtGui.QPushButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon)
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.gridLayout.addWidget(self.addButton, 0, 1, 1, 1)
        self.removeButton = QtGui.QPushButton(self.groupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeButton.setIcon(icon1)
        self.removeButton.setObjectName(_fromUtf8("removeButton"))
        self.gridLayout.addWidget(self.removeButton, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Settings)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.pollingIntervalSpinbox = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.pollingIntervalSpinbox.setSuffix(_fromUtf8(" sec"))
        self.pollingIntervalSpinbox.setMinimum(0.5)
        self.pollingIntervalSpinbox.setMaximum(5000000.0)
        self.pollingIntervalSpinbox.setSingleStep(0.5)
        self.pollingIntervalSpinbox.setObjectName(_fromUtf8("pollingIntervalSpinbox"))
        self.gridLayout_2.addWidget(self.pollingIntervalSpinbox, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.sleepTimeSpinbox = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.sleepTimeSpinbox.setSuffix(_fromUtf8(" sec"))
        self.sleepTimeSpinbox.setMinimum(0.0)
        self.sleepTimeSpinbox.setMaximum(5.0)
        self.sleepTimeSpinbox.setSingleStep(0.1)
        self.sleepTimeSpinbox.setProperty(_fromUtf8("value"), 0.5)
        self.sleepTimeSpinbox.setObjectName(_fromUtf8("sleepTimeSpinbox"))
        self.gridLayout_2.addWidget(self.sleepTimeSpinbox, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.line = QtGui.QFrame(Settings)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.label_3 = QtGui.QLabel(Settings)
        self.label_3.setToolTip(_fromUtf8(""))
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setWordWrap(True)
        self.label_3.setIndent(0)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QtGui.QApplication.translate("Settings", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Settings", "Environment Variables", None, QtGui.QApplication.UnicodeUTF8))
        self.variableTable.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Settings", "Variable name", None, QtGui.QApplication.UnicodeUTF8))
        self.variableTable.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Settings", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("Settings", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("Settings", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Settings", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Settings", "Polling interval:", None, QtGui.QApplication.UnicodeUTF8))
        self.pollingIntervalSpinbox.setToolTip(QtGui.QApplication.translate("Settings", "Update service status every x seconds.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Settings", "Append sleep to start/stop command:", None, QtGui.QApplication.UnicodeUTF8))
        self.sleepTimeSpinbox.setToolTip(QtGui.QApplication.translate("Settings", "Wait x seconds after execution of start/stop commands before rechecking service status.\n"
"If the status immediatly flashes back to inactive when starting a service, increase this value.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Settings", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Nimbus Sans L\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Environment Variables:</span> Set bash variables which are available in the commands. Please ensure that all needed variables are set here if certain services do not work.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Settings:</span> Hover over the input fields for help.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import Icons_Default_rc
