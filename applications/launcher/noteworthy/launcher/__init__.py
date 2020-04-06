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

    def install(self, archive_path: str = None, docker_access: bool = False, **kwargs):
        self.sub_parser.add_argument(
             '--archive', help='path of archive to install')
        args = self.sub_parser.parse_known_args(self.args)[0]
        # we use env here to figure out which Dockerfile we should use
        # when building an apps' container; in PROD we want to use the base
        # decentralabs/noteworthy:latest container that the user already has
        # in dev we want to use decentralabs/noteworthy:DEV that we build locally
        # with make .docker
        # TODO figure out if version pinning is needed here
        env = os.environ.get('NOTEWORTHY_ENV', 'prod')
        volumes = []
        if docker_access:
            volumes.append('/var/run/docker.sock:/var/run/docker.sock')
        if archive_path or args.archive:
            if not archive_path:
                archive_path = args.archive
            app, version = os.path.basename(archive_path).split('-')
            version = version.replace('.tar.gz', '')
            app_dir = os.path.join(self.PACKAGE_CACHE, f'{app}/{version}')
            deploy_dir = os.path.join(self.plugin_path, 'deploy')
            Path(self.PACKAGE_CACHE).mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(archive_path, self.PACKAGE_CACHE)
            shutil.copyfile(os.path.join(deploy_dir, 'install.sh'), os.path.join(app_dir, 'install.sh'))
            shutil.copyfile(os.path.join(deploy_dir, f'Dockerfile.{env}'), os.path.join(app_dir, 'Dockerfile'))
            self._build_container(app_dir, app, version)
            self.docker.containers.run(f'noteworthy-{app}:{version}',
            tty=True,
            cap_add=['NET_ADMIN'],
            network='noteworthy',
            stdin_open=True,
            name=f"noteworthy-{app}",
            #auto_remove=True,
            volumes=volumes,
            detach=True)
        else:
            raise NotImplementedError(
                'Installing from repository not supported yet.')
        print('Done.')

    def _build_container(self, app_dir, app, version):
        self.docker.images.build(
            path=app_dir, tag=f'noteworthy-{app}:{version}', nocache=True)


Controller = LauncherController
