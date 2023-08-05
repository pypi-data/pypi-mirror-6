#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='bb',
      version='0.1',
      description='bitbucket simple CLI interface',
      author='Laurent Peuch',
      #long_description='',
      author_email='cortex@worlddomination.be',
      url='http://',
      install_requires=['argh', 'bitbucket-api'],
      packages=[],
      license= 'MIT',
      scripts=['bb'],
      keywords='bitbucket cli interface',
     )
