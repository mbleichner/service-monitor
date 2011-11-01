# -*- coding: utf-8 -*-
import os

from ServiceMonitor import *

codedir = os.path.dirname(__file__)

# Set up localization
locale = QLocale.system().name()
translator = QTranslator()
translator.load(locale, '%s/translations' % codedir)
QApplication.installTranslator(translator)

## The main function called by Plasma.
def CreateApplet(parent):
  return ServiceMonitor(parent)