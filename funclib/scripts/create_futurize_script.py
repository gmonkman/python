# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Generate a futurize script to upgrade files to Python 3.5'''

import argparse
from os import path

import subprocess as _subprocess

from funclib.iolib import file_list_glob_generator
from funclib.iolib import write_to_file

# DEBUG Need to debug this before use


def main():
    '''execute if script was entry point'''
    parser = argparse.ArgumentParser(description='Create a futurize batch script for python (.py) files.\n'
                                     'Example:\n'
                                     'create_futurize_script -r -e -o c:/myscript.bat -f C:/Python352/Scripts/futurize.exe c:/development/python/funclib c:/development/python/dblib'
                                     )
    parser.add_argument('-r', '--recurse',
                        help='Recurse folders', action='store_true')
    parser.add_argument('-o', '--outfile', help='Output batch file')
    parser.add_argument('f', '--futurize_exe', help='Path to futurize executable',
                        default=r'C:\Python352\Scripts\futurize.exe')
    parser.add_argument('e', '--execute_script',
                        help='execute the script after creation', action='store_true')
    parser.add_argument('dirs', help='Folders to check', nargs='+')
    args = parser.parse_args()

    flds = [path.normpath(path.join(f, '*.py'))
            for f in file_list_glob_generator(args.dirs, recurse=True)]

    # c:/python352/Scripts/futurize -w -1
    # "C:/Development/python/funclib/plotlib/matplotlib-3d.py"

    for idx, val in enumerate(flds):
        flds[idx] = '%s -w -1 "%s"' % (args.futurize_exe, val)

    print('Creating futurize script at %s' % args.outfile)
    write_to_file(flds, open_in_npp=False, full_file_path=args.outfile)
    print('Done. Run the script from a command line/shell')

    if args.execute_script:
        p = _subprocess.Popen(path.normpath(args.execute_script), shell=True, stdout=_subprocess.PIPE)
        dummy, dummy1 = p.communicate()
        if p.returncode == 0:
            print('Reported to have finished successfully')
        else:
            print('Script terminated with errorcode %s' % p.returncode)


if __name__ == '__main__':
    main()
