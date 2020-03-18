#!/bin/bash

cd $WORKSPACE/notectl
rm -rf build/ dist/
python setup.py install
notectl

cd plugins/test_plugin
python setup.py install
cd -

pytest