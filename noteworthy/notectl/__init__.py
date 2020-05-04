import argparse
import os
import yaml
import docker

from noteworthy.notectl.plugins import PluginManager
from noteworthy.notectl.ascii import NOTEWORTHY
from clicz import cli_method

class NoteworthyController:
    '''manage Noteworthy deployments
    '''

    PLUGIN_NAME = 'noteworthy'
    version_string = '0.0.7'

    def __init__(self):
        self.plugins = PluginManager.load_plugins()
        # The app manifest that determines what "services"
        # are started upon `notecl start`
        # Also used for building launcher installable packages
        self.docker = docker.from_env()
        self.arg_parser = argparse.ArgumentParser()

    @cli_method 
    def list_plugins(self):
        '''
        List installed plugins
        '''
        print('Installed plugins')
        print('-'*20)
        [ print(f'{k}') for k,v in self.plugins.items() ]
        print()
    list_plugins.clicz_aliases = ['plugins']

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
        self.arg_parser = arg_parser
        command_list = 'list_plugins, '
        plugin_list = ', '.join([plugin for plugin in self.plugins])


    def get_installed_apps(self):
        '''
        Return the list of installed Django applications wrapped as Noteworthy plugins.
        See http_service for the base Django project.
        '''
        return [ p.Controller.DJANGO_APP_MODULE for name, p in self.plugins.items() if hasattr(p.Controller, 'DJANGO_APP_MODULE')]

    def shell(self, **kwargs):
        os.system('ipython')

    @cli_method
    def install(self, app:str):
        '''install a Noteworthy application
        ---
        Args:
            app: the application to install
        '''

        print(f'I will install {app}')

    install.clicz_aliases = ['install', 'i']


def clicz_entrypoint(clicz):
    clicz.register_controller(NoteworthyController)
    for _, plugin_module in PluginManager.load_plugins().items():
        clicz.register_controller(plugin_module.Controller)