import pkg_resources

def load_plugins():
    discovered_plugins = {
        entry_point.name: entry_point.load()
        for entry_point
        in pkg_resources.iter_entry_points('notectl.plugins')
    }
    return discovered_plugins