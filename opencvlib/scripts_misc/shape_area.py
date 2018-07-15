# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''find height at 50% of shape area, prints it to screen.

Height is a proportion of the total height.
'''

import argparse


import cv2
import numpy as np



from opencvlib.view import draw_points
from opencvlib.view import show
from opencvlib import getimg
import statistics


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-rt', help='Reverse and threshhold the image', action='store_true')
    cmdline.add_argument('imgfile', help='File with the image')
    args = cmdline.parse_args()

    img = getimg(args.imgfile)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if args.rt:
        #correction for some dark grey artifacts in image after
        #binarizing the image
        img[img < 50] = 51
        img[img > 51] = 0
        img[img == 51] = 255
        #now the fish profile is white on black

    assert isinstance(img, np.ndarray)

    n = 0
    pxcnt = 0
    pxmax = 0
    for _, col in enumerate(img.T):
        if 255 in col:
            n += 1
            pxcnt += len(col[col == 255])
            pxmax = len(col[col == 255]) if len(col[col == 255]) > pxmax else pxmax

    print('Standard mean height: %.3f' % ((pxcnt/n)/pxmax))





if __name__ == '__main__':
    main()
