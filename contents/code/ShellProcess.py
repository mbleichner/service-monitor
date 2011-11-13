# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyKDE4.kdecore import *


class ShellProcess(KProcess):

  def __init__(self, command, parent = None):
    KProcess.__init__(self, parent)
    self.setOutputChannelMode(KProcess.MergedChannels)
    self.setProgram(self.generateProgram(command))

  def generateProgram(self, command):
    return QStringList() << "/bin/bash" << "-c" << command


class RootProcess(ShellProcess):

  def __init__(self, command, rootpw, parent = None):
    ShellProcess.__init__(self, command, parent)
    self.rootpw = rootpw

  def generateProgram(self, command):
    return (QStringList() << "/usr/bin/sudo" << "-kS") + ShellProcess.generateProgram(self, command)

  def start(self):
    ShellProcess.start(self)
    self.waitForReadyRead()
    prompt = self.readAllStandardOutput()
    if "password for" not in prompt:
      print "sudo not installed?"
      self.close()
    self.write(self.rootpw + '\n')
    self.waitForReadyRead()
    response = QString(self.readAllStandardOutput())
    if response.trimmed() == "Sorry, try again.":
      print "wrong sudo password"
      self.close()
    self.closeWriteChannel()



    