# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''working with opencv shapes'''
import math as _math

import numpy as _np
from numpy.random import uniform

import funclib.baselib as _baselib
import opencvlib.distance as _dist


def get_rnd_pts(range_=(-50, 50), n=10, dtype=_np.int):
    '''(2-tuple, 2-tuple, int, class:numpy.dtype) -> ndarray
    Returns an n x 2 ndarray of unique random points
    '''

    if isinstance(dtype, _np.int):
        range_ = (range_[0], range_[1] + 1)

    return _np.reshape(uniform(range_[0], range_[1], n*2), (n, 2)).astype(dtype)


def triangle_pt(pt1, pt2, ret_max_y_pt=True):
    '''(2-array, 2-array, bool)-> 2-list
    Given a line defined by pt1 and pt2, get the third point
    to make a right angled triangle.

    Coordinates are CVXY

    pt1:
        first line point
    pt2:
        second point
    ret_max_y_pt:
        return the point with the maximum y coordinate,
        otherwise returns the point with the minimum y coordinate

    returns:
        2-list, representing the third point
    '''
    assert len(pt1) == len(pt2) == 2, 'pt1 and pt2 should be 2 elements array likes.'
    y1 = pt1[1]
    y2 = pt2[1]
    x1 = pt1[0]
    x2 = pt2[0]

    pt3 = [x2, y1]
    pt4 = [x1, y2]

    if pt3[1] > pt4[1]:
        return pt3 if ret_max_y_pt else pt4

    return pt3 if not ret_max_y_pt else pt4


def angle_between_pts(pt1, pt2, as_degrees=True):
    '''(array, array, bool, bool) -> float
    Calculate the angle between two points
    '''
    ang1 = _np.arctan2(*pt1[::-1])
    ang2 = _np.arctan2(*pt2[::-1])
    if as_degrees:
        return _np.rad2deg((ang1 - ang2) % (2 * _np.pi))

    return (ang1 - ang2) % (2 * _np.pi)


def angle_min_rotation_to_x(angle, as_degrees=True):
    '''(float) -> float
    Get the minimum rotation to the x-axis from angle,
    where angle is the rotation to x axis, with negative
    being clockwise.

    angle:
        the angle, e.g -180 would be a line with coords ((0,0), (-1,0))
        this line would be parralel to the x-axis, rotating -180 would
        be incorrect in most circumstances, it should be rotated 0 degrees.

    Example:
    >>> angle_min_rotation_to_x(-45)
    -45
    >>> angle_min_rotation_to_x(-300)
    60 #anticlockwise
    >>> angle_min_rotation_to_x(-190)
    -10 #clockwise
    '''
    if -270 <= angle <= -90:
        a = 180 - abs(angle)
    elif angle == -360:
        a = 0
    elif -360 < angle < -270:
        a = 360 - abs(angle)
    else:
        a = angle

    if not as_degrees:
        a = _math.radians(a)

    return a




def length_petween_pts(pts, closed=False):
    '''(array, bool) -> float
    Length of lines defined by points

    pts:
        iterable, in format [[1,2], [3,4], ...]
    closed:
        include length between first and last point
    '''
    l = 0

    if len(pts) <= 1:
        return 0

    for i in range(0, len(pts) - 1):
        l += _dist.L1dist(pts[i], pts[i+1])

    if closed:
        l += _dist.L2dist(pts[0], pts[-1])
    return l


def rotation_angle(pt1, pt2, as_radians=False):
    '''(2-array, 2-array, bool) -> float
    Get the angle a line (defined by two points) needs
    to be rotated through to be parallel with the x-axis

    Intended to find the rotation required for a
    'standard' line has been found.

    Assumes CVXY frame

    pt1:
        first point
    pt2:
        second point
    as_radians:
        return as radians, not angle

    returns:
        the angle

    Notes:
    Transforms.rotate takes an angle, not radians. Although the
    frame is interpreted as standard xy, this works out as a
    negative anticlockwise rotation.
    '''
    max_y = triangle_pt(pt1, pt2)[1]
    pt = _baselib.list_flatten([x for x in [pt1, pt2] if x[1] == max_y])
    T = [x*-1 for x in pt] #get the translation needed to move pt to the origin
    pt_to_transform = pt1 if pt2 == pt else pt2 #get the other point of the line
    rad = _math.atan2(pt_to_transform[1] + T[1], pt_to_transform[0] + T[0]) #calculate the angle after translation to the origin
    return rad if as_radians else _math.degrees(rad)


def rotate_points(pts, angle, center=(0, 0)):
    '''(ndarray|list, float, 2-tuple|None) -> nx2-tuple
    Rotates a point "angle" degree around center.
    Negative angle is clockwise.

    pts:
        array like of len 2, eg [[1,2],[2,3], ...]
    angle:
        angle to rotate in degrees (e.g. -90)
    center:
        point around which to rotate, (x, y),
        if center is None, rotate about the
        center of the points

    Example:
    >>>rotate_points([[10,10],[20,20]], -45, center=(15,15))
    [(15.0, 7.9289321881345245), (15.0, 22.071067811865476)]
    '''
    out = []
    if not center:
        center = _np.mean(pts, axis=0)

    for _ in pts:
        out = [rotate_point(pt, angle, center) for pt in pts]
    return out


def rotate_point(pt, angle, center=(0, 0)):
    '''(2-array, float, 2-tuple) -> 2-tuple
    Rotates a point "angle" degree around center.
    Negative angle is clockwise.

    pt:
        array like of len 2, eg [1,2]
    angle:
        angle to rotate in degrees (e.g. -90)
    center:
        point around which to rotate, (x, y)
    '''
    angle = -1*angle #the angle as passed will be negative for clockwise, but this routine uses positive for clockwise - make it behave the same
    angle_rad = _math.radians(angle % 360)
    # Shift the point so that center_point becomes the origin
    new_pt = (pt[0] - center[0], pt[1] - center[1])
    new_pt = (new_pt[0] * _math.cos(angle_rad) - new_pt[1] * _math.sin(angle_rad),
                 new_pt[0] * _math.sin(angle_rad) + new_pt[1] * _math.cos(angle_rad))
    # Reverse the shifting we have done
    return (new_pt[0] + center[0], new_pt[1] + center[1])


def centroid(pts, dtype=_np.float):
    '''(ndarray|list|tuple) -> 2-list
    Get centroid of pts as 2-list

    pts:
        n x 2 list like

    Example:
    >>> centroid([[0,0],[10,10]])
    [5.0, 5.0]
    '''
    ndpts = _np.asarray(pts)
    mn = _np.mean(ndpts, axis=0)
    return mn.astype(dtype).tolist()


def valid_point_pairs(pts1, pts2):
    '''Build matched array of points
    Returns 2 arrays of points.

    If no points found, returns [],[]

    e.g.
    >>>x, y = build_matched([[None, 1], [10,20]], [[1, 1], [1,2]])
    >>>print(x)
    [[10,20]]
    >>>print(y)
    [[1,2]]
    '''
    pt1_out = []
    pt2_out = []
    for i in range(min([len(pts1), len(pts2)])):
        if not None in pts1[i] and not None in pts2[i]:
            pt1_out.append(pts1[i])
            pt2_out.append(pts2[i])
    return pt1_out, pt2_out


def points_rmsd(V, W):
    '''(ndarray|list|tuple, ndarray|list|tuple) -> float
    Calculates the Root mean square dev between
    two sets of n-dimensional points.

    V, M:
        array like representations of n-D points.
        Should ignore pairwise points where values are None
        or np.nan
    '''
    D = len(V[0])
    N = len(V)
    rmsd = 0.0
    for v, w in zip(V, W):
        v = _np.array(v).astype(_np.float)
        w = _np.array(w).astype(_np.float)
        if True in _np.isnan(v) or True in _np.isnan(w):
            continue
        rmsd += sum([(v[i] - w[i]) ** 2.0 for i in range(D)])

    return _np.sqrt(rmsd/N)



def order_points(p):
    '''(list|tuple|ndarray) -> list
    Sorts a list of points by their position.
    '''
    if isinstance(p, (list, tuple, set)):
        pts = _np.array(p)
    pts = pts.tolist()
    cent = (sum([p[0] for p in pts])/len(pts), sum([p[1] for p in pts])/len(pts))
    pts.sort(key=lambda p: _math.atan2(p[1] - cent[1], p[0] - cent[0]))
    return pts
