# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''settings file, stopped using an ini'''
from os import path as _path
from inspect import getsourcefile as _getsourcefile
import mmo as _mmo
from funclib import iolib as _iolib


_THIS_FILE_PATH = _path.normpath(_iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
_MODULE_ROOT = _path.normpath(_mmo.__path__[0]) #root of opencvlib
BIN_FOLDER = _path.normpath(_path.join(_MODULE_ROOT, 'bin'))


class PATHS():
    '''folder settings'''
    NAMED_ENTITIES_ALL = _path.normpath(_path.join(BIN_FOLDER, 'named_entities_all.pkl'))
    NAMED_ENTITIES_ALL_SINGLE = _path.normpath(_path.join(BIN_FOLDER, 'named_entities_all_single.pkl')) #the whitelist of individual words
    LOG_WRITE_HINTS = _path.normpath('c:/temp/log_write_hints.py.log')
    LOG_NAMED_ENTITIES = _path.normpath('c:/temp/log_named_entities.py.log') #currently unused
    NAMED_ENTITIES_DUMP_FOLDER = BIN_FOLDER
    LOG_CLEAN_UGC = _path.normpath('c:/temp/clean_ugc.py.log')
    LOG_CLEAN_GAZ = _path.normpath('c:/temp/clean_gaz.py.log')
