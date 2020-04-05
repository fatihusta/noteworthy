from noteworthy.notectl.plugins import NoteworthyPlugin

from grpcz import grpc_controller, grpc_method

from noteworthy.hub.proto.messages_pb2 import ReservationRequest, ReservationResponse

@grpc_controller
class HubController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-hub'
    DJANGO_APP_MODULE = 'noteworthy.hub.api'

    def __init__(self):
        pass

    @grpc_method(ReservationRequest, ReservationResponse)
    def reserve_domain(self, domain: str, pub_key: str, auth_code: str):
        return {"endpoint": '10.0.0.1', "port":1557, "ip_assignment":"10.0.0.2"}


Controller = HubController
