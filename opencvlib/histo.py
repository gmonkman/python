# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''histogram helpers

See test_histo.py for usage examples.
'''
from warnings import warn as _warn

import cv2 as _cv2
import numpy as _np
from fast_histogram import histogram1d as _h1d

import funclib.iolib as _iolib



from opencvlib.transforms import BGR2HSV as _BGR2HSV
from opencvlib import getimg as _getimg


def histo_hsv(img, histo=None, channels=(0, 1), mask=None, accumulate=False, img_is_hsv=False, normalise=True):
    '''(str|ndarray, &ndarray, str, bool, bool)
    Get image histogram over specified channels

    img:
        file path or ndarray. Converted to HSV.
    histo:
        BYREF, pointer with previous histogram results
        Previous results will be deleted if accumulate is false
    channels:
        channels to include, default is H and S
    accumulate:
        add historgram to previous results in histo
    img_is_hsv:
        pass if the image is already in HSV format

    Returns:
    '''
    if not img_is_hsv:
        img = _BGR2HSV(img)

    if not accumulate:
        histo = None

    if not isinstance(img, list):
        img = [img]

    histSize = []
    ranges = []
    for c in channels:
        if c == 0:
            histSize.append(180)
            ranges.append(0)
            ranges.append(180)
        if c == 1:
            histSize.append(255)
            ranges.append(0)
            ranges.append(256)
        if c == 2:
            histSize.append(255)
            ranges.append(0)
            ranges.append(256)

    if mask:
        mask = mask.astype('uint8')

    h = _cv2.calcHist(img, channels, mask, histSize, ranges, histo, accumulate=accumulate) #accumulate in sel
    if normalise:
        h = _cv2.normalize(h, None, 0, 255, _cv2.NORM_MINMAX)
    return h


def histo_rgb(img, rect_patch=None, channels=(0, 1, 2), bins=256, flatten_channels=False, normalise_img=True, normalise_histo=True):
    '''(str|ndarray, 4-tuple, 1,2,3-tuple|int, int, 2-tuple, bool, bool)-> list, list .....
    Get image histogram, merging all channels. Returns the bin edges as a list
    followed by len(channels) number of lists.

    img:
        file path or ndarray. Converted to HSV.
    rect_patch:
        Get histo for this patch, format is (x, y, w, h)
    channels:
        channels to include, remember, order is BGR, e.g.
        (0,1) = BG only; (0,1,2) = BGR
    bins:
        nr. of histo bins
    flatten_channels:
        merge all channels, so R=255, G=255, B=255
        would be 255:3, rather than 255:1 255:1 255:1
    normalise_img:
        Pixel range between 0 and 1
    normalise_histo:
        normalise histo output (ie. np.sum(histo) == 1). Currently
        normalization occurs within channel.


    Note:
    This function uses the fast-histogram package rather
    than numpy's implementation because .. performance.
    https://github.com/astrofrog/fast-histogram

    Example:
    >>>im = cv2.imread()
    >>>histo_rgb('./a.jpg', bins=10, flatten_channels=True, channels=(0,2))
    [0. , 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.], #bin edges
    [0.2 ,0.8, 0, 0, 0, 0, 0, 0, 0, 0], #frequencies for channel 0
    [0.1 ,0.7, 0, 0.1, 0, 0, 0.1, 0, 0, 0]  #frequencies for channel 2
    '''
    def _dstack(slice_, hist, i):
        if i == 0:
            return slice_
        return  _np.dstack((hist, slice_))

    if rect_patch:
        assert len(rect_patch) == 4, 'The tuple rect_path should be a 4-tuple of format (x, y, w, h)'


    img = _getimg(img)
    img_ = img.copy()

    if len(img_.shape) < 1: _warn('The image was a 1D ndarray, expect 2D or 3D array')

    if rect_patch:
        img_, _ = _cropimg_xywh(img_, *rect_patch)

    if normalise_img:
        img_ = (img_ / 255)
        range_ = (0, 1)
    else:
        range_ = (0, 255)

    if isinstance(channels, int): channels = (channels,)
    hist = None
    for i, c in enumerate(channels):
        if flatten_channels or len(img_.shape) == 2: #black and white 2D ndarray, or told to flatten everything
            img_ = _np.ravel(img_)
            hist = _h1d(img_, range=range_, bins=bins)
        else:
            if c == 0:
                hist0 = _h1d(img_[:, :, 0], range=range_, bins=bins)
                if normalise_histo: hist0 /= _np.sum(hist0)
                hist = _dstack(hist0, hist, i)
            elif c == 1:
                hist1 = _h1d(img_[:, :, 1], range=range_, bins=bins)
                if normalise_histo: hist1 /= _np.sum(hist1)
                hist = _dstack(hist1, hist, i)
            elif c == 2:
                hist2 = _h1d(img_[:, :, 2], range=range_, bins=bins)
                if normalise_histo: hist2 /= _np.sum(hist2)
                hist = _dstack(hist2, hist, i)
            else:
                _warn('Got unexpected number %s in channel tuple argument' % c)

    edges = _np.linspace(range_[0], range_[1], bins + 1).tolist()

    if len(hist.shape) == 1:
        return edges, hist.tolist()

    hist = hist.squeeze().T
    if hist.shape[0] == 2:
        return edges, hist[0,: ].tolist(), hist[1, :].tolist()

    return edges, hist[0, :].tolist(), hist[1, :].tolist(), hist[2, :].tolist()


def hsv_map(x=256, y=180):
    '''(int, int) -> ndarray
    x:
        number of cols
    y:
        number of rows

    Make a hsv map as an ndarry.
    A visualisation of HSV space
    '''
    hsvm = _np.zeros((180, 256, 3), _np.uint8)
    h, s = _np.indices(hsvm.shape[:2])
    hsvm[:, :, 0] = h
    hsvm[:, :, 1] = s
    hsvm[:, :, 2] = 255
    hsvm = _cv2.cvtColor(hsvm, _cv2.COLOR_HSV2BGR)
    return hsvm



def hist_load_from_folder(wildcardedpath, strmatch=None, normalise=True, accumulate=False):
    '''(str, str|None) -> list:ndarray
    Accumulate saved histogram files in
    a folder, or return a list of histograms
    as ndarray

    wildcardedpath:
        eg c:/*.tmp
    strmatch:
        additional string which
        the filename must contain

    Normalised hist extension = '.nrm'
    Saved hist extension: '.hst'

    Returns:
        list of histogram(s) as ndarrays
    '''
    list_arr = []
    first = True
    for f in _iolib.file_list_glob_generator(wildcardedpath):
        if isinstance(strmatch, str):
            dummy, fname, dummy = _iolib.get_file_parts(f)
            if  strmatch.startswith(fname):
                continue

        if accumulate:
            if first:
                arr = _np.load(f)
                first = False
            else:
                arr += _np.load(f)
        else:
            arr = _np.load(f)
            if isinstance(arr, _np.ndarray) and normalise:
                arr = _cv2.normalize(arr, None, 0, 255, _cv2.NORM_MINMAX)
            list_arr.append(arr)

    if accumulate:
        if isinstance(arr, _np.ndarray) and normalise:
            list_arr = [_cv2.normalize(arr, None, 0, 255, _cv2.NORM_MINMAX)]
    return list_arr




class VisualColorHisto():
    '''visualise the hue and saturation histogram of an image

    Example:
        H = histo.VisualColorHisto(self.Grass)
        cv2.waitKey(0)
        H(cv2.cvtColor(self.Grass, cv2.COLOR_BGR2GRAY))
    '''

    def __init__(self, img, win_name='hist'):
        '''(ndarray|str) -> void

        img:
            BGR image, or filepath
        '''
        self._hist_scale = 10
        self._hsv_map = hsv_map()
        self._win_name = win_name
        self._img = _getimg(img)
        self._histimg = None
        self._hidden = False
        _cv2.imshow('hsv_map', self._hsv_map)
        _cv2.namedWindow(self._win_name, 0)
        _cv2.createTrackbar('scale', self._win_name, self._hist_scale, 32, self.set_scale)
        self.refresh()


    def __call__(self, img):
        self._img = _getimg(img)
        self.refresh()

    def set_scale(self, val):
        '''set scale'''
        self._hist_scale = val
        self.refresh()


    def refresh(self):
        '''process the img'''
        small = _cv2.pyrDown(self._img)
        hsv = _cv2.cvtColor(small, _cv2.COLOR_BGR2HSV)
        dark = hsv[..., 2] < 32
        hsv[dark] = 0
        h = _cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        h = _np.clip(h * 0.005 * self._hist_scale, 0, 1)
        vis = self._hsv_map * h[:, :, _np.newaxis] / 255.0
        self._histimg = vis
        _cv2.imshow('hist', vis)


def _cropimg_xywh(img, x, y, w, h):
    '''(str|ndarray, int, int, int, int)->ndarray, bool
    Return a rectangular region from an image. Also see transforms.crop.

    Crops to the edge if area would be outside the
    bounds of the image.

    x, y:
        Define the point form which to crop, CVXY assumed
    w, h:
        Size of region

    Returns:
        cropped image area,
        boolean indicating if crop was truncated to border
        of the image

    Notes:
        transforms.crop provides conversion and cropping
        around a point
    '''
    assert isinstance(img, _np.ndarray)
    relu = lambda x: max(0, x)
    crop_truncated = (relu(y), min(y+h, img.shape[0]), relu(x), min(x+w, img.shape[1]))
    crop = (y, y+h, x, x+w)
    return img[relu(y):min(y+h, img.shape[0]), relu(x):min(x+w, img.shape[1])], crop_truncated == crop