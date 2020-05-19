import os
import time
from pathlib import Path

def run_migration():
    PROFILE_PATH = '/opt/noteworthy/profiles'
    profile_dirs = os.listdir(PROFILE_PATH)
    config_dirs = [os.path.join(PROFILE_PATH, d) for d in profile_dirs
                   if d.startswith('.')]
    for dir in config_dirs:
        success_path = os.path.join(dir, 'CONFIGURATION_SUCCESS')
        with open(success_path, 'w') as f:
            f.write(time.asctime())
    # migrate hub links
    HUB_DIR = '/opt/noteworthy/profiles/.noteworthy-hub'
    if HUB_DIR in config_dirs:
        links_dir = os.path.join(HUB_DIR, 'links')
        Path(links_dir).mkdir(exist_ok=True, parents=True)
        os.chdir(HUB_DIR)
        os.system('ls | grep .yaml | xargs -i mv {} ./links')
