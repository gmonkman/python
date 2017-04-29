# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''related to getting regions of interest
from an image.

Includes some geometry related functions for shapes
'''
from random import randint

import cv2
import numpy as np
from numpy import ma

from opencvlib.decs import decgetimg
from opencvlib import ImageInfo

__all__ = ['sample_rect', 'poly_area', 'roi_polygons_get', 'to_rect', 'rect_as_points',
           'bounding_rect_as_points', 'bounding_ellipse_as_points', 'rect2rect_mtx',
           'rects_intersect']

@decgetimg
def sample_rect(img, w, h):
    '''(str|ndarray,int,int,int,int)->ndarray|None
    Return a retangle of an image as an ndarray
    randomly chosen from the original image.

    ndarray or the path to an image can be used.

    Returns None if the image is smaller than the area
    '''
    # if isinstance(img, str):
    #   img = cv2.imread(path.normpath(img) , -1)

    img_w, img_h = ImageInfo.getsize(img)
    if img_w < w or img_h < h:
        return None

    rnd_col = randint(0, img_w - w)  # 0 index
    rnd_row = randint(0, img_h - h)

    return img[rnd_row:rnd_row + h, rnd_col:rnd_col + w, ::-1]


def poly_area(pts=None, x=None, y=None):
    '''(list, list, list)->float
    If points are in two matched lists, use x= and y=
    Else if you have an array of points, use pts=

    eg. x=[1,2,3,4], y=[5,6,7,8]
    or pts=[(1,5),(2,6),(3,7),(4,8)]
    '''
    if pts:
        x = [pt[0] for pt in pts]
        y = [pt[1] for pt in pts]

    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


@decgetimg
def roi_polygons_get(img, points):
    '''(ndarray or path, [tuple list|ndarray])->ndarray, ndarray, ndarray
    Points are a tuple list e.g. [(0,0), (50,0), (0,50), (50,50)]

    Returns 3 ndarrays
    [0] White pixels for the bounding polygon
    [1] A numpy masked array where pixels outside the polygon are masked (False)
    [2] The original image inside the polygon, with black pixels outside the polygon
    '''

    # mask defaulting to black for 3-channel and transparent for 4-channel
    # (of course replace corners with yours)
    white_mask = np.zeros(img.shape, dtype=np.uint8)
    if isinstance(points, np.ndarray):
        roi_corners = cv2.convexHull(points)
    else:
        roi_corners = cv2.convexHull(np.array([points], dtype=np.int32))

    roi_corners = np.squeeze(roi_corners)

    channel_count = img.shape[2]  # i.e.  3 or 4 depending on your image
    ignore_mask_color = (255,) * channel_count
    cv2.fillConvexPoly(white_mask, roi_corners, ignore_mask_color)

    mask = ma.masked_values(white_mask, 0)

    return white_mask, mask, cv2.bitwise_and(img, white_mask)


def to_rect(a):
    '''(arraylike)->nparray of type float64
    Takes a point [1,2] and returns
    a rectangle sized according to the
    origin [0,0] and the point.

    eg a=[2,3] returns
    [[0,0]
     [2,3]]
    '''
    a = np.ravel(a)
    if len(a) == 2:
        a = (0, 0, a[0], a[1])
    return np.array(a, np.float64).reshape(2, 2)


def rect_as_points(rw, col, w, h):
    '''(int,int,int,int)->list
    Given a rectangle specified by the top left point
    and width and height, convert to a list of points

    Note opencv points have origin in top left and are (x,y) ie col,row (width,height). Not the matrix standard.
    '''
    return [(col, rw), (col, rw + h), (col + w, rw), (col + w, rw + h)]

#DEBUG bounding_rect_of_poly
def bounding_rect_of_poly(points):
    '''(list|ndarray)->list
    Return points of a bounding rectangle in opencv point format.

    Returns corner points ([[x,y],[x+w,y],[x,y+h],[x+w,y+h]]
    and *not* top left point with width and height (ie x,y,w,h).
    Note opencv points have origin in top left
    and are (x,y) i.e. col,row (width,height). Not the matrix standard.
    '''
    x, y, w, h = cv2.boundingRect(points)
    return rect_as_points(x, y, w, h)


#DEBUG bounding_rect_of_ellipse
def bounding_rect_of_ellipse(centre_point, rx, ry):
    '''(list|tuple,int,int)->list
    center_point: x,y  ie. col,row
    Return points of a bounding rectangle in opencv point format.

    For circle, pass in the radius twice.

    Returns corner points ([[x,y],[x+w,y],[x,y+h],[x+w,y+h]]
    and *not* top left point with width and height (ie x,y,w,h).
    Note opencv points have origin in top left
    and are (x,y) i.e. col,row (width,height). Not the matrix standard.
    '''
    x, y = centre_point
    # DEBUG Check outputs of bounding_ellipse_as_points
    return [[x - rx, y - ry], [x + rx, y - ry], [x - rx, y + ry], [x + rx, y + ry]]


def rect2rect_mtx(src, dst):
    '''no idea what this does!'''
    src, dst = to_rect(src), to_rect(dst)
    cx, cy = (dst[1] - dst[0]) / (src[1] - src[0])
    tx, ty = dst[0] - src[0] * (cx, cy)
    M = np.float64([[cx, 0, tx], [0, cy, ty], [0, 0, 1]])
    return M

def rects_intersect(rect1, rect2):
    '''
    Function to calculate overlapping areas
    `detection_1` and `detection_2` are 2 detections whose area
    of overlap needs to be found out.
    Each detection is list in the format ->
    [x-top-left, y-top-left, confidence-of-detections, width-of-detection, height-of-detection]
    The function returns a value between 0 and 1,
    which represents the area of overlap.
    0 is no overlap and 1 is complete overlap.
    Area calculated from ->
    http://math.stackexchange.com/questions/99565/simplest-way-to-calculate-the-intersect-area-of-two-rectangles
    '''
    # Calculate the x-y co-ordinates of the
    # rectangles
    x1_tl = rect1[0]
    x2_tl = rect2[0]
    x1_br = rect1[0] + rect1[3]
    x2_br = rect2[0] + rect2[3]
    y1_tl = rect1[1]
    y2_tl = rect2[1]
    y1_br = rect1[1] + rect1[4]
    y2_br = rect2[1] + rect2[4]
    # Calculate the overlapping Area
    x_overlap = max(0, min(x1_br, x2_br) - max(x1_tl, x2_tl))
    y_overlap = max(0, min(y1_br, y2_br) - max(y1_tl, y2_tl))
    overlap_area = x_overlap * y_overlap
    area_1 = rect1[3] * rect2[4]
    area_2 = rect2[3] * rect2[4]
    total_area = area_1 + area_2 - overlap_area
    return overlap_area / float(total_area)


def nms_rects(detections, threshold=.5):
    '''
    This function performs Non-Maxima Suppression.
    `detections` consists of a list of detections.
    Each detection is in the format ->
    [x-top-left, y-top-left, confidence-of-detections, width-of-detection, height-of-detection]
    If the area of overlap is greater than the `threshold`,
    the area with the lower confidence score is removed.
    The output is a list of detections.
    '''
    if len(detections) == 0:
        return []
    # Sort the detections based on confidence score
    detections = sorted(detections, key=lambda detections: detections[2],
                        reverse=True)
    # Unique detections will be appended to this list
    new_detections = []
    # Append the first detection
    new_detections.append(detections[0])
    # Remove the detection from the original list
    del detections[0]
    # For each detection, calculate the overlapping area
    # and if area of overlap is less than the threshold set
    # for the detections in `new_detections`, append the
    # detection to `new_detections`.
    # In either case, remove the detection from `detections` list.
    for index, detection in enumerate(detections):
        for new_detection in new_detections:
            if rects_intersect(detection, new_detection) > threshold:
                del detections[index]
                break
        else:
            new_detections.append(detection)
            del detections[index]
    return new_detections