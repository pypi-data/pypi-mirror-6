#!/usr/bin/env python

# To upload a version to PyPI, run:
#
#    python setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python setup.py register

from distutils.core import setup
import os

VERSION = '1.0.0'

# Auto generate a __version__ package for the package to import
with open(os.path.join('basic_crypto', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n"%VERSION)
    
setup(name='basic_crypto',
      version=VERSION,
      description='Wrapper around PyCrypto providing basic symmetric key encryption with AES in CFB mode.',
      author='Chris Billington',
      author_email='chrisjbillington@gmail.com',
      url='https://bitbucket.org/cbillington/basic_crypto/',
      license="BSD",
      packages=['basic_crypto']
     )
