from noteworthy.wireguard import Controller as WireGuardController


def test_can_import():
    wgc = WireGuardController()
    wgc.build()