# pylint: disable=C0103, too-few-public-methods,
# locally-disabled,no-self-use, unused-argument,reimported

'''
This module contains some common routines used by other samples.
From https://github.com/opencv/opencv/blob/master/samples/python/common.py#L1
'''
# region imports
from glob import glob as _glob

import numpy as _np
import cv2 as _cv2
import imghdr as _imghdr
import fuckit as _fuckit

from funclib.iolib import fixp as _fixp
from funclib.stringslib import read_number as _read_number

import decs as _decs

__all__ = ['show', 'getimg', 'Info', 'ImageInfo', 'homotrans', 'checkwaitkey', 'getwaitkey']
# endregion


def getimg(img):
    '''(ndarray|str)->ndarray
    tries to load the image if its a path and returns the loaded ndarray
    otherwise returns input img if it is an ndarray

    Also consider using @decs._decs.decgetimg decorator
    '''
    if isinstance(img, str):
        return _cv2.imread(_fixp(img), -1)
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
