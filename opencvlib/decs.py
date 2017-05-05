# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''my decorators'''

from functools import wraps as _wraps

import numpy as _np
import cv2 as _cv2
import PIL as _PIL
from PIL import Image as _Image

from funclib.iolib import fixp as _fixp

__all__ = ['decgetimg']


def decgetimg(func):
    '''
    decorator to wrap opening an
    image using opencv.imread
    '''
    #this decorator makes a function accept an image path or ndarray
    @_wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):
        if not img is None:

            if isinstance(img, str):
                i = _cv2.imread(_fixp(img), -1)
            elif isinstance(img, _np.ndarray):
                i = img
            else:
                i = None
            return func(i, *args, **kwargs)
    return _getimg_wrapper

def decgetimgpil(func):
    '''
    decorator to wrap opening an
    image using pil.Image.open

    PIL is a lazy load so checking resolution for example
    will not load the full image into memory
    '''
    #this decorator makes a function accept an image path or ndarray
    @_wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):
        if not img is None:

            if isinstance(img, str):
                i = _Image.open(_fixp(img))
            elif isinstance(img, _PIL.Image.Image):
                i = img
            elif isinstance(img, _np.ndarray):
                i = img
            else:
                i = None

            return func(i, *args, **kwargs)
    return _getimg_wrapper
