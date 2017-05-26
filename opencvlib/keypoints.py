# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''keypoint helpers'''
import copy
import numpy as _np
import cv2 as _cv2



def applymask(keypoints, mask):
    '''(list:cv2.keypoint, ndarray) -> ndarray
    
    Removes keypoints from a keypoint list according to the mask.

    Leave the keypoints intact, and returns a copy with 
    masked keypoints removed.

    keypoints:
        list:cv2.KeyPoints

    mask:
        ndarray. False, -1 and np.nan are mask values

    Returns:
        list:cv2.KeyPoints
    '''
    kps = copy.deepcopy(keypoints)
    assert isinstance(kps, list)
    if mask is None:
        return kps

    for ind, kp in reversed(list(enumerate(keypoints))):
        assert isinstance(kp, _cv2.KeyPoint)
        if mask[kp.pt[1], kp.pt[0], ...] != _np.nan and mask[kp.pt[1], kp.pt[0], ...] != False and mask[kp.pt[1], kp.pt[0], ...] != 0: #ie we want to keep it
            pass
        else:
            del kps[ind]
    return kps
