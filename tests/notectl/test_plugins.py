from noteworthy.notectl import plugins

def test_load_plugins():
    loaded_plugins = plugins.load_plugins()
    assert 'test_plugin' in loaded_plugins