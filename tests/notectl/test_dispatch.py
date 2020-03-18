from noteworthy.notectl.dispatch import NoteworthyController


def test_noteworthy_controller():
    nc = NoteworthyController()
    nc.dispatch('version')