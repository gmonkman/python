# pylint: disable=C0103, too-few-public-methods, arguments-differ
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
CV_FEATURE_DETECTORS.remove('HOG')


class _BaseDetector(_ABC):
    '''base class to handle basic feature
    detector operations such as save and create
    features of a single image.
    '''

    def __init__(self, output_folder, fdType, load_as_RGB=False, load_as_grey=False):
        '''(str, Enum:eFeatureDetectorType, bool, bool) -> void

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
        self._is_grey = load_as_grey
        self._is_rgb = load_as_RGB
        self._fdType = fdType
        self._output_folder = output_folder

        self.descriptors = None
        self.keypoints = None
        self._img_descriptors = None
        self._img = None
        self._imgpath = ''
        self._imgname = ''
        self._imgfolder = ''
        self._mask = None
        self.other_outputs = {}


    def __call__(self, img, mask):
        '''(str|ndarray, ndarray|None) -> void
        Loading of the image is deferred until
        needed (assuming img is a str)

        img:
            file path of an image, or an ndarray
            representation of the image
        mask:
            some functions support passing in an ndarray mask
            where True/1 values indicate matching 'pixels' should
            be processed.
        '''

        self._imgpath = None #file path to image
        self._img_descriptors = None #an image of the detected features for review, debugging etc
        
        self._mask = mask
        self.keypoints = None
        self.descriptors = None #detected feature vector
        self.other_outputs = {} #dict to hold other outputs

        #so we leave the other as None
        if isinstance(img, str):
            self._imgpath = img
            self._imgfolder, self._imgname, dummy = _iolib.get_file_parts2(self._imgpath)
        elif isinstance(img, _np.ndarray):
            self._img = img



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
    def view(self, dump=False, show=True, show_original=True):
        '''(ndarray, bool, bool) -> ndarray

        Image visualising the "endpoint" keypoints or
        more frequently descriptors

        dump:
            save the image as a file
        show:
            show the descriptors/keypoints
        show_original:
            show the original image
        
        Notes:
        show and show_original will tile the two images

        The inheriting class will usually overide this,
        but should call super so this method
        can handle dumping or/and showing the image
        '''
        if not isinstance(self._img_descriptors, _np.ndarray): return

        #none critical - wrap in handler
        if self._img_descriptors is None: return

        try:
            if dump:
                s = '%s.jpg' % _get_feat_file_name(self._output_folder, self._imgname, self._fdType)
                _cv2.imwrite(s, self._img_descriptors)
            if show and show_original:
                _show([self._img_descriptors, self._img])
            elif show:
                _show(self._img_descriptors)
            elif show_original:
                _show(self._img)

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
        if not _baselib.isempty(imgpath):
            if _iolib.file_exists(imgpath):
                if self._is_grey:
                    self._img = _opengrey(imgpath)
                elif self._is_rgb:
                    self._img = _openSK(imgpath)
                else:
                    self._img = _openCV(imgpath)
                self._imgfolder, self._imgname, dummy = _iolib.get_file_parts2(imgpath)
                self._imgpath = imgpath
                s = 'Opened image %s' % imgpath
                prints(s)
            else:
                prints('Asked to load image %s, but the file doesnt exist.' % imgpath)
            return

        if force and _iolib.file_exists(self._imgpath):
            if self._is_grey:
                self._img = _opengrey(self._imgpath)                
            elif self._is_rgb:
                self._img = _openSK(self._imgpath)
            else:
                self._img = _openCV(self._imgpath)
            self._imgfolder, self._imgname, dummy = _iolib.get_file_parts2(self._imgpath)
            s = 'Opened image %s' % self._imgpath
            prints(s)
            return
            
        if force and not _iolib.file_exists(self._imgpath):
            s = 'Requested force load of image %s, but the file doesnt exist' % self._imgpath
            self._img = None
            prints(s)

        if not force and isinstance(self._img, _np.ndarray):
            if not _opencvlib.ImageInfo.typeinfo(self._img) & _opencvlib.eImgType.CHANNEL_1.value:
                self._img = _opencvlib.transforms.togreyscale(self._img)
        return


    def save_descriptors_to_file(self):
        '''(void) -> void
        Save feature.
        '''
        _iolib.create_folder(self._output_folder)

        s = _get_feat_file_name(self._output_folder, self._imgname, self._fdType)

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
        
        kpnr = 0 if self.keypoints is None else len(self.keypoints)
        dnr = 0 if self.descriptors is None else len(self.descriptors)

        msg = 'Dumped %s keypoints and %s descriptors for image (or image region) %s to %s' % (kpnr, dnr, self._imgpath, s)
        prints(msg)

    

    def read_descriptors_from_file(self):
        '''(void) -> ndarray
        Loads feature descriptors from file.

        Depending on the detection function,
        this may load descriptors or features
        '''
        s = _get_feat_file_name(self._output_folder, self._imgname, self._fdType)
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

    _keypoint_color = (0, 255, 0)
    
    def __init__(self, output_folder, Detector, dfType, load_as_RGB=False, load_as_grey=False):
        '''(str, obj:CV2Detector, ndarray|None, Enum:eFeatureDetectorType, bool)
        
        output_folder:
            Location to save descriptors/points
        Detector:
            OpenCV Detector instance created with opencvs _create calls
        eFeatureDetectorType:
            Used in the naming of persisted output features
        load_as_RGB:
            load image as RGB, necessary if using non-opencv detectors
        '''
        self._Detector = Detector
        super().__init__(output_folder=output_folder, fdType=dfType, load_as_RGB=load_as_RGB, load_as_grey=load_as_grey)


    def __call__(self, img, mask=None, extract=False):
        '''(str|ndarray, ndarray|None, bool) -> void

        img:
            image file path, or ndarray
        mask:
            Boolean array mask of same shape as img
        extract:
            Force extracting on the call, rather than
            perform a seperate call to extract_descriptors
        '''
        super().__call__(img, mask=mask)
        if extract:
            self.extract_descriptors()


    def view(self, dump=False, show=False, force=False, show_original=False):
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
        if _baselib.isempty(self._img):
            prints('View was called, but there was no image set')
            return

        if not self._has_keypoints:
            prints('View was called, but no keypoints have been calculated. Call extract_keypoints first.')
            return

        if _baselib.isempty(self._img_descriptors) or force:
            self._img_descriptors = _cv2.drawKeypoints(self._img, self.keypoints, color=_OpenCVDetector._keypoint_color, flags=0)
        super().view(dump, show, show_original)


    def extract_descriptors(self):
        '''
        Extract descriptors, and also
        keypoints if they don't already exist
        '''
        super().extract_descriptors() #parent handles loading the image
        if _baselib.isempty(self.keypoints):
            self.keypoints, self.descriptors = self._Detector.detectAndCompute(image=self._img, mask=self.mask)
        else:
            self.descriptors = self._Detector.compute(image=self._img, keypoints=self.keypoints)


    def extract_keypoints(self):
        super().extract_keypoints() #parent handles loading the image
        self.keypoints = self._Detector.detect(image=self._img, mask=self.mask)



class OpenCV_ORB(_OpenCVDetector):
    '''create an opencv ORB detector

    Note that ORB options should be set
    by accessing Detector
    '''
    kwargs = {'nfeatures':500, 'scaleFactor':1.2, 'nlevels':8, 'edgeThreshold':31, 'firstLevel':0, 'WTA_K':2, 'scoreType':_cv2.ORB_HARRIS_SCORE, 'patchSize':31, 'fastThreshold':20}
    #http://docs.opencv.org/3.1.0/db/d95/classcv_1_1ORB.html
    Detector = _cv2.ORB_create(**kwargs)

    def __init__(self, output_folder, load_as_RGB=False):
        super().__init__(output_folder, OpenCV_ORB._Detector, eFeatureDetectorType.ORB, load_as_RGB=False, load_as_grey=True)
    
    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class OpenCV_SIFT(_OpenCVDetector):
    '''create an opencv SIFT detector

    Note that ORB options should be set
    by accessing Detector
    '''
    kwargs = {'nfeatures':500, 'nOctaveLayers':3, 'contrastThreshold':0.04, 'edgeThreshold':10, 'sigma':1.6}
    Detector = _cv2.xfeatures2d.SIFT_create(**kwargs)
    

    def __init__(self, output_folder, load_as_RGB=False):
        super().__init__(output_folder, OpenCV_SIFT._Detector, eFeatureDetectorType.SIFT, load_as_RGB=False, load_as_grey=True)

    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class OpenCV_FAST(_OpenCVDetector):
    '''create an opencv FAST detector

    Note that FAST options should be set
    by accessing Detector

    This is a keypoint only detector, use BRISK
    '''
    kwargs = {'threshold':10, 'nonmaxSuppression':True, 'type':_cv2.FAST_FEATURE_DETECTOR_TYPE_9_16}
    _Detector = _cv2.FastFeatureDetector_create(**kwargs)


    def __init__(self, output_folder, load_as_RGB=False):
        super().__init__(output_folder, OpenCV_FAST._Detector, eFeatureDetectorType.FAST, load_as_RGB=False, load_as_grey=True)


    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class OpenCV_BRISK(_OpenCVDetector):
    '''BRISK keypoint and descriptors
    https://www.robots.ox.ac.uk/~vgg/rg/papers/brisk.pdf
    '''
    kwargs = {'thresh':30, 'octaves':4, 'patternScale':1.0}
    Detector = _cv2.BRISK_create(**kwargs)
    

    def __init__(self, output_folder, load_as_RGB=False):
        super().__init__(output_folder, OpenCV_BRISK._Detector, eFeatureDetectorType.BRISK, load_as_RGB=False, load_as_grey=True)


    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class OpenCV_SURF(_OpenCVDetector):
    '''SURF keypoint and descriptors
    '''
    kwargs = {'nOctaves':4, 'nOctaveLayers':3, 'extended':False, 'upright':False}
    Detector = _cv2.xfeatures2d.SURF_create(**kwargs)


    def __init__(self, output_folder):
        super().__init__(output_folder, OpenCV_SURF._Detector, eFeatureDetectorType.SURF, load_as_RGB=False, load_as_grey=True)


    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class HOGDetector(_BaseDetector):
    '''HOG feature extractor, implementation
    is from skimage

    Example args:
        hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualise=True)
    '''

    kwargs = {'transform_sqrt':True, 'block_norm':'L2-Hys', 'cells_per_block':(3, 3), 'pixels_per_cell':(8, 8), 'orientations':9}
    args = []

    def __init__(self, output_folder):
        '''(str, bool) -> void
        
        output_folder:
            Where to save features/keypoints
        load_keypoint_visual:
            load the image overlayed with the keypoints/descriptors for
            the view function. Has an overhead, so use when debugging
        '''
        self._load_keypoint_visual = False
        #load_as_RGB=True - this is an skimage func
        super().__init__(output_folder, eFeatureDetectorType.HOG, load_as_RGB=False, load_as_grey=True)

    
    def __call__(self, img, mask=None, extract=False, load_keypoint_visual=False):
        self._load_keypoint_visual = load_keypoint_visual
        super().__call__(img, mask)
        if extract:
            self.extract_descriptors()


    def view(self, dump=False, show=True, show_original=True):
        super().view(dump, show, show_original)


    def extract_descriptors(self):
        super().extract_descriptors() #loads image
        
        if self._load_keypoint_visual:
            fd, hog_image = _skfeature.hog(self._img, visualise=True, *HOGDetector.args, **HOGDetector.kwargs)
            self._img_descriptors = _opencvlib.transforms.rescale_intensity(hog_image, in_range=(0, 0.02))
        else:
            self._img_descriptors = None
            fd, hog_image = _skfeature.hog(self._img, visualise=False, *HOGDetector.args, **HOGDetector.kwargs)
            
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

@_decs.decgetimg
def _opengrey(img):
    return _opencvlib.transforms.togreyscale(img)


def _keypoints_pickle(keypoints, descriptors):
    '''(class:cv2.KeyPoints, ndarray)->list
    prepare keypoints and descriptor
    for pickling'''
    i = 0
    temp_array = []

    if keypoints is None and descriptors is None:
        return

    #we dont always have keypoints and descriptors
    if _baselib.isempty(keypoints):
        for dummy, desc in enumerate(descriptors):
            temp = (None, None, None, None, None, None, desc)     
            temp_array.append(temp)
    elif _baselib.isempty(descriptors):
        for i, point in enumerate(keypoints):
            temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id, None)     
            temp_array.append(temp)
    else:
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
