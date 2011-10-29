# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from time import *


## A QProcess which executes bash commands.
class ShellProcess(QProcess):

  def __init__(self, command, parent = None):
    QProcess.__init__(self, parent)
    self.command = QString(command)
    self.startTime = None

  def start(self):
    self.startTime = time()
    QProcess.start(self, '/bin/bash')
    self.waitForStarted()
    self.write(self.command.toUtf8())
    self.closeWriteChannel()

  def runningTime(self):
    return (time() - self.startTime) if self.startTime else None