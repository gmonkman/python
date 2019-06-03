# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''settings file, stopped using an ini'''
from os import path as _path
import funclib.iolib as _iolib
import mmo as _mmo

_THIS_FILE_PATH = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
_MODULE_ROOT = _path.normpath(mmo.__path__[0]) #root of opencvlib
BIN_FOLDER = _path.normpath(_path.join(_MODULE_ROOT, '/bin/'))

_np = _path.normpath



class PATHS():
    WHITELIST_WORDS = _np(_path.join([BIN_FOLDER,'whitelist.pkl']))
