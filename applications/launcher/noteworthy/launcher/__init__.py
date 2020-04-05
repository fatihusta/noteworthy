import os
import shutil
from pathlib import Path

import docker

from noteworthy.notectl.plugins import NoteworthyPlugin


class LauncherController(NoteworthyPlugin):

    PLUGIN_NAME = 'launcher'

    PACKAGE_CACHE = '/var/noteworthy/cache/packages'

    def __init__(self):
        super().__init__(__file__)
        self.args = None
        self.docker = docker.from_env()

    def install(self, **kwargs):
        self.sub_parser.add_argument(
            '--archive', help='path of archive to install')
        args = self.sub_parser.parse_known_args(self.args)[0]
        if args.archive:
            app, version = os.path.basename(args.archive).split('-')
            version = version.replace('.tar.gz', '')
            app_dir = os.path.join(self.PACKAGE_CACHE, f'{app}/{version}')
            deploy_dir = os.path.join(self.plugin_path, 'deploy')
            Path(self.PACKAGE_CACHE).mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(args.archive, self.PACKAGE_CACHE)
            for file in ['Dockerfile', 'install.sh']:
                shutil.copyfile(os.path.join(deploy_dir, file), os.path.join(app_dir, file))
            self._build_container(app_dir, app, version)
            self.docker.containers.run(f'noteworthy-{app}:{version}',
            tty=True,
            cap_add=['NET_ADMIN'],
            network='noteworthy',
            stdin_open=True,
            name=f"noteworthy-{app}",
            #auto_remove=True,
            #volumes=['/opt/noteworthy/noteworth-wireguard/hub:/opt/noteworthy/noteworthy-wireguard/hub'],
            detach=True)
        else:
            raise NotImplementedError(
                'Installing from repository not supported yet.')
        print('Done.')

    def _build_container(self, app_dir, app, version):
        self.docker.images.build(
            path=app_dir, tag=f'noteworthy-{app}:{version}', nocache=True)


Controller = LauncherController
