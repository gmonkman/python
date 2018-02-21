# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use
'''unit tests for common'''
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2 as _cv2
import unittest
import numpy as np

import funclib.iolib as iolib
import opencvlib.common as _common
from opencvlib.view import show
from opencvlib.common import _getimg

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        lpath = 'test/bin/images/lena.jpg'
        self.lena = _getimg(lpath)


    @unittest.skip("Temporaily disabled while debugging")
    def test_chessboard(self):
        '''test making a chessboard'''
        img = _common.chessboard(100, (0, 0, 0), (255, 255, 255), cols=10, rows=14)
        _cv2.imwrite(r'c:\temp\chequer_50x67.jpg', img)
        show(img)
        iolib.folder_open(r'c:\temp')


    #@unittest.skip("Temporaily disabled while debugging")
    def test_draw_str(self):
        '''test drawing text'''
        img = np.copy(self.lena)
        _common.draw_str(img, 10, 10, 'This is some text', (0, 0, 0), scale=0.5, box_background=255)
        show(img)


if __name__ == '__main__':
    unittest.main(verbosity=2)
