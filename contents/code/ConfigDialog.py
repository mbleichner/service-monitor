# -*- coding: utf-8 -*-
import shutil, random, os, sys, getpass, copy
from functools import *
from operator import attrgetter

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyKDE4.kdeui import *

from generated.Services_ui import *
from generated.Custom_ui import *
from generated.Sources_ui import *
from generated.Settings_ui import *
from generated.About_ui import *

from Source import *
from Service import *
from functions import *

contentsdir = os.path.dirname(os.path.dirname(__file__))
codedir     = contentsdir + "/code"
sourcedir   = contentsdir + "/sources"

## A KPageDialog for accessing and manipulating settings.
##
## This dialog consists of 4 pages: services, sources, settings and custom services,
## which are made in Qt Designer and simply provide the widgets. All the logic
## is contained in this class here.
##
## Whenever the configuration is changed, the signal configurationChanged() is emitted.
## This signal tells the ServiceMonitor class to re-setup its widgets and monitoring.
class ConfigDialog(KPageDialog):

  ## This signal is triggered whenever a configuration value changed.
  configurationChanged = pyqtSignal()

  ## Sets up pages, widgets and connections and loads the source files.
  def __init__(self, parent = None):
    KPageDialog.__init__(self)
    self.sources = {}       # Place for all xml sources, by ID.
    self.services = {}      # Place for all services, by ID. On collisions the priority is considered.
    self.editmode = False   # Indicates if editmode is on or off.
    self.cache = {}         # Cache for various things, currently only icons
    self.config = QSettings('plasma-desktop', 'service-monitor')

    # make sure the setting contain sane defaults
    self.setConfigDefaults()
    
    # Daten einlesen
    self.readSources()

    # Dialog einrichten, Pages hinzufügen
    self.setButtons(KDialog.ButtonCode(KDialog.Close))
    self.setCaption(self.tr('Service Monitor Configuration'))
    self.settingsPage = SettingsPage(self)
    self.servicesPage = ServicesPage(self)
    self.sourcesPage = SourcesPage(self)
    self.customPage = CustomPage(self)
    self.aboutPage = AboutPage(self)
    self.addPage(self.servicesPage, self.tr("Activate Services")).setIcon(KIcon("run-build-configure"))
    self.addPage(self.settingsPage, self.tr("Settings")).setIcon(KIcon("configure"))
    self.addPage(self.sourcesPage, self.tr("Manage Sources")).setIcon(KIcon("document-new"))
    self.addPage(self.customPage, self.tr("Custom Services")).setIcon(KIcon("edit-rename"))
    self.addPage(self.aboutPage, self.tr("About")).setIcon(KIcon("help-about"))

    # Settings page does not depend on other pages, load it directly
    self.populateSettings()

    # When opening one of the other pages, populate the corresponding widgets dynamically
    self.servicesPage.show.connect(chain(self.execInstallChecks, self.populateServiceLists))
    self.sourcesPage.show.connect(self.populateSourceList)
    self.customPage.show.connect(self.populateCustomList)
    
    # Connections für die ServicesPage
    self.servicesPage.activeServicesList.itemClicked[QListWidgetItem].connect(self.showServiceInfo)
    self.servicesPage.inactiveServicesList.itemClicked[QListWidgetItem].connect(self.showServiceInfo)
    self.servicesPage.activateButton.clicked.connect(self.activateService)
    self.servicesPage.deactivateButton.clicked.connect(self.deactivateService)
    self.servicesPage.sortUpButton.clicked.connect(self.sortUp)
    self.servicesPage.sortDownButton.clicked.connect(self.sortDown)
    self.servicesPage.sortTopButton.clicked.connect(self.sortTop)
    self.servicesPage.sortBottomButton.clicked.connect(self.sortBottom)
    self.servicesPage.hideUnavailableCheckBox.stateChanged.connect(self.refreshIndicatorsAndVisibility)

    # Connections für die SourcesPage
    self.sourcesPage.searchButton.clicked.connect(self.performUpdate)
    self.sourcesPage.sourceList.itemClicked[QListWidgetItem].connect(self.showSourceInfo)
    self.sourcesPage.sourceList.itemChanged[QListWidgetItem].connect(self.saveActiveSources)

    # Connections für die CustomPage
    self.customPage.serviceList.itemClicked[QListWidgetItem].connect(self.synchronizeLineEdits)
    self.customPage.serviceList.itemDoubleClicked[QListWidgetItem].connect(self.startEditmode)
    self.customPage.editButton.clicked.connect(self.toggleEditmode)
    self.customPage.removeButton.clicked.connect(self.removeCustomService)
    self.customPage.addButton.clicked.connect(self.addCustomService)
    self.customPage.shareButton.clicked.connect(self.uploadCustomService)
    self.customPage.copyComboBox.currentIndexChanged.connect(self.copyService)

    # Connections für die SettingsPage
    self.settingsPage.panelBehaviorComboBox.currentIndexChanged[int].connect(partial(self.saveConfigValue, 'panelBehavior'))
    self.settingsPage.pollingIntervalSpinbox.valueChanged[float].connect(partial(self.saveConfigValue, 'pollingInterval'))
    self.settingsPage.sleepTimeSpinbox.valueChanged[float].connect(partial(self.saveConfigValue, 'sleepTime'))
    self.settingsPage.iconStyleComboBox.currentIndexChanged[int].connect(partial(self.saveConfigValue, 'iconStyle'))
    self.settingsPage.themeComboBox.currentIndexChanged[QString].connect(partial(self.saveConfigValue, 'indicatorTheme'))
    self.settingsPage.suppressStdoutCheckBox.stateChanged[int].connect(partial(self.saveConfigValue, 'suppressStdout'))
    self.settingsPage.kNotifyCheckBox.stateChanged[int].connect(partial(self.saveConfigValue, 'useKNotify'))
    self.settingsPage.sudoHelperComboBox.currentIndexChanged[int].connect(self.showSudoSnippet)
    self.settingsPage.checkSudoButton.clicked.connect(self.checkSudo)

    # Cleanup actions when closing the config dialog
    self.closeClicked.connect(self.stopEditmode)

    # Sonstige Initialisierungaufgaben...
    self.settingsPage.sudoHelperDefaultText = self.settingsPage.sudoHelperTextarea.document().toPlainText()
    self.execInstallChecks()


  ## Executes install checks for all services.
  def execInstallChecks(self):
    for source in self.activeSources():
      for service in source.services:
        service.execute('installcheck', 'init-installstate')


  ## Initialize the internal QSettings object with sensible default values
  def setConfigDefaults(self):
    if not self.config.contains('panelBehavior'):   self.config.setValue('panelBehavior', 0)
    if not self.config.contains('suppressStdout'):  self.config.setValue('suppressStdout', 0)
    if not self.config.contains('useKNotify'):      self.config.setValue('useKNotify', Qt.Checked)
    if not self.config.contains('pollingInterval'): self.config.setValue('pollingInterval', 4.0)
    if not self.config.contains('sleepTime'):       self.config.setValue('sleepTime', 0.5)
    if not self.config.contains('indicatorTheme'):  self.config.setValue('indicatorTheme', 'plusminus')
    if not self.config.contains('iconStyle'):       self.config.setValue('iconStyle', 2)
    if not self.config.contains('activeSources'):   self.config.setValue('activeSources', QStringList() << "daemons-common.xml" << "tools-settings.xml")


  ## Parses all XML source files and loads containing services.
  def readSources(self):
    self.sources = {}
    self.services = {}
    print 'loading definition source files from %s...' % sourcedir
    for fn in [fn for fn in os.listdir(sourcedir) if fn.endswith('.xml') and not fn.startswith('.') ]:
      try: source = Source('%s/%s' % (sourcedir, fn))
      except: print 'Error parsing %s.' % fn; continue
      self.sources[source.filename] = source
      for service in source.services:
        if not self.services.has_key(service.id) or self.services[service.id].priority <= service.priority:
          self.services[service.id] = service
          service.installStateChanged.connect(partial(self.refreshIndicatorsAndVisibility, service))
          service.overridden = False
        else:
          service.overridden = True
      print '* loaded %s (%i services).' % (fn, len(source.services))


# PUBLIC GETTERS ###########################################################################################################


  ## Returns a list of all services.
  ## On ID collisions only the one with higher priority is contained in the list.
  def allServices(self):
    return self.services.values()


  ## Returns the list of active services.
  ## This function may return fewer services than the config file contains because there might be temporarily unavailable services.
  ## Such services will not be removed from the config, as they might be available again later.
  def activeServices(self):
    activeServicesIDs = self.config.value('activeServices').toStringList()
    activeSourcesIDs = [s.filename for s in self.activeSources()]
    return [self.services[id] for id in activeServicesIDs if self.services.has_key(id) and self.services[id].source.filename in activeSourcesIDs]


  ## Returns the list of active services.
  def activeSources(self):
    activeSourcesIDs = sorted(list(set(self.config.value('activeSources').toStringList() + ["custom.xml"])))
    return [self.sources[id] for id in activeSourcesIDs if self.sources.has_key(id)]


  ## Returns the polling interval from the settings page.
  def pollingInterval(self):
    return self.config.value('pollingInterval').toDouble()[0]


  ## Returns the sleep time from the settings page.
  def sleepTime(self):
    return self.config.value('sleepTime').toDouble()[0]


  ## Returns the sleep time from the settings page.
  def iconStyle(self):
    return self.config.value('iconStyle').toInt()[0]


  ## Returns the name of the theme for the state indicator icons.
  def indicatorTheme(self):
    theme = self.config.value('indicatorTheme').toString()
    return theme if theme and os.path.isdir(codedir + '/indicators/' + theme) else 'default'

  ## Returns a QIcon for the given service.
  def serviceIcon(self, service):
    if service.icon is not None and QFile.exists('%s/icons/%s.png' % (sourcedir, service.icon)):
      return QIcon('%s/icons/%s.png' % (sourcedir, service.icon))
    return KIcon(service.icon) if service.icon is not None else QIcon(':/panel-icon.png')


  ## Returns the install state icon for the given service.
  def installStateIndicator(self, service):
    style = self.iconStyle()
    theme = self.indicatorTheme()
    key = ('icon', 'installstate', style, theme, service.icon, service.state)
    if not self.cache.has_key(key):
      indicator = QIcon("%s/indicators/%s/%s.png" % (codedir, theme, service.state[0]))
      icon = self.serviceIcon(service)
      sat = {'installed': 1, 'unknown': 0.5, 'missing': 0}[service.state[0]]
      if style == 0:
        self.cache[key] = indicator
      elif style == 1:
        self.cache[key] = changeSaturation(icon, sat)
      else:
        self.cache[key] = combineIcons(changeSaturation(icon, sat), indicator)
    return self.cache[key]


  ## Returns the running state icon for the given service.
  def runningStateIndicator(self, service):
    style = self.iconStyle()
    theme = self.indicatorTheme()
    key = ('icon', 'runningstate', style, theme, service.icon, service.state)
    if not self.cache.has_key(key):
      indicator = QIcon("%s/indicators/%s/%s.png" % (codedir, theme, service.state[1]))
      icon = self.serviceIcon(service)
      sat = {'running': 1, 'starting': 0.5, 'stopping': 0.5, 'unknown': 0, 'stopped': 0}[service.state[1]]
      if style == 0:
        self.cache[key] = indicator
      elif style == 1:
        self.cache[key] = changeSaturation(icon, sat)
      else:
        self.cache[key] = combineIcons(changeSaturation(icon, sat), indicator)
    return self.cache[key]


  ## Returns the value of the "suppress stdout" setting.
  def suppressStdout(self):
    return self.config.value('suppressStdout').toInt()[0] > 0


  ## Returns the value of the "behavior when put into panel" setting.
  def panelBehavior(self):
    return self.config.value('panelBehavior').toInt()[0]


  ## Returns the value of the "use KNotify" setting.
  def useKNotify(self):
    return self.config.value('useKNotify').toInt()[0] > 0


# SERVICES PAGE ###########################################################################################################


  ## Populates both lists in the services page.
  ## The right list can theoretically contain multiple services with the same ID.
  ## When this happens, only the one with higher priority (or the one parsed later) is displayed.
  def populateServiceLists(self, select = None):
    activeServices = self.activeServices()
    activeSources = self.activeSources()
    self.servicesPage.activeServicesList.clear()
    self.servicesPage.inactiveServicesList.clear()
    self.servicesPage.activeServicesList.setSpacing(1)
    self.servicesPage.inactiveServicesList.setSpacing(1)
    self.servicesPage.activeServicesList.setIconSize(QSize(22,22))
    self.servicesPage.inactiveServicesList.setIconSize(QSize(22,22))
    for service in activeServices:
      item = QListWidgetItem(service.name)
      item.service = service
      self.servicesPage.activeServicesList.addItem(item)
      if select == service.id: self.servicesPage.activeServicesList.setCurrentItem(item)
    for source in sorted(activeSources, key=attrgetter('filename')):
      filename = source.filename
      servicesToShow = [s for s in source.services if not s in activeServices and not s.overridden]
      if len(servicesToShow) == 0: continue
      item = QListWidgetItem(source.name if source.name else source.filename)
      item.source = source
      item.setBackground(QBrush(QColor(50, 50, 50)))
      item.setSizeHint(QSize(100, 20))
      item.setForeground(QBrush(QColor(255, 255, 255)))
      font = item.font(); font.setBold(True); item.setFont(font)
      self.servicesPage.inactiveServicesList.addItem(item)
      for service in sorted(servicesToShow, key=attrgetter('name')):
        item = QListWidgetItem(service.name)
        item.service = service
        self.servicesPage.inactiveServicesList.addItem(item)
        if select == service.id: self.servicesPage.inactiveServicesList.setCurrentItem(item)
    self.refreshIndicatorsAndVisibility()


  ## Iterates over service lists and sets the indicator and visibility.
  def refreshIndicatorsAndVisibility(self, service = None):
    activeItems    = [self.servicesPage.activeServicesList.item(i) for i in range(self.servicesPage.activeServicesList.count()) if hasattr(self.servicesPage.activeServicesList.item(i), "service")]
    inactiveItems  = [self.servicesPage.inactiveServicesList.item(i) for i in range(self.servicesPage.inactiveServicesList.count()) if hasattr(self.servicesPage.inactiveServicesList.item(i), "service")]
    for item in activeItems + inactiveItems:
      if service is None or item.service == service:
        item.setIcon(self.installStateIndicator(item.service))
    for item in inactiveItems:
      item.setHidden(self.servicesPage.hideUnavailableCheckBox.checkState() == Qt.Checked and item.service.state[0] == 'missing')


  ## Print info about the clicked service in the textarea.
  def showServiceInfo(self, item):
    if hasattr(item, 'source'):
      self.servicesPage.infoTextarea.document().setHtml(item.source.description)
    elif hasattr(item, 'service'):
      s = item.service
      self.servicesPage.infoTextarea.document().setHtml(self.tr('''<strong>%1</strong><br/>
        %2<br/>
        <table>
        <tr><td>Install check:</td><td>&nbsp;</td><td>%3</td></tr>
        <tr><td>Running check:</td><td>&nbsp;</td><td>%4</td></tr>
        <tr><td>Start command:</td><td>&nbsp;</td><td>%5</td></tr>
        <tr><td>Stop command:</td><td>&nbsp;</td><td>%6</td></tr>
        <tr><td>Root privileges:</td><td>&nbsp;</td><td>%7</td></tr>
        </table>''').arg(s.name).arg(s.description).arg(s.installcheck).arg(s.runningcheck).arg(s.startcommand).arg(s.stopcommand).arg(self.tr("Yes") if s.sudo else self.tr("No"))
      )


  ## Add selected service to the list of active services (then repopulate lists).
  def activateService(self):
    activeServicesIDs = self.config.value("activeServices").toStringList()
    try: activeServicesIDs << self.servicesPage.inactiveServicesList.currentItem().service.id
    except: return
    self.config.setValue("activeServices", activeServicesIDs)
    self.populateServiceLists()
    self.configurationChanged.emit()


  ## Remove selected service to the list of active services (then repopulate lists).
  def deactivateService(self):
    activeServicesIDs = self.config.value("activeServices").toStringList()
    try: activeServicesIDs.removeAll( self.servicesPage.activeServicesList.currentItem().service.id )
    except: return
    self.config.setValue("activeServices", activeServicesIDs)
    self.populateServiceLists()
    self.configurationChanged.emit()


  ## Called when clicking one of the sort buttons
  ## @param direction identifies the clicked button
  def sort(self, direction):
    if not self.servicesPage.activeServicesList.currentItem(): return

    # load active services and currently selected service
    activeServices = self.activeServices()
    n = len(activeServices)
    service1 = self.servicesPage.activeServicesList.currentItem().service
    pos = activeServices.index(service1)

    # find service to change positions with
    if   direction == 'top'    and n > 1:     service2 = activeServices[0]
    elif direction == 'bottom' and n > 1:     service2 = activeServices[n-1]
    elif direction == 'up'     and pos > 0:   service2 = activeServices[pos-1]
    elif direction == 'down'   and pos < n-1: service2 = activeServices[pos+1]
    else: return

    # adapt id list in self.config, repopulate list and emit config change
    activeServicesIDs = self.config.value("activeServices").toStringList()
    pos1 = activeServicesIDs.indexOf(service1.id)
    pos2 = activeServicesIDs.indexOf(service2.id)
    activeServicesIDs.swap(pos1, pos2)
    self.config.setValue("activeServices", activeServicesIDs)
    self.populateServiceLists(service1.id)
    self.configurationChanged.emit()


  ## Calls self.sort('up')
  def sortUp(self): self.sort('up')

  ## Calls self.sort('down')
  def sortDown(self): self.sort('down')

  ## Calls self.sort('top')
  def sortTop(self): self.sort('top')

  ## Calls self.sort('bottom')
  def sortBottom(self): self.sort('bottom')


# SOURCE PAGE ###########################################################################################################


  ## Populates the list of sources from self.sources.
  def populateSourceList(self):
    self.sourcesPage.sourceList.clear()
    activeSources = self.activeSources()
    for filename, source in sorted(self.sources.items()):
      if filename == QString('custom.xml'): continue
      item = QListWidgetItem(self.tr('%1 (%2, %3 entries)').arg(source.name if source.name else 'Unnamed').arg(filename).arg(len(source.services)))
      item.source = source
      item.setCheckState(Qt.Checked if source in activeSources else Qt.Unchecked)
      self.sourcesPage.sourceList.addItem(item)
    if len(self.sources) > 0:
      lastmod = max([QFileInfo(sourcedir + "/" + s.filename).created() for s in self.sources.values()])
      self.sourcesPage.lastUpdateLabel.setText(lastmod.toString(Qt.SystemLocaleShortDate))
    else:
      self.sourcesPage.lastUpdateLabel.setText("unknown")
      

  ## Called when a checkbox is changed in the sources list. Removes or adds a source to the list of active sources in the config file.
  def saveActiveSources(self, item):
    activeSourcesIDs = self.config.value('activeSources').toStringList()
    if item.checkState() == Qt.Checked:
      activeSourcesIDs << item.source.filename
      activeSourcesIDs.removeDuplicates()
      self.config.setValue('activeSources', activeSourcesIDs)
    else:
      activeSourcesIDs.removeAll(item.source.filename)
      self.config.setValue('activeSources', activeSourcesIDs)
    self.configurationChanged.emit()


  ## Updates the sources from the selected server.
  def performUpdate(self):
    index = self.sourcesPage.updateComboBox.currentIndex()
    if index == -1:
      return
    if index == 0: url = QUrl("http://www.documentroot.net/service-monitor/service-monitor-master.tar.gz")
    else:          url = QUrl("https://github.com/mbleichner/service-monitor/tarball/master")
    print "starting update from %s" % url.toString()
    self.man = QNetworkAccessManager()
    oldText = self.sourcesPage.searchButton.text()
    self.sourcesPage.searchButton.setText(self.tr("Updating"))
    self.sourcesPage.searchButton.setEnabled(False)
    def startDownload():
      self.res = self.man.get(QNetworkRequest(url))
      self.res.finished.connect(finished)
    def finished():
      redirect = self.res.attribute(QNetworkRequest.RedirectionTargetAttribute).toString()
      if redirect:
        print "following redirect to %s" % redirect
        self.res = self.man.get(QNetworkRequest(QUrl(redirect)))
        self.res.finished.connect(finished)
        return
      if self.res.error() != QNetworkReply.NoError:
        errorMessage = "There was an error. Try again or choose another server."
        if self.res.error() == QNetworkReply.ConnectionRefusedError:       errorMessage = self.tr("Connection refused by the server. Usually this means that the server is temporarily offline.")
        if self.res.error() == QNetworkReply.RemoteHostClosedError:        errorMessage = self.tr("The remote host closed the connection prematurely. Try again.")
        if self.res.error() == QNetworkReply.HostNotFoundError:            errorMessage = self.tr("The update server could not be found. Are you online?")
        if self.res.error() == QNetworkReply.TimeoutError:                 errorMessage = self.tr("The request timed out. Probably the server is under heavy load and you should try again later.")
        if self.res.error() == QNetworkReply.TemporaryNetworkFailureError: errorMessage = self.tr("Network error. Please check your connection and try again.")
        if self.res.error() == QNetworkReply.ContentAccessDenied:          errorMessage = self.tr("Server access denied. Write me a mail if this happens and try another server.")
        if self.res.error() == QNetworkReply.ContentNotFoundError:         errorMessage = self.tr("File not found. Write me a mail if this happens and try another server.")
        QMessageBox.critical(self, "Connection failed", errorMessage)
      else:
        f = QFile("/tmp/sources.tar.gz")
        f.open(QIODevice.WriteOnly)
        f.write(self.res.readAll())
        f.close()
        print "received file, unpacking..."
        exitcode = QProcess.execute("/bin/tar", QStringList() << "xfz" << f.fileName() << "-C" << sourcedir << "--no-anchored" << "sources" << "--strip-components=3" << "--exclude" << "custom.xml")
        f.remove()
        if exitcode == 0:
          self.cache.clear()
          self.readSources()
          self.populateSourceList()
          self.configurationChanged.emit()
          print "update finished."
          QMessageBox.information(self, self.tr('Update successful'), self.tr('Update successful.'))
        else:
          QMessageBox.critical(self, self.tr('Update failed'), self.tr('The file could be downloaded, but there was an error unpacking it. Maybe it is corrupted.'))
          print "update failed."
      self.sourcesPage.searchButton.setText(oldText)
      self.sourcesPage.searchButton.setEnabled(True)
    QTimer.singleShot(0, startDownload)


  ## Shows information about the clicked source in the text area.
  def showSourceInfo(self, item):
    if not hasattr(item, 'source'): return
    self.sourcesPage.infoTextarea.document().setHtml(item.source.description)


# CUSTOM PAGE ###########################################################################################################


  ## Populates list of custom services from custom.xml source file.
  ## @param select automatically select service with given id
  def populateCustomList(self, select = None):
    self.customPage.serviceList.clear()
    self.customPage.serviceList.setIconSize(QSize(22,22))
    
    if not self.sources.has_key(QString('custom.xml')):
      self.customPage.serviceList.addItem(self.tr('Error - custom.xml is missing or has been damaged'))
      self.customPage.setEnabled(False)
      return
      
    self.customPage.setEnabled(True)
    for service in self.sources[QString('custom.xml')].services:
      icon = self.serviceIcon(service)
      item = QListWidgetItem(icon, (service.name + ' - ' + service.description) if service.description else service.name)
      item.service = service
      self.customPage.serviceList.addItem(item)
      if select == service.id:
        self.customPage.serviceList.setCurrentItem(item)
          
    self.customPage.copyComboBox.clear()
    self.customPage.copyComboBox.view().setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    self.customPage.copyComboBox.addItem(QIcon(':plus.png'), self.tr("Copy existing"))
    self.customPage.copyComboBox.addItem("")
    for source in self.activeSources():
      self.customPage.copyComboBox.addItem(source.name)
      for service in source.services:
        self.customPage.copyComboBox.addItem("  " + service.name, QString(source.filename + "|" + service.id))
      self.customPage.copyComboBox.addItem("")


  ## Switches editmode on or off.
  ## @param save Save when disabling editmode?
  ## When entering editmode, the list is disabled and the line edits are enabled and vice versa when editmode is left.
  ## In editmode, the edit button becomes a save button and the remove button becomes a cancel button.
  def toggleEditmode(self, save = True):
    if self.editmode:
      self.stopEditmode()
    else:
      self.startEditmode()


  ## Starts edit mode for the selected service. Disables and relabels buttons.
  def startEditmode(self):
    item = self.customPage.serviceList.currentItem()
    if not item: return
    self.editmode = True

    # Widget-Status anpassen
    self.setLineEditsEnabled(True)
    self.synchronizeLineEdits()
    self.customPage.editButton.setText(self.tr('Save'))
    self.customPage.removeButton.setText(self.tr('Cancel'))
    self.customPage.addButton.setEnabled(False)
    self.customPage.shareButton.setEnabled(False)
    self.customPage.serviceList.setEnabled(False)
    self.customPage.copyComboBox.setEnabled(False)


  ## Quits edit mode. The save parameter determines if the definition should be written back to the source file.
  def stopEditmode(self, save = True):
    if not self.customPage.serviceList.currentItem(): return
      
    if save:
      # Konfiguration schreiben und relevante Bereiche aktualisieren
      self.synchronizeService()
      self.sources[QString('custom.xml')].writeBack()
      self.configurationChanged.emit() # Falls sich der Name geändert hat
      service = self.customPage.serviceList.currentItem().service
      self.populateCustomList(service.id)
    else:
      # LineEdits wieder mit ursprünglichen Werten füllen
      self.synchronizeLineEdits()

    # Stoppe Editmode
    self.setLineEditsEnabled(False)
    self.editmode = False

    # Widget-Status anpassen
    self.customPage.editButton.setText(self.tr('Edit'))
    self.customPage.removeButton.setText(self.tr('Remove'))
    self.customPage.addButton.setEnabled(True)
    self.customPage.shareButton.setEnabled(True)
    self.customPage.serviceList.setEnabled(True)
    self.customPage.copyComboBox.setEnabled(True)
    

  ## Writes data of selected custom service to line edits.
  ## Called as slot when a custom service in the list is clicked.
  def synchronizeLineEdits(self, x = None):
    service = self.customPage.serviceList.currentItem().service
    self.customPage.serviceNameInput.setText(service.name)
    self.customPage.descriptionInput.setText(service.description)
    self.customPage.installCheckInput.setText(service.installcheck)
    self.customPage.runningCheckInput.setText(service.runningcheck)
    self.customPage.startCommandInput.setText(service.startcommand)
    self.customPage.stopCommandInput.setText(service.stopcommand)
    self.customPage.sudoCheckbox.setCheckState(Qt.Checked if service.sudo else Qt.Unchecked)


  ## Writes data in line edits to selected custom service.
  def synchronizeService(self, x = None):
    service = self.customPage.serviceList.currentItem().service
    service.name         = self.customPage.serviceNameInput.text()
    service.description  = self.customPage.descriptionInput.text()
    service.installcheck = self.customPage.installCheckInput.text()
    service.runningcheck = self.customPage.runningCheckInput.text()
    service.startcommand = self.customPage.startCommandInput.text()
    service.stopcommand  = self.customPage.stopCommandInput.text()
    service.sudo         = self.customPage.sudoCheckbox.checkState() == Qt.Checked


  ## Deletes selected custom service (and repopulate all lists).
  ## When in editmode, cancel without saving.
  def removeCustomService(self):

    if self.editmode: # cancel editing
      self.stopEditmode(False)

    elif self.customPage.serviceList.currentItem():
      answer = QMessageBox.question(self, self.tr('Remove service'), self.tr('Really delete the selected service?'), QMessageBox.Yes | QMessageBox.No)
      if answer == QMessageBox.No: return
      item = self.customPage.serviceList.currentItem()
      self.sources[QString('custom.xml')].services.remove(item.service)
      self.sources[QString('custom.xml')].writeBack()
      self.readSources() # update self.services
      self.populateCustomList()
      self.configurationChanged.emit()


  ## Adds a new, empty service with random ID to custom.xml and reload the sources.
  def addCustomService(self):
    service = Service()
    service.id = 'custom-%i' % random.randrange(1, 999999)
    service.name = self.tr('New Service, edit me')
    service.description = self.tr('Enter a short, concise description here')
    self.sources[QString('custom.xml')].services.append(service)
    self.sources[QString('custom.xml')].writeBack()
    self.readSources()
    self.populateCustomList(service.id)
    self.synchronizeLineEdits() # Triggert nicht automatisch


  ## Enable/disable all line edits of the custom services page in one call.
  def setLineEditsEnabled(self, status):
    self.customPage.serviceNameInput.setEnabled(status)
    self.customPage.descriptionInput.setEnabled(status)
    self.customPage.installCheckInput.setEnabled(status)
    self.customPage.runningCheckInput.setEnabled(status)
    self.customPage.startCommandInput.setEnabled(status)
    self.customPage.stopCommandInput.setEnabled(status)
    self.customPage.sudoCheckbox.setEnabled(status)


  ## Submits the data of the currently selected service via GET request to documentroot.net.
  def uploadCustomService(self):
    if not self.customPage.serviceList.currentItem(): return
    answer = QMessageBox.question(self, self.tr('Upload service definition'), self.tr('This will open a page in your web browser where you can submit the selected service definition to the community.'), QMessageBox.Ok | QMessageBox.Cancel)
    if answer == QMessageBox.Cancel: return
    item = self.customPage.serviceList.currentItem()
    url = QUrl('http://www.documentroot.net/en/submit-service-definition')
    url.addQueryItem('servicename', item.service.name)
    url.addQueryItem('description', item.service.description)
    url.addQueryItem('installcheck', item.service.installcheck)
    url.addQueryItem('runningcheck', item.service.runningcheck)
    url.addQueryItem('startcommand', item.service.startcommand)
    url.addQueryItem('stopcommand', item.service.stopcommand)
    QDesktopServices.openUrl(url)


  ## Copies the selected service and adds it as a custom service
  def copyService(self):
    index = self.customPage.copyComboBox.currentIndex()
    data = self.customPage.copyComboBox.itemData(index).toString()
    if index == -1 or len(data.split("|")) != 2:
      return
    (sourceFilename, serviceId) = data.split("|")
    matches = [s for s in self.sources[sourceFilename].services if s.id == serviceId]
    if len(matches) != 1:
      return
    service = copy.deepcopy(matches[0])
    self.sources[QString("custom.xml")].services.append(service)
    service.id = 'custom-%i' % random.randrange(1, 999999)
    self.sources[QString("custom.xml")].writeBack()
    self.readSources()
    self.populateCustomList(service.id)
    self.synchronizeLineEdits()
    self.customPage.copyComboBox.setCurrentIndex(0)



# SETTINGS PAGE ###########################################################################################################


  ## Populates everything in the settings frame (currently only polling time and sleep time).
  def populateSettings(self):
    self.settingsPage.iconStyleComboBox.setCurrentIndex(self.config.value('iconStyle').toInt()[0])
    self.settingsPage.pollingIntervalSpinbox.setValue(self.config.value('pollingInterval').toDouble()[0])
    self.settingsPage.sleepTimeSpinbox.setValue(self.config.value('sleepTime').toDouble()[0])
    self.settingsPage.usernameLabel.setText(getpass.getuser())
    self.settingsPage.suppressStdoutCheckBox.setCheckState(self.config.value('suppressStdout').toInt()[0])
    self.settingsPage.kNotifyCheckBox.setCheckState(self.config.value('useKNotify').toInt()[0])
    themes = QStringList([fn for fn in os.listdir(codedir + "/indicators")])
    themes.sort()
    self.settingsPage.themeComboBox.blockSignals(True)
    self.settingsPage.themeComboBox.clear()
    self.settingsPage.themeComboBox.addItems(themes)
    self.settingsPage.themeComboBox.setCurrentIndex(themes.indexOf(self.indicatorTheme()))
    self.settingsPage.themeComboBox.blockSignals(False)


  ## Saves a value under the given name in the configuration file
  def saveConfigValue(self, name, value):
    self.config.setValue(name, value)
    self.configurationChanged.emit()


  ## Generates /etc/sudoers snippets
  def showSudoSnippet(self, selected):
    if selected == 0:
      text = self.settingsPage.sudoHelperDefaultText
    else:
      text = self.tr("# copy-paste this snippet into your /etc/sudoers file:\n\n")
      if selected in [2,4]:
        text.append("Defaults rootpw\n")
      if selected in [3,4]:
        text.append("%s ALL=(ALL:ALL) ALL" % getpass.getuser())
      else:
        text.append(chr(37)).append("sudo ALL=(ALL:ALL) ALL")
    self.settingsPage.sudoHelperTextarea.document().setPlainText(text)
    

  ## Executes a command to check sudo configuration and gives hints on errors
  def checkSudo(self):
    if not self.settingsPage.passwordLineEdit.text():
      QMessageBox.warning(None, self.tr('Enter password'), self.tr("Please enter your password."))
      return
    proc = BashProcess()
    proc.setBashCommand('cat /etc/sudoers')
    proc.setSudoPassword(self.settingsPage.passwordLineEdit.text())
    errorCode = proc.start()

    # check for startup or sudo errors. if no error occurred, update the service state
    if errorCode == BashProcess.StartupError:
      QMessageBox.critical(None, self.tr('Process failed to start'), self.tr('Process failed to start. This should not happen and maybe it is a serious bug.'))
    elif errorCode == BashProcess.SudoError:
      QMessageBox.critical(None, self.tr('Sudo installation error'), self.tr("Sudo could not be started. Make sure it is installed correctly."))
    elif errorCode == BashProcess.PermissionError:
      QMessageBox.critical(None, self.tr('Sudo permission error'), self.tr("Permission denied by /etc/sudoers. Make sure it contains the correct lines."))
    elif errorCode == BashProcess.PasswordError:
      QMessageBox.warning(None, self.tr('Wrong password'), self.tr("It seems you gave the wrong password. Try again."))
    else:
      QMessageBox.information(None, self.tr('Success'), self.tr("Your installation seems to be working. Now try to start/stop some services in your list."))




################################################################################################################


## A widget which emits a signal "show".
class CustomWidget(QWidget):
  show = pyqtSignal()
  def showEvent(self, event):
    self.emit(SIGNAL("show()"))

## The "Sources" tab in the settings dialog (only the widgets, logic is contained in ConfigDialog)
class SourcesPage(CustomWidget, Ui_Sources):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

## The "Services" tab in the settings dialog (only the widgets, logic is contained in ConfigDialog)
class ServicesPage(CustomWidget, Ui_Services):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

## The "Custom Sources" tab in the settings dialog (only the widgets, logic is contained in ConfigDialog)
class CustomPage(CustomWidget, Ui_Custom):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

## The "Settings" tab in the settings dialog (only the widgets, logic is contained in ConfigDialog)
class SettingsPage(CustomWidget, Ui_Settings):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

## The "About" tab in the settings dialog (only the widgets, logic is contained in ConfigDialog)
class AboutPage(CustomWidget, Ui_About):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)


