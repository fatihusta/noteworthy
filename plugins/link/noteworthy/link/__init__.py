import os
from clicz import cli_method


from noteworthy.notectl.plugins import NoteworthyPlugin


class LinkController(NoteworthyPlugin):

    PLUGIN_NAME = 'link'

    def __init__(self):
        super().__init__(__file__)

    @cli_method
    def start(self):
        '''start link, blocking
        '''
        self.start_dependencies()
        os.system('tail -f /dev/null')
    
Controller = LinkController
