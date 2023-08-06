#!/usr/bin/env python

from setuptools import setup

setup(name='SimpleFramework',
      version='1.2.5',
      description='Simple Web Framework by Simplendi',
      author='Simplendi',
      author_email='info@simplendi.com',
      url='https://github.com/Simplendi/SimpleFramework',
      packages=['framework', 'framework.constants', 'framework.email', 'framework.httpexceptions', 'framework.util'],
      )
