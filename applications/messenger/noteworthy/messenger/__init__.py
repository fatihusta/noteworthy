import os
import time
import string
import secrets
from jinja2 import Template

from clicz import cli_method
from procz import TimedLoop
from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.notectl.plugins import PluginManager


class MessengerController(NoteworthyPlugin):

    PLUGIN_NAME = 'messenger'
    PACKAGE_CACHE = '/var/noteworthy/cache/packages'

    SECRET_ALPHABET = string.digits + string.ascii_letters + ".,;^&*-_+=#~@"
    SECRET_LENGTH = 50

    def __init__(self):
        super().__init__(__file__)
        self.plugins = PluginManager.load_plugins()

    def _run_first_time_setup(self):
        self.create_config_dir()
        if 'riot_web' in self.plugins:
            riot = self.plugins['riot_web'].Controller()
            web_client_location = os.path.join(riot.config_dir, 'webapp')
        else:
            web_client_location = None
        configs = {
            'domain': os.environ['NOTEWORTHY_DOMAIN'],
            'registration_shared_secret': self._get_new_secret(),
            'macaroon_secret_key': self._get_new_secret(),
            'form_secret': self._get_new_secret(),
            'web_client_location': web_client_location,
            'config_dir': self.config_dir}
        homeserver_tmpl = os.path.join(
            self.deploy_dir, 'homeserver.tmpl.yaml')
        homeserver_target = os.path.join(
            self.config_dir, 'homeserver.yaml')
        self._generate_file_from_template(
            homeserver_tmpl, homeserver_target, configs)
        from synapse.config.homeserver import HomeServerConfig
        HomeServerConfig.load_or_generate_config('Noteworthy Messenger',
        ['-c', homeserver_target, '--generate-missing-configs'])

    def _generate_file_from_template(self, tmpl_path, target, configs):
        with open(tmpl_path, 'r') as f:
            tmpl = Template(f.read())
        rendered = tmpl.render(configs)
        with open(target, 'w') as f:
            f.write(rendered)

    def _get_new_secret(self):
        return ''.join((
            secrets.choice(self.SECRET_ALPHABET)
            for i
            in range(self.SECRET_LENGTH)))

    @cli_method
    def start(self, *args, **kwargs):
        '''Daemonize messenger
        '''
        if self.is_first_run:
            self._run_first_time_setup()
        if not self._is_synctl_running():
            hs_config = os.path.join(self.config_dir, 'homeserver.yaml')
            os.chdir(self.config_dir)
            os.system(f'synctl start --daemonize -c {hs_config}')
        self._poll_for_synctl_start()
        self.start_dependencies()

    def _is_synctl_running(self):
        pid_file = os.path.join(self.config_dir, 'homeserver.pid')
        return os.path.isfile(pid_file)

    def _poll_for_synctl_start(self):
        with TimedLoop(20) as l:
            l.run_til(self._is_synctl_running)

Controller = MessengerController
