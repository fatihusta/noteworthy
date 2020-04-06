import tarfile
from noteworthy.notectl.plugins import NoteworthyPlugin


class RiotWebController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-riot-web'

    def __init__(self):
        super().__init__(__file__)

    def start(self, *args, **kwargs):
        with tarfile.open(f'{self.plugin_path}/deploy/web_app.tar.gz') as tar:
            tar.extractall(path='/riot-web')


Controller = RiotWebController
