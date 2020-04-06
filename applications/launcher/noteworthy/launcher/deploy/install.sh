#!/bin/bash

cd /opt/noteworthy/dist

for plugin in */; do
    cd $plugin
    python setup.py install
    ./install.sh
    cd -
done

# Install WireGuard
apt install software-properties-common -y
add-apt-repository ppa:wireguard/wireguard -y
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys AE33835F504A1A25
apt update
apt install wireguard-tools -y
