# pylint: disable=C0103, too-few-public-methods, arguments-differ
'''extract features
all images are opened as cv2 BGR
'''
from enum import Enum as _Enum
from os import path as _path
from abc import ABC as _ABC
from abc import abstractmethod

import cv2 as _cv2
import skimage.feature as _skfeature
import numpy as _np




import opencvlib as _opencvlib
import opencvlib.decs as _decs
import opencvlib.keypoints as _keypoints

from opencvlib import Log as _Log
from opencvlib import show as _show

from funclib import iolib as _iolib
from funclib import baselib as _baselib

DESCRIPTOR_EXT = '.dsc'
FEATURE_POINT_EXT = '.fpt'

SILENT = False

class eFeatureDetectorType(_Enum):
    '''feature detectors
    '''
    cvBRIEF = 0
    cvBRISK = 1
    cvFAST = 2
    cvFREAK = 3
    cvMSER = 5
    cvORB = 6
    cvSIFT = 7
    cvSTAR = 8
    cvSURF = 9
    cvHOG = 10
    skHOG = 1024


SK_FEATURE_DETECTORS = [x.name for x in eFeatureDetectorType if x.name.startswith('sk')]
CV_FEATURE_DETECTORS = [x.name for x in eFeatureDetectorType if x.name.startswith('cv')]



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
        self._output_folder = output_folder #where we save files, set at call time, eg by reading from an inifile

        self.descriptors = None #descriptor vectors (usually ndarray)
        self.keypoints = None #keypoints vectors, ndarray, or list cv2.KeyPoints 
        self._img_descriptors = None #ndarray showing the results of detection
        self._img = None #holds the image as an ndarray or path
        self._imgpath = '' #holds the image path c:/xyz.jpg, needed for creating names to dump files
        self._imgname = '' #nae of the image, xyz.jpg
        self._imgfolder = '' #folder of the image c:/
        self._descriptor_filename = '' #the filename which gets used if we save the descriptors
        self._keypoints_filename = ''#the filename which gets used if we save the keypoints
        self._feature_image_filename = '' #used when we dump the image of the descriptors to the hdd

        self._mask = None #ndarray used for some feature detection algos
        self.other_outputs = {} #optional dict bag to stuff additional results if needed


    def __call__(self, img, imgpath, mask):
        '''(str|ndarray, ndarray|None) -> void
        Loading of the image is deferred until
        needed (assuming img is a str)

        img:
            file path of an image, or an ndarray
            representation of the image
        img_path:
            path to the file on the file system.
            Used in save and read operations
            eg c:/temp/myimage.jpg
        mask:
            some functions support passing in an ndarray mask
            where True/1 values indicate matching 'pixels' should
            be processed.
        '''

        self._imgpath = imgpath #file path to image
        self._img_descriptors = None #an image of the detected features for review, debugging etc
        
        self._mask = mask
        self.keypoints = None
        self.descriptors = None #detected feature vector
        self.other_outputs = {} #dict to hold other outputs
        
        self._mask_size_check()

        #support deferring loading of the image if we dont
        #pass an ndarray
        if not isinstance(img, _np.ndarray) and not isinstance(img, str):
            img = imgpath

        if isinstance(img, str):
            self._imgpath = img
            self._imgfolder, self._imgname, dummy = _iolib.get_file_parts2(self._imgpath)
        elif isinstance(img, _np.ndarray):
            self._img = img
        
        self._set_img_text()
        self._set_file_names()


    def _set_img_text(self):
        '''(void) -> void
        Set self _imgfolder and _imgname.

        These are used when persisting the
        pointers/descriptors to file
        '''
        self._imgfolder, self._imgname, dummy = _iolib.get_file_parts2(self._imgpath)


    def _mask_size_check(self):
        '''check the mask size matches the img size,
        throw error if they dont'''
        if isinstance(self._mask, _np.ndarray) and isinstance(self._img, _np.ndarray):
            if self._mask.shape != self._img.shape:
                raise ValueError('Mask shape %s did not match the image shape %s' % (str(self._img.shape), StopIteration(self._mask.shape)))


    def _set_dense_keypoints(self,
        initFeatureScale=1.,
        featureScaleLevels=1, 
        featureScaleMul=0.1,
        initXyStep=6,
        initImgBound=0, 
        varyXyStepWithScale=True,
        varyImgBoundWithScale=False
                            ):
        ''' (float, int, float, int, int, bool, bool) -> void

        Populates keypoints with a dense
        keypoint grid, to support dense 
        feature detection. 
        
        Obeys instance mask if set
        
        Args:
            initFeatureScale:
            featureScaleLevels:
            featureScaleMul:
            initXyStep:
            initImgBound:
            varyXyStepWithScale:
            varyImgBoundWithScale:

        Returns:
            list of cv2.Keypoints
        '''
        #other variables
        #img - the input image
        #mask - mask

        self.keypoints = []
        curScale = float(initFeatureScale)
        curStep = initXyStep
        curBound = initImgBound
        for dummy in range(featureScaleLevels):  #( int curLevel = 0 curLevel < featureScaleLevels curLevel++ )
            x = curBound
            y = 0
            while x < self._img.shape[1] - curBound:
                while y < self._img.shape[0] - curBound:
                    self.keypoints.append(_cv2.KeyPoint(x, y, curScale))
                    y += curStep
                x += curStep

            curScale = float(curScale * featureScaleMul)

            if varyXyStepWithScale:
                curStep = int(curStep * featureScaleMul + 0.5)

            if varyImgBoundWithScale:
                curBound = int(curBound * featureScaleMul + 0.5)
        
        self.keypoints = _keypoints.applymask(self.keypoints, self._mask)
        #KeyPointsFilter::runByPixelsMask( keypoints, mask )




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
                s = '%s.jpg' % self._feature_image_filename
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
            
            self._mask_size_check()

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


    @abstractmethod
    def write(self, nd_keypoints, nd_descriptors):
        '''(ndarray|None, ndarray|None) -> void
        
        Save features and points to hdd.

        The inheriting class provides the logic to
        convert outputs to ndarrays. These arrays
        are saved in this function by call to
        super().write(ndarray, ndarray)
        '''      
        _iolib.create_folder(self._output_folder)
        
        if isinstance(nd_descriptors, _np.ndarray): nd_descriptors.dump(self._descriptor_filename) 
        if isinstance(nd_keypoints, _np.ndarray): nd_keypoints.dump(self._keypoints_filename)

        msg = 'Dumped keypoints and descriptors for image (or region) %s to %s' % (self._imgpath, self._output_folder)
        prints(msg)

    
    @abstractmethod
    def read(self):
        '''(void) -> ndarray, ndarray
        Loads keypoints and descriptors from file
        as ndarrays.

        Returns:
            keypoints, descriptors

        The derived class should first call kp, desc = super().read()
        and then provide code to translate to suitable form if required
        '''
        if _iolib.file_exists(self._keypoints_filename): 
            kps = _np.load(self._keypoints_filename)
        else:
            kps = None

        if _iolib.file_exists(self._descriptor_filename): 
            dsc = _np.load(self._descriptor_filename)
        else:
            dsc = None

        return kps, dsc

    
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


    def _set_file_names(self):
        '''(str, Enum:eFeatureDetectorType) -> str, str
        Build filenames for feature points
        and feature descriptors in preparation
        for saving.
        
        Returns:
            feature points file name, descriptors file name

        image_name_only:
            file name sans path, eg. 123.jpg
        fdType:
            The enum eFeatureDetectorType

        example output
            123.jpg_ORB.fpt, 123.jpg_ORB.dsc
        '''

        s_ptr = '%s_%s%s' % (self._imgname, str(self._fdType.name), FEATURE_POINT_EXT) #123.jpg_ORB.fpt
        self._keypoints_filename = _path.normpath(_path.join(self._output_folder, s_ptr))
        
        s_dsc = '%s_%s%s' % (self._imgname, str(self._fdType.name), DESCRIPTOR_EXT) #123.jpg_ORB.dsc
        self._descriptor_filename = _path.normpath(_path.join(self._output_folder, s_dsc))
        
        s_fif = '%s_%s%s' % (self._imgname, str(self._fdType.name), '.jpg') #123.jpg_ORB.jpg
        self._feature_image_filename = _path.normpath(_path.join(self._output_folder, s_fif))
 

  
          
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


    def __call__(self, img, imgpath, mask=None, extract_now=False):
        '''(str|ndarray, ndarray|None, bool) -> void

        img:
            image file path, or ndarray
        mask:
            Boolean array mask of same shape as img
        extract:
            Force extracting on the call, rather than
            perform a seperate call to extract_descriptors
        '''
        super().__call__(img, imgpath, mask=mask)
        if extract_now:
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
        if repr(self._Detector).startswith('<HOGDescriptor'): #Detect and compute not supported for HOGDescriptor
            self.descriptors = self._Detector.compute(image=self._img, keypoints=self.keypoints)
        else:
            if _baselib.isempty(self.keypoints):
                self.keypoints, self.descriptors = self._Detector.detectAndCompute(image=self._img, mask=self.mask)
            else:
                self.descriptors = self._Detector.compute(image=self._img, keypoints=self.keypoints)


    def extract_keypoints(self):
        if 'dense' in repr(self._Detector).lower():
            self._set_dense_keypoints(self.initFeatureScale, self.featureScaleLevels,
                            self.featureScaleMul, self.initXyStep, self.initImgBound,
                            self.varyXyStepWithScale, self.varyImgBoundWithScale
                            )
        else:
            super().extract_keypoints() #parent handles loading the image
            self.keypoints = self._Detector.detect(image=self._img, mask=self.mask)


    def write(self):
        '''write descriptors and keypoints to the file system,
        this function handles converting keypoints to an ndarray
        '''
        if not self._has_keypoints() and not self._has_descriptors():
            s = 'keypoint and descriptor write called, but they are empty. The image was %s' % self._imgpath
            prints(s)
            return

        if self._has_descriptors():
            d = self.descriptors #opencv outputs descriptors as an ndarray
        else:
            d = _np.array([[]])


        k = _np.array([[]], dtype='float')
        if self._has_keypoints(): #array of opencv KeyPoint class instances
            for point in self.keypoints:
                temp = _np.ndarray([[point.pt[0], point.pt[1], point.size, point.angle, point.response, point.octave, point.class_id]])
                k = _np.append(k, temp, 0)

        super().write(k, d)
        return
    

    def read(self):
        '''read keypoints from file and
        convert them to their native cv2
        keypoint type
        '''
        nd_kp, self.descriptors = super().read()

        kp_list = []
        for k in nd_kp:
            KP = _cv2.KeyPoint(x=k[0], y=k[1], _size=k[2], _angle=k[3], _response=k[4], _octave=k[5], _class_id=k[6])
            kp_list.append(KP)
        
        self.keypoints = kp_list



class OpenCV_ORB(_OpenCVDetector):
    '''create an opencv ORB detector

    Note that ORB options should be set
    by accessing Detector
    '''
    kwargs = {'nfeatures':500, 'scaleFactor':1.2, 'nlevels':8, 'edgeThreshold':31, 'firstLevel':0, 'WTA_K':2, 'scoreType':_cv2.ORB_HARRIS_SCORE, 'patchSize':31, 'fastThreshold':20}
    #http://docs.opencv.org/3.1.0/db/d95/classcv_1_1ORB.html
    Detector = _cv2.ORB_create(**kwargs)

    def __init__(self, output_folder, load_as_RGB=False):
        super().__init__(output_folder, OpenCV_ORB._Detector, eFeatureDetectorType.cvORB, load_as_RGB=False, load_as_grey=True)
    
    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class OpenCV_SIFT(_OpenCVDetector):
    '''create an opencv SIFT detector

    Note that SIFT options should be set
    by accessing Detector
    '''
    kwargs = {'nfeatures':500, 'nOctaveLayers':3, 'contrastThreshold':0.04, 'edgeThreshold':10, 'sigma':1.6}
    Detector = _cv2.xfeatures2d.SIFT_create(**kwargs)
    

    def __init__(self, output_folder, load_as_RGB=False):
        super().__init__(output_folder, OpenCV_SIFT._Detector, eFeatureDetectorType.cvSIFT, load_as_RGB=False, load_as_grey=True)

    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)


class OpenCV_DenseSIFT(_OpenCVDetector):
    '''Dense SIFT Detector'''
    kwargs = {'nfeatures':500, 'nOctaveLayers':3, 'contrastThreshold':0.04, 'edgeThreshold':10, 'sigma':1.6}
    Detector = _cv2.xfeatures2d.SIFT_create(**kwargs)
    

    def __init__(self, output_folder, load_as_RGB=False,
                initFeatureScale=1.,
                featureScaleLevels=1, 
                featureScaleMul=0.1,
                initXyStep=6,
                initImgBound=0, 
                varyXyStepWithScale=True,
                varyImgBoundWithScale=False
                ):

        self.initFeatureScale = initFeatureScale,
        self.featureScaleLevels = featureScaleLevels, 
        self.featureScaleMul = featureScaleMul,
        self.initXyStep = initXyStep,
        self.initImgBound = initImgBound, 
        self.varyXyStepWithScale = varyXyStepWithScale,
        self.varyImgBoundWithScale = varyImgBoundWithScale

        super().__init__(output_folder, Detector, eFeatureDetectorType.cvSIFT, load_as_RGB=False, load_as_grey=True)


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
        super().__init__(output_folder, OpenCV_FAST._Detector, eFeatureDetectorType.cvFAST, load_as_RGB=False, load_as_grey=True)


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
        super().__init__(output_folder, OpenCV_SURF._Detector, eFeatureDetectorType.cvSURF, load_as_RGB=False, load_as_grey=True)


    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)

    

class OpenCV_HOG(_OpenCVDetector):
    '''HOG Detector using opencv
     This detector does not accept named arguments.
     args order is:
        winSize, blockSize, blockStride,
        cellSize, nbins, derivAperture
        winSigma histogramNormType,
        L2HysThreshold, gammaCorrection,
        nlevels
    '''
    args = [(64, 64), (16, 16), (8, 8), (8, 8), 9, 1, 4., 0, 2.0000000000000001e-01, 0, 64]
    Detector = _cv2.HOGDescriptor(args)


    def __init__(self, output_folder):
        OpenCV_HOG.Detector.cellSize = (OpenCV_HOG.kwargs['cellSize'])
        super().__init__(output_folder, OpenCV_HOG._Detector, eFeatureDetectorType.cvHOG, load_as_RGB=False, load_as_grey=True)


    def __call__(self, img, mask=None, extract=False):
        super().__call__(img, mask, extract)



class skHOGDetector(_BaseDetector):
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
        super().__init__(output_folder, eFeatureDetectorType.skHOG, load_as_RGB=False, load_as_grey=True)

    
    def __call__(self, img, imgpath, mask=None, extract=False, load_keypoint_visual=False):
        self._load_keypoint_visual = load_keypoint_visual
        super().__call__(img, imgpath, mask)
        if extract:
            self.extract_descriptors()


    def view(self, dump=False, show=True, show_original=True):
        super().view(dump, show, show_original)


    def extract_descriptors(self):
        super().extract_descriptors() #loads image
        
        if self._load_keypoint_visual:
            fd, hog_image = _skfeature.hog(self._img, visualise=True, *skHOGDetector.args, **skHOGDetector.kwargs)
            self._img_descriptors = _opencvlib.transforms.rescale_intensity(hog_image, in_range=(0, 0.02))
        else:
            self._img_descriptors = None
            fd, hog_image = _skfeature.hog(self._img, visualise=False, *skHOGDetector.args, **skHOGDetector.kwargs)
            
        self.descriptors = fd
        self.keypoints = None


    def extract_keypoints(self):
        self.extract_descriptors()

    def read(self):
        self.keypoints, self.descriptors = super().read()

    def write(self):
        super().write(self.keypoints, self.descriptors)



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



def prints(s, log=True):
    '''silent print'''
    if not SILENT:
        print(s)
    if log:
        _Log.info(s)
#endregion



#region ENTRY
def main():
    '''execute if script was entry point'''
    D = OpenCV_DenseSIFT('C:/temp/img')
    D('C:/temp/DSCF8249.JPG')
    D.extract_keypoints()
    
    
    
#This only executes if this script was the entry point
if __name__ == '__main__':
    #execute my code
    main()
#endregion
