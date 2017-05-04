# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''my decorators'''

from functools import wraps

import numpy as np
import cv2
from PIL.Image import open as pil_open

from funclib.iolib import fixp

__all__ = ['decgetimg']


def decgetimg(func):
    '''
    decorator to wrap opening an
    image using opencv.imread
    '''
    #this decorator makes a function accept an image path or ndarray
    @wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):
        if not img is None:

            if isinstance(img, str):
                i = cv2.imread(fixp(img), -1)
            elif isinstance(img, np.ndarray):
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
    @wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):
        if not img is None:

            if isinstance(img, str):
                i = pil_open(fixp(img))
            elif isinstance(img, np.ndarray):
                i = img
            else:
                i = None
            return func(i, *args, **kwargs)
    return _getimg_wrapper
