import functools
import inspect


class GRPCZServer:

    registered_modules = {}

    def register_controller(self, controller):
        members = inspect.getmembers(controller, predicate=inspect.ismethod)
        for member in members:
            if hasattr(member[1], 'grpcz'):
                module_path = f'{controller.grpcz_module_prefix}.{member[0]}'
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
    func.grpcz = True
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped

class TestController:

    grpcz_module_prefix = 'tc'

    @grpcz_method
    def sayHello(self, name, *args, **kwargs):
        return f'Hello {name}'

    @grpcz_method
    def raiseIt(self, *args, **kwargs):
        raise Exception('Some broken shit')

    