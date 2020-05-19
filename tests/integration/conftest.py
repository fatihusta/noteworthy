

def pytest_addoption(parser):
    parser.addoption("--hub", action="store")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.hub
    if 'hub' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("hub", [option_value], scope='session')
