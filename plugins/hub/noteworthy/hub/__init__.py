from noteworthy.notectl.plugins import NoteworthyPlugin

import docker

from grpcz import grpc_controller, grpc_method

from noteworthy.hub.proto.messages_pb2 import ReservationRequest, ReservationResponse

@grpc_controller
class HubController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-hub'
    DJANGO_APP_MODULE = 'noteworthy.hub.api'

    def __init__(self):
        self.docker = docker.from_env()

    @grpc_method(ReservationRequest, ReservationResponse)
    def reserve_domain(self, domain: str, pub_key: str, auth_code: str):
        volumes = []
        app_env = {'NOTEWORTHY_ROLE': 'link'}
        ports = {'18521/udp': None}
        container_name = domain.replace('.', '-')
        self.docker.containers.run(f'noteworthy-launcher:DEV',
        tty=True,
        cap_add=['NET_ADMIN'],
        network='noteworthy',
        stdin_open=True,
        name=f'{container_name}-link',
        #auto_remove=True,
        volumes=volumes,
        ports=ports,
        detach=True,
        environment=app_env)
        return {"endpoint": '10.0.0.1', "port":1557, "ip_assignment":"10.0.0.2"}


Controller = HubController
