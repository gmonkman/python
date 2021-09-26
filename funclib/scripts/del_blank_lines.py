# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''new script wih argparse'''
__doc__ = ('Create a copy of a text file without empty lines.'
            '\n\n'
            'Example:\n'
            'del_blank_lines.py "C:/file_in.csv" "file_out.csv"')

import argparse
import os.path as path

from funclib.iolib import PrintProgressFlash as PPF
from funclib.iolib import get_file_parts2 as gfp
def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description='Delete all empty lines from a text file'
                                        '\n\n'
                                        'Example:\n'
                                        'del_blank_lines.py "C:/test.csv" "testout.csv"'
                                        )
    cmdline.add_argument('file_in', help='File to process')
    cmdline.add_argument('file_out', help='Output filename')
    args = cmdline.parse_args()
    fname = path.normpath(args.file_in)
    outname = path.normpath(args.file_out)

    pth_in, _, _ = gfp(fname)
    pth_out, fname_out, _ = gfp(outname)

    if pth_out == '':
        outname = path.normpath(path.join(pth_in, fname_out))

    if path.isfile(outname):
        print('Output file %s already exists. Delete it first.' % outname)
        return

    msg = 'Opening file %s\n' % fname
    P = PPF(ticks=None, msg=msg)
    if path.isfile(fname):
        with open(fname, 'r', encoding="utf-8") as infile, open(outname, 'w') as outfile:
            for line in infile:
                P.update()
                if not line.isspace() and not line == '\n':
                    outfile.write(line)
        print('Done')
    else:
        print('Source file %s not found' % fname)


if __name__ == '__main__':
    main()
