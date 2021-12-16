# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
__doc__ = ('Extract files from zips')

import os.path as _path
import shutil as _shutil
import zipfile as _zipfile 
from warnings import warn as _warn

import fuckit as _fuckit

import funclib.iolib as _iolib
import funclib.stringslib as _stringslib

class ExceptionNotAZip(Exception):
    """The file was not recognised as a zip file"""


#not currently used, behaviour of extract is just to 
#retain the original relative directory structure
def _mkdir(fname, saveto, use_zip_name_as_subfolder):
    '''make dir for extracted files'''
    saveto = _path.normpath(saveto)
    if use_zip_name_as_subfolder:
        saveto = _path.normpath('{}\{}'.format(saveto, zipname))
    _iolib.create_folder(saveto)


def extract(fname, saveto, match_folder_name=None, match_file_name=None, match_file_ext=None):
    '''(str, str, str|iter, str|iter, str|iter) -> void
    Extract all files
    fname:
        zip file name
    saveto:
        root folder to save extracted files to.
    match_folder_name:
        string or iterable containing simple strings to match on to the folder name (excluding any part of the file name)
    match_file_name:
        string or iterable containing simple strings to match on to the file name (excluding the dotted extension)
    match_file_ext:
         iterable of dotted file extensions to match

    Returns: None

    Notes: 
    This will silently overwrite files, so advise using a temporary folder to extract to.
    docs.filetypes has iterables of common file extensions.
    Any exception will stop extraction

    Example (note file extension are dotted):
        zip.extract('./myzip.zip', match_folder_name=('folder',), match_file_name=('1',), match_file_ext=('.doc',))
        zip.extract('./myzip.zip', match_file_name=('1',), match_file_ext=filetypes.Images.dotted)
    '''
    saveto, fname = tuple(_path.normpath(p) for p in (saveto, fname))
    _, zipname, _ = _iolib.get_file_parts(fname)
    
    if  not _zipfile.is_zipfile(fname):
        raise ExceptionNotAZip('{} is not a valid zipfile'.format(fname))

    with _zipfile.ZipFile(fname, mode='r') as Z: #open the zipfile
        for ZI in Z.infolist(): #iterate over ZipInfo objects in zipfile
            if ZI.is_dir():
                continue

            fld, fname, ext = _iolib.get_file_parts(ZI.filename)

            if match_file_name and not _stringslib.iter_member_in_str(fname, match_file_name, ignore_case=True):
                continue

            if match_folder_name and not _stringslib.iter_member_in_str(fld, match_folder_name, ignore_case=True):
                continue

            if match_file_ext and not ext in match_file_ext:
                continue

            Z.extract(ZI, path=saveto)
