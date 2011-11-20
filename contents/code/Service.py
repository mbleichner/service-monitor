# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *

from ShellProcess import *
from time import *
from functools import *

## Container for service definitions and state polling.
# This class manages a list of processes which perform install/running checks and
# it can be set up to monitor its own state. When the state changes, the stateChanged()
# signal is emitted.
class Service(QObject):


  def __init__(self, parent = None):
    QObject.__init__(self, parent)
    self.parent = self.source = parent

    self.id = ''
    self.name = ''
    self.priority = 0
    self.description = ''
    self.installCheck = ''
    self.runningCheck = ''
    self.startCommand = ''
    self.stopCommand = ''
    self.process = None
    self.sleepTime = 0
    self.state = ('unknown', 'unknown')   # (Install-Status, Running-Status)
    self.interval = 4000
    self.polling = False
    self.timer = QTimer()
    self.timer.setSingleShot(True)
    QObject.connect(self.timer, SIGNAL('timeout()'), partial(self.execute, "runningcheck"))


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


  ## Sets the polling interval for this service.
  # @param interval the interval in seconds.
  def setPollingInterval(self, interval):
    self.timer.setInterval(interval*1000)


  ## Starts polling with the interval set up by setPollingInterval().
  def startPolling(self):
    self.polling = True
    self.timer.start()
    self.execute("runningcheck")


  ## Stops polling...
  def stopPolling(self):
    self.polling = False


  def execRunningCheck(self): self.execute("runningcheck")
  def execInstallCheck(self): self.execute("installcheck")
  def execStartCommand(self): self.execute("startcommand")
  def execStopCommand(self):  self.execute("stopcommand")


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
    self.killRunningProcess()
    self.timer.stop()
    if "command" in which:
      self.process = RootProcess(self.startCommand if which == "startcommand" else self.stopCommand)
      self.setRunningState("starting" if which == "startcommand" else "stopping")
    else:
      self.process = ShellProcess(self.runningCheck if which == "runningcheck" else self.installCheck)
    QObject.connect(self.process, SIGNAL('finished(int)'), partial(self.procFinished, which))
    QTimer.singleShot(0, self.process.start)


  def procFinished(self, which):
    errorOutput = QString(self.process.readAllStandardError())
    if errorOutput:
      QMessageBox.critical(None, self.name, self.tr('The command produced the following error:') + '\n' + errorOutput, QMessageBox.Ok)
    if which == "installcheck":
      self.setInstallState('installed' if (self.process.exitCode() == 0 and self.process.readAll().length() > 0) else 'missing')
    if which == "runningcheck":
      self.setRunningState('running' if (self.process.exitCode() == 0 and self.process.readAll().length() > 0) else 'stopped')
    if self.polling:
      self.timer.start()
    self.killRunningProcess()


  ## Sets a sleep time to be appended to all commands.
  def setSleepTime(self, n):
    self.sleepTime = n


  ## [internal] Kills all running Processes.
  def killRunningProcess(self):
    if self.process is not None:
      #QObject.disconnect(self.process, self)
      self.process.deleteLater()
      self.process = None


## Shortcut for creating a DOM element containing text data.
def mkTextElement(doc, tagName, textData):
  node = doc.createElement(tagName)
  textNode = doc.createTextNode(textData)
  node.appendChild(textNode)
  return node