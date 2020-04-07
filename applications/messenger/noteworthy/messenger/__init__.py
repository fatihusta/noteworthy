from noteworthy.notectl.plugins import NoteworthyPlugin


class MessengerController(NoteworthyPlugin):

    PLUGIN_NAME = 'messenger'

    def __init__(self):
        super().__init__(__file__)

    def run(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        self._start(self.PLUGIN_NAME)


Controller = MessengerController
