# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''
Generate negative  images from the images with bass in them.

The global var _OUT is the output dir.
Example:
    make_negs.py
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


#TARGET_CNT = 816 #number of negative images
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

_OUT = r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\negative'



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
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__

    #named: eg script.py -part head
    cmdline.add_argument('-n', '--number', help='The number of images to produce. If not provided will sample 10 from every image found.', default=0)
    cmdline.add_argument('-s', '--skip_file_check', help='Do not halt if output folder has files.', action='store_true')
    args = cmdline.parse_args()
    n_target = int(args.number)

    nr_files = iolib.file_count(_FOLDERS, '*.jpg', False)
    if nr_files == 0:
        print('\nSource folders appear to be empty or invalid.')
        return

    if not args.skip_file_check:
        if not chkdir(_OUT):
            return

    if args.number == 0:
        n = 10

    skipped = 0; processed = 0

    h_neg = 121; w_neg = 508 #size of bass train imgs
    negs = 0
    Gen = gen.VGGROI(_FILES)
    n = int(round(n_target / nr_files, 0))
    PP = iolib.PrintProgress(n * nr_files, init_msg='Creating negatves in %s' % _OUT)

    for _, fname, reg_attr in Gen.generate(path_only=True):
        x, y, w, h = (reg_attr.x, reg_attr.y, reg_attr.w, reg_attr.h)
        #img = transforms.resize(img, width=WIDTH, height=HEIGHT)
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

        for _ in range(n):
            PP.increment()
            i = roi.sample_rect(sample_space, w_neg, h_neg)
            if isinstance(i, np.ndarray) and i.shape == (h_neg, w_neg, 3):
                f = iolib.get_file_parts2(fname)[1]
                lp_cnt = 0
                while True:
                    s = path.normpath(_OUT + '/n' + rndstr(3) +  f)
                    if not iolib.file_exists(s):
                        break
                    lp_cnt += 1
                    if lp_cnt > 100:
                        raise StopIteration('To many iterations to create unique filename.')
                cv2.imwrite(s, i)
                negs += 1
            if negs >= n_target:
                break
        processed += 1
        if negs >= n_target:
            break

    print('Create %s negatives from %s images.\n' % (negs, processed))





if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
