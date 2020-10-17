import os
import time
from pathlib import Path

'''
This migrations fixes: https://github.com/decentralabs/noteworthy/issues/17

The fix forces the hub to use link container names instead of IPs in its nginx configuration.
In order to migrate old links to the new system, we update cached SNI backends and sites-enabled records.
'''

def run_migration():
    PROFILE_PATH = '/opt/noteworthy/profiles'
    profile_dirs = os.listdir(PROFILE_PATH)
    config_dirs = [os.path.join(PROFILE_PATH, d) for d in profile_dirs
                   if d.startswith('.')]
    # migrate nginx records for hubs
    NGINX_DIR = '/opt/noteworthy/profiles/.nginx'
    HUB_DIR = '/opt/noteworthy/profiles/.noteworthy-hub'
    if (NGINX_DIR in config_dirs) and (HUB_DIR in config_dirs):
        from noteworthy.nginx import NginxController
        nc = NginxController()
        backends = nc.get_link_set().get('backends')
        for backend in backends:
            if backend['name'].startswith('link'):
                nc.store_link(backend['name'], backend['domain'], backend['name'])
                nc.set_http_proxy_pass(backend['name'], backend['domain'], backend['name'], reload = False)
        bk = nc.get_link_set()
        nc.write_config(bk)
