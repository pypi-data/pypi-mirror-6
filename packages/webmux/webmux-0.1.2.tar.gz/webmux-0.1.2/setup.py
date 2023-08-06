#!/usr/bin/env python

# to distribute:
# python setup.py register sdist upload

from setuptools import setup

import sys
import os
import webmux

try:
    ## Remove 'MANIFEST' file to force
    ## distutils to recreate it.
    ## Only in "sdist" stage. Otherwise
    ## it makes life difficult to packagers.
    if sys.argv[1] == 'sdist':
        os.unlink('MANIFEST')
except:
    pass

setup(
    name='webmux',
    version=webmux.__version__,
    description='An open-source web based SSH terminal multiplexer',
    long_description='An open-source web based SSH terminal multiplexer',
    author='Ron Reiter (@ronreiter)',
    author_email='ron.reiter@gmail.com',
    url='http://github.com/ronreiter/webmux',
    packages=['webmux'],
    scripts=['webmuxd'],
    license='MIT'
)
