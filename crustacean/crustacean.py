# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member
'''MODULE COMMENTS HERE
'''

#region imports
#region base imports
import datetime
import itertools
import math	
import os
import time
#end region

#region 3rd party imports
import cv2
import fuckit
import matplotlib.pyplot as plt
import matplotlib.image as mping
import numpy as np
import pandas as pd
import scipy
import scipy.stats
import xlwings
#endregion

#region my imports
import funclib.arraylib as arraylib
import funclib.inifilelib as inifilelib
import funclib.iolib as iolib
#import funclib.statslib as statslib #includes rpy which takes ages to load
from funclib.stringslib import add_right
from enum import Enum
from funclib.baselib import switch
#endregion
#endregion

_INI_NAME = ''
_MOVIE = ''

#region main

def test():
    global _INI_NAME

def init(getcmdlineargs=False, initialise_ini=False):
    '''(bool)->void
	Main is only called if the script is directly executed and can
	be used to do stuff in here like testing.
		
	Setting getcmdlineargs to true will set up cmdline arguments,
	which can be loaded into global variables as required (need to define)
	'''
    global _INI_NAME
    global _MOVIE

    if getcmdlineargs:
        cmdline = argparse.ArgumentParser(description='Description if script is excuted with -h option')
        cmdline.add_argument('-f','--file', help='name of a movie file', required=False)
        cmdargs = cmdline.parse_args()

        if cmdargs.file == 'THE FOO ARG':
			#global _FOO = cmdargs.foo
			#do stuff
            pass

    if initialise_ini:
        _INI_NAME = os.path.abspath(__file__) + '.ini'
        ini = inifilelib.ConfigFile(_INI_NAME)
        _MOVIE = ini.tryread('MOVIES', 'movie', False)

def get_frame(cap, scaling_factor):
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=scaling_factor, 
            fy=scaling_factor, interpolation=cv2.INTER_AREA)
    return frame

if __name__ == '__main__':
    init(getcmdlineargs=False, initialise_ini=True)
    cap = cv2.VideoCapture(_MOVIE)
    scaling_factor = 0.5

    while True:
        frame = get_frame(cap, scaling_factor) 
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # define range of skin color in HSV
        lower = np.array([0,70,60])
        upper = np.array([50,150,255])

        # define blue range
        #lower = np.array([60,100,100])
        #upper = np.array([180,255,255])

        # Threshold the HSV image to get only blue color
        mask = cv2.inRange(hsv, lower, upper)

        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame, frame, mask=mask)
        res = cv2.medianBlur(res, 5)

        cv2.imshow('Original image', frame)
        cv2.imshow('Color Detector', res)
        c = cv2.waitKey(5) 
        if c == 27:
            break

    cv2.destroyAllWindows()


#endregion