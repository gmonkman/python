#pylint: skip-file
'''for fiducial marker processing'''

import cv2 as _cv2
import numpy as _np
from cv2 import aruco as _aruco

import opencvlib.color as _color
from opencvlib.view import pad_images as _pad_images


MARKERS = {0:'DICT_4X4_50', 1:'DICT_4X4_100', 2:'DICT_4X4_250', \
        3:'DICT_4X4_1000', 4:'DICT_5X5_50', 5:'DICT_5X5_100', 6:'DICT_5X5_250', 7:'DICT_5X5_1000', \
        8:'DICT_6X6_50', 9:'DICT_6X6_100', 10:'DICT_6X6_250', 11:'DICT_6X6_1000', 12:'DICT_7X7_50', \
        13:'DICT_7X7_100', 14:'DICT_7X7_250', 15:'DICT_7X7_1000', 16:'DICT_ARUCO_ORIGINAL'}


def getmarker(markerid, sz_pixels=500, border_sz=0, border_color=_color.CVColors.white, saveas=''):
    '''(int, int, int, 3-tuple) -> ndarry
    Get marker image.

    markerid:
        Dictionary lookup for MARKERS
    sz_pixels:
        Size in pixels
    border_sz:
        border size
    border_color:
        tuple (0,0,0)
    saveas:
        filename to dump img to
    Returns:
        Image as an ndarray
    '''  
    m = cv2.aruco.drawMarker(cv2.aruco.getPredefinedDictionary(16),markerid, border_sz, 1)
    m = _cv2.cvtColor(m, _cv2.COLOR_GRAY2BGR)
    if border_sz > 0:
        m = _pad_images(m, border_color=border_color)
    
    if saveas:
        _cv2.imwrite(saveas,m)
    return m
