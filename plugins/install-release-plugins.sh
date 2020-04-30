#!/bin/bash

cd $1
rm -rf build/ dist/
if [ -f "./install.sh" ]; then
    ./install.sh
fi
python setup.py install
