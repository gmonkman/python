# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''my decorators'''

from functools import wraps

import numpy as np
import cv2

from funclib.iolib import fixp

__all__ = ['decgetimg']

# region Decorators
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
# endregion
