# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyKDE4.kdecore import *

class BashProcess(KProcess):

  def __init__(self, command, parent = None):
    KProcess.__init__(self, parent)
    
    self._errorType = None
    self._errorTypeMessage = None
    
    self.setBashCommand(command)
    self.setProcessChannelMode(QProcess.SeparateChannels)

  def errorType(self):
    return self._errorType if self._errorType is not None else KProcess.error(self)

  def setBashCommand(self, command):
    command = command.replace('$INITDIR', '/etc/init.d')
    self.setProgram( QStringList() << "/bin/bash" << "-c" << command )

  def errorMessage(self):
    return self._errorTypeMessage

  def spitError(self, code, msg):
    self._errorType = code
    self._errorTypeMessage = msg
    self.terminate()
    self.close()
    self.error.emit(self.errorType())
  

class SudoBashProcess(BashProcess):
  
  PasswordError      = 11
  PermissionError    = 12
  
  wrongPassword = pyqtSignal()

  def __init__(self, command, password, parent = None):
    BashProcess.__init__(self, command, parent)
    self._password = password

  def setBashCommand(self, command):
    BashProcess.setBashCommand(self, command)
    self.setProgram( QStringList() << "/usr/bin/sudo" << "-kS" << "-D 8" << self.program() )
    # Der Parameter -D 8 sorgt für eine sofortige Ausgabe nach erfolgreicher Passworteingabe.
    # Ohne den Parameter hängt start() sonst so lange, bis das Hauptkommando ferig ist oder eine Ausgabe produziert.

  def start(self):

    # start sudo and listen on stderr, since sudo prints everything there
    BashProcess.start(self)
    self.setReadChannel(QProcess.StandardError)

    # start sudo, check if password prompt is present, then enter the password
    self.waitForReadyRead(); output = self.readAll()
    if not output.contains("password for"):
      return self.spitError(QProcess.FailedToStart, "please check your sudo installation")
    self.write("%s\n" % self._password)
    
    # wait for response and either issue an error or continue with normal process management
    self.waitForReadyRead(); output = self.readAll()
    if output.contains("try again"):
      return self.spitError(SudoBashProcess.PasswordError, "wrong sudo password")
    elif output.contains("not in the sudoers file"):
      return self.spitError(SudoBashProcess.PermissionError, "your user is not mentioned in the sudoers file")

