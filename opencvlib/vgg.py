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
import argparse
import sys
from shutil import copy
from math import pi

from funclib.stringslib import datetime_stamp
from funclib.iolib import get_file_parts
from funclib.baselib import dictp

from opencvlib.common import rect_as_points
from opencvlib.common import poly_area

silent = False
_JSON_FILE_NAME = ''
_JSON_FILE = []
_LOG_FILE_NAME = 'vgg.py.' + datetime_stamp() + '.log'

_VALID_SHAPES_ALL = ['', 'polygon', 'rect', 'circle', 'ellipse', 'point']
_VALID_SHAPES_2D = ['polygon', 'rect', 'circle', 'ellipse']

_VALID_PARTS = ['', 'whole', 'head']
_VALID_SPECIES = ['bass',
    'dab',
    'mackerel',
    'flounder',
    'dogfish',
    'plaice',
    'gurnard grey',
    'flatfish',
    'cod']

def _prints(s):
    if not silent:
        print(s)

logging.basicConfig(format='%(asctime)s %(message)s',
    filename=_LOG_FILE_NAME,
    filemode='w',
    level=logging.DEBUG)

_prints('Logging to %s' % _LOG_FILE_NAME)


def _fix_keys():
    '''loop through json file and correct file sizes
    '''
    for key in _JSON_FILE:
        # relies on VGG JSON file being in same dir as files
        filepath = get_file_parts(_JSON_FILE_NAME)[0]
        filename = _JSON_FILE[key]['filename']
        fullname = path.join(filepath, filename)
        size_in_bytes = path.getsize(fullname)
        newkey = filename + str(size_in_bytes)
        _JSON_FILE[newkey] = _JSON_FILE.pop(key)
    save_json()


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
        Returns None if no image file does not exist
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
            self.filefolder, self.filename, self.fileext = get_file_parts(path.abspath(path.normpath(self.filepath)))
            self.filename = self.filename + self.fileext
            self.key = self._get_key()

    def subjects_generator(self, species):
        '''(str)->Subject
        identify subject of given species'''
        subjectids = []

        if species not in _VALID_SPECIES:
            raise ValueError('Invalid species ' + species)

        d = dictp(_JSON_FILE)
        regions = d[self.key]['regions']

        if regions:
            assert isinstance(regions, dict)
            for region in regions.values():
                if region['region_attributes']['species'].casefold() == species.casefold():
                    subjectid = region['region_attributes']['subjectid']
                    if subjectid not in subjectids:
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

        d = dictp(_JSON_FILE)
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
        if part not in _VALID_PARTS:
            raise ValueError('Invalid image region type (part) ' + part)

        if shape not in _VALID_SHAPES_ALL:
            raise ValueError('Invalid shape ' + part)

        d = dictp(_JSON_FILE)
        regions = d[self.key]['regions']

        # region_ids is the ids of all regions which share a common
        # region_attributes['subjectid']
        for region_key in self.region_ids:
            shape_attr = regions[region_key]['shape_attributes']
            region_attr = regions[region_key]['region_attributes']
            if shape_attr:
                reg = _Region(part=region_attr.get('part', 'whole'),
                              image_key=self.key,  # no get, error if doesnt exist
                              has_attrs=True if region_attr else False,
                              region_key=region_key,  # no get, error if doesnt exist
                              species=region_attr.get('species'),
                              subjectid=region_attr.get('subjectid'),
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
        elif self.shape == 'point':
            self.all_points = [(self.x, self.y)]
        elif self.shape == 'rect':
            self.all_points = rect_as_points(self.y, self.x, self.h, self.w)
            self.area = poly_area(pts=self.all_points)
        elif self.shape == 'circle':
            self.area = pi * self.r ** 2
        elif self.shape == 'ellipse':
            self.area = pi * self.rx * self.ry

    def write(self):
        '''->void
        write the region to the in memory json file _JSON_FILE
        '''
        _JSON_FILE[self.image_key]['regions'][self.region_key]['region_attributes']['subjectid'] = str(self.subjectid)
        _JSON_FILE[self.image_key]['regions'][self.region_key]['region_attributes']['species'] = self.species
        _JSON_FILE[self.image_key]['regions'][self.region_key]['region_attributes']['part'] = self.part

# region Save and Load the file
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
        s = 'Created backup of VGG file %s' % bk
        _prints(s)
        logging.info(s)
    with open(_JSON_FILE_NAME, 'w') as outfile:
        json.dump(_JSON_FILE, outfile)
    s = 'Saved VGG JSON file %s' % _JSON_FILE_NAME
    _prints(s)
    logging.info(s)
# endregion
def write_region_attributes(species, backup=True):
    '''(str)->void
    Species is the species name to write to the VGG file.

    Will write the region tags:
    species=bass, subjectid=1, part=head|tail
    Decides to write head/tail based on the shape area.

    Only works if there is a single subject (fish) with shapes.

    This is purely a fix to save manual entry.

    *Note, load_json needs to be called fits.
    '''
    max_area = 0
    max_region_key = None
    region_cnt = 0
    region_shape_cnt = 0
    dobreak = False
    dosave = False

    if not _JSON_FILE:
        raise ValueError('No VGG JSON file loaded. Call load_json first')

    # first pass to get some stats
    for key in _JSON_FILE:
        subj = _Subject(key)
        for region in subj.regions_generator():
            assert isinstance(region, _Region)
            if region.has_attrs:
                dobreak = True
                break

            region_cnt += 1
            region_shape_cnt = region_shape_cnt + \
                (1 if region.shape in _VALID_SHAPES_2D else 0)
            if region.area > max_area:
                max_area = region.area
                max_region_key = region.region_key

        if dobreak:  # move to next image if there is not two shapes
            dobreak = False
            break

        if region_cnt == 2 and region_cnt == region_shape_cnt:
            for region in subj.regions_generator():
                if not region.has_attrs:
                    region.species = species
                    region.subjectid = 1
                    region.part = ('whole' if region.region_key == max_region_key else 'head')
                    region.write()
                    s = 'Updated regions in %s, part: %s' % (key, region.part)
                    logging.info(s)
                    _prints(s)
                    dosave = True

    if dosave:
        save_json(backup)



#need to import argparse

#if _CMDLINEARGS.foo == 'THE FOO ARG':
    #do stuff

#if _CMDLINEARGS.bar == 'WAS_EMPTY':
    #do stuff if no bar argument was passed

def main():
    '''main entry if run from commandline
    '''
    cmdline = argparse.ArgumentParser(description='Routines related to VGG files')
    cmdline.add_argument('file', help='VGG JSON file to manipulate') #position argument
    cmdline.add_argument('-r', '--region', help='Write region attributes to the specified file, species can be specified', required=False, action='store_true') #specied value argument
    cmdline.add_argument('-f', '--fix_keys', help='Fix the keys in specied file to account for file size changes', required=False, action='store_true')
    cmdline.add_argument('-s', '--species', help='Specify species where this is used', required=False, default='') #present or absent test
    args = cmdline.parse_args()

    spp = args.species

    global silent
    silent = True

    load_json(path.normpath(args.file))
    if args.region:
        if spp == '': spp = 'bass'
        print("\nUpdating regions, assuming subject is %s....\n" % spp)
        write_region_attributes(spp)

    if args.fix_keys:
        print("\nFixing keys with new file sizes....\n")
        _fix_keys()

if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
