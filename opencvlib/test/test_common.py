'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2
import numpy as np

import funclib.iolib as _iolib

import opencvlib.common as common

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


    def test_showarray(self):
        '''test'''
        common.showarray([self.patch, self.patch])



if __name__ == '__main__':
    unittest.main()
