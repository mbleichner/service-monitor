# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyKDE4.kdecore import *


class ShellProcess(KProcess):

  def __init__(self, command, parent = None):
    KProcess.__init__(self, parent)
    command = command.replace('$INITDIR', '/etc/init.d')
    self.setOutputChannelMode(KProcess.MergedChannels)
    self.setProgram(self.generateProgram(command))

  def generateProgram(self, command):
    return QStringList() << "/bin/bash" << "-c" << command


class RootProcess(ShellProcess):

  wrongPassword = pyqtSignal()

  def __init__(self, command, password, parent = None):
    ShellProcess.__init__(self, command, parent)
    self.password = password

  def generateProgram(self, command):
    return (QStringList() << "/usr/bin/sudo" << "-kS") + ShellProcess.generateProgram(self, command)

  def start(self):
    ShellProcess.start(self)
    self.state = 'prompt'
    self.waitForReadyRead()
    output = self.readAllStandardOutput()
    if output.contains("password for"):
      self.write("%s\n" % self.password)
    else:
      print "sudo error:", output
    self.readyReadStandardOutput.connect(self.processOutput)

  def processOutput(self):    
    output = self.readAllStandardOutput()
    if output.contains("try again"):
      self.wrongPassword.emit()
    if output.contains("not in the sudoers file"):
      print "sudo error:", output
      self.terminate()
      self.close()





    