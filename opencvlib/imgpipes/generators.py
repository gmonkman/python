# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, dangerous-default-value, attribute-defined-outside-init, return-in-init, unnecessary-pass, arguments-differ
'''simple image file generators.

All yielded generators have an error handler wrapping which logs errors
to prevent stop failures during big processing tasks

The RandomRegion generator returns None on err'''

from os import path as _path
import abc as _abc


import cv2 as _cv2
import numpy as _np
from numpy.random import randint as _randint


import funclib.baselib as _baselib
import funclib.iolib as _iolib

import opencvlib.decs as _decs
from opencvlib import ImageInfo as _ImageInfo
from opencvlib import getimg as _getimg

from opencvlib.distance import nearN_euclidean as _nearN_euclidean

import opencvlib.imgpipes.vgg as _vgg
import opencvlib.imgpipes.digikamlib as _digikamlib
import opencvlib.imgpipes.filters as _filters
from opencvlib.imgpipes import config as _config

from opencvlib.roi import roi_polygons_get as _roi_polygons_get
from opencvlib.roi import sample_rect as _sample_rect
from opencvlib.roi import get_image_from_mask as _get_image_from_mask

import opencvlib.transforms as _transforms
from opencvlib import Log as _log

from opencvlib import IMAGE_EXTENSIONS_AS_WILDCARDS as _IMAGE_EXTENSIONS_AS_WILDCARDS

#__all__ = ['image_generator', 'Images', 'DigikamSearchParams', 'VGGSearchParams']

# hard coded vgg file which needs to be in each directory
VGG_FILE = 'vgg.json'


#region Generator related classes
class _BaseGenerator(_abc.ABC):
    '''abstract class for all these generator functions
    '''
    @_abc.abstractmethod
    def generate(self):
        '''placeholder'''
        pass


class _Generator(_BaseGenerator):
    '''base generator class
    Use with BaseGenerator to create new generators

    Pops transforms and filters.

    When instantiating classes which inherit Generator
    provide kwargs with
    transforms=Transforms (Transforms class - a collection of Transfor classes)
    filters=Filters (Filters class - a collection of Filter classes)
    '''
    def __init__(self, *args, **kwargs):
        self._transforms = kwargs.pop('transforms', None)
        if not isinstance(self._transforms, _transforms.Transforms) and not self._transforms is None:
            raise ValueError('Base generator class keyword argument "transforms" requires class type "transforms.Transforms"')

        self._filters = kwargs.pop('filters', None)
        if not isinstance(self._filters, _filters.Filters) and not self._filters is None:
            raise ValueError('Base generator class keyword argument "filters" requires class type "filters.Filters"')
       # assert isinstance(self._transforms, _transforms.Transforms)
       # assert isinstance(self._filters, _filters.Filters)


    @property
    def transforms(self):
        '''transforms getter'''
        return self._transforms
    @transforms.setter
    def transforms(self, transforms):
        '''transforms setter'''
        self._transforms = transforms


    @property
    def filters(self):
        '''filters getter'''
        return self._filters
    @filters.setter
    def filters(self, filters):
        '''filters setter'''
        self._filters = filters


    @_decs.decgetimgmethod
    def executeTransforms(self, img):
        '''(ndarray|str)->ndarray
        execute transforms enqueued in the Transforms class
        and return the transformed image
        '''
        #img = _getimg(img)
        if isinstance(self._transforms, _transforms.Transforms):
            try:
                img = self.transforms.validate(img)
            except ValueError as e:
                _log.exception(str(e))
        return img


    @_decs.decgetimgmethod
    def isimagevalid(self, img):
        '''does the image pass a filter
        '''
        #img = _getimg(img)
        assert isinstance(self.filters, _filters.Filters)
        return self.filters.validate(img)


    @_decs.decgetimgmethod
    def generate(self, img):
        '''(str|ndarray,cv2.imread flag..)->None|ndarray
        takes img, applies relvant filters and transforms
        and returns to calling generater to bubble up the
        transformed image

        Returns None if filter fails
        '''
        if self.isimagevalid(img):
            img = self.executeTransforms(img)
            return img
        else:
            return None
#endregion



#region Params VGG and Digikam Filter Classes
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

    @staticmethod
    def no_digikam_filters(dkparam):
        '''(DigikamSearchParams)->bool
        Return bool indicating if
        there are any digikam filters set
        in the passed DigikamSearchParams class instance
        '''
        if dkparam is None:
            return True
        else:
            return dkparam.no_filters()
#endregion



#region Generators
class DigiKam(_Generator):
    '''Generate images based on a digikam filter'''

    #load db in class context for efficiency
    dkImages = _digikamlib.ImagePaths(_config.digikamdb)

    def __init__(self, digikam_params, *args, **kwargs): #args and kwargs get passed back to the base class - supports filters and transforms
        #super call to base supports passing kawrgs for
        #transforms and filters
        self._digikam_params = digikam_params
        assert isinstance(self._digikam_params, DigikamSearchParams)
        self._dirty_filters = True
        self._image_list = None
        self._refresh_image_list()
        super().__init__(*args, **kwargs)


    @property
    def image_list(self):
        '''image_list getter'''
        return self._image_list


    @property
    def digikam_params(self):
        '''digikam_params getter'''
        return self._digikam_params
    @digikam_params.setter
    def digikam_params(self, digikam_params):
        '''digikam_params setter'''
        self._digikam_params = digikam_params
        self._dirty_filters = True
        self._refresh_image_list()


    def generate(self, yield_path_only=False, outflag=_cv2.IMREAD_UNCHANGED):
        '''(bool)->ndarray,str
        generate whole images applying only the digikam filter
        Yields:
        image region (ndarray), full image path (eg c:/images/myimage.jpg)

        If yeild_path_only, then the yielded ndarray will be none.

        Has an error handler which logs failures in the generator
        '''

        if self._digikam_params.no_filters() or not self.image_list:
            return None, None, {}

        for imgpath in self.image_list:
            try:
                if yield_path_only:
                    yield None, imgpath, {}
                else:
                    img = _getimg(imgpath, outflag)
                    img = super().generate(img) #Check filters an execute transforms
                    if isinstance(img, _np.ndarray):
                        yield img, imgpath, {}
            except Exception as dummy:
                s = 'Processing of %s failed.' % imgpath
                _log.exception(s)



    def _refresh_image_list(self, force=False):
        '''(bool)->list
        force:
            force reload of the image list even if filters are not dirty

        Loads list of digikam images according to the digikamsearch parameters
        '''

        if self.digikam_params.no_filters():
            self.image_list = []
            return None

        assert isinstance(self.digikam_params, DigikamSearchParams)
        assert DigiKam.dkImages is not None
        if force or self._dirty_filters:
            imgs = DigiKam.dkImages.images_by_tags(
                filename=self.digikam_params.filename,
                album_label=self.digikam_params.album_label,
                relative_path=self.digikam_params.relative_path,
                bool_type=self.digikam_params.key_value_bool_type,
                **self.digikam_params.keyvaluetags
            )
            self._image_list = [_iolib.fixp(i) for i in imgs]



class FromPaths(_Generator):
    '''Generate images from a list of folders
    Transforms can be added by instantiating Transform objects and
    adding them to Transforms
    '''
    def __init__(self, paths, wildcards=_IMAGE_EXTENSIONS_AS_WILDCARDS, *args, **kwargs):
        self._paths = paths
        self._wildcards = wildcards
        super().__init__(*args, **kwargs)


    @property
    def paths(self):
        '''paths getter'''
        return self._paths
    @paths.setter
    def paths(self, paths):
        '''paths setter'''
        self._paths = paths


    def generate(self, outflag=_cv2.IMREAD_UNCHANGED, pathonly=False, recurse=False):
        '''(cv2.imread option, bool, bool) -> ndarray, str, dict
        Globs through every file in paths matching wildcards returning
        the image as an ndarray

        recurse:
            Recurse through paths
        outflag:
            <0 - Loads as is, with alpha channel if present)
            0 - Force grayscale
            >0 - 3 channel color iage (stripping alpha if present
        pathonly:
            only generate image paths, the ndarray will be None
         '''

        for imgpath in _iolib.file_list_generator1(self._paths, self._wildcards, recurse=recurse):
            try:
                if pathonly:
                    yield None, imgpath, {}
                else:
                    img = _cv2.imread(imgpath, outflag)
                    img = super().generate(img) #delegate to base method to transform and filter (if specified)
                    if isinstance(img, _np.ndarray):
                        yield img, imgpath, {}
            except Exception as dummy:
                s = 'Processing of %s failed.' % imgpath
                _log.exception(s)



class VGGRegions(_Generator):
    '''Generate regions configured in VGG
    '''
    def __init__(self, digikam_params, vgg_params, *args, **kwargs):
        '''(DigikamSearchParams, VGGSearchParams, bool)->yields ndarray
        folders must have a vgg.json file in them, otherwise they will be ignored
        '''
        self.silent = False
        self._digikam_params = digikam_params
        self._vgg_params = vgg_params
        self._dirty_filters = True
        super().__init__(*args, **kwargs)

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


    def generate(self, pathonly=False, outflag=_cv2.IMREAD_UNCHANGED, *args, **kwargs):
        '''(bool)-> ndarray,str,str,str

        Note that this uses the filters set in the VGGFilter and DigikamSearchParams
        Yields:
        image region (ndarray), species (eg bass), part (eg head, whole), full image path (eg c:/images/myimage.jpg)

        outflag is a cv2.imread flag, determining the format of the returned image
        cv2.IMREAD_COLOR
        cv2.IMREAD_GRAYSCALE
        cv2.IMREAD_UNCHANGED

        Has an error handler which logs failures in the generator
        '''
        if DigikamSearchParams.no_digikam_filters(self.digikamParams):
            dk_image_list = []
        else:
            dkGen = DigiKam(self.digikamParams)
            dk_image_list = [i for unused_, i, dummy in dkGen.generate(yield_path_only=True)]

        if self.vggParams.recurse:
            for fld in _iolib.folder_generator(self.vggParams.folders):

                try:
                    if _dir_has_vgg(fld):

                        p = _iolib.fixp(_path.join(fld, VGG_FILE))
                        _vgg.load_json(p)
                        if not self.silent:
                            print('Opened regions file %s' % p)

                        for Img in _vgg.imagesGenerator():

                            if dk_image_list:
                                if not Img.filepath in dk_image_list:  # effectively applying a filter for the digikamlib conditions
                                    continue

                            for spp in self.vggParams.species:
                                for subject in Img.subjects_generator(spp):
                                    assert isinstance(subject, _vgg.Subject)
                                    for part in self.vggParams.parts:  # try all parts, eg whole, head
                                        for region in subject.regions_generator(part):
                                            assert isinstance(region, _vgg.Region)
                                            if pathonly:
                                                cropped_image = None
                                            else:
                                                i = _getimg(Img.filepath, outflag)
                                                i = super().generate(i)

                                                if isinstance(i, _np.ndarray):
                                                    mask, dummy, dummy1, cropped_image = _roi_polygons_get(i, region.all_points) #3 is the image cropped to a rectangle, with black outside the region
                                                else:
                                                    _log.warning('File %s was readable, but ignored because of a filter or failed image transformation. This can usually be ignored.')
                                                    cropped_image = None

                                                yield cropped_image, Img.filepath, {'species':spp, 'part':part, 'shape':region.shape, 'mask':mask, 'roi':region.all_points}

                except Exception as dummy:
                    s = 'Processing of file:%s failed.' % Img.filepath
                    _log.exception(s)

        else:
            for fld in self.vggParams.folders:

                try:
                    if _dir_has_vgg(fld):
                        p = _iolib.fixp(_path.join(fld, VGG_FILE))
                        _vgg.load_json(p)
                        if not self.silent:
                            print('Opened regions file %s' % p)

                        for Img in _vgg.imagesGenerator():

                            if dk_image_list:
                                if not Img.filepath in dk_image_list:  # effectively applying a filter for the digikamlib conditions
                                    continue

                            for spp in self.vggParams.species:
                                for subject in Img.subjects_generator(spp):
                                    assert isinstance(subject, _vgg.Subject)
                                    if pathonly:
                                        cropped_image = None
                                    else:
                                        i = _getimg(Img.filepath, outflag)
                                        i = super().generate(i)

                                        if isinstance(i, _np.ndarray):
                                            mask, dummy, dummy1, cropped_image = _roi_polygons_get(i, region.all_points) #3 is the image cropped to a rectangle, with black outside the region
                                        else:
                                            _log.warning('File %s was readable, but ignored because of a filter or failed image transformation. This can usually be ignored.')
                                            cropped_image = None

                                        yield cropped_image, Img.filepath, {'species':spp, 'part':part, 'shape':region.shape, 'mask':mask, 'roi':region.all_points}
                except Exception as dummy:
                    s = 'Processing of file:%s failed.' % Img.filepath
                    _log.exception(s)



class RandomRegions(DigiKam):
    '''get random regions from the digikam library based on search criteria
    which are first set in the DigikamSearchParams class.
    '''
    def __init__(self, digikam_params, *args, **kwargs):
        #resolutions is a dictionary of dictionaries {'c:\pic.jpg':{'w':1024, 'h':768}}

        #Code relies on d_res and pt_res having same indices
        #All points are w,h
        self.d_res = _baselib.odict() #ordered dictionary (collections.OrderedDict) of resolutions
        self.pt_res = [] #resolutions as a list of points
        super().__init__(digikam_params, *args, **kwargs)


    def generate(self, img, region_w, region_h, sample_size=10, mask=None, outflag=_cv2.IMREAD_UNCHANGED):
        '''(ndarray|str|tuple, int, int, int, ndarray, int)->ndarray|None, str, dict
        Retrieve a random image region sampled from the digikam library
        nearest in resolution to the passed in image.

        **NOT A GENERATOR, RETURNS A SINGLE IMAGE**

        img:
            Original image to get resolution. This can be an ndarray, path (c:/pic.jpg) or list like point (w, h)
        region_w, region_h:
            Size of region to sample from similiar resolution image
        sample_size:
            Randomly sample an image from the sample_size nearest in resolution from the digikam library
        mask:
            optional white mask to apply to the image
        outflag:
            cv2.imread flag, determining the format of the returned image
            cv2.IMREAD_COLOR
            cv2.IMREAD_GRAYSCALE
            cv2.IMREAD_UNCHANGED

        Returns an image (ndarray) and the image path.

        Can return None as image.

        No error handler
        '''
        imgout = None
        try:

            if self.digikam_params.no_filters():
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
                sample_image = _getimg(samp_path, outflag)[0]

                if self.isimagevalid(sample_image):
                    if region_w <= samp_path[1][0] and region_h <= samp_path[1][1]:
                        sample_image = self.executeTransforms(sample_image)
                        imgout = _sample_rect(sample_image, region_w, region_h)
                        break
                    elif region_w <= samp_path[1][1] and region_h <= samp_path[1][0]: #see if ok
                        sample_image = self.executeTransforms(sample_image)
                        imgout = _sample_rect(sample_image, region_h, region_w)
                        imgout = _cv2.rotate(imgout, _cv2.ROTATE_90_CLOCKWISE)
                        assert imgout.shape[0] == region_h and imgout.shape[1] == region_w
                        break
                    elif len(samples) > 1: #image too small to get region sample, delete it and try again
                        samples.remove(samp_path)
                    elif counter > 20: #lets not get in an infinite loop
                        sample_image = self.executeTransforms(sample_image)
                        imgout = sample_image
                        break
                    else: #Last one, just use it
                        sample_image = self.executeTransforms(sample_image)
                        imgout = sample_image
                        break
                counter += 1
        except Exception as e:
            print('Error was ' + str(e))
        finally:
            if imgout is None: #catch all
                return None, samp_path[0], {}

        if not mask is None:
            imgout = _get_image_from_mask(imgout, mask=mask)

        return imgout, samp_path[0], {}



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

        if self.digikam_params.no_filters():
            return

        for dummy, img_path, dummy in super().generate(yield_path_only=True):
            w, h = _ImageInfo.resolution(img_path) #use the pil lazy loader
            self.d_res[img_path] = (w, h) #ordered dict, matching order of pts, order is critical for getting random image
            self.pt_res.append([w, h])

        self._dirty_filters = False
#endregion


class RegionDualPosNeg():
    '''Generate positive and negative
    training images using VGG defined regions and
    a search specified by digikam tags.

    Negative regions are generated by using
    seperately defined digikam tags and picking randomly from
    images closest in resolution to the training image
    and deriving a randomly placed sample region of
    the same shape of the positive region
    '''
    def __init__(self, vggPos, dkPos, vggNeg, dkNeg, T, F): 
        '''(VGGSearchParams, DigiKamSearchParams, VGGSearchParams, DigiKamSearchParams, Transforms, Filters)

        Generate a positive and negtive training image from
        VGG configured regions
        '''
        self.vggPos = vggPos
        self.vggNeg = vggNeg
        self.dkPos = dkPos
        self.dkNeg = dkNeg
        self.T = T
        self.F = F
        self._pos_list = []
        self._neg_list = []
        assert isinstance(self.T, _transforms.Transforms)
        assert isinstance(self.F, _filters.Filters)

    def __call__(self, vggPos, dkPos, vggNeg, dkNeg, T, F):
        '''(VGGSearchParams, DigiKamSearchParams, DigiKamSearchParams, Transforms, Filters)

        All classes in opencvlib.generators
        '''
        self.vggPos = vggPos
        self.vggNeg = vggNeg
        self.dkPos = dkPos
        self.dkNeg = dkNeg
        self.T = T
        self.F = F
        self._pos_list = []
        self._neg_list = []


    def generate(self, outflag=_cv2.IMREAD_UNCHANGED):
        '''(cv2 imread flag) -> ndarray|None, str, ndarray|None, str
        Generate train and test image regions.

        Yields:
        positive image region,
        postive image path,
        negative image region,
        negative image path

        Images return None if an error occurs
        '''
        #Get training region
        self._pos_list = []
        self._neg_list = []

        assert isinstance(self.T, _transforms.Transforms)
        assert isinstance(self.F, _filters.Filters)

        PipePos = VGGRegions(self.dkPos, self.vggPos, filters=None, transforms=None)
        PipeNeg = VGGRegions(self.dkNeg, self.vggNeg, filters=None, transforms=None)

        for dummy, img_path, argsout in PipePos.generate(pathonly=True, outflag=outflag): #Pipe is a region generator
            self._pos_list.append([img_path, argsout.get('roi')])

        for dummy, img_path, argsout in PipeNeg.generate(pathonly=True, outflag=outflag): #Pipe is a region generator
            self._neg_list.append([img_path, argsout.get('roi')])

        for ind, x in enumerate(self._pos_list):

            try:
                imgpos = _getimg(x[0])
                imgneg = _getimg(self._neg_list[ind][0])

                if not self.F.validate(imgpos): continue
                if not self.F.validate(imgneg): continue

                imgposT = self.T.executeQueue(imgpos)
                imgnegT = self.T.executeQueue(imgneg)

                if imgposT is None: continue
                if imgnegT is None: continue

                ipos = _roi_polygons_get(imgposT, x[1])
                ineg = _roi_polygons_get(imgnegT, self._neg_list[ind][1])
            except Exception as dummy:
                s = 'Failed to generate a test region for %s' % img_path
                _log.warning(s)
                ipos = None
                ineg = None
            finally:
                yield ipos, x[0], ineg, self._neg_list[ind][0]



class RegionPosRandomNeg():
    ''' wrapper to generate a region with
    a corresponding random negative image of equal region
    size from an image of same approximate resolution.

    Train images require a VGGSearch parameter to
    extract prelabelled regions.
    '''
    def __init__(self, vggSP, pos_dkSP, neg_dkSP, T, F):
        '''(VGGSearchParams, DigiKamSearchParams, DigiKamSearchParams, Transforms, Filters)

        All classes in opencvlib.generators
        '''
        self.vggSP = vggSP
        self.pos_dkSP = pos_dkSP
        self.neg_dkSP = neg_dkSP
        self.T = T
        self.F = F


    def __call__(self, vggSP, pos_dkSP, neg_dkSP, T, F):
        '''(VGGSearchParams, DigiKamSearchParams, DigiKamSearchParams, Transforms, Filters)

        All classes in opencvlib.generators
        '''
        self.vggSP = vggSP
        self.pos_dkSP = pos_dkSP
        self.neg_dkSP = neg_dkSP
        self.T = T
        self.F = F


    def generate(self, outflag=_cv2.IMREAD_UNCHANGED):
        '''
        Generate train and test image regions.
        '''
        #Get training region
        Pipe = VGGRegions(self.pos_dkSP, self.vggSP, filters=self.F, transforms=self.T)

        #Instantiate random sample generator class
        RR = RandomRegions(self.neg_dkSP, filters=self.F, transforms=self.T)

        for img, img_path, argsout in Pipe.generate(outflag=outflag): #Pipe is a region generator
            if img is None:
                continue

            mask = argsout.get('mask', None)

            w, h = _ImageInfo.resolution(img)
            test_region, dummy, dummy1 = RR.generate(img_path, w, h, 10, mask, outflag=outflag)

            if test_region is None:
                s = 'Failed to generate a test region for %s' % img_path
                _log.warning(s)
                continue

            yield img, test_region, {}


#region Helper funcs
def _dir_has_vgg(fld):
    fld = _path.join(_path.normpath(fld), VGG_FILE)
    return _path.isfile(fld)
#endregion
