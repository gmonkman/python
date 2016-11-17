#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager
''' helper for interacting with application ini files'''

import ConfigParser as cp
import os

import funclib.iolib as iolib

class configfile(object):
    '''handles ini file defaults for common sections and values
    like data paths etc
    '''
    def __init__(self, ini_file):
        self.ini_file_path, self.ini_file_name = os.path.split(os.path.abspath(ini_file))
        self.ini_file = ini_file
        if not str(ini_file).endswith('ini') or str(ini_file).endswith('cfg'):
            raise ValueError('Expected ini file to have extension ini or cfg')

        if not os.path.isfile(ini_file):
            iolib.file_create(ini_file)
        self._config = cp.ConfigParser()        
        self._config.read(ini_file)
        
    def __str__(self):
        assert isinstance(self._config, cp.ConfigParser)
        return str(self._config.options)
    
    def tryread(self, section, option, force_create=True, value_on_create=''):
        '''(str,str) -> str
        section is the section [DEFAULT]
        option is the key.
        if force_create is true then the section and option will be create with the value value_on_create
        Returns the value read, which will default to value_on_create if no section or option is found.
        Saves to disk if new option created.
        '''
        assert isinstance(self._config, cp.ConfigParser)
        if self._config.has_section(section):
            if self._config.has_option(section, option):
                return self._config.get(section, option)
            else:
                if force_create: 
                    self._config.set(section, option, value_on_create)
                    self.save()
                return value_on_create
        else:
            if force_create:
                self._config.add_section(section)
                self._config.set(section, option, value_on_create)
                self.save()
            return value_on_create
    
    def trywrite(self, section, option, value):
        '''(str,str,str) ->void
        tries to write out a value to ini, creating new section if
        the section doesnt already exist
        Saves to disk once done
        '''
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, option, value)
        self.save()

    def save(self):
        '''save the config to disk'''
        with open(self.ini_file, 'w') as configfile:
            self._config.write(configfile)

def iniexists(file):
    '''(str) -> bool
    Checks if the file exists
    '''
    return iolib.file_exists(file)
