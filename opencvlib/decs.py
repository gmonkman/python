# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''my decorators'''

from functools import wraps as _wraps

import numpy as _np
import cv2 as _cv2
import PIL as _PIL
from PIL import Image as _Image
#from skimage.io import imread as _skimread

from funclib.iolib import fixp as _fixp


__all__ = ['decgetimg']


def decgetimgmethod(meth):
    '''
    decorator to wrap opening an
    image using opencv.imread
    '''
    #this decorator makes a function accept an image path or ndarray
    @_wraps(meth)
    def _getimg_wrapper(self, img, *args, **kwargs):
        if not img is None:

            if isinstance(img, str):
                i = _cv2.imread(_fixp(img))
            elif isinstance(img, _np.ndarray):
                i = img
            else:
                i = None
            return meth(self, i, *args, **kwargs)
    return _getimg_wrapper


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
                i = _cv2.imread(_fixp(img))
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


def decgetimgsk(func):
    '''
    decorator to wrap opening an
    image for consumption by skimage functions
    which expect RGB format.

    Expects an opencv BGR ndarray or loads using cv2.imread to derive
    a BGR image.

    Function then coverts it to RGB ndarray, this should be
    converted back to BGR after the scikit function is applied to img
    '''
    #this decorator makes a function accept an image path or ndarray
    @_wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):
        if not img is None:
            if isinstance(img, str):
                i = _cv2.imread(_fixp(img))
                i = _BGR2RGB(i)
            elif isinstance(img, _np.ndarray):
                i = _RGB2BGR(img)
            else:
                i = None

            return func(i, *args, **kwargs)
    return _getimg_wrapper



#region helper functions reproduced to stop circular import errs
def _BGR2RGB(img):
    '''(ndarray)->ndarray
    BGR  to RGB
    opencv to skimage
    '''
    return _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)


def _RGB2BGR(img):
    '''(ndarray)->ndarray
    RGB  to BGR
    skimage to opencv
    '''
    return _cv2.cvtColor(img, _cv2.COLOR_RGB2BGR)
#endregion
