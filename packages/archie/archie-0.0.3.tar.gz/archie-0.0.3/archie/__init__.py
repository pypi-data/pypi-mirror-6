import os
from .configuration import Config
from . import handlers as cmd


VERSION = '0.0.3'
APPNAME = 'archie'


def main(args):
    configfile = args['--config'] or os.path.join(args['PACKAGE'], 'a.rc')
    cfg = Config(configfile, args)

    if args['install']:
        result = cmd.Install(cfg)
    elif args['restore']:
        result = cmd.Restore(cfg)

    for item in result:
        print(item)
