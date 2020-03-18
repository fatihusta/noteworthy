import pkg_resources

class PluginManager:
    plugin_namespace = 'notectl.plugins'

    def __init__(self):
        self._load_plugins()

    def _load_plugins(self):
        self.plugins = {
            entry_point.name: entry_point.load()
            for entry_point
            in pkg_resources.iter_entry_points(PluginManager.plugin_namespace)
        }

    def list_plugins(self):
        print('Installed plugins')
        print('-'*20)
        [ print(f'{k}\t{v}') for k,v in self.plugins.items() ]
        print()