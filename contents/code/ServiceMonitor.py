# -*- coding: utf-8 -*-
import sys, dbus

from functools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import *
from PyKDE4.plasmascript import *
from PyKDE4.kdeui import *

from generated.indicators_default_rc import *
from generated.Password_ui import *
from ConfigDialog import *
from PasswordDialog import *


contentsdir = os.path.dirname(os.path.dirname(__file__))
codedir     = contentsdir + "/code"
sourcedir   = contentsdir + "/sources"


## This is the plasmoid which can be placed on the desktop or in dock.
# First the config dialog is initialised which loads all sources, services and configuration.
# Then the applet gets the list of active services from the config, draws all widgets and sets up monitoring.
class ServiceMonitor(Applet):


  def __init__(self, parent, args=None):
    Applet.__init__(self, parent)
    self.widgets = {}      ##< [dict] Place for all widgets, so they can be addressed nicely.
    self.mainLayout = None ##< [QLayout] The layout containing all the widgets.
    

  def init(self):

    # Konfig-Dialog einrichten
    self.setHasConfigurationInterface(True)
    self.configDialog = ConfigDialog(self)
    self.configDialog.configurationChanged.connect(self.setupServicesAndWidgets)

    # Passwort-Dialog
    self.passwordDialog = PasswordDialog(self.configDialog)

    # Benutzeroberfläche einrichten
    if self.formFactor() == Plasma.Planar:
      self.mode = 'desktop'
      self.setupAppletUi()
    else:
      self.mode = 'popup'
      self.setupPopupUi()
      
    QTimer.singleShot(0, self.mainLayout.invalidate) # seems to be necessary only on start

    # Widgets im Main-Layout erzeugen, Timer starten
    self.setupServicesAndWidgets()
    


  ## Sets up all widgets in a popup which can be opened when clicking the applet.
  def setupPopupUi(self):
    self.mode = 'popup'

    # QGraphicsView initialisieren, in das alles gezeichnet wird
    self.scene = QGraphicsScene()
    self.view = QGraphicsView()
    self.view.setScene(self.scene)
    self.view.setFrameStyle(QFrame.NoFrame)
    self.view.setStyleSheet('background-color: transparent;')
    self.view.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # Layout-Container-Widget erzeugen und in die Szene einfügen
    self.container = QGraphicsWidget()
    self.mainLayout = QGraphicsGridLayout()
    self.container.setLayout(self.mainLayout)
    self.scene.addItem(self.container)
    self.mainLayout.setPreferredWidth(270)

    # Popup erzeugen
    self.popup = Plasma.Dialog()
    self.popup.setWindowFlags(Qt.Popup)
    self.popupLayout = QVBoxLayout()
    self.popup.setLayout(self.popupLayout)
    self.popupLayout.addWidget(self.view)
    self.popup.resize(250, 300)

    # Im Applet ein Icon anzeigen
    self.icon = Plasma.IconWidget(KIcon(":/panel-icon.png"), "")
    self.iconLayout = QGraphicsLinearLayout()
    self.iconLayout.addItem(self.icon)
    self.setAspectRatioMode(Plasma.ConstrainedSquare)
    self.applet.setLayout(self.iconLayout)
    self.icon.clicked.connect(self.togglePopup)


  ## Sets up all widgets directly in the main applet.
  def setupAppletUi(self):
    self.verticalLayout = QGraphicsLinearLayout(Qt.Vertical)
    self.setLayout(self.verticalLayout)
    self.mainLayout = QGraphicsGridLayout()
    self.verticalLayout.addItem(self.mainLayout)
    self.verticalLayout.addStretch(1)
    self.applet.setAspectRatioMode(Plasma.IgnoreAspectRatio)


  ## Open the config dialog; called by plasma.
  def showConfigurationInterface(self):
    self.configDialog.show()


  ## Triggered on wrongPassword signal. Retries the last command.
  def askPasswordAndRetry(self, service):
    try: self.passwordDialog.newPasswordAvailable.disconnect()
    except: pass # if no slots are connected
    self.passwordDialog.setWindowTitle(service.name)
    self.passwordDialog.setCommandInfo(getattr(service, service.lastCommand()))
    self.passwordDialog.focusPasswordField()
    self.passwordDialog.setVisible(True)
    def retry(pw):
      self.passwordDialog.setVisible(False)
      QTimer.singleShot(0, partial(service.retryLastCommand, pw))
    self.passwordDialog.newPasswordAvailable[QString].connect(retry)


  ## Create all widgets inside the main layout and set up the services for monitoring.
  # This function is called as slot whenever the configuration has changed.
  @pyqtSlot()
  def setupServicesAndWidgets(self):

    # Alte Widgets löschen und Szene leeren
    while self.mainLayout.count():
      self.mainLayout.itemAt(0).graphicsItem().deleteLater()
      self.mainLayout.removeAt(0)
    self.widgets = {}

    activeServices = self.configDialog.activeServices()

    # Falls Services eingerichtet: Service-Widgets anzeigen
    if activeServices:
      for i, service in enumerate(activeServices):
        nameLabel = Plasma.Label()
        statusIcon = Plasma.IconWidget('')
        self.widgets[service.id] = { 'name': nameLabel, 'status': statusIcon }
        nameLabel.setText(u'<strong>%s</strong>' % service.name)
        nameLabel.nativeWidget().setWordWrap(False)
        statusIcon.setMinimumHeight(22)
        statusIcon.setMaximumHeight(22)
        statusIcon.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.refreshStateIcon(service)
        if self.mode == 'icons':
          self.mainLayout.addItem(statusIcon, 0, i)
        else:
          self.mainLayout.addItem(statusIcon, i, 0)
          self.mainLayout.addItem(nameLabel, i, 1)
        statusIcon.clicked.connect(partial(self.iconClicked, service))

    # Falls keine Services eingerichtet: Einleitungstext anzeigen
    if not activeServices:
      self.widgets['intro'] = Plasma.Label()
      self.widgets['intro'].setText(self.tr('<b>Thank you for downloading<br/>Service Monitor!</b><br/><br/>Right click to open the<br/>settings dialog.'))
      self.mainLayout.addItem(self.widgets['intro'], 0, 0)

    # Hier ist das Layout eingerichtet - aktivieren
    self.mainLayout.activate()

    # Scrollbarer Bereich verkleinert sich nicht automatisch im Popup, also von Hand
    if hasattr(self, 'popup'):
      self.container.adjustSize()
      self.scene.setSceneRect(self.container.geometry())

    # Alle Polling-Prozesse anhalten und alte Connections trennen
    for service in self.configDialog.allServices():
      service.setPolling(False)
      try: service.runningStateChanged.disconnect()
      except: pass

    # Aktive Prozesse neu einrichten und Polling starten
    interval = self.configDialog.pollingInterval()
    sleepTime = self.configDialog.sleepTime()
    for service in activeServices:
      service.runningStateChanged.connect(partial(self.refreshStateIcon, service))
      service.wrongPassword[str].connect(partial(self.askPasswordAndRetry, service))
      service.setSleepTime(sleepTime)
      service.setErrorReporting(not self.configDialog.suppressStdout())
      service.setPolling(True, interval)


  ## Starts or stops a service corresponding to the icon clicked.
  def iconClicked(self, service):
    if service.state[0] == 'missing':
      QMessageBox.warning(None, self.tr("Error"), self.tr('Service "%1" not installed. Aborting.').arg(service.id))
      return
    if service.state[1] in ['running', 'starting']: command = "stopcommand"
    if service.state[1] in ['stopped', 'stopping']: command = "startcommand"
    service.execute(command, 'requested', self.passwordDialog.password())


  ## Updates the icon corresponding to the service argument.
  def refreshStateIcon(self, service, reason = ''):
    icon = self.configDialog.runningStateIndicator(service)
    self.widgets[service.id]['status'].setIcon(icon)

    # send a KNotify notification if the change wasn't issued by the user
    if self.configDialog.useKNotify() and service.state[1] in ["running", "stopped"] and reason == 'polling':
      if service.state[1] == "running":
        message = self.tr("%1 is now running.").arg(service.name)
      else:
        message = self.tr("%1 has been stopped.").arg(service.name)
      self.knotify(icon, message)


  ## The call to knotify must be made from an external script, because python allows no self-connections
  def knotify(self, icon, message):
    byteArray = QByteArray()
    buffer = QBuffer(byteArray)
    icon.pixmap(QSize(32, 32)).toImage().rgbSwapped().save(buffer, "PNG") # KNotify seems to expect a BGR file
    tmp = file('icon.png', 'w')
    tmp.write(byteArray.data())
    tmp.close()
    self.knotifyProcess = KProcess()
    self.knotifyProcess.setProgram(QStringList() << "/usr/bin/python" << ("%s/KNotify.py" % codedir) << message)
    self.knotifyProcess.start()


  ## Shows/hides popup dialog.
  @pyqtSlot()
  def togglePopup(self):
    if self.popup.isVisible():
      self.popup.animatedHide(Plasma.Direction(0))
    else:
      self.popup.move(self.popupPosition(self.popup.sizeHint()))
      self.popup.animatedShow(Plasma.Direction(0))

