from setuptools import setup, find_packages

setup(name='matrixbz',
      url="https://decentralabs.io",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=['matrixbz'],
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[
        'matrix-nio==0.10.0'
      ]
     )
