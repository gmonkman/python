#pylint: skip-file

'''
Video capture sample.

Sample shows how VideoCapture class can be used to acquire video
frames from a camera of a movie file. Also the sample provides
an example of procedural video generation by an object, mimicking
the VideoCapture interface (see Chess class).

'create_capture' is a convinience function for capture creation,
falling back to procedural video in case of error.

Usage:
    video.py [--shotdir <shot path>] [source0] [source1] ...'

    sourceN is an
     - integer number for camera capture
     - name of video file
     - synth:<params> for procedural video

Synth examples:
    synth:bg=../data/lena.jpg:noise=0.1
    synth:class=chess:bg=../data/lena.jpg:noise=0.1:size=640x480

Keys:
    ESC    - exit
    SPACE  - save current frame to <shot path> directory

'''
import common as _common
import sys as _sys
import getopt as _getopt

import numpy as _np
from numpy import _pi, _sin, _cos
import cv2 as _cv2



class _TestSceneRender():

    def __init__(self, bgImg=None, fgImg=None,
                 deformation=False, speed=0.25, **params):
        self.time = 0.0
        self.timeStep = 1.0 / 30.0
        self.foreground = fgImg
        self.deformation = deformation
        self.speed = speed

        if bgImg is not None:
            self.sceneBg = bgImg.copy()
        else:
            self.sceneBg = _np.zeros(defaultSize, defaultSize, _np.uint8)

        self.w = self.sceneBg.shape[0]
        self.h = self.sceneBg.shape[1]

        if fgImg is not None:
            self.foreground = fgImg.copy()
            self.center = self.currentCenter = (
                int(self.w / 2 - fgImg.shape[0] / 2), int(self.h / 2 - fgImg.shape[1] / 2))

            self.xAmpl = self.sceneBg.shape[0] - \
                (self.center[0] + fgImg.shape[0])
            self.yAmpl = self.sceneBg.shape[1] - \
                (self.center[1] + fgImg.shape[1])

        self.initialRect = _np.array([(self.h / 2, self.w / 2), (self.h / 2, self.w / 2 + self.w / 10),
                                     (self.h / 2 + self.h / 10, self.w / 2 + self.w / 10), (self.h / 2 + self.h / 10, self.w / 2)]).astype(int)
        self.currentRect = self.initialRect

    def getXOffset(self, time):
        return int(self.xAmpl * _cos(time * self.speed))

    def getYOffset(self, time):
        return int(self.yAmpl * _sin(time * self.speed))

    def setInitialRect(self, rect):
        self.initialRect = rect

    def getRectInTime(self, time):

        if self.foreground is not None:
            tmp = _np.array(self.center) + \
                _np.array((self.getXOffset(time), self.getYOffset(time)))
            x0, y0 = tmp
            x1, y1 = tmp + self.foreground.shape[0:2]
            return _np.array([y0, x0, y1, x1])
        else:
            x0, y0 = self.initialRect[0] + \
                _np.array((self.getXOffset(time), self.getYOffset(time)))
            x1, y1 = self.initialRect[2] + \
                _np.array((self.getXOffset(time), self.getYOffset(time)))
            return _np.array([y0, x0, y1, x1])

    def getCurrentRect(self):

        if self.foreground is not None:

            x0 = self.currentCenter[0]
            y0 = self.currentCenter[1]
            x1 = self.currentCenter[0] + self.foreground.shape[0]
            y1 = self.currentCenter[1] + self.foreground.shape[1]
            return _np.array([y0, x0, y1, x1])
        else:
            x0, y0 = self.currentRect[0]
            x1, y1 = self.currentRect[2]
            return _np.array([x0, y0, x1, y1])

    def getNextFrame(self):
        img = self.sceneBg.copy()

        if self.foreground is not None:
            self.currentCenter = (
                self.center[0] + self.getXOffset(self.time), self.center[1] + self.getYOffset(self.time))
            img[self.currentCenter[0]:self.currentCenter[0] + self.foreground.shape[0],
                self.currentCenter[1]:self.currentCenter[1] + self.foreground.shape[1]] = self.foreground
        else:
            self.currentRect = self.initialRect + \
                _np.int(30 * _cos(self.time * self.speed) +
                       50 * _sin(self.time * self.speed))
            if self.deformation:
                self.currentRect[1:3] += self.h / 20 * _cos(self.time)
            _cv2.fillConvexPoly(img, self.currentRect, (0, 0, 255))

        self.time += self.timeStep
        return img

    def resetTime(self):
        self.time = 0.0


class _VideoSynthBase(object):
    def __init__(self, size=None, noise=0.0, bg=None, **params):
        self.bg = None
        self.frame_size = (640, 480)
        if bg is not None:
            self.bg = _cv2.imread(bg, 1)
            h, w = self.bg.shape[:2]
            self.frame_size = (w, h)

        if size is not None:
            w, h = map(int, size.split('x'))
            self.frame_size = (w, h)
            self.bg = _cv2.resize(self.bg, self.frame_size)

        self.noise = float(noise)

    def render(self, dst):
        pass

    def read(self, dst=None):
        w, h = self.frame_size

        if self.bg is None:
            buf = _np.zeros((h, w, 3), _np.uint8)
        else:
            buf = self.bg.copy()

        self.render(buf)

        if self.noise > 0.0:
            noise = _np.zeros((h, w, 3), _np.int8)
            _cv2.randn(noise, _np.zeros(3), _np.ones(3) * 255 * self.noise)
            buf = _cv2.add(buf, noise, dtype=_cv2.CV_8UC3)
        return True, buf

    def isOpened(self):
        return True


class _Book(_VideoSynthBase):
    def __init__(self, **kw):
        super(_Book, self).__init__(**kw)
        backGr = _cv2.imread('../data/graf1.png')
        fgr = _cv2.imread('../data/box.png')
        self.render = _TestSceneRender(backGr, fgr, speed=1)

    def read(self, dst=None):
        noise = _np.zeros(self.render.sceneBg.shape, _np.int8)
        _cv2.randn(noise, _np.zeros(3), _np.ones(3) * 255 * self.noise)

        return True, _cv2.add(self.render.getNextFrame(), noise, dtype=_cv2.CV_8UC3)


class _Cube(_VideoSynthBase):
    def __init__(self, **kw):
        super(_Cube, self).__init__(**kw)
        self.render = _TestSceneRender(_cv2.imread(
            '../data/pca_test1.jpg'), deformation=True,  speed=1)

    def read(self, dst=None):
        noise = _np.zeros(self.render.sceneBg.shape, _np.int8)
        _cv2.randn(noise, _np.zeros(3), _np.ones(3) * 255 * self.noise)

        return True, _cv2.add(self.render.getNextFrame(), noise, dtype=_cv2.CV_8UC3)


class _Chess(_VideoSynthBase):
    def __init__(self, **kw):
        super(_Chess, self).__init__(**kw)

        w, h = self.frame_size

        self.grid_size = sx, sy = 10, 7
        white_quads = []
        black_quads = []
        for i, j in _np.ndindex(sy, sx):
            q = [[j, i, 0], [j + 1, i, 0], [j + 1, i + 1, 0], [j, i + 1, 0]]
            [white_quads, black_quads][(i + j) % 2].append(q)
        self.white_quads = _np.float32(white_quads)
        self.black_quads = _np.float32(black_quads)

        fx = 0.9
        self.K = _np.float64([[fx * w, 0, 0.5 * (w - 1)],
                             [0, fx * w, 0.5 * (h - 1)],
                             [0.0, 0.0,      1.0]])

        self.dist_coef = _np.float64([-0.2, 0.1, 0, 0])
        self.t = 0

    def draw_quads(self, img, quads, color=(0, 255, 0)):
        img_quads = _cv2.projectPoints(
            quads.reshape(-1, 3), self.rvec, self.tvec, self.K, self.dist_coef)[0]
        img_quads.shape = quads.shape[:2] + (2,)
        for q in img_quads:
            _cv2.fillConvexPoly(img, _np.int32(
                q * 4), color, _cv2.LINE_AA, shift=2)

    def render(self, dst):
        t = self.t
        self.t += 1.0 / 30.0

        sx, sy = self.grid_size
        center = _np.array([0.5 * sx, 0.5 * sy, 0.0])
        phi = _pi / 3 + _sin(t * 3) * _pi / 8
        c, s = _cos(phi), _sin(phi)
        ofs = _np.array([_sin(1.2 * t), _cos(1.8 * t), 0]) * sx * 0.2
        eye_pos = center + _np.array([_cos(t) * c, _sin(t) * c, s]) * 15.0 + ofs
        target_pos = center + ofs

        R, self.tvec = _common.lookat(eye_pos, target_pos)
        self.rvec = _common.mtx2rvec(R)

        self.draw_quads(dst, self.white_quads, (245, 245, 245))
        self.draw_quads(dst, self.black_quads, (10, 10, 10))


_classes = dict(chess=_Chess, book=_Book, cube=_Cube)

_presets = dict(
    empty='synth:',
    lena='synth:bg=../data/lena.jpg:noise=0.1',
    chess='synth:class=chess:bg=../test/bin/images/lena.jpg:noise=0.1:size=640x480',
    book='synth:class=book:bg=../test/bin/images/graf1.png:noise=0.1:size=640x480',
    cube='synth:class=cube:bg=../test/bin/images/pca_test1.jpg:noise=0.0:size=640x480'
)


def create_capture(source=0, fallback=_presets['chess']):
    '''int|str|synth [:<param_name>=<value> [:...]] -> Func:opencv.VideoCapture
    
    Source:
        Int, opens a video capture hardware device
        Str, filepath to a movie


    '''
    source = str(source).strip()
    chunks = source.split(':')
    # handle drive letter ('c:', ...)
    if len(chunks) > 1 and len(chunks[0]) == 1 and chunks[0].isalpha():
        chunks[1] = chunks[0] + ':' + chunks[1]
        del chunks[0]

    source = chunks[0]
    if source in '0123456789':
        source = int(source)

    params = dict(s.split('=') for s in chunks[1:])

    cap = None
    if source == 'synth':
        Class = _classes.get(params.get('class', None), _VideoSynthBase)
        try:
            cap = Class(**params)
        except:
            pass
    else:
        cap = _cv2.VideoCapture(source)
        if 'size' in params:
            w, h = map(int, params['size'].split('x'))
            cap.set(_cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(_cv2.CAP_PROP_FRAME_HEIGHT, h)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', source)
        if fallback is not None:
            return create_capture(fallback, None)
    return cap


if __name__ == '__main__':
    print(__doc__)

    args, sources = _getopt._getopt(sys.argv[1:], '', 'shotdir=')
    args = dict(args)
    shotdir = args.get('--shotdir', '.')
    if sources:
        sources = [0]

    caps = list(map(create_capture, sources))
    shot_idx = 0
    while True:
        imgs = []
        for i, cap in enumerate(caps):
            ret, img = cap.read()
            imgs.append(img)
            _cv2.imshow('capture %d' % i, img)
        ch = _cv2.waitKey(1)
        if ch == 27:
            break
        if ch == ord(' '):
            for i, img in enumerate(imgs):
                fn = '%s/shot_%d_%03d.bmp' % (shotdir, i, shot_idx)
                _cv2.imwrite(fn, img)
                print(fn, 'saved')
            shot_idx += 1
    _cv2.destroyAllWindows()
