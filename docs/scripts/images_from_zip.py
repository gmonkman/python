# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
#THIS NEEDS TESTING
__doc__ = ('Extract images from all zip files in and below a root folder.')
import argparse
import os.path as _path

from docs.filetypes import Images
import docs.zip as zip
import funclib.iolib as iolib

from docs.zip import ExceptionNotAZip
from zipfile import BadZipFile
from zipfile import LargeZipFile


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('root', help='Root folder to recurse through to find zips. e.g. "C:/temp"')
    cmdline.add_argument('dest', help='Folder to extract to e.g. "C:/temp"')

    #named: eg script.py -part head
    #cmdline.add_argument('-part', '--part', help='The region part eg. head.', required=True)

    cmdline.add_argument('-r', '--recurse', help='Recurse through root and all subfolders', action='store_true')

    f = lambda s: [str(item) for item in s.split(',')]
    parser.add_argument('-f', '--folder_match', type=f, help='Comma delimited list of strings to match to folders, eg -f folderA,folderB')
    
    parser.add_argument('-n', '--name_match', type=f, help='Comma delimited list of strings to match to file names, eg -f fileA,fileB')

    args = cmdline.parse_args()

    zips = (z for z in iolib.file_list_generator1(args.root, '*.zip', recurse=args.recuruse)) #items are already normpathed
    PP = iolib.PrintProgress(len(zips))

    folder_match = tuple(args.folder_match) if args.folder_match else None
    name_match = tuple(args.name_match) if args.name_match else None

    for z in zips:   
        try:
            zip.extract(z, _path.normpath(args.dest), match_folder_name=folder_match, match_file_name=name_match, match_file_ext=Images.dotted()) 
        except (ExceptionNotAZip, BadZipFile, LargeZipFile) as e: #not fatal, continue on
            print(e)
        except Exception: #unexpted, stop eveything
            raise
        finally:
            PP.increment()
        
    print('Done. Zip extracted to %s' % _path.normpath(args.dest)) 
    
    
if __name__ == "__main__":
    main()


