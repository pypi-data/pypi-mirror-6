#!/usr/bin/env python

import re
#from dput import __appname__
from setuptools import setup

#long_description = open('README.md').read()
long_description = '''dput-ng
-------

dput-ng is a from-scratch refresh of the old `dput(1)` command. This tool is
used (at some point) to aid with the act of uploading a package to an archive.

dput-ng aims to be compatible with the old `dput(1)` config files, while
adding additional features for better sanity checking, and designed in an
extensible way.

Check the [docs](http://dput.rtfd.org) for more on topics that might
interest you.
'''
#cur = open('debian/changelog', 'r').readline().strip()
#pobj = re.findall(
#    r'(?P<src>.*) \((?P<version>.*)\) (?P<suite>.*); .*',
#    cur
#)[0]
#src, version, suite = pobj
# Yes, I'm sorry, world. I'm sorry.

setup(
    name='dput',
    version='1.6',
    packages=[
        'dput',
        'dput.hooks',
        'dput.configs',
        'dput.commands',
        'dput.commands.contrib',
        'dput.uploaders',
        'dput.interfaces',
    ],
    install_requires=['python-debian==0.1.21-nmu2'],
    author="dput authors",
    author_email="paultag@debian.org",
    long_description=long_description,
    description='dput-ng -- like dput, but better',
    license="GPL-2+",
    url="",
    platforms=['any']
)
