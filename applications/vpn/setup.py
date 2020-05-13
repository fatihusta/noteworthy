from setuptools import setup, find_namespace_packages
from setuptools.command.install import install

class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
          super().run()
          self.spawn(['./install.sh'])

setup(name='noteworthy-vpn',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={'notectl.plugins':  'vpn = noteworthy.vpn'},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[],
      cmdclass={
            'install': CustomInstallCommand,
      },
      include_package_data=True
      )
