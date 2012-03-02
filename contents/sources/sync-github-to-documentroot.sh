#!/bin/bash

wget https://github.com/mbleichner/service-monitor/tarball/master -O service-monitor-master.tar.gz
scp service-monitor-master.tar.gz documentroot@documentroot.net:homepage/service-monitor/
rm service-monitor-master.tar.gz
