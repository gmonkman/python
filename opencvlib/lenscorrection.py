# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member
'''MODULE COMMENTS HERE
'''

#region imports
#region base imports
import argparse
import datetime
import itertools
import math	
import os
import time
#end region

#region 3rd party imports
import cv2
import fuckit
import glob
import numpy as np
import pandas as pd
import scipy
import scipy.stats
import xlwings
#endregion

#region my imports
import funclib.arraylib as arraylib
import funclib.iolib as iolib
import funclib.inifilelib as inifilelib
#import funclib.statslib as statslib #includes rpy which takes ages to load
from funclib.stringslib import add_right
from enum import Enum
from funclib.baselib import switch
#endregion
#endregion


class camera(object):
    def __init__(self, calibration_image_path, model):
        self._model = model
        self._calibration_image_path = calibration_image_path

    @property
    def model(self):
        return self._model

    @property
    def calibration_image_path(self):
        return self._calibration_image_path
    @calibration_image_path.setter
    def calibration_image_path(self, calibration_image_path):
        self._calibration_image_path = calibration_image_path


class calibration_grid(object):
    def _init_(self, x_intersects, y_intersects):
        self._x = x_intersects
        self._y = y_intersects

    @property
    def x_intersects(self):
        return self._x_intersects

    @property
    def y_intersects(self):
        return self._y_intersects



#region main
def main(getcmdlineargs=False, initialise_ini=False):
    '''(bool)->void
    Main is only called if the script is directly executed and can
    be used to do stuff in here like testing.
		
    Setting getcmdlineargs to true will set up cmdline arguments,
    which can be loaded into global variables as required (need to define)
    '''
    if getcmdlineargs:
        cmdline = argparse.ArgumentParser(description='Description if script is excuted with -h option')
        cmdline.add_argument('-f','--foo', help='Description for foo argument', required=True)
        cmdline.add_argument('-b','--bar', help='Description for bar argument', required=False, default='WAS_EMPTY')
        cmdargs = cmdline.parse_args()

    if initialise_ini:
        ini_name = os.path.abspath(__file__) + '.ini'
        ini = inifilelib.configfile(ini_name)
        calibration_path = ini.tryread('MODEL', 'CALIBRATION_PATH', force_create=False)
        model = ini.tryread('MODEL', 'MODEL', force_create=False)

    camera = camera(calibration_path, model)

if __name__ == '__main__':
    main(initialise_ini=True)


#endregion