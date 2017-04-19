# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Copies files with defined tags to
a specified subfolder where the image has valid regions
'''
import argparse
import os.path as path
import json

import opencvlib.vgg as vgg
from funclib.iolib import print_progress
from funclib.baselib import dic_merge_two


def main():
    '''(str, kwags)->void
    Copies files matching the tags kwargs to
    the subfolder where the image has no set
    '''

    cmdline = argparse.ArgumentParser(description='Copies image files to a specified subfolder where which have'
                                      ' the specified tags in digikam\n\n'
                                      'Only images in the root of the VGG file folder are checked.\n\n'
                                      )
    cmdline.add_argument('-i', '--files_in',
                         help='VGG JSON files to merge', nargs='+')
    cmdline.add_argument('-f', '--fix_keys', help='Fix keys, only valid with the -c option',
                         action='store_true')  # position argument
    cmdline.add_argument('-o', '--out', help='Output file')
    args = cmdline.parse_args()

    vgg.SILENT = True

    # precheckes
    merged = {}

    cnt = 0
    for fname in args.files_in:
        fname = path.normpath(fname)
        if not path.isfile(fname):
            print('\nFile %s not found. Please check your paths.' % fname)
            return

        try:
            vgg.load_json(fname, args.fix_keys, backup=False)
            # Python 3.5 syntax y = {**x, **z} not currently supported in PTVS
            # 2017 Apr
            merged = dic_merge_two(merged, vgg.JSON_FILE)

        except Exception as e:
            s = ('Failed to load VGG JSON file %s.\n' /
                 'The error was %s.\n' /
                 'Check it is a valid JSON file.' % (fname, str(e)))
            print(s)
            return

        cnt += 1
        print_progress(cnt, len(args.files_in), "%s of %s" %
                       (cnt, len(args.files_in)))

    with open(path.normpath(args.out), 'w', encoding='utf8') as outfile:
        json.dump(merged, outfile, ensure_ascii=True)
    print('\nDone. Merged file is %s' % args.out)


if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
