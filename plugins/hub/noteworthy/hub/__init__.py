from noteworthy.notectl.plugins import NoteworthyPlugin


class HubController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-hub'
    DJANGO_APP_MODULE = 'noteworthy.hub.api'

    def __init__(self):
        pass


Controller = HubController
