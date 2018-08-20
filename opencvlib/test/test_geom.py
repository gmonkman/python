# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, no-self-use, unused-variable

'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
from math import sin, cos, tan, radians, degrees

import cv2
import numpy as np

import funclib.iolib as iolib
import opencvlib.geom as geom
from opencvlib.view import show
from opencvlib.common import draw_points


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        self.Patch = np.array(np.ones((750, 1400, 3))) * 255





    @unittest.skip("Temporaily disabled while debugging")
    def test_points_rmsd(self):
        '''rmsd'''
        x = geom.points_rmsd([[1, None], [2, 10]], [[1, 1], [2, 10]])
        self.assertEqual(x, 0)
        x = geom.points_rmsd([[1, None], [2, 10]], [[1, 1], [2, 5]])
        pass


    @unittest.skip("Temporaily disabled while debugging")
    def test_flip_points(self):
        '''test'''
        pts = [[50, 50], [100, 50], [100, 100], [50, 100]]
        pts_flip_h = geom.flip_points(pts, self.I.shape[0], self.I.shape[1], hflip=True)
        pts_flip_v = geom.flip_points(pts, self.I.shape[0], self.I.shape[1], hflip=False)

        img = draw_points(pts, self.I)
        img_h = draw_points(pts_flip_h, img)
        img_v = draw_points(pts_flip_v, img)

        show(img_h)
        show(img_v)


    @unittest.skip("Temporaily disabled while debugging")
    def test_bound_poly_rect_side_length2(self):
        '''test'''
        angle = 10
        I = np.array(np.ones((750, 1400, 3))) * 255
        pts = [[1200, 450], [1200, 200], [200, 450], [200, 200]]
        I = draw_points(pts, I)
        pts_rotated, A, B = geom.bound_poly_rect_side_length2(pts, angle)
        I = draw_points(pts_rotated, I)
        print(pts_rotated, A, B)
        show(I)


    #@unittest.skip("Temporaily disabled while debugging")
    def test_rect_inner_side_length2(self):
        '''test'''
        pts = [[1200, 450], [1200, 200], [200, 450], [200, 200]]
        angle = 10
        ratio = (1200 - 200) / (450 - 200)

        pts_rotated = geom.rotate_points(pts, angle, center=None)

        #pts_bound is the corolloray of a rotated detection
        pts_bound, B, A = geom.bound_poly_rect_side_length2(pts, angle)

        #check looks ok
        self.Patch = draw_points(pts, self.Patch, join=True, line_color=(0, 0, 0))
        self.Patch = draw_points(pts_bound, self.Patch, join=True, line_color=(0, 255, 0))
        self.Patch = draw_points(pts_rotated, self.Patch, join=True, line_color=(255, 0, 0))
        #show(self.Patch)

        b, a, theta = geom.rect_inner_side_length2(pts_bound, ratio)
        print(b, a, degrees(theta))
        self.assertAlmostEqual(b, 250, 4)
        self.assertAlmostEqual(a, 1000, 4)
        self.assertAlmostEqual(theta, radians(10), 4)





if __name__ == '__main__':
    unittest.main(verbosity=2)
