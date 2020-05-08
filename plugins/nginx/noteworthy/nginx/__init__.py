import os
import json
import shutil
import time
import yaml
from pathlib import Path
from jinja2 import Template
from clicz import cli_method

from noteworthy.notectl.plugins import NoteworthyPlugin


class NginxController(NoteworthyPlugin):

    PLUGIN_NAME = 'nginx'

    def __init__(self):
        super().__init__(__file__)
        self.nginx_gateway_template = os.path.join(self.deploy_dir, 'nginx.gateway.tmpl.conf')
        self.nginx_app_template = os.path.join(self.deploy_dir, 'app.link.nginx.tmpl.conf')
        self.nginx_config_path = '/etc/nginx/nginx.conf'
        self.nginx_sites_enabled = '/etc/nginx/sites-enabled'
        self.letsencrypt_dir = '/etc/letsencrypt'
        self.nginx_pid_file = '/run/nginx.pid'
        self.nginx_start_poll_count = 5
        self.tls_success_file = os.path.join(self.config_dir, 'tls_success')
        self.sites_dir = os.path.join(self.config_dir, 'sites')
        self.tls_backend_dir = os.path.join(self.config_dir, 'backends')
        self.letsencrypt_bk = os.path.join(self.config_dir, 'letsencrypt')

    @cli_method
    def run(self):
        '''start nginx, blocking
        '''
        os.system("nginx -g 'daemon off;'")

    def poll_for_good_status(self, endpoint, max_tries=30):
        '''
        Poll http endpoint until we get a good http response (< 400)
        '''
        import time
        from http import client
        def do_request(endpoint, count=0):
            c = client.HTTPConnection(endpoint, timeout=1)
            c.request('GET', '/')
            resp = c.getresponse()
            if resp.status < 400:
                return True
            if count >= max_tries:
                raise Exception(f'HTTP poll for good status (< 400) at {endpoint} failed.')
            time.sleep(1)
            do_request(endpoint, count+1)
        return do_request(endpoint)


    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)
        # wait for nginx to start
        count = 0
        while not os.path.exists(self.nginx_pid_file) and count <= self.nginx_start_poll_count:
            time.sleep(1)
            running = os.path.exists(self.nginx_pid_file)
            if running:
                break
            if count == self.nginx_start_poll_count:
                raise Exception('Giving up waiting for nginx to start. Check nginx config.')
            count = count + 1

        if self.is_first_run:
            self.create_config_dir()
            Path(self.sites_dir).mkdir(exist_ok=True)
            Path(self.tls_backend_dir).mkdir(exist_ok=True)
            if os.environ['NOTEWORTHY_ROLE'] == 'link':
                self.add_tls_stream_backend('launcher', os.environ['NOTEWORTHY_DOMAIN_REGEX'], '10.0.0.2')
                self.set_http_proxy_pass('launcher', os.environ['NOTEWORTHY_DOMAIN_REGEX'], '10.0.0.2')
            elif os.environ['NOTEWORTHY_ROLE'] == 'taproot':
                Path(self.letsencrypt_bk).mkdir(exist_ok=True)
                # TODO emit events for these type of interdependent interactions
                self.poll_for_good_status(os.environ['NOTEWORTHY_DOMAIN'])
                # Request Let's Encrypt certs with certbot
                self.get_tls_certs([os.environ['NOTEWORTHY_DOMAIN'], f"matrix.{os.environ['NOTEWORTHY_DOMAIN']}"])
        else:
            self._reconfigure_nginx()
            self._reload()


    def _reload(self, **kwargs):
        os.system('nginx -s reload')

    def _reconfigure_nginx(self):
        # TODO this will change need to change when taproots can act as hubs too
        if os.environ['NOTEWORTHY_ROLE'] == 'hub':
            backends = self.get_link_set()
            self.write_config(backends)
        if os.environ['NOTEWORTHY_ROLE'] in ['taproot', 'hub']:
            os.system(f'cp -r {self.sites_dir}/* {self.nginx_sites_enabled}')
        if os.environ['NOTEWORTHY_ROLE'] == 'taproot':
            Path(self.letsencrypt_dir).mkdir(parents=True, exist_ok=True)
            os.system(f'cp -r {self.letsencrypt_bk}/* {self.letsencrypt_dir}')
            nginx_conf_bak = os.path.join(self.config_dir, 'nginx.conf')
            os.system(f'cp {nginx_conf_bak} {self.nginx_config_path}')


    def _render_template(self, template_path, config):
        with open(template_path, 'r') as template:
            t = Template(template.read())
        return t.render(config)

    def write_config(self, backends):
        '''
        writes main nginx config to self.nginx_config_path
        used to config transparent tls-proxying gateway->link & link->taproot
        '''
        if isinstance(backends, str):
            backends = json.loads(backends)

        rendered_config = self._render_template(self.nginx_gateway_template, backends)
        with open(self.nginx_config_path, 'w') as output_file:
            output_file.write(rendered_config)
        self._reload()

    def set_http_proxy_pass(self, app_name: str, domain: str, ip_addr: str,
        template_path: str = None):
        '''
        add new "virtualhost" site to nginx (ie noteworthy app)
        <app>.conf to nginx_sites_enabled
        '''
        if not template_path:
            template_path = self.nginx_app_template

        config = {'domain': domain, 'container': ip_addr}
        rendered_config = self._render_template(template_path, config)
        with open(os.path.join(self.nginx_sites_enabled, f'{app_name}.conf'), 'w') as output_file:
            output_file.write(rendered_config)
        with open(os.path.join(self.sites_dir, f'{app_name}.conf'), 'w') as output_file:
            output_file.write(rendered_config)
        self._reload()

    def add_tls_stream_backend(self, app_name: str, domain: str, ip_addr: str):
        self.store_link(app_name, domain, ip_addr)
        backends = self.get_link_set()
        self.write_config(backends)

    def _get_letsencrypt_cert(self, domains_str: str):
        '''
        Get Let's Encrypt certs wit Certbot
        '''
        os.system(f'certbot certonly --non-interactive --agree-tos --webroot -m hi@decentralabs.io -w /var/www/html -d {domains_str}')

    def _install_letsencrypt_cert(self, domain: str):
        os.system(f'certbot install --cert-path /etc/letsencrypt/live/{domain}/cert.pem --key-path /etc/letsencrypt/live/{domain}/privkey.pem --fullchain-path /etc/letsencrypt/live/{domain}/fullchain.pem -d {domain} --redirect')

    def get_tls_certs(self, domains: list):
        domains_str = ' -d '.join(domains)
        self._get_letsencrypt_cert(domains_str)
        self._install_letsencrypt_cert(domains[0])
        os.system(f'cp -r {self.letsencrypt_dir}/* {self.letsencrypt_bk}')
        os.system(f'cp {self.nginx_config_path} {self.config_dir}')
        os.system(f'touch {self.tls_success_file}')


    def poll_cerbot_success(self):
        count = 0
        while count < 15:
            if os.path.exists(self.tls_success_file):
                return True
            count = count + 1
            time.sleep(1)
        raise Exception('Giving up waiting for certbot success.')


    def read_yaml_file(self, filename):
        with open(filename, 'r') as peer_file:
            res = yaml.safe_load(peer_file.read())
        return res

    def store_link(self, app_name: str, domain: str, ip_addr: str):
        link = { 'domain': f'{domain}',
                    'endpoint': f'{ip_addr}:443'}

        with open(os.path.join(self.tls_backend_dir, f'{app_name}.yaml'), 'w') as link_file:
            link_file.write(yaml.dump(link))

    def get_link_set(self):

        links = [ self.read_yaml_file(os.path.join(self.tls_backend_dir, link_file))
                    for link_file in os.listdir(self.tls_backend_dir) ]
        return {
            'backends': links
        }

Controller = NginxController
