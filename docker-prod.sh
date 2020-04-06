#!/bin/bash

cd /opt/noteworthy/grpcz
rm -rf build/ dist/
python setup.py install

cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py install

cd /opt/noteworthy/notectl/applications/launcher
rm -rf build/ dist/
python setup.py install

# TODO don't install every plugin
for plugin in plugins/*/; do
    cd $plugin
    rm -rf build/ dist/
    python setup.py install
    cd -
done

notectl package package launcher
