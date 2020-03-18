import pytest

from noteworthy.notectl.__main__ import main

def test_main_no_arguments_shows_help(capsys):
    with pytest.raises(SystemExit) as pytest_exception:
        main()
    assert pytest_exception.type == SystemExit
    assert pytest_exception.value.code == 1

    captured = capsys.readouterr()
    assert 'usage: ' in captured.out