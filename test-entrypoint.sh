#!/bin/bash
set -e

cd $WORKSPACE/grpcz
rm -rf build/ dist/
python setup.py install
cd -

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

# integration tests
# echo "Starting integration tests..."
# notectl wireguard start_hub
# notectl wireguard start_peer
# sleep 3
# docker exec wg-easy-hub ping -c 5 -W 1 10.0.0.2
# notectl wireguard stop wg-easy-hub wg-easy-peer