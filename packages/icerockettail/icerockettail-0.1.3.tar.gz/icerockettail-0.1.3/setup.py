#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='icerockettail',
      version='0.1.3',
      description='equivalent of tail -f on icerocket twitter search results',
      author='Laurent Peuch',
      #long_description='',
      author_email='cortex@worlddomination.be',
      url='https://github.com/psycojoker/icerockettail',
      install_requires=['requests', 'argh', 'BeautifulSoup4'],
      packages=[],
      license= 'MIT',
      scripts=['icerockettail'],
      keywords='icerocket twitter tail',
     )
