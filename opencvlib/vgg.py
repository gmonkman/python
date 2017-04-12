# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''handles getting additional region data generated from vgg jason files
http://www.robots.ox.ac.uk/~vgg/software/via/

Note that this assumes that the VGG file is in the same folder
as the images for the key fix hack to work

Coordinate system for VGG is:
x = Columns, with origin at left
y = Rows, with origin at top

So: 50x50 image. Top Left x=0,y=0: Bottom Right x=50, y=50
'''

import os.path as path
import json
import logging
from shutil import copy

from cv2 import convexHull
import numpy as np

from funclib.stringslib import datetime_stamp
from funclib.iolib import get_file_parts
from funclib.baselib import dictp
from opencvlib.common import rect_as_points

_JSON_FILE_NAME = ''
_JSON_FILE = []
_LOG_FILE_NAME = 'vgg.py.' + datetime_stamp() + '.log'

_VALID_SHAPES = ['', 'polygon', 'rect', 'circle', 'ellipse', 'point']
_VALID_PARTS = ['', 'whole', 'head']
_VALID_SPECIES = ['bass', 'dab', 'mackerel', 'flounder', 'dogfish', 'plaice', 'gurnard grey',
                  'flatfish', 'cod']

logging.basicConfig(filename=_LOG_FILE_NAME, filemode='w', level=logging.DEBUG)
print('Logging to', _LOG_FILE_NAME)

def _fix_keys():
    '''loop through json file and correct file sizes
    '''
    for key, value in _JSON_FILE.items():
        #relies on VGG JSON file being in same dir as files
        filepath, filepart, ext = get_file_parts(_JSON_FILE_NAME)
        filename = _JSON_FILE[key]['filename']
        fullname = path.join(filepath, filename)
        size_in_bytes = path.getsize(fullname)
        newkey = filename + str(size_in_bytes)
        _JSON_FILE[newkey] = _JSON_FILE.pop(key)
    save_json()

class Image(object):
    '''Load and iterate VGG configured image regions
    based on the image name, size and path
    '''
    def __init__(self, filepath=''):
        '''(str)
        optionally provide a filepath - ie a path including the file name
        '''
        self.size_in_bytes = 0
        self.filepath = filepath
        self.size_in_bytes = 0
        self.key = ''
        self.filename = ''
        self.fileext = ''
        self.filefolder = ''
        #self.key_ignores_filesize = key_ignores_filesize
        self.load_image(filepath)

    def _get_key(self):
        '''->[str | None]
        Generate unique key for image file
        Returns None if no image file does not exist
        or an error occurs
        '''
        if path.isfile(self.filepath):
            try:
                self.size_in_bytes = path.getsize(self.filepath)
                #return self.filename + str(self.size_in_bytes)
                return self.filename #Not using exact key as file sizes can change when image tags change
            except Exception:
                log = 'Failed to generate key for file %s' % self.filepath
                logging.warning(log)
                return None
        else:
            log = 'File not found %s' % self.filepath
            logging.warning(log)
            return None

    def load_image(self, filepath):
        '''(str,int)->void
        try loading image data from JSON file, key is unique per image
        '''
        self.filepath = filepath
        if filepath != '':
            self.filefolder, self.filename, self.fileext = get_file_parts(path.abspath(path.normpath(self.filepath)))
            self.filename = self.filename + self.fileext
            self.key = self._get_key()

    def subjects_generator(self, species):
        '''(str)->Subject
        identify subject of given species'''
        subjectids = []

        if not species in _VALID_SPECIES:
            raise ValueError('Invalid species ' + species)

        d = dictp(_JSON_FILE)
        regions = d[self.key]['regions']

        if regions:
            for key, region in regions.items():
                if region['region_attributes']['species'].casefold() == species.casefold():
                    subjectid = region['region_attributes']['subjectid']
                    if not subjectid in subjectids:
                        subjectids.append(subjectid)
                        sbj = _Subject(self.key, subjectid)
                        yield sbj
        else:
            s = 'No VGG regions defined for image %s' % self.filepath
            logging.warning(s)

class _Subject(object):
    '''really a fish object, has many regions
    Should not be accessed directly.
    Iterate through the Images class subjects_generator.
    '''
    def __init__(self, key, subjectid):
        '''(str, str)
        Key is the unique key for the image,
        subjectid is set as an integer to uniquely identify a subject
        '''
        self.key = key
        self.subjectid = subjectid
        self.region_ids = set([])
        self.set_regions()

    def set_regions(self):
        '''
        Checks all regions defined on the image, regions which
        are defined on the same Object/Subject (by subjectid set in VGG) have their region key
        saved to region_ids for access later
        '''
        d = dictp(_JSON_FILE)
        regions = d[self.key]['regions']

        for key, region in regions.items():
            if region['region_attributes']['subjectid'] == self.subjectid:
                self.region_ids.add(key)

    def regions_generator(self, part='', shape=''):
        '''(str, str)->Yields Region classes
        Yields regions for the given subject in the photo
        (identifed by its subjectid) which is unique within image only.

        If part == '', yields all parts associated with the object/subject
        Otherwise only yields the part specified (e.g., head or whole)

        If shape is specified, only yields regions of the corresponding shape

        If no region attributes assumes region is the whole object ('whole')
        '''
        if part not in _VALID_PARTS:
            raise ValueError('Invalid image region type (part) ' + part)

        if shape not in _VALID_SHAPES:
            raise ValueError('Invalid shape ' + part)

        d = dictp(_JSON_FILE)
        regions = d[self.key]['regions']

        for region_key in self.region_ids:
            shape_attr =  regions[region_key]['shape_attributes']
            region_attr = regions[region_key]['region_attributes']
            if shape_attr:
                reg = _Region(part=region_attr.get('part', 'whole'),
                    species=region_attr.get('species'),
                    shape=shape_attr.get('name'),
                    x=shape_attr.get('x'),
                    y=shape_attr.get('y'),
                    r=shape_attr.get('r'),
                    w=shape_attr.get('w'),
                    h=shape_attr.get('h'),
                    all_points_x=shape_attr.get('all_points_x'),
                    all_points_y=shape_attr.get('all_points_y'))
                if part == '' or part.casefold() == region_attr['part'].casefold():
                    if shape == '' or shape.casefold() == shape_attr.get('name'):
                        yield reg
            else:
                s = 'shape_attributes undefined in VGG for image key %s' % self.key
                logging.warning(s)

class _Region(object):
    def __init__(self, **kwargs):
        '''supported kwargs
        name= [circle | polygon | rect]
        object_part = [head, whole]

        circle: x,y,r
        rect: x,y,w,h
        polygon: [all_points_x], [all_points_y]  [10,20,50], [30,50, 100]

        values set to None if not read

        Coordinate system for VGG is:
        x = Columns, with origin at left
        y = Rows, with origin at top

        So: 50x50 image. Top Left x=0,y=0: Bottom Right x=50, y=50
        '''
        self.shape = kwargs.get('shape')
        self.species = kwargs.get('species')
        self.part = kwargs.get('part')

        if self.shape == 'rect':
            self.x = kwargs.get('x')
            self.y = kwargs.get('y')
        else: #points, ellipses, circles
            self.x = kwargs.get('cx')
            self.y = kwargs.get('cy')

        #ellipse only
        self.rx = kwargs.get('rx')
        self.ry = kwargs.get('ry')

        #circles only
        self.r = kwargs.get('r')

        #rect
        self.w = kwargs.get('w')
        self.h = kwargs.get('h')

        #polygon
        self.all_points_x = kwargs.get('all_points_x')
        self.all_points_y = kwargs.get('all_points_y')

        if self.shape == 'polygon':
            self.all_points = list(zip(self.all_points_x, self.all_points_y))
        elif self.shape == 'point':
            self.all_points = [(self.x, self.y)]
        elif self.shape == 'rect':
            self.all_points = rect_as_points(self.y, self.x, self.h, self.w)

def load_json(vgg_file, fix_keys=True):
    '''(str)->void
    Load the VGG JSON file into the module variable _JSON_FILE
    '''
    pth = path.normpath(vgg_file)
    global _JSON_FILE
    global _JSON_FILE_NAME
    with open(pth) as data_file:
        _JSON_FILE = json.load(data_file)
    _JSON_FILE_NAME = pth
    if fix_keys:
        _fix_keys()

def save_json():
    '''->void
    called after we have fixed the keys in the JSON file
    to reflect any changes in image filesize
    caused by changing tags
    '''
    filepath, filename, ext = get_file_parts(_JSON_FILE_NAME)
    bk = path.join(filepath,filename + datetime_stamp + ext + '.bak')
    copy(_JSON_FILE_NAME, bk)
    s = 'Created backup of VGG file %s' % bk
    print(s)
    logging.info(s)
    with open(_JSON_FILE_NAME, 'w') as outfile:
        json.dump(_JSON_FILE, outfile)
