#!/usr/bin/env python

from distutils.core import setup
setup(name='python-spaceapi',
    version='0.1.2',
    description='Pythonic interface to the SpaceAPI',
    author='Torrie Fischer',
    author_email='tdfischer@hackerbots.net',
    url='http://github.com/tdfischer/python-spaceapi',
    py_modules=['spaceapi'],
    requires=['requests', 'dnspython', 'beautifulsoup4'],
)
