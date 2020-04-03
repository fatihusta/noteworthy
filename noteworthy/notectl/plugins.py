import os
import argparse
import pkg_resources

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

    def __init__(self, file=__file__):
        self.plugin_path = self.get_plugin_path(file)

    @classmethod
    def _setup_argparse(cls, arg_parser):
        cls.arg_parser = arg_parser

    def help(self, **kwargs):
        print('''Help is not available for this plugin.''')

    def start(self, **kwargs):
        raise NotImplementedError(f'Method start not implemented for {self.__class__.__name__}')

    def run(self, **kwargs):
        raise NotImplementedError(f'Method run not implemented for {self.__class__.__name__}')

    def _start(self, plugin):
        os.system(f'notectl {plugin} run&')

    @staticmethod
    def get_plugin_path(file):
        return os.path.dirname(os.path.realpath(file))
