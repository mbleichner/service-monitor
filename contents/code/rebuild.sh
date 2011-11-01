#/bin/bash

# rebuilds resources, translations and UI dialogs.

# DIALOGS
for dialog in 'Services' 'Settings' 'Custom' 'Sources'
do pyuic4 dialogs/${dialog}.ui > generated/${dialog}_ui.py; done

# ICONS
pyrcc4 resources/icons/icons.qrc > generated/icons_rc.py
for icontheme in 'indicators_default'
do pyrcc4 resources/${icontheme}/theme.qrc > generated/${icontheme}_rc.py; done

# TRANSLATIONS
for lang in 'de'
do
  pylupdate4 *.py generated/*.py -ts translations/${lang}.ts
  lrelease translations/${lang}.ts -qm translations/${lang}.qm
done