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
        os.system('socat UDP4-RECVFROM:18522,fork UDP4-SENDTO:10.0.0.2:18522,sp=18523,reuseaddr')
    
Controller = LinkController
