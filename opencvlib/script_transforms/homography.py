# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''testing homography matching
Didnt work great
'''
from os import path

import cv2
import numpy as np

from opencvlib.imgpipes import vgg
from opencvlib.common import draw_points
from opencvlib.display_utils import KeyBoardInput as Key


RADIUS = 5

def build_matched(pts1, pts2):
    '''Build matched array of points
    Returns 2 arrays of points.

    If no points found, returns [],[]

    e.g.
    >>>x, y = build_matched([[None, 1], [10,20]], [[1, 1], [1,2]])
    >>>print(x)
    [[10,20]]
    >>>print(y)
    [[1,2]]
    '''
    pt1_out = []
    pt2_out = []
    for i in range(min([len(pts1), len(pts2)])):
        if not None in pts1[i] and not None in pts2[i]:
            pt1_out.append(pts1[i])
            pt2_out.append(pts2[i])
    return pt1_out, pt2_out


if __name__ == '__main__':
    print('Press "q" to quit')
    pts_dest = np.loadtxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate/roi_grow/resized/vgg_landmarks_train_points.np')

    for Img in vgg.imagesGenerator(json_file='C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate/roi_grow/resized/vgg_landmarks.json'):
        assert isinstance(Img, vgg.Image)
        Pts = [[None, None]] * 19 #store all the points
        has_points = False
        for vggReg in Img.roi_generator(shape_type='point'):
            has_points = True
            assert isinstance(vggReg, vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pts[lbl-1] = [vggReg.x, vggReg.y]

        if not has_points:
            continue

        Pts, pts_dest_filtered = build_matched(Pts, pts_dest)
        Pts = np.array(Pts)
        pts_dest_filtered = np.array(pts_dest_filtered)

        if len(Pts) < 10:
            continue

        im_src = cv2.imread(Img.filepath)
        im_src_with_its_points = draw_points(Pts, im_src, radius=RADIUS)

        h, status = cv2.findHomography(Pts, pts_dest_filtered, method=cv2.RANSAC, ransacReprojThreshold=5)

        im_out = cv2.warpPerspective(im_src, h, (im_src.shape[1], im_src.shape[0]))
        #im_out_orig_points = draw_points(Pts, im_out, radius=RADIUS)
        im_out_mean_points = draw_points(pts_dest_filtered, im_out, radius=RADIUS)

        # Display images
        cv2.imshow("Original image with its points", im_src_with_its_points)
        cv2.imshow("Warped with mean pts", im_out_mean_points)

        if Key.check_pressed_key('q', cv2.waitKey(0)):
            exit()
