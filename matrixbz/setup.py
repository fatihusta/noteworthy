from setuptools import setup, find_packages

setup(name='matrixbz',
      url="https://decentralabs.io",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
        'matrix-nio',
        'requests',
        'Pillow'
      ]
     )
