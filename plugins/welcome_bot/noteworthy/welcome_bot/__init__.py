import os
import yaml
import matrixbz
from noteworthy.notectl.plugins import NoteworthyPlugin

CHANNEL_GREETING = '''
<h1>Welcome to Noteworthy Messenger</h1>
<p>I'm <strong>WelcomeBot</strong> your personal tour guide to the Noteworthy Ecosystem.</p>
<h2>Getting started</h2>
<ul>
    <li>Join #welcome:noteworthy.im say hi</li>
    <li>Get support #support:noteworthy.im</li>
    <li>Learn about <a href="https://about.riot.im/features">Riot</a></li>
</ul>
<h2>Try more Noteworthy applications</h2>
<ul>
    <li><code>notectl install vpn</code></li>
</ul>
'''

@matrixbz.matrixbz_controller('welcomebot', channel_greeting=CHANNEL_GREETING)
class WelcomeBotController(NoteworthyPlugin):
    PLUGIN_NAME = 'welcome_bot'

    AUTH = matrixbz.auth.UserWhitelist

    def __init__(self):
        super().__init__(__file__)
        if self.is_first_run:
            self.create_config_dir()
            main_user = os.environ['MATRIX_USER']
            domain = os.environ['NOTEWORTHY_DOMAIN']
            address = f'@{main_user}:{domain}'
            auth_config = {
                'whitelist': [address]
            }
            self._write_yaml_config('auth', auth_config)
        auth = self._read_yaml_config('auth')
        self.USER_WHITELIST = auth.get('whitelist')

    def start(self):
        pass

    def _read_yaml_config(self, filename):
        file_path = os.path.join(self.config_dir, f'{filename}.yaml')
        with open(file_path, 'r') as f:
            res = yaml.safe_load(f.read())
        return res

    def _write_yaml_config(self, filename, data):
        file_path = os.path.join(self.config_dir, f'{filename}.yaml')
        with open(file_path, 'w') as f:
            f.write(yaml.dump(data))
        return file_path



Controller = WelcomeBotController
