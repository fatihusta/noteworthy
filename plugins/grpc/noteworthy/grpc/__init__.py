import argparse

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.notectl.plugins import PluginManager


from grpcz import GRPCZServer

class GrpcController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-grpc'

    def __init__(self):
        self.server = GRPCZServer()
        self._register_grpc_services()

    def _register_grpc_services(self):
        for plugin, module in PluginManager.load_plugins().items():
            if hasattr(module.Controller, 'grpc_controller'):
                print(f'Registered GRPC controller for plugin: {plugin}')
                self.server.register_controller(module.Controller())

    def start(self, *args, **kwargs):
        self.server.start()

    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl grpc')
        cls.sub_parser.add_argument('argument', nargs='*', help='hostname of hub to join')


Controller = GrpcController
