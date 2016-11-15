# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, no-member, ungrouped-imports, too-many-arguments, wrong-import-order, relative-import, too-many-instance-attributes, too-many-locals, unused-variable, not-context-manager
'''
various routines to work with the digikam library, stored in sqlite
'''
import os

import cv2
import sqlite3
import fuckit

import funclib.iolib as iolib


class MeasuredImages(object):
    '''Gets a list of my measured images from my digikamlib
    providing an ndarray (image) generator to access the list and
    as lists to valid, invalid images and the full list of all images in
    the database.

    The list is created from a view in the digikamlib.
    '''
    cConn = sqlite3.connect(':memory:') #set in memory, simply so intellisense works
    cConn.row_factory = sqlite3.Row
    assert isinstance(cConn, sqlite3.Connection)

    def __init__(self, cn_str, digikam_measured_tag, digikam_camera_tag):
        '''initialise the class'''
        try:
            self.connect_string = cn_str
            self.digikam_measured_tag = digikam_measured_tag
            self.digikam_camera_tag = digikam_camera_tag
            self._image_names = None
            self._invalid_images = []
            MeasuredImages.cConn = sqlite3.connect(cn_str)
            MeasuredImages.cConn.row_factory = sqlite3.Row
            self._get_measured_images()
        except Exception:
            MeasuredImages.close()
            raise

    def __del__(self):
        with fuckit:
            MeasuredImages.close()

    def _set_invalid_images(self):
        '''create a list of images which look invalid'''
        self._invalid_images = []
        for images in self._image_names:
            if not os.path.isfile(images):
                if not iolib.file_exists(images):
                    self._invalid_images.append(images)

    @property
    def invalid_image_count(self):
        '''number of invalid images'''
        return len(self._invalid_images)

    @property
    def invalid_images(self):
        '''return a list of images which are invalid or could not be loaded
        from the image_names list'''
        return self._invalid_images

    @property
    def valid_images(self):
        '''->list
        return list of valid images
        '''
        return list(set(self._image_names).difference(self._invalid_images))

    @property
    def image_names(self):
        '''image_names getter
        returns list of image names with full path'''
        return self._image_names

    def image_generator(self):
        '''void->ndarray
        ndarray generator for all valid images read from the
        _image_names list
        '''
        self._invalid_images = []
        for image in self._image_names:
            if iolib.file_exists(image):
                try:
                    nd = cv2.imread(image)
                    yield nd
                except Exception:
                    self._invalid_images.append(image)
            else:
                self._invalid_images.append(image)

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

        image_paths = []
        cur = MeasuredImages.cConn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        for res in row:
            drive = iolib.get_drive_from_uuid(res['identifier'].encode('ascii', 'ignore'), strip=['-', 'volumeid:?uuid=']) + os.sep
            spath = res['specificPath'].encode('ascii', 'ignore')
            rpath = res['relativePath'].encode('ascii', 'ignore')
            name = os.sep + res['name'].encode('ascii', 'ignore')
            full_path = os.path.normpath(drive + spath + rpath + name)
            image_paths.append(full_path)
        self._image_names = image_paths
        self._set_invalid_images()

    @staticmethod
    def close(commit=False):
        '''close the engine'''
        with fuckit:
            if commit:
                MeasuredImages.cConn.commit()
            else:
                MeasuredImages.cConn.rollback()
            MeasuredImages.cConn.close()

    @staticmethod
    def commit():
        '''try a commit'''
        with fuckit:
            MeasuredImages.cConn.commit()

    @staticmethod
    def rollback():
        '''try a rollback'''
        with fuckit:
            MeasuredImages.cConn.rollback()
