#! /usr/bin/env python

from distutils.core import setup
from archie import APPNAME, VERSION

setup(
    name         = APPNAME,
    version      = VERSION,
    description  = 'Symlink management for configuration (rc) file.',
    author       = 'Nurahmadie',
    author_email = 'nurahmadie@gmail.com',
    url          = 'http://bitbucket.org/fudanchii/archie',
    packages     = ['archie', 'archie.handlers'],
    scripts      = ['arc'],
    requires     = ['docopt'],
    classifiers  = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ]
)
