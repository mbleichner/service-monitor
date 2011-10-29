# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtXml import *
from ServiceMonitor import *

## The main function called by Plasma.
def CreateApplet(parent):
  return ServiceMonitor(parent)