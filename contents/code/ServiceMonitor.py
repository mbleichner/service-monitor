# -*- coding: utf-8 -*-
from functools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import *
from PyKDE4.plasmascript import *
from PyKDE4.kdeui import *

import generated.indicators_default_rc
from generated.Password_ui import *

from ConfigDialog import *

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
    self.setupAppletUi() if self.formFactor() == Plasma.Planar else self.setupPopupUi()
    QTimer.singleShot(0, self.mainLayout.invalidate) # seems to be necessary only on start

    # Widgets im Main-Layout erzeugen, Timer starten
    self.setupServicesAndWidgets()
    


  ## Sets up all widgets in a popup which can be opened when clicking the applet.
  def setupPopupUi(self):

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
    try: self.passwordDialog.passwordAvailable.disconnect()
    except: pass
    self.passwordDialog.resetPassword()
    self.passwordDialog.setWindowTitle(service.name)
    self.passwordDialog.setVisible(True)
    def retry(pw):
      self.passwordDialog.setVisible(False)
      service.setSudoPassword(pw)
      QTimer.singleShot(0, service.retryLastCommand)
    self.passwordDialog.passwordAvailable[QString].connect(retry)


  ## [slot] Create all widgets inside the main layout and set up the services for monitoring.
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

    # Alle Polling-Prozesse anhalten
    for service in self.configDialog.allServices():
      service.setPolling(False)

    # Aktive Prozesse neu einrichten und Polling starten
    interval = self.configDialog.pollingInterval()
    sleepTime = self.configDialog.sleepTime()
    for service in activeServices:
      service.stateChanged.connect(partial(self.refreshStateIcon, service))
      service.wrongPassword[str].connect(partial(self.askPasswordAndRetry, service))
      service.setSleepTime(sleepTime)
      service.setPolling(True, interval)


  ## [slot] Starts or stops a service corresponding to the icon clicked.
  def iconClicked(self, service):
    if service.state[0] == 'missing':
      QMessageBox.warning(None, self.tr("Error"), self.tr('Service "%1" not installed. Aborting.').arg(service.id))
      return
    if service.state[1] in ['running', 'starting']: command = "stopcommand"
    if service.state[1] in ['stopped', 'stopping']: command = "startcommand"
    service.setSudoPassword(self.passwordDialog.password())
    service.execute(command)
    self.refreshStateIcon(service)


  ## Updates the icon corresponding to the service argument.
  def refreshStateIcon(self, service):
    icon = self.configDialog.runningStateIndicator(service)
    self.widgets[service.id]['status'].setIcon(icon)


  ## [slot] Shows/hides popup dialog.
  @pyqtSlot()
  def togglePopup(self):
    if self.popup.isVisible():
      self.popup.animatedHide(Plasma.Direction(0))
    else:
      self.popup.move(self.popupPosition(self.popup.sizeHint()))
      self.popup.animatedShow(Plasma.Direction(0))



class PasswordDialog(QDialog, Ui_PasswordDialog):

  passwordAvailable = pyqtSignal(QString)

  def __init__(self, configDialog, parent = None):
    QDialog.__init__(self, parent)
    self.configDialog = configDialog
    self._password = ''
    
    self.setupUi(self)
    self.rememberTimeCombobox.setCurrentIndex(self.configDialog.rememberType())
    self.rememberTimeSpinbox.setValue(self.configDialog.rememberTime())
    self.rememberTimeSpinbox.setEnabled(self.rememberTimeCombobox.currentIndex() == 1) # "Remember for fixed time"
    self.setFixedSize(self.sizeHint())
    
    self.rememberTimeCombobox.currentIndexChanged[int].connect(self.rememberTypeChanged)
    self.rememberTimeSpinbox.valueChanged[int].connect(self.rememberTimeChanged)
    self.buttonBox.accepted.connect(self.savePassword)

  def savePassword(self):
    self._password = self.passwordLineEdit.text()
    self.passwordAvailable.emit(self.password())


  def resetPassword(self):
    self.passwordLineEdit.setText("")

  def rememberTypeChanged(self, index):
    self.configDialog.setRememberType(index)
    self.rememberTimeSpinbox.setEnabled(index == 1) # "Remember for fixed time"

  def rememberTimeChanged(self, value):
    self.configDialog.setRememberTime(value)

  def password(self):
    return self._password
    