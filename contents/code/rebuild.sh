#/bin/bash
# Rebuild resources, translations and UI dialogs. Use -r to remove obsolete translation strings.

# parse command line params
for PAR in $@; do
  case $PAR in
    -r)
      PYLUPDATE='-noobsolete'
      ;;
    -h|--help)
      echo "Usage: rebuild.py [options]"
      echo
      echo "Possible options are:"
      echo "-h --help   show this message"
      echo "-r          remove obsolete strings from .tr files"
      exit 0
      ;;
  esac
done

# DIALOGS
for dialog in 'Services' 'Settings' 'Custom' 'Sources'
do
  pyuic4 dialogs/${dialog}.ui > generated/${dialog}_ui.py
  sed -e '1p;/^#/d' -i generated/${dialog}_ui.py
done

# ICONS
pyrcc4 resources/icons/icons.qrc > generated/icons_rc.py
for icontheme in 'indicators_default'
do
  pyrcc4 resources/${icontheme}/theme.qrc > generated/${icontheme}_rc.py
  sed -e '1p;/^#/d' -i generated/${icontheme}_rc.py
done

# TRANSLATIONS
for lang in 'de' 'fr' 'es'
do
  pylupdate4 $PYLUPDATE *.py generated/*.py -ts translations/${lang}.ts
  lrelease translations/${lang}.ts -qm translations/${lang}.qm
done