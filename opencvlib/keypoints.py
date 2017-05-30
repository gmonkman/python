# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''keypoint helpers
keypoint detection is handled in features.py'''
import numpy as _np
import cv2 as _cv2

from opencvlib import getimg as _getimg


def applymask(keypoints, mask):
    '''(list:cv2.keypoint, ndarray) -> void
    
    Removes keypoints the keypoints argument *byref*

    keypoints:
        list:cv2.KeyPoints
    mask:
        ndarray. False, -1 and np.nan are mask values
    '''
    if mask is None:
        return

    assert isinstance(mask, _np.ndarray)
    for ind, kp in reversed(list(enumerate(keypoints))):
        if mask[int(kp.pt[1]), int(kp.pt[0])] != _np.nan and mask[int(kp.pt[1]), int(kp.pt[0])] != False and mask[int(kp.pt[1]), int(kp.pt[0])] != 0: #ie we want to keep it
            pass
        else:
            del keypoints[ind]
    return



def equal(kp1, kp2, xy_only=False):
    '''(class:cv.KeyPoint, class:cv.KeyPoint, bool) -> bool
    test if two cv2.KeyPoints are equal

    xy_only:
        Only compare the point location
    '''
    if xy_only:
        return kp1.pt == kp2.pt
    else:
        return kp1.angle == kp2.angle and kp1.octave == kp2.octave and kp1.pt == kp2.pt and kp1.size == kp2.size



def printkp(kp, spacer='\n'):
    '''(cv2.KeyPoint)
    print keypoint details'''
    s = 'angle: {0!s}{6}' \
    'class_id: {1!s}{6}' \
    'octave: {2!s}{6}' \
    'pt(x,y): {3!s}{6}' \
    'response: {4!s}{6}' \
    'size {5!s}'.format(kp.angle, kp.class_id, kp.octave, kp.pt, kp.response, kp.size, spacer)
    print(s)



class DenseKeypoints():
    '''Get grid of dense keypoints over an image
    
    initFeatureScale
        Initial feature radius in pixels
    featureScaleLevels
        Number of scales overwhich we wish to make keypoints
    featureScaleMuliplier
        Scale adjustment for initFeatureScale over featureScaleLevels
    initXyStep
        moving window column step
    initImgBound
        row/col bounding region to ignore around the image (pixels)
    varyXyStepWithScale
        Boolean, do we change step with scale
    self.varyImgBoundWithScale
        Boolean, do we alter size of 'ignore' border with scale

    Example Usage:
        D = keypoints.DenseKeypoints(initFeatureScale=20)
        kps = D(img)
    '''

    def __init__(self,
                initFeatureScale=20.,
                featureScaleLevels=1, 
                featureScaleMultiplier=0.5,
                initXyStep=10,
                initImgBound=0, 
                varyXyStepWithScale=True,
                varyImgBoundWithScale=True
        ):
        ''' (float, int, float, int, int, bool, bool) -> void
        '''
        self.keypoints = None
        self.img = None
        self._mask = None
        self.initFeatureScale = initFeatureScale
        self.featureScaleLevels = featureScaleLevels
        self.featureScaleMultiplier = featureScaleMultiplier
        self.initXyStep = initXyStep
        self.initImgBound = initImgBound
        self.varyXyStepWithScale = varyXyStepWithScale
        self.varyImgBoundWithScale = varyImgBoundWithScale


    def __call__(self, img, mask=None):
        '''(ndarray|str, ndarray) -> ndarray
        Set keypoints for img.

        img:
            ndarray or filepath, if filepath then it is loaded to self.img
        mask:
            ndarray or None, if set, only True/Non zero region keypoints are returned


        Returns:
            ndarray of keypoints, also sets keypoints member
        '''
        self.img = _getimg(img)
        self._mask = mask
        self._set_dense_keypoints()
        return self.keypoints


    def _set_dense_keypoints(self):
        '''Calculate keypoints
        '''
        self.keypoints = []
        curScale = float(self.initFeatureScale)
        curStep = self.initXyStep
        curBound = self.initImgBound

        for dummy in range(self.featureScaleLevels):  #( int curLevel = 0 curLevel < featureScaleLevels curLevel++ )
            x = curBound
            y = curBound
            while x < self.img.shape[1] - curBound:
                while y < self.img.shape[0] - curBound:
                    self.keypoints.append(_cv2.KeyPoint(x, y, curScale))
                    y += curStep
                x += curStep
                y = curBound

            curScale = float(curScale * self.featureScaleMultiplier)

            if self.varyXyStepWithScale:
                curStep = int(curStep * self.featureScaleMultiplier + 0.5)

            if self.varyImgBoundWithScale:
                curBound = int(curBound * self.featureScaleMultiplier + 0.5)
        
        applymask(self.keypoints, self._mask) #byref call to check
