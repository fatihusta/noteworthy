from setuptools import setup, find_packages

setup(name='procz',
      url="https://decentralabs.io",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=['procz'],
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[
        'python-daemon==2.2.4',
        'lockfile==0.12.2'
      ]
     )
