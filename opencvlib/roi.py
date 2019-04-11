# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-import
# no-self-use, unused-argument
'''related to getting regions of interest
from an image.

Includes some geometry related functions for shapes
'''
from random import randint as _randint
from enum import Enum as _enum

import cv2 as _cv2
import numpy as _np
from numpy import ma as _ma
import scipy.spatial.distance as _scipy_dist
import scipy.cluster.hierarchy as _scipy_heir
import scipy.ndimage as _ndimage

import opencvlib as _opencvlib
import opencvlib.info as _info
import opencvlib.distance as _dist
import opencvlib.geom as _geom
import opencvlib.color as _color
from opencvlib.histo import histo_rgb as _histo_rgb

import funclib.baselib as _baselib
from funclib.arraylib import np_round_extreme as _rnd
from opencvlib import getimg as _getimg


#as we may expect to find these here as well
from opencvlib.geom import bounding_rect_of_poly2, rect_as_points, flip_points





__all__ = ['bounding_rect_of_ellipse', 'bounding_rect_of_poly', 'poly_area',
           'rect2rect_mtx', 'rect_as_points', 'rects_intersect', 'roi_polygons_get',
           'sample_rect', 'to_rect']


class ePointConversion(_enum):
    '''Enumeration for point coversion between frames
    XYMinMaxtoCVXY is [xmin,xmax,ymin,ymax] to [[x,y], ...]
    '''
    XYtoRC = 0
    XYtoCVXY = 1
    RCtoXY = 2
    RCtoCVXY = 3
    CVXYtoXY = 4
    CVXYtoRC = 5
    XYMinMaxtoCVXY = 6 #[xmin,xmax,ymin,ymax]
    Unchanged = 99


class ePointsFormat(_enum):
    '''
    Output formats of points in an array

    XY:
        [[x1, y1], [x2, y2]]
    eForPolyLine:
        numpy array of shape (pts nr, 1, 2), used for plotting polylines
    XXXX_YYYY:
        [[x1, x2, x3, x4], [y1, y2, y3, y4]]
    minMax:
        [xmin, xmax, ymin, ymax]
    xywh:
        [xmin, ymin, w, h]
    rchw:
        [ymin, xmin, h, w]
    '''
    XY = 0
    ForPolyLine = 1
    XXXX_YYYY = 2 #[[x1, x2, x3, x4], [y1, y2, y3, y4]]
    XYWH = 3
    RCHW = 4
    XYXYXYXY = 5


class ePointFormat(_enum):
    '''Format of an individual point'''
    XY = 0
    CVXY = 1
    RC = 2


class Line():
    '''Holds a line
    Angles are from the y axis, which is 0 degrees

    Point formats are CVXY
    '''

    def __init__(self, pt1, pt2):
        '''(array, array)
        pt1 and pt2 are both 2-arrays, they should be
        in CVXY format (i.e. origin at top left, x-coord first)
        '''
        assert len(pt1) == len(pt2) == 2, 'pt1 and pt2 should be 2 elements array likes.'
        self.pt1 = pt1
        self.pt2 = pt2
        self.length = None
        self.angle_to_x = None
        self.angle_min_rotation_to_x = None #smallest rotation to make parallel to x axis
        self.midpoint = None
        self._refresh()


    def __call__(self, pt1, pt2):
        self.pt1 = pt1
        self.pt2 = pt2
        self._refresh()


    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)


    def _refresh(self):
        '''internal function to refresh
        length and angles
        '''
        self.length = _dist.L2dist(self.pt1, self.pt2)
        self.angle_to_x = _geom.rotation_angle(self.pt1, self.pt2)
        self.angle_min_rotation_to_x = _geom.angle_min_rotation_to_x(self.angle_to_x)
        self.midpoint = [(self.pt1[0] + self.pt2[0]) / 2, (self.pt1[1] + self.pt2[1]) / 2]


class Quadrilateral():
    '''represents a quadrilateral shape in opencv
    and provides support for rotations.

    The size of the image must be provided for
    proper rotation.

    Properties:
        lines: list of Line instances
        angle_to_origin:angle required to rotate shape to be parallel with origin
    '''

    def __init__(self, pts, frame_x, frame_y):
        '''(array, int, int)

        pts:
            array like of 4 points e.g. [[0,0],[10,0],[0,10],[10,10]]
        frame_x:
            image width
        frame_y:
            image height
        '''
        self._pts = pts
        self.lines = []
        self.angle_to_origin = None
        self._frame_x = frame_x
        self._frame_y = frame_y
        if pts:
            self._refresh()


    def __call__(self, pts, frame_x=None, frame_y=None):
        self._pts = pts
        if frame_x:
            self._frame_x = frame_x
        if frame_y:
            self._frame_y = frame_y
        self._refresh()


    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)


    def _refresh(self):
        assert len(self._pts) == 4, 'Expected 4 points, got %s.' % len(self._pts)
        for l in range(0, len(self._pts) - 1):
            self.lines.append(Line(self._pts[l], self._pts[l + 1]))
        self.lines.append(Line(self._pts[-1], self._pts[0])) #line joining first and last points
        self._angle()


    def _angle(self):
        '''() -> void
        calculates the angle to rotate the quadrilateral to
        make it parralel with the x axis, setting the class property
        angle_to_origin

        It doe this by finding the line joining the midpoint of the two shortest sides and
        and calculating the angle of this line to the x-axis using arctan.
        '''
        #get two shortest sides
        assert len(self.lines) == 4, 'Expected 4 line objects in quadrilateral object, have you initialised it properly?'
        dic = {i:ln.length for i, ln in enumerate(self.lines)}
        s = _baselib.dic_sort_by_val(dic)

        line1 = self.lines[s[0][0]]
        line2 = self.lines[s[1][0]]
        assert isinstance(line1, Line)
        assert isinstance(line2, Line)

        #get the angle from the two shortest sides as defined by their points
        self.angle_to_origin = _geom.rotation_angle(line1.midpoint, line2.midpoint)


    @property
    def rotated_to_x(self, as_int=True):
        '''(bool) -> array
        Returns the quadrilateral points, rotated so the
        shape is parralel with the origin along its long
        axis

        as_int:
            return points as integers,

        Returns:
            array of points in CVXY format
        '''
        ret = roi_rotate(self._pts, self.angle_to_origin, self._frame_x/2, self._frame_y/2)
        if as_int:
            ret = _rnd(ret)

        return ret


    @property
    def bounding_rectangle(self):
        '''() -> array

        return the bounding rectangle of the
        rotated_to_x quadrilateral

        Returns:
            array of points in CVXY format
        '''
        pts = self.rotated_to_x
        return bounding_rect_of_poly(pts)



def points_convert(pts, img_x, img_y, e_pt_cvt, e_out_format=ePointsFormat.XY):
    '''(array, 2:tuple, Enum:ePointConversion, Enum:ePointsFormat) -> list
    Converts points in one frame to another.
    XY:Standard cartesian coordinates, RC:Matrix coordinates,
    CVXY:OpenCV XY format which has the Y origin at the top of the image.

    Note that all points are assumed to be in a 0 index.


    pts:
       An array like of points, e.g. [[1,2], [2,3]],
       or [xmin,xmax,ymin,ymax] for XYMinMaxtoCVXY
    img_x:
        image width, e.g. 1024 in a 1024x768 image
    img_y:
        image height, e.g. 768 in a 1024x768 image
    e_pt_cvt:
        the enumeration ePointConversion defining the required conversion
    e_out_format:
        the format of the output points, see ePointsFormat, Note that this just
        the output form - the XY does not imply the order of the axis etc which
        is defined by Enum:ePointConversion.

    returns:
        list of points, [[1,2],[2,3]]
    '''
    #we are using 0 indicies
    img_x -= 1
    img_y -= 1

    out = []

    if e_out_format == ePointsFormat.XYXYXYXY: raise NotImplementedError

    if e_pt_cvt == ePointConversion.XYMinMaxtoCVXY: #e.g. of points in for this format (10, 50, 20, 30),  i.e. xmin,xmax,ymin,ymax
        out = [[pts[0], pts[2]], [pts[1], pts[2]], [pts[1], pts[3]], [pts[0], pts[3]]]
    else:
        for pt in pts:
            if e_pt_cvt == ePointConversion.XYtoRC:
                out.append([abs(pt[1] - img_y), pt[0]])
            elif e_pt_cvt == ePointConversion.XYtoCVXY:
                out.append([pt[0], abs(pt[1] - img_y)])
            elif e_pt_cvt == ePointConversion.RCtoXY:
                out.append([pt[1], abs(pt[0] - img_y)])
            elif e_pt_cvt == ePointConversion.RCtoCVXY:
                out.append([pt[1], pt[0]])
            elif e_pt_cvt == ePointConversion.CVXYtoXY:
                out.append([pt[0], abs(pt[1] - img_y)])
            elif e_pt_cvt == ePointConversion.CVXYtoRC:
                out.append([pt[1], pt[0]])
            elif e_pt_cvt == ePointConversion.Unchanged:
                pass
            else:
                raise ValueError('Unknown conversion enumeration for function argument e_pt_cvt, ensure the enum ePointConversion is used.')

    if e_out_format == ePointsFormat.ForPolyLine:
        poly_pts = _np.array(out, dtype='int32')
        return poly_pts.reshape((-1, 1, 2))
    elif e_out_format == ePointsFormat.XY:
        return out
    elif e_out_format == ePointsFormat.XXXX_YYYY:
        return list(zip(*out))
    elif e_out_format == ePointsFormat.XYWH:
        x, y = list(zip(*out))
        return (min(x), min(y), max(x) - min(x), max(y) - min(y))
    elif e_out_format == ePointsFormat.RCHW:
        c, r = list(zip(*out))
        return (min(r), min(c), max(r) - min(r), max(c) - min(c))
    else:
        raise ValueError('Unknown output format specified for function argument e_out_format')


def points_normalize(pts, h, w):
    '''(2-list, int|float, int|float)->2-list
    Normalize a list of pts
    pts: A list of pts, i.e. [[0,0],[10,10]]
    h: Image height (rows)
    w: Image width (cols)

    Returns:
        list of coverted points
    '''
    pts_ = list(pts)
    d = _baselib.depth(pts)
    if d == 1:
        pts_ = [pts]
    d = _baselib.depth(pts_)
    assert d == 2, 'Depth of pts should be 1 or 2. Got %s' % d
    out = [[pt[0]/w, pt[1]/h] for pt in pts_]
    return out


def points_denormalize(pts, h, w, asint=True):
    '''(2-list, int|float, int|float)->2-list
    Denormalize a list of pts
    pts: A list of pts, i.e. [[0,0],[10,10]]
    h: Image height (rows)
    w: Image width (cols)

    Returns:
        list of coverted points
    '''
    f = lambda x: int(round(x, 0)) if asint else x
    pts_ = list(pts)
    d = _baselib.depth(pts)
    if d == 1:
        pts_ = [pts]
    d = _baselib.depth(pts_)
    assert d == 2, 'Depth of pts should be 1 or 2. Got %s' % d
    out = [[f(pt[0] * w), f(pt[1] * h)] for pt in pts_]
    return out


def sample_rect(img, w, h):
    '''(str|ndarray,int,int,int,int)->ndarray|None
    Return a retangle of an image as an ndarray
    randomly chosen from the original image.

    ndarray or the path to an image can be used.

    Returns None if the image is smaller than the area
    '''
    # if isinstance(img, str):
    #   img = _cv2.imread(path.normpath(img) , -1)
    img = _getimg(img)
    img_w, img_h = _info.ImageInfo.getsize(img)
    if img_w < w or img_h < h:
        return None

    rnd_col = _randint(0, img_w - w)  # 0 index
    rnd_row = _randint(0, img_h - h)

    I = img[rnd_row:rnd_row + h, rnd_col:rnd_col + w]
    return I


def cropimg_xywh(img, x, y, w, h):
    '''(str|ndarray, int, int, int, int)->ndarray, bool
    Return a rectangular region from an image. Also see transforms.crop.

    Crops to the edge if area would be outside the
    bounds of the image.

    x, y:
        Define the point form which to crop, CVXY assumed
    w, h:
        Size of region

    Returns:
        cropped image area,
        boolean indicating if crop was truncated to border
        of the image

    Notes:
        transforms.crop provides conversion and cropping
        around a point
    '''
    assert isinstance(img, _np.ndarray)
    relu = lambda x: max(0, x)
    crop_truncated = (relu(y), min(y+h, img.shape[0]), relu(x), min(x+w, img.shape[1]))
    crop = (y, y+h, x, x+w)
    return img[relu(y):min(y+h, img.shape[0]), relu(x):min(x+w, img.shape[1])], crop_truncated == crop


def cropimg_minmax(img, xmin, ymin, xmax, ymax):
    pts = geom.order_points([[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]])
    return cropimg_pts(img, pts)


def cropimg_pts(img, corners):
    '''(str|ndarray, 4-list|tuple|ndarray) -> ndarray
    Return a rectangular region from an imag. Also see transforms.crop

    corners:
        List of 4 CVXY points of a rectangle.

    Returns:
        The image cropped to the rectangle

    Notes:
        transforms.crop provides conversion and cropping
        around a point
    '''
    assert isinstance(img, _np.ndarray)
    r, c, h, w = rect_as_rchw(corners)
    img_out, _ = cropimg_xywh(img, c, r, w, h)
    return img_out


def poly_area(pts=None, x=None, y=None):
    '''(list|ndarray|None, list|None, list|None) -> float
    Calculate area of a polygon defined by
    its vertices.

    Supports CVXY or XXXXYYYY format

    Example:
        >>>poly_area(x=[1,2,3,4], y=[5,6,7,8])
        >>>poly_area(pts=[(1,5),(2,6),(3,7),(4,8)])
    '''
    x = [pt[0] for pt in pts]
    y = [pt[1] for pt in pts]
    return 0.5 * _np.abs(_np.dot(x, _np.roll(y, 1)) - _np.dot(y, _np.roll(x, 1)))


def centroid(pts):
    '''(ndarray|list) -> 2-tuple
    Calculate the centroid of non-self-intersecting polygon.

    pts:
        Numeric array of points, e.g [[1,2],[10,12], ...]

    Returns:
        2-tuple of the centroid, e.g. (10, 15)
    '''
    return (sum([pt[0] for pt in pts]) / len(pts), sum([pt[1] for pt in pts]) / len(pts))


def roi_polygons_get(img, points):
    '''(ndarray or path, [tuple list|ndarray])->ndarray, ndarray, ndarray, ndarray
    Points are a tuple list e.g. [(0,0), (50,0), (0,50), (50,50)]

    Returns 3 ndarrays and a masked array
    [0] White pixels for the bounding polygon, cropped to a rectangle bounding the roi
    [1] A numpy masked array where pixels outside the roi are masked (False)
    [2] The original image inside the polygon, with black pixels outside the roi
    [3] The original image cropped to a rectangle bounding the roi
    '''

    # mask defaulting to black for 3-channel and transparent for 4-channel
    # (of course replace corners with yours)
    img = _getimg(img)
    white_mask = _np.zeros(img.shape, dtype=_np.uint8)

    roi_corners = _cv2.convexHull(_np.array([points], dtype=_np.int32))
    roi_corners = _np.squeeze(roi_corners)

    if _opencvlib.info.ImageInfo.typeinfo(img) & _opencvlib.info.eImgType.CHANNEL_1.value:
        channel_count = 1
    else:
        channel_count = img.shape[2]  # i.e.  3 or 4 depending on your image

    ignore_mask_color = (255,) * channel_count
    _cv2.fillConvexPoly(white_mask, roi_corners, ignore_mask_color)

    rect = bounding_rect_of_poly(_np.array([points], dtype=_np.int32), as_points=False) #x,y,w,h
    bitwise = _cv2.bitwise_and(img, white_mask)
    rectcrop, _ = cropimg_xywh(bitwise, *rect)
    white_mask_crop, _ = cropimg_xywh(white_mask, *rect)
    mask = _ma.masked_values(white_mask_crop, 0)

    return white_mask_crop, mask, bitwise, rectcrop


def polys_to_mask(img, polys, getcontours=True, cnt_mode=_cv2.RETR_EXTERNAL, cnt_method=_cv2.CHAIN_APPROX_SIMPLE, use_bounding_rect=False):
    '''(str|ndarray, list|ndarray, tuple|int, enum:ePointsFormat, bool, bool) -> ndarray, ndarray, tuple
    Create a mask (255 = Include, 0 = Exclude) from an n-4-2-array of polygons.

    img: path or ndarray image
    polys:a list or ndarray of polygons, each "row" represents a polygon, i.e. an n x 4 x 2 array|list
    getcontours: Also return contours (uses mask)
    cnt_mode, cnt_method: mode and method args for the contour function
    use_bounding_rect: Detected contours are first converted to their bounding rectangle
    Returns:
        mask (b&w image with shape=img.shape), contours, countour hierachy

    #Contour doc:https://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html?highlight=findcontours#findcontours
    '''
    img = _getimg(img)
    assert isinstance(img, _np.ndarray)

    #make maskbg a 3 deep array so we can
    #multiply each channel seperately
    mask = _np.zeros_like(img, dtype='uint8')
    polys_ = _np.array(polys, dtype='int32')

    #poly sould be an n x 4 x 2 array here
    for poly in polys_:
        poly = _np.array(poly, dtype='int32')
        if use_bounding_rect:
            poly = _np.array(bounding_rect_of_poly(poly.squeeze()), dtype='int32')
        mask = _cv2.fillPoly(mask, [poly], (255, 255, 255))

    if getcontours:
        cnt = _cv2.findContours(mask[:, :, 0:1], cnt_mode, cnt_method) #find contours requires a 1-channel image
    else:
        cnt = (None, None)
    #imgcountours = _cv2.drawContours(mask,cnt[0],-1,(0,255,0))
    return mask, cnt[0], cnt[1]



def get_image_from_mask(img, mask):
    '''(ndarray, ndarray)->ndarray
    Apply a white mask representing an roi
    to image.

    img and mask must be the same size,
    otherwise None is returned
    '''

    img = _getimg(img)
    if img.shape[0] != mask.shape[0] or img.shape[1] != mask.shape[1]:
        return None

    if len(img.shape) != len(mask.shape):
        if _info.ImageInfo.typeinfo(img) & _info.eImgType.CHANNEL_1.value: #1 channel image, need 1 channel mask
            mask = _cv2.cvtColor(mask, _cv2.COLOR_BGR2GRAY)
        elif _info.ImageInfo.typeinfo(img) & _info.eImgType.CHANNEL_3.value: #3 channel image, need 3 ch mask
            mask = _cv2.cvtColor(mask, _cv2.COLOR_GRAY2BGR)
        elif _info.ImageInfo.typeinfo(img) & _info.eImgType.CHANNEL_4.value:
            mask = _cv2.cvtColor(mask, _cv2.COLOR_GRAY2BGR)
            img = img[:, :, 0:3]
        else:
            assert 1 == 2 #looks like unexpected condition
            return None

    bitwise = _cv2.bitwise_and(img, mask)
    return bitwise


def roi_rescale(roi_pts, proportion=1.0, h=None, w=None):
    '''(ndarray|list|tuple, float, int|None, int|None) -> ndarray
    Grow or shrink an roi around the centre of
    the roi. CVXY is implied.

    roi_pts:
        Array of points [[0,0], [10,10] ....]
    h, w:
        Cap for the width and height, i.e. the roi will be set to h or w
        if it would h or w after rescaling. Lower cap of 0 is also applied.

    Returns:
        Array of rescaled points, eg.
        [[0,0], [10,10] ....]
    '''
    centre = centroid(roi_pts)
    pts = [[_get_limited_val(x, proportion, centre[0], w), _get_limited_val(y, proportion, centre[1], h)] for x, y in roi_pts]
    return pts


def _get_limited_val(v, proportion, centre, limit):
    '''(int|float, float, int|float, int|float|none) -> int
    getval, limted by 0 and limit
    '''
    g = lambda x: proportion * x + (1 - proportion) * centre
    out = int(g(v))
    if limit:
        if out < 0:
            return 0
        if out > limit:
            return limit
    return out


def roi_rescale2(roi_pts, proportion_x=1.0, proportion_y=1.0, h=None, w=None):
    '''(ndarray|list|tuple, float, float, int|None, int|None) -> ndarray
    Grow or shrink an roi around the centre of
    the roi. CVXY is implied.

    roi_pts:
        Array of points [[0,0], [10,10] ....]
    proportion_x, proportion_y:
        Proportion to grow width and height
    h, w:
        Cap for the width and height, i.e. the roi will be set to h or w
        if it would h or w after rescaling. Lower cap of 0 is also applied.
    Returns:
        Array of rescaled points, eg.
        [[0,0], [10,10] ....]
    '''
    centre = centroid(roi_pts)
    pts = [[_get_limited_val(x, proportion_x, centre[0], w), _get_limited_val(y, proportion_y, centre[1], h)] for x, y in roi_pts]
    return pts



def roi_resize(roi_pts, current, target):
    '''(ndarray|list|tuple, 2-tuple, 2-tuple, bool) -> ndarray

    Given an array like of 2d points, transform from the original
    image size to which they refer, to the new image size.

    **Note, this is to maintain the same selection when
    we resize the image, and will not grow the roi**

    roi_points in OpenCV XY frame, where y has origin at image row 0

    roi_pts:
        An array like (which is converted to a numpy array) of points
        in opencv xy format.
    current:
        size of 'image' which points are from, (w,h)
    target:
        size of image to project points on, (w,h)

    returns:
        numpy array of resized points

    comments:
        Use roi.points_convert prior to passing if your points
        are in an RC or cartesian frame.

    '''
    t_mat = _np.eye(2)
    t_mat[0, 0] = target[0]/current[0]
    t_mat[1, 1] = target[1]/current[1]

    return _np.array(_np.matrix(roi_pts) * _np.matrix(t_mat), dtype='uint8')


def roi_rotate(roi_pts, angle, frame_x, frame_y):
    '''(ndarray|list|tuple, float, int, int) -> ndarray
    Rotate an array of 2d points by angle.

    roi_points in OpenCV XY frame, where y has origin at image row 0

    host image size is necessary as rotation occurs around the image center
    and not the origin.

    roi_pts:
        An array like (which is converted to a numpy array) of points
        in opencv xy format.
    angle:
        angle of rotation, negative is clockwise
    frame_x:
        width of image frame
    frame_y:
        height of image frame

    returns:
        numpy array of resized points

    comments:
        Use roi.points_convert prior to passing if your points
        are in an RC or cartesian frame.
    '''
    pts = [_geom.rotate_point(pt, angle, (frame_x, frame_y)) for pt in roi_pts]
    return _np.array(pts)


def pts_reverse(pts):
    '''(ndarray|list|tuple) -> ndarray
    Takes an array of points and reverses it, this
    is effectively an xy to rc or vica versa conversion

    pts:
        listlike array of points

    returns
        ndarray of points, reversed.
    '''
    ndpts = _np.array(pts)
    assert isinstance(ndpts, _np.ndarray)
    assert len(ndpts[0]) == 2, 'Expected points to contain 2 numbers, not %s' % len(ndpts[0]) == 2
    return _np.flip(ndpts, 1)


def to_rect(a):
    '''(arraylike)->ndarray of type float64
    Takes a point [1,2] and returns
    a rectangle sized according to the
    origin [0,0] and the point.

    a:
        single point e.g. (1,2)

    return:
        4-tuple, e.g. (0, 0, 1, 2)

    Example: to_rect([2,3]) would return (0, 0, 2, 3)
    '''
    a = _np.ravel(a)
    if len(a) == 2:
        a = (0, 0, a[0], a[1])
    return _np.array(a, _np.float64).reshape(2, 2)

def rect_xywh_to_pts(x, y, w, h):
    '''(int|float,int|float,int|float,int|float) -> 4,2-list
    xywh defined rect to cvxy points

    Example:
    >>>rect_xywh_to_pts(0, 0, 10, 10)
    [[0,0], [0,10], [10,10], [10,0]]
    '''
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def rect_as_rchw(pts):
    '''(ndarray|list|tuple)-> int, int, int, int
    Take points in CVXY format, and return rectangle defined
    as  r, c, h, w

    pts:
        array of points in CVXY format
    Returns:
        row, col, height, width

    Example:
    >>> pts = [[5,10], [5, 100], [110, 100], [100, 10]]
    >>> rect_as_xywh(pts)
    (5, 10, 106, 91)
    '''
    if len(pts) != 4:
        raise ValueError('Expected 4 points, got %s' % len(pts))

    dims = tuple([len(i) for i in pts])
    if max(dims) != 2 or min(dims) != 2:
        raise ValueError('Some items in iterable argument pts do not have 2 dimensions.')

    pts = _np.array(pts)

    x = pts[:, 0].min()
    y = pts[:, 1].min()
    w = pts[:, 0].max() + 1 - pts[:, 0].min()
    h = pts[:, 1].max() + 1 - pts[:, 1].min()
    return y, x, h, w


def rect_xy_to_tlbr(pts):
    '''(list|tuple)->2-list
    Given xy formatted rect, convert
    to rect defined by top left and top right points

    Order points first, just in case
    Example:
    >>>rect_xy_to_tlbr([[0,0],[10,0],[10,10],[0,10]])
    [[0,0],[10,10]]
    '''
    out = _geom.order_points(pts)
    return [out[0], out[2]]


def rect_xy_to_xywh(pts):
    '''(list|tuple)->2-list
    Given xy formatted rect, convert
    to xywh format.

    Order points first, just in case
    Example:
    >>>rect_xy_to_tlbr([[0,0],[10,0],[10,10],[0,10]])
    [[0,0],[10,10]]
    '''
    out = _geom.order_points(pts)
    xs, ys = zip(*pts)
    return [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]


def rect_longform_to_cvpts(pts):
    '''(arraylike) -> list

    Takes an ndarray, list or tuple longform
    representation (x1,y1,x2,y2,x3,y3,x4,y4) of a rect and coverts it
    to cv2 point format.

    Example:
    >>>rect_longform_to_cvpts([0,0,10,0,10,10,0,10])
    [[0,0], [10,0], [10,10], [10,0]]
    '''
    if isinstance(pts, _np.ndarray):
        a = _np.squeeze(pts)
        a = a.tolist()
    else:
        a = pts.copy()

    return [[a[0], a[1]],
            [a[2], a[3]],
            [a[4], a[5]],
            [a[6], a[7]]]



# DEBUG bounding_rect_of_poly
def bounding_rect_of_poly(points, as_points=True):
    '''(list|ndarray)->n-list
    Return points of a bounding rectangle in opencv point format if
    as_points=True. Returns integer list.

    Use bounding_rect_of_poly2 if want floats.

    If as_points is false, returns as a tuple (x,y,w,h)

    Returns corner points ([[x,y],[x+w,y],[x,y+h],[x+w,y+h]]
    and *not* top left point with width and height (ie x,y,w,h).
    Note opencv points have origin in top left
    and are (x,y) i.e. col,row (width,height).
    '''
    if not isinstance(points, _np.ndarray):
        points = _np.array([points], dtype=_np.int32)

    #round negatives more negative, positives more positive, and convert to int - boundingrect fails if not integers
    #Note: boundingRect returns Top Left coordinate, it accepts points
    x, y, w, h = _cv2.boundingRect(_np.array(_rnd(points), 'int'))

    if as_points:
        return rect_as_points(y, x, w, h)

    return (x, y, w, h)



# DEBUG bounding_rect_of_ellipse
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
    M = _np.float64([[cx, 0, tx], [0, cy, ty], [0, 0, 1]])
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
    if not detections:
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


def iou(pts_gt, pts):
    '''(list, list) -> float

    pts_gr, pts:
        list of points, e.g. [[1,0],[0,1], [0,0],[1,1]]
    Return the intersection over union score

    Example:
    >>>iou([[1,0],[0,1], [0,0],[1,1]], [[0.5,0],[0,0.5], [0,0],[0.5,0.5]])
    0.25

    Notes:
        Orders the points prior to calculating
    '''
    pts_gt_ = _geom.order_points(pts_gt)
    pts_ = _geom.order_points(pts)

    x, y = zip(*pts_gt_)
    gt_xmax = max(x)
    gt_xmin = min(x)
    gt_ymax = max(y)
    gt_ymin = min(y)

    x, y = zip(*pts_)
    xmax = max(x)
    xmin = min(x)
    ymax = max(y)
    ymin = min(y)

    dx = min(gt_xmax, xmax) - max(gt_xmin, xmin)
    dy = min(gt_ymax, ymax) - max(gt_ymin, ymin)

    overlap = 0
    if (dx >= 0) and (dy >= 0):
        overlap = dx*dy
    total_area = ((xmax - xmin) * (ymax - ymin)) + ((gt_xmax - gt_xmin) * (gt_ymax - gt_ymin))
    union_area = total_area - overlap
    return overlap / union_area


def iou2(gt_xmin, gt_xmax, gt_ymin, gt_ymax, xmin, xmax, ymin, ymax):
    '''(float, float, float, float, float, float, float, float) -> float

    Args:
        coordinate min and maxes

    Returns the intersection over union score

    Example:
    >>>iou2(0, 1, 0, 1, 0, 0.5, 0, 0.5)
    0.25

    Notes:
        Orders the points prior to calculating
    '''

    if None in [gt_xmin, gt_xmax, gt_ymin, gt_ymax, xmin, xmax, ymin, ymax]:
        return None

    dx = min(gt_xmax, xmax) - max(gt_xmin, xmin)
    dy = min(gt_ymax, ymax) - max(gt_ymin, ymin)

    overlap = 0
    if (dx >= 0) and (dy >= 0):
        overlap = dx*dy
    total_area = ((xmax - xmin) * (ymax - ymin)) + ((gt_xmax - gt_xmin) * (gt_ymax - gt_ymin))
    union_area = total_area - overlap
    return overlap / union_area


def crop_from_rects(img, rects, crop=True, mask_with_boundary_pixels=False):
    '''(ndarray, list|tuple, bool) -> ndarray, ndarray, n-2-list
    Given a set of possibly nonintersecting rectangles
    build a mask.

    Note, if we ask to crop the image, the returned
    image dimensions won't match the mask dimensions.

    rects:numpy array of contours, each contour contains n points, a contour has shape n,1,2
    crop:crop the output image to extent of included regions
    mask_with_boundary_pixels: rather than a black mask, fill with
    mean boundary pixel value

    Returns:
        mask image, mask, extent (n-2-list) in cvpt format

    Example:
    >>>rect1 = [[100, 100], [300, 100], [300, 300], [100, 300]]
    >>>rect2 = [[350, 350], [475, 350], [475, 400], [350, 400]]
    >>>i, mask, extent = roi.crop_from_rects(self.I, [rect1, rect2])
    '''
    mask = _np.zeros_like(img)
    if len(img.shape) == 2:
        colour = 255
    elif len(img.shape)== 3:
        colour = (255, 255, 255)
    else:
        colour = (255, 255, 255, 255)

    pts = []

    for rect in rects:
        _cv2.fillPoly(mask, _np.array([rect], dtype='int32'), color=colour)
        pts.extend(rect.squeeze().tolist())

    i = get_image_from_mask(img, mask)
    if crop:
        miny = img.shape[0]; maxy=0; minx=img.shape[1]; maxx = 0;
        xs, ys = zip(*pts)
        miny = miny if min(ys) > miny else min(ys)
        maxy = maxy if max(ys) < maxy else max(ys)
        minx = minx if min(xs) > minx else min(xs)
        maxx = maxx if max(xs) < maxx else max(xs)

        if len(img.shape) == 2:
            i = i[miny:maxy+1, minx:maxx+1]
        else:
            i = i[miny:maxy+1, minx:maxx+1, ...]

    return i, mask, [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]]



def contours_join_slow(img, contours, thresh, thresh_is_pixels=False):
    '''(ndarray, ndarray, int|float, bool) -> ndarray
    Join nearby contours with distance threshhold of thresh.

    Returns:
        Joined contours
    '''
    def _find_if_close(cnt1, cnt2):
        if not thresh_is_pixels:
            thresh_ = thresh * _np.mean(img.shape[0:2])
        else:
            thresh_ = thresh

        row1, row2 = cnt1.shape[0],cnt2.shape[0]

        for i in range(row1):
            for j in range(row2):
                dist = _np.linalg.norm(cnt1[i] - cnt2[j])
                if abs(dist) < thresh_ :
                    return True
                elif i==row1 - 1 and j==row2 - 1:
                    return False


    LENGTH = len(contours)
    status = _np.zeros((LENGTH, 1))
    gray = _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)

    for i, cnt1 in enumerate(contours):
        x = i
        if i != LENGTH - 1:
            for j, cnt2 in enumerate(contours[i+1:]):
                x += 1
                dist = _find_if_close(cnt1, cnt2)
                if dist == True:
                    val = min(status[i],status[x])
                    status[x] = status[i] = val
                else:
                    if status[x]==status[i]:
                        status[x] = i + 1

    unified = []
    maximum = int(status.max())+1

    for i in xrange(maximum):
        pos = _np.where(status==i)[0]
        if pos.size != 0:
            cont = _np.vstack(contours[i] for i in pos)
            hull = _cv2.convexHull(cont)
            unified.append(hull)

    return unified


def mask_join(img, kernel=(5,5), iterations=10):
    '''(ndarray, ndarray, 2-tuple, int) -> ndarray
    Attempt to simplify a mask. Note for masks; White=Keep, Black=Mask out

    img:the mask, a binary mask image
    kernel:tuple, the size of the kernel for dilation
    iterations:nr iterations for dilation operation

    Returns: image (ndarray)
    '''
    if len(img.shape) == 2:
        imgbw = img.astype('uint8')
    else:
        imgbw = _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)

    imgdil = _cv2.dilate(imgbw, kernel=kernel, iterations=iterations)
    contour, hier = _cv2.findContours(imgdil, _cv2.RETR_CCOMP, _cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contour:
        _cv2.drawContours(imgdil, [cnt], 0, 255, -1)
    return imgdil


def contours_cluster_by_histo(img, contours, hist_bins=3, thresh=0.2, additional_obs=None):
    '''(ndarray, n-1-2-list, int, float, list) -> dict, list
    Cluster contours by their histograms using cosine distances.

    Arguments:
    img: the original image from which we build are patch histos
    contours: Contours found with cv2.findcontours, each contour is a n-1-2 list of cv points
    >>>contours[0]
    array([[[100, 200]],
       [[100, 299]],
       [[199, 299]],
       [[199, 200]]], dtype=int32)
    >>>contours.shape
    (4, 1, 2)

    hist_bins: Number of bins for each channel's histogram
    thresh: The cosine distance below which contours are considered the same. Note that cosine distances vary between -1 and 1. For all positive plane values, distances vary between 0 and 1.
    additional_obs: an len(contours),n-list of additional data to append to the observationss
    Note:
    contours is a n-list where each element is an n,1,2-ndarray
    of points which represent the contour.

    Returns:
        dictionary, each key is a group containing a list of contours. The keys are 'C1', 'C2' etc.
        and a simple list of contour numerical labels
    '''
    dout = {}; obs = None
    for i, contour in enumerate(contours):
        bx = contour.squeeze().tolist()
        bx_xywh = rect_xy_to_xywh(bounding_rect_of_poly(bx))
        _, hist1, hist2, hist3 = _histo_rgb(img, bx_xywh, (0, 1, 2), bins=hist_bins)
        if additional_obs: hist3.extend(tuple(additional_obs[i]))
        hist2.extend(tuple(hist3))
        hist1.extend(tuple(hist2))
        if obs is None:
            obs = _np.array([hist1])
        else:
            obs = _np.concatenate((obs, _np.array([hist1])), 0)

    distances = _scipy_dist.pdist(obs, metric='cosine')
    distances_sq = _scipy_dist.squareform(distances) #n x n pairwise distance matrix as usual

    Z = _scipy_heir.single(distances)
    F = _scipy_heir.fcluster(Z, thresh, criterion='distance')

    lkey = lambda k: 'C%s' % k
    for grp in set(F):
        dout[lkey(grp)] = []

    for i, grp in enumerate(F):
        dout[lkey(grp)].append(contours[i])

    return dout, F.tolist()


def mask_get(img, thresh=(1,1,1)):
    '''(ndarray, list|tuple|int) -> 2d-ndarray
    Return a 1 channel image mask, masking out pixels
    below thresh.

    All values less than thresh are masked, setting
    all values >= thresh to white
    '''
    img_ = img.copy()

    if len(img_.shape) > 2:
        CI = _color.ColorInterval(_color.eColorSpace.BGR, thresh, (255, 255, 255))
        CD = _color.ColorDetection(img_, CI, _color.eColorSpace.BGR)
        CD.detect()
        return CD.detected_as_mask()


    if isinstance(thresh, (tuple, list)):
        thresh = thresh[0]

    img_[img_ < thresh] = 0


def boundary_colour_mean(img, rects):
    '''
    Get the mean boundary colour for rects
    '''
    assert img.shape[2] == 3, 'Expected a 3 channel image'

    topb = []; topg = []; topr = []
    bottomb = [];bottomg = [];bottomr = []
    leftb = [];leftg = [];leftr = []
    rightb = [];rightg = [];rightr = []
    for rect in rects:
        rect = _geom.order_points(rect)
        r, c, h, w = rect_as_rchw(rect)
        topb.append(_np.mean(img[r + 1, c:c + w, 0]))
        topg.append(_np.mean(img[r + 1, c:c + w, 1]))
        topr.append(_np.mean(img[r + 1, c:c + w, 2]))

        bottomb.append(_np.mean(img[r + h - 1, c:c + w, 0]))
        bottomg.append(_np.mean(img[r + h - 1, c:c + w, 1]))
        bottomr.append(_np.mean(img[r + h - 1, c:c + w, 2]))

        leftb.append(_np.mean(img[r:r + h, c + 1, 0]))
        leftg.append(_np.mean(img[r:r + h, c + 1, 1]))
        leftr.append(_np.mean(img[r:r + h, c + 1, 2]))

        rightb.append(_np.mean(img[r:r + h, c + w - 1, 0]))
        rightg.append(_np.mean(img[r:r + h, c + w - 1, 1]))
        rightr.append(_np.mean(img[r:r + h, c + w - 1, 2]))

    m = lambda l: sum(l) / len(l)
    out = (int((m(topb) + m(bottomb) + m(leftb) + m(rightb))/4),
           int((m(topg) + m(bottomg) + m(leftg) + m(rightg))/4),
           int((m(topr) + m(bottomr) + m(leftr) + m(rightr))/4))
    return out


def contour_to_cvpts(cnt):
    '''(n,1,2-ndarray) -> n,2-list
    Convert a contour points to
    standard CVXY points list.

    cnt:A cv2 contour, which is an n,1,2 ndarray

    Returns:
    List of points in standard cv format, e.g. [[0,0],[1,2]]
    '''
    if isinstance(cnt, _np.ndarray):
        return cnt.squeeze().tolist()
    return cnt

def cvpts_to_contour(pts):
    '''(n,2-list) -> n,1,2-ndarray
    Convert a standard CVXY points list to
    a cv contour (e.g. an element in the list
    returned by cv2.findContours.

    pts: List of points in standard cv format, e.g. [[0,0],[1,2]]

    Returns:
    A cv2 contour, which is an n,1,2 ndarray

    Example:
    >>>cvpts_to_contour([[0,0],[1,2]]).shape
    (2, 1, b2)

    '''
    return _np.array(pts, dtype='int32').reshape(len(pts), -1, 2)


def contours_to_bounding_rects(contours):
    '''(n,m,1,2-ndarray) -> (n,4,1,2-ndarray)

    Get bounding contours from contour polygons.
    Contour polygons are returned by the cv2.findContours
    function.

    contours: contours list, e.g. from cv2.findContours

    Returns:
    contours converted to their bounding rects.
    '''
    cnts_ = list(contours) #copy it
    for i, cnt in enumerate(contours):
         x, y, w, h = _cv2.boundingRect(cnt)
         c = cvpts_to_contour(rect_xywh_to_pts(x, y, w, h))
         cnts_[i] = c
    return cnts_


def contour_cluster_outliers(contours, thresh, plane_size=None, thresh_is_proportion=True):
    '''(list:n,1,2-ndarray, float|int, None|2-tuple, bool)-> list, list, 2-tuple:n,2-lists
    Given a set of contours (e.g. from cv2.findContours), split the
    contours into contours further than thresh away from any other contour

    Parameters:
    contours: Contour list, list of n,1,2-ndarray polygons
    thresh: Threshold distance, any shape > threshold from all other shapes is an outlier. Based on the greatest image shape rather than average - think of case when image is cut off, we don't want to allow very small distances as the larger dimension will be reflective of the "real" doc size.
    plane_size: The total plane size, use when using thresh_is_proportion
    thresh_is_proportion:distances are calculated as a proportion of the plane size, otherwise thresh is pixels.

    Returns:
        list of clustered contours, and list of outlier contours then a 2-tuple containing the indices of the inliers and outliers.
        i.e. "return inliers, outliers, (inlier_idxs, outlier_idxs)"
        Returns empty lists if no outliers and outlier indices.
    Example:
    >>>inliers, outliers, indices = contour_cluster_outliers(contours, 0.1, img.shape)
    '''
    if len(contours) == 1: return contours, [], ([0], []) #no outliers with a single contour!

    assert thresh_is_proportion and plane_size, 'Cannot have a proportional threshhold without  plane_size'

    y1, y2, x1, x2 = contours_bounding_rect(contours) #bounding rect of all contours

    if plane_size:
        I = _np.zeros(plane_size[0:2], dtype='int32') #int32 might be required for ndimage manipulation so force it
    else:
        I = _np.zeros((y2, x2), dtype='int32')

    if thresh_is_proportion:
        px_dist = int(plane_size[1] * thresh)
    else:
        px_dist = int(thresh)

    I = _cv2.drawContours(I, contours, -1, 255)
    I, _ = _ndimage.label(I)
    D = _dist.feature_dist(I)

    inlier_idxs = list(set(_np.argwhere((D < px_dist) & (D != 0)).flatten().tolist()))
    inliers = [contours[i] for i in inlier_idxs]

    outlier_idxs = _baselib.list_not(range(len(contours)), inlier_idxs)
    outliers = [contours[i] for i in outlier_idxs]
    return inliers, outliers, (inlier_idxs, outlier_idxs)



def contours_bounding_rect(contours):
    '''(list:n,1,2-ndarray)->y1, y2, x1, x2

    Returns:
        y1, y2, x1, x2. Chosen for ease of use in using for slicing
    '''
    allpts = []
    for c in contours:
        pts = contour_to_cvpts(c)
        _ = [allpts.append(pt) for pt in pts]
    xs, ys = zip(*allpts)
    return min(ys), max(ys), min(xs), max(xs)
