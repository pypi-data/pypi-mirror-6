import os, errno

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def get_backupfile(cfg, key):
    fname = os.path.basename(get_rcfile(cfg, key))
    backupfile = os.path.join(cfg.get('dirs', 'backup-dir'), \
        '%s-%s.tgz' % (cfg.args['PACKAGE'].replace('/', '_'), fname))
    return backupfile

def get_rcfile(cfg, key):
    rcfile = cfg.get('rcfiles', key)
    if rcfile and rcfile[-1] != '/':
        return os.path.abspath(rcfile)
    if rcfile and rcfile[-1] == '/':
        return os.path.join(os.path.abspath(rcfile), '.%s' % key)
    return os.path.join(cfg.get('dirs', 'target'), '.%s' % key)

def add_checksum(filename): pass

def verify_checksum(filename): pass
