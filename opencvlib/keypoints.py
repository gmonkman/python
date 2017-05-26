# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''keypoint helpers'''
import copy
import numpy as _np
import cv2 as _cv2


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

    for ind, kp in reversed(list(enumerate(keypoints))):
        if mask[int(kp.pt[1]), int(kp.pt[0])] != _np.nan and mask[int(kp.pt[1]), int(kp.pt[0])] != False and mask[int(kp.pt[1]), int(kp.pt[0])] != 0: #ie we want to keep it
            pass
        else:
            del keypoints[ind]
    return


def equal(kp1, kp2):
    return kp1.angle == kp2.angle and kp1.octave == kp2.octave and kp1.pt == kp2.pt and kp1.size == kp2.size