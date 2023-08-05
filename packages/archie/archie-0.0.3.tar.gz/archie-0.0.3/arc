#! /usr/bin/env python

"""
Usage:
    arc (install | restore) [--backup-dir=<backup-dir>] [--config=<config>] [--target=<target>] PACKAGE
    arc (-h | --help)
    arc (-v | --version)

Options:
    -b <backup-dir>, --backup-dir=<backup-dir>  Use this directory to store backup file.
                                                  (override `backup-dir' from config file)
    -c <config>, --config=<config>              Configuration file to use.
                                                  (default is <PACKAGE>/a.rc)
    -h --help                                   Show this help.
    -t <target>, --target=<target>              Target directory to install to.
                                                  (default is /tmp)
    -v --version                                Show program version.
"""

__author__ = 'Nurahmadie <nurahmadie@gmail.com>'

from docopt import docopt

import archie

if __name__ == '__main__':
    args = docopt(__doc__, version='%s %s' % (archie.APPNAME, archie.VERSION))
    archie.main(args)
