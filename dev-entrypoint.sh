#!/bin/bash

cd /opt/noteworthy/grpcz
rm -rf build/ dist/
python setup.py develop

cd /opt/noteworthy/notectl/applications/launcher
python setup.py develop

cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py develop

# Install all plugins
for plugin in plugins/*/; do
    cd $plugin
    python setup.py develop
    ./install.sh
    cd -
done


bash
