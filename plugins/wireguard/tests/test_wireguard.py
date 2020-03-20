from noteworthy.wireguard import Controller as WireGuardController

class MockArgsNamespace:
    command = 'wireguard'
    action = 'init'
    no_cache = False

def test_can_import():
    c = WireGuardController()
    c.init(MockArgsNamespace)