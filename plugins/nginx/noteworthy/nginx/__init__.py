import os

from noteworthy.notectl.plugins import NoteworthyPlugin


class NginxController(NoteworthyPlugin):

    PLUGIN_NAME = 'nginx'

    def __init__(self):
        pass

    def run(self, **kwargs):
        os.system("nginx -g 'daemon off;'")

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

Controller = NginxController
