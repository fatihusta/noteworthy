#!/bin/bash

cd /opt/noteworthy/dist

for plugin in */; do
    cd $plugin
    rm -rf build/ dist/
    python setup.py install
    ./install.sh
    cd -
done
