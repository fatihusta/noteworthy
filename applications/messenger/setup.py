from setuptools import setup, find_namespace_packages

setup(name='noteworthy-messenger',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={'notectl.plugins':  'messenger = noteworthy.messenger'},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      # matrix-synapse moved to requirements.txt for Dockerfile cache gainz
      #install_requires=['PyJWT==1.7.1'],
      include_package_data=True
      )
