# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyKDE4.kdecore import *


## Allows execution of bash scripts with possibility to use sudo.
## If sudo should be used, simply set the password via setSudoPassword().
## Commands can contain the $INITDIR variable, which is replaced by /etc/init.d or
## /etc/rc.d, depending on the distribution.
class BashProcess(KProcess):
  
  PasswordError      = 11
  PermissionError    = 12

  def __init__(self, parent = None):
    KProcess.__init__(self, parent)
    self._errorType = None
    self._errorMessage = None
    self._password = None
    self._command = ''

  ## Sets the password which is forwarded to sudo.
  def setSudoPassword(self, pw):
    self._password = pw

  ## Returns true if sudo should be used to execute the command.
  def usesSudo(self):
    return self._password is not None

  ## Returns the type of the last error.
  def errorType(self):
    return self._errorType if self._errorType is not None else KProcess.error(self)

  ## Sets the command to be executed. It may contain the variable $INITDIR, which will be replaced according to guessInitDir().
  def setBashCommand(self, command):
    command = command.replace('$INITDIR', self.guessInitDir())
    self._command = command

  ## Returns either /etc/init.d or /etc/rc.d (e.g. on Arch systems).
  def guessInitDir(self):
    return "/etc/rc.d" if QFile.exists("/etc/rc.d") else "/etc/init.d"

  ## Returns the human-readable message of the last error.
  def errorMessage(self):
    return self._errorMessage

  ## [internal] Convenience method.
  def spitError(self, code, msg):
    self._errorType = code
    self._errorMessage = msg
    self.terminate()
    self.close()
    self.error.emit(self.errorType())


  ## Starts the process. If we are using sudo and there is a sudo error (e.g. password or misconfiguration), it will immediately fail.
  ## If no error occured (or sudo isn't used), the process will be detached and the finished() signal can be used to get notified.
  def start(self):

    # setup program
    # Der Parameter -D 8 sorgt für eine sofortige Ausgabe nach erfolgreicher Passworteingabe.
    # Ohne den Parameter hängt start() sonst so lange, bis das Hauptkommando ferig ist oder eine Ausgabe produziert.
    program = QStringList()
    if self.usesSudo():
      program << "/usr/bin/sudo" << "-kS" << "-D 8" << "-p" << "enter sudo password: "
    program << "/bin/bash" << "-c" << self._command
    
    # start program
    self.setProgram(program)
    self.setProcessChannelMode(QProcess.SeparateChannels)
    KProcess.start(self)

    if self.usesSudo():

      # listen on stderr, since sudo prints everything there
      self.setReadChannel(QProcess.StandardError)

      # start sudo, check if password prompt is present, then enter the password
      self.waitForReadyRead()
      output = self.readAll()
      if not output.contains("enter sudo password:"):
        return self.spitError(QProcess.FailedToStart, "Please check your sudo installation")
      self.write("%s\n" % self._password)

      # wait for response and either issue an error or continue with normal process management
      self.waitForReadyRead(); output = self.readAll()
      if output.contains("try again"):
        return self.spitError(BashProcess.PasswordError, "Wrong sudo password")
      elif output.contains("not in the sudoers file"):
        return self.spitError(BashProcess.PermissionError, "Your user is not mentioned in the sudoers file")

