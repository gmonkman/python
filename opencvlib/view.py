# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, reimported, superfluous-parens, unused-import

'''
This module contains some common routines used by other samples.
From https://github.com/opencv/opencv/blob/master/samples/python/common.py#L1
'''
import itertools as _it
import math as _math

import numpy as _np
import cv2 as _cv2



from funclib.baselib import isPython2 as _isPython2
import funclib.baselib as _baselib

import opencvlib.decs as _decs
import opencvlib.color as _color
import opencvlib.info as _info
from opencvlib import transforms as _transforms
from opencvlib.common import draw_str as _draw_str
from opencvlib import getimg as _getimg
from opencvlib.display_utils import KeyBoardInput, eSpecialKeys
from opencvlib.common import draw_grid, draw_line, draw_points, draw_scale, draw_str #for convieniance
__all__ = ['mosaic', 'pad_images', 'show', 'showarray']

_SHOW_WIDTH = 800.



def _getwaitkey(i):
    '''get a string representation
    of the key pressed to end opencv.waitkey
    '''
    return chr(i & 255)


def _checkwaitkey(key_as_string, waitkeyval):
    '''pass in a character, returns true if matched'''
    return _getwaitkey(waitkeyval) == key_as_string



def showarray(ndarrs, maximise_show_width=True):
    '''(ndarray|list:ndarray) -> void
    visualise an array or arrays'''
    pixel_size = 1
    if isinstance(ndarrs, _np.ndarray):
        ndarrs = [ndarrs]

    A = [_square_array(a) for a in ndarrs]
    w = [Z.shape[1] for Z in A]

    if maximise_show_width:
        pixel_size = _SHOW_WIDTH/max(w)
    show(A, pixel_size=pixel_size)


def _square_array(ndarr):
    '''(ndarray) -> ndarray
    Flattens an array then
    returns the array as a 2d
    square array padded with 0s
    primarily for display purposes
    '''
    assert isinstance(ndarr, _np.ndarray)
    flt = ndarr.flatten()
    _math.sqrt(len(flt))
    sqr = _math.ceil(_math.sqrt(len(flt)))

    tup = (0, sqr**2 - len(flt))
    pad = _np.pad(flt, tup, mode='constant', constant_values=0)
    pad = _np.reshape(pad, (sqr, sqr))
    return pad



@_decs.decgetimg
def pad_images(imgs, pad_color=_color.CVColors.black):
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
            if len(img.shape) == 2:
                i = _cv2.cvtColor(img, _cv2.COLOR_GRAY2BGR)
            else:
                i = img
            i = _cv2.copyMakeBorder(img, 0, add_h, 0, add_w, borderType=_cv2.BORDER_CONSTANT, value=pad_color)
            assert maxh == i.shape[0] and maxw == i.shape[1]
        else:
            i = None

        outimgs.append(i)

    return outimgs


def show_all_channels(img):
    '''(ndarray, str)->void
    Show a mosaic of all channels of an image
    '''
    img = _getimg(img)

    brg = _transforms.chswap(img, (0, 2, 1))
    _draw_str(brg, 10, 10, 'bgr->brg', color=(0, 0, 0), box_background=255)

    rgb = _transforms.chswap(img, (2, 1, 0))
    _draw_str(rgb, 10, 10, 'bgr->rgb', color=(0, 0, 0), box_background=255)

    rbg = _transforms.chswap(img, (2, 0, 1))
    _draw_str(rbg, 10, 10, 'bgr->rbg', color=(0, 0, 0), box_background=255)

    grb = _transforms.chswap(img, (1, 2, 0))
    _draw_str(grb, 10, 10, 'bgr->grb', color=(0, 0, 0), box_background=255)

    gbr = _transforms.chswap(img, (1, 0, 2))
    _draw_str(gbr, 10, 10, 'bgr->gbr', color=(0, 0, 0), box_background=255)

    m = mosaic([img, brg, rgb, rbg, grb, gbr])
    show(m)


#@_decs.decgetimg
def show(img, title='img', max_width=_SHOW_WIDTH, waitsecs=0, pad_color=_color.CVColors.black, absolute=True, pixel_size=1., color_space=_color.eColorSpace.BGR, draw_str_=''):
    '''(str|ndarray|iterable, int, int)->int, str
    Show an image, passing in a path or ndarray

    A list of images can be passed, which will be mosaiced
    prior to showing

    max_width:
        maximum width, aspect ratio is maintained
    waitsecs
        seconds to wait before closing the window
    pad_color
        color to use to fill in gaps when mosaicing multiple images
    absolute
        absolute the image, (ie negative->positive), useful
        for visualising some convolutions
    pixel_size
        increase or decrease image using basic interpolation, good for showing small
        pixel based images. This occurs after mosaicing, but before max_width resize
        A pixel_size=2 implies that each pixel in the original image will be
        represented by 2x2 pixels in the new image
    title
        string to show on image as title

    Returns
        the key value pressed and the title
        <no key>=255
        y=121
        <space>=32
        n=110
    '''
    img = _getimg(img)
    if isinstance(img, _np.ndarray):
        im = img
        if absolute:
            im = _np.abs(im).astype('uint8')
    elif _baselib.isIterable(img):
        im = mosaic([_np.abs(i).astype('uint8') if absolute else i for i in img], pad_color=pad_color)

    w, h = _info.ImageInfo.getsize(im)

    w = w*pixel_size
    h = h*pixel_size

    im = _transforms.resize(im, w, h, _cv2.INTER_NEAREST)

    w, h = _info.ImageInfo.getsize(im)

    if w > max_width:
        ratio = max_width/w
        new_w = int(max_width)
        new_h = int(h * ratio)
    else:
        new_w = int(w)
        new_h = int(h)


    millisecs = int(waitsecs*1000)
    if millisecs < 0:
        millisecs = 0

    if draw_str_ != '':
        _draw_str(im, 10, 10, draw_str, (0, 255, 255))

    _cv2.namedWindow(title, _cv2.WINDOW_NORMAL)
    _cv2.resizeWindow(title, new_w, new_h)
    _cv2.imshow(title, im)
    key = _cv2.waitKey(millisecs) #255 is no key press

    _cv2.destroyAllWindows()
    return key, title


@_decs.decgetimg
def mosaic(imgs, cols=None, pad=True, pad_color=_color.CVColors.black):
    '''(list|tuple, int|None, bool) -> ndarray

    Make a grid from images.
    imgs:
        mixed str|ndarray list or tuple of images
    cols:
        number of grid columns. If None, then assumes square matrix
    pad:
        padding will be used so all images are the same (maximum) size
        If pad is false, an error will be raised if image dimensions differ
    '''

    if isinstance(imgs, _np.ndarray):
        return imgs

    cols = _math.ceil(_math.sqrt(len(imgs))) if cols is None else cols

    #stacks funcs need same channel number
    hasbw = False
    for img in imgs:
        if _info.ImageInfo.typeinfo(img) & _info.eImgType.CHANNEL_1.value:
            hasbw = True
            break

    if hasbw:
        imgs = [_cv2.cvtColor(i, _cv2.COLOR_GRAY2BGR) if len(i.shape) == 2 else i for i in imgs]

    imgs = pad_images(imgs, pad_color=pad_color) #make images the same size by adding padding

    I = iter(imgs)
    img0 = next(I)

    pad = _np.zeros_like(img0)
    I = _it.chain([img0], I)
    rows = _grouper(cols, I, pad)
    out = _np.vstack(map(_np.hstack, rows))
    return out



def _grouper(n, iterable, fillvalue=None):
    '''grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx'''
    args = [iter(iterable)] * n
    if not _isPython2():
        output = _it.zip_longest(fillvalue=fillvalue, *args)
    else:
        output = _it.izip_longest(fillvalue=fillvalue, *args)
    return output
