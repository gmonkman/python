# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Script to blur faces in images
'''
import argparse
import os.path as path
from shutil import copyfile

from funclib.iolib import get_file_parts
from funclib.iolib import datetime_stamp as dts
from funclib.iolib import print_progress
from funclib.iolib import file_list_generator1 as flg

#DEBUG ebug fix_newlines.py script
def main():
    '''
    Blurs faces in folders.
    '''
    cmdline = argparse.ArgumentParser(description='Replaces newlines according to OS.\n'
                                      'Directories can be optionally recursed.\n'
                                      'Example:\n'
                                      'fix_newlines.py -n -r "C:/development/python/funclib" "C:/development/python/opencvlib"'
                                      )
    cmdline.add_argument(
        '-n', '--nobackup', help='Do not create a backup.', action='store_true')
    cmdline.add_argument(
        '-r', '--recurse', help='Recurse directories.', action='store_true')
    cmdline.add_argument(
        'dirs', help='list of directories to search for py files in', nargs='+')
    args = cmdline.parse_args()
    suffix = dts()
    for fld in args.dirs:
        if not path.exists(path.normpath(fld)):
            print('Path %s does not exist. Exiting.' % fld)
            return

    # preload so can do progress bar
    fs = []

    for f in flg(args.dirs, ['*.py'], recurse=args.recurse):
        fs.append(f)

    cnt = 0
    for f in fs:
        try:
            if not args.nobackup:
                backup = path.join(get_file_parts(f)[0], get_file_parts(f)[1] + suffix + get_file_parts(f)[2])
                copyfile(f, backup)

            fileContents = open(f,"r").read()
            with open(f, 'w', newline=None) as myfile:
                myfile.write(fileContents)
        except Exception as e:
            print('Newline fix for file %s failed. The error was %s' % (f, str(e)))
        finally:
            cnt += 1
            print_progress(cnt, len(fs), '%s of %s' % (cnt, len(fs)))

    print('Done.')


if __name__ == "__main__":
    main()
