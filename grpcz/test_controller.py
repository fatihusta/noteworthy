from grpcz import grpc_method, grpc_controller

@grpc_controller
class TestController:
    pass

    # @grpc_method
    # def sayHello(self, name, *args, **kwargs):
    #     return f'Hello {name}'

    # @grpc_method
    # def raiseIt(self, *args, **kwargs):
    #     raise Exception('Some broken shit')

    