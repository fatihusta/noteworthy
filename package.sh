#!/bin/bash

cd /opt/noteworthy/grpcz
rm -rf build/ dist/
pip install -e .

cd /opt/noteworthy/notectl
rm -rf build/ dist/
pip install -e .

# install package plugin
cd plugins/package
pip install -e .
cd -

notectl package package $APP_NAME $VERSION
