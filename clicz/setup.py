from setuptools import setup, find_namespace_packages

setup(name='clicz',
      url="https://decentralabs.io",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=['clicz'],
      # namespace packages wont work without zip_safe=False
      zip_safe=False
      )