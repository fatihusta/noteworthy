import tarfile
from noteworthy.notectl.plugins import NoteworthyPlugin


class RiotWebController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-riot-web'

    def __init__(self):
        pass

    def run(self, **kwargs):
        tar = tarfile.open('/opt/noteworthy/dist/web_app.tar.gz')
        tar.extractall(path='/riot-app')


Controller = RiotWebController
