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


    def _reload(self, **kwargs):
        os.system('nginx -s reload')

    def serve_domain(self, domain, config, get_certs=True):
        if get_certs:
            cert_info = self._cerbot(domain)
        self._write_config(domain, config, cert_info)
        self._reload()

Controller = NginxController
