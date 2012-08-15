# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyKDE4.kdecore import *


## Allows execution of bash scripts with possibility to use sudo.
## If sudo should be used, simply set the password via setSudoPassword().
## Commands can contain the $INITDIR variable, which is replaced by /etc/init.d or
## /etc/rc.d, depending on the distribution.
class BashProcess(KProcess):

  NoError         = 0
  StartupError    = 1
  PermissionError = 2
  PasswordError   = 3
  SudoError       = 4

  def __init__(self, parent = None):
    KProcess.__init__(self, parent)
    self._errorType = None
    self._errorMessage = None
    self._password = None
    self._command = ''

  def kill(self):
    KProcess.kill(self)
    KProcess.close(self)
    
  ## Sets the password which is forwarded to sudo.
  def setSudoPassword(self, pw):
    self._password = pw

  ## Returns true if sudo should be used to execute the command.
  def usesSudo(self):
    return self._password is not None

  ## Sets the command to be executed. It may contain the variable $INITDIR, which will be replaced according to guessInitDir().
  def setBashCommand(self, command):
    command = command.replace('$INITDIR', self.guessInitDir())
    self._command = command

  ## Returns either /etc/init.d or /etc/rc.d (e.g. on Arch systems).
  def guessInitDir(self):
    return "/etc/rc.d" if QFile.exists("/etc/rc.d") else "/etc/init.d"

  ## [internal] Convenience method.
  def spitError(self, code, msg):
    self._errorType = code
    self._errorMessage = msg
    self.kill()
    self.close()
    self.error.emit(self.errorType())
    self.finished.emit(1, 0)

  ## Starts the process and returns an error code indicating startup errors (e.g. wrong password, sudo not installed, etc)
  ## If no error occured, the process is detached and fires the finished() signal when it terminates.
  def start(self):

    # setup program
    # Ohne den echo-Befehl hängt waitForReadyRead() so lange, bis das Hauptkommando fertig ist oder eine Ausgabe produziert.
    program = QStringList()
    if self.usesSudo():
      program << "/usr/bin/sudo" << "-kS" << "-p" << "enter sudo password: " << "/bin/bash" << "-c" << ("echo 'password ok' >&2\n" + self._command)
    else:
      program << "/bin/bash" << "-c" << self._command
    
    # start program
    self.setProgram(program)
    self.setProcessChannelMode(QProcess.SeparateChannels)
    KProcess.start(self)

    if self.error() == QProcess.FailedToStart:
      return StartupError

    if self.usesSudo():

      # listen on stderr, since sudo prints everything there
      self.setReadChannel(QProcess.StandardError)
      
      # start sudo, check if password prompt is present, then enter the password
      self.waitForReadyRead()
      output = self.readAll()
      if not output.contains("enter sudo password:"):
        self.kill()
        return BashProcess.SudoError
        
      self.write("%s\n" % self._password)

      # wait for response and either issue an error or continue with normal process management
      self.waitForReadyRead()
      output = self.readAll()
      if output.contains("try again"):
        self.kill()
        return BashProcess.PasswordError
      elif output.contains("not in the sudoers file"):
        self.kill()
        return BashProcess.PermissionError

    return 0
        
