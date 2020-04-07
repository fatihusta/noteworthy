import argparse
import docker
import os
import sys

import getpass

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
        from noteworthy.hub import HubController
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
            wg.init('wg0', my_ip, wg_key_path)
            wg.add_peer('wg0', peer_pubkey, peer_ip)
        elif role == 'taproot':
            my_ip = '10.0.0.2/24'
            peer_ip = '10.0.0.1/32'
            # provision link node
            hc = HubController.get_grpc_stub(f"{os.environ['NOTEWORTHY_HUB']}:8000")
            res = hc.reserve_domain(os.environ['NOTEWORTHY_DOMAIN'], pubkey, None)
            wg.init('wg0', my_ip, wg_key_path)
            wg.add_peer('wg0', res.link_wg_pubkey, peer_ip, res.link_wg_endpoint)

        else:
            raise Exception(f'Unrecognized NOTEWORTHY_ROLE: {role}')


    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl wireguard ')
        cls.sub_parser.add_argument('argument', nargs='*', help='hostname of hub to join')
        cls.sub_parser.add_argument('--no-cache', action="store_true", help="discard container\
 build cache when building WireGuard container.")


Controller = WireGuardController