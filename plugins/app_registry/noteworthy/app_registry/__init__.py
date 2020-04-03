import argparse
import docker
import os
import sys

import getpass

from noteworthy.notectl.plugins import NoteworthyPlugin
from grpcz import grpc_controller, grpc_method


@grpc_controller
class AppRegistryController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-app-registry'

    def __init__(self):
        pass

    def build(self, **kwargs):
        # TODO: build the container
        pass

    def start():
        # TODO: start the server
        pass

    @grpc_method
    def update_app(self, **kwargs):
        # TODO: write file and update yml
        pass


Controller = AppRegistryController
