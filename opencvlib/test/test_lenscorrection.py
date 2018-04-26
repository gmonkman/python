# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use
'''unit tests for lenscorrection'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import funclib.iolib as iolib
import opencvlib.lenscorrection.lenscorrection as _lc
from funclib.iolib import wait_key as _wait_key

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        

#region Undistort
    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_GoProHero5PhotoWide(self):
        '''undistort_GoProHero5PhotoWide'''
        cam = _lc.get_camera('GoProHero5PhotoWide')
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/wide'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/wide/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/wide'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/wide/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        print('Press any key to continue')
        _wait_key()


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_GoProHero5PhotoMedium(self):
        '''undistort_GoProHero5PhotoMedium'''
        cam = _lc.get_camera('GoProHero5PhotoMedium')
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/medium'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/medium/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/medium'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/goprohero5/medium/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        print('Press any key to continue')
        _wait_key()


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_bass(self):
        '''test_undistort_bass'''
        #cam = _lc.get_camera('GoProHero4PhotoWide')
        #in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero4/wide'
        #out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero4/wide/undistorted_standard'
        #iolib.files_delete(out_path)
        #_lc.undistort(cam, in_path, out_path, use_fisheye=False)
        #iolib.wait_key()
        pass


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_GoProHero4PhotoMediumShore(self):
        '''undistort_GoProHero5PhotoMedium'''
        cam = _lc.get_camera('GoProHero4PhotoMedium')
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero4/medium'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero4/medium/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        print('Press any key to continue')
        _wait_key()


    @unittest.skip("Temporaily disabled while debugging")
    def test_undistort_GoProHero5PhotoMediumShore(self):
        '''undistort_GoProHero5PhotoMediumShore'''
        cam = _lc.get_camera('GoProHero5PhotoMedium')
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/medium'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/goprohero5/medium/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        print('Done GoProHero5PhotoMediumShore. Press any key to continue...')
        _wait_key()
#endregion


 
#region Calibration
    @unittest.skip("Temporaily disabled while debugging")
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

        cam = _lc.get_camera('GoProHero4PhotoWide')
        _lc.calibrate(cam)

        #GoPro5
        #cam = _lc.get_camera('GoProHero5PhotoWide')
        #_lc.calibrate(cam)
        #print('Press any key to continue....')
        #cam = _lc.get_camera('GoProHero5PhotoMedium')
        #_lc.calibrate(cam)
        #print('Press any key to continue....')
        #cam = _lc.get_camera('GoProHero5PhotoNarrow')
        #_lc.calibrate(cam)
        #print('Press any key to continue....')

        #cam = _lc.get_camera('s5690')
        #_lc.calibrate(cam, skip_fisheye=True)

        #cam = _lc.get_camera('finepixXP30')
        #_lc.calibrate(cam, skip_fisheye=True

        iolib.wait_key()
        
           
    @unittest.skip("Temporaily disabled while debugging")
    def test_calibrate_undistort_512G(self):
        '''test_calibrate_undistort_512G'''
        #calibrate
        cam = _lc.get_camera('NEXTBASE512G')
        _lc.calibrate(cam, skip_fisheye=True)
        print('press any key to continue')
        iolib.wait_key()

        #undistort the images used in the calibration
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/nextbase512g'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/nextbase512g/undistorted_standard'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=False)

        print('press any key to continue')
        iolib.wait_key()


    @unittest.skip("Temporaily disabled while debugging")
    def test_calibrate_undistort_GoProHero4Wide(self):
        '''test_calibrate_undistort_GoProHero4Wide'''
        #calibrate
        cam = _lc.get_camera('GoProHero4PhotoWide')
        _lc.calibrate(cam, skip_fisheye=False)

        print('press any key to continue')
        iolib.wait_key()

        #undistort the images used in the calibration
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero4/wide'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero4/wide/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        print('press any key to continue')
        iolib.wait_key()


    @unittest.skip("Temporaily disabled while debugging")
    def test_calibrate_undistort_GoProHero5(self):
        '''test_calibrate_undistort_GoProHero5Wide'''
        #WIDE calibrate
        cam = _lc.get_camera('GoProHero5PhotoWide')
        _lc.calibrate(cam, skip_fisheye=False)

        #WIDE undistort the images used in the calibration
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero5/wide'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero5/wide/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        #-----

        #Medium Standard calibrate
        cam = _lc.get_camera('GoProHero5PhotoMedium')
        _lc.calibrate(cam, skip_fisheye=False)

        #Medium undistort the images used in the calibration
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero5/medium'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero5/medium/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        #-----

        #Narrow Standard calibrate
        cam = _lc.get_camera('GoProHero5PhotoNarrow')
        _lc.calibrate(cam, skip_fisheye=False)

        #Narrow undistort the images used in the calibration
        in_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero5/narrow'
        out_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/gopro/hero5/narrow/undistorted_fisheye'
        iolib.files_delete(out_path)
        _lc.undistort(cam, in_path, out_path, use_fisheye=True)

        print('Press any key to continue')
        iolib.wait_key()
#endregion    




#region misc tests
    #@unittest.skip("Temporaily disabled while debugging")
    def test_list_profile_param(self):
        '''test'''
        res = _lc.list_profile_param('GoProHero5PhotoWide', 1440, 1080, 'D', printit=True)
        print(res)


    @unittest.skip("Temporaily disabled while debugging")
    def test_delete_profile(self):
        '''test_delete_profile'''
        _lc.delete_profile('GoProHero4', 1280, 738)       
#endregion




if __name__ == '__main__':
    unittest.main(verbosity=2)
