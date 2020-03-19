#!/bin/bash
cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py develop

# Install all plugins
for plugin in plugins/*/; do
    cd $plugin
    python setup.py develop
    cd -
done


bash
