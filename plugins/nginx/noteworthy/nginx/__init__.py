import os
import json
import shutil
import yaml

from jinja2 import Template

from noteworthy.notectl.plugins import NoteworthyPlugin


class NginxController(NoteworthyPlugin):

    PLUGIN_NAME = 'nginx'

    def __init__(self):
        super().__init__(__file__)
        self.nginx_gateway_template = os.path.join(self.deploy_dir, 'nginx.gateway.tmpl.conf')
        self.nginx_app_template = os.path.join(self.deploy_dir, 'app.link.nginx.tmpl.conf')
        self.nginx_config_path = '/etc/nginx/nginx.conf'
        self.nginx_sites_enabled = '/etc/nginx/sites-enabled'

    def run(self, **kwargs):
        os.system("nginx -g 'daemon off;'")

    def poll_for_good_status(self, endpoint, max_tries=30):
        '''
        Poll http endpoint until we get a good http response (< 400)
        '''
        import time
        from http import client
        def do_request(endpoint, count=0):
            c = client.HTTPConnection(endpoint)
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
        if self.is_first_run:
            self.create_config_dir()
            if os.environ['NOTEWORTHY_ROLE'] == 'link':
                self.add_tls_stream_backend(os.environ['NOTEWORTHY_DOMAIN'], '10.0.0.2')
                self.set_http_proxy_pass('launcher', f".{os.environ['NOTEWORTHY_DOMAIN']}", '10.0.0.2')
            elif os.environ['NOTEWORTHY_ROLE'] == 'taproot':
                # TODO emit events for these type of interdependent interactions
                self.poll_for_good_status(os.environ['NOTEWORTHY_DOMAIN'])
                # Request Let's Encrypt certs with certbot
                self.certbot([os.environ['NOTEWORTHY_DOMAIN'], f"matrix.{os.environ['NOTEWORTHY_DOMAIN']}"])


    def _reload(self, **kwargs):
        os.system('nginx -s reload')

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

    def set_http_proxy_pass(self, app_name, domain: str, ip_addr: str,
        template_path: str = None):
        '''
        add new "virtualhost" site to nginx (ie noteworthy app)
        <app>.conf to nginx_sites_enabled
        '''
        if not template_path:
            template_path = self.nginx_app_template

        config = {'domain': f'{domain}', 'container': ip_addr}
        rendered_config = self._render_template(template_path, config)
        with open(os.path.join(self.nginx_sites_enabled, f'{app_name}.conf'), 'w') as output_file:
            output_file.write(rendered_config)
        self._reload()

    def add_tls_stream_backend(self, domain: str, ip_addr: str):
        self.store_link(domain, ip_addr)
        backends = self.get_link_set()
        self.write_config(backends)

    def certbot(self, domains: list):
        '''
        Get Let's Encrypt certs wit Certbot
        '''
        domain_param = ' -d '.join(domains)
        os.system(f'certbot certonly --non-interactive --agree-tos --webroot -m hi@decentralabs.io -w /var/www/html -d {domain_param}')
        os.system(f'certbot install --cert-path /etc/letsencrypt/live/{domains[0]}/cert.pem --key-path /etc/letsencrypt/live/{domains[0]}/privkey.pem --fullchain-path /etc/letsencrypt/live/{ domains[0] }/fullchain.pem -d { domains[0] } --redirect')

    def read_yaml_file(self, filename):
        with open(filename, 'r') as peer_file:
            res = yaml.safe_load(peer_file.read())
        return res

    def store_link(self, domain: str, ip_addr: str):
        link = { 'domain': f'~{domain}',
                    'endpoint': f'{ip_addr}:443'}

        with open(os.path.join(self.config_dir, f'{domain}.yaml'), 'w') as link_file:
            link_file.write(yaml.dump(link))

    def get_link_set(self):

        links = [ self.read_yaml_file(os.path.join(self.config_dir, link_file))
                    for link_file in os.listdir(self.config_dir) ]
        return {
            'backends': links
        }

Controller = NginxController
