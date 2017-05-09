# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''transforms on an image which return an image'''

from collections import deque as _deque


import cv2 as _cv2
import numpy as _np


import funclib.baselib as _baselib

import opencvlib.decs as _decs
from opencvlib.common import getimg as _getimg

#from scikit-image
#see http://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.is_low_contrast

import skimage.exposure as _exposure



#region Handling Transforms in Generators
class Transform():
    ''' class to hold and execute a transform

    Transforms should all take img as the first argument,
    hence we should be able to also store cv2 or other
    functions directly.

    Where we cant store 3rd party lib transforms directly
    we will wrap them in transforms.py
    '''
    def __init__(self, func, *args, **kwargs):
        '''the functionand the arguments to be applied
        '''
        self._args = args
        self._kwargs = kwargs
        self._func = func
        self.img_transformed = None


    @_decs.decgetimgmethod
    def exectrans(self, img, force=False):
        '''(str|ndarray, bool)->ndarray
        Perform the transform on passed image.
        Returns the transformed image and sets
        to class instance variable img_transformed

        force: force execution of the transform
        '''
        if isinstance(self.img_transformed, _np.ndarray) and not force:
            return self.img_transformed #dont apply again
        else:
            if not img is None:
                img_transformed = self._func(img, *self._args, **self._kwargs)
                if isinstance(img_transformed, _np.ndarray):
                    self.img_transformed = img_transformed
                elif isinstance(img_transformed, list) or isinstance(img_transformed, tuple):
                    self.img_transformed = _baselib.item_from_iterable_by_type(img_transformed, _np.ndarray)
                else:
                    raise ValueError('Unexpectedly failed to get ndarray image from transforms.exectrans. Check the transformation function "%s" returns an ndarray.' % self._func.__name__)
                return self.img_transformed
            else:
                return None


class Transforms():
    '''class which holds a queue of Transform classes
    to apply to a single image.

    Transforms are first in - first out
    '''
    def __init__(self, img=None, *args):
        '''(str|ndarray, Transform(s))
        '''
        self.img = _getimg(img)
        self.img_transformed = None
        self.tQueue = _deque()
        self.tQueue.extend(args)


    def add(self, *args):
        '''(Transform|Transforms)->void

        Queue a transform or many transforms.

        Transforms are executed FIFO when executeQueue is invoked
        '''
        self.tQueue.extend(args)


    @_decs.decgetimgmethod
    def executeQueue(self, img=None):
        '''(str|ndarray)->ndarray
        perform the transformations. Is FIFO.
        Set img_transformed property, and returns
        the transformed image
        '''
        if not img is None:
            self.img = img

        first = True
        if _baselib.isempty(self.tQueue):
            return self.img
        else:
            while len(self.tQueue) > 0:
                T = self.tQueue.popleft()
                assert isinstance(T, Transform)
                if first:
                    self.img_transformed = T.exectrans(self.img)
                    first = False
                else:
                    self.img_transformed = T.exectrans(self.img_transformed)
            return self.img_transformed
#endregion


#skimage transforms in skimage.exposure
@_decs.decgetimgsk
def adjust_gamma(img, gamma=1, gain=1):
    '''(ndarray|str, float, float) -> BGR-ndarray
    Performs Gamma Correction on the input image.
    Transforms the input image pixelwise according to the equation O = I**gamma after scaling each pixel to the range 0 to 1.

    eg: gamma_corrected = exposure.adjust_gamma(image, 2)
    '''

    return RGB2BGR(_exposure.adjust_gamma(img, gamma, gain))


@_decs.decgetimgsk
def adjust_log(img, gain=1, inv=False):
    '''(ndarray|str, float, bool) -> BGR-ndarray
    '''
    i = _exposure.adjust_log(img, gain=gain, inv=inv)
    return RGB2BGR(i)


@_decs.decgetimgsk
def adjust_sigmoid(img, cutoff=0.5, gain=10, inv=False):
    '''(ndarray|str, float, float, bool) -> BGR-ndarray
    Performs Sigmoid Correction on the input image.
    '''
    i = _exposure.adjust_sigmoid(img, cutoff=cutoff, gain=gain, inv=inv)
    return RGB2BGR(i)


@_decs.decgetimgsk
def equalize_adapthist(img, kernel_size=8, clip_limit=0.5, nbins=255):
    '''(ndarray|str, int|listlike, float, int) -> BGR-ndarray
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Supports color.

    kernel_size: integer or list-like, optional
        Defines the shape of contextual regions used in the algorithm.
        If iterable is passed, it must have the same number
        of elements as image.ndim (without color channel).
        If integer, it is broadcasted to each image dimension.
        By default, kernel_size is 1/8 of image height by 1/8 of its width.
    clip_limit : float, optional
        Clipping limit, normalized between 0 and 1 (higher values give more contrast).

    nbins : int, optional
        Number of gray bins for histogram (“data range”).
    '''
    i = _exposure.equalize_adapthist(img, kernel_size=8, clip_limit=0.05, nbins=255)
    return RGB2BGR(i)


@_decs.decgetimgsk
def equalize_hist(img, nbins=256, mask=None):
    '''(ndarray|str, int, ndarray of bools, 0 or 1s) -> BGR-ndarray
    Perform historgram equalization with optional mask.
    True mask values only are evaluated
    '''
    i = _exposure.equalize_hist(img, nbins, mask)
    return RGB2BGR(i)


@_decs.decgetimgsk
def rescale_intensity(img, in_range='image', out_range='dtype'):
    '''(ndarray|str, str|2-tuple, str|2-tuple) -> ndarray [BGR]

    in_range, out_range : str or 2-tuple
    Min and max intensity values of input and output image. The possible values for this parameter are enumerated below.
    ‘image’
        Use image min/max as the intensity range.

    ‘dtype’
        Use min/max of the image’s dtype as the intensity range.
    dtype-name
        Use intensity range based on desired dtype. Must be valid key in DTYPE_RANGE.
    2-tuple
        Use range_values as explicit min/max intensities.
    '''
    i = _exposure.rescale_intensity(img, in_range=in_range, out_range=out_range)
    return RGB2BGR(i)
#endregion


def BGR2RGB(img):
    '''(ndarray)->ndarray
    BGR  to RGB
    opencv to skimage
    '''
    return _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)


def RGB2BGR(img):
    '''(ndarray)->ndarray
    RGB  to BGR
    skimage to opencv
    '''
    return _cv2.cvtColor(img, _cv2.COLOR_RGB2BGR)


@_decs.decgetimg
def togreyscale(img):
    '''(str|ndarray)->ndarray
    Convert image to greyscale
    '''
    return _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)


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
def histeq_adapt(img, clip_limit=2, tile_size=(8, 8)):
    '''(ndarray|str, int, (int,int))->ndarray
    Adaptive histogram equalization.
    Performs equaliation in equal size tiles as specified by tile_size.

    tile_size of 8x8 will divide the image into 8 by 8 tiles

    clip_limit set the threshold for contrast limiting.
    '''
    clahe = _cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    return clahe.apply(img)



@_decs.decgetimg
def histeq(im):
    '''(ndarray|str, int)->ndarray
    Histogram equalization of a grayscale image.
    '''
    img_bw = togreyscale(im)
    return _cv2.equalizeHist(img_bw)


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
