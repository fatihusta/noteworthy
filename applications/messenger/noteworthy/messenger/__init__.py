import os
import shutil
from pathlib import Path

import docker

from noteworthy.notectl.plugins import NoteworthyPlugin


class MessengerController(NoteworthyPlugin):

    PLUGIN_NAME = 'messenger'

    PACKAGE_CACHE = '/var/noteworthy/cache/packages'

    def __init__(self):
        super().__init__(__file__)
        self.args = None
        self.docker = docker.from_env()

    def start(self, **kwargs):
        pass


Controller = MessengerController
