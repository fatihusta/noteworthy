import os
from pathlib import Path
from unittest import mock
import pytest
from noteworthy.nginx import NginxController


@pytest.fixture
def nc(tmpdir, monkeypatch):
    monkeypatch.setattr('noteworthy.notectl.plugins.NoteworthyPlugin.base_config_dir', tmpdir.strpath)
    nc = NginxController()
    assert nc.nginx_config_path == '/etc/nginx/nginx.conf'
    assert nc.nginx_sites_enabled == '/etc/nginx/sites-enabled'
    assert nc.letsencrypt_dir == '/etc/letsencrypt'
    assert nc.nginx_pid_file == '/run/nginx.pid'
    assert os.path.exists(nc.nginx_gateway_template)
    assert os.path.exists(nc.nginx_app_template)
    assert nc.nginx_start_poll_count == 5
    assert nc.sites_dir == os.path.join(nc.config_dir, 'sites') 
    assert nc.tls_backend_dir == os.path.join(nc.config_dir, 'backends')
    assert nc.letsencrypt_bk == os.path.join(nc.config_dir, 'letsencrypt')
    assert nc.tls_success_file == os.path.join(nc.config_dir, 'tls_success')

    # pretend nginx is running
    nginx_pid_file = os.path.join(tmpdir.strpath, 'nginx.pid')
    os.system(f'touch {nginx_pid_file}')
    nc.nginx_pid_file = nginx_pid_file
    # create system dirs
    nc.nginx_config_path = os.path.join(tmpdir.strpath, 'nginx.conf')
    nc.nginx_sites_enabled = os.path.join(tmpdir.strpath, 'sites-enabled')
    nc.letsencrypt_dir = os.path.join(tmpdir.strpath, 'letsencrypt')
    Path(nc.nginx_sites_enabled).mkdir(exist_ok=True)
    Path(nc.letsencrypt_dir).mkdir(exist_ok=True)

    def mock_start(plugin_name):
        return None
    monkeypatch.setattr(nc, '_start', mock_start)
    return nc

@pytest.fixture
def mock_poll_for_good_status(monkeypatch):
    def do_mock(status):
        class MockRespone:
            def __init__(self, status):
                self.status = status
        def mock_getresponse(status):
            def getresponse(self):
                return MockRespone(status)
            return getresponse
        def mock_request(self, method, uri):
            return None

        monkeypatch.setattr('http.client.HTTPConnection.request', mock_request)
        monkeypatch.setattr('http.client.HTTPConnection.getresponse', mock_getresponse(status))
    return do_mock

@mock.patch('os.system')
def test_nginx_reload(os_system, nc):
    nc._reload()
    os_system.assert_called_once_with("nginx -s reload")

def test_poll_for_good_status(mock_poll_for_good_status, nc):

    mock_poll_for_good_status(200)
    assert nc.poll_for_good_status('testaddress.dev') == True

    mock_poll_for_good_status(400)
    with pytest.raises(Exception) as excepinfo:
        nc.poll_for_good_status('testaddress.dev', 1)
    assert 'testaddress.dev failed' in str(excepinfo)

# def test_start_nginx_fail(nc):
#     nc.nginx_pid_file = 'no_exist.pid'
#     # test poll for nginx start
#     with pytest.raises(Exception) as exception:
#         nc.nginx_start_poll_count = 1
#         nc.start()
#     assert 'Giving up waiting for nginx to start.' in str(exception)

def test_start_nginx_link(nc, monkeypatch):
    monkeypatch.setenv('NOTEWORTHY_ROLE', 'link')
    monkeypatch.setenv('NOTEWORTHY_DOMAIN_REGEX', '.matrix.testdomain.com')

    assert os.path.exists(nc.config_dir) == False
    nc.start()
    assert os.path.exists(nc.config_dir) == True
    assert os.path.exists(nc.sites_dir) == True
    assert os.path.exists(nc.tls_backend_dir) == True

    links = nc.get_link_set()
    assert 'backends' in links
    assert links['backends'][0]['domain'] == '.matrix.testdomain.com'
    assert links['backends'][0]['endpoint'] == '10.0.0.2:443'

    with open(nc.nginx_config_path, 'r') as nginx_config:
        nginx_config = nginx_config.read()
    assert '$targetBackend {\n\t\n\t.matrix.testdomain.com\t10.0.0.2:443;\n\t\n' in nginx_config

    with open(os.path.join(nc.nginx_sites_enabled,'launcher.conf'), 'r') as launcher_config:
        launcher_config = launcher_config.read()

    assert 'proxy_pass http://10.0.0.2;' in launcher_config

def test_start_nginx_taproot(nc, monkeypatch, mock_poll_for_good_status):
    monkeypatch.setenv('NOTEWORTHY_ROLE', 'taproot')
    monkeypatch.setenv('NOTEWORTHY_DOMAIN_REGEX', '.matrix.testdomain.com')
    monkeypatch.setenv('NOTEWORTHY_DOMAIN', 'testdomain.testdomain.com')

    def mock_certbot(domains):
        return None
    monkeypatch.setattr(nc, '_get_letsencrypt_cert', mock_certbot)
    monkeypatch.setattr(nc, '_install_letsencrypt_cert', mock_certbot)
    assert os.path.exists(nc.config_dir) == False
    mock_poll_for_good_status(200)

    # write something to letsencrypt dir to test backing it up
    with open(os.path.join(nc.letsencrypt_dir, 'testfile'), 'w') as testfile:
        testfile.write('something')
    with open(os.path.join(nc.nginx_config_path), 'w') as testfile:
        testfile.write('taproot-nginx.conf')
    nc.start()
    assert os.path.exists(nc.config_dir) == True
    assert os.path.exists(nc.sites_dir) == True
    assert os.path.exists(nc.tls_backend_dir) == True
    assert os.path.exists(nc.letsencrypt_bk) == True

    assert os.path.exists(os.path.join(nc.letsencrypt_bk, 'testfile'))
    assert os.path.exists(os.path.join(nc.config_dir, 'nginx.conf'))
    assert os.path.exists(nc.tls_success_file)
    nc.set_http_proxy_pass('test_app', 'test-app-container', '172.18.0.2')

    # test nc._reconfigure_nginx
    assert nc.is_first_run == False
    os.system(f'rm -rf {nc.nginx_sites_enabled}/*')
    os.system(f'rm -rf {nc.letsencrypt_dir}/*')
    os.system(f'rm -rf {nc.nginx_config_path}')

    nc.start()
    assert os.path.exists(nc.nginx_config_path) == True
    assert os.path.exists(os.path.join(nc.letsencrypt_dir, 'testfile')) == True
    assert os.path.exists(os.path.join(nc.nginx_sites_enabled, 'test_app.conf')) == True