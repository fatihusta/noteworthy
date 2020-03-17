from setuptools import setup

setup(name='notectl',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=['notectl'],
      entry_points={
          'console_scripts': [
              'notectl = notectl.__main__:main'
          ]
      },
      )