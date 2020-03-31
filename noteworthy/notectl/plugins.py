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

    @classmethod
    def _setup_argparse(cls, arg_parser):
        cls.arg_parser = arg_parser

    def help(self, **kwargs):
        print('''Help is not available for this plugin.''')