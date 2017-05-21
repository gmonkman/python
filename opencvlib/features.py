# pylint: disable=C0103, too-few-public-methods
'''extract features
all images are opened as cv2 BGR
'''
import pickle
from enum import Enum as _Enum
from os import path as _path
from abc import ABC as _ABC
from abc import abstractmethod

import cv2 as _cv2
import skimage.feature as _skfeature
import numpy as _np




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
    args = []
    kwargs = {}

    def __init__(self, img, mask=None, load_as_RGB=False, force_img_load=False):
        '''(str|ndarray, ndarray|None, bool, bool) -> void
        img:
            file path of an image, or an ndarray
            representation of the image
        mask:
            some functions support passing in an ndarray mask
            where True/1 values indicate matching 'pixels' should
            be processed.
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

        if _BaseDetector.fdType is None:
            raise ValueError('fdType (Enum:eFeatureDetectorType) must be set for the class before object creation')

        self._imgpath = None #file path to image
        self._img = None #ndarray image, the image on which to perform detection
        self._img_descriptors = None #an image of the detected features for review, debugging etc
        self._is_rgb = load_as_RGB
        self._imgname = _iolib.get_file_parts2(self._imgpath)[1]

        self.mask = mask
        self.keypoints = None
        self.descriptors = None #detected feature vector

        self.other_outputs = {} #dict to hold other outputs


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
        if self._img_descriptors is None: return

        try:
            if dump:
                s = '%s.jpg' % _get_feat_file_name(self.folder_root, self._imgname, self.fdType)
                _cv2.imwrite(s, self._img_descriptors)
            if show:
                _show(self._img_descriptors)
        except Exception as e:
            _Log.exception('Keypoints or descriptors image dump or show failed.')
            if not SILENT: print('Error was ' + str(e))



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

        s = 'Opened image %s' % self._imgpath
        prints(s)

        return self.img


    def save_descriptors_to_file(self):
        '''(void) -> void
        Save feature.
        '''
        s = _get_feat_file_name(_BaseDetector.folder_root, self._imgname, self.fdType)

        if _baselib.isempty(self.keypoints) and _baselib.isempty(self.descriptors):
            msg = 'No keypoints or descriptors to dump for image (or image region) %s.', self._imgpath
            _Log.info(msg)
            prints(msg)

        if self._has_keypoints:
            k = self.keypoints
        else:
            k = []

        if self._has_descriptors: 
            d = self.descriptors
        else:
            d = _np.array([[]])

        temp = _keypoints_pickle(k, d)

        with open(s, 'wb') as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)
        msg = 'Dumped %s keypoints and %s descriptors for image (or image region) %s to %s' % (len(self.keypoints), len(self.descriptors), self._imgpath, s)
        prints(msg)

    


    def read_descriptors_from_file(self):
        '''(void) -> ndarray
        Loads feature descriptors from file.

        Depending on the detection function,
        this may load descriptors or features
        '''
        s = _get_feat_file_name(_BaseDetector.folder_root, self._imgname, _BaseDetector.fdType)
        try:

            with open(s, 'rb') as ff:
                f = pickle.load(ff)
            self.keypoints, self.descriptors = _keypoints_unpickle(f)
            msg = 'Read %s keypoints and %s descriptors from %s' % (len(self.keypoints), len(self.descriptors), s)
            prints(msg)
            _Log.info(msg)
        except Exception as e:
            _Log.exception('Failed to read feature %s from disk.', s)
            prints(e)
            self.keypoints = None
            self.descriptors = None

    
    def _has_keypoints(self):
        '''() -> bool

        Check if we have keypoints
        '''
        if isinstance(self.keypoints, list):
            if len(self.keypoints) > 0:
                return isinstance(self.keypoints[0], _cv2.KeyPoint)
            else:
                return False
        else:
            return False


    def _has_descriptors(self):
        '''() -> bool
        Check if we have descriptors
        '''
        if isinstance(self.descriptors, _np.ndarray):
            return len(self.descriptors) > 0
        else:
            return False

    
class _OpenCVDetector(_BaseDetector):
    '''base class for making
    opencv detectors
    See http://docs.opencv.org/3.1.0/classes.html
    '''
    fdType = None
    args = []
    kwargs = {}
    Detector = None
    keypoint_color = (0, 255, 0)

    def __init__(self, img, mask=None, load_as_RGB=False, force_img_load=False):
        super().__init__(self, img, mask=mask, load_as_RGB=load_as_RGB, force_img_load=force_img_load)


    def view(self, dump=False, show=False, force=False):
        '''(bool, bool, bool) -> void
        View or dump the detected keypoints
        
        dump:
            dump the image to the file system
        show:
            show the image using opencv.imshow
        force:
            force loading the keypoints image, if false then
            we will use the existing keypoints image if present
        '''
        if _baselib.isempty(self._img_descriptors) or force:
            self._img_descriptors = _cv2.drawKeypoints(self.img, self.keypoints, color=_OpenCVDetector.keypoint_color, flags=0)
        super().view(dump, show)


    def extract_descriptors(self):
        '''
        Extract descriptors, and also
        keypoints if they don't already exist
        '''
        super().extract_descriptors()
        if _baselib.isempty(self.keypoints):
            self.keypoints, self.descriptors = OpenCV_ORB.Detector.detectAndCompute(image=self.img, mask=self.mask)
        else:
            self.descriptors = _OpenCVDetector.Detector.compute(image=self.img, keypoints=self.keypoints)

    def extract_keypoints(self):
        super().extract_keypoints() #load image
        self.keypoints = _OpenCVDetector.Detector.detect(image=self.img, mask=self.mask)



class OpenCV_ORB(_OpenCVDetector):
    '''create an opencv ORB detector

    Note that ORB options should be set
    by accessing Detector
    '''
    fdType = eFeatureDetectorType.ORB
    kwargs = {'nfeatures':500, 'scaleFactor':1.2, 'nlevels':8, 'edgeThreshold':31, 'firstLevel':0, 'WTA_K':2, 'scoreType':_cv2.ORB_HARRIS_SCORE, 'patchSize':31, 'fastThreshold':20}
    #http://docs.opencv.org/3.1.0/db/d95/classcv_1_1ORB.html
    Detector = _cv2.ORB_create(**kwargs)
    


class OpenCV_SIFT(_OpenCVDetector):
    '''create an opencv SIFT detector

    Note that ORB options should be set
    by accessing Detector
    '''
    fdType = eFeatureDetectorType.SIFT
    kwargs = {'nfeatures':500, 'nOctaveLayers':3, 'contrastThreshold':0.04, 'edgeThreshold':10, 'sigma':1.6}
    Detector = _cv2.xfeatures2dSIFT_create(**kwargs)
    


class OpenCV_FAST(_OpenCVDetector):
    '''create an opencv FAST detector

    Note that FAST options should be set
    by accessing Detector

    This is a keypoint only detector, use BRISK
    '''
    fdType = eFeatureDetectorType.FAST
    kwargs = {'threshold':10, 'nonmaxSuppression':True, 'type':_cv2.FAST_FEATURE_DETECTOR_TYPE_9_16}
    Detector = _cv2.FastFeatureDetector_create(**kwargs)


class OpenCV_BRISK(_OpenCVDetector):
    '''BRISK keypoint and descriptors
    https://www.robots.ox.ac.uk/~vgg/rg/papers/brisk.pdf
    '''
    fdType = eFeatureDetectorType.BRISK
    kwargs = {'thresh':30, 'octaves':4, 'patternScale':1.0}
    Detector = _cv2.BRISK_create(**kwargs)
    


class HOGDetector(_BaseDetector):
    '''HOG feature extractor, implementation
    is from skimage

    Example args:
        hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualise=True)
    '''
    fdType = eFeatureDetectorType.HOG
    args = []
    visualise = False
    kwargs = {'transform_sqrt':True, 'block_norm':'L1', 'cells_per_block':(3, 3), 'pixels_per_cell':(8, 8), 'orientations':9}

    def __init__(self, img, force_img_load=False):
        #load_as_RGB=True - this is an skimage func
        super().__init__(img, load_as_RGB=True, force_img_load=force_img_load)


    def view(self, dump=False, show=False):
        super().view(dump, show)


    def extract_descriptors(self):
        super().extract_descriptors() #loads image
        
        if HOGDetector.visualise:
            fd, hog_image = _skfeature.hog(self.img, visualise=True, *HOGDetector.args, **HOGDetector.kwargs)
            self._img_descriptors = _opencvlib.transforms.rescale_intensity(hog_image, in_range=(0, 0.02))
        else:
            self._img_descriptors = None
            fd, hog_image = _skfeature.hog(self.img, visualise=False, *HOGDetector.args, **HOGDetector.kwargs)
            

        self.descriptors = fd
        self.keypoints = None


    def extract_keypoints(self):
        self.extract_descriptors()





#region Local Helpers
@_decs.decgetimg
def _openSK(img):
    return _opencvlib.transforms.BGR2RGB(img)


@_decs.decgetimg
def _openCV(img):
    return img


def _keypoints_pickle(keypoints, descriptors):
    '''(class:cv2.KeyPoints, ndarray)->list
    prepare keypoints and descriptor
    for pickling'''
    i = 0
    temp_array = []
    for i, point in enumerate(keypoints):
        temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id, descriptors[i])     
        temp_array.append(temp)
    return temp_array


def _keypoints_unpickle(array):
    '''(list) -> list:cv2.KeyPoints, ndarray

    pickled array loaded from the filesystem
    '''
    keypoints = []
    descriptors = []
    for point in array:
        temp_feature = _cv2.KeyPoint(x=point[0][0], y=point[0][1], _size=point[1], _angle=point[2], _response=point[3], _octave=point[4], _class_id=point[5])
        temp_descriptor = point[6]  
        keypoints.append(temp_feature)
        descriptors.append(temp_descriptor)
    return keypoints, _np.array(descriptors)


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


def prints(s, log=True):
    '''silent print'''
    if not SILENT:
        print(s)
    if log:
        _Log.info(s)
#endregion
