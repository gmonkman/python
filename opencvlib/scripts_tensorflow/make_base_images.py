# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''
Generate base train, evaluation and test image sets

Example:
    make_base_images.py
'''
import argparse
import os.path as path
import os
import math

import cv2

from opencvlib.view import show
import funclib.iolib as iolib
import opencvlib.roi as roi
import opencvlib.imgpipes.generators as gen
import opencvlib.transforms as transforms
import opencvlib.common as common
import opencvlib.info as info

PP = iolib.PrintProgress()

_SOURCE = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/bass_all_unprocessed/sharpened'
_OUT_EVAL = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/eval'
_OUT_TEST = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/test'
_OUT_TRAIN = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train'


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
    if not chkdir(_OUT_EVAL) or not chkdir(_OUT_TEST) or not chkdir(_OUT_TRAIN):
        return

    PP.max = iolib.file_count(_SOURCE, '*.jpg', False)
    skipped = 0; processed = 0

    res = info.ImageInfo.get_image_resolutions(path.normpath(path.join(_SOURCE, '*.jpg')), False)
    if not res:
        print('Found no resolutions for images in "%s"' % _SOURCE)
        return

    zres = list(zip(*res))
    heights = zres[1]
    widths = zres[0]
    minh = min(heights)
    minw = min(widths)

    h = sum(heights)/len(heights)
    w = sum(widths)/len(widths)
    HEIGHT = 120 #smallest image height
    WIDTH = int(HEIGHT * (w/h))
    Gen = gen.FromPaths(_SOURCE, '*.jpg')
    for img, fname, _ in Gen.generate():
        #img = transforms.histeq_color(img)
        img = transforms.resize(img, width=WIDTH, height=HEIGHT)
        f = iolib.get_file_parts2(fname)[1]
        s = path.normpath(_OUT_TRAIN + '/mbi' + f)
        cv2.imwrite(s, img)
        PP.increment()
        processed += 1



    print('\n%s of %s images processed. %s images skipped.\n' % (processed, PP.max, skipped))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
