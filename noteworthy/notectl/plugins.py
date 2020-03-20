import pkg_resources

class PluginManager:
    plugin_namespace = 'notectl.plugins'

    @staticmethod
    def load_plugins():
        plugins = {
            entry_point.name: entry_point.load()
            for entry_point
            in pkg_resources.iter_entry_points(PluginManager.plugin_namespace)
        }

        return plugins


class NoteworthyPlugin:

    @classmethod
    def setup_argparse(cls, arg_parser):
        cls.arg_parser = arg_parser

    def help(self, **kwargs):
        print('''Help is not available for this plugin.''')