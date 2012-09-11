# -*- coding: utf-8 -*-
import os

## @mainpage
## <p>For a description of Service Monitor, see http://kde-look.org/content/show.php/Service+Monitor?content=125203</p>
##
## <p>Development repository is hosted on GitHub: https://github.com/mbleichner/service-monitor</p>

from ServiceMonitor import *

codedir = os.path.dirname(__file__)
contentsdir = os.path.dirname(codedir)
maindir = os.path.dirname(contentsdir)

# Set up localization
locale = QLocale.system().name()
translator = QTranslator()
translator.load(locale, '%s/translations' % codedir)
QApplication.installTranslator(translator)

## The main function called by Plasma.
def CreateApplet(parent):
  return ServiceMonitor(parent)

if __name__ == "__main__":
    os.system("plasmoidviewer %s" % maindir)