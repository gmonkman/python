# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Provides preprocessing routines
'''
import itertools as _it
import math as _math

import cv2 as _cv2
import numpy as _np

import opencvlib.decs as _decs
from funclib.baselib import isPython2 as _isPython2


_JET_DATA = {'red': ((0., 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89, 1, 1),
                     (1, 0.5, 0.5)),
             'green': ((0., 0, 0), (0.125, 0, 0), (0.375, 1, 1), (0.64, 1, 1),
                       (0.91, 0, 0), (1, 0, 0)),
             'blue': ((0., 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1), (0.65, 0, 0),
                      (1, 0, 0))}

_CMAP_DATA = {'jet': _JET_DATA}


# region Private
def _grouper(n, iterable, fillvalue=None):
    '''grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx'''
    args = [iter(iterable)] * n
    if not _isPython2():
        output = _it.zip_longest(fillvalue=fillvalue, *args)
    else:
        output = _it.izip_longest(fillvalue=fillvalue, *args)
    return output
# endregion


def make_cmap(name, n=256):
    '''make a cmap'''
    data = _CMAP_DATA[name]
    xs = _np.linspace(0.0, 1.0, n)
    channels = []
    eps = 1e-6
    for ch_name in ['blue', 'green', 'red']:
        ch_data = data[ch_name]
        xp, yp = [], []
        for x, y1, y2 in ch_data:
            xp += [x, x + eps]
            yp += [y1, y2]
        ch = _np.interp(xs, xp, yp)
        channels.append(ch)
    return _np.uint8(_np.array(channels).T * 255)


@_decs.decgetimg
def pad_images(imgs):
    '''(list|tuple:ndarray|str) -> list
    Pad images so that they are all the same size
    as the maximum dimensions
    '''
    maxh = max([x.shape[0] for x in imgs])
    maxw = max([x.shape[1] for x in imgs])

    outimgs = []

    for img in imgs:
        if isinstance(img, _np.ndarray):
            add_h = maxh - img.shape[0]
            add_w = maxw - img.shape[1]
            i = _cv2.copyMakeBorder(img, 0, add_h, 0, add_w, borderType=_cv2.BORDER_CONSTANT, value=[255, 255, 255])
            assert maxh == i.shape[0] and maxw == i.shape[1]
        else:
            i = None

        outimgs.append(i)

    return outimgs


@_decs.decgetimg
def opencv2matplotlib(image):
    '''(ndarray|str)->ndarray
    OpenCV represents images in BGR order; however, Matplotlib
    expects the image in RGB order, so simply convert from BGR
    to RGB and return
    '''
    return _cv2.cvtColor(image, _cv2.COLOR_BGR2RGB)
