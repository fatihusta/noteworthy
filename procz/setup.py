from setuptools import setup, find_packages

setup(name='procz',
      url="https://decentralabs.io",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=['procz'],
      zip_safe=False,
      install_requires=[
        'python-daemon',
        'lockfile'
      ]
     )
