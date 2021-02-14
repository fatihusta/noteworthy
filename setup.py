from setuptools import setup, find_namespace_packages

setup(name='noteworthy',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={
          'console_scripts': [
              'notectl = noteworthy.notectl.__main__:main'
          ],
          'notectl.entrypoint': 'notectl = noteworthy.notectl'
      },
      install_requires=['PyYAML', 'docker'],
      # namespace packages wont work without zip_safe=False
      zip_safe=False
      )