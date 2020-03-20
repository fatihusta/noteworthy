from noteworthy.notectl import NoteworthyController


def test_noteworthy_controller():
    nc = NoteworthyController()

def test_show_plugins(capsys):
    nc = NoteworthyController()
    nc.list_plugins()
    captured = capsys.readouterr()
    assert 'Installed plugins' in captured.out