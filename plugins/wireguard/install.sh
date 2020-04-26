#!/bin/bash

# Install WireGuard
echo "deb http://deb.debian.org/debian buster-backports main" >> /etc/apt/sources.list
apt update
apt install --no-install-recommends wireguard-tools -y