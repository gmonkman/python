# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''settings file, stopped using an ini'''
from os import path as _path
from inspect import getsourcefile as _getsourcefile
import mmo as _mmo
from funclib import iolib as _iolib


_THIS_FILE_PATH = _path.normpath(_iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
_MODULE_ROOT = _path.normpath(_mmo.__path__[0]) #root of opencvlib
BIN_FOLDER = _path.normpath(_path.join(_MODULE_ROOT, '/bin/'))


class PATHS():
    '''folder settings'''
    WHITELIST_WORDS = _np(_path.join([BIN_FOLDER, 'whitelist.pkl']))
    LOG_WRITE_HINTS = _path.normpath('c:\temp\log_write_hints.py.log')
