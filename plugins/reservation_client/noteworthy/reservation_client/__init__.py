from grpcz import grpc_controller, grpc_method
from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.reservation_client.proto.messages_pb2 import (
    ReservationRequest, ReservationResponse, LinkRequest, LinkResponse)

@grpc_controller
class ReservationController(NoteworthyPlugin):

    PLUGIN_NAME = 'reservation_client'

    @grpc_method(ReservationRequest, ReservationResponse)
    def reserve_domain(self, domain: str, auth_code: str):
        pass

    @grpc_method(LinkRequest, LinkResponse)
    def create_link(self, domain: str, pub_key: str, auth_code: str):
        pass


Controller = ReservationController
