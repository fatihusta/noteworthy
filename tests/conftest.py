import os
import time
import subprocess
import pytest


def pytest_addoption(parser):
    parser.addoption("--hub", action="store", default="192.168.1.203")

def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.hub
    if 'hub' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("hub", [option_value], scope='session')

@pytest.fixture(scope='module')
def launch_hub(hub):
    os.system('docker volume rm noteworthy-launcher-hub-integration-vol')
    os.system('docker rm -f noteworthy-launcher-hub-integration')
    os.system(f'notectl launcher launch_hub {hub} --profile integration')
    # TODO poll for ready state via healthcheck
    time.sleep(10)
    yield
    os.system('docker rm -f noteworthy-launcher-hub-integration')
    os.system('docker volume rm noteworthy-launcher-hub-integration-vol')

@pytest.fixture(scope='module')
def invite_code():
    return subprocess.check_output(['docker', 'exec', 'noteworthy-launcher-hub-integration', 'notectl', 'invite', 'integrationuser']).decode().split(':')[1].strip()

@pytest.fixture(scope='module')
def launch_taproot(invite_code, hub):
    os.system(f'notectl install --profile integration --domain integration.noteworthy.im --invite-code {invite_code} --hub {hub} --accept-tos --no-install-messenger')
    yield
    os.system('docker rm -f noteworthy-integration-noteworthy-im-launcher-integration')
    os.system('docker volume rm noteworthy-integration-noteworthy-im-launcher-integration-vol')

