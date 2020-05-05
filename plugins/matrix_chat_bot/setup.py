from setuptools import setup, find_namespace_packages

setup(name='noteworthy-matrix-chat-bot',
      url="https://noteworthy.im",
      author_email="hi@decentralabs.io",
      version='0.0.1',
      packages=find_namespace_packages(include=['noteworthy.*']),
      entry_points={'notectl.plugins':  'matrix_chat_bot = noteworthy.matrix_chat_bot'},
      # namespace packages wont work without zip_safe=False
      zip_safe=False,
      install_requires=[
        'matrix-nio==0.10.0'
      ],
      include_package_data=True,
      )
