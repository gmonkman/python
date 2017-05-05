'''
Set the config variable.
'''

import configparser as _cp
from inspect import getsourcefile as _getsourcefile
import os.path as _path
#import json

from funclib.iolib import fixp as _fixp
from funclib.iolib import get_file_parts2 as _get_file_parts2


def _cfg_path():
    '''()->str
    returns full path to config file
    '''
    pth = _get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
    pth = _fixp(pth)
    return _fixp(_path.join(pth, 'imgpipes.cfg'))



_config = _cp.RawConfigParser()
_config.read(_cfg_path())

digikamdb = _fixp(_config.get("DIGIKAM", "dbpath"))

#orientations = config.getint("hog", "orientations")
#cells_per_block = json.loads(config.get("hog", "cells_per_block"))
#normalize = config.getboolean("hog", "normalize")
#threshold = config.getfloat("nms", "threshold")
