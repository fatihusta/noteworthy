from noteworthy.notectl.plugins import NoteworthyPlugin


class HttpServiceController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-http-service'

    def __init__(self):
        pass


Controller = HttpServiceController
