#!/usr/bin/env python3

import sys
import pathlib

app_name = str.lower(sys.argv[1])
pathlib.Path(
    f'{app_name}/noteworthy/{app_name}').mkdir(parents=True, exist_ok=True)

module_name = 'noteworthy-' + app_name.replace('_', '-')
SETUP_TEXT = f'''from setuptools import setup, find_namespace_packages

setup(name='{module_name}',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={{'notectl.plugins':  '{app_name} = noteworthy.{app_name}'}},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[]
      )
'''
with open(f'{app_name}/setup.py', 'w') as f:
    f.write(SETUP_TEXT)

controller_name = ''.join([word.title() for word in app_name.split('_')])
INIT_TEXT = f'''from noteworthy.notectl.plugins import NoteworthyPlugin

@grpc_controller
class {controller_name}Controller(NoteworthyPlugin):

    app_name = '{module_name}'

    def __init__(self):
        pass

    @grpc_method
    def check_health(self, **kargs):
        return 'OK'


Controller = {controller_name}Controller
'''
with open(f'{app_name}/noteworthy/{app_name}/__init__.py', 'w') as f:
    f.write(INIT_TEXT)
