# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, superfluous-parens
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

    This is intended for use with class methods
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
    image using opencv.imread.

    Supports a mixed tuple|list of ndarrays and strings (paths)
    or single str (path)

    img(s) elements of type ndarray are simply returned

    Intended for use with functions.
    **NOT** for use with class methods
    '''
    #this decorator makes a function accept an image path or ndarray
    @_wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):

        g = lambda g: _cv2.imread(_fixp(g))

        if img is None:
            return func(None, *args, **kwargs)

        if isinstance(img, list) or isinstance(img, tuple):
            imgsout = []
            for im in img:
                if isinstance(im, str):
                    i = g(im)
                elif isinstance(im, _np.ndarray):
                    i = im
                else:
                    i = None
                imgsout.append(i)
            return func(imgsout, *args, **kwargs)
        else:
            if isinstance(img, str):
                i = g(img)
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
    if _isbw(img):
        return img
    else:
        return _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)


def _RGB2BGR(img):
    '''(ndarray)->ndarray
    RGB  to BGR
    skimage to opencv
    '''
    if _isbw(img):
        return img
    else:
        return _cv2.cvtColor(img, _cv2.COLOR_RGB2BGR)


def _isbw(img):
    #img is a numpy.ndarray, loaded using cv2.imread
    if len(img.shape) > 2:
        looks_like_rgbbw = not False in ((img[:, :, 0:1] == img[:, :, 1:2]) == (img[:, :, 1:2] == img[:, :, 2:3]))
        looks_like_hsvbw = not False in ((img[:, :, 0:1] == 0) == (img[:, :, 1:2]) == 0)
        return looks_like_rgbbw or looks_like_hsvbw
    else:
        return True

#endregion
