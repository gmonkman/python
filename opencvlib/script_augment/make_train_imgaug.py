#pylint: skip-file
'''
Generate training images with random corrections
and distortions. This is used to generate
additional training cases.

The destination folder must be empty.

Example:
    make_train.py -n 10 "C:/images", "C:/images/samples"
'''
#TODO consider converting this to use imgaug

#make_train_imgaug.py -n 10 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\positive", "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\positive_aug"
import argparse
from os import path


import random
import shutil
from contextlib import suppress

import imgaug as ia
from imgaug import augmenters as iaa
from imgaug import parameters as iap

import numpy as np
import cv2
from funclib.iolib import PrintProgress
import funclib.iolib as iolib
from funclib.stringslib import rndstr
from opencvlib.imgpipes.generators import FromPaths
from opencvlib import transforms

OUTCSV = 'd_avg.csv'

def chkempty(dirs):
    '''check output dirs are empty'''
    if isinstance(dirs, str):
        dirs = [dirs]
    for d in dirs:
        iolib.create_folder(path.normpath(d))
        assert not iolib.folder_has_files(path.normpath(d)), '\nDir %s must be empty.' % path.normpath(d)


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-n', '--nr', help='Number output images per input image.', required=True)
    cmdline.add_argument('source', help='Source image folder')
    cmdline.add_argument('dest', help='Destination image folder')

    #argument present or not: e.g. scipt.py -f
    #args.fix == True
    #cmdline.add_argument('-f', '--fix', help='Fix it', action='store_true')
    args = cmdline.parse_args()
    dest = args.dest
    dest = path.normpath(dest)
    chkempty(dest)
    source = args.source
    source = path.normpath(source)
    assert iolib.folder_has_files(source, ['.jpg']), 'No .jpg files found in %s' % source
    assert source != dest, 'Source and destination folders are the same'

    n = int(args.nr)
    assert 0 < n < 1e3, 'n was %s. n should be 0 < n < 1e3' % args.n

    ia.seed(1)

    seq = iaa.SomeOf((1, None),
        [
        iaa.OneOf([iaa.OneOf([iaa.GaussianBlur((0, 0.35)), iaa.AverageBlur(k=(1, 5)), iaa.MedianBlur(k=(1, 5)),]),
                iaa.Sharpen(iap.Uniform(0., 0.3), iap.Uniform(0., 0.3)),
                iaa.ContrastNormalization((0.7, 1.3))
                ]),
        iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.02*255), per_channel=0.3),
        iaa.AddToHueAndSaturation((-20, 20), from_colorspace='BGR', per_channel=0.3),
        iaa.OneOf([iaa.Multiply((0.75, 1.25)), iaa.Add((-20, 20), per_channel=0.3)]),
        iaa.PiecewiseAffine(scale=(0.001, 0.015))
        ], random_order=True) # apply augmenters in random order

    FP = FromPaths(source, wildcards='*.jpg')
    PP = PrintProgress(sum([1 for x in FP.generate(pathonly=True)]) * n)
    status = [['fname','d_avg']]
    for img, imgname, _ in FP.generate():
        for _ in range(n):
            PP.increment()
            img_cp = img.copy() #workaround

            iter = 0
            while True:
                images_aug = seq.augment_image(img_cp)
                d_avg = arrdiff(images_aug, img) #make sure the aug image is quite a bit different from the orig.
                if d_avg > 3.0:
                    break
                iter += 1
                if iter > 100:
                    raise StopIteration('Too many iterations.')

            iter = 0
            _, fname, ext = iolib.get_file_parts(imgname)
            while True:
                fname_out = '%s%s%s' % (fname, rndstr(3), ext)
                fout = path.normpath(path.join(dest, fname_out))
                if not iolib.file_exists(fout):
                    break
                iter += 1
                if iter > 100:
                    raise StopIteration('Too many iterations')
            status.append([fname_out, round(d_avg, 3)])
            cv2.imwrite(fout, images_aug)

    OUTCSV = path.normpath(path.join(dest, OUTCSV))
    iolib.writecsv(OUTCSV, status, inner_as_rows=False)
    print('\nDone.')



def arrdiff(arr1, arr2):
    nb_cells = np.prod(arr2.shape)
    d_avg = np.sum(np.power(np.abs(arr1.astype(np.float64) - arr2.astype(np.float64)), 2)) / nb_cells
    return d_avg



if __name__ == "__main__":
    main()
