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
    node.setAttribute('id',       self.id)
    node.setAttribute('icon',     self.icon if self.icon else "")
    node.setAttribute('priority', self.priority if self.priority else 0)
    node.setAttribute('sudo',     "yes" if self.sudo else "no")
    node.appendChild(mkTextElement(doc, 'name',         self.name))
    node.appendChild(mkTextElement(doc, 'description',  self.description))
    node.appendChild(mkTextElement(doc, 'installcheck', self.installcheck))
    node.appendChild(mkTextElement(doc, 'runningcheck', self.runningcheck))
    node.appendChild(mkTextElement(doc, 'startcommand', self.startcommand))
    node.appendChild(mkTextElement(doc, 'stopcommand',  self.stopcommand))
    return node


  ## Activates or deactivates state polling.
  def setPolling(self, flag, interval = None):
    self.polling = flag
    if self.polling:
      if interval:
        self.timer.setInterval(interval*1000)
      self.timer.start()
      self.execute("runningcheck", 'initial-polling')
    else:
      self.timer.stop()


  ## If set to false, error output on start/stop commands will not be reported though a message box.
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


  ## Convenience method for updateing the state,
  def setRunningState(self, runningState, reason):
    self.setState( (self.state[0], runningState), reason )


  ## Convenience method for updateing the state,
  def setInstallState(self, installState, reason):
    self.setState( (installState, self.state[1]), reason )


  ## Initiates execution of a command or check.
  ## @param reason reflects the reason for the execution (automatic polling, user request or widget startup)
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
      if self.sudo: proc.setSudoPassword(password)
      self._lastCommand = which # remember for the case we have to retry
    else:
      proc.setBashCommand(command)
      
    # connect slot and start process
    proc.finished.connect(partial(self.finished, which, reason))
    errorCode = proc.start()

    # check for startup or sudo errors. if no error occurred, update the service state
    if errorCode == BashProcess.StartupError:
      QMessageBox.critical(None, self.tr('Process failed to start'), self.tr('Process failed to start. This should not happen and maybe it is a serious bug.'))
    elif errorCode == BashProcess.SudoError:
      QMessageBox.critical(None, self.tr('Sudo installation error'), self.tr("Sudo could not be started. Make sure it is installed correctly."))
    elif errorCode == BashProcess.PermissionError:
      QMessageBox.critical(None, self.tr('Sudo permission error'), self.tr("Sudo permission error. Are you sure sudo configured correctly? If you need help, use the sudo tool in the configuration dialog of Service Monitor."))
    elif errorCode == BashProcess.PasswordError:
      self.wrongPassword.emit(which)
    elif which in ["startcommand", "stopcommand"]:
      self.setRunningState("starting" if which == "startcommand" else "stopping", reason)
    

  ## Called when a command or check finishes. This method checks the exit status and updates the state of the service.
  def finished(self, which, reason):
    proc = self.processes[which]

    # check for errors
    if which == "installcheck":
      self.setInstallState('installed' if (proc.exitCode() == 0 and proc.readAllStandardOutput().length() > 0) else 'missing', reason)
    elif which == "runningcheck":
      self.setRunningState('running' if (proc.exitCode() == 0 and proc.readAllStandardOutput().length() > 0) else 'stopped', reason)
    elif which in ['startcommand', 'stopcommand']:
      errorOutput = QString(proc.readAllStandardError())
      if errorOutput and self.reportErrors:
        QMessageBox.warning(None, self.tr('Error output'), errorOutput)
      self.execute('runningcheck', reason)


  ## Retries the last command. Called (externally) when there was a password error.
  def retryLastCommand(self, password):
    if not self.lastCommand(): return
    self.execute(self.lastCommand(), 'requested', password)


  ## Returns the identifier of the last command executed.
  def lastCommand(self):
    return self._lastCommand if self._lastCommand else None


  ## Sets a sleep time to be appended to all commands.
  def setSleepTime(self, n):
    self.sleepTime = n


  ## Kills all given processes.
  def killProcesses(self, *args):
    for which in args:
      self.processes[which].kill()
