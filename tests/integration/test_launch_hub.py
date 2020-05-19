import time
import pytest
import subprocess
import os


@pytest.fixture(scope='module')
def launch_hub(hub):
    os.system('docker volume rm noteworthy-launcher-hub-integration-vol')
    os.system('docker rm -f noteworthy-launcher-hub-integration')
    os.system(f'notectl launcher launch_hub {hub} --profile integration')
    time.sleep(5)
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


def test_launch_hub(launch_hub, launch_taproot):
    subprocess.check_output(['docker', 'exec', 'noteworthy-integration-noteworthy-im-launcher-integration', 'ping', '-c', '5', '-W', '1', '10.0.0.1'])