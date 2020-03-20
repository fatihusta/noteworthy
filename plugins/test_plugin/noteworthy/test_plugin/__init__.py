from noteworthy.notectl.plugins import NoteworthyPlugin


class TestPluginController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-test-plugin'

    def __init__(self):
        pass


Controller = TestPluginController