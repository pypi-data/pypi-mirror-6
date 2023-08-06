#!/usr/bin/env python

from distutils.core import setup

import propdb

setup(name='propdb',
      version=propdb.__version__,
      description='Property Bag Style Database',
      author=propdb.__author__,
      author_email=propdb.__email__,
      url='https://pypi.python.org/pypi/propdb',
      packages=['propdb'],
      long_description=open('README').read(),
      license=propdb.__license__,
     )