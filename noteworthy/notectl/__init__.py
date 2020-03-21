from noteworthy.notectl.plugins import PluginManager

from noteworthy.notectl.ascii import NOTEWORTHY

class NoteworthyController:

    version_string = '0.0.2'

    def __init__(self):
        self.plugins = PluginManager.load_plugins()

    def list_plugins(self, **kwargs):
        print('Installed plugins')
        print('-'*20)
        [ print(f'{k}') for k,v in self.plugins.items() ]
        print()

    def version(self, **kwargs):
        print(NOTEWORTHY)
        print('by Decentralabs - https://decentralabs.io')
        print()
        print(f'Version: {self.version_string}')

    def setup_argparse(self, arg_parser):
        command_list = 'list_plugins, '
        plugin_list = ', '.join([plugin for plugin in self.plugins])
        arg_parser.add_argument('command', nargs='?', default='help', help=command_list + plugin_list)
        arg_parser.add_argument('action', nargs='?', default=None)
        arg_parser.add_argument('-d', '--debug', action='store_true', help='enable debugging output')

