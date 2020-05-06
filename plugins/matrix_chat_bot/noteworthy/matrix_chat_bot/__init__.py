import os
import yaml
from jinja2 import Template
from clicz import cli_method
from procz import ProcManager
from noteworthy.notectl.plugins import NoteworthyPlugin, PluginManager


class MatrixChatBotController(NoteworthyPlugin):
    '''Automagic Matrix ChatBot Registrar and Manager
    '''

    PLUGIN_NAME = 'matrix-chat-bot'

    def __init__(self):
        super().__init__(__file__)

    def start(self, *args, **kwargs):
        if self.is_first_run:
            self.create_config_dir()
            self.bot_manager = ProcManager(lock_dir=self.config_dir)
            self._create_bots()
        else:
            self.restart_bots()

    def _create_bots(self):
        bot_controllers = self._get_bot_controllers()
        [self._create_bot_account(controller.MATRIXBZ_BOT_NAME)
         for controller in bot_controllers]
        [self._launch_bot(controller) for controller in bot_controllers]

    @cli_method
    def restart_bots(self):
        '''Restart and Launch all registered matrix bots
        '''
        bot_controllers = self._get_bot_controllers()
        [self._launch_bot(controller) for controller in bot_controllers]

    def _create_bot_account(self, bot_name):
        password = secrets.token_hex(8)
        from noteworthy.messenger import MessengerController
        mc = MessengerController()
        hscfg = os.path.join(mc.config_dir, 'homeserver.yaml')
        reg_cmd = f'register_new_matrix_user -u {bot_name} -p {password} -a -c {hscfg} http://localhost:8008'
        os.system(reg_cmd)
        domain = os.environ['NOTEWORTHY_DOMAIN']
        creds = {
            'homeserver': f'https://matrix.{domain}',
            'user': '@{bot_name}:{domain}',
            'password': password
        }
        self._write_yaml_config(f'{bot_name}.creds', creds)

    def _launch_bot(self, bot_controller):
        bot_name = bot_controller.MATRIXBZ_BOT_NAME
        creds = self._read_yaml_config(f'{bot_name}.creds')
        create_bot = lambda: bot_controller.create_matrix_bot(creds)
        self.bot_manager.start_proc(bot_name, create_bot, kill_old=True)

    def _get_bot_controllers(self):
        controllers = []
        for plugin, module in PluginManager.load_plugins().items():
            if hasattr(module.Controller, 'matrixbz_controller'):
                controllers.append(module.Controller)
        return controllers

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


Controller = MatrixChatBotController
