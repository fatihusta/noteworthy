import os
import pkg_resources
from pathlib import Path
import yaml
import time
import shutil

class PluginManager:

    @staticmethod
    def load_plugins(plugin_namespace='notectl.plugins'):
        plugins = {
            entry_point.name: entry_point.load()
            for entry_point
            in pkg_resources.iter_entry_points(plugin_namespace)
        }

        return plugins


class NoteworthyPlugin:

    base_config_dir = '/opt/noteworthy/profiles'

    def __init__(self, file=__file__):
        self.plugins = PluginManager.load_plugins()
        self.plugin_path = self.get_plugin_path(file)
        self.config_dir = os.path.join(
            self.base_config_dir, f'.{self.PLUGIN_NAME}')
        self.configuration_success_file = os.path.join(self.config_dir,
                                                       'CONFIGURATION_SUCCESS')
        self.deploy_dir = os.path.join(self.plugin_path, 'deploy/')
        self.service_manifest = os.path.join(self.plugin_path, 'service.yaml')

    def create_config_dir(self, clean=True):
        if clean:
            shutil.rmtree(self.config_dir)
        Path(self.config_dir).mkdir(exist_ok=True)

    def commit_successful_config(self):
        with open(self.configuration_success_file, 'w') as f:
            f.write(time.asctime())

    def help(self, **kwargs):
        print('''Help is not available for this plugin.''')

    def start(self, **kwargs):
        raise NotImplementedError(f'Method start not implemented for {self.__class__.__name__}')

    def run(self, **kwargs):
        raise NotImplementedError(f'Method run not implemented for {self.__class__.__name__}')

    def _start(self, plugin):
        os.system(f'notectl {plugin} run&')

    @property
    def is_first_run(self):
        return not os.path.isfile(self.configuration_success_file)

    @staticmethod
    def get_plugin_path(file):
        return os.path.dirname(os.path.realpath(file))


    def get_plugin(self, plugin_name):
        return self.plugins[plugin_name]

    def start_dependencies(self):
        try:
            with open(self.service_manifest, 'r') as manifest_file:
                manifest = yaml.safe_load(manifest_file)
        except yaml.scanner.ScannerError:
            raise Exception(f'Unable to load {self.service_manifest}')

        def _start_dependencies(key):
            for plugin in manifest['plugins'][key]:
                if plugin not in self.plugins:
                    raise Exception(f'{self.service_manifest} defines plugin {plugin} that is not installed.')
                try:
                    # TODO setup logging
                    self.plugins[plugin].Controller().start()
                    print(f'Service {plugin} started')
                except NotImplementedError:
                    pass

        _start_dependencies('shared')
        role = os.environ.get('NOTEWORTHY_ROLE')
        if role:
            _start_dependencies(role)
