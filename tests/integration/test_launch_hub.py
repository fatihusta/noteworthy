import time
import pytest
import subprocess
import os


@pytest.mark.integration
def test_launch_hub(launch_hub, launch_taproot):
    subprocess.check_output(['docker', 'exec', 'noteworthy-integration-noteworthy-im-launcher-integration', 'ping', '-c', '5', '-W', '1', '10.0.0.1'])