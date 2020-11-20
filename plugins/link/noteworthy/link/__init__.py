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
    def connect(self, protocol: str, container_id: str=None, host_port: int=None, int_port: int=None, fqdn: str=None, link_id: str=None, hub_fqdn: str = 'link.decentralabs.io'):
        '''Connect to a local container or host port via Noteworthy link
        ---
        Args:
            protocol: Supported protocols are ['https']
            container_id: ID of the container that you would like to link, ports will be automatically introspected via Docker's EXPOSE semantic
            host_port: Port on the host to link
            int_port: Port inside container to link
            fqdn: Fully-qualified domain name at which the service will be available
            link_id: ID of the remote link endpoint
            hub_fqdn: Fully-qualified domain name of hub (defaults to link.decentralabs.io)
        '''
        from noteworthy.launcher import LauncherController
        lc = LauncherController()
        #email = input('Please enter your email address: ')
        auth_code = input('Please enter auth_code: ')
        from noteworthy.reservation_client import ReservationController
        rc = ReservationController.get_grpc_stub(f"{hub_fqdn}:8000")
        res = rc.reserve_domain(fqdn, auth_code)
        print(res)
        #rc = ReservationController.get_grpc_stub()
        #auth_code = rc.register(email).auth_code
        lc.launch_launcher_taproot(fqdn, hub_fqdn, auth_code, fqdn.replace('.', '-'), network_mode=f'container:{container_id}', target_port=int(int_port))
        print('Done.')

    # TODO guard against collisions between aliases and plugin name
    connect.clicz_aliases = ['link']

    def _get_container_exposed_ports(self, container_id: str):
        container = self.docker.containers.get(container_id)
        port = int(list(container.attrs['Config']['ExposedPorts'].keys())[0].split('/')[0])
        # TODO handle multiple ports exposed, ask user via interactive dialog
        return {'port': port }


Controller = LinkController
