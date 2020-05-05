import argparse

from clicz import cli_method

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.notectl.plugins import PluginManager


from grpcz import GRPCZServer

class GrpcController(NoteworthyPlugin):
    '''manage grpc server
    '''
    PLUGIN_NAME = 'grpc'

    def __init__(self):
        self.server = GRPCZServer()
        self._register_grpc_services()

    def _register_grpc_services(self):
        for plugin, module in PluginManager.load_plugins().items():
            if hasattr(module.Controller, 'grpc_controller'):
                print(f'Registered GRPC controller for plugin: {plugin}')
                self.server.register_controller(module.Controller())

    @cli_method
    def run(self):
        '''start grpc server, blocking
        '''
        self.server.start()

    def start(self, *args, **kwargs):
        self._start(self.PLUGIN_NAME)

Controller = GrpcController
