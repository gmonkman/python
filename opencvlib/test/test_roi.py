# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for roi'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import numpy as np
import cv2

import opencvlib.roi as roi
import funclib.iolib as iolib
from opencvlib.roi import ePointConversion as eCvt
from opencvlib.view import show
from opencvlib.view import draw_points
from opencvlib.view import mosaic
from opencvlib.transforms import rotate
import opencvlib.geom as geom
import opencvlib.common as common



class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)

        self.db_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db'

        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        pass


    @unittest.skip("Temporaily disabled while debugging")
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


    @unittest.skip("Temporaily disabled while debugging")
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


    @unittest.skip("Temporaily disabled test_showarray")
    def test_show_roi_points(self):
        '''test plotting rois'''
        pts = [[300, 300], [400, 310], [410, 450], [310, 460]]
        img = roi.plot_points(pts)
        show(img)


    @unittest.skip("Temporaily disabled test_showarray")
    def test_quad(self):
        '''test quadrilateral manip'''
        quad = [[300, 300], [400, 310], [410, 450], [310, 460]]
        img = np.ones([650, 800, 3])*255
        img = common.draw_points(quad, img, join=True)
        img_orig_pts = np.copy(img)

        Q = roi.Quadrilateral(quad, img.shape[1], img.shape[0])
        midpoints = [x.midpoint for x in Q.lines]
        img = common.draw_points(midpoints, img) #original plotted quadrilateral with midpoints

        angle = Q.angle_to_origin
        img_rotated = rotate(img, angle, no_crop=True)

        img_rotated_points = np.ones([*img_rotated.shape])*255
        img_rotated_points = common.draw_points(Q.rotated_to_x, img_rotated_points, join=True, line_color=(0, 0, 0))
        img_rotated_points = common.draw_points(Q.bounding_rectangle, img_rotated_points, join=True, line_color=(255, 0, 0))
        show(mosaic([img, img_rotated, img_rotated_points]))


    @unittest.skip("Temporaily disabled test_showarray")
    def test_iou(self):
        '''test quadrilateral manip'''
        pts = [[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.5]]
        pts_gt = [[1, 0], [0, 1], [0, 0], [1, 1]]
        a = roi.iou(pts, pts_gt)
        self.assertEqual(a, 0.25)
        z = 10

    #@unittest.skip("Temporaily disabled test_showarray")
    def test_iou2(self):
        '''test quadrilateral manip'''
        nas = [0.263571990558615,	0.790715971675845,	0.435483870967741,	0.6,
               0.265444666147232,	0.784790337085723,	0.432113647460937,	0.600508213043212]
        a = roi.iou2(*nas)
        self.assertEqual(a, 0.9628434335096393)
        img_path = _path.normpath(_path.join(self.modpath, 'bin/images/r358_FISHUND.jpg'))
        img = cv2.imread(img_path)

        img_flip_path = _path.normpath(_path.join(self.modpath, 'bin/images/r358_FISHUND_flip.jpg'))
        img_flip = cv2.imread(img_flip_path)

        w = 1569; h = 1259
        pts_gt = _get_pts([0.275971956660293, 0.699808795411089, 0.455917394757744, 0.575853852263701], h, w)
        pts_inf = _get_pts([0.275301188230514, 0.701213181018829, 0.455382585525512, 0.573848962783813], h, w)
        img = draw_points(pts_gt, img, join=True, line_color=(0, 0, 0))
        img = draw_points(pts_inf, img, join=True, line_color=(0, 255, 0))
        show(img)

        pts_flip_gt = _get_pts([0.30019120458891, 0.724028043339706, 0.455917394757744, 0.575853852263701], h, w)
        pts_flip_inf = _get_pts([0.303799748420715, 0.725388884544372, 0.453819185495376, 0.575798153877258], h, w)

        img_flip = draw_points(pts_flip_gt, img_flip, join=True, line_color=(0, 0, 0))
        img_flip = draw_points(pts_flip_inf, img_flip, join=True, line_color=(0, 255, 0))
        show(img_flip)



    @unittest.skip("Temporaily disabled test_showarray")
    def test_flip_points(self):
        '''test'''
        w = 1569; h = 1259
        pts = _get_pts([0.175971956660293, 0.699808795411089, 0.455917394757744, 0.575853852263701], h, w)
        pts_flip = roi.flip_points(pts, h, w, hflip=True)
        img_path = _path.normpath(_path.join(self.modpath, 'bin/images/r358_FISHUND.jpg'))
        img = cv2.imread(img_path)
        img = draw_points(pts, img, join=True, line_color=(0, 0, 0), thickness=3)
        img = draw_points(pts_flip, img, join=True, line_color=(0, 255, 0), thickness=3)
        show(img)


    @unittest.skip("Temporaily disabled test_showarray")
    def test_bounding_rect_of_poly(self):
        '''test br'''
        sq = [[0, 0], [10, 10], [0, 10], [10, 0]]
        sq45 = geom.rotate_points(sq, -45, None)
        sq45_bound = roi.bounding_rect_of_poly(sq45)
        pass






def _get_pts(min_max, h, w):
    pts_raw = roi.points_convert(min_max, 1, 1, roi.ePointConversion.XYMinMaxtoCVXY, roi.ePointsFormat.XY)
    return roi.points_denormalize(pts_raw, h, w)


if __name__ == '__main__':
    unittest.main()
