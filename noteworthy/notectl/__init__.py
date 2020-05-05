import os
import random
import yaml
import docker

from noteworthy.notectl.plugins import PluginManager
from noteworthy.notectl.ascii import NOTEWORTHY
from clicz import cli_method, Color

class NoteworthyController:
    '''manage your Noteworthy deployments
    '''
    descriptions = ['Technology worth writing home about.',
                    'Next generation communication platforms for the people.',
                    'Empowering the development of a safe, free web.',
                    'Your network, your data.',
                    'Take ownership of your digital existence.']

    PLUGIN_NAME = 'system'
    version_string = '0.0.7'

    def __init__(self):
        self.plugins = PluginManager.load_plugins()
        # The app manifest that determines what "services"
        # are started upon `notecl start`
        # Also used for building launcher installable packages
        self.docker = docker.from_env()

    @cli_method 
    def list_plugins(self):
        '''
        list installed plugins
        '''
        print('Installed plugins')
        print('-'*20)
        [ print(f'{k}') for k,v in self.plugins.items() ]
        print()
    list_plugins.clicz_aliases = ['plugins']

    @cli_method
    def version(self):
        '''print Noteworthy version
        '''
        print(NOTEWORTHY)
        print('by Decentralabs - https://decentralabs.io')
        print()
        print(f'Version: {self.version_string}')
    version.clicz_aliases = ['version']

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

    def get_installed_apps(self):
        '''
        Return the list of installed Django applications wrapped as Noteworthy plugins.
        See http_service for the base Django project.
        '''
        return [ p.Controller.DJANGO_APP_MODULE for name, p in self.plugins.items() if hasattr(p.Controller, 'DJANGO_APP_MODULE')]


def clicz_entrypoint(clicz):
    notectl_env = os.environ.get('NOTECTL_ENV', 'USER')
    clicz.register_controller(NoteworthyController)
    for _, plugin_module in PluginManager.load_plugins().items():
        if notectl_env == 'SYSTEM':
            clicz.register_controller(plugin_module.Controller)
        else:
            if hasattr(plugin_module.Controller, 'USER_CLI') and plugin_module.Controller.USER_CLI:
                clicz.register_controller(plugin_module.Controller)

    # Return a colorful cli description
    color = Color()
    description = random.choice(NoteworthyController.descriptions)
    return f"{color.yellow('Noteworthy')}: {color.green(description)}"