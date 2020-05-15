#!/bin/bash

NOTEWORTHY_DIR=$WORKSPACE/notectl

pip install -r $NOTEWORTHY_DIR/requirements.dev.txt

cd $NOTEWORTHY_DIR/matrixbz
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/grpcz
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/procz
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/clicz
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/applications/launcher
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/applications/messenger
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/applications/vpn
rm -rf build/ dist/
python setup.py install

cd $NOTEWORTHY_DIR/noteworthy
rm -rf build/ dist/
python setup.py install


# Install all plugins
for plugin in $NOTEWORTHY_DIR/plugins/*/; do
    cd $plugin
    python setup.py install
    if [ -f "./install.sh" ]; then
        ./install.sh
    fi
    cd -
done
