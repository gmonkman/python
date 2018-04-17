# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, no-self-use

'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
import opencvlib.geom as geom


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)

    #@unittest.skip("Temporaily disabled while debugging")
    def test_points_rmsd(self):
        '''rmsd'''
        x = geom.points_rmsd([[1, None], [2, 10]], [[1, 1], [2, 10]])
        self.assertEqual(x, 0)
        x = geom.points_rmsd([[1, None], [2, 10]], [[1, 1], [2, 5]])
        pass





if __name__ == '__main__':
    unittest.main(verbosity=2)
