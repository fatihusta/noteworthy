import os
import argparse
import pkg_resources
from pathlib import Path

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
        self.plugin_path = self.get_plugin_path(file)
        self.sub_parser = argparse.ArgumentParser()
        self.config_dir = os.path.join(
            self.base_config_dir, f'.{self.PLUGIN_NAME}')
        self.deploy_dir = os.path.join(self.plugin_path, 'deploy/')

    def create_config_dir(self):
        Path(self.config_dir).mkdir(exist_ok=True)

    @classmethod
    def _setup_argparse(cls, arg_parser):
        cls.arg_parser = arg_parser
        cls.sub_parser = argparse.ArgumentParser()

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
        return not os.path.exists(self.config_dir)

    @staticmethod
    def get_plugin_path(file):
        return os.path.dirname(os.path.realpath(file))
