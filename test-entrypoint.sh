#!/bin/bash

cd $WORKSPACE/notectl
rm -rf build/ dist/
python setup.py install
notectl version

cd plugins/test_plugin
rm -rf build/ dist/
python setup.py install
cd -

pytest