from noteworthy.notectl.dispatch import NoteworthyController

class MockArgNamespace:
    command = 'version'
    action = None


def test_noteworthy_controller():
    nc = NoteworthyController()
    nc.dispatch(MockArgNamespace)