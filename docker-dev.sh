#!/bin/bash
# This script is used to produce the Noteworthy development environment container.
#
#
#           WARNING: Technical debt #TODO, changes here must be also made to entrypoint-dev.sh
#
#
    cd /opt/noteworthy/matrixbz
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/grpcz
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/procz
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/clicz
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/applications/launcher
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/applications/messenger
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/applications/vpn
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy/applications/cms
    rm -rf build/ dist/
    pip install -e .

    cd /opt/noteworthy
    rm -rf build/ dist/
    pip install -e .

    # Install all plugins
    for plugin in plugins/*/; do
        cd $plugin
        pip install -e .
        if [ -f "./install.sh" ]; then
            ./install.sh
        fi
        cd -
    done