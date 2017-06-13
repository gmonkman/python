# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''histogram helpers'''
import sys

import cv2 as _cv2
import numpy as _np


from opencvlib.transforms import BGR2HSV as _BGR2HSV


def histo_hsv(img, histo, channels=(0, 1), mask=None, accumulate=False, img_is_hsv=False):
    '''(str|ndarray, &ndarray, str, bool, bool)
    Get image histogram over specified channels
    
    img:
        file path or ndarray. Converted to HSV.
    histo:
        BYREF, pointer with previous histogram results
        Previous results will be deleted if accumulate is false
    channels:
        channels to include, default is H and S
    accumulate:
        add historgram to previous results in histo
    img_is_hsv:
        pass if the image is already in HSV format
    '''
    if not img_is_hsv:
        img = _BGR2HSV(img)

    if not accumulate:
        histo = None
    
    if not isinstance(img, list):
        img = [img]

    histSize = []
    ranges = []
    for c in channels:
        if c == 0:
            histSize.append(180)
            ranges.append(0)
            ranges.append(180)
        if c == 1:
            histSize.append(255)
            ranges.append(0)
            ranges.append(256)
        if c == 2:
            histSize.append(255)
            ranges.append(0)
            ranges.append(256)
    

    _cv2.calcHist(img, channels, mask, histSize, ranges, histo, accumulate=True) #accumulate in sel



def hsv_map(x=256, y=180):
    '''(int, int) -> ndarray
    x:
        number of cols
    y:
        number of rows

    Make a hsv map as an ndarry.
    A visualisation of HSV space
    '''
    hsv_map = _np.zeros((180, 256, 3), _np.uint8)
    h, s = _np.indices(hsv_map.shape[:2])
    hsv_map[:, :, 0] = h
    hsv_map[:, :, 1] = s
    hsv_map[:, :, 2] = 255
    hsv_map = _cv2.cvtColor(hsv_map, _cv2.COLOR_HSV2BGR)
    return hsv_map


class VisualColorHisto():
    '''visualise the hsv histogram of an image'''

    def __init__(self, img):
        '''init'''
        self._hist_scale = 10
        self._hsv_map = hsv_map()
        self.win_name = 'hist'
        self._img = _getimg(img)


    def __call__(self, img):
        self._img = _getimg(img)


    def show(self):
        '''show histogram and hsv map'''
        _cv2.imshow('hsv_map', self._hsv_map())
        _cv2.namedWindow(self.win_name, 0)
        _cv2.createTrackbar('scale', self.win_name, self._hist_scale, 32, set_scale)


    def hide(self):
        '''hide histogram and hsv map'''
        try:
            _cv2.destroyWindow('hist')
            _cv2.destroyWindow('hsv_map')
        except:
            pass



    def _process(self,):
        small = _cv2.pyrDown(self._img)



    def set_scale(self, val):
        '''set scale'''
        self._hist_scale = val
    

    while True:

        

        hsv = _cv2.cvtColor(small, _cv2.COLOR_BGR2HSV)
        dark = hsv[..., 2] < 32
        hsv[dark] = 0
        h = _cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])

        h = _np.clip(h * 0.005 * hist_scale, 0, 1)
        vis = hsv_map * h[:, :, _np.newaxis] / 255.0
        _cv2.imshow('hist', vis)

        ch = _cv2.waitKey(1)
