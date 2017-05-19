'''
Set the config variable.
'''

import configparser as _cp
import json as _json

config = _cp.RawConfigParser()
config.read('C:/development/python/opencvlib/objdetect/config.cfg')

min_wdw_sz = _json.loads(config.get("hog", "min_wdw_sz"))
step_size = _json.loads(config.get("hog", "step_size"))
orientations = config.getint("hog", "orientations")
pixels_per_cell = _json.loads(config.get("hog", "pixels_per_cell"))
cells_per_block = _json.loads(config.get("hog", "cells_per_block"))
visualize = config.getboolean("hog", "visualize")
normalize = config.getboolean("hog", "normalize")
pos_feat_ph = config.get("paths", "pos_feat_ph")
neg_feat_ph = config.get("paths", "neg_feat_ph")
model_path = config.get("paths", "model_path")
threshold = config.getfloat("nms", "threshold")
