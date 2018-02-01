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
        

    @unittest.skip("Temporaily disabled while debugging")
    def test_list_profile_param(self):
        '''test'''
        res = _lc.list_profile_param('GoProHero5PhotoWide', 1440, 1080, 'D', printit=True)
        print(res)



    #@unittest.skip("Temporaily disabled while debugging")
    def test_calibrate(self):
        '''test the calibration, also does fisheye (default to do both)

        Gets calibration paths etc from lenscorrection.py.ini

        GoProHero4PhotoMedium, GoProHero4PhotoWide
        GoProHero5PhotoWide, GoProHero5PhotoMedium, GoProHero5PhotoNarrow
        s5690
        finepixXP30
        '''

        #GoPro4
        cam = _lc.get_camera('GoProHero4PhotoMedium')
        _lc.calibrate(cam)
        print('Press any key to continue....')
        cam = _lc.get_camera('GoProHero4PhotoWide')
        _lc.calibrate(cam)
        print('Press any key to continue....')

        #GoPro5
        cam = _lc.get_camera('GoProHero5PhotoWide')
        _lc.calibrate(cam)
        print('Press any key to continue....')
        cam = _lc.get_camera('GoProHero5PhotoMedium')
        _lc.calibrate(cam)
        print('Press any key to continue....')
        cam = _lc.get_camera('GoProHero5PhotoNarrow')
        _lc.calibrate(cam)
        print('Press any key to continue....')

        #cam = _lc.get_camera('s5690')
        #_lc.calibrate(cam, skip_fisheye=True)

        #cam = _lc.get_camera('finepixXP30')
        #_lc.calibrate(cam, skip_fisheye=True

        iolib.wait_key()


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort(self):
        '''standard undistort'''
        cam = _lc.get_camera('GoProHero5PhotoWide')
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/wide/undistorted_standard'
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/wide'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=False)


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_fisheye_wide(self):
        '''fisheye undistort'''
        cam = _lc.get_camera('GoProHero5PhotoWide')
        #out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/wide/undistorted_fisheye'
        #in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/wide'
        #iolib.files_delete(out_path)
        #_lc.undistort(cam, in_path, out_path, use_fisheye=True)

        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/wide/undistorted_fisheye'
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/wide'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)