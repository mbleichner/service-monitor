#/bin/bash

for dialog in 'Services' 'Settings' 'Custom' 'Sources'
do
  pyuic4 $dialog.ui > $dialog.py
done

for resource in 'Icons'
do
  pyrcc4 $resource.qrc > ${resource}_rc.py
done