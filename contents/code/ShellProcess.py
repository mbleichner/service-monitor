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

  def __init__(self, command, parent = None):
    ShellProcess.__init__(self, command, parent)
    self.password = ''

  def generateProgram(self, command):
    return (QStringList() << "/usr/bin/sudo" << "-kS") + ShellProcess.generateProgram(self, command)

  def start(self):
    ShellProcess.start(self)

    self.waitForReadyRead()

    output = QString(self.readAllStandardOutput())
    if output.contains("password for"):
      self.write("%s\n" % self.password)

    self.waitForReadyRead()

    output = QString(self.readAllStandardOutput())
    while output:
      if output.contains("password for"):
        print "wrong password",
        (self.password, success) = QInputDialog.getText(None, "", output)
        self.write("%s\n" % self.password)
      self.waitForReadyRead()
      output = QString(self.readAllStandardOutput())
      
    print "response", output
    if output.trimmed() == "Sorry, try again.":
      print "wrong sudo password"
    else:
      print "password correct"
      
    self.closeWriteChannel()



    