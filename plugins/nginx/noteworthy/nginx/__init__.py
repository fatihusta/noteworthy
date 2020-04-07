import os
import shutil

from jinja2 import Template

from noteworthy.notectl.plugins import NoteworthyPlugin


class NginxController(NoteworthyPlugin):

    PLUGIN_NAME = 'nginx'

    def __init__(self):
        super().__init__(__file__)
        self.nginx_gateway_template = os.path.join(self.deploy_dir, 'nginx.gateway.tmpl.conf')
        self.nginx_config_path = '/etc/nginx/nginx.test.conf'

    def run(self, **kwargs):
        os.system("nginx -g 'daemon off;'")

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)


    def _reload(self, **kwargs):
        os.system('nginx -s reload')

    def write_config(self, config, template_path, output_path, **kwargs):
        with open(template_path, 'r') as template:
            t = Template(template.read())
        rendered_template = t.render(config)
        with open(output_path, 'w') as output_file:
            output_file.write(rendered_template)

    def write_gateway_config(self, **kwargs):
        config = self.tls_stream_backends
        self.write_config(config, self.nginx_gateway_template, self.nginx_config_path)

    def serve_domain(self, domain, config, get_certs=True):
        if get_certs:
            cert_info = self._cerbot(domain)
        self._write_config(domain, config, cert_info)
        self._reload()

    @property
    def tls_stream_backends(self):
        return { 'backends' : [{
                             'domain' : '*.root.community',
                             'endpoint' : '172.18.0.2:443'
                           }]
            }

Controller = NginxController
