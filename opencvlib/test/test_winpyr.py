# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import

'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as _iolib
import opencvlib.view as view
import opencvlib.winpyr as winpyr

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)

    #@unittest.skip("Temporaily disabled test_showarray")
    def test_pyramid_pts(self):
        '''test'''
        pts = [[0, 0], [100, 100], [0, 100], [100, 0]]
        scales = []; points = []; images = []
        for img, pts_, scale in winpyr.pyramid_pts(self.I, pts):
            scales.append(scale)
            points.append(points)
            img_ = view.draw_points(pts_, img)
            images.append(img_)
            print(scale)



if __name__ == '__main__':
    unittest.main()
