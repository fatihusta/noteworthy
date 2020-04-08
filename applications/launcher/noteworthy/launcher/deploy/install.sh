#!/bin/bash

cd /opt/noteworthy/dist

for plugin in */; do
    cd $plugin
    python setup.py install
    ./install.sh
    cd -
done
