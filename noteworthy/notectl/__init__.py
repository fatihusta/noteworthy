import os
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
            hub=kwargs['hub'], domain=kwargs['domain'],
            hub_host=kwargs['hub_host'], auth_code=kwargs['auth_code'],
            profile=kwargs['profile'])

    def protoc(self, **kwargs):
        '''
        $ notectl protoc <service.proto>
        '''
        '''Generate protobuf Python gRPC
           TODO move to dev-tools plugin
        '''
        from grpc_tools import protoc
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
        arg_parser.add_argument('--auth-code', help='reservation key to auth with your host')
        arg_parser.add_argument('--profile', help='profile under which to launch apps and use persistent configs')


    def get_installed_apps(self):
        '''
        Return the list of installed Django applications wrapped as Noteworthy plugins.
        See http_service for the base Django project.
        '''
        return [ p.Controller.DJANGO_APP_MODULE for name, p in self.plugins.items() if hasattr(p.Controller, 'DJANGO_APP_MODULE')]

    def shell(self, **kwargs):
        os.system('ipython')
