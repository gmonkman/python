# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, protected-access, unused-import
'''
Feature matching
'''
from enum import Enum as _Enum
import numpy as _np
import cv2 as _cv2

#import common as _common
from opencvlib.keypoints import printkp as _printkp

_SILENT = False

class eMatcherType(_Enum):
    '''matcher type'''
    BruteForce = 0    
    FLANN = 1


class eFLANN_OPT(_Enum):
    '''flan enum'''
    FLANN_INDEX_KDTREE = 1
    FLANN_INDEX_LSH = 6
    


class _BaseMatcher():
    '''base matcher from which
    new matchers should inherit
    '''

    def __init__(self, Matcher, MatcherType, refFeature, targFeature, filter_match_ratio=0.75, run_match=True):
        '''(Class:cv2::DescriptorMatcher, features.eFeatureDetectorType,
            Class:Features._BaseDetector, Class:Features._BaseDetector)->void

        Matcher:
                a cv2 matcher class
        MatchType:
            Enumeration eMatcherType, defining the matcher type.
            Primarily for information at the moment as the
            inheriting class provides the match specific logic
        refFeature, targFeature:
            Instances of feature detectors with calculated
            features
        run_match:
            If false, the match is not executed
            
        
        Returns: void
        '''
        self._Matcher = Matcher
        self._refFeature = refFeature #Instance inheriting from Class:Features._BaseDetector
        self._targFeature = targFeature  #Instance inheriting from Class:Features._BaseDetector
        self._eMatcherType = MatcherType
        self.homo, self.homo_status = None, None
        self.img_match = None #hold the match visualisation
        self._p1, self._p2, self._kp_pairs = None, None, None
        self._img_match_viz = None #holds visualization of the match
        self._filter_match_ratio = filter_match_ratio
        self.matches = None
        self.matches_filtered = None
        if run_match:
            self._match()


    def __call__(self, refFeature=None, targFeature=None):
        '''(Class:Features._BaseDetector, Class:Features._BaseDetector)->void

        refFeature, targFeature:
            Instances of feature detectors with calculated
            features. Allow None if features were populated
            on init

        Returns: void
        '''
        
        if not refFeature is None:
            self._refFeature = refFeature
        if not targFeature is None:
            self._targFeature = targFeature

        self.homo, self.homo_status = None, None
        self.img_match = None #hold the match visualisation
        self._p1, self._p2, self._kp_pairs = None, None, None
        self._img_match_viz = None #holds visualization of the match
        self.matches = None
        self.matches_filtered = None
        self._match()

    
    @property
    def inlier_nr(self):
        '''() -> int
        number of inliers'''
        return _np.sum(self.homo_status) if isinstance(self.homo_status, _np.ndarray) else 0

    @property
    def match_points_nr(self):
        '''() -> int
        nr of matched points
        '''
        return len(self.homo_status) if isinstance(self.homo_status, _np.ndarray) else 0

    @property
    def filter_match_ratio(self):
        '''filter_match_ratio getter'''
        return self._filter_match_ratio
    @filter_match_ratio.setter   
    def filter_match_ratio(self, filter_match_ratio):
        '''filter_match_ratio setter'''
        self._filter_match_ratio = filter_match_ratio



    def _filter_matches(self):
        '''(float) -> ndarray, ndarray, list:ndarray
        Filter matched points according to the
        magnitude of the distance measure.
        '''
        mkp1, mkp2 = [], []
        for m in self.matches:
            if self.filter_match_ratio != 0:
                if len(m) == 2 and m[0].distance < m[1].distance * self.filter_match_ratio:
                    m = m[0]
                    mkp1.append(self._refFeature.keypoints[m.queryIdx])
                    mkp2.append(self._targFeature.keypoints[m.trainIdx])
            else:
                m = m[0]
                mkp1.append(self._refFeature.keypoints[m.queryIdx])
                mkp2.append(self._targFeature.keypoints[m.trainIdx])
        
        self._p1 = _np.float32([kp.pt for kp in mkp1]) #simple 2:tuple points, _p1, _p2 are matched by index
        self._p2 = _np.float32([kp.pt for kp in mkp2])
        self._kp_pairs = list(zip(mkp1, mkp2))


    def get_match_viz(self, force_calculate=False):
        '''(bool) -> ndarray
        Produce match image visualization

        force_calculate:
            Recalculate even if a preexisting visualization
            exists in _img_match_viz
        '''

        if isinstance(self._img_match_viz, _np.ndarray) and not force_calculate:
            return self._img_match_viz

        h1, w1 = self._refFeature._img.shape[:2]
        h2, w2 = self._targFeature._img.shape[:2]

        vis = _np.zeros((max(h1, h2), w1 + w2), _np.uint8)

        vis[:h1, :w1] = self._refFeature._img
        vis[:h2, w1:w1 + w2] = self._targFeature._img
        vis = _cv2.cvtColor(vis, _cv2.COLOR_GRAY2BGR)

        if self.homo is not None:
            corners = _np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
            corners = _np.int32(_cv2.perspectiveTransform(
                corners.reshape(1, -1, 2), self.homo).reshape(-1, 2) + (w1, 0))
            _cv2.polylines(vis, [corners], True, (255, 255, 255))

        if self.homo_status is None:
            self.homo_status = _np.ones(len(self._kp_pairs), _np.bool_)
        p1, p2 = [], []
        for kpp in self._kp_pairs:
            p1.append(_np.int32(kpp[0].pt))
            p2.append(_np.int32(_np.array(kpp[1].pt) + [w1, 0]))

        green, red = (0, 255, 0), (0, 0, 255)

        for (x1, y1), (x2, y2), inlier in zip(p1, p2, self.homo_status):
            if inlier:
                col = green
                _cv2.circle(vis, (x1, y1), 2, col, -1)
                _cv2.circle(vis, (x2, y2), 2, col, -1)
            else:
                col, r, thickness = red, 2, 3
                _cv2.line(vis, (x1 - r, y1 - r), (x1 + r, y1 + r), col, thickness)
                _cv2.line(vis, (x1 - r, y1 + r), (x1 + r, y1 - r), col, thickness)
                _cv2.line(vis, (x2 - r, y2 - r), (x2 + r, y2 + r), col, thickness)
                _cv2.line(vis, (x2 - r, y2 + r), (x2 + r, y2 - r), col, thickness)

        for (x1, y1), (x2, y2), inlier in zip(p1, p2, self.homo_status):
            if inlier:
                _cv2.line(vis, (x1, y1), (x2, y2), green)
        
        self._img_match_viz = vis
        return vis        

    
    def _match(self):
        '''(float) -> void
        do the match

        filter_ratio:
            parameter defining the nearness of
            points to retain, passed to
        '''
        self.matches = self._Matcher.knnMatch(self._refFeature.descriptors, trainDescriptors=self._targFeature.descriptors, k=2)  # 2
        self._filter_matches() #discard paired points above a certain distance threshold away from each other
        if len(self._p1) >= 4:
            self.homo, self.homo_status = _cv2.findHomography(self._p1, self._p2, _cv2.RANSAC, 5.0)
            if not _SILENT:
                print('%d / %d  inliers/matched' % (self.inlier_nr, self.match_points_nr))
        else:
            self.homo, self.homo_status = None, None
            if not _SILENT:
                print('%d matches found, not enough for homography estimation' % len(self._p1))

    


class FLANNMatcher(_BaseMatcher):
    '''FLANN Matcher

    Initialise with feature classes from features.py.
    
    Feature instances neednt have valid descriptors for
    initalisation.
    
    The matcher will assess best matches based on descriptors
    calculated in feature instances.

    Example initialisation:
        firstSIFT, curSIFT = features.OpenCV_SIFT(), features.OpenCV_SIFT()
        M = matcher.BruteForceMatcher(firstSIFT, curSIFT)
    '''
    def __init__(self, refFeature, targFeature, run_match=True, filter_match_ratio=0.75):
               
        if refFeature.get_matcher_dist_enum == _cv2.NORM_L2:
            flann_params = dict(algorithm=eFLANN_OPT.FLANN_INDEX_KDTREE, trees=5)
        else:
            flann_params = dict(algorithm=eFLANN_OPT.FLANN_INDEX_LSH,
                                table_number=6,  # 12
                                key_size=12,     # 20
                                multi_probe_level=1)  # 2
            
        Matcher = _cv2.FlannBasedMatcher(flann_params, {}) # bug : need to pass empty dict (#1329)

        super().__init__(Matcher, eMatcherType.FLANN, refFeature, targFeature, run_match=run_match, filter_match_ratio=filter_match_ratio)

    
class BruteForceMatcher(_BaseMatcher):
    '''Bruteforce matcher, 

    Initialise with feature classes from features.py
    
    The matcher will assess best matches based on descriptors
    calculated in feature instances.

    Example initialisation:
        firstSIFT, curSIFT = features.OpenCV_SIFT(), features.OpenCV_SIFT()
        M = matcher.BruteForceMatcher(firstSIFT, curSIFT)
    '''

    def __init__(self, refFeature, targFeature, run_match=True, filter_match_ratio=0.75):
        Matcher = _cv2.BFMatcher(refFeature.get_matcher_dist_enum())
        super().__init__(Matcher, eMatcherType.BruteForce, refFeature, targFeature, run_match=run_match, filter_match_ratio=filter_match_ratio)



def printm(match):
    '''cv2::DMatch-> void

    Print a match object to console
    #http://docs.opencv.org/master/d4/de0/classcv_1_1DMatch.html
    '''
   # if not isinstance(match, _cv2.DMatch):
      #  return ''

    #assert isinstance(match, _cv2.DMatch)
    
    s = 'distance {0!r}\n'.format(match.distance) + \
        'imgIdx {0!r}\n'.format(match.imgIdx) + \
        'queryIdx {0!r}\n'.format(match.queryIdx) + \
        'trainIdx {0!r}\n'.format(match.trainIdx)
    
    print(s)
    