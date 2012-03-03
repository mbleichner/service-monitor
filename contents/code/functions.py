# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *


## Returns a function which is the chain of all parameter functions
def chain(*args):
  def fnc():
    for f in args:
      f()
  return fnc


## Shortcut for creating a DOM element containing text data.
def mkTextElement(doc, tagName, textData):
  node = doc.createElement(tagName)
  textNode = doc.createTextNode(textData)
  node.appendChild(textNode)
  return node


## Lays one icon over the other one, respecting alpha channels
def combineIcons(base, overlay):
  base = base.pixmap(22, 22).toImage()
  overlay = overlay.pixmap(13, 13).toImage()
  for x in range(13):
    for y in range(13):
      p1 = int2rgba(base.pixel(9+x,9+y))
      p2 = int2rgba(overlay.pixel(x,y))
      alpha = p2[3] / 255.0
      r = int( alpha * p2[0] + (1-alpha) * p1[0] )
      g = int( alpha * p2[1] + (1-alpha) * p1[1] )
      b = int( alpha * p2[2] + (1-alpha) * p1[2] )
      a = max( p1[3], p2[3] )
      base.setPixel(9+x, 9+y, rgba2int(r,g,b,a))
  return QIcon(QPixmap.fromImage(base))


def changeSaturation(icon, f):
  if f == 1: return QIcon(icon)
  icon = icon.pixmap(22, 22).toImage()
  for x in range(22):
    for y in range(22):
      p = int2rgba(icon.pixel(x, y))
      v = (p[0] + p[1] + p[2]) / 3
      r = f*p[0] + (1-f)*v
      g = f*p[1] + (1-f)*v
      b = f*p[2] + (1-f)*v
      icon.setPixel(x, y, rgba2int(r, g, b, p[3]))
  return QIcon(QPixmap.fromImage(icon))


def rgba2int(r,g,b,a):
  return int(a) * 16**6 + int(r) * 16**4 + int(g) * 16**2 + int(b) * 16**0


def int2rgba(n):
  n = int(n)
  return ( (n / 16**4) % 16**2, (n / 16**2) % 16**2, (n / 16**0) % 16**2, (n / 16**6) % 16**2 )


## Delete contents of a QGraphicsItem recursively
def deleteContentsRecursively(item):
  if item is None:
    return
  elif item.isLayout():
    while item.count():
      deleteContentsRecursively(item.itemAt(0))
      item.removeAt(0)
  elif isinstance(item, QObject):
    item.deleteLater()

    