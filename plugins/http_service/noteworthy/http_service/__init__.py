import argparse
import os
from noteworthy.notectl.plugins import NoteworthyPlugin


class HttpServiceController(NoteworthyPlugin):

    PLUGIN_NAME = 'http_service'

    def __init__(self):
        super().__init__(__file__)

    def run(self, *args, **kwargs):
        os.chdir(os.path.join(self.plugin_path, 'rest_api'))
        if self.is_first_run:
            self.create_config_dir()
            os.system('python manage.py migrate')
        os.system('python manage.py runserver 0.0.0.0:8001')

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl http_service')
        cls.sub_parser.add_argument('argument', nargs='*', help='hostname of hub to join')

Controller = HttpServiceController
