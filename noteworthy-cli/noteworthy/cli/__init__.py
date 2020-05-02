#!/usr/bin/env python
import argparse
import sys
import functools
import inspect
import yaml


class CommandArgParser(argparse.ArgumentParser):


    def print_help(self, *args, **kwargs):
        super().print_help(*args, **kwargs)
        print('''
Get command help: notectl command -h
------------------------------------
Available commands:

network     Create and manage your networks
site        Create and manage websites

        ''')

class NoteworthyCLI:

    
    def __init__(self):
        '''
        Register any controller that has the property `enable_cli=True`
        '''
        self.registered_controllers = {}
        self.controller_instances = {}
        self.proxy_commands = {}
        self.base_parser = argparse.ArgumentParser()
        self.sub_parser = self.base_parser.add_subparsers(title='commands', dest='command', required=True)

    def _build_arg_parser(self, arg_parser, method):
        '''
        '''
        method_name = method.__qualname__.split('.', 1)[1]
        argspec = inspect.getfullargspec(method.__wrapped__)
        static_method = False
        if argspec.args[0] not in ['cls', 'self']:
            static_method = True
        docstring = inspect.getdoc(method).split('---', 1)[1]
        if not docstring:
            print(f'####WARNING######: No docstring defined for {method.__qualname__}')
            return [ arg for arg in argv if not arg.startswith('--') ]
        else:
            # Parse YAML based docstring to auto-generate ArgParser with nice help!
            argspec.args.reverse()
            defaults = dict(zip(argspec.args, argspec.defaults)) if argspec.defaults else []
            try:
                doc_yaml = yaml.safe_load(docstring)
            except:
                raise Exception('Unable to parse docstring; not valid YAML.')
            if not isinstance(doc_yaml, dict) or 'args' not in [key.lower() for key in [*doc_yaml.keys()]]:
                raise Exception('Docstring YAML missing Args key.')
            for arg, help in doc_yaml['Args'].items():
                if not isinstance(help, str):
                    raise Exception(f'Argument description for {arg} must be of type str.')
                if arg in defaults:
                    arg_parser.add_argument(f'--{arg}', default=defaults[arg], help=help)
                else:
                    arg_parser.add_argument(f'{arg}', help=help)
            argspec.args.reverse()
            start_arg_idx = 0 if static_method else 1
            # make sure docstring YAML specifies all arguments defined in argspec
            missing_args = list(set(argspec.args).difference(set([*doc_yaml['Args'].keys()])))
            [missing_args.remove(x) for x in ['self', 'cls'] if x in missing_args]
            if missing_args:
                raise Exception(f"Docstring for {method.__qualname__} missing args: {', '.join(missing_args)}")
            return
            parsed_args = arg_parser.parse_args(argv)
            return [ getattr(parsed_args, key) for key in argspec.args[start_arg_idx:] ]
    
    def dispatch(self, argv):
        '''Dispatch a CLI invocation to a controller.
        First, we fetch the controller class from the map of registered controllers (method wrapped wit @cli_method)
        then we construct an ArgParser based on the Docstring 
        '''

        #self.base_parser.add_argument('action', help="Method on controller to invoke")
        #args = self.base_parser.parse_args(argv[1:3])
        args = self.base_parser.parse_args()
        controller_name = args.command
        #method_name = args.action
        if controller_name not in self.registered_controllers:
            raise Exception(f'Subcommand {controller_name} not found')
        controller = self.registered_controllers[controller_name]
        controller_instance = controller()
        self.controller_instances[controller_name] = controller_instance
        if not hasattr(controller_instance, method_name):
            raise Exception(f'Controller {controller_name} has no CLI method {method_name}')
        method = getattr(controller_instance, method_name)
        if not hasattr(method, 'cli_method'):
            raise Exception(f'Method {method.__qualname__} not registered for CLI invocation.'
                             ' Wrap method with @cli_method to expose via CLI.')
        method_args = self._build_arg_parser(method, argv[3:])
        return method(*method_args)

    def register_controller(self, controller):
        self.registered_controllers[controller.command_name] = controller
        parser = self.sub_parser.add_parser(controller.command_name, help=inspect.getdoc(controller))
        sub_parser = parser.add_subparsers(title='commands', dest='command', required=True)
        controller.parsers = {}
        for name, prop in vars(controller).items():
            if hasattr(prop, 'cli_method'):
                method_description = inspect.getdoc(prop).split('---', 1)[0]
                method_parser = sub_parser.add_parser(name, help=method_description)
                controller.parsers[name] = method_parser
                self._build_arg_parser(method_parser, getattr(controller, name))
                self.base_parser.parse_args()
                sys.exit(1)
                import pdb; pdb.set_trace()
                pass


def cli_method(func=None, parse_docstring=True):
    if not func:
        return functools.partial(cli_method, parse_docstring=parse_docstring)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return res
    wrapper.parse_docstring = True if parse_docstring else False
    wrapper.cli_method = True
    return wrapper
