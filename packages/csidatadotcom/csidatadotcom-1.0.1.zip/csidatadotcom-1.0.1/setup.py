# Created by James Darabi (mail@jdarabi.com)
# License: GNU LGPL

import os
import sys

from distutils.core import setup

from csidatadotcom import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = 'csidatadotcom',
  version = __version__,
  description = 'Retrieve end-of-day market data from www.csidata.com',
  long_description = '\n' + read('README.rst'),
  author = 'James Darabi',
  author_email = 'mail@jdarabi.com',
  url = 'https://bitbucket.org/jamesdarabi/csidatadotcom',
  py_modules = ['csidatadotcom']
)