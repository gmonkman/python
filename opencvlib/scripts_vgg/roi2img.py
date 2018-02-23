# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''
Output defined rectangular ROIs specified
in a VGG file and save them to a specified folder

    -m: Action for handling file naming clashes. Valid modes are: "overwrite", "halt", "skip", "rename", "req_new_dir".'
        Default='rename'
    -p: File prefix to append to the outputted filename. Defaults to roi.
        Default='roi'
    Positional args:
        source_folder, output_folder, vgg_file_name

Modes:
    overwrite   overwite files with same name
    halt        stop processing if there is a name clash
    skip        do not save the file if file exists
    rename      save the file with a new name (random suffix used)
    req_new_dir the output_folder must not exist

Example:
    roi2img.py -m rename -p myprefix "C:/temp/image" "C:/temp/images/rotated" vgg_rotations.json

Comments:
    output_folder will be created if it doesn't exist
'''

import argparse
import os.path as path
import os
import numpy as np
import cv2

import funclib.iolib as iolib
import funclib.stringslib as stringslib
import opencvlib.roi as roi
import opencvlib.imgpipes.vgg as vgg
from opencvlib.imgpipes.generators import VGGROI
import opencvlib.transforms as transforms
from opencvlib.view import show

PP = iolib.PrintProgress()
MODES = ['overwrite', 'halt', 'skip', 'rename', 'req_new_dir']


def main():
    '''
    Rotate images

    Example:
    view_images.py part:head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
    '''

    cmdline = argparse.ArgumentParser(description='Output defined rectangular ROIs specified'
                                      'in a VGG file and save them to a specified folder\n\n'
                                      'Example:\n'
                                      'roi2img.py -m overwrite -p roi "C:/temp/image" "C:/temp/images/rotated" "vgg_rotations.josn"'
                                      )

    cmdline.add_argument('-m', '--mode', help='Action for handling file naming clashes. Valid modes are: "overwrite", "halt", "skip", "rename", "req_new_dir"', default='rename')
    cmdline.add_argument('-p', '--prefix', help='File prefix to append to the outputted filename', default='')
    cmdline.add_argument('source_folder', help='The folder containing the images and vgg file')
    cmdline.add_argument('output_folder', help='The folder to save the ROIs to')
    cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder')

    args = cmdline.parse_args()

    src = path.normpath(args.source_folder)
    out = path.normpath(args.output_folder)
    mode = path.normcase(args.mode)
    prefix = args.prefix
    if mode == 'req_new_dir':
        assert src.lower() != out.lower(), 'The source and output folders must be different.'
    assert mode in [MODES], 'Mode must be empty or in %s' % ''.join(MODES)

    print('\nMode is %s\n' % mode)

    vgg_file = path.normpath(src + '/' + args.vgg_file_name)
    vgg.load_json(vgg_file)
    PP.max = iolib.file_count(src, '*.jpg', False)
    skipped = 0; processed = 0

    if path.isdir(out):
        pass
    else:
        os.mkdir(out) #checked, this fails if out is a file


    #only single vgg_file currently supported by this script, although the
    #generator can take a list of vgg files

    mkname = lambda dest_folder, prefix, fname_noext, suffix, ext: path.normpath(path.join(dest_folder, prefix + fname_noext + suffix + ext))

    G = VGGROI(vgg_file)
    for img, pth, _ in G.generate():
        try:
            dummy, fname_noext, ext = iolib.get_file_parts(pth)
            outname = path.normpath(path.join(out, prefix + fname_noext + ext))
            outname = mkname(out, prefix, fname_noext, '', ext)
            if mode == 'overwrite':
                pass
            elif mode == 'halt':
                if path.isfile(outname):
                    raise FileExistsError('File %s already exists.' % outname)
            elif mode == 'skip':
                if path.isfile(outname):
                    print('Image %s skipped because it already exists in %s' % (pth, out))
                    continue
            elif mode == 'rename':
                cnt = 0
                while True:
                    if cnt > 100:
                        raise InterruptedError('Name generation loop failed to generate a new name after 100 iterations')
                    cnt += 1
                    outname = mkname(out, prefix, fname_noext, stringslib.rndstr(4), ext)
                    if not path.isfile(outname) and not path.isdir(outname):
                        break

            if isinstance(img, np.ndarray):
                cv2.imwrite(outname, img)
                PP.increment()
                processed += 1
                print('ROI %s saved' % outname)
            else:
                print('ROI **NOT SAVED** for file %s' % pth)
        except FileExistsError as fee:
            raise fee
        except InterruptedError as ie:
            raise ie
        except Exception as dummy:
            pass


    print('\n%s of %s images dumped. %s images skipped.\n' % (processed, PP.max, skipped))



if __name__ == "__main__":
    main()