import argparse
import sys


from noteworthy.notectl.dispatch import NoteworthyController


class NoteworthyCLI:
    def __init__(self):
        args = self.parse_args()
        print(args)
        self.controller = NoteworthyController()
        self.controller.dispatch(args)


    def parse_args(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('command', nargs='?', default='help')
        arg_parser.add_argument('action', nargs='?', default=None)
        arg_parser.add_argument('--no-cache', action="store_true")
        self.args = arg_parser.parse_known_args()
        if self.args[0].command == 'help':
            arg_parser.print_help()
            sys.exit(1)
        return self.args[0]

