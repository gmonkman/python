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
        self.camera = 'GoProHero5PhotoWide'

        self.calibration_images_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide'
        self.calibration_images_path_wildcarded = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide/*.jpg'

        self.distorted_images_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/bass/fiducial/charter/GOPROH~2'
        self.distorted_images__output_path = self.distorted_images_path + '/undistorted'

        self.image_paths = [x for x in iolib.file_list_glob_generator(self.calibration_images_path)]

    @unittest.skip("Temporaily disabled while debugging")
    def test_calibrate(self):
        '''test the calibration'''
        cam = _lc.get_camera(self.camera)
        calibrate(cam)

    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort(self):
        '''standard undistort'''
        cam = _lc.get_camera(self.camera)
        undistort(cam, self.distorted_images_path, self.distorted_images__output_path, use_fisheye=false)

    #@unittest.skip("Temporaily disabled while debugging")
    def test_undistort_fisheye(self):
        '''fisheye undistort'''
        cam = _lc.get_camera(self.camera)
        undistort(cam, self.distorted_images_path, self.distorted_images__output_path, use_fisheye=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
    




    #@unittest.skip("Temporaily disabled while debugging")
    def test_undistort(self):
        '''test the undistort'''