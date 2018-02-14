
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
import opencvlib.transforms as t
from opencvlib.view import show
from opencvlib.view import mosaic
from opencvlib.common import draw_points

_fShow = lambda pts: show(draw_points(pts))

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


    #@unittest.skip("Temporaily disabled while debugging")
    def test_sharpen(self):
        '''sharpen'''
        img = t.sharpen(self.I)
        show(mosaic([img, self.I]))





if __name__ == '__main__':
    unittest.main(verbosity=2)
