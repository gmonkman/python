'''unit tests for roi'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import numpy as np

import opencvlib.roi as roi
import funclib.iolib as iolib
from opencvlib.roi import ePointConversion as eCvt

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)

        self.db_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db'

        self.imgpath = _path.normpath(_path.join(self.modpath, 'images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        pass


    #unittest.skip("Temporaily disabled while debugging")
    def test_roi_resize(self):
        '''test roi'''
        pts = np.array([[0, 0], [10, 10], [0, 10], [10, 0]])
        sz1 = np.array([800, 600])
        sz2 = sz1*2

        res = roi.roi_resize(pts, sz1, sz2)
        self.assertTrue(np.array_equal(res, pts*2))

        sz2 = sz1*[1.5, 1]
        res = roi.roi_resize(pts, sz1, sz2)
        self.assertTrue(np.array_equal(res, pts*[1.5, 1]))


    #@unittest.skip("Temporaily disabled while debugging")
    def test_points_convert(self):
        '''test points conversions'''
        w = 1024
        h = 768

        #xy origin, top-right, originish
        xy_pts = [[0, 0], [w-1, h-1], [50, 100]]
        pts = roi.points_convert(xy_pts, w, h, eCvt.XYtoCVXY)
        self.assertTrue(pts == [[0, 767], [1023, 0], [50, 667]])

        pts = roi.points_convert(xy_pts, w, h, eCvt.XYtoRC)
        self.assertTrue(pts == [[767, 0], [0, 1023], [667, 50]])


        #rc top-left, bot-right, top-leftish
        rc_pts = [[0, 0], [h-1, w-1], [50, 100]]
        pts = roi.points_convert(rc_pts, w, h, eCvt.RCtoCVXY)
        self.assertTrue(pts == [[0, 0], [1023, 767], [100, 50]])

        pts = roi.points_convert(rc_pts, w, h, eCvt.RCtoXY)
        self.assertTrue(pts == [[0, 767], [1023, 0], [100, 717]])


        #CVXY top-left, bot-right, top leftish
        cvxy_pts = [[0, 0], [w-1, h-1], [50, 100]]
        pts = roi.points_convert(cvxy_pts, w, h, eCvt.CVXYtoRC)
        self.assertTrue(pts == [[0, 0], [767, 1023], [100, 50]])

        pts = roi.points_convert(cvxy_pts, w, h, eCvt.CVXYtoXY)
        self.assertTrue(pts == [[0, 767], [1023, 0], [50, 667]])


    #@unittest.skip("Temporaily disabled test_showarray")
    def test_show_roi_points(self):
        pts= [[0,0], [10,10], [30, 10], [90,90], [300,300], [250, 450], [10, 300]]
        img = roi.plot_points(pts)
        from opencvlib.view import show
        show(img)

if __name__ == '__main__':
    unittest.main()

