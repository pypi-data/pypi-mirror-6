#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

if os.path.isfile("README.md"):
    with open('README.md') as file:
        long_description = file.read()

setup(name='python-linkfire',
      version='0.1',
      description='Python linkfire.com API',
      author='Lorenzo Setale ( http://who.is.lorenzo.setale.me/? )',
      author_email='koalalorenzo@gmail.com',
      url='https://github.com/koalalorenzo/python-linkfire',
      packages=['linkfire'],
      install_requires=['requests'],
     )
