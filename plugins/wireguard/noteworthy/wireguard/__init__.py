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

    def start(self, **kwargs):
        if self.is_first_run:
            self.create_config_dir()
            wg.genkey(os.path.join(self.config_dir, 'wg.key'))
        else:
            print('already configed')



    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl wireguard ')
        cls.sub_parser.add_argument('argument', nargs='*', help='hostname of hub to join')
        cls.sub_parser.add_argument('--no-cache', action="store_true", help="discard container\
 build cache when building WireGuard container.")


Controller = WireGuardController