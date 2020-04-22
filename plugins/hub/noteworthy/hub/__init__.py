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
        self._validate_reservation(domain, auth_code)
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
        restart_policy={"Name": "always"})
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

    def _validate_reservation(self, domain, auth_code):
        if not auth_code:
            raise Exception('auth_code is required to reserve domain.')
        self._setup_django()
        from noteworthy.hub.api import models
        user = models.BetaUser.objects.get(beta_key=auth_code)
        has_user_reserved = models.BetaReservation.objects.filter(beta_user=user).exists()
        if has_user_reserved:
            user_res = models.BetaReservation.objects.get(beta_user=user)
            user_domain = user_res.domain
            if domain != user_domain:
                raise Exception(f'User, {user}, has already reserved a different domain.')
        else:
            is_domain_taken = models.BetaReservation.objects.filter(domain=domain).exists()
            if is_domain_taken:
                raise Exception(f'Domain, {domain}, is already reserved.')
            models.BetaReservation.objects.create(domain=domain, beta_user=user)
        '''
        perhaps this code should instead return a response that can be used
        by the client application making the reservation request
        TODO: what's best practice for grpc error stuffs?
        '''


    def _setup_django(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'noteworthy.http_service.rest_api.rest_api.settings'
        import django
        django.setup()
        return django
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
