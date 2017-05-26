'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2
import numpy as np

import opencvlib.features as features
import funclib.iolib as _iolib



class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(_path.join(pth, 'myconfig.cfg'))
        self.imgpath = _path.normpath(_path.join(modpath, 'images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        self.mask = np.tri(I.shape[0], I.shape[1], dtype=int) #creates a mask where top 'sandwich' is masked out


    def test_OpenCV_DensSIFT(self):
        D = features.OpenCV_DenseSIFT('c:/temp/')
        D(I, mask=None)
        D.extract_keypoints()
        D.extract_descriptors()

        D(I, mask)
        D.extract_keypoints()
        D.extract_descriptors()



if __name__ == '__main__':
    unittest.main()
