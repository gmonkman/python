#pylint: disable=reimported, missing-docstring, bad-option-value, import-error
'''
This module contains some common routines used by other samples.
From https://github.com/opencv/opencv/blob/master/samples/python/common.py#L1
'''
#region imports
from __future__ import print_function
import sys
from glob import glob

import numpy as np
import cv2
from cv2 import convexHull
import imghdr
import fuckit

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

# built-in modules
import os
import itertools as it
from contextlib import contextmanager

import funclib.iolib as iolib
#endregion


#module consts and variables
IMAGE_EXTENSIONS = ['.bmp', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.pbm', '.pgm', '.ppm']
IMAGE_EXTENSIONS_AS_WILDCARDS = ['*.bmp', '*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff', '*.pbm', '*.pgm', '*.ppm']

# palette data from matplotlib/_cm.py
_jet_data = {'red': ((0., 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89, 1, 1),
                         (1, 0.5, 0.5)),
               'green': ((0., 0, 0), (0.125, 0, 0), (0.375, 1, 1), (0.64, 1, 1),
                         (0.91, 0, 0), (1, 0, 0)),
               'blue': ((0., 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1), (0.65, 0, 0),
                         (1, 0, 0))}

cmap_data = {'jet' : _jet_data}
#module consts and variables


#region classes
class Bunch(object):
    '''bunch'''
    def __init__(self, **kw):
        self.__dict__.update(kw)
    def __str__(self):
        return str(self.__dict__)

class Sketcher(object):
    def __init__(self, windowname, dests, colors_func):
        self.prev_pt = None
        self.windowname = windowname
        self.dests = dests
        self.colors_func = colors_func
        self.dirty = False
        self.show()
        cv2.setMouseCallback(self.windowname, self.on_mouse)

    def show(self):
        cv2.imshow(self.windowname, self.dests[0])

    def on_mouse(self, event, x, y, flags):
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.prev_pt = pt
        elif event == cv2.EVENT_LBUTTONUP:
            self.prev_pt = None

        if self.prev_pt and flags & cv2.EVENT_FLAG_LBUTTON:
            for dst, color in zip(self.dests, self.colors_func()):
                cv2.line(dst, self.prev_pt, pt, color, 5)
            self.dirty = True
            self.prev_pt = pt
            self.show()

class StatValue(object):
    def __init__(self, smooth_coef=0.5):
        self.value = None
        self.smooth_coef = smooth_coef
    def update(self, v):
        if self.value is None:
            self.value = v
        else:
            c = self.smooth_coef
            self.value = c * self.value + (1.0-c) * v

class RectSelector(object):
    def __init__(self, win, callback):
        self.win = win
        self.callback = callback
        cv2.setMouseCallback(win, self.onmouse)
        self.drag_start = None
        self.drag_rect = None
    def onmouse(self, event, x, y, flags):
        x, y = np.int16([x, y]) # BUG
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            return
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                xo, yo = self.drag_start
                x0, y0 = np.minimum([xo, yo], [x, y])
                x1, y1 = np.maximum([xo, yo], [x, y])
                self.drag_rect = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.drag_rect = (x0, y0, x1, y1)
            else:
                rect = self.drag_rect
                self.drag_start = None
                self.drag_rect = None
                if rect:
                    self.callback(rect)
    def draw(self, vis):
        if not self.drag_rect:
            return False
        x0, y0, x1, y1 = self.drag_rect
        cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 255, 0), 2)
        return True
    @property
    def dragging(self):
        return self.drag_rect is not None
#endregion


#region defs
def roi_polygon_set(img, points):
    '''(np array or path, array of points)->img
    Points are for a rectangle as an e.g. [(0,0), (50,0), (0,50), (50,50)]
    '''
    if isinstance(img, str):
        img = cv2.imread(img, -1) # -1 loads as-is so if it will be 3 or 4 channel as the original
    else:
        if not isinstance(img, np.ndarray):
            raise ValueError('Argument must be the path to an image, or an image (ndarray)')

    # mask defaulting to black for 3-channel and transparent for 4-channel
    # (of course replace corners with yours)
    mask = np.zeros(img.shape, dtype=np.uint8)
    roi_corners = convexHull(np.array([points], dtype=np.int32))
    #roi_corners = np.array([points], dtype=np.int32)
    channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
    ignore_mask_color = (255,)*channel_count
    #cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)
    #cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)
    cv2.fillPoly(mask, roi_corners, ignore_mask_color)

    cv2.imshow('preview', mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return cv2.bitwise_and(img, mask) # apply and return the mask

def get_perspective_correction(bg_dist, object_depth, length):
    '''(float, float)->float|None
    Return the length corrected for the depth of the object
    considering the backplane of the object to be the best
    representative of the length
    *NOTE* The length of the object has been accurately measured
    '''
    if bg_dist is None or object_depth is None or length is None:
        return None
    elif bg_dist == 0 or 1-(object_depth/bg_dist) == 0:
        return None
    else:
        return length/(1-(object_depth/bg_dist))

def get_perspective_correction_iter_linear(coeff, const, bg_dist, length, last_length=0, stop_below_proportion=0.01):
    '''(float, float, float, float,float)->float|None
    Return the length corrected for the depth of the object
    considering the backplane of the object to be the best
    representative of the length.
    *NOTE* The length of the object was itself estimated from the foreground standard measure

    Coeff and constant are used to calculate an objects depth from its length
    The object depth is used to create a iterative series sum which add to the length
    to return the sum of lengths once the last length added was less then stop_below

    stop_below_proportion is the stopping criteria, once the last
    calculated length to add is is less than last_length*stop_below_proportion
    we return the result and stop the iteration
    '''
    if last_length == 0:
        object_depth = length*coeff + const
    else:
        object_depth = last_length*coeff + const

    if object_depth == 0:
        return length
    elif length == 0:
        return 0
    elif (last_length/length < stop_below_proportion) and last_length > 0:
        return length

    if last_length == 0: #first call
        l = get_perspective_correction(bg_dist, object_depth, length) - length
    else:
        l = get_perspective_correction(bg_dist, object_depth, last_length) - last_length

    if l is None:
        return None

    return get_perspective_correction_iter_linear(coeff, const, bg_dist, length + l, l, stop_below_proportion)

def get_image_resolutions(glob_str):
    '''(str)->list of lists
    Takes paths and using wildcards globs through all images
    Returns all unique image resolutions (row, column) as
    list of lists
    [[800,600],[1024,768]]
    '''
    dims = []
    for pic in glob(glob_str):
        if is_image(pic):
            with fuckit:
                img = cv2.imread(pic)
            if isinstance(img, np.ndarray):
                h, w = img.shape[:2]
                e = [w, h]
                if e not in dims:
                    dims.append(e)
    return dims

def resolution(img):
    '''ndarray
    width,height
    '''
    assert isinstance(img, np.ndarray)
    return [img.shape[1], img.shape[0]]

def is_image(file_path, try_load=False):
    '''(str)->bool
    Pass in a file string and see if it looks like an image.
    If try_load is true, we try and load the file using cv2.imread (costly)
    '''
    ret = False
    if not imghdr.what(file_path) is None:
        ret = True
        if try_load:
            with fuckit:
                ret = False
                img = cv2.imread(file_path)
                if isinstance(img, np.ndarray):
                    ret = True
    return ret

def image_generator(paths, wildcards, flags=None):
    '''(iterable, iterable)->ndarray (an image)
    Globs through every file in paths matching wildcards returning
    the image as an ndarray
    '''
    for images in iolib.file_list_generator1(paths, wildcards):
        if flags is None:
            yield cv2.imread(images)
        else:
            yield cv2.imread(images, flags)

def splitfn(fn):
    '''(str) -> tuple
    splits a full file name into path, name and extension, returning as a tuple
    '''
    path, fn = os.path.split(fn)
    name, ext = os.path.splitext(fn)
    return path, name, ext

def anorm2(a):
    '''anorm2'''
    return (a*a).sum(-1)
def anorm(a):
    '''anorm'''
    return np.sqrt(anorm2(a))

def homotrans(H, x, y):
    xs = H[0, 0]*x + H[0, 1]*y + H[0, 2]
    ys = H[1, 0]*x + H[1, 1]*y + H[1, 2]
    s = H[2, 0]*x + H[2, 1]*y + H[2, 2]
    return xs/s, ys/s

def to_rect(a):
    a = np.ravel(a)
    if len(a) == 2:
        a = (0, 0, a[0], a[1])
    return np.array(a, np.float64).reshape(2, 2)

def rect_as_points(rw, col, h, w):
    '''(int,int,int,int)->list
    Given a rectangle specified by the top left point
    and width and height, convert to a list of points
    '''
    return [(rw, col), (rw + h, col), (rw, col + w), (h, w)]

def rect2rect_mtx(src, dst):
    src, dst = to_rect(src), to_rect(dst)
    cx, cy = (dst[1] - dst[0]) / (src[1] - src[0])
    tx, ty = dst[0] - src[0] * (cx, cy)
    M = np.float64([[cx, 0, tx], [0, cy, ty], [0, 0, 1]])
    return M

def lookat(eye, target, up=(0, 0, 1)):
    fwd = np.asarray(target, np.float64) - eye
    fwd /= anorm(fwd)
    right = np.cross(fwd, up)
    right /= anorm(right)
    down = np.cross(fwd, right)
    R = np.float64([right, down, fwd])
    tvec = -np.dot(R, eye)
    return R, tvec

def mtx2rvec(R):
    w, u, vt = cv2.SVDecomp(R - np.eye(3))
    p = vt[0] + u[:, 0]*w[0]    # same as np.dot(R, vt[0])
    c = np.dot(vt[0], p)
    s = np.dot(vt[1], p)
    axis = np.cross(vt[0], vt[1])
    return axis * np.arctan2(s, c)

def draw_str(dst, target, s):
    x, y = target
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)

def make_cmap(name, n=256):
    data = cmap_data[name]
    xs = np.linspace(0.0, 1.0, n)
    channels = []
    eps = 1e-6
    for ch_name in ['blue', 'green', 'red']:
        ch_data = data[ch_name]
        xp, yp = [], []
        for x, y1, y2 in ch_data:
            xp += [x, x+eps]
            yp += [y1, y2]
        ch = np.interp(xs, xp, yp)
        channels.append(ch)
    return np.uint8(np.array(channels).T*255)

def clock():
    return cv2.getTickCount() / cv2.getTickFrequency()

@contextmanager
def Timer(msg):
    print(msg, '...',)
    start = clock()
    try:
        yield
    finally:
        print("%.2f ms" % ((clock()-start)*1000))

def grouper(n, iterable, fillvalue=None):
    '''grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx'''
    args = [iter(iterable)] * n
    if PY3:
        output = it.zip_longest(fillvalue=fillvalue, *args)
    else:
        output = it.izip_longest(fillvalue=fillvalue, *args)
    return output

def mosaic(w, imgs):
    '''Make a grid from images.
    w    -- number of grid columns
    imgs -- images (must have same size and format)
    '''
    imgs = iter(imgs)
    if PY3:
        img0 = next(imgs)
    else:
        img0 = next(imgs)
    pad = np.zeros_like(img0)
    imgs = it.chain([img0], imgs)
    rows = grouper(w, imgs, pad)
    return np.vstack(map(np.hstack, rows))

def getsize(img):
    h, w = img.shape[:2]
    return w, h

#def mdot(*args):
   # return reduce(np.dot, args)

def draw_keypoints(vis, keypoints, color=(0, 255, 255)):
    for kp in keypoints:
        x, y = kp.pt
        cv2.circle(vis, (int(x), int(y)), 2, color)

#region jrosebr1
#https://github.com/jrosebr1/imutils/blob/master/imutils/convenience.py
def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    '''(ndarray, int, int, constant)->void
    1) initialize the dimensions of the image to be resized and grab the image size
    2) If both the width and height are None, then return the original image
    3) Both not none then resize to specied witdth and height
    4) Otherwise resize keeping the aspect ratio according to the provided width or height
    '''
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    elif not width is None and not height is None:
        dim = (width, height)
    elif width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    elif height is None:
        r = width / float(w)
        dim = (width, int(h * r))
    return cv2.resize(image, dim, interpolation=inter)

def skeletonize(image, size, structuring=cv2.MORPH_RECT):
    # determine the area (i.e. total number of pixels in the image),
    # initialize the output skeletonized image, and construct the
    # morphological structuring element
    area = image.shape[0] * image.shape[1]
    skeleton = np.zeros(image.shape, dtype="uint8")
    elem = cv2.getStructuringElement(structuring, size)

    # keep looping until the erosions remove all pixels from the
    # image
    while True:
        # erode and dilate the image using the structuring element
        eroded = cv2.erode(image, elem)
        temp = cv2.dilate(eroded, elem)

        # subtract the temporary image from the original, eroded
        # image, then take the bitwise 'or' between the skeleton
        # and the temporary image
        temp = cv2.subtract(image, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        image = eroded.copy()

        # if there are no more 'white' pixels in the image, then
        # break from the loop
        if area == area - cv2.countNonZero(image):
            break

    # return the skeletonized image
    return skeleton

def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    '''(str,cv2readflag)->ndarray
    download the image, convert it to a NumPy array, and then read
     it into OpenCV format
     '''
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, readFlag)
    return image

def opencv2matplotlib(image):
    '''(ndarray0->ndarray
    OpenCV represents images in BGR order; however, Matplotlib
    expects the image in RGB order, so simply convert from BGR
    to RGB and return
    '''
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def is_cv2():
    '''if we are using OpenCV 2, then our cv2.__version__ will start
    with '2.'
    '''
    return opencv_check_version("2.")

def is_cv3():
    '''
    if we are using OpenCV 3.X, then our cv2.__version__ will start
    with '3.'
    '''
    return opencv_check_version("3.")

def opencv_check_version(major, lib=None):
    '''if the supplied library is None, import OpenCV
    '''
    if lib is None:
        import cv2 as lib

    # return whether or not the current OpenCV version matches the
    # major version number
    return lib.__version__.startswith(major)
#endregion
#endregion
