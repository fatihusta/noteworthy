#!/usr/bin/python3

import os
import sys

import yaml


from noteworthy import wg_lib as wg

if __name__ == '__main__':
    peer_spec = yaml.safe_load(sys.stdin.read())
    # Bad hack that prevents us from supporting multiple hubs
    # to avoid adding ourself as a peer (cuz wg-easy|wg-easy-set is hardcoded in entrypoiny for every container)
    if '@hub' in peer_spec['name']:
        print('Not adding peers cuz Im a hub and I add them when the contact me! Which is terrible and should be fixed ASAP. Hub should init network stack on boot; move under flag in entrypoint?')
        sys.exit(0)
    # write out our overlay_ip
    os.system(f"echo {peer_spec['ip']} > /tmp/overlay_ip")
    wg.wg_init('wg0', f"{peer_spec['ip']}/24", '/tmp/private')
    for peer in peer_spec['peers']:
        for peer_name, spec in peer.items():
            print(f'Adding peer {peer_name}')
            print(f"wg0 - {spec['pubkey']} - {spec['allowed-ips']} - {spec['endpoint']}")
            wg.add_peer('wg0', spec['pubkey'], spec['allowed-ips'], spec['endpoint'])

