import os
from grpc_tools import protoc
import yaml
import docker

from noteworthy.notectl.plugins import PluginManager
from noteworthy.notectl.ascii import NOTEWORTHY


class NoteworthyController:

    version_string = '0.0.7'

    def __init__(self):
        self.plugins = PluginManager.load_plugins()
        # The app manifest that determines what "services"
        # are started upon `notecl start`
        # Also used for building launcher installable packages
        self.manifest_path = '/opt/noteworthy/dist/app.yaml'
        self.docker = docker.from_env()

    def list_plugins(self, **kwargs):
        '''
        $ notectl list_plugins
        '''
        print('Installed plugins')
        print('-'*20)
        [ print(f'{k}') for k,v in self.plugins.items() ]
        print()

    def version(self, **kwargs):
        '''
        $ notectl version
        '''
        print(NOTEWORTHY)
        print('by Decentralabs - https://decentralabs.io')
        print()
        print(f'Version: {self.version_string}')

    def launch(self, **kwargs):
        try:
            self.docker.networks.create('noteworthy', check_duplicate=True)
        except:
            pass
        if 'launcher' not in self.plugins:
            raise Exception('Launcher must be installed to run `notectl install`.')
        print('Please wait while Noteworthy launches...')
        self.plugins['launcher'].Controller().launch_launcher(
            '/opt/noteworthy/dist/build/launcher/launcher-DEV.tar.gz',
            hub=kwargs['hub'], domain=kwargs['domain'], hub_host=kwargs['hub_host'])

    def protoc(self, **kwargs):
        '''
        $ notectl protoc <service.proto>
        '''
        '''Generate protobuf Python gRPC
           TODO move to dev-tools plugin
        '''
        cwd = os.getcwd()
        protoc.main([f'-I{cwd}', '--python_out=.', '--grpc_python_out=.', kwargs['action']])

    def _setup_argparse(self, arg_parser):
        command_list = 'list_plugins, '
        plugin_list = ', '.join([plugin for plugin in self.plugins])
        arg_parser.add_argument('command', nargs='?', default='help', help=command_list + plugin_list)
        arg_parser.add_argument('action', nargs='?', default=None)
        arg_parser.add_argument('-d', '--debug', action='store_true', help='enable debugging output')
        arg_parser.add_argument('--hub', action='store_true', help='configure this host as a hub')
        arg_parser.add_argument('--domain', help='domain for your node')
        arg_parser.add_argument('--hub-host', help='ip or hostname of noteworthy hub')


    def get_installed_apps(self):
        '''
        Return the list of installed Django applications wrapped as Noteworthy plugins.
        See http_service for the base Django project.
        '''
        return [ p.Controller.DJANGO_APP_MODULE for name, p in self.plugins.items() if hasattr(p.Controller, 'DJANGO_APP_MODULE')]

    def start(self, **kwargs):
        '''
        This metod (notectl start) is the entrypoint for a Noteworthy application's docker container.
        It consumes the application manifest `app.yaml` and calls `start` on every plugin listed under
        the key `plugins`.
        '''
        try:
            with open(self.manifest_path, 'r') as manifest_file:
                manifest = yaml.safe_load(manifest_file)
        except:
            raise Exception(f'Unable to load {self.manifest_path}')

        for plugin in manifest['plugins']:
            if plugin not in self.plugins:
                raise Exception(f'{self.manifest_path} defines plugin {plugin} that is not installed.')
            try:
                # TODO setup logging
                self.plugins[plugin].Controller().start()
                print(f'Service {plugin} started')
            except NotImplementedError:
                pass

        print('noteworthy finished booting!')
        # TODO tail log file
        os.system('tail -f /dev/null')

    def shell(self, **kwargs):
        os.system('ipython')