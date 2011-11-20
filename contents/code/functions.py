# -*- coding: utf-8 -*-

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