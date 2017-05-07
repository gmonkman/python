# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Provides preprocessing routines
'''
import itertools as _it
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


def mosaic(w, imgs):
    '''Make a grid from images.
    w    -- number of grid columns
    imgs -- images (must have same size and format)
    '''
    imgs = iter(imgs)
    img0 = next(imgs)

    pad = _np.zeros_like(img0)
    imgs = _it.chain([img0], imgs)
    rows = _grouper(w, imgs, pad)
    return _np.vstack(map(_np.hstack, rows))


@_decs.decgetimg
def opencv2matplotlib(image):
    '''(ndarray|str)->ndarray
    OpenCV represents images in BGR order; however, Matplotlib
    expects the image in RGB order, so simply convert from BGR
    to RGB and return
    '''
    return _cv2.cvtColor(image, _cv2.COLOR_BGR2RGB)
