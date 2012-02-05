# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyKDE4.kdeui import *

from BashProcess import *
from time import *
from functools import *
from functions import *

## Container for service definitions and state polling.
# This class manages a list of processes which perform install/running checks and
# it can be set up to monitor its own state. When the state changes, the stateChanged()
# signal is emitted.
class Service(QObject):

  runningStateChanged = pyqtSignal(str)
  installStateChanged = pyqtSignal(str)
  wrongPassword = pyqtSignal(str)

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
    self.sudo = False
    self.icon = None
    self.processes = {'runningcheck': QProcess(), 'installcheck': QProcess(), 'startcommand': QProcess(), 'stopcommand': QProcess()}
    self.sleepTime = 0
    self.state = ('unknown', 'unknown')   # (Install-Status, Running-Status)
    self.polling = False
    self.reportErrors = True
    self._lastCommand = ''
    self.timer = QTimer()
    self.timer.setSingleShot(False)
    self.timer.setInterval(4000)
    self.timer.timeout.connect(partial(self.execute, 'runningcheck', 'polling'))


  ## [static] Creates a new service object from a DOM node.
  @staticmethod
  def loadFromDomNode(root, parent = None):
    assert root.isElement()
    root = root.toElement()
    service = Service(parent)
    service.id = root.attribute('id')
    if root.attribute('icon'):
      service.icon = root.attribute('icon')
    service.sudo = root.attribute('sudo', 'no') in ["yes", "true"]
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
    node.setAttribute('sudo', "yes" if self.sudo else "no")
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
      if interval:
        self.timer.setInterval(interval*1000)
      self.timer.start()
      self.execute("runningcheck", 'initial-polling')
    else:
      self.timer.stop()


  def setErrorReporting(self, flag):
    self.reportErrors = flag


  ## Shortcut for setting state and check if stateChanged() has to be emitted.
  def setState(self, newState, reason):
    oldState = self.state
    self.state = newState
    if newState[0] != oldState[0]:
      self.installStateChanged.emit(reason)
    if newState[1] != oldState[1]:
      self.runningStateChanged.emit(reason)


  def setRunningState(self, runningState, reason):
    self.setState( (self.state[0], runningState), reason )


  def setInstallState(self, installState, reason):
    self.setState( (installState, self.state[1]), reason )


  def execute(self, which, reason = 'requested', password = None):

    if which == 'runningcheck' and (self.processes['startcommand'].state() == QProcess.Running or self.processes['stopcommand'].state() == QProcess.Running):
      return

    # kill old processes
    if which in ["startcommand", "stopcommand"]:
      self.killProcesses('startcommand', 'stopcommand', 'runningcheck')
    elif which in ["runningcheck", "installcheck"]:
      self.killProcesses(which)

    # create new process
    command = getattr(self, which)
    proc = self.processes[which] = BashProcess()
    if which in ["startcommand", "stopcommand"]:
      proc.setBashCommand("%s\nsleep %.1f" % (command, self.sleepTime))
    else:
      proc.setBashCommand(command)
    if which in ["startcommand", "stopcommand"]:
      if self.sudo: proc.setSudoPassword(password)
      self._lastCommand = which
      
    # start process
    proc.start(); proc.waitForStarted()

    # check for startup errors
    if proc.errorType() == QProcess.FailedToStart and proc.errorMessage():
      QMessageBox.critical(None, self.tr('Command failed to start'), QString(proc.errorMessage()))
    elif proc.errorType() == QProcess.FailedToStart and not proc.errorMessage():
      QMessageBox.critical(None, self.tr('Command failed to start'), self.tr("There was an error starting the command. Please check your installation."))
    elif proc.errorType() == BashProcess.PermissionError:
      QMessageBox.critical(None, self.tr('Sudo permission error'), QString(proc.errorMessage()))
    elif proc.errorType() == BashProcess.PasswordError:
      self.wrongPassword.emit(which)

    # if everything went ok, mark state and connect slot
    if proc.state() == QProcess.Running:
      if which in ["startcommand", "stopcommand"]:
        self.setRunningState("starting" if which == "startcommand" else "stopping", reason)
      proc.finished.connect(partial(self.finished, which, reason))

    # if startup failed, issue state check
    else:
      self.execute('runningcheck', reason)
    

  def finished(self, which, reason):
    proc = self.processes[which]
    if which == "installcheck":
      self.setInstallState('installed' if (proc.exitCode() == 0 and proc.readAllStandardOutput().length() > 0) else 'missing', reason)
    elif which == "runningcheck":
      self.setRunningState('running' if (proc.exitCode() == 0 and proc.readAllStandardOutput().length() > 0) else 'stopped', reason)
    elif which in ['startcommand', 'stopcommand']:
      errorOutput = QString(proc.readAllStandardError())
      if errorOutput and self.reportErrors:
        QMessageBox.warning(None, self.tr('Error output'), errorOutput)
      self.execute('runningcheck', reason)
    self.killProcesses(which)


  def retryLastCommand(self, password):
    if not self.lastCommand(): return
    self.execute(self.lastCommand(), 'requested', password)


  def lastCommand(self):
    return self._lastCommand if self._lastCommand else None


  ## Sets a sleep time to be appended to all commands.
  def setSleepTime(self, n):
    self.sleepTime = n


  def killProcesses(self, *args):
    for which in args:
      if self.processes[which] is not None:
        self.processes[which].close()
