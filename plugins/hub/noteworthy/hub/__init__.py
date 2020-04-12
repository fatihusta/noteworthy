import os
from noteworthy.notectl.plugins import NoteworthyPlugin

import docker

from grpcz import grpc_controller, grpc_method

from noteworthy.hub.proto.messages_pb2 import (ReservationRequest, ReservationResponse)
from noteworthy.wireguard import wg

@grpc_controller
class HubController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-hub'
    DJANGO_APP_MODULE = 'noteworthy.hub.api'

    def __init__(self):
        self.docker = docker.from_env()

    @grpc_method(ReservationRequest, ReservationResponse)
    def reserve_domain(self, domain: str, pub_key: str, auth_code: str):
        from noteworthy.nginx import NginxController
        volumes = []
        app_env = {
                   'NOTEWORTHY_ROLE': 'link',
                   'NOTEWORTHY_DOMAIN': domain,
                   'TAPROOT_PUBKEY': pub_key
                   }
        ports = {
                    '18521/udp': None, # random wireguard port
                }
        container_name = domain.replace('.', '-')
        link_node = self.docker.containers.run(f'noteworthy-launcher:DEV',
        tty=True,
        cap_add=['NET_ADMIN'],
        network='noteworthy',
        stdin_open=True,
        name=f'{container_name}-link',
        #auto_remove=True,
        volumes=volumes,
        ports=ports,
        detach=True,
        environment=app_env,
        restart_policy={"Name": "always", "MaximumRetryCount": 5})
        link_node = self.docker.containers.get(link_node.attrs['Id'])
        link_wg_pubkey = link_node.exec_run('notectl wireguard pubkey').output.decode().strip()
        link_wg_port = link_node.attrs['NetworkSettings']['Ports']['18521/udp'][0]['HostPort']
        link_ip = link_node.attrs['NetworkSettings']['Networks']['noteworthy']['IPAddress']
        nc = NginxController()
        # cant do this here
        # need to write config atomically with a lock
        # TODO fix
        nc.add_tls_stream_backend(domain, link_ip)
        nc.set_http_proxy_pass(container_name, f'.{domain}', link_ip)
        return {
                "link_wg_endpoint": f"{os.environ['NOTEWORTHY_HUB']}:{link_wg_port}",
                "link_wg_pubkey": link_wg_pubkey
               }


    # @grpc_method(PeeringRequest, PeeringResponse)
    # def add_peer(self, wg_pubkey: str, auth_token: str):
    #     # TODO make this role check a decorator
    #     # TODO limit the number of peers
    #     if os.environ['NOTEWORTHY_ROLE'] != 'link':
    #         raise Exception('RPC method add_peer only supported by link nodes')
    #     hub_wg_pubkey = wg.pubkey('/opt/noteworthy/.wireguard/wg.key')
    #     wg.add_peer('wg0', wg_pubkey, '10.0.0.2/32')
    #     return {'hub_wg_pubkey': hub_wg_pubkey, 'hub_wg_endpoint': ''}

Controller = HubController
