import argparse
import os
import shutil
from pathlib import Path

import docker
import dockerpty
from jinja2 import Template

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.hub import HubController


class LauncherController(NoteworthyPlugin):

    PLUGIN_NAME = 'launcher'

    PACKAGE_CACHE = '/var/noteworthy/cache/packages'

    def __init__(self):
        super().__init__(__file__)
        self.args = None
        self.docker = docker.from_env()
        self.hub_hostname = os.environ.get('NOTEWORTHY_HUB', 'noteworthy.im:8000')

    # TODO move this code to a lib; its duplicated here and in riot-web plugin
    def _generate_file_from_template(self, tmpl_path, target, configs):
        with open(tmpl_path, 'r') as f:
            tmpl = Template(f.read())
        rendered = tmpl.render(configs)
        with open(target, 'w') as f:
            f.write(rendered)

    def install(self, archive_path: str = None, **kwargs):
        # we use env here to figure out which Dockerfile we should use
        # when building an apps' container; in PROD we want to use the base
        # decentralabs/noteworthy:latest container that the user has already downloaded
        # in dev we want to use decentralabs/noteworthy:DEV that we build locally
        # with make .docker
        # TODO figure out if version pinning is needed here
        profile = kwargs.get('profile') or os.environ['NOTEWORTHY_PROFILE']
        app_env = {
            'NOTEWORTHY_DOMAIN': os.environ['NOTEWORTHY_DOMAIN'],
            'NOTEWORTHY_PROFILE': profile}
        dashed_domain = os.environ['NOTEWORTHY_DOMAIN'].replace('.', '-')
        volumes = []
        if archive_path or self.args.archive:
            if not archive_path:
                archive_path = self.args.archive
            app, version = os.path.basename(archive_path).split('-')
            version = version.replace('.tar.gz', '')
            app_dir = os.path.join(self.PACKAGE_CACHE, f'{app}/{version}')
            Path(self.PACKAGE_CACHE).mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(archive_path, self.PACKAGE_CACHE)
            shutil.copyfile(os.path.join(self.deploy_dir, 'install.sh'), os.path.join(app_dir, 'install.sh'))
            shutil.copyfile(os.path.join(self.deploy_dir, f'Dockerfile'), os.path.join(app_dir, 'Dockerfile'))
            self._build_container(app_dir, app, version)
            app_name = f'{dashed_domain}-{app}'
            app_container_name = f"noteworthy-{app_name}-{profile}"
            profile_volume = self._create_profile_volume(app_name, profile)
            volumes.append(f'{profile_volume.name}:/opt/noteworthy/profiles')
            self.docker.containers.run(f'noteworthy-{app}:{version}',
            tty=True,
            cap_add=['NET_ADMIN'],
            network='noteworthy',
            stdin_open=True,
            name=app_container_name,
            #auto_remove=True,
            volumes=volumes,
            detach=True,
            environment=app_env,
            restart_policy={"Name": "always"})
            # setup app's nginx config
            from noteworthy.nginx import NginxController
            nc = NginxController()
            try:
                nc.set_http_proxy_pass(app, os.environ['NOTEWORTHY_DOMAIN'], app_container_name,
                    os.path.join(self.PACKAGE_CACHE,
                        f'{app}/{version}/{app}/noteworthy/{app}/deploy/nginx.conf'))
            except:
                print(f'No nginx config found for app {app}')

        else:
            raise NotImplementedError(
                'Installing from repository not supported yet.')
        print('Done.')

    def launch_launcher(self, archive_path: str = None, hub: bool = False,
            domain: str = '', hub_host: str = 'hub01.noteworthy.im',
            auth_code: str = '', profile: str = 'default', **kwargs):
        profile = profile or 'default'
        volumes = []
        ports = {}
        app_env = {
                'NOTEWORTHY_HUB': hub_host,
                'NOTEWORTHY_PROFILE': profile
        }
        volumes.append('/var/run/docker.sock:/var/run/docker.sock')
        volumes.append('/usr/local/bin/docker:/usr/local/bin/docker')
        if archive_path or self.args.archive:
            if not archive_path:
                archive_path = self.args.archive
            app, version = os.path.basename(archive_path).split('-')
            app_name = app
            if hub:
                app_name = app + '-hub'
                ports={
                        '80/tcp' : 80,
                        '443/tcp': 443,
                        '8000/tcp': 8000,
                      }
                app_env['NOTEWORTHY_ROLE'] = 'hub'
            else:
                dash_domain = domain.replace('.', '-')
                app_name = f'{dash_domain}-{app}'
                app_env['NOTEWORTHY_DOMAIN'] = domain
                app_env['NOTEWORTHY_ROLE'] = 'taproot'
                app_env['NOTEWORTHY_AUTH_CODE'] = auth_code
                if not domain:
                    raise Exception('Must specify --domain argument')
            #provision link
            version = version.replace('.tar.gz', '')
            app_dir = os.path.join(self.PACKAGE_CACHE, f'{app}/{version}')
            deploy_dir = os.path.join(self.plugin_path, 'deploy')
            Path(self.PACKAGE_CACHE).mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(archive_path, self.PACKAGE_CACHE)
            shutil.copyfile(os.path.join(deploy_dir, 'install.sh'), os.path.join(app_dir, 'install.sh'))
            shutil.copyfile(os.path.join(deploy_dir, 'Dockerfile'), os.path.join(app_dir, 'Dockerfile'))
            self._build_container(app_dir, app, version)

            # create and add profiles volume
            profile_volume = self._create_profile_volume(app_name, profile)
            volumes.append(f'{profile_volume.name}:/opt/noteworthy/profiles')

            # deploy launcher / launcher-hub
            self.docker.containers.run(f'noteworthy-{app}:{version}',
            tty=True,
            cap_add=['NET_ADMIN'],
            network='noteworthy',
            stdin_open=True,
            name=f"noteworthy-{app_name}-{profile}",
            #auto_remove=True,
            volumes=volumes,
            ports=ports,
            detach=True,
            environment=app_env,
            restart_policy={"Name": "always"})

        else:
            raise NotImplementedError(
                'Installing from repository not supported yet.')
        print('Done.')

    def _build_container(self, app_dir, app, version):
        # read release tag from /opt/noteworthy/release
        with open('/opt/noteworthy/release', 'r') as tag_file:
            release_tag = tag_file.read().strip()
        self.docker.images.build(
            path=app_dir, tag=f'noteworthy-{app}:{version}', nocache=True, buildargs={'RELEASE_TAG': release_tag})

    def _create_profile_volume(self, app, profile_name):
        profile_volume_name = f'noteworthy-{app}-{profile_name}-vol'
        volume = self.docker.volumes.create(name=profile_volume_name)
        return volume

    def start(self, **kwargs):
        if os.environ['NOTEWORTHY_ROLE'] == 'taproot':
            if self.is_first_run:
                self.create_config_dir()
                # write out .well-known/matrix/server so matrix federation works
                well_know_target = '/var/www/html/.well-known/matrix/'
                Path(well_know_target).mkdir(parents=True, exist_ok=True)
                self._generate_file_from_template(os.path.join(self.deploy_dir, 'server'),
                    os.path.join(well_know_target, 'server'),
                    {'domain': os.environ['NOTEWORTHY_DOMAIN']})

                # TODO dont install automatically
                os.system('notectl package package messenger')
                self.install('/opt/noteworthy/dist/build/messenger/messenger-DEV.tar.gz')

    def create_user(self, **kwargs):
        # use docker proxy for invoking shell commands
        # via the docker exec
        dashed_domain = os.environ['NOTEWORTHY_DOMAIN'].replace('.', '-')
        profile = kwargs.get('profile') or os.environ['NOTEWORTHY_PROFILE']
        c = self.docker.containers.list(filters={'name':f'noteworthy-{dashed_domain}-messenger-{profile}'})[0]
        dockerpty.exec_command(self.docker.api, c.id, 'register_new_matrix_user -c /opt/noteworthy/.messenger/homeserver.yaml http://localhost:8008')

    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
        usage='notectl launcher')
        cls.sub_parser.add_argument(
             '--archive', help='path of archive to install')

Controller = LauncherController
