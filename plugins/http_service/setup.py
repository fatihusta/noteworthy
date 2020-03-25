from setuptools import setup, find_namespace_packages

setup(name='noteworthy-http-service',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={'notectl.plugins':  'http_service = noteworthy.http_service'},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[]
      )
