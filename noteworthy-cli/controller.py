import sys
from noteworthy.cli import NoteworthyCLI, cli_method

class TestController:
    '''This docstring will describe this controller in the CLI.
    '''

    command_name = 'test'

    @cli_method
    def say_hello(self, name: str, age: int):
        '''\
        Say hello to someone.
        ---
        Args:
            name: This is your name
            age: Hello world
        '''
        print(f'Hello, {name}. You are {age} years old!')



if __name__ == '__main__':
    cli = NoteworthyCLI()
    cli.register_controller(TestController)
    cli.dispatch(sys.argv)