# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''handles getting additional region data generated from vgg jason files
http://www.robots.ox.ac.uk/~vgg/software/via/
'''

import os.path as path
import json

from funclib.iolib import get_file_parts

_JSON_FILE = []

class Image(object):
    def __init__(self, filepath='', size_in_bytes=0):
        '''(str)
        optionally provide a filepath - ie a path including the file name
        '''
        self.load(filepath, size_in_bytes)

    def _get_key(self):
        '''generate unique key for image file'''
        return self.filename + str(self.size_in_bytes) #key used by VGG is the filename.jpg<size in bytes>, so 123.jpg, which was 10k would br 123.jpg10000

    def load(self, filepath='', size_in_bytes=0):
        '''(str,int)->void
        try loading image data from JSON file, key is unique per image
        '''
        self.filepath = filepath
        self.size_in_bytes = size_in_bytes
        self.key = ''
        self.filename = ''
        self.fileext = ''
        self.filefolder = ''

        if filepath != '':
            self.filefolder, self.filename, self.fileext = get_file_parts(path.abspath(path.normpath(self.filepath)))
            self.filename = self.filename + self.fileext
            self.key = self._get_key

    def subjects_generator(self, species):
        '''(str)->Subject
        identify subject of given species'''
        subjectids = []
        for region in _JSON_FILE[self.key]['regions']:
            if region['region_attributes']['species'].casefold() == species.casefold():
                subjectid = region['region_attributes']['subjectid']
                if not subjectid in subjectids:
                    subjectids.append(subjectid)
                    sbj = _Subject(species, subjectid)
                    yield sbj

class _Subject(object):
    '''really a fish object, has many regions
    Should not be accessed directly.
    Iterate through the Images class subjects_generator.
    '''
    def __init__(self, key, subjectid=None):
        '''(str, str)
        Key is the unique key for the image,
        subjectid is set as an integer to uniquely identify a subject
        '''
        self.key = key
        self.subjectid = subjectid
        self.region_ids = set([])
        set_regions()

    def set_regions(self):
        '''
        Checks all regions defined on the image, regions which
        are defined on the same Object/Subject have their region key
        saved to region_ids for access later
        '''
        for key, region in iterate( _JSON_FILE[self.key]['regions']):
            if region['region_attributes']['subjectid'] == self.subjectid:
                self.region_ids.add(key)

    def regions_generator(self, part=''):
        '''(str)->Yields Region classes
        Yields regions for the given subject in the photo
        (identifed by its subjectid) which is unique within image only.

        If part == '', yields all parts associated with the object/subject
        Otherwise only yields the part specified (e.g., head or whole)
        '''
        for region_key in self.region_ids:
            shape_attr = _JSON_FILE[self.key]['regions'][region_key]['shape_attributes']
            region_attr = _JSON_FILE[self.key]['regions'][region_key]['region_attributes']
            reg = _Region(
                part = region_attr['part'],
                shape = shape_attr.get('shape'),
                x = shape_attr.get('x'),
                y = shape_attr.get('y'),
                r = shape_attr.get('r'),
                w = shape_attr.get('w'),
                h = shape_attr.get('h'),
                all_points_x = shape_attr.get('all_points_x'),
                all_points_y = shape_attr.get('all_points_y')
                )
            if part == '' or part.casefold() == region_attr['part'].casefold():
                yield reg


class _Region(object):
    def __init__(self, **kwargs):
        '''supported kwargs
        name= [circle | polygon | rect]
        object_part = [head, whole]

        circle: x,y,r
        rect: x,y,w,h
        polygon: [all_points_x], [all_points_y]  [10,20,50], [30,50, 100]

        values set to None if not read
        '''
        self.shape = kwargs.get('shape')
        self.species = kwargs.get('species')
        self.r = kwargs.get('r')
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')
        self.w = kwargs.get('w')
        self.h = kwargs.get('h')
        self.all_points_x = kwargs.get('all_points_x')
        self.all_points_y = kwargs.get('all_points_y')
        self.part = kwargs.get('part')


def load(vgg_file):
    '''(str)->void
    Load the VGG JSON file into the module variable _JSON_FILE
    '''
    with open(path.normpath(vgg_file)) as data_file:
        _JSON_FILE = json.load(data_file)
