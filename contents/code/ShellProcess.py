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
    self.state = ''

  def generateProgram(self, command):
    return (QStringList() << "/usr/bin/sudo" << "-kS") + ShellProcess.generateProgram(self, command)

  def start(self):
    ShellProcess.start(self)
    self.state = 'prompt'
    self.readyReadStandardOutput.connect(self.inputReady)

  def inputReady(self):
    output = QString(self.readAllStandardOutput())
    if self.state == 'prompt' and output.contains("password for"):
      print "giving password to sudo:", self.password
      self.write("%s\n" % self.password)
      self.state = 'checkresult'
    elif self.state == 'checkresult':
      if "Sorry, try again." in output:
        print "wrong password"
        self.state = 'failed'
        self.wrongPassword.emit()
      else:
        self.state = 'success'
        print "password correct"
      self.close()



    