# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''transforms on an image which return an image'''

import itertools as _it
import cv2 as _cv2
import numpy as _np

import opencvlib.decs as _decs
from funclib.baselib import isPython2 as _isPython2

@_decs.decgetimg
def resize(image, width=None, height=None, inter=_cv2.INTER_AREA):
    '''(ndarray|str, int, int, constant)->ndarray
    1) initialize the dimensions of the image to be resized and grab the image size
    2) If both the width and height are None, then return the original image
    3) Both not none then resize to specied width and height
    4) Otherwise resize keeping the aspect ratio according to the provided width or height
    '''
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    elif width is not None and height is not None:
        dim = (width, height)
    elif width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    elif height is None:
        r = width / float(w)
        dim = (width, int(h * r))
    return _cv2.resize(image, dim, interpolation=inter)


@_decs.decgetimg
def histeq_color(img):
    '''(ndarray)->ndarray
        Equalize histogram of color image
        '''
    img_yuv = _cv2.cvtColor(img, _cv2.COLOR_BGR2YUV)

    # equalize the histogram of the Y channel
    img_yuv[:, :, 0] = _cv2.equalizeHist(img_yuv[:, :, 0])

    # convert the YUV image back to RGB format
    return _cv2.cvtColor(img_yuv, _cv2.COLOR_YUV2BGR)


@_decs.decgetimg
def histeq(im, nbr_bins=256):
    '''(ndarray|str, int)->ndarray
    Histogram equalization of a grayscale image.
    '''

    # get image histogram
    imhist, bins = _np.histogram(im.flatten(), nbr_bins, normed=True)
    cdf = imhist.cumsum()  # cumulative distribution function
    cdf = 255 * cdf / cdf[-1]  # normalize

    # use linear interpolation of cdf to find new pixel values
    im2 = _np.interp(im.flatten(), bins[:-1], cdf)

    return im2.reshape(im.shape), cdf


def compute_average(imlist, silent=True):
    """(list,[bool])->ndarray
        Compute the average of a list of images. """

    # open first image and make into array of type float
    averageim = _np.array(_cv2.imread(imlist[0], -1), 'f')

    skipped = 0

    for imname in imlist[1:]:
        try:
            averageim += _np.array(_cv2.imread(imname), -1)
        except Exception as e:
            if not silent:
                print(imname + "...skipped. The error was %s." % str(e))
                skipped += 1

    averageim /= (len(imlist) - skipped)
    if not silent:
        print('Skipped %s images of %s' % (skipped, len(imlist)))
    return _np.array(averageim, 'uint8')


@_decs.decgetimg
def compute_average2(img, imlist, silent=True):
    """(list,[bool])->ndarray
        Compute the average of a list of images.
        This exists to be compatible with imgpipes transformation framework"""

    # open first image and make into array of type float
    assert isinstance(imlist, list)

    imlist.append(img)
    averageim = _np.array(_cv2.imread(imlist[0], -1), 'f')

    skipped = 0

    for imname in imlist[1:]:
        try:
            averageim += _np.array(_cv2.imread(imname), -1)
        except Exception as e:
            if not silent:
                print(imname + "...skipped. The error was %s." % str(e))
                skipped += 1

    averageim /= (len(imlist) - skipped)
    if not silent:
        print('Skipped %s images of %s' % (skipped, len(imlist)))
    return _np.array(averageim, 'uint8')
