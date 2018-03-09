# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''
Generate negative  images from the images with bass in them

Example:
    make_base_images.py
'''
import argparse
import os.path as path
import os
import math

import cv2
import numpy as np


import funclib.iolib as iolib
from funclib.stringslib import rndstr
from funclib.arraylib import vstackt, hstackt

import opencvlib.roi as roi
import opencvlib.imgpipes.generators as gen
import opencvlib.transforms as transforms
import opencvlib.common as common
import opencvlib.info as info
from opencvlib.view import show


TARGET_CNT = 1000 #number of negative images

PP = iolib.PrintProgress()

_FILES = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm/undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690/undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm/undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/undistorted/vgg_whole.json']

_FOLDERS = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm/undistorted',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690/undistorted',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm/undistorted',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/undistorted']

_OUT = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/not_bass'



def chkdir(d):
    '''check dir, create if doesnt exist'''
    if not path.isdir(d):
        print('Creating dir %s' % d)
        os.mkdir(d) #checked, this fails if out is a file

    d = path.normpath(d)
    if iolib.folder_has_files(d, '.jpg'):
        print('Output folder "%s contains files. The directory must be empty.' % d)
        return False
    return True


def main():
    '''main
    '''
    if not chkdir(_OUT):
        return

    PP.max = iolib.file_count(_FOLDERS, '*.jpg', False)
    skipped = 0; processed = 0
    if not PP.max or PP.max == 0:
        print('\nSource folders appear to be empty or invalid. Check the _SOURCES assignment in this script')
        return

    h_neg = 120; w_neg = 514 #size of bass train imgs

    negs = 0

    Gen = gen.VGGROI(_FILES)

    for _, fname, reg_attr in Gen.generate(path_only=True):
        x, y, w, h = (reg_attr.x, reg_attr.y, reg_attr.w, reg_attr.h)
        #img = transforms.resize(img, width=WIDTH, height=HEIGHT)
        PP.increment()
        img = cv2.imread(fname)
        assert isinstance(img, np.ndarray)
        if not isinstance(img, np.ndarray):
            skipped += 1
            continue

        top = img[0:y, :, :] #top strip
        bottom = img[y+h:, :, :] #bottom strip

        left = np.rollaxis(img[0:, 0:x, :], 0, 2) #side strip and rotate
        right = np.rollaxis(img[0:, x+w:, :], 0, 2)

        left_right = hstackt([left, right])

        #stack into single image then sample from it
        sample_space = vstackt([top, bottom, left_right])

        for _ in range(10):
            i = roi.sample_rect(sample_space, w_neg, h_neg)
            if isinstance(i, np.ndarray) and i.shape == (h_neg, w_neg, 3):
                f = iolib.get_file_parts2(fname)[1]
                s = path.normpath(_OUT + '/neg' + rndstr(3) +  f)
                cv2.imwrite(s, i)
                negs += 1
        processed += 1

    print('Create %s negatives from %s images.\n' % (negs, processed))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
