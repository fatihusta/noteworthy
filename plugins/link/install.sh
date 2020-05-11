#!/bin/bash

apt update
apt install socat -y
rm -rf /var/lib/apt/lists/*