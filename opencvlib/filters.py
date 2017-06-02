# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''keypoint helpers
keypoint detection is handled in features.py'''
from enum import Enum as _Enum
import numpy as _np
import cv2 as _cv2

import opencvlib.decs as _decs
from opencvlib import getimg as _getimg


class eColorSpace(_Enum):
    HSV = 0
    RGB = 1
    BGR = 2


class ColorRange():
    '''class to store a filter range
    in the HSV color space'''

    def __init__(self, ch1=(0, 0), ch2=(0,0), ch3=(0,0)):
        assert(max(ch1))< 255.00000001
        self.ch1 = ch1
        self.ch2 = ch2
        self.ch3 = ch3
        _check()


    def _check(self):
        f = lambda x: x if max(x) <= 255 and min(x) >= 0 else None
        if f(self.ch1) is None:
            raise ValueError('H range was invalid')

        if f(self.ch2) is None:
            raise ValueError('S range was invalid')

        if f(self.ch3) is None:
            raise ValueError('V range was invalid')


class ColorDetection():
    '''color detection stuff'''

    @_decs.decgetimgmethod
    def __init__(self, img, ch1=None, ch2=None, ch3=None, color_space=eColorSpace.HSV, paired=True):
        '''(ndarray|str, .ch1.2.3... tuple:class:ColorRange|class:ColorRange|None, bool) -> void

        img:
            will load img if a path is passed
        ch123:
            Class ColorRange or None, tuples defining channel ranges to keep
        paired:
            If true, assumes that ch1, ch2 and ch3 operate together, otherwise
            applies all filters independently
        '''
        if color_space == eColorSpace.BGR:
            pass
        elif color_space == eColorSpace.HSV:
            img = _cv2.cvtColor(img, _cv2.COLOR_BGR2HSV)
        elif color_space == eColorSpace.RGB:
            img = _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)
        else:
            raise ValueError('Unsupported color space enumeration')

        self.img = img


    def mask(self, invert=False):
        '''get the mask, can be inverted'''
        self._mask = None
        return self._mask
    
    
    def get_image(self, mask_color=(0, 0, 0), invert=False):
        '''-> ndarray|None
        Get the image with ranges masked with mask_color

        mask_color:
            tuple specifying the mask color
        invert:
            Invert the mask selection
   

        Returns:
            masked image
        '''