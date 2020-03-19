#!/bin/bash

cd $WORKSPACE/notectl
rm -rf build/ dist/
python setup.py install
notectl version

for plugin in plugins/*/; do
    cd $plugin
    rm -rf build/ dist/
    python setup.py install
    cd -
done

pytest

# Run tests for each plugin
for plugin in plugins/*/; do
    cd $plugin
    pytest
    cd -
done