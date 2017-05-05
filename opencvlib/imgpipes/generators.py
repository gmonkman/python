# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, dangerous-default-value, attribute-defined-outside-init, return-in-init
'''simple image file generators'''
from os import path as _path

import cv2 as _cv2
import numpy as _np
from numpy.random import randint as _randint

import funclib.baselib as _baselib
import funclib.iolib as _iolib

from opencvlib import ImageInfo as _ImageInfo
from opencvlib import getimg as _getimg

from opencvlib.distance import nearN_euclidean as _nearN_euclidean

import opencvlib.imgpipes.vgg as _vgg
import opencvlib.imgpipes.digikamlib as _digikamlib
from opencvlib.imgpipes import config as _config

from opencvlib.roi import roi_polygons_get as _roi_polygons_get
from opencvlib.roi import sample_rect as _sample_rect


from opencvlib import IMAGE_EXTENSIONS_AS_WILDCARDS as _IMAGE_EXTENSIONS_AS_WILDCARDS
from opencvlib import IMAGE_EXTENSIONS as _IMAGE_EXTENSIONS

__all__ = ['image_generator', 'Images', 'DigikamSearchParams', 'VGGSearchParams']

# hard coded vgg file which needs to be in each directory
VGG_FILE = 'vgg.json'


def image_generator(paths, wildcards=_IMAGE_EXTENSIONS_AS_WILDCARDS, flags=-1):
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

    for images in _iolib.file_list_generator1(paths, wildcards):
        if flags is None:
            yield _cv2.imread(images)
        else:
            yield _cv2.imread(images, flags)

# region Main Region and Image Generator


class VGGSearchParams(object):
    '''VGGSearchParams
    '''
    def __init__(self, folders, parts, species, recurse=False):
        '''(list|str, list|str, list|str, bool)
        folders: paths to folders containing vgg.json regions file and associated images
        parts: region name tags, such as head or whole
        species: species
        recurse: recurse down directories in folders. Only folders with a vgg.json are relevant
        '''
        if isinstance(parts, str):
            parts = [parts]

        if isinstance(species, str):
            species = [species]

        if isinstance(folders, str):
            folders = [folders]

        self._parts = _vgg.valid_parts_in_list(parts)
        self._species = _vgg.valid_species_in_list(species)
        self._folders = folders
        self.recurse = recurse

    @property
    def parts(self):
        '''regions getter'''
        return self._parts

    @parts.setter
    def parts(self, parts):
        '''regions setter'''
        self._parts = _vgg.valid_parts_in_list(parts)

    @property
    def species(self):
        '''species getter'''
        return self._species

    @species.setter
    def species(self, species):
        '''species setter'''
        self._species = _vgg.valid_species_in_list(species)

    @property
    def folders(self):
        '''folders getter'''
        return self._folders
    @folders.setter
    def folders(self, folders):
        '''folders setter'''
        self._folders = [folders] if isinstance(folders, str) else folders


class DigikamSearchParams():
    '''digikam search params'''

    def __init__(self, filename='', album_label='', relative_path='', key_value_bool_type='AND', **keyvaluetags):
        self.filename = filename
        self.album_label = album_label
        self.relative_path = relative_path
        self.key_value_bool_type = key_value_bool_type
        self.keyvaluetags = keyvaluetags

    def no_filters(self):
        '''()->bool
        returns true if no filters set
        '''
        return self.filename == '' and self.album_label == '' and self.relative_path == '' and not self.keyvaluetags


class Images(object):
    '''
    Images
    '''
    dkImages = None

    def __init__(self, digikam_params, vgg_params, min_res_wh=(None, None), max_res_wh=(None, None), valid_extensions=_IMAGE_EXTENSIONS):
        '''(DigikamSearchParams, VGGSearchParams, bool)->yields ndarray
        folders must have a vgg.json file in them, otherwise they will be ignored

        Note:To work, init_db must be called to open a class global
        connection to the digikam database
        '''
        self.silent = False
        self._digikam_params = digikam_params
        self._vgg_params = vgg_params
        self.valid_extensions = valid_extensions
        self.max_res_wh = max_res_wh
        self.min_res_wh = min_res_wh
        self._dirty_filters = True
        Images._initdb()

    def _no_digikam_filters(self):
        '''()->bool
        Return bool indicating if
        there are any digikam filters set
        '''
        if self._digikam_params is None:
            return True
        else:
            return self._digikam_params.no_filters()

    @property
    def digikamParams(self):
        '''digikamParams getter'''
        return self._digikam_params

    @digikamParams.setter
    def digikamParams(self, digikamParams):
        '''digikamParams setter'''
        self._digikam_params = digikamParams
        self.dirty_filters = True #for use in inherited classes, not needed for this explicitly

    @property
    def vggParams(self):
        '''vggParams getter'''
        return self._vgg_params

    @vggParams.setter
    def vggParams(self, vggParams):
        '''vggParams setter'''
        self._vgg_params = vggParams
        self.dirty_filters = True #for use in inherited classes, not needed for this explicitly

    @staticmethod
    def _initdb():
        '''(void)->void
        load the digikam database configured in imgpipes/config.cfg
        '''
        # need to load the digikam db first, set is as class global
        Images.dkImages = _digikamlib.ImagePaths(_config.digikamdb)

    def _get_digikam_image_list(self, digikam_search_param):
        '''(DigikamSearchParams)->list
        returns list of digikam images which match specified criteria

        Note that Images.dkImages must be set by calling init_db
        '''
        if self._no_digikam_filters():
            return None

        assert isinstance(digikam_search_param, DigikamSearchParams)
        assert Images.dkImages is not None
        imgs = Images.dkImages.images_by_tags(
            filename=digikam_search_param.filename,
            album_label=digikam_search_param.album_label,
            relative_path=digikam_search_param.relative_path,
            bool_type=digikam_search_param.key_value_bool_type,
            **digikam_search_param.keyvaluetags
        )
        imgs_out = [_iolib.fixp(i) for i in imgs]
        return imgs_out

    def digikam_generator(self, yield_path_only=False):
        '''(bool)->ndarray,str
        generate whole images applying only the digikam filter
        Yields:
        image region (ndarray), full image path (eg c:/images/myimage.jpg)

        If yeild_path_only, then the yielded ndarray will be none.
        '''
        if self._no_digikam_filters():
            return

        dk_image_list = self._get_digikam_image_list(self._digikam_params)
        for img in dk_image_list:
            if _ImageInfo.is_lower_res(img, *self.min_res_wh):
                continue

            if _ImageInfo.is_higher_res(img, *self.max_res_wh):
                continue

            if not self.valid_extensions is None:
                if self.valid_extensions != '':
                    if not _iolib.hasext(img, self.valid_extensions):
                        continue

            if yield_path_only:
                yield None, img
            else:
                yield _getimg(img), img

    def generate_regions(self):
        '''(bool)-> ndarray,str,str,str

        Note that this uses the filters set in the VGGFilter and DigikamSearchParams
        Yields:
        image region (ndarray), species (eg bass), part (eg head, whole), full image path (eg c:/images/myimage.jpg)

        '''
        dk_image_list = self._get_digikam_image_list(self._digikam_params)

        if self.vggParams.recurse:
            for fld in _iolib.folder_generator(self.vggParams.folders):
                if _dir_has_vgg(fld):

                    p = _iolib.fixp(_path.join(fld, VGG_FILE))
                    _vgg.load_json(p)
                    if not self.silent:
                        print('Opened regions file %s' % p)

                    for Img in _vgg.imagesGenerator():

                        if not self._no_digikam_filters(): #if no filters set for digikam, just ignore it
                            if not Img.filepath in dk_image_list:  # effectively applying a filter for the digikamlib conditions
                                continue

                        if _ImageInfo.is_lower_res(Img.filepath, *self.min_res_wh):
                            continue

                        if _ImageInfo.is_higher_res(Img.filepath, *self.max_res_wh):
                            continue

                        if not self.valid_extensions is None:
                            if self.valid_extensions != '':
                                if not Img.fileext in self.valid_extensions:
                                    continue

                        for spp in self.vggParams.species:
                            for subject in Img.subjects_generator(spp):
                                assert isinstance(subject, _vgg.Subject)
                                for part in self.vggParams.parts:  # try all parts, eg whole, head
                                    for region in subject.regions_generator(part):
                                        assert isinstance(region, _vgg.Region)
                                        cropped_image = _roi_polygons_get(Img.filepath, region.all_points)[3] #3 is the image cropped to a rectangle, with black outside the region
                                        yield cropped_image, spp, part, Img.filepath
        else:
            for fld in self.vggParams.folders:
                if _dir_has_vgg(fld):
                    _vgg.load_json(_iolib.fixp(_path.join(fld, VGG_FILE)))

                    p = _iolib.fixp(_path.join(fld, VGG_FILE))
                    _vgg.load_json(p)
                    if not self.silent:
                        print('Opened regions file %s' % p)

                    for Img in _vgg.imagesGenerator():

                        if not self._no_digikam_filters(): #if no filters set for digikam, just ignore it
                            if not Img.filepath in dk_image_list:  # effectively applying a filter for the digikamlib conditions
                                continue

                        if _ImageInfo.is_lower_res(Img.filepath, *self.min_res_wh):
                            continue

                        if _ImageInfo.is_higher_res(Img.filepath, *self.max_res_wh):
                            continue

                        if not self.valid_extensions is None:
                            if self.valid_extensions != '':
                                if not Img.fileext in self.valid_extensions:
                                    continue

                        for spp in self.vggParams.species:
                            for subject in Img.subjects_generator(spp):
                                assert isinstance(subject, _vgg.Subject)
                                for part in self.vggParams.parts:  # try all parts, eg whole, head
                                    for region in subject.regions_generator(part):
                                        assert isinstance(region, _vgg.Region)
                                        cropped_image = _roi_polygons_get(Img.filepath, region.all_points)[3] #3 is the image cropped to a rectangle, with black outside the region
                                        yield cropped_image, spp, part, Img.filepath



def _dir_has_vgg(fld):
    fld = _path.join(_path.normpath(fld), VGG_FILE)
    return _path.isfile(fld)
# endregion


#TODO Debug This
class RandomRegions(Images):
    '''get random regions from the digikam library based on search criteria
    which are first set in the DigikamSearchParams class.
    '''
    def __init__(self, digikam_params, vgg_params=None, min_res_wh=(None, None), max_res_wh=(None, None), valid_extensions=_IMAGE_EXTENSIONS):
        #resolutions is a dictionary of dictionaries {'c:\pic.jpg':{'w':1024, 'h':768}}

        #Code relies on d_res and pt_res having same indices
        #All points are w,h
        self.d_res = _baselib.odict() #ordered dictionary (collections.OrderedDict) of resolutions
        self.pt_res = [] #resolutions as a list of points
        return super().__init__(digikam_params, None, min_res_wh, max_res_wh, valid_extensions)


    def generate_regions(self):
        '''DO NOT USE. Only allow the digikam generator
        as makes no sense to sample from a region'''
        raise AttributeError("'RandomRegions' object has no attribute 'generate_regions'")


    def digikam_region(self, img, region_w, region_h, sample_size=1):
        '''(ndarray|str|tuple, int, int, int)->ndarray,str
        Retrieve a random image region sampled from the digikam library
        nearest in resolution to the passed in image.

        img:Original image to get resolution. This can be an ndarray, path (c:/pic.jpg) or list like point (w, h)

        region_w, region_h:Size of region to sample from similiar resolution image

        sample_size:Randomly sample an image from the sample_size nearest in resolution from the digikam library

        Returns an image (ndarray) and the image path
        '''
        if self._no_digikam_filters():
            raise ValueError('No digikam filters set. '
                             'Create a class instance of generators.DigikamSearchParams and '
                             'pass to RandomRegions.digikamParams property, or set at creation')

        self._loadres() #refresh if needed
        if isinstance(img, _np.ndarray):
            h = img.shape[0]
            w = img.shape[1]
        elif isinstance(img, list) or isinstance(img, tuple):
            w = img[0]
            h = img[1]
        else:
            w, h = _ImageInfo.resolution(img)

        #Now get a random sample image of about closest resolution
        samples = _nearN_euclidean((w, h), self.pt_res, sample_size)
        samples = [self.d_res.getbyindex(ind) for ind, dist in samples]

        counter = 0 #counter to break out if we are stuck in the loop
        while True:
            samp_path = samples[_randint(0, len(samples))]
            sample_image = _getimg(samp_path)[0]
            if region_w <= samp_path[1][0] or region_h <= samp_path[1][1]:
                imgout = _sample_rect(sample_image, region_w, region_h)
                break
            elif len(samples) > 1: #image too small to get region sample, delete it and try again
                samples.remove(samp_path)
            elif counter > 20: #lets not get in an infinite loop
                imgout = sample_image
                break
            else: #Last one, just use it
                imgout = sample_image
                break
            counter += 1

        if imgout is None: #catch all
            imgout = sample_image

        return imgout, samp_path[0]


    @staticmethod
    def _gen_res_key(w, h):
        '''(int,int)->str
        generate unique resolution key
        '''
        return str(w) + 'x' + str(h)


    def _loadres(self, force=False):
        '''loads resolutions with full image paths
        '''
        if not force and not self._dirty_filters:
            return

        self.d_res = _baselib.odict()
        self.pt_res = []
        if self._no_digikam_filters():
            return

        for dummy, img_path in self.digikam_generator(True):
            w, h = _ImageInfo.resolution(img_path) #use the pil lazy loader
            self.d_res[img_path] = (w, h) #ordered dict, matching order of pts, order is critical for getting random image
            self.pt_res.append([w, h])
