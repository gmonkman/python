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

from opencvlib.view import show
import funclib.iolib as iolib
from funclib.stringslib import rndstr
import opencvlib.roi as roi
import opencvlib.imgpipes.generators as gen
import opencvlib.transforms as transforms
import opencvlib.common as common
import opencvlib.info as info

TARGET_CNT = 1000 #number of negative images

PP = iolib.PrintProgress()

_SOURCES = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm/undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690/undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm/undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted/vgg_whole.json',
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/undistorted/vgg_whole.json']

_OUT = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/not_bass'



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

    PP.max = iolib.file_count(_SOURCES, '*.jpg', False)
    skipped = 0; processed = 0
    if not PP.max or PP.max == 0:
        print('\nSource folders appear to be empty or invalid. Check the _SOURCES assignment in this script')
        return

    h = 120; w = 512 #size of bass train imgs


    Gen = gen.VGGROI(_SOURCES)

    for _, fname, reg_attr in Gen.generate(path_only=True):
        x, y, w, h = (reg_attr.x, reg_attr.y, reg_attr.w, reg_attr.h)
        #img = transforms.resize(img, width=WIDTH, height=HEIGHT)
        img = cv2.imread(fname)
        assert isinstance(img, np.ndarray)
        if not isinstance(img, np.ndarray):
            skipped += 1
            continue

        rnd_roi1 = img[0:y, :, :] #top strip
        rnd_roi2 = img[y+h:, :, :] #bottom strip
        rnd_roi3 = np.rollaxis(img[0:, 0:x, :]) #rotate
        rnd_roi4 = np.rollaxis(img[0:, x+w:, :]

        sample_space = np.vstack([rnd_roi1, rnd_roi1, rnd_roi1, rnd_roi1])
        for x in range(10):

        if isinstance(rnd_roi1, np.ndarray) and rnd_roi1.shape == (120, 512, 3):
            f = iolib.get_file_parts2(fname)[1]
            s = path.normpath(_OUT_TRAIN + '/neg' + rndstr(3) +  f)
            cv2.imwrite(s, rnd_roi)



        PP.increment()
        processed += 1



    print('\n%s of %s images processed. %s images skipped.\n' % (processed, PP.max, skipped))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
