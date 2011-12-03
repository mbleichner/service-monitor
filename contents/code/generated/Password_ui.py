# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PasswordDialog(object):
    def setupUi(self, PasswordDialog):
        PasswordDialog.setObjectName(_fromUtf8("PasswordDialog"))
        PasswordDialog.resize(309, 173)
        PasswordDialog.setWindowTitle(QtGui.QApplication.translate("PasswordDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        PasswordDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(PasswordDialog)
        self.verticalLayout.setContentsMargins(15, 5, 15, 5)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(PasswordDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setText(QtGui.QApplication.translate("PasswordDialog", "Please enter your sudo password.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.label = QtGui.QLabel(PasswordDialog)
        self.label.setText(QtGui.QApplication.translate("PasswordDialog", "The following command will be executed:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.commandLabel = QtGui.QLabel(PasswordDialog)
        font = QtGui.QFont()
        font.setItalic(True)
        self.commandLabel.setFont(font)
        self.commandLabel.setText(QtGui.QApplication.translate("PasswordDialog", "/etc/init.d/apache stop", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLabel.setObjectName(_fromUtf8("commandLabel"))
        self.verticalLayout.addWidget(self.commandLabel)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.passwordLineEdit = QtGui.QLineEdit(PasswordDialog)
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordLineEdit.setObjectName(_fromUtf8("passwordLineEdit"))
        self.verticalLayout.addWidget(self.passwordLineEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.rememberTimeCombobox = QtGui.QComboBox(PasswordDialog)
        self.rememberTimeCombobox.setObjectName(_fromUtf8("rememberTimeCombobox"))
        self.rememberTimeCombobox.addItem(_fromUtf8(""))
        self.rememberTimeCombobox.setItemText(0, QtGui.QApplication.translate("PasswordDialog", "Remember for this session", None, QtGui.QApplication.UnicodeUTF8))
        self.rememberTimeCombobox.addItem(_fromUtf8(""))
        self.rememberTimeCombobox.setItemText(1, QtGui.QApplication.translate("PasswordDialog", "Remember for fixed time", None, QtGui.QApplication.UnicodeUTF8))
        self.rememberTimeCombobox.addItem(_fromUtf8(""))
        self.rememberTimeCombobox.setItemText(2, QtGui.QApplication.translate("PasswordDialog", "Do not remember", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontalLayout.addWidget(self.rememberTimeCombobox)
        self.rememberTimeSpinbox = QtGui.QSpinBox(PasswordDialog)
        self.rememberTimeSpinbox.setEnabled(False)
        self.rememberTimeSpinbox.setSuffix(QtGui.QApplication.translate("PasswordDialog", " min", None, QtGui.QApplication.UnicodeUTF8))
        self.rememberTimeSpinbox.setMinimum(1)
        self.rememberTimeSpinbox.setProperty("value", 60)
        self.rememberTimeSpinbox.setObjectName(_fromUtf8("rememberTimeSpinbox"))
        self.horizontalLayout.addWidget(self.rememberTimeSpinbox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(PasswordDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PasswordDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PasswordDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PasswordDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PasswordDialog)

    def retranslateUi(self, PasswordDialog):
        pass

