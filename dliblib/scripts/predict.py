#pylint: skip-file

'''
Run shape predictor example.

Reads resources from dliblib.ini
'''
import os
import os.path as path
import sys
import glob
import dlib

import numpy as np

import dliblib.ini as ini
from funclib import iolib
from opencvlib.info import ImageInfo
from opencvlib.view import show
from opencvlib.common import draw_points
from opencvlib.display_utils import KeyBoardInput as Key
from opencvlib import getimg
from opencvlib.imgpipes import vgg

images_folder = path.normpath(ini.Cfg.tryread('predict', 'images_folder'))
assert iolib.folder_exists(images_folder), 'Images folder %s not found or not specified in ini file.' % images_folder

predictor_dat = path.normpath(ini.Cfg.tryread('predict', 'predictor_out'))
predictor = dlib.shape_predictor(predictor_dat)

vgg_file = path.normpath(ini.Cfg.tryread('predict', 'vgg_file'))


print("Press 'q' to quit")

vgg.load_json(vgg_file)
for Img in vgg.imagesGenerator():
    assert isinstance(Img, vgg.Image)
    i = getimg(path.normpath(Img.filepath))
    for roi in Img.roi_generator(shape_type='rect'):
        assert isinstance(roi, vgg.Region)
        d = dlib.rectangle(min(roi.all_points_x), max(roi.all_points_x), min(roi.all_points_y), max(roi.all_points_y))
        i = draw_points(roi.all_points, i, join=True)
        shape = predictor(i, d)

        pts = [(pt.x, pt.y) for pt in shape.parts()]
        i = draw_points(pts, i)
        if Key.check_pressed_key('q', show(i)):
            quit()
