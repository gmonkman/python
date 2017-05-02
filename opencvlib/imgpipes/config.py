'''
Set the config variable.
'''

import configparser as cp
from inspect import getsourcefile
from os.path import abspath
from os.path import join
#import json

from funclib.iolib import fixp
from funclib.iolib import get_file_parts2


def cfg_path():
    '''()->str
    returns full path to config file
    '''
    pth, fname, ext = get_file_parts2(abspath(getsourcefile(lambda:0)))
    pth = fixp(pth)
    return fixp(join(pth,'imgpipes.cfg'))



config = cp.RawConfigParser()
config.read(cfg_path())

digikamdb = config.get("DIGIKAM", "dbpath")

#orientations = config.getint("hog", "orientations")
#cells_per_block = json.loads(config.get("hog", "cells_per_block"))
#normalize = config.getboolean("hog", "normalize")
#threshold = config.getfloat("nms", "threshold")
