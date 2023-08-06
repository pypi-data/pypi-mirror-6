#!/usr/bin/env python

# to distribute:
# python setup.py register sdist upload

from setuptools import setup
from pip.req import parse_requirements

import sys
import os
import webmux

install_reqs = parse_requirements('requirements.txt')

reqs = [str(ir.req) for ir in install_reqs]

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
    license='MIT',
    install_requires=reqs
)
