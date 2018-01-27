# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use
'''unit tests for lenscorrection'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import funclib.iolib as iolib
import opencvlib.lenscorrection.lenscorrection as _lc


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)

        self.distorted_images_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/bass/fiducial/charter/GOPROH~2'
        self.distorted_images_output_path = self.distorted_images_path + '/undistorted'
        self.distorted_images_output_path_fe = self.distorted_images_path + '/undistorted_fisheye'


    @unittest.skip("Temporaily disabled while debugging")
    def test_calibrate(self):
        '''test the calibration
        Also does fisheye (default to do both)

        Gets calibration paths etc from lenscorrection.py.ini

        GoProHero5PhotoWide
        GoProHero5PhotoMedium
        GoProHero5PhotoNarrow
        '''
        cam = _lc.get_camera('GoProHero5PhotoMedium')
        _lc.calibrate(cam)

    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort(self):
        '''standard undistort'''
        cam = _lc.get_camera('GoProHero5PhotoWide')
        _lc.undistort(cam, self.distorted_images_path, self.distorted_images_output_path, use_fisheye=False)

    #@unittest.skip("Temporaily disabled while debugging")
    def test_undistort_fisheye(self):
        '''fisheye undistort'''
        cam = _lc.get_camera('GoProHero5PhotoWide')
        iolib.files_delete(self.distorted_images_output_path_fe)
        _lc.undistort(cam, 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/medium',
                      'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/medium/undistorted',
                      use_fisheye=True)




if __name__ == '__main__':
    unittest.main(verbosity=2)
