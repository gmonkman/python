# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, no-member, ungrouped-imports, too-many-arguments, wrong-import-order, relative-import, too-many-instance-attributes, too-many-locals, unused-variable, not-context-manager
'''
various routines to work with the digikam library, stored in sqlite
'''
import os
import warnings

import cv2
import sqlite3

from funclib.baselib import get_platform
from funclib.iolib import get_available_drive_uuids
from funclib.stringslib import rreplace
from funclib.iolib import print_progress

import dblib.sqlitelib as sqlitelib

SPECIFIC_PATH_OVERRIDE = ''

def read_specific_path(pathin):
    '''(str)->str
    Use SPECIFIC_PATH_OVERRIDE if defined, primarily
    for if we run on a different computer
    '''
    if SPECIFIC_PATH_OVERRIDE == '':
        return pathin
    else:
        return SPECIFIC_PATH_OVERRIDE

class _ImagesValidator(object):
    '''Use this to process a list of digikam image paths.
    It processes the paths to generate valid and invalid links

    Pass a list of files during instance creation,
    or setting the image_files property to a list of files will also force a validation

    If cv_load_test is true, then validation will try and load images with cv2.imread.
    '''
    def __init__(self, file_ptrs=None):
        '''files is a list of paths'''
        self._image_files = file_ptrs
        self._invalid_image_files = []
        self._valid_image_files = []
        self.cv_load_test = False

        if not file_ptrs is None:
            self._validate()

    def _validate(self):
        '''go through self._image_paths and assign valid and invalid paths to module variables'''
        self._invalid_image_files = []
        for images in self._image_files:
            if not os.path.isfile(images):
                self._invalid_image_files.append(images)
            else:
                if self.cv_load_test:
                    try:
                        nd = cv2.imread(images)
                        if nd is None:
                            nd = None
                            self._invalid_image_files.append(images)
                    except Exception:
                        self._invalid_image_files.append(images)

        self._valid_image_files = list(set(self._image_files).difference(self._invalid_image_files))

    @property
    def invalid_count(self):
        '''number of invalid images'''
        return len(self._invalid_image_files)

    @property
    def valid_count(self):
        '''number of invalid images'''
        return len(self._image_files) - len(self._invalid_image_files)

    @property
    def total_count(self):
        '''total number of images'''
        return len(self._image_files)

    @property
    def invalid(self):
        '''return a list of images which are invalid
        from the image_names list'''
        return self._invalid_image_files

    @property
    def valid(self):
        '''->list
        return list of valid images, these have just
        been validated as existing and no attempt
        has been made to load in opencv UNLESS image_generator
        was used to generate the valid and invalid lists
        '''
        return self._valid_image_files

    @property
    def image_files(self):
        '''image_names getter
        returns list of image names with full path'''
        return self._image_files
    @image_files.setter
    def image_files(self, image_files):
        '''(list, bool)->void
        resets list of files and does basic validation

        If self.cv_load_test is false then does not attempt load in OpenCV,
        if self.cv_load_test is true it will test to see if file can
        be loaded in opencv, this can take a long time!

        You can optionally use image_generator which as well
        as generating nd arrays via cv2.imread()
        also set valid and invalid lists based on the
        success or imread()
        '''
        self._image_files = image_files
        self._validate()

    def image_generator(self):
        '''void->ndarray
        ndarray generator for all valid images read from the
        _image_paths list, which is set in class initialisation

        This also clears the current valid and invalid image lists and
        resets them based on if the image was successfully loaded by cv2.imread
        '''
        self._invalid_image_files = []
        self._valid_image_files = []
        for image in self._image_files:
            if os.path.isfile(image):
                try:
                    nd = cv2.imread(image)
                    self._valid_image_files.append(image)
                    yield nd
                except Exception:
                    self._invalid_image_files.append(image)
            else:
                self._invalid_image_files.append(image)

class _ReadFiles(object):
    '''executes the sql and generates and instantiates an ImageValidator member
    Handles conversion of digikam stored paths to actual file paths if in
    Linux or windows

    The SQL SELECT must include the fields:
        identifier, specificPath, relativePath and name
    '''

    def __init__(self, sql, dbfile):
        '''(str, str)
        SQL is an sql statement, which must include the fields
        identifier, specificPath, relativePath and name
        '''
        self.sql = sql
        self.dbfile = dbfile
        self.images = _ImagesValidator()
        self._read()

    def read(self, sql, dbfile):
        '''refresh images read from db using a new sql
        '''
        self.sql = sql
        self.dbfile = dbfile
        if sql != '' or not sql is None:
            self._read()

    def _read(self):
        '''void->void
        Loads image pointers into the ImagesValidator object, self.images

        Requires that the initial sql contains the fields:
          identifier
          specificPath
          relativePath
          name
        '''
        image_paths = []

        with sqlitelib.Conn(self.dbfile) as cn:
            assert isinstance(cn, sqlite3.Connection)

            cur = cn.cursor()
            cur.execute(self.sql)
            row = cur.fetchall()
            print('Reading image paths from digikam database')
            cnt = 0
            strip = ['-', 'VOLUMEID:?UUID=']
            drives = get_available_drive_uuids(strip=strip)
            invalid_uuids = []
            for res in row:
                if SPECIFIC_PATH_OVERRIDE == '':
                    if get_platform() == 'windows':
                        uuid = res['identifier'].upper()

                        for char in strip:
                            uuid = uuid.replace(char, '')

                        if uuid in drives:
                            drive = drives[uuid] + os.sep
                        else:
                            if not uuid in invalid_uuids:
                                invalid_uuids.append(uuid)
                                warnings.warn('No drive found for UUID', uuid)
                            drive = ''
                    elif get_platform() == 'linux':
                        drive = ''
                    else:
                        warnings.warn('Warning: Platform not recognised or unsupported. Treating as Linux.')
                        drive = ''
                else:
                    drive = SPECIFIC_PATH_OVERRIDE

                spath = read_specific_path(res['specificPath'])
                rpath = res['relativePath'] #.encode('ascii', 'ignore')
                name = os.sep + res['name'] #.encode('ascii', 'ignore')
                full_path = os.path.normpath(drive + spath + rpath + name)
                image_paths.append(full_path)
                cnt += 1
                print_progress(cnt, len(row), bar_length=30)

            self.images.image_files = image_paths


class MeasuredImages(object):
    '''Gets a list of my measured images from my digikamlib
    providing an ndarray (image) generator to access the list and
    as lists to valid, invalid images and the full list of all images in
    the database.

    The list is created from a view in the digikamlib.
    '''
    def __init__(self, dbfile, digikam_measured_tag, digikam_camera_tag):
        '''initialise the class'''
        self.digikam_measured_tag = digikam_measured_tag
        self.digikam_camera_tag = digikam_camera_tag
        self.dbfile = dbfile
        self._get_measured_images()
        self.Files = None

    def _get_measured_images(self):
        '''void->list
        returns list of full image paths
        from a digikam database using the module level _CONNECTION
        which needs to be previousl set
        '''
        sql = ('select distinct Images.id, AlbumRoots.identifier, AlbumRoots.specificPath, Albums.relativePath, images.name '
                'from Images '
                    ' inner join Albums on albums.id=images.album '
                    ' inner join AlbumRoots on AlbumRoots.id=Albums.albumRoot '
                'where '
                'Images.id in ( '
                'select '
                    'Images.id '
                'from images '
                    'inner join ImageTags on images.id=ImageTags.imageid '
                    'inner join Tags on Tags.id=ImageTags.tagid '
                'where '
                'Tags.name="camera") '
                'AND '
                'Images.id in ( '
                'select Images.id '
                'from images '
                'inner join ImageTags on images.id=ImageTags.imageid '
                'inner join Tags on Tags.id=ImageTags.tagid '
                'where '
                'Tags.name="' + self.digikam_measured_tag + '") '
                'AND '
                'Images.id in ( '
                'select Images.id '
                'from images '
                'inner join ImageTags on images.id=ImageTags.imageid '
                'inner join Tags on Tags.id=ImageTags.tagid '
                'where Tags.name="' + self.digikam_camera_tag + '")')

        self.Files = _ReadFiles(sql, self.dbfile)

class ImagePaths(object):
    '''This creates lists of paths to image files (ie the full file name, like C:/imgs/myimg.jpg)
    It also only uses files from digikam which exist on the file system.

    Create multiple ImagePaths and append results to master list
    to reproduce an OR query.
    '''
    def __init__(self, digikam_path):
        '''(str)
        set the path to the digikam db digikam4.db'''
        self.digikam_path = digikam_path

    def ImagesByTags(self, **kwargs):
        '''(Key-value kwargs representing parent tag name and child tag name)->list

        Retrieve images by the tags, where kwargs is parent key=child key
        Hence for bass, we would call using:
          ImagesByTags(species='bass')

        Pass in __any__ = <tag> for a single non-heirarchy match, eg __any__ = 'bass' will pick up anything tagged with bass anywhere

        Get a list of a images by the tags passed in args
        '''
        sql = [
            'select distinct '
                'Images.id, AlbumRoots.identifier, AlbumRoots.specificPath, Albums.relativePath, images.name '
            'from '
                'Images '
                'inner join Albums on albums.id=images.album '
                ' inner join AlbumRoots on AlbumRoots.id=Albums.albumRoot '
            'where '
                'Images.id in '
                    '( '
                        'select '
                            'images.id '
                        ' from '
                            'images '
                            ' inner join imagetags on images.id=ImageTags.imageid '
                            ' inner join tags on tags.id=imagetags.tagid '
                        'where '
                            'imagetags.tagid in '
                            '( '
                                'select '
                                    'children.id as tagid '
                                'from '
                                    'tags children '
                                    'left join tags parent on children.pid=parent.id '
                                'where '
                                #    'parent.name="species"'
                                  #  'AND children.name="bass"'
                         #   ')'
                  #  ')'
        ]

        where = [" parent.name='%s' AND children.name='%s' AND" % (key, value) for key, value in kwargs.items()]
        where[-1] = rreplace(where[-1], 'AND', '', 1)
        sql.append(''.join(where))
        sql.append('));')
        query = "".join(sql)

        #Fix string if we arnt bothered about a parent match for any kwarg args
        #which would look like:
        #where parent.name='__any__' AND children.name='bass'
        query.replace("parent.name='__any__' AND'", " ")
        rf = _ReadFiles(query, self.digikam_path)
        print('Total image paths: %s | Valid: %s | Invalid: %s' % (rf.images.total_count, rf.images.valid_count, rf.images.invalid_count))
        return rf.images.valid
