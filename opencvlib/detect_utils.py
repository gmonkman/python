# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''utils for detections'''

import opencvlib.roi as _roi
import opencvlib.geom as _geom

def iou(gt, det):
    '''(2-list, 2-list) -> float

    Get the iou stat from groundtruth rectangle and
    detection rectangle.

    Rects are CVXY points.

    gt:
        groundtruth rectangle points.
    det:
        detection rectangle points.

    Example:
    >>> iou()
    '''

    _roi.rects_intersect(gt, det)

