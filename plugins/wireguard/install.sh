#!/bin/bash

# Install WireGuard
apt update
apt install software-properties-common -y
add-apt-repository ppa:wireguard/wireguard -y
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys AE33835F504A1A25
apt update
apt install --no-install-recommends wireguard-tools -y