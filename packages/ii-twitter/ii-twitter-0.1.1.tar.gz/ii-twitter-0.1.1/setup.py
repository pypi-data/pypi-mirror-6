#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='ii-twitter',
      version='0.1.1',
      description='shell command for a twitter bot intant to be used with ii',
      author='Laurent Peuch',
      #long_description='',
      author_email='cortex@worlddomination.be',
      url='https://github.com/psycojoker/ii-twitter',
      install_requires=['argh', 'tweepy', 'sh'],
      packages=[],
      license= 'MIT',
      scripts=['ii-twitter', 'ii-twitter-register'],
      keywords='twitter ii tail',
     )
