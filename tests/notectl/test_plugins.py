from noteworthy.notectl.plugins import PluginManager


def test_load_plugins():
    plugins = PluginManager.load_plugins()
    assert 'test_plugin' in plugins
