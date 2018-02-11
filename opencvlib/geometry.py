# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''working with opencv shapes'''
import math as _math

import numpy as _np

import funclib.baselib as _baselib
import opencvlib.distance as _dist


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
    return _np.rad2deg((ang1 - ang2) % (2 * _np.pi))


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
