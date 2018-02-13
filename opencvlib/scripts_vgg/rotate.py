# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Rotate images generated from VGG file and save them the specified folder.

Rotations are calculated by using two points without any attributes which
have been added to the image using vgg.

The output folder must be empty
Example:
rotate.py "C:/temp/image" "C:/temp/images/rotated" vgg_rotations.json
'''
import argparse
import os.path as path

import cv2

from opencvlib.view import show
import funclib.iolib as iolib
import opencvlib.roi as roi
import opencvlib.imgpipes.vgg as vgg
import opencvlib.transforms as transforms

PP = iolib.PrintProgress()

def main():
    '''
    Rotate images

    Example:
    view_images.py part:head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
    '''

    cmdline = argparse.ArgumentParser(description='Rotate images generated from VGG file'
                                      'and save them the specified folder\n\n'
                                      'Example:\n'
                                      'rotate.py "C:/temp/image" "C:/temp/images/rotated" "vgg_rotations.josn"'
                                      )
    cmdline.add_argument('source_folder', help='The folder containing the images and vgg file', required=True)
    cmdline.add_argument('output_folder', help='The folder to save the rotated images to', required=True)
    cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder', required=True)
    args = cmdline.parse_args()


    src = path.normpath(args.source_folder)
    out = path.normpath(args.output_folder)
    assert src.lower() != out.lower(), 'The source and output folders must be different.'
    assert not iolib.hasfile(out), 'Folder %s contains files. The directory must be empty.'

    vgg_file = path.normpath(src + '/' + args.vgg_file_name)
    vgg.load_json(vgg_file)

    PP.max = iolib.file_count(src, '*.jpg', False)

    skipped = 0; processed = 0
    for I in vgg.imagesGenerator():
        PP.increment
        if len(I.image_points) != 2:
            skipped += 1
            continue

        L = roi.Line(*I.image_points)
        img = transforms.rotate(I.filepath, L.angle_to_x, no_crop=True)
        s = path.normpath(out + '/r' + I.filename)
        cv2.imwrite(s)
        processed += 1

    print('\n%s of %s images rotated. %s images skipped.\n' % (processed, PP.max, skipped))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
