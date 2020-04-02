from noteworthy.notectl.plugins import NoteworthyPlugin


class AppRegistryController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-app-registry'

    def __init__(self):
        pass


Controller = AppRegistryController
