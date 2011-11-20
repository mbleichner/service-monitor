# -*- coding: utf-8 -*-
import shutil, random, os, sys
from functools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyKDE4.kdeui import *

from generated.Services_ui import *
from generated.Custom_ui import *
from generated.Sources_ui import *
from generated.Settings_ui import *

from Source import *
from Service import *
from functions import *

contentsdir = os.path.dirname(os.path.dirname(__file__))
codedir     = contentsdir + "/code"
sourcedir   = contentsdir + "/sources"

## A KPageDialog for accessing and manipulating settings.
#
# This dialog consists of 4 pages: services, sources, settings and custom services,
# which are made in Qt Designer and simply provide the widgets. All the logic
# is contained in this class here.
#
# Whenever the configuration is changed, the signal configurationChanged() is emitted.
# This signal tells the ServiceMonitor class to re-setup its widgets and monitoring.
class ConfigDialog(KPageDialog):

  ## Sets up pages, widgets and connections and loads the source files.
  def __init__(self, parent = None):
    KPageDialog.__init__(self)
    self.sources = {}       ##< [dict] Place for all xml sources, by ID.
    self.services = {}      ##< [dict] Place for all services, by ID. On collisions the priority is considered.
    self.editmode = False   ##< [bool] Indicates if editmode is on or off.
    self.config = QSettings('KDE Plasmoid', 'Service Monitor') ##< [QSettings] Internal config object.

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
    self.addPage(self.servicesPage, self.tr("Activate Services")).setIcon(KIcon("run-build-configure"))
    self.addPage(self.settingsPage, self.tr("Settings")).setIcon(KIcon("configure"))
    self.addPage(self.sourcesPage, self.tr("Manage Sources")).setIcon(KIcon("document-new"))
    self.addPage(self.customPage, self.tr("Custom Services")).setIcon(KIcon("edit-rename"))

    # When opening a page, populate the corresponding widgets
    QObject.connect(self.servicesPage, SIGNAL('show()'), chain(self.execInstallChecks, self.populateServiceLists))
    QObject.connect(self.sourcesPage,  SIGNAL('show()'), self.populateSourceList)
    QObject.connect(self.settingsPage, SIGNAL('show()'), self.populateSettings)
    QObject.connect(self.customPage,   SIGNAL('show()'), self.populateCustomList)
    
    # Connections für die ServicesPage
    QObject.connect(self.servicesPage.activeServicesList, SIGNAL('itemClicked(QListWidgetItem*)'), partial(self.showServiceInfo))
    QObject.connect(self.servicesPage.inactiveServicesList, SIGNAL('itemClicked(QListWidgetItem*)'), partial(self.showServiceInfo,))
    QObject.connect(self.servicesPage.activateButton, SIGNAL('clicked()'), self.activateService)
    QObject.connect(self.servicesPage.deactivateButton, SIGNAL('clicked()'), self.deactivateService)
    QObject.connect(self.servicesPage.sortUpButton, SIGNAL('clicked()'), self.sortUp)
    QObject.connect(self.servicesPage.sortDownButton, SIGNAL('clicked()'), self.sortDown)
    QObject.connect(self.servicesPage.sortTopButton, SIGNAL('clicked()'), self.sortTop)
    QObject.connect(self.servicesPage.sortBottomButton, SIGNAL('clicked()'), self.sortBottom)

    # Connections für die SourcesPage
    QObject.connect(self.sourcesPage.addButton, SIGNAL('clicked()'), self.addSource)
    QObject.connect(self.sourcesPage.removeButton, SIGNAL('clicked()'), self.removeSource)
    QObject.connect(self.sourcesPage.searchButton, SIGNAL('clicked()'), self.downloadSources)
    QObject.connect(self.sourcesPage.sourceList, SIGNAL('itemClicked(QListWidgetItem*)'), partial(self.showSourceInfo))

    # Connections für die CustomPage
    QObject.connect(self.customPage.serviceList, SIGNAL('itemClicked(QListWidgetItem*)'), partial(self.synchronizeLineEdits))
    QObject.connect(self.customPage.serviceList, SIGNAL('itemDoubleClicked(QListWidgetItem*)'), self.startEditmode)
    QObject.connect(self.customPage.editButton, SIGNAL('clicked()'), self.toggleEditmode)
    QObject.connect(self.customPage.removeButton, SIGNAL('clicked()'), self.removeCustomService)
    QObject.connect(self.customPage.addButton, SIGNAL('clicked()'), self.addCustomService)
    QObject.connect(self.customPage.shareButton, SIGNAL('clicked()'), self.uploadCustomService)

    # Connections für die SettingsPage
    QObject.connect(self.settingsPage.pollingIntervalSpinbox, SIGNAL('valueChanged(double)'), self.setPollingInterval)
    QObject.connect(self.settingsPage.sleepTimeSpinbox, SIGNAL('valueChanged(double)'), self.setSleepTime)

    # Cleanup actions when closing the config dialog
    QObject.connect(self, SIGNAL('closeClicked()'), self.stopEditmode)


  def execInstallChecks(self):
    for source in self.sources.values():
      for service in source.services:
        service.execute("installcheck")


  ## Initialize the internal QSettings object with sensible default values
  def setConfigDefaults(self):
    if not self.config.contains('pollingInterval'): self.config.setValue('pollingInterval', 4.0)
    if not self.config.contains('sleepTime'):       self.config.setValue('sleepTime', 0.5)


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
          QObject.connect(service, SIGNAL("stateChanged()"), partial(self.refreshIndicator, service))
      print '* loaded %s (%i services).' % (fn, len(source.services))


# PUBLIC GETTERS ###########################################################################################################


  ## Returns a list of all services.
  # On ID collisions only the one with higher priority is contained in the list.
  def allServices(self):
    return self.services.values()


  ## Returns the list of active services.
  def activeServices(self):
    activeServicesIDs = self.config.value('activeServices').toStringList()
    return [self.services[id] for id in activeServicesIDs if self.services.has_key(id)]


  ## Returns the polling interval from the settings page.
  def pollingInterval(self):
    return self.config.value('pollingInterval').toDouble()[0]


  ## Returns the sleep time from the settings page.
  def sleepTime(self):
    return self.config.value('sleepTime').toDouble()[0]


  def indicatorTheme(self):
    return "default"


  def installStateIndicator(self, service):
    return QIcon("%s/indicators/%s/%s.png" % (codedir, self.indicatorTheme(), service.state[0]))


  def runningStateIndicator(self, service):
    return QIcon("%s/indicators/%s/%s.png" % (codedir, self.indicatorTheme(), service.state[1]))


# SERVICES PAGE ###########################################################################################################


  ## Populates both lists in the services page.
  # The right list can theoretically contain multiple services with the same ID.
  # When this happens, only the one with higher priority (or the one parsed later) is displayed.
  @pyqtSlot()
  def populateServiceLists(self):

    # load ID list of active services and clean orphans (fixes bug when reordering list)
    activeServicesIDs = self.config.value('activeServices').toStringList()
    deadlinks = [id for id in activeServicesIDs if not self.services.has_key(id)]
    if deadlinks:
      for id in deadlinks: activeServicesIDs.removeAll(id)
      self.config.setValue('activeServices', activeServicesIDs)

    # now populate the lists
    self.servicesPage.activeServicesList.clear()
    self.servicesPage.inactiveServicesList.clear()
    for service in self.activeServices():
      item = QListWidgetItem(service.name)
      item.service = service
      self.servicesPage.activeServicesList.addItem(item)
      item.setIcon(self.installStateIndicator(service))
    for filename, source in sorted(self.sources.items()):
      servicesToShow = [s for s in source.services if not activeServicesIDs.contains(s.id) and self.services[s.id] == s]
      if len(servicesToShow) == 0: continue
      item = QListWidgetItem(source.name if source.name else source.filename)
      item.source = source
      font = item.font(); font.setBold(True); item.setFont(font)
      self.servicesPage.inactiveServicesList.addItem(item)
      for service in servicesToShow:
        item = QListWidgetItem(service.name)
        item.service = service
        self.servicesPage.inactiveServicesList.addItem(item)
        item.setIcon(self.installStateIndicator(service))


  ## [slot] Updates the icon in the list for the service which has sent the stateChanged() signal.
  def refreshIndicator(self, service):
    allItems = [self.servicesPage.activeServicesList.item(i) for i in range(self.servicesPage.activeServicesList.count())] + \
               [self.servicesPage.inactiveServicesList.item(i) for i in range(self.servicesPage.inactiveServicesList.count())]
    for item in allItems:
      if hasattr(item, "service") and item.service == service:
        item.setIcon(self.installStateIndicator(service))


  ## [slot] Print info about the clicked service in the textarea.
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
        </table>''').arg(s.name).arg(s.description).arg(s.installCheck).arg(s.runningCheck).arg(s.startCommand).arg(s.stopCommand)
      )


  ## [slot] Add selected service to the list of active services (then repopulate lists).
  @pyqtSlot()
  def activateService(self):
    '''Fügt einen Service zur Liste der aktiven hinzu und aktualisiert dann alles'''
    activeServicesIDs = self.config.value("activeServices").toStringList()
    try: activeServicesIDs << self.servicesPage.inactiveServicesList.currentItem().service.id
    except: return
    self.config.setValue("activeServices", activeServicesIDs)
    self.populateServiceLists()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Remove selected service to the list of active services (then repopulate lists).
  @pyqtSlot()
  def deactivateService(self):
    activeServicesIDs = self.config.value("activeServices").toStringList()
    try: activeServicesIDs.removeAll( self.servicesPage.activeServicesList.currentItem().service.id )
    except: return
    self.config.setValue("activeServices", activeServicesIDs)
    self.populateServiceLists()
    self.emit(SIGNAL('configurationChanged()'))


  ## Called when clicking one of the sort buttons
  #  @param direction identifies the clicked button
  def sort(self, direction):
    activeServicesIDs = self.config.value('activeServices').toStringList()
    n = len(activeServicesIDs)
    oldPosition = self.servicesPage.activeServicesList.currentRow()
    if   direction == 'top'    and n > 1:             newPosition = 0
    elif direction == 'bottom' and n > 1:             newPosition = n-1
    elif direction == 'up'     and oldPosition > 0:   newPosition = oldPosition-1
    elif direction == 'down'   and oldPosition < n-1: newPosition = oldPosition+1
    else: return
    activeServicesIDs.move(oldPosition, newPosition)
    self.config.setValue("activeServices", activeServicesIDs)
    self.populateServiceLists()
    self.servicesPage.activeServicesList.setCurrentRow(newPosition)
    self.emit(SIGNAL('configurationChanged()'))

  ## [slot] Calls self.sort('up')
  @pyqtSlot()
  def sortUp(self): self.sort('up')

  ## [slot] Calls self.sort('down')
  @pyqtSlot()
  def sortDown(self): self.sort('down')

  ## [slot] Calls self.sort('top')
  @pyqtSlot()
  def sortTop(self): self.sort('top')

  ## [slot] Calls self.sort('bottom')
  @pyqtSlot()
  def sortBottom(self): self.sort('bottom')


# SOURCE PAGE ###########################################################################################################


  ## Populates the list of sources from self.sources.
  def populateSourceList(self):
    self.sourcesPage.sourceList.clear()
    for filename, source in sorted(self.sources.items()):
      if filename == QString('custom.xml'): continue
      icon = KIcon('application-xml')
      item = QListWidgetItem(icon, self.tr('%1 (%2, %3 entries)').arg(source.name if source.name else 'Unnamed').arg(filename).arg(len(source.services)))
      item.source = source
      self.sourcesPage.sourceList.addItem(item)


  ## [slot] Selects and copies a file into the sources directory (and repopulates sources list).
  @pyqtSlot()
  def addSource(self):
    filename = QFileDialog.getOpenFileName(self, self.tr('Select source file'), '~', self.tr('Service definitions (*.xml)'))
    if not filename: return
    fileinfo = QFileInfo(filename)
    destination = '%s/sources/%s' % (contentsdir, fileinfo.fileName())
    if QFile.exists(destination):
      answer = QMessageBox.question(self, self.tr('Add source file'), self.tr('This will overwrite an existing file. Continue?'), QMessageBox.Yes | QMessageBox.No)
      if answer == QMessageBox.No: return
    shutil.copyfile(filename, destination)
    self.readSources()
    self.populateSourceList()
    self.populateServiceLists()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Deletes a file from the sources directory (and repopulates sources list).
  @pyqtSlot()
  def removeSource(self):
    '''Löscht eine XML-Datei aus dem source-Verzeichnis'''
    answer = QMessageBox.question(self, self.tr('Delete source file'), self.tr('Really delete the file?'), QMessageBox.Yes | QMessageBox.No)
    if answer == QMessageBox.No: return
    item = self.sourcesPage.sourceList.currentItem()
    QFile.remove('%s/%s' % (sourcedir, item.source.filename))
    self.readSources()
    self.populateServiceLists()
    self.populateSourceList()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Opens a browser and go to the sources download page on documentroot.net.
  @pyqtSlot()
  def openBrowser(self):
    answer = QMessageBox.question(self, self.tr('Search for new sources'), self.tr('This will open a page in your web browser where additional service definitions can be downloaded.'), QMessageBox.Ok | QMessageBox.Cancel)
    if answer == QMessageBox.Ok: QDesktopServices.openUrl(QUrl('http://www.documentroot.net/en/download-service-definitions'))


  def downloadSources(self):
    self.url = QUrl("http://www.documentroot.net/service-monitor/sources.tar.gz")
    self.man = QNetworkAccessManager()
    self.req = QNetworkRequest(self.url)
    self.res = self.man.get(self.req)
    def finished():
      f = QFile("/tmp/sources.tar.gz")
      f.open(QIODevice.WriteOnly)
      f.write(self.res.readAll())
      f.close()
      QProcess.execute("/bin/tar", QStringList() << "xfz" << f.fileName() << "-C" << sourcedir)
      self.readSources()
      self.populateSourceList()
    QObject.connect(self.res, SIGNAL('finished()'), finished)


  ## [slot] Shows information about the clicked source in the text area.
  @pyqtSlot('QListWidgetItem*')
  def showSourceInfo(self, item):
    if not hasattr(item, 'source'): return
    self.sourcesPage.infoTextarea.document().setHtml(item.source.description)


# CUSTOM PAGE ###########################################################################################################


  ## Populates list of custom services from custom.xml source file.
  # @param select automatically select service with given id
  def populateCustomList(self, select = None):
    self.customPage.serviceList.clear()
    if not self.sources.has_key(QString('custom.xml')):
      self.customPage.serviceList.addItem(self.tr('Error - custom.xml is missing or has been damaged'))
      return
    for service in self.sources[QString('custom.xml')].services:
      icon = KIcon('text-x-generic')
      item = QListWidgetItem(icon, (service.name + ' - ' + service.description) if service.description else service.name)
      item.service = service
      self.customPage.serviceList.addItem(item)
      if select == service.id:
        self.customPage.serviceList.setCurrentRow(self.customPage.serviceList.count()-1)

  ## [slot] Switches editmode on or off.
  # @param save Save when disabling editmode?
  # When entering editmode, the list is disabled and the line edits are enabled and vice versa when editmode is left.
  # In editmode, the edit button becomes a save button and the remove button becomes a cancel button.
  @pyqtSlot()
  def toggleEditmode(self, save = True):
    if self.editmode:
      self.stopEditmode()
    else:
      self.startEditmode()

  @pyqtSlot()
  def startEditmode(self):
    item = self.customPage.serviceList.currentItem()
    if not item: return
    self.editmode = True

    # Widget-Status anpassen
    self.setLineEditsEnabled(True)
    self.synchronizeLineEdits()
    self.customPage.editButton.setText(self.tr('Save changes'))
    self.customPage.removeButton.setText(self.tr('Cancel editing'))
    self.customPage.addButton.setEnabled(False)
    self.customPage.shareButton.setEnabled(False)
    self.customPage.serviceList.setEnabled(False)
      
  @pyqtSlot()
  def stopEditmode(self, save = True):
    if not self.customPage.serviceList.currentItem(): return
      
    if save:
      # Konfiguration schreiben und relevante Bereiche aktualisieren
      self.synchronizeService()
      self.sources[QString('custom.xml')].writeBack()
      self.emit(SIGNAL('configurationChanged()')) # Falls sich der Name geändert hat
      service = self.customPage.serviceList.currentItem().service
      self.populateCustomList(service.id)
      self.populateServiceLists()
    else:
      # LineEdits wieder mit ursprünglichen Werten füllen
      self.synchronizeLineEdits()

    # Stoppe Editmode
    self.setLineEditsEnabled(False)
    self.editmode = False

    # Widget-Status anpassen
    self.customPage.editButton.setText(self.tr('Edit selected'))
    self.customPage.removeButton.setText(self.tr('Remove selected'))
    self.customPage.addButton.setEnabled(True)
    self.customPage.shareButton.setEnabled(True)
    self.customPage.serviceList.setEnabled(True)

  ## [slot] Writes data of selected custom service to line edits.
  # Called as slot when a custom service in the list is clicked.
  @pyqtSlot()
  def synchronizeLineEdits(self, x = None):
    service = self.customPage.serviceList.currentItem().service
    self.customPage.serviceNameInput.setText(service.name)
    self.customPage.descriptionInput.setText(service.description)
    self.customPage.installCheckInput.setText(service.installCheck)
    self.customPage.runningCheckInput.setText(service.runningCheck)
    self.customPage.startCommandInput.setText(service.startCommand)
    self.customPage.stopCommandInput.setText(service.stopCommand)


  ## Writes data in line edits to selected custom service.
  def synchronizeService(self, x = None):
    service = self.customPage.serviceList.currentItem().service
    service.name         = self.customPage.serviceNameInput.text()
    service.description  = self.customPage.descriptionInput.text()
    service.installCheck = self.customPage.installCheckInput.text()
    service.runningCheck = self.customPage.runningCheckInput.text()
    service.startCommand = self.customPage.startCommandInput.text()
    service.stopCommand  = self.customPage.stopCommandInput.text()


  ## [slot] Deletes selected custom service (and repopulate all lists)
  # When in editmode, cancel without saving.
  @pyqtSlot()
  def removeCustomService(self):

    if self.editmode: # cancel editing
      self.stopEditmode(False)

    elif self.customPage.serviceList.currentItem():
      answer = QMessageBox.question(self, self.tr('Remove service'), self.tr('Really delete the selected service?'), QMessageBox.Yes | QMessageBox.No)
      if answer == QMessageBox.No: return
      item = self.customPage.serviceList.currentItem()
      self.sources[QString('custom.xml')].services.remove(item.service)
      self.sources[QString('custom.xml')].writeBack()
      self.populateCustomList()
      self.populateServiceLists()
      if item.service in self.activeServices():
        self.activeServices.remove(item.service)
        self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Adds a new, empty service with random ID to custom.xml and reload the sources.
  @pyqtSlot()
  def addCustomService(self):
    service = Service()
    service.id = 'custom-%i' % random.randrange(1, 999999)
    service.name = self.tr('New Service, edit me')
    service.description = self.tr('Enter a short, concise description here')
    self.sources[QString('custom.xml')].services.append(service)
    self.sources[QString('custom.xml')].writeBack()
    self.readSources()
    self.populateServiceLists()
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


  ## [slot] Submits the data of the currently selected service via GET request to documentroot.net.
  @pyqtSlot()
  def uploadCustomService(self):
    if not self.customPage.serviceList.currentItem(): return
    answer = QMessageBox.question(self, self.tr('Upload service definition'), self.tr('This will open a page in your web browser where you can submit the selected service definition to the community.'), QMessageBox.Ok | QMessageBox.Cancel)
    if answer == QMessageBox.Cancel: return
    item = self.customPage.serviceList.currentItem()
    url = QUrl('http://www.documentroot.net/en/submit-service-definition')
    url.addQueryItem('servicename', item.service.name)
    url.addQueryItem('description', item.service.description)
    url.addQueryItem('installcheck', item.service.installCheck)
    url.addQueryItem('runningcheck', item.service.runningCheck)
    url.addQueryItem('startcommand', item.service.startCommand)
    url.addQueryItem('stopcommand', item.service.stopCommand)
    QDesktopServices.openUrl(url)


# SETTINGS PAGE ###########################################################################################################


  ## Populates everything in the settings frame (currently only polling time and sleep time).
  def populateSettings(self):
    self.settingsPage.pollingIntervalSpinbox.setValue(self.config.value('pollingInterval').toDouble()[0])
    self.settingsPage.sleepTimeSpinbox.setValue(self.config.value('sleepTime').toDouble()[0])


  ## [slot] Save polling interval to internal config.
  @pyqtSlot('double')
  def setPollingInterval(self, newValue):
    self.config.setValue('pollingInterval', newValue)
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Save sleep time to internal config.
  @pyqtSlot('double')
  def setSleepTime(self, newValue):
    self.config.setValue('sleepTime', newValue)
    self.emit(SIGNAL('configurationChanged()'))




################################################################################################################

class CustomWidget(QWidget):
  def showEvent(self, event):
    self.emit(SIGNAL("show()"))

class SourcesPage(CustomWidget, Ui_Sources):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

class ServicesPage(CustomWidget, Ui_Services):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

class CustomPage(CustomWidget, Ui_Custom):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

class SettingsPage(CustomWidget, Ui_Settings):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)



