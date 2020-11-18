import os
from clicz import cli_method
import docker

from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.reservation_client import ReservationController


class LinkController(NoteworthyPlugin):

    PLUGIN_NAME = 'link_connect'

    def __init__(self):
        super().__init__(__file__)
        self.docker = docker.from_env()

    @cli_method
    def connect(self, protocol: str, container_id: str=None, host_port: int=None, fqdn: str=None, link_id: str=None):
        '''Connect to a local container or host port via Noteworthy link
        ---
        Args:
            protocol: Supported protocols are ['https']
            container_id: ID of the container that you would like to link, ports will be automatically introspected via Docker's EXPOSE semantic
            host_port: Link to a port on the host
            fqdn: Fully-qualified domain name at which the service will be available
            link_id: ID of the remote link endpoint
        '''
        from noteworthy.launcher import LauncherController
        lc = LauncherController()
        #email = input('Please enter your email address: ')
        auth_code = input('Please enter auth_code: ')
        from noteworthy.reservation_client import ReservationController
        rc = ReservationController.get_grpc_stub("hub.noteworthy.im:8000")
        res = rc.reserve_domain(fqdn, auth_code)
        print(res)
        #rc = ReservationController.get_grpc_stub()
        #auth_code = rc.register(email).auth_code
        network_port = self._get_container_exposed_ports(container_id)
        lc.launch_launcher_taproot(fqdn, 'hub.noteworthy.im', auth_code, fqdn.replace('.', '-'), network_mode=f'container:{container_id}', target_port=network_port['port'])
        print('Done.')

    # TODO guard against collisions between aliases and plugin name
    connect.clicz_aliases = ['link']

    def _get_container_exposed_ports(self, container_id: str):
        container = self.docker.containers.get(container_id)
        network_id = container.attrs['NetworkSettings']['Networks']['bridge']['NetworkID']
        port = int(list(container.attrs['Config']['ExposedPorts'].keys())[0].split('/')[0])
        # TODO handle multiple ports exposed, ask user via interactive dialog
        return {'port': port, 'network_id': network_id}


Controller = LinkController
