import getpass
import os
import nio
import time
import string
import asyncio
import secrets
from jinja2 import Template

from clicz import cli_method
from procz import TimedLoop
from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.notectl.plugins import PluginManager


class MessengerController(NoteworthyPlugin):
    '''manage Noteworthy messenger (create user, etc)
    '''

    PLUGIN_NAME = 'messenger'
    USER_CLI = True

    SECRET_ALPHABET = string.digits + string.ascii_letters + ".,;^&*-_+=#~@"
    SECRET_LENGTH = 50

    def __init__(self):
        super().__init__(__file__)
        self.plugins = PluginManager.load_plugins()
        self.log_config_file = os.path.join(self.config_dir, 'homeserver.log.config')
        self.log_file = os.path.join(self.config_dir, 'homeserver.log')

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
            'config_dir': self.config_dir,
            'homeserver_log_config': self.log_config_file,
            'homeserver_log_target': self.log_file}
        homeserver_tmpl = os.path.join(
            self.deploy_dir, 'homeserver.tmpl.yaml')
        homeserver_target = os.path.join(
            self.config_dir, 'homeserver.yaml')
        self._generate_file_from_template(
            homeserver_tmpl, homeserver_target, configs)
        logconfig_tmpl = os.path.join(
            self.deploy_dir, 'log.config.tmpl.yaml')
        self._generate_file_from_template(
            logconfig_tmpl, self.log_config_file, configs)
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
        '''daemonize messenger
        '''
        was_first_run = False
        if self.is_first_run:
            self._run_first_time_setup()
            was_first_run = True
        if not self._is_synctl_running():
            hs_config = os.path.join(self.config_dir, 'homeserver.yaml')
            os.chdir(self.config_dir)
            os.system(f'synctl start {hs_config}')
        self._poll_for_synctl_start()
        if was_first_run:
            # TODO password should be passed a more secure way
            self.create_user(os.environ['MATRIX_USER'], os.environ['MATRIX_PASSWORD'], True)
            try:
                asyncio.get_event_loop().run_until_complete(self._invite_welcomebot())
            except:
                pass
        self.start_dependencies()
        os.chdir(self.config_dir)
        self._poll_for_homeserver_log()
        os.system(f'tail -f {self.log_file}')

    def _is_synctl_running(self):
        pid_file = os.path.join(self.config_dir, 'homeserver.pid')
        return os.path.isfile(pid_file)

    def _poll_for_synctl_start(self):
        with TimedLoop(20) as l:
            l.run_til(self._is_synctl_running)

    def _does_log_file_exist(self):
        return os.path.isfile(self.log_file)

    def _poll_for_homeserver_log(self):
        with TimedLoop(20) as l:
            l.run_til(self._does_log_file_exist)

    async def _invite_welcomebot(self):
        domain = os.environ.get('NOTEWORTHY_DOMAIN')
        user_name = os.environ.get('MATRIX_USER')
        user_address = f'@{user_name}:{domain}'
        client = nio.AsyncClient(f'https://matrix.{domain}', user_address)
        user_password = os.environ.get('MATRIX_PASSWORD')
        await client.login(user_password)
        await client.room_create(is_direct=True, invite=[f'@welcomebot:{domain}'])
        await client.logout()

    @cli_method
    def create_user(self, username=None, password=None, admin=False):
        '''create a matrix user
        ---
        Args:
            username: username of user to create
            password: of user to create
            admin: grant user admin privileges
        '''
        if not username:
            username = input('Username: ')
        if not password:
            password = getpass.getpass()
        os.chdir(self.config_dir)
        if admin:
            os.system(f'register_new_matrix_user -u {username} -p {password} -a -c homeserver.yaml http://localhost:8008')
        else:
            os.system(f'register_new_matrix_user -u {username} -p {password} --no-admin -c homeserver.yaml http://localhost:8008')

Controller = MessengerController
