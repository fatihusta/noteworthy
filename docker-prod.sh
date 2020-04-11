#!/bin/bash

cd /opt/noteworthy/grpcz
rm -rf build/ dist/
python setup.py install

cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py install

# TODO don't install every plugin
for plugin in package hub nginx wireguard
do
    cd plugins/$plugin
    rm -rf build/ dist/
    python setup.py install
    cd -
done

cd /opt/noteworthy/notectl/applications/launcher
rm -rf build/ dist/
python setup.py install

notectl package package launcher
