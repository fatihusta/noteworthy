#!/bin/bash

cd $WORKSPACE/notectl
rm -rf build/ dist/
python setup.py install
notectl
pytest