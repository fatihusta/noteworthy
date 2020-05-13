import os
import shutil

from grpcz import grpc_controller, grpc_method
from clicz import cli_method

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.wireguard import wg

class VpnController(NoteworthyPlugin):

    PLUGIN_NAME = 'vpn'
    DJANGO_APP_MODULE = 'noteworthy.vpn'

    def __init__(self):
        super().__init__(__file__)
        self.wg_config_template_path = os.path.join(self.deploy_dir, 'wg.tmpl.conf')

    def start(self, **kwargs):
        self._start(self.PLUGIN_NAME)

    def run(self, **kwargs):
        raise NotImplementedError(
            f'Method run not implemented for {self.__class__.__name__}')

    def check_health(self, **kargs):
        return 'OK'

    @cli_method
    def add_device(self, device_name: str = 'mobile', device_type: str = 'mobile'):
        '''
        Add a device to your network.
        ---
        Args:
            device_name: Name of the device you're adding
            device_type: Type of device 'mobile' or 'desktop'
        '''
        if self.is_first_run:
            self.create_config_dir()
            wg_key_path = os.path.join(self.config_dir, 'wg1.key')
            wg.genkey(wg_key_path)
            wg.init('wg1', '10.0.1.1/24', wg_key_path)
        device_wg_key_path = os.path.join(self.config_dir, f'{device_name}.key')
        if os.path.exists(device_wg_key_path):
            self._gen_device_config(device_name)
        else:
            wg.genkey(device_wg_key_path)
            shutil.copy(self.wg_config_template_path, os.path.join(self.config_dir, f'{device_name}.conf'))
            self._gen_device_config(device_name)

    def _gen_device_config(self, device_name: str, device_type: str = 'mobile'):
        conf_file = os.path.join(self.config_dir, f'{device_name}.conf')
        qr_out = os.path.join(self.config_dir, f'{device_name}.png')
        os.system(f'qrencode -o {qr_out} < {conf_file}')
        os.system(f'qrencode -t ansiutf8 < {conf_file}')

Controller = VpnController
