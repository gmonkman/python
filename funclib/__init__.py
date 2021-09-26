'''main init for funclib'''


__all__ = [
    'arraylib',
    'baselib',
    'configlib',
    'excellib',
    'inifilelib',
    'iolib',
    'jsonlib',
    'log',
    'numericslib',
    'pandaslib',
    'shell_lib',
    'statslib',
    'stopwatch',
    'stringslib',
    'to_precision',
    'xmllib']


from funclib.baselib import get_platform
from funclib.baselib import isPython2
from funclib.baselib import isPython3
from funclib.baselib import isIterable

def totextfile(s, fname):
    '''dum s, to a file.
    where s can be a string, list, dict etc
    '''
    with open(fname, "w") as text_file:
        text_file.write(s)