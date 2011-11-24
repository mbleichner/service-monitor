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
    self.installcheck = ''
    self.runningcheck = ''
    self.startcommand = ''
    self.stopcommand = ''
    self.processes = {'runningcheck': None, 'installcheck': None, 'startcommand': None, 'stopcommand': None}
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
        service.installcheck  = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'runningcheck':
        service.runningcheck = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'startcommand':
        service.startcommand = node.toElement().firstChild().toText().data()
      if node.isElement() and node.toElement().tagName() == 'stopcommand':
        service.stopcommand = node.toElement().firstChild().toText().data()
      node = node.nextSibling()
    return service


  ## Outputs a DOM node containing all data of this service.
  def saveToDomNode(self, doc):
    node = doc.createElement('service')
    node.setAttribute('id', self.id)
    node.appendChild(mkTextElement(doc, 'name',         self.name))
    node.appendChild(mkTextElement(doc, 'description',  self.description))
    node.appendChild(mkTextElement(doc, 'installcheck', self.installcheck))
    node.appendChild(mkTextElement(doc, 'runningcheck', self.runningcheck))
    node.appendChild(mkTextElement(doc, 'startcommand', self.startcommand))
    node.appendChild(mkTextElement(doc, 'stopcommand',  self.stopcommand))
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
    command = getattr(self, which)
    if which in ["startcommand", "stopcommand"]:
      self.killProcesses('startcommand', 'stopcommand', 'runningcheck')
      proc = RootProcess(command)
      self.setRunningState("starting" if which == "startcommand" else "stopping")
    elif which in ["runningcheck", "installcheck"]:
      self.killProcesses(which)
      proc = ShellProcess(command)
    self.processes[which] = proc
    proc.finished.connect(partial(self.procFinished, which))
    print self.id, [x for x,y in self.processes.items() if y is not None]
    proc.start()


  def procFinished(self, which):
    proc = self.processes[which]
    if which == "installcheck":
      self.setInstallState('installed' if (proc.exitCode() == 0 and proc.readAll().length() > 0) else 'missing')
    if which == "runningcheck":
      self.setRunningState('running' if (proc.exitCode() == 0 and proc.readAll().length() > 0) else 'stopped')
    self.killProcesses(which)
    if self.polling and which in ['startcommand', 'stopcommand', 'runningcheck']:
      self.timer.start()


  ## Sets a sleep time to be appended to all commands.
  def setSleepTime(self, n):
    self.sleepTime = n


  def killProcesses(self, *args):
    for which in args:
      if self.processes[which] is not None:
        self.processes[which].deleteLater()
        self.processes[which] = None
