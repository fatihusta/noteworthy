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
        self.sub_parser.add_argument('--archive', help='path of archive to install')
        args = self.sub_parser.parse_known_args(self.args)[0]
        if args.archive:
            self.app, self.version = os.path.basename(args.archive).split('-')
            self.version = self.version.replace('.tar.gz', '')
            self.app_dir = os.path.join(self.PACKAGE_CACHE, f'{self.app}/{self.version}')
            self.deploy_dir = os.path.join(self.plugin_path, 'deploy')
            Path(self.PACKAGE_CACHE).mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(args.archive, self.PACKAGE_CACHE)
            for file in ['Dockerfile', 'install.sh', 'app.yaml']:
                shutil.copyfile(os.path.join(self.deploy_dir, file), os.path.join(self.app_dir, file))
            self.build_container()
        else:
            raise NotImplementedError('Installing from repository not supported yet.')
        print('Done.')

    def build_container(self, **kwargs):
        self.docker.images.build(path=self.app_dir, tag=f'noteworthy-{self.app}:{self.version}')


Controller = LauncherController
