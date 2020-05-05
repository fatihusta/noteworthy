import tarfile
import os
from jinja2 import Template
from noteworthy.notectl.plugins import NoteworthyPlugin


class RiotWebController(NoteworthyPlugin):

    PLUGIN_NAME = 'riot_web'

    def __init__(self):
        super().__init__(__file__)

    def start(self, *args, **kwargs):
        if self.is_first_run:
            tar_path = os.path.join(self.deploy_dir, 'web_app.tar.gz')
            with tarfile.open(tar_path) as tar:
                top_lvl_dir = tar.getnames()[0]
                self.create_config_dir()
                tar.extractall(path=self.config_dir)
            app_dir = os.path.join(self.deploy_dir, top_lvl_dir)
            target_app_dir = os.path.join(self.deploy_dir, 'webapp')
            os.system(f'mv {app_dir} {target_app_dir}')
            config_tmpl = os.path.join(self.deploy_dir, 'config.tmpl.json')
            config_target = os.path.join(self.config_dir, 'webapp/config.json')
            configs = {'domain': os.environ['NOTEWORTHY_DOMAIN']}
            self._generate_file_from_template(
                config_tmpl, config_target, configs)

    def _generate_file_from_template(self, tmpl_path, target, configs):
        with open(tmpl_path, 'r') as f:
            tmpl = Template(f.read())
        rendered = tmpl.render(configs)
        with open(target, 'w') as f:
            f.write(rendered)


Controller = RiotWebController
