#!/bin/bash

cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py install

notectl
