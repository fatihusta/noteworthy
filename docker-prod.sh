#!/bin/bash

cd /opt/noteworthy/grpcz
rm -rf build/ dist/
python setup.py install

cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py install
notectl version

for plugin in plugins/*/; do
    cd $plugin
    rm -rf build/ dist/
    python setup.py install
    cd -
done

for application in applications/*/; do
    cd $application
    rm -rf build/ dist/
    python setup.py install
    cd -
done

