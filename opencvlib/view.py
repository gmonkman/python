# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, reimported, superfluous-parens, unused-import

'''
This provides tools to view and annotate images,
largely for debugging purposes

Also check common.py and transforms.py for some other common img manipulation tasks.
'''
import itertools as _it
import math as _math
from warnings import warn as _warn
from enum import Enum as _Enum

import numpy as _np
import cv2 as _cv2



from funclib.baselib import isPython2 as _isPython2
import funclib.baselib as _baselib

import opencvlib.decs as _decs
import opencvlib.color as _color
import opencvlib.info as _info
from opencvlib import transforms as _transforms
from opencvlib.common import draw_str as _draw_str
import opencvlib.geom as _geom
import opencvlib.roi as _roi
from opencvlib import getimg as _getimg
from opencvlib.display_utils import KeyBoardInput, eSpecialKeys
from opencvlib.common import draw_grid, draw_line, draw_points, draw_scale, draw_str #for convieniance
__all__ = ['mosaic', 'pad_images', 'show', 'showarray']

_SHOW_WIDTH = 800.

class ePadColorMode(_Enum):
    tuple_ = 0
    border = 1
    blackwhite = 2


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


def pad_image(img, border_sz, pad_color=_color.CVColors.black , pad_mode=ePadColorMode.tuple_):
    '''(ndarray|str, int|2-tuple, 3-tuple, enum:ePadColorMode) -> ndarray
    Pad an image by border_sz pixels of color pad_color. Alternatively
    use a black or white padding, to contrast least with the guessed
    backgroud.

    guess_pad_color overrides pad_color, and a black or white pad color
    is chosen, based on what contrasts least with the background.

    Parameters:
        imgs: An list of image file system paths, a single image (ndarray) or a list of images ndarrays.
        border_sz: int or two tuple, order is (height, width), if int, same size used for height and width
        pad_color:a color tuple, e.g. (0,0,0)
        guess_pad_color: Pad with black or white, according to the closest match to the background

    Returns:
        the padded image
    '''
    img = _getimg(img)

    if len(border_sz) == 1:
        border_sz = (border_sz, border_sz)
    h, w = border_sz

    if pad_mode == ePadColorMode.blackwhite:
        i_grey = _transforms.togreyscale(img)
        pad_color = (0, 0, 0) if len(i_grey[i_grey < 128]) > len(i_grey[i_grey >= 128]) else (255, 255, 255)
    elif pad_mode == ePadColorMode.border:
        pad_color = _roi.boundary_color_mean(img)

    i = _cv2.copyMakeBorder(img, h, h, w, w, borderType=_cv2.BORDER_CONSTANT, value=pad_color)
    return i


@_decs.decgetimg
def pad_images(imgs, pad_color=_color.CVColors.black):
    '''(list:ndarray|str|ndarray) -> list
    Pad images so that they are all the same size
    as the maximum dimensions.

    for a grayscale image, a tuple is still used for pad color.

    guess_pad_color overrides pad_color, and a black or white pad color
    is chosen, based on what contrasts least with the background.

    Parameters:
        imgs: A list of image file system paths, a single image (ndarray) or a list of images ndarrays.
        pad_color:a color tuple, e.g. (0,0,0)
        guess_pad_color: Pad with black or white, according to the closest match to the background

    Returns:
        array of padded image
    '''
    maxh = max([x.shape[0] for x in imgs])
    maxw = max([x.shape[1] for x in imgs])

    if isinstance(imgs, _np.ndarray):
        return imgs

    if isinstance(imgs, (list, tuple)):
        if len(imgs) == 1:
            return imgs
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


def img_make(h=1024, w=768, depth=3, colour=255):
    '''(int, int, int, int) -> ndarray
    make an image of uniform colour
    '''
    shape = (h, w, depth)
    return _np.array(_np.ones(shape) * colour)


def mosaic(imgs, cols=None, pad=True, pad_color=_color.CVColors.black, save_as='', show_=False):
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

    imgsout = []
    for im in imgs:
        if isinstance(im, str):
            i = _getimg(im)
        elif isinstance(im, _np.ndarray):
            i = im
        else:
            i = None
        imgsout.append(i)

    imgs = imgsout
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

    if save_as:
        try:
            _cv2.imwrite(save_as, out)
        except:
            _warn('Failed to save the mosaic to %s' % save_as)

    if show_:
        show(out)
    return out



def _grouper(n, iterable, fillvalue=None):
    '''grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx'''
    args = [iter(iterable)] * n
    if not _isPython2():
        output = _it.zip_longest(fillvalue=fillvalue, *args)
    else:
        output = _it.izip_longest(fillvalue=fillvalue, *args)
    return output


def contours_show(img, contours, labels, add_label=True, show_=True):
    '''(ndarray, n-list:n,1,2-ndarray, n-list)- > ndarray

    Plot contours with unique colours according to a label list.

    img: image on which to plot the contours
    contours: an n-list of of ndarray of contours, of that output by findContours, can also pass a list of cv points
    label: a list of grouping labels, of len(labels) == len(contours)
    show: show the image

    Returns: Nothng, just shows the mage
    '''
    unq_lbls = list(set(labels))
    dpth = _baselib.depth(contours)
    if dpth == 1:
        for c in contours:
            assert isinstance(c, _np.ndarray), 'Contours should be a depth 2 list of ndarrays'
    elif dpth == 2:
        assert isinstance(contours[0][0], _np.ndarray), 'Contours should be a depth 2 list of ndarrays'
        pass
    else:
        raise ValueError('Contours should be a depth 2 list of ndarrays')

    color_ramp = list(_color.getDistinctColors(len(unq_lbls)))
    im = img.copy()

    for i, c in enumerate(contours):
        lbl = str(labels[i])
        bg_col = color_ramp[unq_lbls.index(labels[i])]
        lbl_col = _color.black_or_white(bg_col)
        if isinstance(c, _np.ndarray):
            c = [c]
        im = _cv2.drawContours(im, c, -1, bg_col, -1)
        vert = _geom.centroid(_roi.contour_to_cvpts(c[0]), dtype=_np.int)
        assert len(vert) == 2, 'len(vert) was %s. Expected len(vert) == 2' % len(vert)
        draw_str(im, vert[0], vert[1], lbl, color=lbl_col, scale=2, thickness=1.5, centre_box_at_xy=True)

    if show_:
        show(im)
    return im
