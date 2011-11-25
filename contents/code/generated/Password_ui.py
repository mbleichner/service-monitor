# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PasswordDialog(object):
    def setupUi(self, PasswordDialog):
        PasswordDialog.setObjectName(_fromUtf8("PasswordDialog"))
        PasswordDialog.resize(398, 61)
        PasswordDialog.setWindowTitle(QtGui.QApplication.translate("PasswordDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(PasswordDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(PasswordDialog)
        self.label.setText(QtGui.QApplication.translate("PasswordDialog", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.passwordLineEdit = QtGui.QLineEdit(PasswordDialog)
        self.passwordLineEdit.setObjectName(_fromUtf8("passwordLineEdit"))
        self.horizontalLayout.addWidget(self.passwordLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(PasswordDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PasswordDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PasswordDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PasswordDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PasswordDialog)

    def retranslateUi(self, PasswordDialog):
        pass

