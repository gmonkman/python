# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''
Rotate images generated from VGG file and save them the specified folder.

Rotations are calculated by using two points without any attributes which
have been added to the image using vgg.

The output folder must be empty, and is created if it doesn't exist.

Example:
    rotate.py "C:/temp/image" "C:/temp/images/rotated" vgg_rotations.json
'''
import argparse
import os.path as path
import os
from shutil import copy2

import cv2

from funclib.baselib import list_not
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
    cmdline.add_argument('-u', '--unmarked_folder', help='Folder to copy files which have no rotations defined or are not in the vgg file', default='')
    cmdline.add_argument('source_folder', help='The folder containing the images and vgg file')
    cmdline.add_argument('output_folder', help='The folder to save the rotated images to')
    cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder')
    args = cmdline.parse_args()

    src = path.normpath(args.source_folder)
    out = path.normpath(args.output_folder)
    assert src.lower() != out.lower(), 'The source and output folders must be different.'

    if path.isdir(out):
        pass
    else:
        print('Creating dir %s' % out)
        os.mkdir(out) #checked, this fails if out is a file

    if iolib.folder_has_files(out, '.jpg'):
        print('Output folder "%s contains jpg files. The directory must be empty.' % out)
        return

    if args.unmarked_folder != '':
        unmarked_folder = path.normpath(args.unmarked_folder)
        if iolib.folder_has_files(unmarked_folder, '.jpg'):
            print('Unmarked folder "%s contains jpg files. The directory must be empty.' % unmarked_folder)
            return



    vgg_file = path.normpath(src + '/' + args.vgg_file_name)
    vgg.load_json(vgg_file)


    skipped = 0; processed = 0
    fskipped = []
    imgnames = []
    vgg_img_list = [i.filename for i in vgg.imagesGenerator(skip_imghdr_check=True)] #skip_imghdr_check=True set because was seeing jpgs being skipped despite being valid images
    PP.max = len(vgg_img_list)

    for I in vgg.imagesGenerator(skip_imghdr_check=True):
        if I.image_points:
            imgnames.append(I.filename)
            if len(I.image_points) != 2:
                fskipped.append(I.filename)
                skipped += 1
                continue
            L = roi.Line(*I.image_points)
            img = transforms.rotate(I.filepath, L.angle_min_rotation_to_x, no_crop=True)
            #img = transforms.equalize_adapthist(img)
            s = path.normpath(out + '/r' + I.filename)
            cv2.imwrite(s, img)
            processed += 1
        else:
            skipped += 1
            fskipped.append(I.filename)
        PP.increment()


    allfiles = [iolib.get_file_parts2(f)[1] for f in iolib.file_list_generator1(src, '*.jpg')]
    fnot_in_vgg = list_not(allfiles, imgnames)


    print('\n%s of %s images rotated. %s images skipped.\n' % (processed, PP.max, skipped))
    if fskipped:
        print('\nSkipped files were:\n%s' % '\n'.join(fskipped))
    if fnot_in_vgg:
        print('\nFiles in folder, not in vgg file:\n%s' % '\n'.join(fnot_in_vgg))

    if unmarked_folder != '' and (fnot_in_vgg or fskipped):
        copy_list = []
        try:
            for f in [*fnot_in_vgg, *fskipped]:
                fsrc = path.normpath(path.join(src, f))
                iolib.file_copy(fsrc, unmarked_folder, dest_is_folder=True)
                copy_list.append(f)
        except Exception as _:
            pass
        finally:
            if copy_list:
                print('Copied these skipped files:%s' % '\n'.join(copy_list))



if __name__ == "__main__":
    main()
    print('\nDone')
