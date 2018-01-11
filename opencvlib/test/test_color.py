# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, protected-access, unused-variable
'''unit tests for color module'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import numpy as np
import cv2


import funclib.iolib as _iolib
import opencvlib.color as color
from opencvlib.color import eColorSpace
from opencvlib.view import show

_TEST_COLORS = set(('white', 'black', 'blue', 'green', 'red', 'yellow'))

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))

        
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

        self.MOSAIC_BGR = np.vstack([np.hstack([self.BLUE_PATCH, self.RED_PATCH]), np.hstack([self.GREEN_PATCH, self.YELLOW_PATCH]), np.hstack([self.BLACK_PATCH, self.WHITE_PATCH])]).astype('uint8')
        self.MOSAIC_HSV = cv2.cvtColor(self.MOSAIC_BGR, cv2.COLOR_BGR2HSV)
        self.MOSAIC_GREY = cv2.cvtColor(self.MOSAIC_BGR, cv2.COLOR_BGR2GRAY)
        self.MOSAIC_RGB = cv2.cvtColor(self.MOSAIC_BGR, cv2.COLOR_BGR2RGB)


    @unittest.skip("Temporaily disabled while debugging")
    def test_cvt(self):
        '''test_cvt
        test convert function'''
        I = self.MOSAIC_BGR.copy()
        T = color.cvt(I, eColorSpace.BGR, eColorSpace.Grey)
        self.assertTrue(np.array_equal(T, self.MOSAIC_GREY))

        T = color.cvt(I, eColorSpace.BGR, eColorSpace.HSV)
        self.assertTrue(np.array_equal(T, self.MOSAIC_HSV))

        T = color.cvt(I, eColorSpace.BGR, eColorSpace.RGB)
        self.assertTrue(np.array_equal(T, self.MOSAIC_RGB))


        I = self.MOSAIC_RGB.copy()
        T = color.cvt(I, eColorSpace.RGB, eColorSpace.Grey)
        self.assertTrue(np.array_equal(T, self.MOSAIC_GREY))

        T = color.cvt(I, eColorSpace.RGB, eColorSpace.HSV)
        self.assertTrue(np.array_equal(T, self.MOSAIC_HSV))

        T = color.cvt(I, eColorSpace.RGB, eColorSpace.BGR)
        self.assertTrue(np.array_equal(T, self.MOSAIC_BGR))


        I = self.MOSAIC_HSV.copy()
        T = color.cvt(I, eColorSpace.HSV, eColorSpace.Grey)
        self.assertTrue(np.array_equal(T, self.MOSAIC_HSV[:, :, 2:3].squeeze())) #HSV gray different from BGR/RGB->Grey

        T = color.cvt(I, eColorSpace.HSV, eColorSpace.RGB)
        self.assertTrue(np.array_equal(T, self.MOSAIC_RGB))

        T = color.cvt(I, eColorSpace.HSV, eColorSpace.BGR)
        self.assertTrue(np.array_equal(T, self.MOSAIC_BGR))


    @unittest.skip("Temporaily disabled while debugging")
    def test_ColorInterval(self):
        '''test_ColorInterval
        Instances of this class can be consumed for
        color filter/selection operations
        '''
        CI = color.ColorInterval(color.eColorSpace.BGR, (0, 0, 0), (255, 0, 0))
        self.assertTrue(np.array_equal(CI.lower_interval(), np.array([0, 0, 0]).astype('uint8')))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([255, 0, 0]).astype('uint8')))

        CI.color_space = color.eColorSpace.RGB #swap to RGB, converts on the call
        self.assertTrue(np.array_equal(CI.lower_interval(), np.array([0, 0, 0]).astype('uint8')))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([0, 0, 255]).astype('uint8')))

        CI.color_space = color.eColorSpace.Grey
        self.assertTrue(CI.lower_interval().shape[0] == 1 and len(CI.lower_interval().shape) == 1)
        self.assertTrue(CI.upper_interval().shape[0] == 1 and len(CI.lower_interval().shape) == 1)

        with self.assertRaises(UserWarning):
            CI = color.ColorInterval(color.eColorSpace.HSV, (0, 0, 0), (180, 0, 0))
            CI = color.ColorInterval(color.eColorSpace.HSV, (180, 0, 0), (0, 0, 0))
            CI = color.ColorInterval(color.eColorSpace.HSV, (0, 0, 0), (0, 0, 256))
            CI = color.ColorInterval(color.eColorSpace.HSV, (0, 256, 0), (0, 0, 0))

        CI = color.ColorInterval(color.eColorSpace.HSV, (0, 0, 0), (179, 0, 0))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([179, 0, 0]).astype('uint8')))

        CI = color.ColorInterval(color.eColorSpace.HSV255255255, (255, 100, 250), (255, 100, 255))
        self.assertTrue(np.array_equal(CI.lower_interval(), np.array([179, 100, 250]).astype('uint8')))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([179, 100, 255]).astype('uint8')))

        CI = color.ColorInterval(color.eColorSpace.HSV360100100, (360, 100, 100), (360, 100, 100))
        self.assertTrue(np.array_equal(CI.lower_interval(), np.array([179, 255, 255]).astype('uint8')))
        self.assertTrue(np.array_equal(CI.upper_interval(), np.array([179, 255, 255]).astype('uint8')))


    @unittest.skip("Temporaily disabled while debugging")
    def test_ColorDetectionBGR(self):
        '''test_ColorDetectionBGR
        which takes an image and
        keeps colors (pixels) which match ranges
        set by a ColorInterval class'''
        ciBLUE = color.ColorInterval(color.eColorSpace.BGR, (0, 0, 0), (255, 0, 0)) #b
        ciRED = color.ColorInterval(color.eColorSpace.BGR, (0, 0, 0), (0, 0, 255))
        ciGREEN = color.ColorInterval(color.eColorSpace.BGR, (0, 0, 0), (0, 255, 0))
        ciBLACK = color.ColorInterval(color.eColorSpace.BGR, (0, 0, 0), (0, 0, 0))
        ciWHITE = color.ColorInterval(color.eColorSpace.BGR, (255, 255, 255), (255, 255, 255))
        ciYELLOW = color.ColorInterval(color.eColorSpace.BGR, (0, 0, 0), (0, 255, 255))
        #MOSAIC
        #BR
        #GY
        #BW
        mosaic = self.MOSAIC_BGR.copy()
        ciAll = []

        #BLUE picker
        ciAll.append(ciBLUE)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.BGR)
        CD.detect()

        self.assertTrue(CD._img.shape == CD.img_detected.shape)
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('blue' in sCols)
        
        #BLUE and RED picker
        ciAll.append(ciRED)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.BGR)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('red' in sCols and 'blue' in sCols)

        ciAll.append(ciGREEN)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.BGR)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('red' in sCols and 'blue' in sCols and 'green' in sCols)

        ciAll.append(ciYELLOW)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.BGR)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.img_detected)
        self.assertTrue('red' in sCols and 'blue' in sCols and 'green' in sCols and 'yellow' in sCols)
   


    #@unittest.skip("Temporaily disabled while debugging")
    def test_ColorDetectionHSV360(self):
        '''test_ColorDetectionHSV360
        test the colordetection algo
        which takes an image and
        keeps colors (pixels) which match ranges
        set by a ColorInterval class'''
        ciBLUE = color.ColorInterval(color.eColorSpace.HSV360100100, (230, 90, 90), (250, 100, 100))
        ciRED1 = color.ColorInterval(color.eColorSpace.HSV360100100, (350, 90, 90), (360, 100, 100))
        ciRED2 = color.ColorInterval(color.eColorSpace.HSV360100100, (0, 90, 90), (10, 100, 100))
        ciGREEN = color.ColorInterval(color.eColorSpace.HSV360100100, (110, 90, 90), (130, 100, 100))
        ciYELLOW = color.ColorInterval(color.eColorSpace.HSV360100100, (50, 90, 90), (70, 100, 100))
        ciBLACK = color.ColorInterval(color.eColorSpace.HSV360100100, (0, 0, 0), (255, 0, 0))
        ciWHITE = color.ColorInterval(color.eColorSpace.HSV360100100, (0, 0, 255), (255, 0, 255))
        #MOSAIC
        #BR
        #GY
        #BW
        mosaic = self.MOSAIC_HSV.copy()
        show(mosaic)
        ciAll = []

        #BLUE picker
        ciAll.append(ciBLUE)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.HSV, no_conversion=True)
        CD.detect()
        self.assertTrue(CD._img.shape == CD.img_detected.shape)
        self.assertTrue(CD._img.shape == CD.detected_as_bgr().shape)
        sCols, sNoCols = _chkMBGR(CD.detected_as_bgr())
        self.assertTrue('blue' in sCols)

        #BLUE picker
        ciAll.append(ciBLUE)
        CD = color.ColorDetection(self.MOSAIC_BGR, ciAll, color.eColorSpace.HSV, no_conversion=False)
        CD.detect()
        self.assertTrue(CD._img.shape == CD.img_detected.shape)
        self.assertTrue(CD._img.shape == CD.detected_as_bgr().shape)
        sCols, sNoCols = _chkMBGR(CD.detected_as_bgr())
        self.assertTrue('blue' in sCols)
        

        #BLUE and RED picker
        ciAll.extend([ciRED1, ciRED2])
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.HSV, no_conversion=True)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.detected_as_bgr())
        self.assertTrue('red' in sCols and 'blue' in sCols)

        ciAll.append(ciGREEN)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.HSV, no_conversion=True)
        CD.detect()
        sCols, sNoCols = _chkMBGR(CD.detected_as_bgr())
        self.assertTrue('red' in sCols and 'blue' in sCols and 'green' in sCols)

        ciAll.append(ciYELLOW)
        CD = color.ColorDetection(mosaic, ciAll, color.eColorSpace.HSV, no_conversion=True)
        CD.detect()
        show(CD.detected_as_bgr())
        sCols, sNoCols = _chkMBGR(CD.detected_as_bgr())
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
    unittest.main(verbosity=2)
    
