import argparse
import docker
import os
import sys

import getpass
import yaml

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.wireguard import wg


class WireGuardController(NoteworthyPlugin):

    PLUGIN_NAME = 'wireguard'

    def __init__(self):
        super().__init__(__file__)
        self.docker = docker.from_env()

    def pubkey(self, **kwargs):
        '''
        Loop forever until wg.key shows up
        Used in provisioning.. probably a bad idea
        '''
        import time
        key_path = os.path.join(self.config_dir, 'wg.key')
        count = 0
        while not os.path.exists(key_path):
            if count > 30:
                break
            time.sleep(.5)
            count = count + 1
        print(wg.pubkey(key_path))

    def start(self, **kwargs):
        wg_key_path = os.path.join(self.config_dir, 'wg.key')
        if self.is_first_run:
            self.create_config_dir()
            wg.genkey(wg_key_path)
        pubkey = wg.pubkey(wg_key_path)
        role = os.environ['NOTEWORTHY_ROLE']
        if role == 'hub':
            # ip = '10.9.0.1/24'
            # for now, do nothing
            return
        elif role == 'link':
            my_ip = '10.0.0.1/24'
            peer_ip = '10.0.0.2/32'
            peer_pubkey = os.environ['TAPROOT_PUBKEY']
            endpoint = None
        elif role == 'taproot':
            my_ip = '10.0.0.2/24'
            peer_ip = '10.0.0.1/32'
            if not os.path.exists(os.path.join(self.config_dir, 'link.yaml')):
                # provision link node
                from noteworthy.reservation_client import ReservationController
                rc = ReservationController.get_grpc_stub(f"{os.environ['NOTEWORTHY_HUB']}:8000")
                res = rc.reserve_domain(os.environ['NOTEWORTHY_DOMAIN'], pubkey, os.environ['NOTEWORTHY_AUTH_CODE'])
                self.store_link(res.link_wg_endpoint, res.link_wg_pubkey)
                peer_pubkey = res.link_wg_pubkey
                endpoint = res.link_wg_endpoint
            else:
                res = self.get_link()
                peer_pubkey = res['pubkey']
                endpoint = res['endpoint']

        else:
            raise Exception(f'Unrecognized NOTEWORTHY_ROLE: {role}')

        wg.init('wg0', my_ip, wg_key_path)
        wg.add_peer('wg0', peer_pubkey, peer_ip, endpoint)

    def store_link(self, endpoint, pubkey):
        link_data = {'endpoint': endpoint, 'pubkey': pubkey}
        with open(os.path.join(self.config_dir, 'link.yaml'), 'w') as yaml_file:
            yaml_file.write(yaml.dump(link_data))

    def get_link(self,):
        with open(os.path.join(self.config_dir, 'link.yaml'), 'r') as yaml_file:
            link_data = yaml.safe_load(yaml_file.read())
        return link_data

Controller = WireGuardController
