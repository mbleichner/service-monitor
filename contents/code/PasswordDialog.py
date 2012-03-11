# -*- coding: utf-8 -*-
from functools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from generated.Password_ui import *


## A dialog which asks the user for his sudo password and can store it for a given time.
class PasswordDialog(QDialog, Ui_PasswordDialog):

  RememberForSession   = 0
  RememberForFixedTime = 1
  DoNotRemember        = 2

  ## This signal is triggered whenever the user entered a password and confirmed the dialog.
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


  ## Sets sensible default configuration values.
  def setConfigDefaults(self):
    if not self.config.contains('rememberType'): self.config.setValue('rememberType', 0)
    if not self.config.contains('rememberTime'): self.config.setValue('rememberTime', 60)


  ## Called when the user hits OK. Emits a signal to notify the main widget.
  def accepted(self):
    self._password = self.passwordLineEdit.text()
    self.newPasswordAvailable.emit(self._password)
    if self.rememberType() == PasswordDialog.RememberForSession:
      self.forgetTimer.stop()
    if self.rememberType() == PasswordDialog.RememberForFixedTime:
      self.forgetTimer.start()
    if self.rememberType() == PasswordDialog.DoNotRemember:
      self.forgetPassword()


  ## Saves value to config file. 
  def rememberTypeChanged(self, index):
    self.config.setValue('rememberType', index)
    self.rememberTimeSpinbox.setEnabled(index == PasswordDialog.RememberForFixedTime)


  ## Saves value to config file. 
  def rememberTimeChanged(self, minutes):
    self.config.setValue('rememberTime', minutes)
    self.forgetTimer.setInterval(minutes * 1000 * 60)


  ## Gets the configuration value for the combo box.
  def rememberType(self):
    return self.config.value('rememberType').toInt()[0]


  ## Gets the configuration value for the spin box.
  def rememberTime(self):
    return self.config.value('rememberTime').toInt()[0]


  ## Called when the forget timer triggers. Deletes the cached password.
  def forgetPassword(self):
    self._password = ''
    self.passwordLineEdit.setText('')


  ## Return the password given by the user.
  def password(self):
    return self._password


  ## Sets the command to be executed as an information for the user.
  def setCommandInfo(self, command):
    self.commandLabel.setText(command)
    self.adjustSize()


  ## Sets the cursor into the password field.
  def focusPasswordField(self):
    self.passwordLineEdit.setFocus(Qt.PopupFocusReason)
