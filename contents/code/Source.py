# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtXml import *

from Service import *

import os


## This class reads service definitions from XML files and can write them back.
class Source(QObject):


  def __init__(self, filepath, parent = None):
    QObject.__init__(self, parent)

    self.filepath = filepath
    self.filename = QString(os.path.basename(filepath))

    # DOM laden
    dom = QDomDocument()
    file = QFile(self.filepath)
    dom.setContent(file)
    root = dom.documentElement()

    assert root.isElement()
    assert root.toElement().tagName() == 'services'

    self.services = []

    node = root.firstChild()
    while not node.isNull():
      if node.isElement() and node.toElement().tagName() == 'service':
        s = Service.loadFromDomNode(node, self)
        self.services.append(s)
      if node.isElement() and node.toElement().tagName() == 'name':
        self.name = node.toElement().firstChild().toText().data().trimmed()
      if node.isElement() and node.toElement().tagName() == 'description':
        self.description = node.toElement().firstChild().toText().data().trimmed()
      node = node.nextSibling()

    file.close()


  ## Writes all services back to the xml file.
  def writeBack(self):
    doc = QDomDocument()
    root = doc.createElement('services')
    doc.appendChild(root)
    root.appendChild(mkTextElement(doc, 'name', self.name))
    root.appendChild(mkTextElement(doc, 'description', self.description))
    for service in self.services:
      root.appendChild(service.saveToDomNode(doc))
    content = unicode(doc.toString(2))

    f = QFile(self.filepath)
    f.open(QIODevice.WriteOnly)
    f.write(content)
    f.close()

