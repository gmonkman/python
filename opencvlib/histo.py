# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''histogram helpers'''
import cv2 as _cv2
import numpy as _np


import funclib.iolib as _iolib


from opencvlib.transforms import BGR2HSV as _BGR2HSV
from opencvlib import getimg as _getimg


def histo_hsv(img, histo=None, channels=(0, 1), mask=None, accumulate=False, img_is_hsv=False):
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
    
    mask = mask.astype('uint8')
    return _cv2.calcHist(img, channels, mask, histSize, ranges, histo, accumulate=accumulate) #accumulate in sel



def hsv_map(x=256, y=180):
    '''(int, int) -> ndarray
    x:
        number of cols
    y:
        number of rows

    Make a hsv map as an ndarry.
    A visualisation of HSV space
    '''
    hsvm = _np.zeros((180, 256, 3), _np.uint8)
    h, s = _np.indices(hsvm.shape[:2])
    hsvm[:, :, 0] = h
    hsvm[:, :, 1] = s
    hsvm[:, :, 2] = 255
    hsvm = _cv2.cvtColor(hsvm, _cv2.COLOR_HSV2BGR)
    return hsvm



def hist_accum_in_folder(wildcardedpath, strmatch=None, normalise=True):
    '''(str, str|None)
    Accumulate saved histogram files in 
    a folder.

    wildcardedpath:
        eg c:/*.tmp
    strmatch:
        additional string which
        the filename must contain

    Normalised hist extension = '.nrm'
    Saved hist extension: '.hst'
    '''
    first = True
    for f in _iolib.file_list_glob_generator(wildcardedpath):
        if isinstance(strmatch, str):
            dummy, fname, dummy = _iolib.get_file_parts(f)
            if  strmatch.startswith(fname):
                continue


        #TODO if use, test this accumulation
        if first:
            arr = _np.load(f)
            first = False
        else:
            arr += _np.load(f)

    if isinstance(arr, _np.ndarray) and normalise:
        arr = _cv2.normalize(arr, None, 0, 255, _cv2.NORM_MINMAX)

    return arr
        



class VisualColorHisto():
    '''visualise the hue and saturation histogram of an image

    Example:
        H = histo.VisualColorHisto(self.Grass)
        cv2.waitKey(0)
        H(cv2.cvtColor(self.Grass, cv2.COLOR_BGR2GRAY))
    '''

    def __init__(self, img, win_name='hist'):
        '''(ndarray|str) -> void

        img:
            BGR image, or filepath
        '''
        self._hist_scale = 10
        self._hsv_map = hsv_map()
        self._win_name = win_name
        self._img = _getimg(img)
        self._histimg = None
        self._hidden = False
        _cv2.imshow('hsv_map', self._hsv_map)
        _cv2.namedWindow(self._win_name, 0)
        _cv2.createTrackbar('scale', self._win_name, self._hist_scale, 32, self.set_scale)
        self.refresh()


    def __call__(self, img):
        self._img = _getimg(img)
        self.refresh()

    def set_scale(self, val):
        '''set scale'''
        self._hist_scale = val
        self.refresh()


    def refresh(self):
        '''process the img'''
        small = _cv2.pyrDown(self._img)
        hsv = _cv2.cvtColor(small, _cv2.COLOR_BGR2HSV)
        dark = hsv[..., 2] < 32
        hsv[dark] = 0
        h = _cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        h = _np.clip(h * 0.005 * self._hist_scale, 0, 1)
        vis = self._hsv_map * h[:, :, _np.newaxis] / 255.0
        self._histimg = vis
        _cv2.imshow('hist', vis)
