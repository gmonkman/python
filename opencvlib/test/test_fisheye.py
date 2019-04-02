#pylint: skip-file

'''unit tests for features'''
import cv2 as _cv2
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import opencvlib.lenscorrection.fisheye as _fe
from opencvlib.view import show as _show

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        
        self.calibration_images_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide'


        
        

    #unittest.skip("Temporaily disabled while debugging")
    def test_calibrate_goprowide(self):
        '''test it'''
        in_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide/*.jpg'
        img_paths = [x for x in iolib.file_list_glob_generator(in_path)]
        model_file = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide/gopro5_wide_1440x1080.np'

        Fish = _fe.FishEye(9, 6)
        Fish.calibrate(img_paths)
        Fish.save(model_file)


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_gopro_wide(self):
        '''undistort goprohero wide'''
        model_file = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide/gopro5_wide_1440x1080.np'
        Fish = _fe.load_model(model_file)
        
        in_path = 'C:/Users/GRAHAM~1/OneDrive/DOCUME~1/PHD/images/CALIBR~2/gopro/hero5/wide/goprohero5/wide/*.jpg'
        for ipath in iolib.file_list_glob_generator(in_path):
            img = _cv2.imread(ipath)
            img_und = Fish.undistort(img)
            _show(img_und)


if __name__ == '__main__':
    unittest.main(verbosity=2)
    
