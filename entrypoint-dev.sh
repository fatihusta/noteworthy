#!/bin/bash
# This script is used to produce the Noteworthy development environment container.
#
#
#           WARNING: Technical debt #TODO, changes here must be also made to docker-dev.sh
#
#
# To re-run this dev container provisioning script
# rm .noteworthy-dev-install-lock then run `make shell` 


if [ -f .noteworthy-dev-install-lock ]; then
    bash
else

    cd /opt/noteworthy/matrixbz
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/grpcz
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/procz
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/clicz
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/applications/launcher
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/applications/messenger
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/applications/vpn
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy/applications/cms
    rm -rf build/ dist/
    python setup.py develop

    cd /opt/noteworthy
    rm -rf build/ dist/
    python setup.py develop

    # Install all plugins
    for plugin in plugins/*/; do
        cd $plugin
        python setup.py develop
        cd -
    done

date > .noteworthy-dev-install-lock
bash

fi
