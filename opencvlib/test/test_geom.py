# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, no-self-use

'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

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




    @unittest.skip("Temporaily disabled while debugging")
    def test_points_rmsd(self):
        '''rmsd'''
        x = geom.points_rmsd([[1, None], [2, 10]], [[1, 1], [2, 10]])
        self.assertEqual(x, 0)
        x = geom.points_rmsd([[1, None], [2, 10]], [[1, 1], [2, 5]])
        pass


    #@unittest.skip("Temporaily disabled while debugging")
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




if __name__ == '__main__':
    unittest.main(verbosity=2)
