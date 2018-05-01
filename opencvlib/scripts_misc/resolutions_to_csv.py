# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Get the resolutions of images in a folder
and export them to a csv with code and filename

Example:
resolutions_to_csv.py "C:/temp/fshpics"
'''
#Source images in: "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/processors/undistorted"

import argparse
import os.path as path

from funclib.iolib import get_file_parts2
import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from opencvlib.view import show
from opencvlib.imgpipes.generators import FromPaths
CSVOUT = 'resolutions_to_csv.csv'


#Fix to read in dab laser distances

def getkey(fname):
    '''(str) -> str
    Get key
    '''
    assert isinstance(fname, str)
    s = fname.replace('_UND', '')
    s = s.replace('.png', '')
    s = s.replace('.jpg', '')
    s = s.replace('.JPG', '')
    s = s.replace('_FISHUND', '')
    s = s.replace('r', '')
    return s


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images')
    args = cmdline.parse_args()
    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    out_file = path.normpath(path.join(folder, CSVOUT))

    outdata = [['key', 'x', 'y']]
    FP = FromPaths(folder)
    PP = PrintProgress(sum([1 for x in FP.generate(pathonly=True)]), init_msg='\nProcessing...')
    for img, fname, _ in FP.generate():
        PP.increment()
        _, fname, _ = get_file_parts2(fname)
        key =  getkey(fname)
        outdata.append([key, img.shape[1], img.shape[0]])


    print('Saving CSV data ...')
    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))





if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
