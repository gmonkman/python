# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''
Take images in a folder of the same approximate size
and resize them to an average aspect ratio. Output
is saved to a different folder.

The output height can be set to the maximum, mean or minimum
of all the source images.

The resolution can be fixed by specifying integers for -r and -c
arguments.

Example:
    average_resize.py -h mean "C:/images" "C:/images/resized"
'''
#average_resize.py -h mean "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate/roi_whole" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate/roi_whole/resized"
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
    cmdline.add_argument('-r', '--rows', help="Target height/rows of the image, valid values are an int, 'mean', 'max' or min'.", default='mean')
    cmdline.add_argument('-c', '--cols', help="Target columns of the image, only valid if rows is an integer", default=0)
    cmdline.add_argument('source', help='Location of jpg images to resize.')
    cmdline.add_argument('output', help='Folder to copy resized images to.')
    args = cmdline.parse_args()

    src = path.normpath(args.source)
    out = path.normpath(args.output)

    if not chkdir(out):
        return

    PP = iolib.PrintProgress()
    PP.max = iolib.file_count(src, '*.jpg', False)
    if PP.max == 0:
        print('No jpg images in %s' % src)
        return

    skipped = 0; processed = 0

    res = info.ImageInfo.get_image_resolutions(path.normpath(path.join(src, '*.jpg')), False)
    if not res:
        print('Found no resolutions for images in "%s"' % src)
        return

    zres = list(zip(*res))
    heights = zres[1]
    widths = zres[0]

    minh = min(heights)
    minw = min(widths)

    h = sum(heights)/len(heights)
    w = sum(widths)/len(widths)

    if args.rows == 'mean':
        targ_rows = int(sum(x/len(heights) for x in heights))
    elif args.rows == 'max':
        targ_rows = max(heights)
    elif args.rows == 'min':
        targ_rows = min(heights)
    else:
        targ_rows = int(args.rows)
        targ_cols = 0
        if int(args.cols) != 0:
            targ_cols = int(args.cols)

    if targ_cols > 0:
        targ_width = targ_cols
    else:
        targ_width = int(targ_rows * (w/h))

    Gen = gen.FromPaths(src, '*.jpg')
    for img, fname, _ in Gen.generate():
        #img = transforms.histeq_color(img)
        img = transforms.resize(img, width=targ_width, height=targ_rows)
        f = iolib.get_file_parts2(fname)[1]
        s = path.normpath(path.join(out, f))
        cv2.imwrite(s, img)
        PP.increment()
        processed += 1



    print('\n%s of %s images processed. %s images skipped.\n' % (processed, PP.max, skipped))





if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
