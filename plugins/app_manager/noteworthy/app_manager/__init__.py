from noteworthy.notectl.plugins import NoteworthyPlugin


class AppManagerController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-app-manager'

    def __init__(self):
        pass


Controller = AppManagerController
