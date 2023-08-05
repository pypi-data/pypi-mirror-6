import os
import tarfile
from contextlib import closing
from archie import helpers

def find_backup(cfg):
    files = []
    rcfiles = cfg.options('rcfiles')
    for rc in rcfiles:
        backup = helpers.get_backupfile(cfg, rc)
        rcfile = helpers.get_rcfile(cfg, rc)
        if tarfile.is_tarfile(backup):
            files.append((backup, rcfile))
    return files

def gunzip_and_restore(cfg, backupfiles):
    for backup, rc in backupfiles:
        if os.path.islink(rc):
            os.unlink(rc)
        with closing(tarfile.open(backup, 'r:gz')) as tar:
            tar.extractall('/')
    return backupfiles

def Restore(cfg):
    backupfiles = find_backup(cfg)
    return gunzip_and_restore(cfg, backupfiles)
