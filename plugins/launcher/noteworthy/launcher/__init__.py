from noteworthy.notectl.plugins import NoteworthyPlugin


class LauncherController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-launcher'

    def __init__(self):
        pass


Controller = LauncherController
