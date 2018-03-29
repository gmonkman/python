# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''
Merge multiple vgg files.

Example
merge_vggs.py - "C:/temp/a.json" "D:/temp/c.json" -o "C:/temp/merged.json"
'''
import argparse
import os.path as path
import json

import opencvlib.imgpipes.vgg as vgg
from funclib.iolib import print_progress
from funclib.baselib import dic_merge_two


def main():
    '''entry'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-i', '--files_in', help='VGG JSON files to merge', nargs='+', required=True)
    cmdline.add_argument('-o', '--out', help='Output file', required=True)
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
            vgg.load_json(fname)
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
