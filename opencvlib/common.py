# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, reimported, superfluous-parens

'''
This module contains some common routines used by other samples.
From https://github.com/opencv/opencv/blob/master/samples/python/common.py#L1
'''

from glob import glob as _glob
from enum import Enum as _Enum

import numpy as _np
import cv2 as _cv2
import imghdr as _imghdr
import fuckit as _fuckit

from funclib.iolib import fixp as _fixp
from funclib.stringslib import read_number as _read_number

import opencvlib.decs as _decs

__all__ = ['show', 'getimg', 'Info', 'ImageInfo', 'homotrans', 'checkwaitkey', 'getwaitkey']




class eImgType(_Enum):
    '''bitwise enum to hold img information'''
    COLOR_BW = 2**0
    COLOR_COLOR = 2**1
    COLOR_UNKNOWN = 2**2
    CHANNEL_1 = 2**3
    CHANNEL_2 = 2**4
    CHANNEL_3 = 2**5
    CHANNEL_4 = 2**6
    CHANNEL_UNKOWN = 2**7
    DEPTH8BIT = 2**8
    DEPTH16BIT = 2**9
    DEPTH32BIT = 2**10
    DEPTH_FLOAT = 2**11
    DEPTH_UNKNOWN = 2**12



def getimg(img, outflag=_cv2.IMREAD_UNCHANGED):
    '''(ndarray|str)->ndarray
    tries to load the image if its a path and returns the loaded ndarray
    otherwise returns input img if it is an ndarray

    Also consider using @decs._decs.decgetimg decorator
    '''
    if isinstance(img, str):
        return _cv2.imread(_fixp(img), outflag)
    else:
        return img


def homotrans(H, x, y):
    '''(3x3 ndarray,float,float)->float,float
    return homogenous coordinates
    '''
    xs = H[0, 0] * x + H[0, 1] * y + H[0, 2]
    ys = H[1, 0] * x + H[1, 1] * y + H[1, 2]
    s = H[2, 0] * x + H[2, 1] * y + H[2, 2]
    return xs / s, ys / s


def getwaitkey(i):
    '''get a string representation
    of the key pressed to end opencv.waitkey
    '''
    return chr(i & 255)


def checkwaitkey(key_as_string, waitkeyval):
    '''pass in a character, returns true if matched'''
    return getwaitkey(waitkeyval) == key_as_string


@_decs.decgetimg
def show(img, title='img', max_width=800, waitsecs=0):
    '''(str|ndarray)->int, str
    Show an image, passing in a path or ndarray

    Returns the key value pressed and the title
    <no key>=255
    y=121
    <space>=32
    n=110
    '''
    w, h = ImageInfo.getsize(img)

    if w > max_width:
        ratio = max_width/w
        new_w = int(max_width)
        new_h = int(h * ratio)
    else:
        new_w = int(w)
        new_h = int(h)

    waitsecs = int(_read_number(waitsecs)*1000)
    if waitsecs < 0:
        waitsecs = 0

    _cv2.namedWindow(title, _cv2.WINDOW_NORMAL)
    _cv2.resizeWindow(title, new_w, new_h)
    _cv2.imshow(title, img)
    key = _cv2.waitKey(waitsecs) #255 is no key press

    _cv2.destroyAllWindows()
    return key, title


@_decs.decgetimg
def mosaic(imgs, cols=None, pad=True):
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

    cols = _math.ceil(_math.sqrt(len(imgs))) if cols is None else cols

    imgs = pad_images(imgs)

    I = iter(imgs)
    img0 = next(I)

    pad = _np.zeros_like(img0)
    I = _it.chain([img0], I)
    rows = _grouper(cols, I, pad)
    return _np.vstack(map(_np.hstack, rows))


# region UTIL CLASSES
class _BaseImg(object):
    '''inherit from, sets up an image in the init
    '''
    silent = False

    def __init__(self, img=None):
        '''ndarray
        '''
        if not img is None:
            try:
                self.img = getimg(img)
            except Exception as e:
                if not ImageInfo.silent:
                    print('Failed to load image in init. Error was ' + str(e))


class Info(object):
    '''general info about versions, system etc'''
    def __init(self):
        pass


    @staticmethod
    def is_cv2():
        '''if we are using OpenCV 2, then our _cv2.__version__ will start
        with '2.'
        '''
        return Info.opencv_check_version("2.")


    @staticmethod
    def is_cv3():
        '''
        if we are using OpenCV 3.X, then our _cv2.__version__ will start
        with '3.'
        '''
        return Info.opencv_check_version("3.")


    @staticmethod
    def opencv_check_version(major):
        '''(int,_cv2 library)->bool
        Checks major version of _cv2.
        eg. opencv_check_version("3.") will be true for any _cv2 version 3.x.x

        If the supplied library is None, _cv2 will be imported
        '''
        return _cv2.__version__.startswith(major)




class ImageInfo(_BaseImg):
    '''general info about an image'''

    def __init__(self, img=None):
        super().__init__(img)


    @staticmethod
    @_decs.decgetimg
    def _isbw(img):
        #img is a numpy.ndarray, loaded using cv2.imread
        if len(img.shape) > 2:
            looks_like_rgbbw = not False in ((img[:, :, 0:1] == img[:, :, 1:2]) == (img[:, :, 1:2] == img[:, :, 2:3]))
            looks_like_hsvbw = not False in ((img[:, :, 0:1] == 0) == ((img[:, :, 1:2]) == 0))
            return looks_like_rgbbw or looks_like_hsvbw
        else:
            return True


    @staticmethod
    @_decs.decgetimg
    def isbw(img):
        '''is img black and white, even if it has multichannels'''
        return bool(eImgType.COLOR_BW.value & ImageInfo.typeinfo(img))


    @staticmethod
    @_decs.decgetimg
    def typeinfo(img):
        '''(ndarray|str)->int
        Return information about the image
        which can be compared bitwise with
        the enum eImgType

        Returns 0 if not an ndarray
        '''
        if not isinstance(img, _np.ndarray):
            return 0

        out = 0
        if img.dtype == 'uint8':
            out += eImgType.DEPTH8BIT.value
        elif img.dtype == 'uint16':
            out += eImgType.DEPTH16BIT.value
        elif img.dtype == 'uint32':
            out += eImgType.DEPTH32BIT.value
        elif 'float' in str(img.dtype):
            out += eImgType.DEPTH_FLOAT.value
        else:
            out += eImgType.DEPTH_UNKNOWN.value
            raise ValueError('Unknown image color depth. Numpy array type not IN uint8, uint16, uint32, float.')

        if len(img.shape) == 2:
            out += eImgType.COLOR_BW.value
            out += eImgType.CHANNEL_1.value
        elif len(img.shape) == 3:
            if img.shape[2] == 3:
                out += eImgType.CHANNEL_3.value
                if ImageInfo._isbw(img):
                    out += eImgType.COLOR_BW.value
                else:
                    out += eImgType.COLOR_COLOR.value
            elif img.shape[2] == 4:
                out += eImgType.CHANNEL_4.value
                if ImageInfo._isbw(img):
                    out += eImgType.COLOR_BW.value
                else:
                    out += eImgType.COLOR_COLOR.value
            elif img.shape[2] == 2:
                out += eImgType.CHANNEL_2.value
                out += eImgType.COLOR_UNKNOWN.value
        return out

    @staticmethod
    @_decs.decgetimgpil
    def is_higher_res(img, w, h, either=False):
        '''(ndarray|str, int, int, bool)->bool
        Check if img is
        If either is false, image is considered higher res
        if both w and h are greater than the image w, h
        '''
        x, y = ImageInfo.resolution(img)
        if either:
            if not w is None:
                return x < w
            if not h is None:
                return y < h
            return False
        else:
            if not w is None and not h is None:
                return x < w and y < h
            else:
                return False


    @staticmethod
    @_decs.decgetimgpil
    def is_lower_res(img, w, h, either=True):
        '''(ndarray|str, int, int, bool)->bool
        Check if img is lower res than that defined by w and h.
        If either is true, image is considered lower res
        if either the width or the height is less than w, h
        '''
        x, y = ImageInfo.resolution(img)
        if either:
            if not w is None:
                return x > w
            if not h is None:
                return y > h
            return False
        else:
            if not w is None and not h is None:
                return x > w and y > h
            else:
                return False


    @staticmethod
    @_decs.decgetimgpil
    def resolution(img):
        '''(str|ndarray)->int,int
        width,height
        '''
        if isinstance(img, _np.ndarray):
            h, w = img.shape[:2]
            return w, h
        else:
            return [img.width, img.height]


    @staticmethod
    def is_image(file_path, try_load=False):
        '''(str)->bool
        Pass in a file string and see if it looks like an image.
        If try_load is true, we try and load the file using _cv2.imread (costly)
        '''
        ret = False
        if not _imghdr.what(file_path) is None:
            ret = True
            if try_load:
                with _fuckit:
                    ret = False
                    img = _cv2.imread(file_path)
                    if isinstance(img, _np.ndarray):
                        ret = True
        return ret


    @staticmethod
    def get_image_resolutions(glob_str):
        '''(str)->list of lists
        Takes a path with wildcard (eg C:/temp/*.jpg') and using wildcards globs through all images
        Returns all unique image resolutions (column, row) as
        list of lists
        [[800,600],[1024,768]]
        '''
        dims = []
        for pic in _glob(glob_str):
            if ImageInfo.is_image(pic):  # does the work
                with _fuckit:
                    img = _cv2.imread(pic)
                if isinstance(img, _np.ndarray):
                    h, w = img.shape[:2]
                    e = [w, h]
                    if e not in dims:
                        dims.append(e)
        return dims


    @staticmethod
    def getsize(img):
        '''(ndarray|str)->int, int
        return width and height of an image (in that order)

        Can pass in a file path or ndarray
        '''
        if isinstance(img, str):
            img = _cv2.imread(img)

        h, w = img.shape[:2]
        return w, h


    @staticmethod
    def getsize_dict(img):
        '''(ndarray|str)->{'w':cols,'h':rows}
        return width and height of an image (in that order)

        Can pass in a file path or ndarray
        '''
        if isinstance(img, str):
            img = _cv2.imread(img)

        h, w = img.shape[:2]
        return {'w': w, 'h': h}
# endregion
