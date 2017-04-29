# pylint: disable=C0103, too-few-public-methods, locally-disabled,no-self-use, unused-argument,reimported

'''
This module contains some common routines used by other samples.
From https://github.com/opencv/opencv/blob/master/samples/python/common.py#L1
'''
# region imports
from os import path
from glob import glob

import numpy as np
import cv2
import imghdr

import fuckit

__all__ = ['show', 'getimg', 'Info', 'fixp', 'ImageInfo', 'homotrans']
# endregion


def fixp(pth):
    '''(str)->str
    basically path.normpath
    '''
    return path.normpath(pth)


def getimg(img):
    '''(ndarray|str)->ndarray
    tries to load the image if its a path and returns the loaded ndarray
    otherwise returns input img if it is an ndarray
    '''
    if isinstance(img, str):
        return cv2.imread(fixp(img), -1)
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


def show(img):
    '''(str|ndarray)->void
    Show an image, passing in a path or ndarray
    '''
    if isinstance(img, str):
        img = fixp(img)
        img = cv2.imread(img)

    cv2.imshow('img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


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
        '''if we are using OpenCV 2, then our cv2.__version__ will start
        with '2.'
        '''
        return Info.opencv_check_version("2.")

    @staticmethod
    def is_cv3():
        '''
        if we are using OpenCV 3.X, then our cv2.__version__ will start
        with '3.'
        '''
        return Info.opencv_check_version("3.")

    @staticmethod
    def opencv_check_version(major, lib=None):
        '''(int,cv2 library)->bool
        Checks major version of cv2.
        eg. opencv_check_version("3.") will be true for any cv2 version 3.x.x

        If the supplied library is None, cv2 will be imported
        '''
        if lib is None:
            import cv2 as lib

        # return whether or not the current OpenCV version matches the
        # major version number
        return lib.__version__.startswith(major)


class ImageInfo(_BaseImg):
    '''general info about an image'''

    def __init__(self, img=None):
        super().__init__(img)

    @staticmethod
    def resolution(img):
        '''ndarray
        width,height
        '''
        assert isinstance(img, np.ndarray)
        return [img.shape[1], img.shape[0]]

    @staticmethod
    def is_image(file_path, try_load=False):
        '''(str)->bool
        Pass in a file string and see if it looks like an image.
        If try_load is true, we try and load the file using cv2.imread (costly)
        '''
        ret = False
        if not imghdr.what(file_path) is None:
            ret = True
            if try_load:
                with fuckit:
                    ret = False
                    img = cv2.imread(file_path)
                    if isinstance(img, np.ndarray):
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
        for pic in glob(glob_str):
            if ImageInfo.is_image(pic): #does the work
                with fuckit:
                    img = cv2.imread(pic)
                if isinstance(img, np.ndarray):
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
            img = cv2.imread(img)

        h, w = img.shape[:2]
        return w, h

    @staticmethod
    def getsize_dict(img):
        '''(ndarray|str)->{'w':cols,'h':rows}
        return width and height of an image (in that order)

        Can pass in a file path or ndarray
        '''
        if isinstance(img, str):
            img = cv2.imread(img)

        h, w = img.shape[:2]
        return {'w': w, 'h': h}
# endregion
