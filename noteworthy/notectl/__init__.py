import os
from grpc_tools import protoc

from noteworthy.notectl.plugins import PluginManager
from noteworthy.notectl.ascii import NOTEWORTHY


class NoteworthyController:

    version_string = '0.0.2'

    def __init__(self):
        self.plugins = PluginManager.load_plugins()

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


    def get_installed_apps(self):
        return [ p.Controller.DJANGO_APP_MODULE for name, p in self.plugins.items() if hasattr(p.Controller, 'DJANGO_APP_MODULE')]
