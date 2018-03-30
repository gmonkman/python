# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''
Output defined rectangular ROIs specified
in a VGG file and save them to a specified folder

    -m: Action for handling file naming clashes. Valid modes are: "overwrite", "halt", "skip", "rename", "req_new_dir".'
        This must be explicitly specified.
    -p: File prefix to append to the outputted filename. Defaults to roi.
        Default='roi'
    Positional args:
        source_folder, output_folder, vgg_file_name

Modes:
    overwrite   overwite files with same name
    halt        stop processing if there is a name clash
    skip        do not save the file if file exists
    rename      save the file with a new name if it already exists in output_folder (random suffix used)
    req_new_dir the output_folder must not exist

Example:
    img2roi.py -m rename -p myprefix "C:/temp/image" "C:/temp/images/roi_whole" vgg_whole.json

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
vgg.SILENT = True

def main():
    '''
    Rotate images

    Example:
    view_images.py part:head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
    '''

    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-m', '--mode', help='Action for handling file naming clashes. Valid modes are: "overwrite", "halt", "skip", "rename", "req_new_dir"', required=True)
    cmdline.add_argument('-p', '--prefix', help='File prefix to append to the outputted filename', default='')
    cmdline.add_argument('source_folder', help='The folder containing the images and vgg file')
    cmdline.add_argument('output_folder', help='The folder to save the ROIs to')
    cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder')

    args = cmdline.parse_args()

    src = path.normpath(args.source_folder)
    out = path.normpath(args.output_folder)
    mode = path.normcase(args.mode)
    prefix = args.prefix

    assert src.lower() != out.lower(), 'The source and output folders must be different.'
    assert mode in MODES, 'Mode must be in %s, but got mode %s.' % (' '.join(MODES), mode)

    print('Mode is %s\n' % mode)

    vgg_file = path.normpath(src + '/' + args.vgg_file_name)
    vgg.load_json(vgg_file)
    print('Loaded vgg file %s' % vgg_file)

    if mode == 'req_new_dir':
        if iolib.folder_has_files(out):
            print('Mode was req_new_dir, but folder %s contains files')
            return
        iolib.create_folder(out)

    if path.isdir(out):
        print('Found output folder %s' % out)
    else:
        os.mkdir(out) #checked, this fails if out is a file
        print('Created output folder %s' % out)


    #only single vgg_file currently supported by this script, although the
    #generator can take a list of vgg files

    mkname = lambda dest_folder, prefix, fname_noext, suffix, ext: path.normpath(path.join(dest_folder, prefix + fname_noext + suffix + ext))
    saved = []
    not_saved = []
    already_existed = []
    G = VGGROI(vgg_file)
    PP.max = sum(1 for x in vgg.imagesGenerator(skip_imghdr_check=True))
    for img, pth, _ in G.generate(skip_imghdr_check=True):
        PP.increment()
        try:
            dummy, fname_noext, ext = iolib.get_file_parts(pth)
            outname = mkname(out, prefix, fname_noext, '', ext)
            if mode == 'overwrite':
                pass
            elif mode == 'halt':
                if path.isfile(outname):
                    raise FileExistsError('File %s already exists.' % outname)
            elif mode == 'skip':
                if path.isfile(outname):
                    already_existed.append(pth)
                    continue
            elif mode == 'rename':
                cnt = 0
                while True:
                    if cnt > 100:
                        raise InterruptedError('Name generation loop failed to generate a new name after 100 iterations')
                    cnt += 1
                    if not path.isfile(outname) and not path.isdir(outname):
                        break
                    outname = mkname(out, prefix, fname_noext, stringslib.rndstr(4), ext)

            if isinstance(img, np.ndarray):
                cv2.imwrite(outname, img)
                saved.append(outname)
            else:
                not_saved.append(pth)
        except FileExistsError as fee:
            raise fee
        except InterruptedError as ie:
            raise ie
        except Exception as dummy:
            pass




    if saved:
        print('\nExported ROIs:')
        print('\n'.join(saved))

    if not_saved:
        print('\nImages no ROI:')
        print('\n'.join(not_saved))

    if already_existed:
        print('\nNot exported, destination existed:')
        print('\n'.join(already_existed))

    print('\n%s of %s images dumped. %s images skipped.\n' % (len(saved), PP.max, len(already_existed)))
    print('%s images were in the file, but had no ROI defined.' % (PP.max - len(saved) - len(already_existed)))



if __name__ == "__main__":
    main()
