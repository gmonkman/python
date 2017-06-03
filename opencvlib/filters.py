# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''keypoint helpers
keypoint detection is handled in features.py'''
from enum import Enum as _Enum
import numpy as _np
import cv2 as _cv2


import opencvlib.transforms as _transforms
from opencvlib import getimg as _getimg

class eColorSpace(_Enum):
    '''colorspace types'''
    HSV = 0
    RGB = 1
    BGR = 2
    Grey = 3


class ColorInterval():
    '''class to store a filter range
    in defined color space and
    convert between them.
    
    Initialise with tuples where tuples are paired to represent a range
    e.g. start=(0,0,0), finish=(255,255,255) is then enture range
    '''
    BGR_RED = _np.array([[17, 15, 100], [50, 56, 200]]).astype('uint8')
    BGR_BLUE = _np.array([[86, 31, 4], [220, 88, 50]]).astype('uint8')
    BGR_GREEN = _np.array([[103, 86, 65], [145, 133, 128]]).astype('uint8')

    def __init__(self, color_space=eColorSpace.BGR, start=(None, None, None), finish=(None, None, None)):
        self._start = start
        self._finish = finish
        self._color_space = color_space
        self._check_intervals()
        if color_space == eColorSpace.Grey:
            if len(start) != 1 and len(finish) != 1:
                raise ValueError('Color space set to grey, but tuple start and /or finish length greater not equal 1')
        else:
            self._asnumpyinterval = _np.array([start, finish]).astype('uint8')



    
    @property
    def color_space(self):
        '''color_space getter'''
        return self._color_space
    @color_space.setter
    def color_space(self, color_space):
        '''color_space setter'''
        self._asnumpyinterval = self._cvt(color_space)
        self._color_space = color_space
        


    def _check_intervals(self):
        f = lambda x: x if max(x) <= 255 and min(x) >= 0 else None
        if f(self._start) is None:
            raise ValueError('Start range was invalid')

        if f(self._finish) is None:
            raise ValueError('Finish range was invalid')
    

    def lower_interval(self):
        '''return the lbound numpy array
        eg [[0,0,0]]
        '''
        return self._asnumpyinterval[0]


    def upper_interval(self):
        '''return the lbound numpy array
        eg [[0,0,0]]
        '''
        return self._asnumpyinterval[1]
    
     
    def _cvt(self, to):
        '''(Enum:eColorSpace) -> ndarray
        Given a range conversion converts the
        start and finish set on initialisation
        to defined space and returns the ndarray
        as a single range.

        to:
            target colour interval format
        Return:
            Single ndarray of shape 2,3.
            e.g. ([[0,0,0], [255,255,255]])

        '''
        assert isinstance(to, eColorSpace)

        toImg = lambda x: _np.reshape(x, [1, 2, 3])
        toBWImg = lambda x: _np.reshape(x, [1, 2])

        toBound = lambda x: _np.reshape(x, [2, 3])
        toBoundBW = lambda x: _np.reshape(x, [2, 1])

        if self._asnumpyinterval.shape[1] >= 3:
            tmp = toImg(self._asnumpyinterval.copy())
        else:
            tmp = toBWImg(self._asnumpyinterval.copy())

        if self._color_space == eColorSpace.BGR:
            if to == eColorSpace.BGR:
                tmp = self._asnumpyinterval.copy()
            elif to == eColorSpace.Grey:
                tmp = _transforms.togreyscale(tmp)
                tmp = toBoundBW(tmp)
            elif to == eColorSpace.HSV:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_BGR2HSV)
                tmp = toBound(tmp)
            elif to == eColorSpace.RGB:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_BGR2RGB)
                tmp = toBound(tmp)
            else:
                raise ValueError('Unexpected conversion options encountered')
            return tmp

        if self._color_space == eColorSpace.HSV:
            if to == eColorSpace.BGR:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_HSV2BGR)
                tmp = toBound(tmp)
            elif to == eColorSpace.Grey:
                tmp = _transforms.HSVtoGrey(tmp)
                tmp = toBoundBW(tmp)
            elif to == eColorSpace.HSV:
                tmp = self._asnumpyinterval.copy()
            elif to == eColorSpace.RGB:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_HSV2RGB)
                tmp = toBound(tmp)
            else:
                raise ValueError('Unexpected conversion options encountered')
            return tmp
        
        if self._color_space == eColorSpace.RGB:
            if to == eColorSpace.BGR:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_RGB2BGR)
                tmp = toBound(tmp)
            elif to == eColorSpace.Grey:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_RGB2GRAY)
                tmp = toBoundBW(tmp)
            elif to == eColorSpace.HSV:
                tmp = _cv2.cvtColor(tmp, _cv2.COLOR_RGB2HSV)
                tmp = toBound(tmp)
            elif to == eColorSpace.RGB:
                tmp = self._asnumpyinterval
            else:
                raise ValueError('Unexpected conversion options encountered')
            return tmp


        if self._color_space == eColorSpace.Grey:
            if to == eColorSpace.Grey:
                return self._asnumpyinterval
            else:
                raise ValueError('Cannot get color intervals from a grey scale interval')

        raise ValueError('Unexpected conversion options encountered')



class ColorDetection():
    '''color detection stuff'''

    def __init__(self, img, ColInt, color_space=eColorSpace.HSV):
        '''(ndarray|str, class:ColorInterval|list:class:ColorInterval, Enum:eColorSpace) -> void

        img:
            Will load img if a path is passed.
        color_space:
           Convert to this colorspace, assumes OpenCV format (BGR) of img
        ColInt:
            Class ColorInterval or list like of ColorInterval instances.
            Colorinterval class specifies an color interval and the
            format of that interval (eg, RGB, BGR, HSV).
            If color_space is Grey, then the image will be converted to greyscale            
        '''
        img = _getimg(img)
        if color_space == eColorSpace.BGR:
            pass
        elif color_space == eColorSpace.HSV:
            img = _cv2.cvtColor(img, _cv2.COLOR_BGR2HSV)
        elif color_space == eColorSpace.RGB:
            img = _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)
        elif color_space == eColorSpace.Grey:
            img = _transforms.togreyscale(img)
        else:
            raise ValueError('Unsupported color space enumeration')


        self._color_space = color_space
        self._ColInt = ColInt
        self._img = img

        #self.boolmask = None
        self.img_detected = None


    def detect(self):
        '''
        Carry out the detection.

        Set class members and img_detected
        '''
        if isinstance(self._ColInt, ColorInterval):
            intervals = [self._ColInt]
        else:
            intervals = self._ColInt

        I = self._img.copy()
        m = _np.ndarray([])
        first = True
        for ci in intervals:
            assert isinstance(ci, ColorInterval)
            if first:
                m = _cv2.inRange(I, ci.lower_interval(), ci.upper_interval())
                first = False
            else:
                m = _cv2.bitwise_or(m, _cv2.inRange(I, ci.lower_interval(), ci.upper_interval()))
            
        I = _cv2.bitwise_and(I, I, mask=m) 
        self.img_detected = I    
        #self.boolmask = m.astype('bool')


