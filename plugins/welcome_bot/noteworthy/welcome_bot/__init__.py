import os
import time
import yaml
import matrixbz
from noteworthy.notectl.plugins import NoteworthyPlugin

CHANNEL_GREETING = '''
<h1>Welcome to Noteworthy Messenger</h1>
<p>I'm <strong>WelcomeBot</strong> your personal tour guide to the Noteworthy ecosystem.</p>
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
        self.first_run_file = os.path.join(self.config_dir, 'first_run')

    @matrixbz.matrixbz_startup_method
    async def startup(self, client, **kwargs):
        if not self._has_run():
            room = await client.room_create(is_direct=True, invite=self.USER_WHITELIST)
            await client.room_send(room_id=room.room_id,
                                   message_type='m.room.message',
                                   content={
                                       'msgtype': 'm.text',
                                       'format': 'org.matrix.custom.html',
                                       'body': CHANNEL_GREETING,
                                       'formatted_body': CHANNEL_GREETING})
            with open(self.first_run_file, 'w') as f:
                f.write(time.asctime())

    def start(self):
        pass

    def _has_run(self):
        return os.path.isfile(self.first_run_file)

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
