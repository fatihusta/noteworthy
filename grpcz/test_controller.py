from grpcz import grpcz_method


class TestController:


    @grpcz_method
    def sayHello(self, name, *args, **kwargs):
        return f'Hello {name}'

    @grpcz_method
    def raiseIt(self, *args, **kwargs):
        raise Exception('Some broken shit')

    