from noteworthy.notectl.plugins import NoteworthyPlugin
from grpcz import grpc_controller, grpc_method

@grpc_controller
class SampleAppController(NoteworthyPlugin):

    app_name = 'noteworthy-sample-app'

    def __init__(self):
        pass

    @grpc_method
    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    def run(self, **kwargs):
        raise NotImplementedError(
            f'Method run not implemented for {self.__class__.__name__}')

    @grpc_method
    def check_health(self, **kargs):
        return 'OK'


Controller = SampleAppController
