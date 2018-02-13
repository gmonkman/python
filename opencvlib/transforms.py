# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, protected-access, unused-import
'''transforms on an image which return an image'''
import cv2 as _cv2
import numpy as _np
from enum import Enum as _Enum

import funclib.baselib as _baselib

import opencvlib.decs as _decs
from opencvlib import getimg as _getimg
from opencvlib import color as _color
from opencvlib import Log as _Log
from opencvlib.color import BGR2HSV, BGR2RGB, HSVtoGrey, togreyscale
import opencvlib.roi as _roi



#from scikit-image
#see http://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.is_low_contrast
import skimage.exposure as _exposure


class eRegionFormat(_Enum):
    '''
    RCHW: (r, c, h, w)
    CVXYWH: (x, y, w, h)
    CVXYXYXYXY: [[x,y], [x,y], [x,y], [x,y]], origin at top left
    XYXYXYXY: [[x,y], [x,y], [x,y], [x,y]], cartesian origin
    HW: (h, w), used for cropping an image at a point
    WH: (w, h), used for cropping an image at a point
    '''
    RCHW = 0
    CVXYWH = 1
    CVXYXYXYXY = 2
    XYXYXYXY = 3
    HW = 4
    WH = 5


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

        if not img is None:
            img_transformed = self._func(img, *self._args, **self._kwargs)
            if isinstance(img_transformed, _np.ndarray):
                self.img_transformed = img_transformed
            elif isinstance(img_transformed, (list, tuple)):
                self.img_transformed = _baselib.item_from_iterable_by_type(img_transformed, _np.ndarray)
            else:
                raise ValueError('Unexpectedly failed to get ndarray image from transforms.exectrans. Check the transformation function "%s" returns an ndarray.' % self._func.__name__)
            return self.img_transformed

        return None


class Transforms():
    '''class which holds a queue of Transform classes
    to apply to a single image.

    Transforms are first in - first out
    '''
    def __init__(self, img=None, *args):
        '''(str|ndarray, Transform(s))

        Transforms can be queued before
        setting img.
        '''
        self.img = _getimg(img)
        self.img_transformed = None
        self.tQueue = []
        self.tQueue.extend(args)


    def __call__(self, img=None, execute=True):
        '''(str|ndarray) -> void
        Set image if not done previously
        '''
        if not img is None:
            self.img = _getimg(img)

        if execute:
            self.executeQueue()


    def add(self, *args):
        '''(Transform|Transforms)->void

        Queue a transform or many transforms.

        Transforms are executed FIFO when executeQueue is invoked
        '''
        s = 'Queued transforms ' + ' '.join([f._func.__name__ for f in args])
        _Log.info(s)
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

        for T in self.tQueue:
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
    i = _exposure.adjust_gamma(img, gamma, gain)
    return _color.RGB2BGR(i)


@_decs.decgetimgsk
def adjust_log(img, gain=1, inv=False):
    '''(ndarray|str, float, bool) -> BGR-ndarray
    '''
    i = _exposure.adjust_log(img, gain=gain, inv=inv)
    assert str(i.dtype) == 'uint8'
    return _color.RGB2BGR(i)


def int32_to_uint8(ndarray, absolute=True):
    '''(ndarray)->ndarray
    Convert array to uint8 if it is int32

    abs:
        perform an abs if True

    return
        converted array
    '''
    assert isinstance(ndarray, _np.ndarray)
    if ndarray.dtype == 'int32':
        return absolute(ndarray).astype('uint8') if absolute else ndarray.astype('uint8')

    return ndarray


@_decs.decgetimgsk
def adjust_sigmoid(img, cutoff=0.5, gain=10, inv=False):
    '''(ndarray|str, float, float, bool) -> BGR-ndarray
    Performs Sigmoid Correction on the input image.
    '''
    i = _exposure.adjust_sigmoid(img, cutoff=cutoff, gain=gain, inv=inv)
    return _color.RGB2BGR(i)


@_decs.decgetimgsk
def equalize_adapthist(img, kernel_size=None, clip_limit=0.01, nbins=256):
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
    i = _exposure.equalize_adapthist(img, kernel_size=kernel_size, clip_limit=clip_limit, nbins=nbins)
    return _color.RGB2BGR(i) #this func is wrapped to handle black and white as well


def to8bpp(img):
    '''(ndarray:float)->ndarray:uint8
    Convert float image representation to
    8 bit image.
    '''
    assert isinstance(img, _np.ndarray)
    if 'float' in str(img.dtype):
        return _np.array(img * 255, dtype=_np.uint8)
    elif str(img.dtype) == 'uint8':
        return img

    assert img.dtype == 'uint8' #unexpected, debug if occurs
    return img


def toFloat(img):
    '''(ndarray:float)->ndarray:uint8
    Convert float image representation to
    8 bit image.
    '''
    assert isinstance(img, _np.ndarray)
    if 'uint' in str(img.dtype):
        return _np.array(img / 255, dtype=_np.float)
    elif 'float' in str(img.dtype):
        return img

    assert 'float' in str(img.dtype) #unexpected, debug if occurs
    return img


@_decs.decgetimgsk
def equalize_hist(img, nbins=256, mask=None):
    '''(ndarray|str, int, ndarray of bools, 0 or 1s) -> BGR-ndarray
    Perform historgram equalization with optional mask.
    True mask values only are evaluated
    '''
    i = _exposure.equalize_hist(img, nbins, mask)
    return _color.RGB2BGR(i)


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
    return _color.RGB2BGR(i)
#endregion


def crop(img, region, eRegfmt=eRegionFormat.RCHW, around_point=None, allow_crop_truncate=True):
    '''(ndarray, list|tuple, Enum:roi.eRegionFormat, 2-tuple|None, bool) -> ndarray
    Crops an image.

    img:
        The image
    region:
        Coordinate array, a 4-tuple/list in format defined by ePtType
        Tuple can be a 1-deep list if in rchw like format,
        or a 4-tuple of points, e.g. ((0, 0), (100, 100), (0, 100), (100,0))
        If around_point is True, then the region must be just wh, or hw
    eRegfmt:
        The format of the points in variable region
    around_point:
        If none, standard crop assuming some xywh 4-tuple passed,
        otherwise around_point is a CVXY 2-tuple point and array is
        in WH or HW format (i.e. a 2-tuple).
    allow_crop_truncate:
        If true, will crop to the image edges if the region covers an
        area outside the image, otherwise an error is raised

    Returns:
        The image

    Examples:
    >>>

    '''
    assert isinstance(img, _np.ndarray)
    if around_point:
        assert eRegfmt == eRegionFormat.WH or eRegfmt == eRegionFormat.HW, \
            'Cropping was requested to be around a point, but the RegionFormat was not eRegionFormat.WH or eRegionFormat.HW'
        assert len(region) == 2, 'Cropping around a point, expected region to be a 2-tuple but got a %s tuple' % len(region)
    else:
        assert len(region) == 4, 'Cropping with rchw like area, expected region to be a 4-tuple but got a %s tuple' % len(region)

    r = 0; c = 0; w = 0; h = 0

    if around_point: #around_point is a 2-tuple CVXY point
        if eRegfmt == eRegionFormat.HW:
            w = region[1]; h = region[0]
        elif eRegfmt == eRegionFormat.WH:
            w = region[0]; h = region[1]
        else:
            raise ValueError('around_points was provided but an invalid eRegfmt argument was passed. eRegfmt should be WH or HW')
        c = around_point[0] - int(w/2)
        r = around_point[1] - int(h/2)
    else:
        if eRegfmt == eRegionFormat.CVXYWH:
            r = region[1]; h = region[3]; c = region[0]; w = region[2]
        elif eRegfmt == eRegionFormat.CVXYXYXYXY:
            r, c, h, w = _roi.rect_as_rchw(region)
        elif eRegfmt == eRegionFormat.RCHW:
            r = region[0]; h = region[2]; c = region[1]; w = region[3]
        elif eRegfmt == eRegionFormat.XYXYXYXY:
            pts = _roi.points_convert(region, img.shape[1], img.shape[0], _roi.ePointConversion.XYtoCVXY, _roi.ePointsFormat.XY)
            r, c, h, w = _roi.rect_as_rchw(pts)
        else:
            raise ValueError('Unknown region format enumeration in argument eRegfmt')

    fixy = lambda y: max([min([y, img.shape[0]]), 0])
    fixx = lambda x: max([min([x, img.shape[1]]), 0])

    if allow_crop_truncate:
        pts = [[fixx(c), fixy(r)], [fixx(c + w), fixy(r)], [fixx(c), fixy(r + h)], [fixx(c + w), fixy(r + h)]]
    else:
        pts = [[c, r], [c + w, r], [c, r + h], [c + w, r + h]]
        pts_xxxyyy = list(zip(*pts)) #[[1,2],[3,4] -> [[1, 3], [2, 4]]
        fpts = _baselib.list_flatten(pts)
        if min(fpts) < 0 \
                or max(pts_xxxyyy[0]) + 1 > img.shape[1] \
                or max(pts_xxxyyy[1]) + 1 > img.shape[0]:
            raise ValueError('allow_crop_truncate was false, but the crop area was out of the bounds of the image shape')

    r, c, h, w = _roi.rect_as_rchw(pts)
    h -= 1; w -= 1
    i = _roi.cropimg_xywh(img, c, r, w, h)
    return i


def resize(image, width=None, height=None, inter=_cv2.INTER_AREA):
    '''(ndarray|str, int, int, constant)->ndarray
    Resize an image, to width or height, maintaining the aspect.

    image:
        an image or path to an image
    width:
        width of image
    height:
        height of image
    inter:
        interpolation method

    Returns:
        An image

    Notes:
        Returns original image if width and height are None.
        If width or height or provided then the image is resized
        to width or height and the aspect ratio is kept.
    '''
    image = _getimg(image)
    dim = None
    (h, w) = image.shape[:2]
    image = _getimg(image)
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
    dim = (int(dim[0]), int(dim[1]))
    return _cv2.resize(image, dim, interpolation=inter)


def rotate(image, angle, no_crop=False):
    '''(str|ndarray, float, bool) -> ndarray
    Rotate an image through 'angle' degrees.

    image:
        the image as a path or ndarray
    angle:
        angle, positive for anticlockwise, negative for clockwise
    no_crop:
        if true, the image will not be cropped

    '''
    img = _getimg(image)
    (h, w) = img.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    M = _cv2.getRotationMatrix2D((cX, cY), angle, 1.0)

    if no_crop:
        cos = _np.abs(M[0, 0])
        sin = _np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        return _cv2.warpAffine(image, M, (nW, nH))

    return _cv2.warpAffine(image, M, (w, h))



def histeq_color(img, cvtToHSV=True):
    '''(ndarray)->ndarray
        Equalize histogram of color image
        '''
    img = _getimg(img)

    if cvtToHSV:
        img_yuv = _cv2.cvtColor(img, _cv2.COLOR_BGR2YUV)
    else:
        img_yuv = img

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

    img is converted to black and white, as required by cv2.createCLAHE
    '''
    img_bw = _color.togreyscale(img)
    clahe = _cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    return clahe.apply(img_bw)



@_decs.decgetimg
def histeq(im):
    '''(ndarray|str, int)->ndarray
    Histogram equalization of a grayscale image.
    '''
    img_bw = _color.togreyscale(im)
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


def homotrans(H, x, y):
    '''(3x3 ndarray,float,float)->float,float
    return homogenous coordinates
    '''
    xs = H[0, 0] * x + H[0, 1] * y + H[0, 2]
    ys = H[1, 0] * x + H[1, 1] * y + H[1, 2]
    s = H[2, 0] * x + H[2, 1] * y + H[2, 2]
    return xs / s, ys / s
