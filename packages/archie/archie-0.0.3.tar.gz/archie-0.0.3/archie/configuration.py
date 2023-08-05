try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import ConfigParser as SafeConfigParser

class Config:
    def __init__(self, configfile, args):
        self.args = args
        try:
            self.conf = SafeConfigParser(allow_no_value = True)
        except TypeError:
            self.conf = SafeConfigParser()
        self.conf.readfp(open(configfile))

    def get(self, section, key):
        if section == 'args':
            return self.args[key]
        if section == 'dirs':
            return self.__defaults_(key)
        return self.conf.get(section, key, raw = False, vars = {
            'target':       self.__defaults_('target'),
            'backup-dir':   self.__defaults_('backup-dir') })

    def options(self, section):
        return self.conf.options(section)

    def __defaults_(self, key):
        return self.args['--' + key] or self.conf.get('dirs', key, raw = False)
