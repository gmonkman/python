# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Script to blur faces in images
'''
import argparse
import os.path as path
from shutil import copyfile

from funclib.iolib import get_file_parts2
from funclib.iolib import create_folder
from funclib.iolib import print_progress
from funclib.iolib import file_list_generator1 as flg

from opencvlib.faces import blur_face
from opencvlib.common import IMAGE_EXTENSIONS_AS_WILDCARDS


def main():
    '''
    Blurs faces in folders.
    '''
    cmdline = argparse.ArgumentParser(description='Attempts to apply a blur to faces in user specified folders.\n'
                                      'In overwrite mode, existing images are copied to a datetime stamped subfolder then the originals overwritten.\n'
                                      'Otherwise the anonymised images are copied to the new datetime stamped folder.\n'
                                      'The face regions can optionally be saved alongside the original images.\n'
                                      'Example:\n'
                                      'blur_faces.py -s -o "C:/images" "C:/other_images"'
                                      )
    cmdline.add_argument(
        '-s', '--save_faces', help='Save detected face regions with original images.', action='store_true')
    cmdline.add_argument(
        '-o', '--overwrite', help='Overwrite original images. Originals are backuped in a timestamped subfolder.', action='store_true')
    cmdline.add_argument(
        'dirs', help='list of directories to search for images in', nargs='+')
    args = cmdline.parse_args()

    for fld in args.dirs:
        if not path.exists(path.normpath(fld)):
            print('%s does not exist. Nothing was processed.' % fld)
            return

    # preload so can do progress bar
    images = [img for img in flg(args.dirs, IMAGE_EXTENSIONS_AS_WILDCARDS)]
    cnt = 0
    for img in images:
        try:
            blur_face(img, args.save_faces, args.overwrite)
        except Exception as e:
            print('Blur failed for %s. The error was %s' % (img, str(e)))
        finally:
            cnt += 1
            print_progress(cnt, len(images), '%s of %s' % (cnt, len(images)))

    print('\nDone.')


if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
