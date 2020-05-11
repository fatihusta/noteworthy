#!/bin/bash


if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    apt update
    apt install qrencode -y
fi