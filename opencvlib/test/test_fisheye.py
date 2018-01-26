# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import opencvlib.lenscorrection.fisheye as _fe


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.calibration_images_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide/*.jpg'
        self.image_paths = [x for x in iolib.file_list_glob_generator(self.calibration_images_path)]

    #@unittest.skip("Temporaily disabled while debugging")
    def test_calibrate(self):
        '''test it'''
        Fish = _fe.FishEye(9, 6)
        Fish.calibrate(self.image_paths)


if __name__ == '__main__':
    unittest.main(verbosity=2)
    
