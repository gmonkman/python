# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, protected-access, unused-variable

'''unit tests for filters.py'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2
import numpy as np


import opencvlib.filters as filters
import funclib.iolib as _iolib

_TEST_COLORS = set(('white', 'black', 'blue', 'green', 'red', 'yellow'))

class Test(unittest.TestCase):
    '''unittest for streams'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'images/matt_pemb5.jpg'))

        
        self.I = cv2.imread(self.imgpath)
        self.mask = np.tri(self.I.shape[0], self.I.shape[1], dtype=int) #creates a mask where top 'sandwich' is masked out
        self.output_folder = _path.normpath(_path.join(self.modpath, 'output'))

        self.BLUE_PATCH = np.zeros((100, 100, 3))
        self.BLUE_PATCH[:, :, 0:1] = 255

        self.RED_PATCH = np.zeros((100, 100, 3))
        self.RED_PATCH[:, :, 2:3] = 255

        self.GREEN_PATCH = np.zeros((100, 100, 3))
        self.GREEN_PATCH[:, :, 1:2] = 255

        self.YELLOW_PATCH = np.zeros((100, 100, 3))
        self.YELLOW_PATCH[:, :, 1:2] = 255
        self.YELLOW_PATCH[:, :, 2:3] = 255

        self.BLACK_PATCH = np.zeros((100, 100, 3))
        self.WHITE_PATCH = np.ones((100, 100, 3))*255

        self.MOSAIC = np.vstack([np.hstack([self.BLUE_PATCH, self.RED_PATCH]), np.hstack([self.GREEN_PATCH, self.YELLOW_PATCH]), np.hstack([self.BLACK_PATCH, self.WHITE_PATCH])])



    def test_ColorInterval(self):
        '''test colorinterval class
        Instances of this class can be consumed for
        color filter/selection operations
        '''
        CI = filters.ColorInterval(filters.eColorSpace.BGR, (0, 0, 0), (255, 0, 0))
        self.assertTrue(np.array_equal(CI.lower_interval(), np.array([0, 0, 0]).astype('uint8')))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([255, 0, 0]).astype('uint8')))

        CI.color_space = filters.eColorSpace.RGB #swap to RGB, converts on the call
        self.assertTrue(np.array_equal(CI.lower_interval(), np.array([0, 0, 0]).astype('uint8')))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([0, 0, 255]).astype('uint8')))

        CI.color_space = filters.eColorSpace.Grey
        self.assertTrue(CI.lower_interval().shape[0] == 1 and len(CI.lower_interval().shape) == 1)
        self.assertTrue(CI.upper_interval().shape[0] == 1 and len(CI.lower_interval().shape) == 1)

        with self.assertRaises(ValueError):
            CI.color_space = filters.eColorSpace.BGR #this should error as we cant recreate from greyscale


    def test_ColorDetectionRGB(self):
        '''test the colordetection algo
        which takes an image and
        keeps colors (pixels) which match ranges
        set by a ColorInterval class'''
        ciBLUE = filters.ColorInterval(filters.eColorSpace.BGR, (0, 0, 0), (255, 0, 0)) #b
        ciRED = filters.ColorInterval(filters.eColorSpace.BGR, (0, 0, 0), (0, 0, 255))
        ciGREEN = filters.ColorInterval(filters.eColorSpace.BGR, (0, 0, 0), (0, 255, 0))
        ciBLACK = filters.ColorInterval(filters.eColorSpace.BGR, (0, 0, 0), (0, 0, 0))
        ciWHITE = filters.ColorInterval(filters.eColorSpace.BGR, (255, 255, 255), (255, 255, 255))
        ciYELLOW = filters.ColorInterval(filters.eColorSpace.BGR, (0, 0, 0), (0, 255, 255))
        #MOSAIC
        #BR
        #GY
        #BW
        mosaic = self.MOSAIC.copy()
        ciAll = []

        #BLUE picker
        ciAll.append(ciBLUE)
        CD = filters.ColorDetection(mosaic, ciAll, filters.eColorSpace.BGR)
        CD.detect()

        self.assertTrue(CD.boolmask.shape == CD.img_detected.shape[0:2])
        self.assertTrue(CD._img.shape == CD.img_detected.shape)
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('blue' in sCols)
        
        #BLUE and RED picker
        ciAll.append(ciRED)
        CD = filters.ColorDetection(mosaic, ciAll, filters.eColorSpace.BGR)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('red' in sCols and 'blue' in sCols)

        ciAll.append(ciGREEN)
        CD = filters.ColorDetection(mosaic, ciAll, filters.eColorSpace.BGR)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('red' in sCols and 'blue' in sCols and 'green' in sCols)

        ciAll.append(ciYELLOW)
        CD = filters.ColorDetection(mosaic, ciAll, filters.eColorSpace.BGR)
        CD.detect()
        Inverted = CD.get_inverted()
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('red' in sCols and 'blue' in sCols and 'green' in sCols and 'yellow' in sCols)

    


def _chkMBGR(mosaic):
    '''(ndarray) -> set, set
    check what colors we have
    after filter

    Returns:
        colors present in mosaic, colors NOT present in mosaic
    '''
        
    has_colors = set()
    no_colors = set()
    assert isinstance(mosaic, np.ndarray)

    #Blu Gre Blk Red Yel Whi
    for x in range(50, 200, 100):
        for y in range(50, 300, 100):
            if mosaic.item(y, x, 0) == 255 and mosaic.item(y, x, 1) == 255 and mosaic.item(y, x, 2) == 255:
                has_colors.add('white')
            if mosaic.item(y, x, 0) == 0 and mosaic.item(y, x, 1) == 0 and mosaic.item(y, x, 2) == 0:
                has_colors.add('black')
            if mosaic.item(y, x, 0) == 255 and mosaic.item(y, x, 1) == 0 and mosaic.item(y, x, 2) == 0:
                has_colors.add('blue')
            if mosaic.item(y, x, 0) == 0 and mosaic.item(y, x, 1) == 255 and mosaic.item(y, x, 2) == 0:
                has_colors.add('green')
            if mosaic.item(y, x, 0) == 0 and mosaic.item(y, x, 1) == 0 and mosaic.item(y, x, 2) == 255:
                has_colors.add('red')
            if mosaic.item(y, x, 0) == 0 and mosaic.item(y, x, 1) == 255 and mosaic.item(y, x, 2) == 255:
                has_colors.add('yellow')
            
    no_colors = _TEST_COLORS.difference(has_colors)
    return has_colors, no_colors



if __name__ == '__main__':
    unittest.main()
