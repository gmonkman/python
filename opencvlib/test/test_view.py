'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2
import numpy as np

import funclib.iolib as _iolib
import opencvlib.view as view


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.patch = np.array([[0, 0, 0, 0, 0], [0, 255, 255, 255, 0], [0, 255, 255, 255, 0], [0, 255, 255, 255, 0], [0, 0, 0, 0, 0]])
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        self.mask = np.tri(self.I.shape[0], self.I.shape[1], dtype=int) #creates a mask where top 'sandwich' is masked out
        self.output_folder = _path.normpath(_path.join(self.modpath, 'output'))

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
        self.MOSAIC_RGB = cv2.cvtColor(self.MOSAIC_BGR, cv2.COLOR_BGR2RGB)
        self.MOSAIC_GREY = cv2.cvtColor(self.MOSAIC_BGR, cv2.COLOR_BGR2GRAY)


    @unittest.skip("Temporaily disabled test_showarray")
    def test_showarray(self):
        '''test'''
        view.showarray([self.patch, self.patch])



if __name__ == '__main__':
    unittest.main()
