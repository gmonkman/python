
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
from opencvlib.common import _getimg
import opencvlib.transforms as t
from opencvlib.view import show
from opencvlib.view import mosaic
from opencvlib.common import draw_points
from opencvlib.display_utils import KeyBoardInput as Keys

_fShow = lambda pts: show(draw_points(pts))

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.imggraf = r'C:\development\python\opencvlib\test\bin\images\graf1.png'

        self.img_matt_pemb5 = _getimg(self.imgpath)
        self.blurred = _getimg(self.imggraf)
        self.blurred = cv2.GaussianBlur(self.blurred, (9, 9), 10)


    @unittest.skip("Temporaily disabled while debugging")
    def test_crop(self):
        '''test'''
        img = t.crop(self.I, (200, 100), t.eRegionFormat.HW, (100, 100), allow_crop_truncate=False)
        self.assertTupleEqual(img.shape, (200, 100, 3))

        img = t.crop(self.I, (100, 200), t.eRegionFormat.HW, (100, 100), allow_crop_truncate=False)
        self.assertTupleEqual(img.shape, (100, 200, 3))


        #asking for a 100 by 200 image (w,h)
        img = t.crop(self.I, (100, 200), t.eRegionFormat.WH, (25, 50), allow_crop_truncate=True)
        self.assertTupleEqual(img.shape, (150, 75, 3))

        #asking for image 100 rows x 50 cols
        with self.assertRaises(ValueError):
            img = t.crop(self.I, (100, 50), t.eRegionFormat.HW, (100, 25), allow_crop_truncate=False)

        with self.assertRaises(ValueError):
            img = t.crop(self.I, (100, 50), t.eRegionFormat.WH, (25, 100), allow_crop_truncate=False)

        img = t.crop(self.I, ((0, 0), (100, 0), (0, 100), (100, 100)), t.eRegionFormat.XYXYXYXY)
        self.assertTupleEqual(img.shape, (101, 101, 3))


    @unittest.skip("Temporaily disabled while debugging")
    def test_sharpen(self):
        '''sharpen'''
        img = t.sharpen(self.I)
        show(mosaic([img, self.I]))


    @unittest.skip("Temporaily disabled while debugging")
    def test_unsharpmask(self):
        '''sharpen'''
        img = t.sharpen_unsharpmask(self.blurred, kernel_size=(21, 21), weight=1.1)
        show(mosaic([self.blurred, img]))


    @unittest.skip("Temporaily disabled while debugging")
    def test_intensity_wrapper(self):
        '''tests intensity wrapper and
        intensity transform'''
        #this should increase the contrast
        iout = t.intensity_wrapper(self.img_matt_pemb5, 1)
        show(iout)
        #this should decrease the contrast
        iout = t.intensity_wrapper(self.img_matt_pemb5, -1)
        show(iout)


    @unittest.skip("Temporaily disabled while debugging")
    def test_brightness(self):
        '''bright'''
        iout = t.brightness(self.img_matt_pemb5, -20)
        show(iout)


    #@unittest.skip("Temporaily disabled while debugging")
    def test_transform_shuffle(self):
        '''shuffle'''
        print('Press "q" to stop')
        t1 = t.Transform(t.brightness, value=50)
        t2 = t.Transform(t.gamma, gamma_=0.7)
        t3 = t.Transform(t.rotate, angle=90)
        Ts = t.Transforms(t1, t2, t3)

        while True:
            iout = Ts.executeQueue(img=self.img_matt_pemb5, print_debug=True)
            print('\n')
            if Keys.check_pressed_key('q', show(iout)[0]):
                break
            Ts.shuffle()


if __name__ == '__main__':
    unittest.main(verbosity=2)
