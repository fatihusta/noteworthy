from noteworthy.notectl.plugins import NoteworthyPlugin
from grpcz import grpc_controller, grpc_method

class VpnController(NoteworthyPlugin):

    PLUGIN_NAME = 'vpn'
    DJANGO_APP_MODULE = 'noteworthy.vpn'

    def __init__(self):
        pass

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    def run(self, **kwargs):
        raise NotImplementedError(
            f'Method run not implemented for {self.__class__.__name__}')

    def check_health(self, **kargs):
        return 'OK'


Controller = VpnController
