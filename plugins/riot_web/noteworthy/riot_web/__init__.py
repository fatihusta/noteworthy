import tarfile
import os
from noteworthy.notectl.plugins import NoteworthyPlugin


class RiotWebController(NoteworthyPlugin):

    PLUGIN_NAME = 'riot_web'

    def __init__(self):
        super().__init__(__file__)

    def start(self, *args, **kwargs):
        if self.is_first_run:
            tar_path = os.path.join(self.deploy_dir, 'web_app.tar.gz')
            with tarfile.open(tar_path) as tar:
                self.create_config_dir()
                tar.extractall(path=self.config_dir)


Controller = RiotWebController
