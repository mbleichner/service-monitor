# -*- coding: utf-8 -*-
from functools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from generated.Password_ui import *

class PasswordDialog(QDialog, Ui_PasswordDialog):

  RememberForSession   = 0
  RememberForFixedTime = 1
  DoNotRemember        = 2

  newPasswordAvailable = pyqtSignal(QString)

  def __init__(self, configDialog, parent = None):
    QDialog.__init__(self, parent)
    self._password = ''

    self.config = QSettings('plasma-desktop', 'service-monitor')
    self.setConfigDefaults()

    self.forgetTimer = QTimer()
    self.forgetTimer.setSingleShot(True)
    self.forgetTimer.timeout.connect(self.forgetPassword)

    self.setupUi(self)

    self.rememberTimeCombobox.currentIndexChanged[int].connect(self.rememberTypeChanged)
    self.rememberTimeSpinbox.valueChanged[int].connect(self.rememberTimeChanged)
    self.buttonBox.accepted.connect(self.accepted)
    
    self.rememberTimeCombobox.setCurrentIndex(self.rememberType())
    self.rememberTimeSpinbox.setValue(self.rememberTime())
    
  def setConfigDefaults(self):
    if not self.config.contains('rememberType'): self.config.setValue('rememberType', 0)
    if not self.config.contains('rememberTime'): self.config.setValue('rememberTime', 60)
    
  def accepted(self):
    self._password = self.passwordLineEdit.text()
    self.newPasswordAvailable.emit(self._password)
    if self.rememberType() == PasswordDialog.RememberForSession:
      self.forgetTimer.stop()
    if self.rememberType() == PasswordDialog.RememberForFixedTime:
      self.forgetTimer.start()
    if self.rememberType() == PasswordDialog.DoNotRemember:
      self.forgetPassword()

  def rememberTypeChanged(self, index):
    self.config.setValue('rememberType', index)
    self.rememberTimeSpinbox.setEnabled(index == PasswordDialog.RememberForFixedTime)

  def rememberTimeChanged(self, minutes):
    self.config.setValue('rememberTime', minutes)
    self.forgetTimer.setInterval(minutes * 1000 * 60)

  def rememberType(self):
    return self.config.value('rememberType').toInt()[0]

  def rememberTime(self):
    return self.config.value('rememberTime').toInt()[0]

  def forgetPassword(self):
    self._password = ''
    self.passwordLineEdit.setText('')

  def password(self):
    return self._password

  def setCommandInfo(self, command):
    self.commandLabel.setText(command)
    self.adjustSize()

  def focusPasswordField(self):
    self.passwordLineEdit.setFocus(Qt.PopupFocusReason)
