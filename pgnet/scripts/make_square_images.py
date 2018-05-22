# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Create square and noise mages in two folders.

make_square_images.py "C:/squares" "C:/noise"

Distribute them using pgnet.sort_test_train_eval.py, you'll need to edit pgnet.ini
'''
#dump_digikam.py -a images -t fid_overlay "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/all"
import argparse
from os import path

import cv2
import numpy as np

from funclib.iolib import PrintProgress
import funclib.iolib as iolib
from funclib import stringslib
from opencvlib.imgpipes.generators import DigiKam
from opencvlib.imgpipes.generators import DigikamSearchParams



def chkempty(dirs):
    '''check output dirs are empty'''
    if isinstance(dirs, str):
        dirs = [dirs]
    for d in dirs:
        iolib.create_folder(path.normpath(d))
        assert not iolib.folder_has_files(path.normpath(d)), '\nDir %s must be empty.' % path.normpath(d)


def main():
    '''main'''
    f = lambda s: [item for item in s.split(',')]
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-r', '--rows', help='rows (h) of image in pixels', default=200)
    cmdline.add_argument('-c', '--columns', help='columns (w) of image in pixels', default=200)
    cmdline.add_argument('-d', '--depth', help='image channels', default=3)
    cmdline.add_argument('-s', '--side', help='square side length in pixels', default=50)
    cmdline.add_argument('-n', '--nr', help='number of noise images and number of square images', default=400)
    cmdline.add_argument('squaredir', help='Destination for square containing images')
    cmdline.add_argument('noisedir', help='Destination image folder to create random noise images')
    cmdline.add_argument('circledir', help='Destination image folder to create circle images')
    args = cmdline.parse_args()

    height = int(args.rows); width = int(args.columns); channels = int(args.depth); side = int(args.side); nr = int(args.nr)
    assert channels in [1,3], 'Need or two channels'
    assert side < height and side < width, 'Square side is bigger than height or width'

    squaredir = path.normpath(args.squaredir)
    noisedir = path.normpath(args.noisedir)
    circledir = path.normpath(args.circledir)
    assert noisedir != squaredir != circledir, 'circledir, noisedir or squaredir were the same'
    chkempty(squaredir)
    chkempty(noisedir)

    PP = PrintProgress(nr, init_msg='\nCreating noise and squares ...')
    for n in range(nr):
        PP.increment()
        square = np.ones((width, height, channels)) * 255
        circle = square.copy()
        circle = cv2.circle(circle, (100,100), 50, (0, 0, 255), -1)
        square[0:side, 0:side, ...] = int(np.random.uniform(0, 50))
        noise = np.random.uniform(0, 255, size=(height * width * channels)).reshape((height, width, channels))

        while True:
            sqname = path.normpath(path.join(squaredir, '%s%s' % (stringslib.rndstr(5), '.jpg')))
            if not iolib.file_exists(sqname):
                break

        while True:
            cirname = path.normpath(path.join(circledir, '%s%s' % (stringslib.rndstr(5), '.jpg')))
            if not iolib.file_exists(cirname):
                break

        while True:
            nname = path.normpath(path.join(noisedir, '%s%s' % (stringslib.rndstr(5), '.jpg')))
            if not iolib.file_exists(nname):
                break

        cv2.imwrite(sqname, square)
        cv2.imwrite(nname, noise)
        cv2.imwrite(cirname, circle)





if __name__ == "__main__":
    main()
