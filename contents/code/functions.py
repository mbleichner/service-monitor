# -*- coding: utf-8 -*-

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
  base = base.pixmap(20, 20).toImage()
  overlay = overlay.pixmap(12, 12).toImage()

  # Basisbild etwas abdunkeln
  for x in range(20):
    for y in range(20):
      p = int2rgba(base.pixel(x, y))
      base.setPixel(x, y, rgba2int(p[0]*0.8, p[1]*0.8, p[2]*0.8, p[3]))

  # Overlay darüber zeichnen
  for x in range(12):
    for y in range(12):
      p1 = int2rgba(base.pixel(8+x,8+y))
      p2 = int2rgba(overlay.pixel(x,y))
      alpha = p2[3] / 255.0
      r = int( alpha * p2[0] + (1-alpha) * p1[0] )
      g = int( alpha * p2[1] + (1-alpha) * p1[1] )
      b = int( alpha * p2[2] + (1-alpha) * p1[2] )
      a = max( p1[3], p2[3] )
      base.setPixel(8+x, 8+y, rgba2int(r,g,b,a))
  return QIcon(QPixmap.fromImage(base))


def rgba2int(r,g,b,a):
  return int(a) * 16**6 + int(r) * 16**4 + int(g) * 16**2 + int(b) * 16**0


def int2rgba(n):
  n = int(n)
  return ( (n / 16**4) % 16**2, (n / 16**2) % 16**2, (n / 16**0) % 16**2, (n / 16**6) % 16**2 )

