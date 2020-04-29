#!/bin/bash

pip install -r /opt/noteworthy/requirements.txt

cd /opt/noteworthy/grpcz
rm -rf build/ dist/
python setup.py develop

cd /opt/noteworthy/applications/launcher
python setup.py develop

cd /opt/noteworthy
rm -rf build/ dist/
python setup.py develop

# Install all plugins
for plugin in plugins/*/; do
    cd $plugin
    python setup.py develop
    if [ -f "./install.sh" ]; then
        ./install.sh
    fi
    cd -
done

