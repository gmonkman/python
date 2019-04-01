
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''new script wih argparse'''
import argparse
import os.path as path
import pytesseract

import funclib.iolib as iolib
from textract.mags import SeaAngler




def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    #positional: e.g. scipt.py c:/temp
    #args.folder == 'c:/temp'
    cmdline.add_argument('folder', help='folder')
    args = cmdline.parse_args()
    fld = path.normpath(args.folder)



if __name__ == "__main__":
    main()
