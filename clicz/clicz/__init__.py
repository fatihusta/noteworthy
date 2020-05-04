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
Available commands:

network     Create and manage your networks
site        Create and manage websites

        ''')

class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class NoteworthyCLI:

    TOP_LEVEL_COMMANDS = ['install', 'uninstall', 'status', 'doctor', 'list_plugins']

    def __init__(self):
        '''
        Register any controller that has the property `enable_cli=True`
        # TODO figure out if we can get default subcommands working
        https://stackoverflow.com/questions/6365601/default-sub-command-or-handling-no-sub-command-with-argparse
        '''
        self.registered_controllers = {}
        self.controller_instances = {}
        self.parser = argparse.ArgumentParser()
        self.parser_subparser_factory = self.parser.add_subparsers(title='Management commands', dest='mgmt_command', metavar='')
        self.proxy_commands = {}
        self.base_parser = argparse.ArgumentParser()
        self.base_parser.add_argument('-d', '--debug', help='show debug output', action='store_true')
        self.base_parser._action_groups.append(self.parser._action_groups[-1])
        #print(self.parser.format_help())
        self.sub_parser_factory = self.base_parser.add_subparsers(title='Plugin commands', dest='command', required=True, metavar='')
        self._init_clicz()

    def _init_clicz(self):
        for entry_point in pkg_resources.iter_entry_points('clicz.entrypoint'):
            clicz_module = entry_point.load()
            clicz_module.clicz_entrypoint(self)

    def dispatch(self, argv=None):
        '''Dispatch a CLI invocation to a controller.
        First, we fetch the controller class from the map of registered controllers (methods wrapped wit @cli_method)
        then we construct an ArgParser based on the Docstring
        '''

        if sys.argv[1] in self.TOP_LEVEL_COMMANDS:
            self.parser.parse_known_args()
            sys.argv.insert(1, 'noteworthy')
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
        controller_sub_parser_factory = self.parsers[controller.command_name].add_subparsers(title='commands', dest='subcommand', required=True, metavar='')
        for name, method in vars(controller).items():
            if hasattr(method, 'cli_method'):
                self._build_method_argparser(controller_sub_parser_factory, name, method)

    def _build_method_argparser(self, sub_parser_factory, method_name, method):
        '''
        '''
        method_description = inspect.getdoc(method)
        if not method_description:
            raise Exception(f'Missing docstring for {Color.FAIL}{method.__qualname__}{Color.ENDC}. Docstrings are required.')
        try:
            method_description = inspect.getdoc(method).split('---', 1)[0]
        except KeyError:
            pass
        alias_parser = None
        if hasattr(method, 'clicz_aliases'):
            self.TOP_LEVEL_COMMANDS.extend(method.clicz_aliases)
            alias_parser = self.parser_subparser_factory.add_parser(method.clicz_aliases[0], help=method_description, description=method_description, aliases=method.clicz_aliases[1:])
            method_arg_parser = sub_parser_factory.add_parser(method_name, help=method_description, description=method_description, aliases=method.clicz_aliases)
        else:
            method_arg_parser = sub_parser_factory.add_parser(method_name, help=method_description, description=method_description)

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
                        method_arg_parser.add_argument(f'--{arg}', default=defaults[arg], help=help)
                        if alias_parser:
                            alias_parser.add_argument(f'--{arg}', default=defaults[arg], help=help)

                    else:
                        method_arg_parser.add_argument(f'{arg}', help=help)
                        if alias_parser:
                            alias_parser.add_argument(f'{arg}', help=help)
                argspec.args.reverse()
                # make sure docstring YAML spe  cifies all arguments defined in argspec
                missing_args = list(set(argspec.args).difference(set([*doc_yaml['Args'].keys()])))
                [missing_args.remove(x) for x in ['self', 'cls'] if x in missing_args]
                if missing_args:
                    raise Exception(f"Docstring for {Color.FAIL}{method.__qualname__}{Color.ENDC} missing args: {', '.join(missing_args)}")
            def get_invocation_args(parsed_args):
                return [ getattr(parsed_args, key) for key in argspec.args[start_arg_idx:] ]
            method.get_invocation_args = get_invocation_args

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
