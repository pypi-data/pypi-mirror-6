#!/usr/bin/env python3
from distutils.core import setup

from blizzard import __version__

setup(name='blizzard',
    author = 'Thomas Levine',
    author_email = '_@thomaslevine.com',
    description = 'Find the unique indices for a ton of datasets',
    url = 'https://github.com/tlevine/blizzard.git',
    classifiers = [
        'Intended Audience :: Developers',
    ],
    packages = ['blizzard'],
    install_requires = ['networkx','special_snowflake','requests'],
    scripts = ['bin/blizzard'],
    tests_require = ['nose'],
    version = __version__,
    license = 'AGPL',
)
