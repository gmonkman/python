# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Generate training images with random corrections
and distortions. This is used to generate
additional training cases.

The destination folder must be empty.

Example:
    make_train.py -n 10 "C:/images", "C:/images/samples"
'''
#TODO consider converting this to use imgaug

#make_train_augmentor.py -n 10 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/bass", "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/bass/subsamples"
import argparse
from os import path
import tempfile
import os
import glob

import random
import shutil
from contextlib import suppress

from tqdm import tqdm
from Augmentor import Pipeline
import cv2

import funclib.iolib as iolib
from opencvlib.imgpipes.generators import FromPaths
from opencvlib import transforms
from opencvlib.display_utils import KeyBoardInput as Keys
from opencvlib.view import show



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
    chkempty(dest)

    source = args.source

    assert iolib.folder_has_files(source, ['.jpg']), 'No .jpg files found in %s' % source
    assert source != dest, 'Source and destination folders are the same'

    n = int(args.nr)
    assert 0 < n < 1e3, 'n was %s. n should be 0 < n < 1e3' % args.n

    tmpdir = source + '/output'
    Pipe = Pipeline(source_directory=source)
    Pipe.random_distortion(0.5, grid_width=random.randint(6, 10), grid_height=random.randint(6, 10), magnitude=random.randint(1, 4))
    Pipe.sample(iolib.file_count(source, wildcards='*.jpg') * n)


    for img_distorted, fname, _ in tqdm(FromPaths([tmpdir], wildcards='*.jpg').generate(pathonly=False)):
        t1 = transforms.Transform(transforms.gamma, p=1, gamma_=random.uniform(0.4, 1.4))
        t2 = transforms.Transform(transforms.intensity_wrapper, p=1, intensity_=random.uniform(-0.4, 0.4))
        Q = transforms.Transforms(t1, t2)
        Q.shuffle()
        Q.executeQueue(img_distorted, print_debug=True)
        _, fname, _ = iolib.get_file_parts2(fname)
        fld_out = path.normpath(path.join(dest, fname))
        cv2.imwrite(fld_out, Q.img_transformed)

    with suppress(Exception):
        shutil.rmtree(tmpdir)



if __name__ == "__main__":
    main()
