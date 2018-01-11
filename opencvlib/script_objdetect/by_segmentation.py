# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member
'''detect an object by threshholding and iterating through contours'''
#by_segmentation.by "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore" -s
import sys
import cv2
import imutils
import numpy as np
import argparse

import funclib.baselib as baselib
import funclib.iolib as iolib
import opencvlib.transforms as transforms
import opencvlib.common as common
from opencvlib.view import show, mosaic, showarray
from opencvlib import color


def filter_image(img_in):
    '''(ndarray)->ndarray
    Take an image, filter it to pick up the lobster
    '''
    ciH = color.ColorInterval(color.eColorSpace.HSV255255255, (33, 0, 0), (255, 255, 102))
    CD = color.ColorDetection(img_in, ciH, color.eColorSpace.HSV, no_conversion=False)
    CD.detect()
    return CD.detected_as_bgr()



def main(img, show_debug_images=False):
    '''img:ndarray, bool -> ndarray
    Pass in an image, do the work, return processed image

    show_debug_images
        Shows all images if true
    '''


    filtered = filter_img(img)
    blurred = cv2.GaussianBlur(filtered, (5, 5), 0)
    blurred_grey = transforms.togreyscale(img)   
    thresh = cv2.threshold(blurred_grey, 1, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh.copy(), None, iterations=3)

    cnts = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    hullImage = np.zeros(img.shape[:2], dtype='uint8')

    if show_debug_images: 
        outimg = mosaic([img, thresh, dilated])
        show(outimg, title='original/thresh/dilated')

    for i, c in enumerate(cnts):
        area = cv2.contourArea(c)
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        extent = area / float(w * h)
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        solidity = area / float(hull_area)
        shape = ''

        if aspect_ratio >= 1.9 and extent < 0.6 and solidity < 0.8:
            shape = 'FISH'
            cv2.drawContours(hullImage, [hull], -1, 255, 1)
            cv2.drawContours(img, [c], -1, (240, 0, 159), 3)
            cv2.putText(img, shape, (x, y -10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 0, 159), 2)
            print('Contour #{} -- aspect_ratio={:.1f}, extent={:.1f}, solidity={:.2f}'.format(i + 1, aspect_ratio, extent, solidity))

            if show_debug_images: 
                show(hullImage, title='Convex Hull - hullImage')

            show(img, 'Fish Region')

        return img


if __name__ == "__main__":
    #need to import argparse
    _CMDLINE = argparse.ArgumentParser(description='Path to images')
    _CMDLINE.add_argument('path', help='Path to images to test') #argument by pos
    _CMDLINE.add_argument('-s', '--show_all', help='Show all debugging images', action="store_true", required=False) #argument either there or not
    _CMDLINEARGS = _CMDLINE.parse_args()

    sh = _CMDLINEARGS.show_all

    for fname in iolib.file_list_generator1([_CMDLINEARGS.path], common.image_extensions):
        im = transforms.resize(fname, 400)
        #test_color(im)
        im = main(im, sh)
        #show(im)
