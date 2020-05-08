import os

from unittest import mock

import pytest

from noteworthy.nginx import NginxController

@pytest.fixture
def nc(tmpdir):
    nc = NginxController(tmpdir.strpath)
    return nc

def test_nginx_templates_and_paths(nc):
    assert os.path.exists(nc.nginx_gateway_template)
    assert os.path.exists(nc.nginx_app_template)
    assert nc.nginx_config_path == '/etc/nginx/nginx.conf'
    assert nc.nginx_sites_enabled == '/etc/nginx/sites-enabled'
    assert nc.letsencrypt_dir == '/etc/letsencrypt'
    assert nc.sites_dir == os.path.join(nc.config_dir, 'sites') 
    assert nc.tls_backend_dir == os.path.join(nc.config_dir, 'backends')
    assert nc.letsencrypt_bk == os.path.join(nc.config_dir, 'letsencrypt')
    
@mock.patch('os.system')
def test_nginx_run(os_system, nc):
    nc.run()
    os_system.assert_called_once_with("nginx -g 'daemon off;'")