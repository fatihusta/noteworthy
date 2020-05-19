import os
import time

def run_migration():
    PROFILE_PATH = '/opt/noteworthy/profiles'
    profile_dirs = os.listdir(PROFILE_PATH)
    config_dirs = [os.path.join(PROFILE_PATH, d) for d in profile_dirs
                   if d.startswith('.')]
    for dir in config_dirs:
        success_path = os.path.join(dir, 'CONFIGURATION_SUCCESS')
        with open(success_path, 'w') as f:
            f.write(time.asctime())
