from noteworthy.notectl.plugins import NoteworthyPlugin


class RiotWebController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-riot-web'

    def __init__(self):
        pass


Controller = RiotWebController
