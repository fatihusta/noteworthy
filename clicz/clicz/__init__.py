#!/usr/bin/env python
import argparse
import sys
import functools
import inspect
import yaml
import pkg_resources


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
        # TODO figure out if we can get default subcommands working
        https://stackoverflow.com/questions/6365601/default-sub-command-or-handling-no-sub-command-with-argparse
        '''
        self.registered_controllers = {}
        self.controller_instances = {}
        self.proxy_commands = {}
        self.base_parser = argparse.ArgumentParser()
        self.base_parser.add_argument('-d', '--debug', help='show debug output', action='store_true')
        self.sub_parser_factory = self.base_parser.add_subparsers(title='commands', dest='command', required=True)
        self._init_clicz()

    def _init_clicz(self):
        for entry_point in pkg_resources.iter_entry_points('clicz.entrypoint'):
            clicz_module = entry_point.load()
            clicz_module.clicz_entrypoint(self)

    def _build_arg_parser(self, arg_parser, method):
        '''
        '''
        argspec = inspect.getfullargspec(method.__wrapped__)
        static_method = False
        if argspec.args[0] not in ['cls', 'self']:
            static_method = True
        start_arg_idx = 0 if static_method else 1
        docstring = inspect.getdoc(method)
        if not docstring:
            raise Exception('YAML based Docstring are required for clicz methods.')
        else:
            # Parse YAML based docstring to auto-generate ArgParser with nice help!
            # if method is static and has arguments or not a static_method with more than 1 args
            if (static_method and len(argspec.args)) or (not static_method and len(argspec.args) > 1):
                docstring = docstring.split('---', 1)[1]
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
                # make sure docstring YAML specifies all arguments defined in argspec
                missing_args = list(set(argspec.args).difference(set([*doc_yaml['Args'].keys()])))
                [missing_args.remove(x) for x in ['self', 'cls'] if x in missing_args]
                if missing_args:
                    raise Exception(f"Docstring for {method.__qualname__} missing args: {', '.join(missing_args)}")
            def get_invocation_args(parsed_args):
                return [ getattr(parsed_args, key) for key in argspec.args[start_arg_idx:] ]
            return get_invocation_args

    def dispatch(self, argv=None):
        '''Dispatch a CLI invocation to a controller.
        First, we fetch the controller class from the map of registered controllers (method wrapped wit @cli_method)
        then we construct an ArgParser based on the Docstring 
        '''

        if not argv:
            argv = sys.argv
        args = self.base_parser.parse_args()
        controller_name = args.command
        controller_method = args.subcommand
        if controller_name not in self.registered_controllers:
            raise Exception(f'Subcommand {controller_name} not found')
        controller = self.registered_controllers[controller_name]
        controller_instance = controller()
        self.controller_instances[controller_name] = controller_instance
        if not hasattr(controller_instance, controller_method):
            raise Exception(f'Controller {controller_name} has no CLI method {controller_method}')
        method = getattr(controller_instance, controller_method)
        if not hasattr(method, 'cli_method'):
            raise Exception(f'Method {method.__qualname__} not registered for CLI invocation.'
                             ' Wrap method with @cli_method to expose via CLI.')
        return method(*method.get_invocation_args(args))

    def register_controller(self, controller):
        self.registered_controllers[controller.command_name] = controller
        self.parsers = {}
        self.parsers[controller.command_name] = self.sub_parser_factory.add_parser(controller.command_name, help=inspect.getdoc(controller))
        controller_sub_parser_factory = self.parsers[controller.command_name].add_subparsers(title='commands', dest='subcommand', required=True, metavar='command')
        controller.method_parsers = {}
        for name, prop in vars(controller).items():
            if hasattr(prop, 'cli_method'):
                try:
                    method_description = inspect.getdoc(prop).split('---', 1)[0]
                except KeyError:
                    method_description = inspect.getdoc(prop)
                if not method_description:
                    raise Exception('Docstrings are required.')
                controller.method_parsers[name] = controller_sub_parser_factory.add_parser(name, help=method_description)
                prop.get_invocation_args = self._build_arg_parser(controller.method_parsers[name], getattr(controller, name))
                #sys.exit(1)
                #import pdb; pdb.set_trace()
            


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
