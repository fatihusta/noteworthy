import docker
import os
import sys

import getpass
import yaml

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.wireguard import wg

from clicz import cli_method


class WireGuardController(NoteworthyPlugin):

    PLUGIN_NAME = 'wireguard'

    def __init__(self):
        super().__init__(__file__)
        self.docker = docker.from_env()

    @cli_method
    def pubkey(self):
        '''
        Loop forever until wg.key shows up
        '''
        import time
        key_path = os.path.join(self.config_dir, 'wg.key')
        count = 0
        while True:
            if count > 30:
                break
            time.sleep(1)
            count = count + 1
            pubkey = wg.pubkey(key_path).strip()
            if len(pubkey) == 44:
                print(pubkey)
                break

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
            # user key from env var
            os.system(f"echo {os.environ['LINK_WG_KEY']} > {wg_key_path}")
        elif role == 'taproot':
            my_ip = '10.0.0.2/24'
            peer_ip = '10.0.0.1/32'
            if not os.path.exists(os.path.join(self.config_dir, 'link.yaml')):
                # provision link node
                from noteworthy.reservation_client import ReservationController
                rc = ReservationController.get_grpc_stub(f"{os.environ['NOTEWORTHY_HUB']}:8000")
                res = rc.create_link(os.environ['NOTEWORTHY_DOMAIN'], pubkey, os.environ['NOTEWORTHY_AUTH_CODE'])
                if res.error:
                    raise Exception(f'Failed to create link. Server Error:\n\t{res.error}\n')
                self.store_link(res.link_wg_endpoint, res.link_wg_pubkey, res.link_udp_proxy_endpoint, res.link_udp_proxy_endpoint_2)
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
        if self.is_first_run:
            self.commit_successful_config()

    def store_link(self, endpoint, pubkey, link_udp_proxy_endpoint, link_udp_proxy_endpoint_2):
        link_data = {'endpoint': endpoint, 'pubkey': pubkey, 'udp_proxy_endpoint': link_udp_proxy_endpoint, 'udp_proxy_endpoint_2': link_udp_proxy_endpoint_2}
        with open(os.path.join(self.config_dir, 'link.yaml'), 'w') as yaml_file:
            yaml_file.write(yaml.dump(link_data))

    def get_link(self,):
        with open(os.path.join(self.config_dir, 'link.yaml'), 'r') as yaml_file:
            link_data = yaml.safe_load(yaml_file.read())
        return link_data

Controller = WireGuardController
