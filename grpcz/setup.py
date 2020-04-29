from setuptools import setup, find_packages

setup(name='grpcz',
      url="https://decentralabs.io",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=['grpcz'],
      # namespace packages wont work without zip_safe=False
      zip_safe=False
      )