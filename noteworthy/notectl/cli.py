import argparse
import sys


from noteworthy.notectl import NoteworthyController


class NoteworthyCLI:
    def __init__(self):
        self.controller = NoteworthyController()

    def dispatch(self):
        '''Translate cli arguments into method invocations passing everything
        we get from argparse as kwargs.
        '''
        # use root arg_parser here
        self.arg_parser = argparse.ArgumentParser()
        self.arg_parser.add_argument('-d', '--debug', action='store_true', help='enable debugging output')
        self.args = self.arg_parser.parse_known_args()[0]
        if self.args.debug:
            print(self.args)
        if sys.argv[1] in self.controller.plugins:
            self.arg_parser.add_argument(sys.argv[1], help='Command')
            self.arg_parser.add_argument('action', nargs='?', default=None)
            self.args = self.arg_parser.parse_known_args()[0]
            plugin = self.args.command
            command = self.args.action
            if not command:
                command = 'help'
            controller_cls = self.controller.plugins[plugin].Controller
            controller_cls._setup_argparse(self.arg_parser)
            # use plugin arg parser to parse args
            plugin_args = controller_cls.sub_parser.parse_known_args(sys.argv[3:])[0]
            controller_cls.args = sys.argv[3:]
            plugin_controller = controller_cls()
            plugin_controller.args = plugin_args
            if self.args.debug:
                print(plugin_args)
            NoteworthyCLI._invoke_method(plugin_controller, command, plugin_args.__dict__)
            sys.exit(0)
        NoteworthyCLI._invoke_method(self.controller, sys.argv[1], self.args.__dict__)


    @staticmethod
    def _invoke_method(target, method, kwargs):
        method = getattr(target, method)
        method(**kwargs)