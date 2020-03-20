from noteworthy.notectl.plugins import NoteworthyPlugin


class DockerController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-docker'

    def __init__(self):
        pass

Controller = DockerController