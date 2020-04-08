import os
import json
import shutil

from jinja2 import Template

from noteworthy.notectl.plugins import NoteworthyPlugin


class NginxController(NoteworthyPlugin):

    PLUGIN_NAME = 'nginx'

    def __init__(self):
        super().__init__(__file__)
        self.nginx_config_template = os.path.join(self.deploy_dir, 'nginx.gateway.tmpl.conf')
        self.nginx_config_path = '/etc/nginx/nginx.conf'
        self.nginx_sites_enabled = '/etc/nginx/sites-enabled'

    def run(self, **kwargs):
        os.system("nginx -g 'daemon off;'")

    def start(self, **kwargs):
        if os.environ['NOTEWORTHY_ROLE'] == 'link':
            self.set_tls_stream_backend(os.environ['NOTEWORTHY_DOMAIN'], '10.0.0.2')
            self.set_http_proxy_pass('launcher', os.environ['NOTEWORTHY_DOMAIN'], '10.0.0.2')
        self._start(self.PLUGIN_NAME)

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

        rendered_config = self._render_template(self.nginx_config_template, backends)
        with open(self.nginx_config_path, 'w') as output_file:
            output_file.write(rendered_config)
        self._reload()

    def set_http_proxy_pass(self, app_name, domain: str, ip_addr: str):
        '''
        add new "virtualhost" site to nginx (ie noteworthy app)
        <app>.conf to nginx_sites_enabled
        '''
        template_path = os.path.join(self.deploy_dir, 'app.link.nginx.tmpl.conf')
        config = {'domain': domain, 'ip_addr':ip_addr}
        rendered_config = self._render_template(template_path, config)
        with open(os.path.join(self.nginx_sites_enabled, f'{app_name}.conf'), 'w') as output_file:
            output_file.write(rendered_config)
        self._reload()

    def set_tls_stream_backend(self, domain: str, ip: str):
        backends =  { 'backends' : [{
                                               'domain' : f'~.{domain}',
                                             'endpoint' : f'{ip}:443'
                                            }]
                           }
        self.write_config(backends)

    def certbot(self, domains: list):
        '''
        certbot certonly --non-interactive --agree-tos --webroot -m hi@decentralabs.io -w /var/www/html -d demo.noteworthy.im -d matrix.demo.notworthy.im
        certbot install --cert-path /etc/letsencrypt/live/hub.root.community/cert.pem --key-path /etc/letsencrypt/live/hub.root.community/privkey.pem --fullchain-path /etc/letsencrypt/live/hub.root.community/fullchain.pem -d root.community --redirect
        '''



Controller = NginxController
