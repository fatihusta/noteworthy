import argparse
from noteworthy.notectl.plugins import NoteworthyPlugin

from grpcz import grpc_controller, grpc_method

@grpc_controller
class ReservationController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-reservation'

    def __init__(self):
        pass

    @grpc_method
    def reserve(self, domain, public_key):
        domain = domain.decode()
        print(domain)
        print(public_key)
        return f'Successfully reserved {domain}'

    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl grpc')
        cls.sub_parser.add_argument('argument', nargs='*', help='hostname of hub to join')


Controller = ReservationController
