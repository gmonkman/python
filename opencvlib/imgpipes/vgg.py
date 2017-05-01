# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
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
from math import pi

from cv2 import boundingRect

from funclib.stringslib import datetime_stamp
from funclib.baselib import dictp

from funclib.iolib import get_file_parts
from funclib.iolib import get_file_parts2

from funclib.iolib import print_progress
from funclib.baselib import list_not
from funclib.baselib import list_and

from opencvlib.roi import rect_as_points
from opencvlib.roi import bounding_rect_of_poly
from opencvlib.roi import poly_area
from opencvlib.roi import bounding_rect_of_ellipse
from  opencvlib import ImageInfo

SILENT = True
_JSON_FILE_NAME = ''
JSON_FILE = []
_LOG_FILE_NAME = 'vgg.py.' + datetime_stamp() + '.log'

VALID_SHAPES_ALL = ['', 'polygon', 'rect', 'circle', 'ellipse', 'point']
VALID_SHAPES_2D = ['polygon', 'rect', 'circle', 'ellipse']

VALID_PARTS = ['', 'whole', 'head']
VALID_SPECIES = ['bass',
                 'dab',
                 'mackerel',
                 'flounder',
                 'dogfish',
                 'plaice',
                 'gurnard grey',
                 'flatfish',
                 'cod']


def valid_parts_in_list(parts, silent=False):
    for r in list_not(parts, VALID_PARTS):
        if not silent:
            print('Part %s invalid' % r)
    return list_and(parts, VALID_PARTS)

def valid_species_in_list(species, silent=False):
    for r in list_not(species, VALID_SPECIES):
        if not silent:
            print('Species %s invalid' % r)
    return list_and(species, VALID_SPECIES)

def _prints(s):
    if not SILENT:
        print(s)


logging.basicConfig(format='%(asctime)s %(message)s',
                    filename=_LOG_FILE_NAME,
                    filemode='w',
                    level=logging.DEBUG)

_prints('Logging to %s' % _LOG_FILE_NAME)


def fix_keys(backup=True, show_progress=False):
    '''loop through json file and correct file sizes
    '''
    cnt = 0
    _prints('\n\nFixing keys...\n')
    for key in JSON_FILE:
        # relies on VGG JSON file being in same dir as files
        filepath = get_file_parts(_JSON_FILE_NAME)[0]
        filename = JSON_FILE[key]['filename']
        fullname = path.join(filepath, filename)
        size_in_bytes = path.getsize(fullname)
        newkey = filename + str(size_in_bytes)
        JSON_FILE[newkey] = JSON_FILE.pop(key)

        if not SILENT or show_progress:
            cnt += 1
            s = '%s of %s' % (cnt, len(JSON_FILE))
            print_progress(cnt, len(JSON_FILE), s, bar_length=30)

    save_json(backup)
    _prints('\n\nKey fixing complete.\n')

def imagesGenerator():
    '''Generate VGG.Image class objects
    for every image in the vgg file
    '''
    for img in JSON_FILE:
        pth = get_file_parts2(_JSON_FILE_NAME)[0]
        img_pth = path.join(pth, img['filename'])
        if ImageInfo.is_image(img_pth):
            i = Image(img_pth)
            yield i

class Image(object):
    '''Load and iterate VGG configured image regions
    based on the actual image file name, size and path
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
        Returns None if image file does not exist
        or an error occurs
        '''
        if path.isfile(self.filepath):
            try:
                self.size_in_bytes = path.getsize(self.filepath)
                # return self.filename + str(self.size_in_bytes)
                return self.filename  # Not using exact key as file sizes can change when image tags change
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
            self.filefolder, self.filename, self.fileext = get_file_parts(
                path.abspath(path.normpath(self.filepath)))
            self.filename = self.filename + self.fileext
            self.key = self._get_key()

    def subjects_generator(self, species):
        '''(str)->Subject
        identify subject of given species'''
        subjectids = []

        if species not in VALID_SPECIES:
            raise ValueError('Invalid species ' + species)

        d = dictp(JSON_FILE)
        regions = d[self.key]['regions']

        if regions:
            assert isinstance(regions, dict)
            for region in regions.values():
                if region.get('region_attributes').get('species', '').casefold() == species.casefold():
                    subjectid = region.get(
                        'region_attributes').get('subjectid')
                    if subjectid not in subjectids:
                        subjectids.append(subjectid)
                        sbj = Subject(self.key, subjectid)
                        yield sbj
        else:
            s = 'No VGG regions defined for image %s' % self.filepath

            if not SILENT:
                print(s)
            logging.warning(s)

    @property
    def subject_count(self, species=''):
        '''str->int
        Returns number of valid regions

        If species is set, checks for that species only
        '''
        cnt = 0

        for spp in VALID_SPECIES:
            if species.casefold() == spp.casefold() or species == '':
                for region in self.subjects_generator(spp):
                    cnt += 1
        return cnt

    @property
    def shape_count(self):
        '''->int
        Returns number of shapes
        '''
        d = dictp(JSON_FILE)
        regions = d[self.key]['regions']
        cnt = 0
        if regions:
            assert isinstance(regions, dict)
            for region in regions.values():
                if region.get('shape_attributes'):
                    cnt += 1
        return cnt


class Subject(object):
    '''really a fish object, has many regions
    Should not be accessed directly.
    Iterate through the Images class subjects_generator.

    If no subjectid is used to initialise the class, then
    the iterator will ignore subject assignmensts, ie all
    regions are treated as belonging to the same subject (fish)
    '''

    def __init__(self, key, subjectid=None):
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

        d = dictp(JSON_FILE)
        regions = d[self.key]['regions']

        for key, region in regions.items():
            # if called with no subject id, just yield all the regions in
            # regions generator,
            # this ignores subject and assumes there is only one fish.
            # This is used write_region_attributes

            if self.subjectid is None:
                self.region_ids.add(key)
            else:
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
        if part not in VALID_PARTS:
            raise ValueError('Invalid image region type (part) ' + part)

        if shape not in VALID_SHAPES_ALL:
            raise ValueError('Invalid shape ' + part)

        d = dictp(JSON_FILE)
        regions = d[self.key]['regions']

        # region_ids is the ids of all regions which share a common
        # region_attributes['subjectid']
        for region_key in self.region_ids:
            shape_attr = regions[region_key]['shape_attributes']
            region_attr = regions[region_key]['region_attributes']
            if shape_attr:
                reg = Region(part=region_attr.get('part', 'whole'),
                             image_key=self.key,  # no get, error if doesnt exist
                             has_attrs=True if region_attr else False,
                             region_key=region_key,  # no get, error if doesnt exist
                             species=region_attr.get('species'),
                             subjectid=region_attr.get('subjectid'),
                             shape=shape_attr.get('name'),
                             x=shape_attr.get('x'),
                             y=shape_attr.get('y'),
                             r=shape_attr.get('r'),
                             w=shape_attr.get('width'),
                             h=shape_attr.get('height'),
                             all_points_x=shape_attr.get('all_points_x'),
                             all_points_y=shape_attr.get('all_points_y'))
                if part == '' or part.casefold() == region_attr['part'].casefold():
                    if shape == '' or shape.casefold() == shape_attr.get('name'):
                        yield reg
            else:
                s = 'shape_attributes undefined in VGG for image key %s' % self.key
                logging.warning(s)


class Region(object):
    '''Object representing a a single shape marked on a subject,
    like a head or the whole.

    Note opencv points have origin in top left and are (x,y) ie col,row (width,height). Not the matrix standard.
    '''

    def __init__(self, **kwargs):
        '''supported kwargs
        name= [circle | polygon | rect]
        object_part = [head, whole]

        circle: x,y,r
        rect: x,y,w,h
        polygon: [all_points_x], [all_points_y]  [10,20,50], [30,50, 100]

        values set to None if not read

        Coordinate system for VGG (which is the same as *points* in opencv) is:
        x = Columns, with origin at left
        y = Rows, with origin at top

        So: 50x50 image. Top Left x=0,y=0: Bottom Right x=50, y=50

        bounding_rectangle property is the x,y,w,h representation of a rectangle
        '''
        self.image_key = kwargs['image_key']
        self.has_attrs = kwargs.get('has_attrs')
        # should never be None (but can be an empty dict), so error if not
        # present
        self.region_key = kwargs['region_key']
        self.shape = kwargs.get('shape')
        self.species = kwargs.get('species')
        self.part = kwargs.get('part')
        self.subjectid = kwargs.get('subjectid')
        self.area = 0
        if self.shape == 'rect':
            self.x = kwargs.get('x')
            self.y = kwargs.get('y')
        else:  # points, ellipses, circles
            self.x = kwargs.get('cx')
            self.y = kwargs.get('cy')

        # ellipse only
        self.rx = kwargs.get('rx')
        self.ry = kwargs.get('ry')

        # circles only
        self.r = kwargs.get('r')

        # rect
        self.w = kwargs.get('w')
        self.h = kwargs.get('h')

        # polygon
        self.all_points_x = kwargs.get('all_points_x')
        self.all_points_y = kwargs.get('all_points_y')

        if self.shape == 'polygon':
            self.all_points = list(zip(self.all_points_x, self.all_points_y))
            self.area = poly_area(pts=self.all_points)
            self.bounding_rectangle_as_points = bounding_rect_of_poly(
                self.all_points)
            self.bounding_rectangle = boundingRect(self.all_points)
        elif self.shape == 'point':
            self.all_points = [(self.x, self.y)]
            self.bounding_rectangle_as_points = None
        elif self.shape == 'rect':
            self.all_points = rect_as_points(self.x, self.y, self.w, self.h)
            self.area = poly_area(pts=self.all_points)
        elif self.shape == 'circle':
            self.area = pi * self.r ** 2
            self.bounding_rectangle_as_points = bounding_rect_of_ellipse(
                (self.x, self.y), self.r, self.r) #circle is just an ellipse
            self.bounding_rectangle = [
                self.rx - self.r, self.ry - self.r, self.r * 2, self.r * 2]
        elif self.shape == 'ellipse':
            self.area = pi * self.rx * self.ry
            self.bounding_rectangle_as_points = bounding_rect_of_ellipse(
                (self.x, self.y), self.rx, self.ry)
            self.bounding_rectangle = [
                self.rx - self.rx, self.ry - self.ry, self.rx * 2, self.ry * 2]

    def write(self):
        '''->void
        write the region to the in memory json file _JSON_FILE
        '''
        JSON_FILE[self.image_key]['regions'][self.region_key]['region_attributes']['subjectid'] = str(
            self.subjectid)
        JSON_FILE[self.image_key]['regions'][self.region_key]['region_attributes']['species'] = self.species
        JSON_FILE[self.image_key]['regions'][self.region_key]['region_attributes']['part'] = self.part

# region Save and Load the file


def load_json(vgg_file, fixkeys=True, backup=True):
    '''(str)->void
    Load the VGG JSON file into the module variable _JSON_FILE
    '''
    pth = path.normpath(vgg_file)
    global JSON_FILE
    global _JSON_FILE_NAME
    with open(pth) as data_file:
        JSON_FILE = json.load(data_file)
    _JSON_FILE_NAME = pth
    if fixkeys:
        fix_keys(backup)


def save_json(backup=True):
    '''->void
    called after we have fixed the keys in the JSON file
    to reflect any changes in image filesize
    caused by changing tags

    If backup then the file is backed up before writing out
    the in memory JSON file
    '''
    filepath, filename, ext = get_file_parts(_JSON_FILE_NAME)
    if backup:
        bk = path.join(filepath, filename + datetime_stamp() + ext + '.bak')
        copy(_JSON_FILE_NAME, bk)
        s = '\nCreated backup of VGG file %s' % bk
        _prints(s)
        logging.info(s)
    with open(_JSON_FILE_NAME, 'w') as outfile:
        json.dump(JSON_FILE, outfile)
    s = '\nSaved VGG JSON file %s' % _JSON_FILE_NAME
    _prints(s)
    logging.info(s)
# endregion
