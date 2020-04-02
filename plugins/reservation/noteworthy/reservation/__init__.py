import argparse
from noteworthy.notectl.plugins import NoteworthyPlugin

from grpcz import grpc_controller, grpc_method

@grpc_controller
class ReservationController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-reservation'

    def __init__(self):
        pass

    @grpc_method
    def reserve(self, **kwargs):
        domain = kwargs['argument'][0].decode()
        #public_key = kwargs['argument'][1].decode()
        return f'Successfully reserved {domain}'

    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl grpc')
        cls.sub_parser.add_argument('argument', nargs='*', help='hostname of hub to join')
        cls.sub_parser.add_argument('--rpc', action='store_true', help='invoke command on remote host')


Controller = ReservationController
