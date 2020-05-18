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
        if self.is_first_run:
            self.commit_successful_config()

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    @cli_method
    def shell(self, **kwargs):
        '''start python shell with django already setup
        '''
        os.chdir(os.path.join(self.plugin_path, 'rest_api'))
        os.system('python manage.py shell')

Controller = HttpServiceController
