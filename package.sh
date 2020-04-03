#!/bin/bash

pip install grpcio grpcio-tools
cd /opt/noteworthy/grpcz
rm -rf build/ dist/
python setup.py develop

cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py develop

# install package plugin
cd plugins/package
python setup.py develop
cd -

notectl package package $APP_NAME $VERSION
