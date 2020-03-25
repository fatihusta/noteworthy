#!/usr/bin/env python3

import sys
import pathlib

plugin_name = str.lower(sys.argv[1])
pathlib.Path(
    f'{plugin_name}/noteworthy/{plugin_name}').mkdir(parents=True, exist_ok=True)

module_name = 'noteworthy-' + plugin_name.replace('_', '-')
SETUP_TEXT = f'''from setuptools import setup, find_namespace_packages

setup(name='{module_name}',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={{'notectl.plugins':  '{plugin_name} = noteworthy.{plugin_name}'}},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[]
      )
'''
with open(f'{plugin_name}/setup.py', 'w') as f:
    f.write(SETUP_TEXT)

controller_name = ''.join([word.title() for word in plugin_name.split('_')])
INIT_TEXT = f'''from noteworthy.notectl.plugins import NoteworthyPlugin


class {controller_name}Controller(NoteworthyPlugin):

    PLUGIN_NAME = '{module_name}'

    def __init__(self):
        pass


Controller = {controller_name}Controller
'''
with open(f'{plugin_name}/noteworthy/{plugin_name}/__init__.py', 'w') as f:
    f.write(INIT_TEXT)