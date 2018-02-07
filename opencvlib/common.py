#pylint: skip-file
#Dont remove any functions from here
'''
From opencv demos
This module contains some common routines used by other opencv demos.
'''

# Python 2/3 compatibility
import sys as _sys
from functools import reduce as _reduce

import numpy as _np
import cv2 as _cv2

# built-in modules
import os as _os
import itertools as _it
from contextlib import contextmanager as _contextmanager

IMAGE_EXTENSIONS = ['.bmp', '.jpg', '.jpeg',
                    '.png', '.tif', '.tiff', '.pbm', '.pgm', '.ppm']

class Bunch(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __str__(self):
        return str(self.__dict__)


def splitfn(fn):
    path, fn = _os.path.split(fn)
    name, ext = _os.path.splitext(fn)
    return path, name, ext


def anorm2(a):
    return (a * a).sum(-1)


def anorm(a):
    return _np.sqrt(anorm2(a))


def homotrans(H, x, y):
    xs = H[0, 0] * x + H[0, 1] * y + H[0, 2]
    ys = H[1, 0] * x + H[1, 1] * y + H[1, 2]
    s = H[2, 0] * x + H[2, 1] * y + H[2, 2]
    return xs / s, ys / s


def to_rect(a):
    a = _np.ravel(a)
    if len(a) == 2:
        a = (0, 0, a[0], a[1])
    return _np.array(a, _np.float64).reshape(2, 2)


def rect2rect_mtx(src, dst):
    src, dst = to_rect(src), to_rect(dst)
    cx, cy = (dst[1] - dst[0]) / (src[1] - src[0])
    tx, ty = dst[0] - src[0] * (cx, cy)
    M = _np.float64([[cx,  0, tx], [0, cy, ty], [0,  0,  1]])
    return M


def lookat(eye, target, up=(0, 0, 1)):
    fwd = _np.asarray(target, _np.float64) - eye
    fwd /= anorm(fwd)
    right = _np.cross(fwd, up)
    right /= anorm(right)
    down = _np.cross(fwd, right)
    R = _np.float64([right, down, fwd])
    tvec = -_np.dot(R, eye)
    return R, tvec


def mtx2rvec(R):
    w, u, vt = _cv2.SVDecomp(R - _np.eye(3))
    p = vt[0] + u[:, 0] * w[0]    # same as _np.dot(R, vt[0])
    c = _np.dot(vt[0], p)
    s = _np.dot(vt[1], p)
    axis = _np.cross(vt[0], vt[1])
    return axis * _np.arctan2(s, c)


def draw_str(dst, x, y, s, color=(255, 255, 255), scale=1.0, bottom_left_origin=False):
    '''(ndarray, 2:tuple, str) -> void
    Draw text on dst - ByRef

    dst:
        Image to draw text on, byref
    target:
        draw text on dst at these coordinates.
        tuple is (x, y)
    '''
    #FONT_HERSHEY_PLAIN
    _cv2.putText(dst, s, (x, y), _cv2.FONT_HERSHEY_TRIPLEX,
                scale, color, lineType=_cv2.LINE_AA, bottomLeftOrigin=bottom_left_origin)


class Sketcher:
    def __init__(self, windowname, dests, colors_func):
        self.prev_pt = None
        self.windowname = windowname
        self.dests = dests
        self.colors_func = colors_func
        self.dirty = False
        self.show()
        _cv2.setMouseCallback(self.windowname, self.on_mouse)

    def show(self):
        _cv2.imshow(self.windowname, self.dests[0])

    def on_mouse(self, event, x, y, flags, dummy):
        pt = (x, y)
        if event == _cv2.EVENT_LBUTTONDOWN:
            self.prev_pt = pt
        elif event == _cv2.EVENT_LBUTTONUP:
            self.prev_pt = None

        if self.prev_pt and flags & _cv2.EVENT_FLAG_LBUTTON:
            for dst, color in zip(self.dests, self.colors_func()):
                _cv2.line(dst, self.prev_pt, pt, color, 5)
            self.dirty = True
            self.prev_pt = pt
            self.show()


# palette data from matplotlib/_cm.py
_jet_data = {'red':   ((0., 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89, 1, 1),
                       (1, 0.5, 0.5)),
             'green': ((0., 0, 0), (0.125, 0, 0), (0.375, 1, 1), (0.64, 1, 1),
                       (0.91, 0, 0), (1, 0, 0)),
             'blue':  ((0., 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1), (0.65, 0, 0),
                       (1, 0, 0))}

cmap_data = {'jet': _jet_data}


def make_cmap(name, n=256):
    data = cmap_data[name]
    xs = _np.linspace(0.0, 1.0, n)
    channels = []
    eps = 1e-6
    for ch_name in ['blue', 'green', 'red']:
        ch_data = data[ch_name]
        xp, yp = [], []
        for x, y1, y2 in ch_data:
            xp += [x, x + eps]
            yp += [y1, y2]
        ch = _np.interp(xs, xp, yp)
        channels.append(ch)
    return _np.uint8(_np.array(channels).T * 255)


def nothing(*dummy1, **dummy2):
    pass


def clock():
    '''
    returns absolute time in seconds since
    ticker started (usually when OS started
    '''
    return _cv2.getTickCount() / _cv2.getTickFrequency()


@_contextmanager
def Timer(msg):
    print(msg, '...',)
    start = clock()
    try:
        yield
    finally:
        print("%.2f ms" % ((clock() - start) * 1000))


class StatValue:
    def __init__(self, smooth_coef=0.5):
        self.value = None
        self.smooth_coef = smooth_coef

    def update(self, v):
        if self.value is None:
            self.value = v
        else:
            self.value = self.smooth_coef * self.value + (1.0 - self.smooth_coef) * v


class RectSelector:
    def __init__(self, win, callback):
        self.win = win
        self.callback = callback
        _cv2.setMouseCallback(win, self.onmouse)
        self.drag_start = None
        self.drag_rect = None

    def onmouse(self, event, x, y, flags):
        x, y = _np.int16([x, y])  # BUG
        if event == _cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            return
        if self.drag_start:
            if flags & _cv2.EVENT_FLAG_LBUTTON:
                xo, yo = self.drag_start
                x0, y0 = _np.minimum([xo, yo], [x, y])
                x1, y1 = _np.maximum([xo, yo], [x, y])
                self.drag_rect = None
                if x1 - x0 > 0 and y1 - y0 > 0:
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
        _cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 255, 0), 2)
        return True

    @property
    def dragging(self):
        return self.drag_rect is not None


def grouper(n, iterable, fillvalue=None):
    '''grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx'''
    args = [iter(iterable)] * n
    if PY3:
        output = _it.zip_longest(fillvalue=fillvalue, *args)
    else:
        output = _it.izip_longest(fillvalue=fillvalue, *args)
    return output


def chessboard(patch_sz=100, col_first_patch=(0, 0, 0), col_second_patch=(255, 255, 255), cols=9, rows=6):
    '''(int, 3-tuple, 3-tuple, int, int, bool) -> ndarray
    Returns a chessboard pattern.
    The nr. of vertices = (cols-1) * (rows-1)

    patch_sz:
        Size of patches in pixels
    col_first_patch:
        colour of starting patch (top left)
    col_second_light:
        colour of next patch
    cols:
        number of patch columns
    rows:
        number of patch rows
    '''
    patch_sz = int(patch_sz)
    cols = int(cols)
    rows = int(rows)
    color = col_first_patch
    board = _np.zeros([patch_sz*cols, patch_sz*rows, 3]).astype('uint8')
    for i in range(0, (rows+1)*patch_sz, patch_sz):
        for j in range(0, (cols+1)*patch_sz, patch_sz):
            board[j:j+patch_sz, i:i+patch_sz, :1] = color[0]
            board[j:j+patch_sz, i:i+patch_sz, :2] = color[1]
            board[j:j+patch_sz, i:i+patch_sz, :3] = color[2]
            color = col_second_patch if color==col_first_patch else col_first_patch
    return board