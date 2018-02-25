# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Script to fix keys in a VGG file.
Discrepancies arise because editing tags in digikam changes file sizes,
this fixes the file sizes in the vgg file specified, and overwrites it
with the updated keys.

Assumes all images are in same folder as the vgg JSON file

Example:
    fix_keys.py "C:/temp/vgg.json" -b
'''
import argparse
import os.path as path

import opencvlib.imgpipes.vgg as vgg


def main():
    '''main entry if run from commandline
    '''
    cmdline = argparse.ArgumentParser(
        description='VGG keys use file sizes, this will fix keys in the '
                    'specified file where file sizes have changed. The '
                    'original file is overwritten.\n'
                    'Example:'
                    'fix_keys.py "C:/temp/vgg.json" -b'
                    )
    # position argument
    cmdline.add_argument('file', help='VGG JSON file to manipulate')
    cmdline.add_argument('-b', '--backup', help='Backup the VGG file before updating',
                         action='store_true')  # present or absent test
    args = cmdline.parse_args()

    vgg.SILENT = True
    print('Fixing keys...')
    vgg.load_json(path.normpath(args.file), fixkeys=True)  # also fixes keys
    print('Done')


if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
