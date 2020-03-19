#!/bin/sh

if [[ "$(uname)" == "Linux" ]]; then
    # TODO handle rekeying for every invocation
    if [ ! -f "/tmp/private" ]; then
        wg_privkey=$(wg genkey)
        echo $wg_privkey > /tmp/private
        overlay_ip="dynamic"
    else
        wg_privkey=$(cat /tmp/private)
        overlay_ip=$(cat /tmp/overlay_ip)
    fi
    pubkey=$(echo $wg_privkey |wg pubkey)
elif [[ "$(uname)" == "Darwin" ]]; then
    # Use docker to access wireguard-tools
    wg_privkey=$(docker run --rm -it wg:latest wg genkey)
    pubkey=$(echo $wg_privkey |docker run -i --rm wg:latest wg pubkey)
    #echo "Generated WireGuard Pub Key:" $pubkey
fi

# Send pubkey to hub
# The following command should either return Peer YAML to be parsed by wg-easy-set
# or just complete WireGuard config to be copy and pasted into Windows/Mac desktop client

# TODO Use SSH CA
ssh -p 2222 -o StrictHostKeyChecking=no -i /home/wg-easy/.ssh/id_rsa wg-easy@$HUB_HOST $PEER_NAME $pubkey $overlay_ip
