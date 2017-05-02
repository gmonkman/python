'''
Set the config variable.
'''

import configparser as cp
#import json

config = cp.RawConfigParser()
config.read('./config.cfg')

digikamdb = config.get("DIGIKAM", "dbpath")
#orientations = config.getint("hog", "orientations")
#cells_per_block = json.loads(config.get("hog", "cells_per_block"))
#normalize = config.getboolean("hog", "normalize")
#threshold = config.getfloat("nms", "threshold")
