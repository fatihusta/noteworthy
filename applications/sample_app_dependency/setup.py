from setuptools import setup, find_namespace_packages

setup(name='noteworthy-sample-app-dependency',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={'notectl.plugins':  'sample_app_dependency = noteworthy.sample_app_dependency'},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[]
      )
