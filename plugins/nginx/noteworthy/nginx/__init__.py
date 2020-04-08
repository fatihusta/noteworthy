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
        self.nginx_config_path = '/etc/nginx/nginx.test.conf'
        self.nginx_sites_enabled = '/etc/nginx/sites-enabled'

    def run(self, **kwargs):
        os.system("nginx -g 'daemon off;'")

    def start(self, **kwargs):
        if os.environ['NOTEWORTHY_ROLE'] == 'link':
            self.set_link_tls_stream_backend(os.environ['NOTEWORTHY_DOMAIN'])
            launcher_nginx_conf = {
                'domain'  : f"*.{os.environ['NOTEWORTHY_DOMAIN']}",
                'link_ip' : '10.0.0.2'
            }
            self.add_app_nginx_config('launcher', 'link', launcher_nginx_conf)
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

    def add_app_nginx_config(self, app_name, role, config):
        '''
        add new "virtualhost" site to nginx (ie noteworthy app)
        <app>.conf to nginx_sites_enabled
        '''
        if role == 'link':
            template_path = os.path.join(self.deploy_dir, 'app.link.nginx.tmpl.conf')
        elif role == 'hub':
            template_path = os.path.join(self.deploy_dir, 'app.gateway.nginx.tmpl.conf')
        else:
            raise Exception(f'Unsupported role: {role} for NginxController.add_app_nginx_config')
        rendered_config = self._render_template(template_path, config)
        with open(os.path.join(self.nginx_sites_enabled, f'{app}.conf'), 'w') as output_file:
            output_file.write(rendered_config)
        self._reload()

    def set_link_tls_stream_backend(self, domain: str):
        backends =  { 'backends' : [{
                                               'domain' : f'*.{domain}',
                                             'endpoint' : '10.0.0.2:443'
                                            }]
                           }
        self.write_config(backends)



Controller = NginxController
