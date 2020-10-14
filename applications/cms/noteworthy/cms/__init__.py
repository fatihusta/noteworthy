import os

import docker

from noteworthy.notectl.plugins import NoteworthyPlugin
from clicz import cli_method


class CmsController(NoteworthyPlugin):

    PLUGIN_NAME = 'cms'
    USER_CLI = True

    #TODO Move to NoteworthyPlugin
    @staticmethod
    def get_domain():
        return 'mzoare.noteworthy.im'

    app_name = 'cms'

    def __init__(self):
        self.docker = docker.from_env()

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    def run(self, **kwargs):
        raise NotImplementedError(
            f'Method run not implemented for {self.__class__.__name__}')

    def check_health(self, **kargs):
        return 'OK'

    @cli_method
    def install(self, domain: str, profile: str = 'default'):
        '''install a Noteworthy CMS (Ghost)
        ---
        Args:
            domain: fqdn to deploy app to
            profile: network profile (default)
        '''
        app_env = {
            'NOTEWORTHY_DOMAIN': os.environ['NOTEWORTHY_DOMAIN'],
            'NOTEWORTHY_PROFILE': profile,
            'url': f'http://{domain}'
            }

        app = 'cms-ghost'
        dashed_domain = os.environ['NOTEWORTHY_DOMAIN'].replace('.', '-')
        volumes = []
        app_name = f'{dashed_domain}-{app}'
        app_container_name = f"noteworthy-{app_name}-{profile}"
        profile_volume = self._create_profile_volume(app_name, profile)
        volumes.append(f'{profile_volume.name}:/var/lib/ghost/content')
        print('Installing Noteworthy CMS...')
        self.docker.containers.run(f"ghost:3",
        tty=True,
        network='noteworthy',
        stdin_open=True,
        name=app_container_name,
        #auto_remove=True,
        volumes=volumes,
        detach=True,
        environment=app_env,
        restart_policy={"Name": "always"})
        print('Done.')

    def _create_profile_volume(self, app, profile_name):
        profile_volume_name = f'noteworthy-{app}-{profile_name}-vol'
        volume = self.docker.volumes.create(name=profile_volume_name)
        return volume

Controller = CmsController
