#!/bin/bash

for plugin in nginx wireguard http_service
do
    cd $plugin
    rm -rf build/ dist/
    python setup.py install
    cd -
done
