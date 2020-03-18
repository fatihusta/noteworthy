from noteworthy.notectl.plugins import PluginManager

def test_load_plugins():
    pm = PluginManager()
    assert 'test_plugin' in pm.plugins

def test_show_plugins(capsys):
    pm = PluginManager()
    pm.list_plugins()
    captured = capsys.readouterr()
    assert 'Installed plugins' in captured.out