import argparse
import sys
import yaml
import shutil
from pathlib import Path
from noteworthy.notectl.plugins import NoteworthyPlugin


class PackageController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-package'
    APP_DIR = '/opt/noteworthy/notectl/applications'
    PLUGIN_DIR = '/opt/noteworthy/notectl/plugins'
    BUILD_DIR = '/opt/noteworthy/build'

    def __init__(self):
        pass

    def package(self, **kwargs):
        app_name = kwargs['app_name']
        version = kwargs['version'] or 'DEV'
        print(f'Packaging {app_name} version {version}...')
        build_dir = f'{self.BUILD_DIR}/{app_name}/{version}'
        collect_dir = f'{build_dir}/tmp'
        print(f'Cleaning {build_dir}...')
        Path(collect_dir).mkdir(parents=True, exist_ok=True)
        shutil.rmtree(build_dir)
        Path(collect_dir).mkdir(parents=True, exist_ok=True)
        print('done.')
        collected_modules = set()
        print('Collecting modules...')
        self._collect_package(app_name, collect_dir, collected_modules)
        print('Zipping package...')
        shutil.make_archive(
            f'{build_dir}/package', 'gztar', collect_dir)
        print('done.')
        print('Cleaning up temp directories...')
        shutil.rmtree(collect_dir)
        print('done.')
        print(f'App packaged at build/{app_name}/{version}/package.tar.gz')

    def _collect_package(self, app_name, build_dir, collected_modules):
        package_path = f'{self.APP_DIR}/{app_name}'
        # get manifest for package
        manifest_path = f'{package_path}/build-manifest.yaml'
        print(f'Loading manifest {manifest_path} ...')
        try:
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)
        except FileNotFoundError:
            sys.exit(
                f'No manifest found for app \'{app_name}\' at {manifest_path}')
        except Exception as e:
            print(f'Unexpected Error reading {manifest_path}', file=sys.stderr)
            raise

        print('done.')
        # copy self
        print(f'Collecting {app_name}...')
        shutil.copytree(package_path, f'{build_dir}/{app_name}')
        collected_modules.add(app_name)
        print('done.')

        # collect bundled packages
        for package in manifest.get('bundle', []):
            if package not in collected_modules:
                self._collect_package(package, build_dir, collected_modules)

        # collect plugins
        for plugin in manifest.get('plugins', []):
            if plugin not in collected_modules:
                self._collect_plugin(plugin, build_dir, collected_modules)

    def _collect_plugin(self, plugin_name, build_dir, collected_modules):
        plugin_path = f'{self.PLUGIN_DIR}/{plugin_name}'
        print(f'Collecting {plugin_name}...')
        shutil.copytree(plugin_path, f'{build_dir}/{plugin_name}')
        collected_modules.add(plugin_name)
        print('done.')

    @classmethod
    def _setup_argparse(cls, arg_parser):
        super()._setup_argparse(arg_parser)
        cls.sub_parser = argparse.ArgumentParser(conflict_handler='resolve',
                                                 usage='notectl package ')
        cls.sub_parser.add_argument('app_name', help='name of application')
        cls.sub_parser.add_argument(
            'version', nargs='?', help='version of application')


Controller = PackageController
