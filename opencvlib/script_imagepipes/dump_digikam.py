# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Grab images from digikam  and dump out to
a new folder.

Options:
    -a: The root album name e.g. images. REQUIRED.
    -p: Option to restrict search within an album path e.g. bass/angler. OPTIONAL.
    -k: The key (i.e. parent) tag, e.g. -k letter. OPTIONAL.
    -t: A comma seperated list of tags to match under key, e.g. -t a,b,c,d'. REQUIRED.
    -s: Type of search, values are: OR|AND. OPTIONAL, defaults to AND, if a key (parent tag) is specified, this will be forced to OR.

    Positional argumenst at end
    <path to database> <destination folder>

Examples:
    Dump all images in album IMAGES, in child folder SCRAPED
    which has tags SPECIES/BASS, SPECIES/DAB or SPECIES/COD
        dump_digikam.py -a IMAGES -p SCRAPED -k SPECIES -t BASS,DAB,COD "C:/digikam.db" "C:/dump_to_folder"


    Dump all images with a tag bass and dab in the album IMAGES
    in database C:/digikam.db to folder C:/dump_to_folder
        dump_digikam.py -a IMAGES -k SPECIES -t BASS,DAB "C:/digikam.db" "C:/dump_to_folder"
'''
#dump_digikam.py -a images -t fid_overlay "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/all"
import argparse
from os import path

#import os
#from contextlib import suppress
from tqdm import tqdm

import funclib.iolib as iolib
from opencvlib.imgpipes.generators import DigiKam
from opencvlib.imgpipes.generators import DigikamSearchParams



def chkempty(dirs):
    '''check output dirs are empty'''
    if isinstance(dirs, str):
        dirs = [dirs]
    for d in dirs:
        iolib.create_folder(path.normpath(d))
        assert not iolib.folder_has_files(path.normpath(d)), '\nDir %s must be empty.' % path.normpath(d)


def main():
    '''main'''
    f = lambda s: [item for item in s.split(',')]
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-a', '--album', help='The root album name, e.g. images', required=True)
    cmdline.add_argument('-p', '--album_path', help='Option to restrict search to an album subfolder, e.g. bass/angler', default='')
    cmdline.add_argument('-k', '--key', help='The key (i.e. parent) tag', default='__any__')
    cmdline.add_argument('-s', '--search_type', help='Type of search, values are: OR|AND', default='AND')
    cmdline.add_argument('-t', '--tags', type=f, help='A comma seperated list of tags to match under key, e.g. -t a,b,c,d', required=True)
    cmdline.add_argument('db', help='Filename of digikam database')
    cmdline.add_argument('dest', help='Destination image folder')
    args = cmdline.parse_args()

    dest = path.normpath(args.dest)
    db = path.normpath(path.normpath(args.db))
    if not iolib.file_exists(db):
        print('Database %s not found' % db)
        return
    chkempty(dest)
    search_type = args.search_type.upper()
    key = '__any__' if args.key == '' else args.key
    tags = args.tags #should now be  a list, e.g. ['a', 'b', 'c', 'd']
    dic = {key:tags}

    search_type = DigikamSearchParams.SearchType.and_ if args.search_type == 'AND' else DigikamSearchParams.SearchType.or_
    dkp = DigikamSearchParams(album_label=args.album, relative_path=args.album_path, search_type=search_type, **dic)

    dk = DigiKam(dkp)
    #PP = iolib.PrintProgress(len(dk.image_list), init_msg='\nCopying files ...')
    for fname in tqdm(dk.image_list, ascii=True):
        #PP.increment()
        _ = iolib.file_copy(fname, dest, rename=True, create_dest=True, dest_is_folder=True)


if __name__ == "__main__":
    main()
