# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *

import shutil, random

from UI.Services import *
from UI.Custom import *
from UI.Sources import *
from UI.Settings import *
from Source import *
from Service import *


contentsdir = os.path.dirname(os.path.dirname(__file__))

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

    ## [dict] Place for all xml sources, by ID.
    self.sources = {}

    ## [dict] Place for all services, by ID. On collisions the priority is considered.
    self.services = {}

    ## [bool] Indicates if editmode is on or off.
    self.editmode = False

    ## [QSettings] Internal config object.
    self.config = QSettings('KDE Plasmoid', 'Service Monitor')
    self.setConfigDefaults()

    # Widgets einrichten
    self.setupUi()

    # Daten einlesen
    self.readSources()


  ## Initialize the internal QSettings object with sensible default values
  def setConfigDefaults(self):
    if not self.config.contains('pollingInterval'): self.config.setValue('pollingInterval', 4.0)
    if not self.config.contains('sleepTime'):       self.config.setValue('sleepTime', 0.5)
    if not self.config.contains('variables'):       self.config.setValue('variables', QStringList() << 'INITDIR' << '/etc/init.d' << 'SUDO' << 'kdesudo')


  ## Set up all pages, widgets and signal-slot connections
  def setupUi(self):
    self.setButtons(KDialog.ButtonCode(KDialog.Close))
    self.setCaption(self.tr('Service Monitor Configuration'))

    # Pages einrichten
    self.settingsPage = SettingsPage(self)
    self.servicesPage = ServicesPage(self)
    self.sourcesPage = SourcesPage(self)
    self.customPage = CustomPage(self)
    self.addPage(self.servicesPage, "Activate Services").setIcon(KIcon("run-build-configure"))
    self.addPage(self.settingsPage, "Settings").setIcon(KIcon("configure"))
    self.addPage(self.sourcesPage, "Manage Sources").setIcon(KIcon("document-new"))
    self.addPage(self.customPage, "Custom Services").setIcon(KIcon("edit-rename"))

    # Connections für die ServicesPage
    QObject.connect(self.servicesPage.activeServicesList, SIGNAL('itemClicked(QListWidgetItem*)'), self, SLOT('showServiceInfo(QListWidgetItem*)'))
    QObject.connect(self.servicesPage.inactiveServicesList, SIGNAL('itemClicked(QListWidgetItem*)'), self, SLOT('showServiceInfo(QListWidgetItem*)'))
    QObject.connect(self.servicesPage.activateButton, SIGNAL('clicked()'), self, SLOT('activateService()'))
    QObject.connect(self.servicesPage.deactivateButton, SIGNAL('clicked()'), self, SLOT('deactivateService()'))
    QObject.connect(self.servicesPage.sortUpButton, SIGNAL('clicked()'), self, SLOT('sortUp()'))
    QObject.connect(self.servicesPage.sortDownButton, SIGNAL('clicked()'), self, SLOT('sortDown()'))
    QObject.connect(self.servicesPage.sortTopButton, SIGNAL('clicked()'), self, SLOT('sortTop()'))
    QObject.connect(self.servicesPage.sortBottomButton, SIGNAL('clicked()'), self, SLOT('sortBottom()'))

    # Connections für die SourcesPage
    QObject.connect(self.sourcesPage.addButton, SIGNAL('clicked()'), self, SLOT('addSource()'))
    QObject.connect(self.sourcesPage.removeButton, SIGNAL('clicked()'), self, SLOT('removeSource()'))
    QObject.connect(self.sourcesPage.searchButton, SIGNAL('clicked()'), self, SLOT('openBrowser()'))
    QObject.connect(self.sourcesPage.sourceList, SIGNAL('itemClicked(QListWidgetItem*)'), self, SLOT('showSourceInfo(QListWidgetItem*)'))

    # Connections für die CustomPage
    QObject.connect(self.customPage.serviceList, SIGNAL('itemClicked(QListWidgetItem*)'), self, SLOT('synchronizeLineEdits()'))
    QObject.connect(self.customPage.serviceList, SIGNAL('itemDoubleClicked(QListWidgetItem*)'), self, SLOT('toggleEditmode()'))
    QObject.connect(self.customPage.editButton, SIGNAL('clicked()'), self, SLOT('toggleEditmode()'))
    QObject.connect(self.customPage.removeButton, SIGNAL('clicked()'), self, SLOT('removeCustomService()'))
    QObject.connect(self.customPage.addButton, SIGNAL('clicked()'), self, SLOT('addCustomService()'))
    QObject.connect(self.customPage.shareButton, SIGNAL('clicked()'), self, SLOT('uploadCustomService()'))

    # Connections für die SettingsPage
    QObject.connect(self.settingsPage.addButton, SIGNAL('clicked()'), self, SLOT('addVariable()'))
    QObject.connect(self.settingsPage.removeButton, SIGNAL('clicked()'), self, SLOT('removeVariable()'))
    QObject.connect(self.settingsPage.variableTable, SIGNAL('itemChanged(QTableWidgetItem*)'), self, SLOT('editVariable(QTableWidgetItem*)'))
    QObject.connect(self.settingsPage.pollingIntervalSpinbox, SIGNAL('valueChanged(double)'), self, SLOT('setPollingInterval(double)'))
    QObject.connect(self.settingsPage.sleepTimeSpinbox, SIGNAL('valueChanged(double)'), self, SLOT('setSleepTime(double)'))

    QObject.connect(self, SIGNAL('closeClicked()'), self, SLOT('toggleEditmode()'))

  ## (re)populates all widgets with current config data when window is shown
  def showEvent(self, event):
    print 'populating config widgets with data...'
    self.populateServiceLists()
    self.execInstallChecks()
    self.populateSourceList()
    self.populateCustomList()
    self.populateVariableList()
    self.populateSettings()


  ## Parses all XML source files and loads containing services.
  def readSources(self):
    self.sources = {}
    self.services = {}
    print 'looking for XML source files and trying to load them...'
    for fn in [fn for fn in os.listdir('%s/sources' % contentsdir) if fn.endswith('.xml') and not fn.startswith('.') ]:
      try: source = Source('%s/sources/%s' % (contentsdir, fn))
      except: print 'Error parsing %s.' % fn; continue
      self.sources[source.filename] = source
      for service in source.services:
        if not self.services.has_key(service.id) or self.services[service.id].priority <= service.priority:
          self.services[service.id] = service
      print 'successfully parsed %s (%i services).' % (fn, len(source.services))


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


  ## Returns a QProcessEnvironment instance containing all environment variables from config.
  def processEnvironment(self):
    variables = self.config.value('variables').toStringList()
    env = QProcessEnvironment.systemEnvironment()
    for i in range(len(variables)/2):
      env.insert(variables[2*i], variables[2*i+1])
    return env


# SERVICES PAGE ###########################################################################################################


  ## Populates both lists in the services page.
  # The right list can theoretically contain multiple services with the same ID.
  # When this happens, only the one with higher priority (or the one parsed later) is displayed.
  @pyqtSlot()
  def populateServiceLists(self):
    activeServicesIDs = self.config.value('activeServices').toStringList()
    self.servicesPage.activeServicesList.clear()
    self.servicesPage.inactiveServicesList.clear()
    for service in self.activeServices():
      item = QListWidgetItem(service.name)
      item.service = service
      self.servicesPage.activeServicesList.addItem(item)
      item.setIcon(QIcon(':/status-%s.png' % service.state[0]))
    for source in self.sources.values():
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
        item.setIcon(QIcon(':/status-%s.png' % service.state[0]))


  ## Initiates install checks for all services shown on the services page.
  # When a state is changed by the install check, the slot self.serviceStateChanged() is called, which updates the icon in the list.
  def execInstallChecks(self):
    print '(re)checking install status of all services...'
    env = self.processEnvironment()
    for service in self.services.values():
      QObject.connect(service, SIGNAL('stateChanged()'), self.serviceStateChanged)
      service.setProcessEnvironment(env)
      service.execInstallCheck()


  ## [slot] Updates the icon in the list for the service which has sent the stateChanged() signal.
  @pyqtSlot()
  def serviceStateChanged(self):
    service = self.sender()
    allItems = [self.servicesPage.activeServicesList.item(i) for i in range(self.servicesPage.activeServicesList.count())] + \
               [self.servicesPage.inactiveServicesList.item(i) for i in range(self.servicesPage.inactiveServicesList.count())]
    activeItems = [item for item in allItems if hasattr(item, 'service') and item.service == service]
    for item in activeItems:
      item.setIcon(QIcon(':/status-%s.png' % service.state[0]))


  ## [slot] Print info about the clicked service in the textarea.
  @pyqtSlot('QListWidgetItem*')
  def showServiceInfo(self, item):
    if hasattr(item, 'source'):
      self.servicesPage.infoTextarea.document().setHtml(item.source.description)
    elif hasattr(item, 'service'):
      s = item.service
      self.servicesPage.infoTextarea.document().setHtml('''
        <strong>%s</strong><br/>
        %s<br/>
        <table>
        <tr><td>Install check:</td><td>&nbsp;</td><td>%s</td></tr>
        <tr><td>Running check:</td><td>&nbsp;</td><td>%s</td></tr>
        <tr><td>Start command:</td><td>&nbsp;</td><td>%s</td></tr>
        <tr><td>Stop command:</td><td>&nbsp;</td><td>%s</td></tr>
        </table>''' % (s.name, s.description, s.installCheck, s.runningCheck, s.startCommand, s.stopCommand)
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
    activeServicesIDs = self.config.value("activeServices").toStringList()
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
    for source in self.sources.values():
      if source.filename == QString('custom.xml'): continue
      icon = KIcon('application-xml')
      item = QListWidgetItem(icon, '%s (%s, %i entries)' % (source.name if source.name else 'Unnamed', source.filename, len(source.services)))
      item.source = source
      self.sourcesPage.sourceList.addItem(item)


  ## [slot] Selects and copies a file into the sources directory (and repopulates sources list).
  @pyqtSlot()
  def addSource(self):
    filename = QFileDialog.getOpenFileName(self, 'moep', '~', 'Service definitions (*.xml)')
    if not filename: return
    fileinfo = QFileInfo(filename)
    destination = '%s/sources/%s' % (contentsdir, fileinfo.fileName())
    if QFile.exists(destination):
      answer = QMessageBox.question(self, 'Add source file', 'This will overwrite an existing file. Continue?', QMessageBox.Yes | QMessageBox.No)
      if answer == QMessageBox.No: return
    shutil.copyfile(filename, destination)
    self.readSources()
    self.populateServiceLists()
    self.execInstallChecks()
    self.populateSourceList()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Deletes a file from the sources directory (and repopulates sources list).
  @pyqtSlot()
  def removeSource(self):
    '''Löscht eine XML-Datei aus dem source-Verzeichnis'''
    answer = QMessageBox.question(self, 'Delete source file', 'Really delete the file?', QMessageBox.Yes | QMessageBox.No)
    if answer == QMessageBox.No: return
    item = self.sourcesPage.sourceList.currentItem()
    QFile.remove('%s/sources/%s' % (contentsdir, item.source.filename))
    self.readSources()
    self.populateServiceLists()
    self.populateSourceList()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Opens a browser and go to the sources download page on documentroot.net.
  @pyqtSlot()
  def openBrowser(self):
    answer = QMessageBox.question(self, 'Search for new sources', 'This will open a page in your web browser where additional service definitions can be downloaded.', QMessageBox.Ok | QMessageBox.Cancel)
    if answer == QMessageBox.Ok: QDesktopServices.openUrl(QUrl('http://www.documentroot.net/en/download-service-definitions'))


  ## [slot] Shows information about the clicked source in the text area.
  @pyqtSlot('QListWidgetItem*')
  def showSourceInfo(self, item):
    if not hasattr(item, 'source'): return
    self.sourcesPage.infoTextarea.document().setHtml(item.source.description)


# CUSTOM PAGE ###########################################################################################################


  ## Populates list of custom services from custom.xml source file.
  def populateCustomList(self):
    self.customPage.serviceList.clear()
    if not self.sources.has_key(QString('custom.xml')):
      self.customPage.serviceList.addItem('Error - custom.xml is missing or has been damaged')
      return
    for service in self.sources[QString('custom.xml')].services:
      icon = KIcon('text-x-generic')
      item = QListWidgetItem(icon, service.name)
      item.service = service
      self.customPage.serviceList.addItem(item)

  ## [slot] Switches editmode on or off.
  # @param save Save when disabling editmode?
  # When entering editmode, the list is disabled and the line edits are enabled and vice versa when editmode is left.
  # In editmode, the edit button becomes a save button and the remove button becomes a cancel button.
  @pyqtSlot()
  def toggleEditmode(self, save = True):

    if self.editmode:

      if save:
        # Konfiguration schreiben und relevante Bereiche aktualisieren
        self.synchronizeService()
        self.sources[QString('custom.xml')].writeBack()
        self.emit(SIGNAL('configurationChanged()')) # Falls sich der Name geändert hat
        self.populateCustomList()
        self.populateServiceLists()
        self.execInstallChecks()
      else:
        # LineEdits wieder mit ursprünglichen Werten füllen
        self.synchronizeLineEdits()

      # Stoppe Editmode
      self.setLineEditsEnabled(False)
      self.editmode = False

      # Widget-Status anpassen
      self.customPage.editButton.setText('Edit selected')
      self.customPage.removeButton.setText('Remove selected')
      self.customPage.addButton.setEnabled(True)
      self.customPage.shareButton.setEnabled(True)
      self.customPage.serviceList.setEnabled(True)

    elif self.customPage.serviceList.currentItem():

      # Starte Editmode
      item = self.customPage.serviceList.currentItem()
      self.editmode = True

      # Widget-Status anpassen
      self.setLineEditsEnabled(True)
      self.synchronizeLineEdits()
      self.customPage.editButton.setText('Save changes')
      self.customPage.removeButton.setText('Cancel editing')
      self.customPage.addButton.setEnabled(False)
      self.customPage.shareButton.setEnabled(False)
      self.customPage.serviceList.setEnabled(False)


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

    if self.editmode:
      self.toggleEditmode(False)

    elif self.customPage.serviceList.currentItem():
      answer = QMessageBox.question(self, 'Remove service', 'Really delete the selected service?', QMessageBox.Yes | QMessageBox.No)
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
    service.name = 'New Service - edit me'
    service.description = 'Enter a short, concise description here'
    self.sources[QString('custom.xml')].services.append(service)
    self.sources[QString('custom.xml')].writeBack()
    self.readSources()
    self.populateServiceLists()
    self.execInstallChecks()
    self.populateCustomList()

    # Letzten Eintrag markieren
    count = self.customPage.serviceList.count()
    self.customPage.serviceList.setCurrentRow(count-1)
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
    answer = QMessageBox.question(self, 'Upload service definition', 'This will open a page in your web browser where you can submit the selected service definition to the community.', QMessageBox.Ok | QMessageBox.Cancel)
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


# CUSTOM PAGE ###########################################################################################################

  ## Populates the table with environment variables.
  def populateVariableList(self):
    self.settingsPage.variableTable.blockSignals(True)
    self.settingsPage.variableTable.clearContents()
    variables = self.config.value('variables').toStringList()
    self.settingsPage.variableTable.setRowCount(len(variables)/2)
    for i in range(len(variables)/2):
      self.settingsPage.variableTable.setItem(i, 0, QTableWidgetItem(variables[2*i]))
      self.settingsPage.variableTable.setItem(i, 1, QTableWidgetItem(variables[2*i+1]))
    self.settingsPage.variableTable.blockSignals(False)


  ## Populates everything in the settings frame (currently only polling time and sleep time).
  def populateSettings(self):
    self.settingsPage.pollingIntervalSpinbox.setValue(self.config.value('pollingInterval').toDouble()[0])
    self.settingsPage.sleepTimeSpinbox.setValue(self.config.value('sleepTime').toDouble()[0])


  ## [slot] Adds a new dummy environment variale to the internal config and repopulates the table.
  @pyqtSlot()
  def addVariable(self):
    variables = self.config.value('variables').toStringList()
    variables << 'NAME'
    variables << '<value>'
    self.config.setValue('variables', variables)
    self.populateVariableList()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Saves changes to the edited variable.
  # @param item The item which has been edited.
  @pyqtSlot('QTableWidgetItem*')
  def editVariable(self, item):
    variables = self.config.value('variables').toStringList()
    row = self.settingsPage.variableTable.row(item)
    regex = QRegExp('([A-Z_][A-Z0-9_]*)', Qt.CaseInsensitive)
    if not regex.exactMatch( self.settingsPage.variableTable.item(row, 0).text() ):
      QMessageBox.warning(self, 'Warning', 'Only alphanumeric characters are allowed in the variable name, so this will not work. Please edit.', QMessageBox.Ok)
    variables[2*row] = self.settingsPage.variableTable.item(row, 0).text()
    variables[2*row+1] = self.settingsPage.variableTable.item(row, 1).text()
    self.config.setValue('variables', variables)
    self.populateVariableList()
    self.execInstallChecks()
    self.emit(SIGNAL('configurationChanged()'))


  ## [slot] Remove selected variable from internal config and repopulate table.
  @pyqtSlot()
  def removeVariable(self):
    variables = self.config.value('variables').toStringList()
    rowsToRemove = list(set([self.settingsPage.variableTable.row(item) for item in self.settingsPage.variableTable.selectedItems()]))
    if len(rowsToRemove) == 0: return
    for row in reversed(sorted(rowsToRemove)):
      variables.removeAt(2*row+1)
      variables.removeAt(2*row)
    self.config.setValue('variables', variables)
    self.populateVariableList()
    self.emit(SIGNAL('configurationChanged()'))


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


class SourcesPage(QWidget, Ui_Sources):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

class ServicesPage(QWidget, Ui_Services):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

class CustomPage(QWidget, Ui_Custom):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)

class SettingsPage(QWidget, Ui_Settings):
  def __init__(self, configDialog):
    QWidget.__init__(self)
    self.setupUi(self)



