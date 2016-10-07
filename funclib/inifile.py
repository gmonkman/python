#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager
''' helper for interacting with application ini files'''

import  ConfigParser as cp
import os

class default(object):
    '''handles ini file defaults for common sections and values
    like data paths etc
    '''
   
    
    def __init__(self, ini_file):
        self.program_path = os.path.dirname(os.path.abspath(program_path))
        self.ini_file = ini_file
        self.path_section = 'PATHS'
        self.__config = cp.ConfigParser()        
         

    def tryread(section, option):
        '''(str,str) -> str
        '''
        