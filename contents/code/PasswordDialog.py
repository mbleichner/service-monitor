# -*- coding: utf-8 -*-
from functools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from generated.Password_ui import *

class PasswordDialog(QDialog, Ui_PasswordDialog):

  passwordAvailable = pyqtSignal(QString)

  def __init__(self, configDialog, parent = None):
    QDialog.__init__(self, parent)
    self.configDialog = configDialog
    self._password = ''
    self.config = QSettings('KDE Plasmoid', 'Service Monitor') ##< [QSettings] Internal config object.

    self.setupUi(self)
    self.rememberTimeCombobox.setCurrentIndex(self.configDialog.rememberType())
    self.rememberTimeSpinbox.setValue(self.configDialog.rememberTime())
    self.rememberTimeSpinbox.setEnabled(self.rememberTimeCombobox.currentIndex() == 1) # "Remember for fixed time"
    self.setFixedSize(self.sizeHint())

    self.rememberTimeCombobox.currentIndexChanged[int].connect(self.rememberTypeChanged)
    self.rememberTimeSpinbox.valueChanged[int].connect(self.rememberTimeChanged)
    self.buttonBox.accepted.connect(self.savePassword)

  def savePassword(self):
    self._password = self.passwordLineEdit.text()
    self.passwordAvailable.emit(self.password())


  def resetPassword(self):
    self.passwordLineEdit.setText("")

  def rememberTypeChanged(self, index):
    self.configDialog.setRememberType(index)
    self.rememberTimeSpinbox.setEnabled(index == 1) # "Remember for fixed time"

  def rememberTimeChanged(self, value):
    self.configDialog.setRememberTime(value)

  def password(self):
    return self._password
    