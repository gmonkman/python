# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''my decorators'''

from functools import wraps

from opencvlib import getimg

__all__ = ['getimgdec']


def decgetimg(func):
    '''this decorator makes a function accept an
    image path or ndarray
    '''
    @wraps(func)
    def _getimg_wrapper(img, *args, **kwargs):
        if not img is None:
            img = getimg(img)
        return _getimg_wrapper(img, *args, **kwargs)
