# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *

from ShellProcess import *
from time import *
from functools import *
from functions import *

## Container for service definitions and state polling.
# This class manages a list of processes which perform install/running checks and
# it can be set up to monitor its own state. When the state changes, the stateChanged()
# signal is emitted.
class Service(QObject):

  stateChanged = pyqtSignal()

  def __init__(self, parent = None):
    QObject.__init__(self, parent)
    self.parent = self.source = parent

    self.id = ''
    self.name = ''
    self.priority = 0
    self.overridden = False # indicates whether there is another service with the same id, but higher priority
    self.description = ''
    self.installCheck = ''
    self.runningCheck = ''
    self.startCommand = ''
    self.stopCommand = ''
    self.runningCheckProcess = None
    self.installCheckProcess = None
    self.commandProcess = None
    self.sleepTime = 0
    self.state = ('unknown', 'unknown')   # (Install-Status, Running-Status)
    self.polling = False
    self.timer = QTimer()
    self.timer.setSingleShot(True)
    self.timer.setInterval(4000)
    self.timer.timeout.connect(partial(self.execute, "runningcheck"))


  ## [static] Creates a new service object from a DOM node.
  @staticmethod
  def loadFromDomNode(root, parent = None):
    assert root.isElement()
    root = root.toElement()
    service = Service(parent)
    service.id = root.attribute('id')
    if not service.id: raise Exception('Service without ID')
    service.priority = root.attribute('priority')
    node = root.firstChild()
    while not node.isNull():
      if node.isElement() and node.toElement().tagName() == 'name':
        service.name = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'description':
        service.description = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'installcheck':
        service.installCheck  = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'runningcheck':
        service.runningCheck = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'startcommand':
        service.startCommand = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'stopcommand':
        service.stopCommand = node.toElement().firstChild().toText().data()
      node = node.nextSibling()
    return service


  ## Outputs a DOM node containing all data of this service.
  def saveToDomNode(self, doc):
    node = doc.createElement('service')
    node.setAttribute('id', self.id)
    node.appendChild(mkTextElement(doc, 'name',         self.name))
    node.appendChild(mkTextElement(doc, 'description',  self.description))
    node.appendChild(mkTextElement(doc, 'installcheck', self.installCheck))
    node.appendChild(mkTextElement(doc, 'runningcheck', self.runningCheck))
    node.appendChild(mkTextElement(doc, 'startcommand', self.startCommand))
    node.appendChild(mkTextElement(doc, 'stopcommand',  self.stopCommand))
    return node


  def setPolling(self, flag, interval = None):
    self.polling = flag
    if self.polling:
      if interval: self.timer.setInterval(interval*1000)
      self.timer.start()
      self.execute("runningcheck")
    else:
      self.timer.stop()


  ## Shortcut for setting state and check if stateChanged() has to be emitted.
  def setState(self, newState):
    oldState = self.state
    self.state = newState
    if newState != oldState:
      self.emit(SIGNAL('stateChanged()'))


  def setRunningState(self, runningState):
    self.setState( (self.state[0], runningState) )


  def setInstallState(self, installState):
    self.setState( (installState, self.state[1]) )


  def execute(self, which):
    self.timer.stop()
    if which in ["startcommand", "stopcommand"]:
      self.killCommandProcess()
      self.commandProcess = proc = RootProcess(self.startCommand if which == "startcommand" else self.stopCommand)
      self.setRunningState("starting" if which == "startcommand" else "stopping")
    elif which == "runningcheck":
      self.killRunningCheckProcess()
      self.runningCheckProcess = proc = ShellProcess(self.runningCheck)
    elif which == "installcheck":
      self.killInstallCheckProcess()
      self.installCheckProcess = proc = ShellProcess(self.installCheck)
    proc.finished.connect(partial(self.procFinished, which))
    proc.start()


  def procFinished(self, which):
    if which == "installcheck":
      self.setInstallState('installed' if (self.installCheckProcess.exitCode() == 0 and self.installCheckProcess.readAll().length() > 0) else 'missing')
      self.killInstallCheckProcess()
    if which == "runningcheck":
      self.setRunningState('running' if (self.runningCheckProcess.exitCode() == 0 and self.runningCheckProcess.readAll().length() > 0) else 'stopped')
      self.killRunningCheckProcess()
      if self.polling:
        self.timer.start()


  ## Sets a sleep time to be appended to all commands.
  def setSleepTime(self, n):
    self.sleepTime = n


  def killRunningCheckProcess(self):
    if self.runningCheckProcess is not None:
      self.runningCheckProcess.deleteLater()
      self.runningCheckProcess = None

  def killInstallCheckProcess(self):
    if self.installCheckProcess is not None:
      self.installCheckProcess.deleteLater()
      self.installCheckProcess = None
      
  def killCommandProcess(self):
    if self.commandProcess is not None:
      self.commandProcess.deleteLater()
      self.commandProcess = None