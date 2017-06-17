# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, protected-access
'''
Feature matching
'''
from enum import Enum as _Enum
import numpy as _np
import cv2 as _cv2

#import common as _common
#import opencvlib.keypoints as _keypoints
import opencvlib.features as _features


class eMatcherType(_Enum):
    '''matcher type'''
    BruteForce = 0    
    FLANN = 1


class eFLANN_OPT(_Enum):
    '''flan enum'''
    FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
    FLANN_INDEX_LSH = 6



class _BaseMatcher():
    '''base matcher from which
    new matchers should inherit
    '''

    def __init__(self, Matcher, MatcherType, refFeature=None, targFeature=None):
        '''(Class:Features._BaseDetector, Class:Features._BaseDetector, 
                Class:cv::DescriptorMatcher, features.eFeatureDetectorType)
        '''
        assert isinstance(targFeature, _features._BaseDetector)
        self._Matcher = Matcher
        self._refFeature = refFeature
        self._targFeature = targFeature
        self._eMatcherType = MatcherType
        self.homo, self.homo_status = None, None
        self.img_match = None #hold the match visualisation
        self._p1, self._p2, self._kp_pairs = None, None, None


    def __call__(self, refFeature, targFeature):
        '''
        call
        '''
        self._refFeature = refFeature
        self._targFeature = targFeature
        self.homo, self.homo_status = None, None
        self.img_match = None #hold the match visualisation
        self._kp_pairs = None


    def _filter_matches(self, ratio=0.75):
        '''(float) -> ndarray, ndarray, list:ndarray
        Filter matched points according to the
        magnitude of the distance measure.
        '''
        mkp1, mkp2 = [], []
        for m in self._matches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append(self.refFeature.keypoints[m.queryIdx])
                mkp2.append(self.targFeature.keypoints[m.trainIdx])
        self._p1 = _np.float32([kp.pt for kp in mkp1])
        self._p2 = _np.float32([kp.pt for kp in mkp2])
        self._kp_pairs = list(zip(mkp1, mkp2))


    def explore_match(self):
        '''produce match image
        '''
        h1, w1 = self.refFeature._img.shape[:2]
        h2, w2 = self.targFeature._img.shape[:2]
        vis = _np.zeros((max(h1, h2), w1 + w2), _np.uint8)
        vis[:h1, :w1] = self.refFeature._img
        vis[:h2, w1:w1 + w2] = self.targFeature._img
        vis = _cv2.cvtColor(vis, _cv2.COLOR_GRAY2BGR)

        if self.homo is not None:
            corners = _np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
            corners = _np.int32(_cv2.perspectiveTransform(
                corners.reshape(1, -1, 2), self.homo).reshape(-1, 2) + (w1, 0))
            _cv2.polylines(vis, [corners], True, (255, 255, 255))

        if self.homo_status is None:
            self.homo_status = _np.ones(len(self._kp_pairs), _np.bool_)
        self._p1, self._p2 = [], []  # python 2 / python 3 change of zip unpacking

        for kpp in self._kp_pairs:
            self._p1.append(_np.int32(kpp[0].pt))
            self._p2.append(_np.int32(_np.array(kpp[1].pt) + [w1, 0]))

        green = (0, 255, 0)
        red = (0, 0, 255)

        for (x1, y1), (x2, y2), inlier in zip(self._p1, self._p2, self.homo_status):
            if inlier:
                col = green
                _cv2.circle(vis, (x1, y1), 2, col, -1)
                _cv2.circle(vis, (x2, y2), 2, col, -1)
            else:
                col = red
                r = 2
                thickness = 3
                _cv2.line(vis, (x1 - r, y1 - r), (x1 + r, y1 + r), col, thickness)
                _cv2.line(vis, (x1 - r, y1 + r), (x1 + r, y1 - r), col, thickness)
                _cv2.line(vis, (x2 - r, y2 - r), (x2 + r, y2 + r), col, thickness)
                _cv2.line(vis, (x2 - r, y2 + r), (x2 + r, y2 - r), col, thickness)

        for (x1, y1), (x2, y2), inlier in zip(self._p1, self._p2, self.homo_status):
            if inlier:
                _cv2.line(vis, (x1, y1), (x2, y2), green)
        
        self.img_match = vis

    
    def _match(self, filter_ratio=0.75):
        '''(float) -> void
        do the match

        filter_ratio:
            parameter defining the nearness of
            points to retain, passed to
        '''
        raw_matches = self._Matcher.knnMatch(self._refFeature.descriptors, trainDescriptors=self._targFeature.descriptors, k=2)  # 2
        self._p1, self._p2, self._kp_pairs = self._filter_matches(ratio=filter_ratio)
        if len(self._p1) >= 4:
            self.homo, self.homo_status = _cv2.findHomography(self._p1, self._p2, _cv2.RANSAC, 5.0)
            print('%d / %d  inliers/matched' % (_np.sum(self.homo_status), len(self.homo_status)))
        else:
            self.homo, self.homo_status = None, None
            print('%d self._matches found, not enough for homography estimation' % len(self._p1))

    


class FLANNMatcher(_BaseMatcher):
    '''FLANN Matcher'''
    def __init__(self, refFeature=None, targFeature=None):
               
        if refFeature.get_matcher_dist_enum == _cv2.NORM_L2:
            flann_params = dict(algorithm=eFLANN_OPT.FLANN_INDEX_KDTREE, trees=5)
        else:
            flann_params = dict(algorithm=eFLANN_OPT.FLANN_INDEX_LSH,
                                table_number=6,  # 12
                                key_size=12,     # 20
                                multi_probe_level=1)  # 2
            
        Matcher = _cv2.FlannBasedMatcher(flann_params, {}) # bug : need to pass empty dict (#1329)

        super().__init__(Matcher, eMatcherType.FLANN, refFeature, targFeature)

    
class BruteForceMatcher(_BaseMatcher):
    '''BF matcher
    '''
    def __init__(self, refFeature=None, targFeature=None):
        Matcher = _cv2.BFMatcher(refFeature.get_matcher_dist_enum)
        super().__init__(Matcher, eMatcherType.BruteForce, refFeature, targFeature, )
