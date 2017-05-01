# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument, dangerous-default-value
'''simple image file generators'''
from os import path

import cv2
import numpy as np

from funclib.iolib import file_list_generator1
from funclib.iolib import file_list_glob_generator as flgg
from funclib.iolib import get_file_parts2
from funclib.iolib import folder_generator

import opencvlib.imgpipes.vgg as vgg
import opencvlib.imgpipes.digikamlib as digikamlib
from opencvlib import ImageInfo
from opencvlib.roi import roi_polygons_get
from opencvlib import fixp
from  opencvlib import getimg

__all__ = ['image_generator', 'IMAGE_EXTENSIONS',
           'IMAGE_EXTENSIONS_AS_WILDCARDS']

#hard coded vgg file which needs to be in each directory
VGG_FILE = 'vgg.json'

# region module consts and variables
IMAGE_EXTENSIONS = ('.bmp',
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.tif',
                    '.tiff',
                    '.pbm',
                    '.pgm',
                    '.ppm')

IMAGE_EXTENSIONS_AS_WILDCARDS = ('*.bmp',
                                 '*.jpg',
                                 '*.jpeg',
                                 '*.png',
                                 '*.tif',
                                 '*.tiff',
                                 '*.pbm',
                                 '*.pgm',
                                 '*.ppm')


def image_generator(paths, wildcards=IMAGE_EXTENSIONS_AS_WILDCARDS, flags=-1):
    '''(iterable, iterable)->ndarray (an image)
    Globs through every file in paths matching wildcards returning
    the image as an ndarray

    paths: List of paths
    wildcards: List of wildcards. eg ['*.bmp', '*.gif']

    Flags:
    <0 - Loads as is, with alpha channel if present)
    0 - Force grayscale
    >0 - 3 channel color iage (stripping alpha if present
    http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html#Mat%20imread(const%20String&%20filename,%20int%20flags)
    '''

    for images in file_list_generator1(paths, wildcards):
        if flags is None:
            yield cv2.imread(images)
        else:
            yield cv2.imread(images, flags)

class VGGSearchParams():
    '''VGGSearchParams
    '''
    def __init_(parts, species):
        '''(list|str, list|str)
        parts are region names, such as head or whole
        '''
        if isinstance(parts,str):
            parts = [parts]

        if isinstance(species,str):
            species = [species]

        self._parts = vgg.valid_parts_in_list(parts)
        self._species = vgg.valid_parts_in_list(species)

    @property
    def parts(self):
        '''regions getter'''
        return self._parts
    @parts.setter
    def parts(self, parts):
        '''regions setter'''
        self._parts = vgg.valid_parts_in_list(parts)


    @property
    def species(self):
        '''species getter'''
        return self._species
    @species.setter
    def species(self, species):
        '''species setter'''
        self._species = vgg.valid_species_in_list(species)


class DigikamSearchParams():
    '''digikam search params'''
    def __init__(self, filename='', album_label='', relative_path='', key_value_bool_type='AND',  **keyvaluetags):
        self.filename=filename
        self.album_label=album_label
        self.relative_path = relative_path
        self.key_value_bool_type = key_value_bool_type
        self.keyvaluetags = keyvaluetags


class Images():
    '''
    Images
    '''
    dkImages = None
    def __init__(self, search_folders, digikam_params, vgg_params, min_res_wh=(None,None), max_res_wh=(None,None), valid_extensions=IMAGE_EXTENSIONS, recurse_search_folders=False):
        '''(iterable,DigikamSearchParams, VGGSearchParams, bool)->yields ndarray
        search_folders - folders to search for valid image
        folders must have a vgg.json file in them, otherwise they will be ignored
        recurse_search_folders: recurse through all search_folders' children

        Note:To work, init_db must be called to open a class global
        connection to the digikam database
        '''
        self.search_folders=search_folders
        self.recurse=recurse
        self._digikam_params = digikam_params
        self._vgg_params = vgg_params
        self.extensions=valid_extensions
        self.max_res_wh = max_res_wh
        self.min_res_wh = min_res_wh
        assert isinstance(digikam_params, DigikamSearchParams)
        assert isinstance(vgg_params, VGGSearchParams)


    @property
    def digikamParams(self):
        '''digikamParams getter'''
        return self._digikam_params
    @digikamParams.setter
    def digikamParams(self, digikamParams):
        '''digikamParams setter'''
        self._digikam_params = digikamParams

    @property
    def vggParams(self):
        '''vggParams getter'''
        return self._vgg_params
    @vggParams.setter
    def vggParams(self, vggParams):
        '''vggParams setter'''
        self._vgg_params = vggParams


    def init_db(dbpath):
        #need to load the digikam db first, set is as class global
        Images.dkImages = digikamlib.ImagePaths(dbpath)

    def _get_digikam_image_list(self, digikam_search_param):
        '''(DigikamSearchParams)->list
        returns list of digikam images which match specified criteria

        Note that Images.dkImages must be set by calling init_db
        '''
        assert isinstance(digikam_search_param,DigikamSearchParams)
        assert Images.dkImages is not None
        imgs = Images.dkImages.images_by_tags(
            filename = digikam_search_param.filename,
            album_label = digikam_search_param.album_label,
            relative_path = digikam_search_param.relative_path,
            bool_type = digikam_search_param.key_value_bool_type,
            **digikam_search_param.keyvaluetags
            )
        imgs_out = [fixp(i) for i in imgs]
        return imgs_out

    def generate_images(self):
        '''(void)->ndarray,str
        generate whole images applying only the digikam filter
        Yields:
        image region (ndarray), full image path (eg c:\images\myimage.jpg)
        '''
        dk_image_list = _get_digikam_image_list(self._digikam_params)
        for img in dk_image_list:
            if ImageInfo.is_lower_res(img.filepath,*self.min_res_wh):
                continue

            if ImageInfo.is_higher_res(img.filepath,*self.max_res_wh):
                continue

            if not valid_extension is None:
                if not valid_extensions=='':
                    if not img.fileext in extensions:
                        continue

            yield getimg(img), img


    def generate_regions(self):
        '''(bool)-> ndarray,str,str,str

        Note that this uses the filters set in the VGGFilter and DigikamSearchParams
        Yields:
        image region (ndarray), species (eg bass), part (eg head, whole), full image path (eg c:\images\myimage.jpg)
        '''
        dk_image_list = _get_digikam_image_list(self._digikam_params)

        if recurse_search_folders:
            for fld in folder_generator(search_folders):
                if _fld_has_vgg():
                    vgg.load_json(fixp(path.join(pth,VGG_FILE)))
                    for img in vgg.imagesGenerator():

                        if not img.filepath in dk_image_list: #effectively applying a filter for the digikamlib conditions
                            continue

                        if ImageInfo.is_lower_res(img.filepath,*self.min_res_wh):
                            continue

                        if ImageInfo.is_higher_res(img.filepath,*self.max_res_wh):
                            continue

                        if not valid_extension is None:
                            if not valid_extensions=='':
                                if not img.fileext in extensions:
                                    continue

                        for spp in vgg_params.species:
                            for subject in img.subjects_generator(spp):
                                assert isinstance(subject, vgg.Subject)
                                for part in vgg_params.parts: #try all parts, eg whole, head
                                    for region in subject.regions_generator(part):
                                        assert isinstance(region, vgg.Region)
                                        white, ma, cropped_image = roi_polygons_get(img.filepath, region.all_points)
                                        yield cropped_image, spp, part, img.filepath
        else:
            for fld in search_folders:
                if _fld_has_vgg():
                    vgg.load_json(fixp(path.join(pth,VGG_FILE)))
                    for img in vgg.imagesGenerator():

                        if not img.filepath in dk_image_list: #effectively applying a filter for the digikamlib conditions
                            continue

                        if ImageInfo.is_lower_res(img.filepath,*self.min_res_wh):
                            continue

                        if ImageInfo.is_higher_res(img.filepath,*self.max_res_wh):
                            continue

                        if not valid_extension is None:
                            if not valid_extensions=='':
                                if not img.fileext in extensions:
                                    continue

                        for spp in vgg_params.species:
                            for subject in img.subjects_generator(spp):
                                assert isinstance(subject, vgg.Subject)
                                for part in vgg_params.parts: #try all parts, eg whole, head
                                    for region in subject.regions_generator(part):
                                        assert isinstance(region, vgg.Region)
                                        white, ma, cropped_image = roi_polygons_get(img.filepath, region.all_points)
                                        yield cropped_image, spp, part, img.filepath


def _fld_has_vgg(fld):
    fld = path.join(path.normpath(fld), VGG_FILE)
    return path.isfile(fld)