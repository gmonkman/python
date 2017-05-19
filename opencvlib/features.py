# pylint: disable=C0103, too-few-public-methods
'''extract features
all images are opened as cv2 BGR
'''
from enum import Enum as _Enum
from os import path as _path
from abc import ABC as _ABC
#from abc import abstractclassmethod
from abc import abstractmethod
#from abc import abstractproperty
#from abc import abstractstaticmethod


import cv2 as _cv2
import skimage.feature as _skfeature
import numpy as _np

import imutils.feature.factories as _factories


import opencvlib as _opencvlib
import opencvlib.decs as _decs
from opencvlib import Log as _Log
from opencvlib import show as _show

from funclib import iolib as _iolib
from funclib import baselib as _baselib

DESCRIPTOR_EXT = '.dsc'
SILENT = False

class eFeatureDetectorType(_Enum):
    '''opencv feature detectors

    A HOG implementation is in sklearn
    '''
    BRIEF = 0
    BRISK = 1
    FAST = 2
    FREAK = 3
    MSER = 5
    ORB = 6
    SIFT = 7
    STAR = 8
    SURF = 9
    HOG = 10


SK_FEATURE_DETECTORS = ['HOG']
CV_FEATURE_DETECTORS = [x.name for x in eFeatureDetectorType]


class _BaseDetector(_ABC):
    '''base class to handle basic feature
    detector operations such as save and create
    features of a single image.

    fdType:
        Enum:eFeatureDetectorType
    folder_root:
        root folder in which to save all vectors for each image

    As we would never mix and match the generation of feature vectors
    the class instance holds the root of the folder to which
    the vectors will be saved, and the feature detector
    algorhythm is set at the class level (rather than instance)
    '''
    folder_root = '.' #absolute or relative root from which to save (or load) a feature vector
    fdType = None

    func = None #the main function object
    args = [] #extraction function args
    kwargs = {} #extraction function kwargs

    def __init__(self, img, load_as_RGB=False, force_img_load=False):
        '''(str|ndarray, bool, bool) -> void
        img:
            file path of an image, or an ndarray
            representation of the image
        load_as_RGB:
            When imgpath is loaded, force format as RGB.
            Necessary if using color based detectors in Non CV2 libs
        force_img_load:
            Loading the image from the file system is usually deferred,
            but this forces loading at instance creation

        If img is a string, we will defer loading it into memory.
        At a later time we can process collections of Detector classes
        which will make them parallizable
        '''

        NEED TO BE ABLE TO HAVE AN INPUT AND OUTPUT LIKE QUEUE FOR
        WHEN WE CHAIN MULTIPLE OPERATIONS CONSIDER USING A DEQUIE


        if _BaseDetector.fdType is None:
            raise ValueError('fdType (Enum:eFeatureDetectorType) must be set for the class before object creation')

        self._imgpath = None #file path to image
        self._img = None #ndarray image
        self._img_descriptors = None #an image of the detected features

        self._is_rgb = load_as_RGB
        self._imgname = _iolib.get_file_parts2(self._imgpath)[1]

        self.keypoints = None
        self.descriptors = None #detected feature vector

        #so we leave the other as None
        if isinstance(img, str):
            self._imgpath = img
        elif isinstance(img, _np.ndarray):
            self.img = img

        if force_img_load:
            self._load_image(force=False)



    @property
    def img(self):
        '''img getter

        We can queue classes with _imgpaths
        without loading the imaged.
        '''
        if isinstance(self.img, _np.ndarray):
            return self._img
        else:
            self._load_image()
        return self._img



    @abstractmethod
    def extract_keypoints(self):
        '''(void) -> ndarray
        Extract keypoints using the
        extraction function func and return
        ndarray keypoints vector

        Also persists to self.keypoints

        Expect this to require overriding frequently
        '''
        self._load_image()
        self.keypoints = _BaseDetector.func(self.img, *_BaseDetector.args, **_BaseDetector.kwargs)
        assert isinstance(self.descriptors, _np.ndarray)


    @abstractmethod
    def extract_descriptors(self):
        '''
        Extract descriptors (usually of the image
        local to keypoints)

        These are frequently calculated as part
        of the keypoint extractor and so expect
        this to require overriding frequently.

        It may more frequently be set directly in
        the overriding inheriting class method for
        extract_keypoints
        '''
        self._load_image()
        self.descriptors = _BaseDetector.func(self.img, *_BaseDetector.args, **_BaseDetector.kwargs)
        assert isinstance(self.descriptors, _np.ndarray)


    @abstractmethod
    def view(self, dump=False, show=False):
        '''(ndarray, bool, bool) -> ndarray

        Image visualising the "endpoint" keypoints or
        more frequently descriptors

        The inheriting class will usually overide this,
        but should call super so this method
        can handle dumping or/and showing the image
        '''
        if not isinstance(self._img_descriptors, _np.ndarray): return

        #none critical - wrap in handler
        try:
            if dump:
                s = '%s.jpg' % _get_feat_file_name(self.folder_root, self._imgname, self.fdType)
                _cv2.imwrite(s, self._img_descriptors)
            if show:
                _show(self._img_descriptors)
        except Exception as e:
            _Log.exception('Keypoints or descriptors image dump or show failed.')
            if not SILENT: print('Error was ' + str(e))


    def save_descriptor_vector(self):
        '''(void) -> bool
        Save feature.
        '''
        assert isinstance(self.descriptors, _np.ndarray)


        s = _get_feat_file_name(_BaseDetector.folder_root, self._imgname, self.fdType)

        self.descriptors.dump(s)
        _Log.info('Dumped descriptors for image (or image region) %s to %s', self._imgpath, s)


    def _load_image(self, force=False, imgpath=''):
        '''(bool, str, bool) -> ndarray|none

        Load an image from disk, according to self.imgpath set
        on a call or during instantiation

        Sets the instance img property as well.

        imgpath:
            if provided loads specified image, overriding
            any presets in class calls or instantiation
        force:
            force load if self.img looks like it already is valid (loaded)
        '''
        i = self._imgpath if _baselib.isempty(imgpath) else imgpath
        if _baselib.isempty(imgpath):
            if self._is_rgb:
                if force or _baselib.isempty(self.img):
                    self.img = _openSK(i)
            else:
                if force or _baselib.isempty(self.img):
                    self.img = _openCV(i)

        self._imgpath = i
        self._imgname = _iolib.get_file_parts2(i)[1]
        return self.img


    def read_descriptors_from_file(self):
        '''(void) -> ndarray
        Loads feature descriptors from file.

        Depending on the detection function,
        this may load descriptors or features
        '''
        s = _get_feat_file_name(_BaseDetector.folder_root, self._imgname, _BaseDetector.fdType)
        try:
            f = _np.load(s)
        except Exception as e:
            _Log.exception('Failed to read feature %s from disk.', s)
            if not SILENT: print(e)
            f = None



class OpenCVDetector(_BaseDetector):
    '''create am opencv detector by

    set_detector:
        main method to setup the detector,
        uses imutils factories to get the
        requested detector object using
        the enum eFeatureDetectorType

    Explanation:
        OpenCV implements create methods which return
        feature extractor objects.

        These objects can be called with args and kwargs to preset
        the options used in the final detect call to the extractor

        cls.DetectorObj holds an object instance:
            cls.DetectorObj = ORB_create(args, kwargs)
    '''

    DetectorObj = None

    def __init__(self, img, load_as_RGB=False, force_img_load=False):
        super.__init__(self, img, load_as_RGB, force_img_load)


    @classmethod
    def set_detector(cls, fdType, *args, **kwargs):
        assert isinstance(fdType, eFeatureDetectorType)
        if not fdType.name in CV_FEATURE_DETECTORS:
            s = 'No "%s" implemention of feature detector %s in OpenCVDetector.' % OpenCVDetector.fdType.name
            raise KeyError(s)
        else:
            cls.fdType = fdType
            cls.args = args
            cls.kwargs = kwargs

        if fdType.name in _factories._DETECTOR_FACTORY:
            cls.DetectorObj = _factories.FeatureDetector_create(fdType.name, *args, **kwargs)
        else:
            cls.DetectorObj = _factories.DescriptorExtractor_create(fdType.name, *args, **kwargs)

        if cls.DetectorObj is None:
            raise KeyError('Failed to create feature detector from imutils.feature.factories. The key was %s' % fdType.name)

        cls.func = cls.DetectorObj.


    def view(self, img, dump=False, show=False):
        super().view(img, dump, show)


    def extract_feature_vector(self):
        super().extract_keypoints()


class HOGDetector(_BaseDetector):
    '''HOG feature extractor, implementation
    is from skimage

    Example args:
        hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualise=True)
    '''
    func = _skfeature.hog

    def __init__(self, img, force_img_load=False, *args, **kwargs):
        #load_as_RGB=True - this is an skimage func
        _BaseDetector.func = _skfeature.hog
        super().__init__(img, True, force_img_load)


    def view(self, dump=False, show=False):
        super().view(dump, show)


    def extract_feature_vector(self):
        fd, hog_image = _skfeature.hog(self.img, visualise=True, *HOGDetector.args, **HOGDetector.kwargs)
        self._img_descriptors = _opencvlib.transforms.rescale_intensity(hog_image, in_range=(0, 0.02))



#region Local Helpers
@_decs.decgetimg
def _openSK(img):
    return _opencvlib.transforms.BGR2RGB(img)


@_decs.decgetimg
def _openCV(img):
    return img


def _get_feat_file_name(fld, img_name_only, fdType):
    '''(str, Enum:eFeatureDetectorType) -> str
    Build feature file name

    image_name_only
        file name sans path, eg. 123.jpg
    fdType
        The enum eFeatureDetectorType

    example output
        123.jpg_ORB.ftr
    '''

    s = '%s_%s%s' % (img_name_only, str(fdType.name), DESCRIPTOR_EXT) #123.jpg_ORB.ftr
    s = _path.join(fld, s)
    return s
#endregion
