#!/usr/bin/python

import sys, dbus
from PyQt4.QtCore import *


tmp = file('icon.png', 'r')
data = tmp.read()
tmp.close()
QFile.remove('icon.png')

byteArray = QByteArray(data)

message = sys.argv[1]

knotify = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
knotify.event("warning", "kde", [], "Service state changed", str(message), QByteArray(data), [], 0, 0, dbus_interface="org.kde.KNotify")