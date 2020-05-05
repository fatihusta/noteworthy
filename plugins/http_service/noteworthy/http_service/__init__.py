import argparse
import os

from clicz import cli_method
from noteworthy.notectl.plugins import NoteworthyPlugin


class HttpServiceController(NoteworthyPlugin):
    '''Django powered http server
    '''

    PLUGIN_NAME = 'http_service'

    def __init__(self):
        super().__init__(__file__)

    @cli_method
    def run(self):
        '''start http_service, blocking
        '''
        os.chdir(os.path.join(self.plugin_path, 'rest_api'))
        if self.is_first_run:
            self.create_config_dir()
        os.system('python manage.py migrate')
        os.system('python manage.py runserver 0.0.0.0:8001')

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    def shell(self, **kwargs):
        os.chdir(os.path.join(self.plugin_path, 'rest_api'))
        os.system('python manage.py shell')

Controller = HttpServiceController
