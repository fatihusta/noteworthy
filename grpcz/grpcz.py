import functools
import inspect
import sys


import grpcz_pb2


class GRPCZServer:

    registered_modules = {}

    def register_controller(self, controller):
        members = inspect.getmembers(controller, predicate=inspect.ismethod)
        for member in members:
            if hasattr(member[1], 'grpcz'):
                module_path = f'{controller.__class__.__name__}.{member[0]}'
                self.registered_modules[module_path] = member[1]

    def _call(self, module_path, *args, **kwargs):
        ok = False
        if module_path not in self.registered_modules:
            result = f"Method or function '{module_path}' is not registered."
            return result, ok
        else:
            try:
                result = self.registered_modules[module_path](*args, **kwargs)
                ok = True
            except Exception as e:
                result = e
        return ok, result

def grpcz_method(func):
    '''
    Controller methods must be decorated with this function in order to be 
    exposed via gRPC. We do this by annotating methods with the truthy boolean property `grpcz`
    We also conditionally override the method in order to produce the stub version of the controller.
    '''
    func.grpcz = True
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        # crazy hack to get the class
        cls = vars(sys.modules[func.__module__])[func.__qualname__.split('.')[0]]
        if cls.grpcz_proxy:
            def proxy(*args, **kwargs):
                return grpcz_pb2.GRPCZRequest(module_path=func.__qualname__, args=args[1:])
            return proxy(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapped

class TestController:


    @grpcz_method
    def sayHello(self, name, *args, **kwargs):
        return f'Hello {name}'

    @grpcz_method
    def raiseIt(self, *args, **kwargs):
        raise Exception('Some broken shit')

    