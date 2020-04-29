from concurrent import futures
import functools
import inspect
import sys

import grpc


import grpcz.grpcz_pb2 as grpcz_pb2
import grpcz.grpcz_pb2_grpc as grpcz_pb2_grpc


class Dispatcher(grpcz_pb2_grpc.DispatchServicer):
    def call(self, message, context):
        ok, msg, response = self.grpcz_server._call(message.module_path, message.request)
        return grpcz_pb2.GRPCZResponse(ok=ok, result=msg,
                response=grpcz_pb2.Any(value=response.SerializeToString()))


class GRPCZServer:

    registered_modules = {}

    def register_controller(self, controller):
        members = inspect.getmembers(controller, predicate=inspect.ismethod)
        for member in members:
            if hasattr(member[1], 'grpc_method'):
                module_path = f'{controller.__class__.__name__}.{member[0]}'
                self.registered_modules[module_path] = member[1]

    def _call(self, module_path, any_request, **kwargs):
        ok = False
        msg = ''
        response = grpcz_pb2.Any()
        if module_path not in self.registered_modules:
            msg = f"Method or function '{module_path}' is not registered."
            return ok, msg, response
        else:
            try:
                method = self.registered_modules[module_path]
                request = method.request().FromString(any_request.value)
                args = [ getattr(request, field.name) for field in method.request.DESCRIPTOR.fields ]
                result = self.registered_modules[module_path](*args, **kwargs)
                response = method.response(**result)
                ok = True
            except Exception as e:
                msg = e
        return ok, msg, response

    def start(self, bind_to='0.0.0.0:8000'):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        dispatcher = Dispatcher()
        dispatcher.grpcz_server = self
        grpcz_pb2_grpc.add_DispatchServicer_to_server(dispatcher, self.server)
        self.server.add_insecure_port(bind_to)
        self.server.start()
        print(f'grpcz server started on {bind_to}')
        self.server.wait_for_termination()


def rpc_request(endpoint, module_path, req_type, resp_type, *args, **kwargs):
    '''
    Invoke the Python function at `module_path` on a remote host via gRPC.
    endpoint: ip or hostname of remote host
    module_path: ie 'RemoteController.do_something'
    req_type: Protobuf message representing request
    resp_type: Protobuf message representing response
    '''
    # TODO move channel to stub controller so we can reuse connection
    channel = grpc.insecure_channel(endpoint)
    stub = grpcz_pb2_grpc.DispatchStub(channel)
    if len(req_type.DESCRIPTOR.fields) != len(args):
        raise Exception('Incorrect argument count for RPC invocation.'
                        'Pass None for optional args') # WTF IDK
    fields = [ field.name for field in req_type.DESCRIPTOR.fields ]
    request = req_type(**dict(zip(fields, args)))
    any_request = grpcz_pb2.Any(value=request.SerializeToString())
    result = stub.call(grpcz_pb2.GRPCZRequest(module_path=module_path, request=any_request))
    response = resp_type().FromString(result.response.value)
    return response


def grpc_method(request, response):
    '''
    Controller methods must be decorated with this function in order to be 
    exposed via gRPC. We do this by annotating methods with the truthy boolean property `grpc_method`
    '''
    def grpc_method_wrapper(func):
        func.grpc_method = True
        func.request = request
        func.response = response
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped
    return grpc_method_wrapper


def grpc_controller(cls):
    # annotate the controller as a grpc enabled controller
    cls.grpc_controller = True

    rpc_calls = {}
    for name, method in cls.__dict__.items():
        if hasattr(method, 'grpc_method'):
            rpc_calls[name] = method

    def wrapper_factory(endpoint, method, module_path):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return rpc_request(endpoint, module_path, method.request,
                    method.response, *args[1:], **kwargs)
        return wrapper

    @staticmethod
    def get_grpc_stub(endpoint='localhost:8000'):
        # by-pass __init__()?
        controller_stub = _get_grpc_controller_stub(cls)
        stub = controller_stub()
        # create the client by iterating over rpc_calls
        for name, method in rpc_calls.items():
            setattr(controller_stub, name, wrapper_factory(endpoint, method, f'{cls.__name__}.{name}'))
        return stub
    cls.get_grpc_stub = get_grpc_stub
    return cls


def _get_grpc_controller_stub(controller_cls):
    '''Copy the Controller class so we can modify its methods
    without side effects.
    '''
    class GRPCControllerStub(controller_cls):
        pass
    GRPCControllerStub.__name__ = f'{controller_cls.__name__}Stub'
    GRPCControllerStub.__qualname__ = f'{controller_cls.__name__}Stub'
    return GRPCControllerStub