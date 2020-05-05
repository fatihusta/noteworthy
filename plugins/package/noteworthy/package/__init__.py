import os
import argparse
import sys
import yaml
import shutil
from subprocess import check_output, STDOUT, CalledProcessError
from pathlib import Path
from noteworthy.notectl.plugins import NoteworthyPlugin


class PackageController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-package'
    APP_DIR = '/opt/noteworthy/applications'
    PLUGIN_DIR = '/opt/noteworthy/plugins'
    BUILD_DIR = '/opt/noteworthy/dist/build'
    SCRATCH_DIR = '/opt/noteworthy/dist/scratch'

    def __init__(self):
        pass

    def package(self, **kwargs):
        app_name = kwargs['app_name']
        package_path = f'{self.APP_DIR}/{app_name}'
        version = kwargs['version'] or 'DEV'
        package_name = f'{app_name}-{version}'
        print(f'Packaging {app_name} version {version}...')
        try:
            # make sure scratch dir is clean
            shutil.rmtree(self.SCRATCH_DIR)
        except:
            pass
        build_dir = f'{self.BUILD_DIR}/{app_name}'
        collect_dir = f'{self.SCRATCH_DIR}/{app_name}/{version}'
        Path(collect_dir).mkdir(parents=True, exist_ok=True)
        Path(build_dir).mkdir(parents=True, exist_ok=True)
        print('done.')
        collected_modules = set()
        print('Collecting modules...')
        self._collect_package(app_name, collect_dir, collected_modules)
        shutil.copyfile(os.path.join(package_path, 'app.yaml'), os.path.join(self.SCRATCH_DIR, f'{app_name}/{version}/app.yaml'))
        print('Zipping package...')
        shutil.make_archive(
            f'{build_dir}/{package_name}', 'gztar', self.SCRATCH_DIR)
        print('done.')
        print('Cleaning up temp directories...')
        shutil.rmtree(self.SCRATCH_DIR)
        print('done.')
        print(
            f'App packaged at {self.BUILD_DIR}/{app_name}/{package_name}.tar.gz')

    def _collect_package(self, app_name, build_dir, collected_modules):
        package_path = f'{self.APP_DIR}/{app_name}'
        # get manifest for package
        manifest_path = f'{package_path}/app.yaml'
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
        plugin_build_path = f'{build_dir}/{plugin_name}'
        shutil.copytree(plugin_path, plugin_build_path)
        try:
            check_output([f'{plugin_build_path}/build.sh'], stderr=STDOUT)
        except CalledProcessError as exc:
            sys.exit(exc.output)
        except FileNotFoundError:
            pass
        except:
            raise
        collected_modules.add(plugin_name)
        print('done.')

Controller = PackageController
