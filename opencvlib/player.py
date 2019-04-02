# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, protected-access
'''
THIS IS THE MAIN PLAYER

Multithreaded video processing
Keys:
    f: framebyframe
    l: loop
    s: snapshot
    escape: exit
    r: restart
    p: pause
    x: xform
    d: detect
'''
from multiprocessing.pool import ThreadPool as _ThreadPool
from collections import deque as _deque
from time import sleep as _sleep
import os.path as _path
from enum import Enum as _Enum


import cv2 as _cv2


from opencvlib import transforms as _transforms
from opencvlib import stopwatch as _stopwatch
from opencvlib import common as _common


import opencvlib.histo as _histo
import opencvlib.display_utils as _display_utils
import funclib.iolib as _iolib


_Keys = _display_utils.KeyBoardInput()

_FUNCTIONS = {'f':'framebyframe', 'l':'loop', 's':'snapshot', 'escape':'exit', 'r':'restart', 'p':'pause', 'x':'xform', 'd':'detect'}

#TODO remove later, just getting it working
class eSource(_Enum):
    '''where did we get the histo'''
    FromFile = 0
    Memory = 1


class MultiProcessStream():
    '''
    Open a movie

    Optionally provide a transformation
    queue (Class:Transforms) to apply
    per frame.
    '''


    _snap_path = _iolib.temp_folder()
    _snap_increment = 0
    _snap_pad = 6

    def __init__(self, source=None, Transforms=None):
        '''(int|str|None, Class:Transforms)

        source:
            capture device number, or filepath to movie
        Transforms:
            Class of Transforms, representing queued transforms
            to be applied per frame.
        '''
        self.signal_strength = _deque(maxlen=10)

        self.subject_hist = []
        self._threadn = _cv2.getNumberOfCPUs()
        self.VideoCapture = None
        self._source = source #holds the full file name of the movie
        self._loop = True
        self._selected_function = ''

        self._frame_out = None #holds the current movie frame, without overlays

        self.Transforms = Transforms if isinstance(Transforms, _transforms.Transforms) else _transforms.Transforms()
        self._xform = False

        self._initialise()

        self._wk_time = 1 #waitkey time

        #mouse selection stuff
        self._region_img = None
        self._region_selection = 0, 0, 0, 0
        self._drag_start = None

        #frame stuff
        self._pending = _deque()
        self._at_end = False
        self._frame_current = 0
        self._buffered_frame_nr = 0
        self._Status = _StatusInfo(self.VideoCapture)
        self.detect = False


#TODO Shoe horned in for demo, will need to do properly at some point
#region backproject
    def load_saved_histos(self):
        '''load saved normalised histos'''

        fld = 'C:/development/python/opencvlib/bin/watershedhisto/*.nrm'
        hists = _histo.hist_load_from_folder(fld)
        for h in hists:
            self.subject_hist.append([h, eSource.FromFile])
        print('Loaded subject histogram(s) from %s' % fld)

    def back_proj(self):
        '''Apply back proj using cached histogram(s)

        Each histogram is used in bkproj
        and the bkproj with the highest match
        is used
        '''

        if not self.subject_hist:
            return
        ihsv = _cv2.cvtColor(self._frame_out, _cv2.COLOR_BGR2HSV)

        bkprojs = [_cv2.calcBackProject([ihsv], (0, 1), b[0], (0, 180, 0, 256), 1)  for b in self.subject_hist]

        sumbp = [bk.sum() for bk in bkprojs]
        i = sumbp.index(max(sumbp))
        bkproj = bkprojs[i]

        disc = _cv2.getStructuringElement(_cv2.MORPH_ELLIPSE, (5, 5))
        _cv2.filter2D(bkproj, -1, disc, bkproj)
        bkproj = _transforms.resize(bkproj, width=400)

        #calc after resize
        ss = ((bkproj != 0).sum() / (bkproj.size*255)) * 100
        self.signal_strength.append(ss)
        if self.signal_strength:
            avg = sum(self.signal_strength)/len(self.signal_strength)

        s = 'Signal:{0:.3f}'.format(avg)

        bkproj = _cv2.cvtColor(bkproj, _cv2.COLOR_GRAY2BGR)
        _display_utils.draw_str(bkproj, 30, 30, s, (0, 255, 255))

        _cv2.imshow('Detect', bkproj)

#endregion


    def __call__(self, source=None, Transforms=None):
        '''(int|str|None, Class:Transforms)

        source:
            capture device number, or filepath to movie
        Transforms:
            Class of Transforms, representing queued transforms
            to be applied per frame.
        '''
        self._source = source
        self.VideoCapture = None
        self.Transforms = Transforms if isinstance(Transforms, _transforms.Transforms) else _transforms.Transforms()
        self._initialise()


    def _initialise(self):
        if not self._source in '0123456789':
            self._source = _path.normpath(self._source)
        self.VideoCapture = _cv2.VideoCapture(self._source)
        self.FrameSpeed = _stopwatch.StopWatch(event_name='imshow')
        self._pending = _deque()
        self._at_end = False
        self._frame_current = 0
        self._buffered_frame_nr = 0
        self._frame_out = None #holds the movie frame
        self._selected_function = ''
        self._buffered_frame_nr = 0
        self.load_saved_histos()


    def _transform(self, img, fr_nr):
        '''(ndarray, int) -> ndarray, int
        perform the transform and pass the frame nr

        Return:
            transformed  image, frame number
        '''
        if self._xform:
            img = self.Transforms.executeQueue(img)
        return img, fr_nr


    #Main play loop
    def play(self):
        '''READ'''
        pool = _ThreadPool(processes=self._threadn)
        is_start = True


        _cv2.namedWindow(self._source, _cv2.WINDOW_NORMAL) #main movie window
        _cv2.namedWindow('region', _cv2.WINDOW_NORMAL) #selected region


        #Progress bars
        _cv2.createTrackbar('frames', self._source, self._frame_current,
                            int(self._Status.total_frames),
                            lambda v: self.tbProgressCallback(v, self))


        _cv2.setMouseCallback(self._source, self.onmouse, self)
        self.FrameSpeed.reset()
        while True:
            #something is queued in pending and if pending
            #is it ready
            while self._pending and self._pending[0].ready():
                frame, self._buffered_frame_nr = self._pending.popleft().get()
                self._frame_out = frame.copy()
                _common.draw_str(frame, 20, 20, "run time (s):  %0.f" % (self.FrameSpeed.run_time))
                _cv2.imshow(self._source, frame)        #show the image
                _cv2.setTrackbarPos('frames', self._source, self._buffered_frame_nr)
                if self.detect and self._buffered_frame_nr%5 == 0:
                    self.back_proj()
                self.FrameSpeed.lap(1)


            #process and add to display queue
            if len(self._pending) < self._threadn:
                self._frame_current = self._Status.frame_next
                ret, raw_frame = self.VideoCapture.read()

                if not ret:
                    self._at_end = True
                    if not self._pending and self._loop: #nothing buffered to show
                        self.set_frame(0)
                    else:
                        break
                else:
                    task = pool.apply_async(self._transform, (raw_frame, self._frame_current))
                    self._pending.append(task)
                    if is_start:
                        _sleep(0.1)
                        is_start = False

            ch = _cv2.waitKey(self._wk_time)
            if ch != 255:
                print(ch)
            #persistent single status changes
            if _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'loop':
                self._loop = not self._loop
                print('loop %s' % self._loop)
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'snapshot':
                self.snap(self._frame_out)
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'exit':
                break
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'restart':
                self.set_frame(0)
                self._pending = _deque()
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'pause':
                self._wk_time = 1 if self._wk_time == 0 else 0
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'framebyframe':
                self._wk_time = 0
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'xform': #stop running transforms
                self._xform = not self._xform
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'detect':
                self.detect = not self.detect

        _cv2.destroyAllWindows()



    #handle region selection
    @staticmethod
    def onmouse(event, x, y, flags, self):
        '''mouse click handler'''

        #print('x:%s, y:%s' % (x, y))
        if event == _cv2.EVENT_LBUTTONDOWN:  #click
            self._wk_time = 0 #pause
            self._pending = _deque()
            self._drag_start = x, y
            self._sel = 0, 0, 0, 0
        elif event == _cv2.EVENT_LBUTTONUP:  #mb release
            if self._region_selection[2] > self._region_selection[0] and self._region_selection[3] > self._region_selection[1]:
                self._region_img = self._frame_out[self._region_selection[1]:self._region_selection[3], self._region_selection[0]:self._region_selection[2]]
                #result = _cv2.matchTemplate(gray, patch, _cv2.TM_CCOEFF_NORMED)
                #result = np.abs(result)**3
                #val, result = _cv2.threshold(result, 0.01, 0, _cv2.THRESH_TOZERO)
                #result8 = _cv2.normalize(
                #   result, None, 0, 255, _cv2.NORM_MINMAX, _cv2.CV_8U)
                _cv2.imshow('region', self._region_img)
            self._drag_start = None
        elif self._drag_start:                    #drag
            # print flags
            if flags & _cv2.EVENT_FLAG_LBUTTON:
                minpos = min(self._drag_start[0], x), min(self._drag_start[1], y)
                maxpos = max(self._drag_start[0], x), max(self._drag_start[1], y)
                self._region_selection = minpos[0], minpos[1], maxpos[0], maxpos[1]
                img = self._frame_out.copy()
                _cv2.rectangle(img, (self._region_selection[0], self._region_selection[1]),
                              (self._region_selection[2], self._region_selection[3]), (0, 255, 255), 1, lineType=_cv2.LINE_AA)
                _cv2.imshow(self._source, img)
            else:
                print("selection is complete")
                self._drag_start = None


    @staticmethod
    def tbProgressCallback(frame_nr, self):
        '''(int)
        '''
        frame_nr = int(frame_nr)

        if abs(self._frame_current - frame_nr) > self._threadn: #size of buffer
            self._pending = _deque() #flush current
            self.VideoCapture.set(_cv2.CAP_PROP_POS_FRAMES, frame_nr)
            self._wk_time = 0
            ret, read = self.VideoCapture.read()
            if ret:
                _common.draw_str(read, 20, 20, 'Press "p" to play')
                _cv2.imshow(self._source, read)
        self._at_end = (frame_nr == self._Status.total_frames - 1)



    def set_frame(self, frame_nr):
        '''(int|float|str)
        Set the net frame to play.

        Supports the following

        frame_nr
            str
                'start', 'end'
            int
                set to that frame
            float 0-1
                set as that proportion
        '''

        if abs(self._frame_current - frame_nr) > 1:
            self._pending = _deque() #flush current

        if frame_nr in [1, 0]:
            frame_nr = int(frame_nr)

        if isinstance(frame_nr, str):
            if frame_nr in ('end', 'finish'):
                f_nr = self._Status.total_frames - 1
                self._at_end = True
            elif frame_nr in ('start', 'begin', 'begining'):
                f_nr = 0
                self._at_end = False
        elif isinstance(frame_nr, int):
            f_nr = frame_nr
            self._at_end = (frame_nr == self._Status.total_frames - 1)
        elif isinstance(frame_nr, float):
            self._at_end = (frame_nr == 1)
            if 0 <= frame_nr <= 1:
                f_nr = (self._Status.total_frames - 1) * frame_nr

        self._frame_current = f_nr
        self.VideoCapture.set(_cv2.CAP_PROP_POS_FRAMES, f_nr)


    @staticmethod
    def snap(img, silent=False):
        '''(ndarray) -> str, str
        Take a snapshot
        img:
            Image as an ndarray

        Returns:
            filename, filepath
        '''
        fname = str(MultiProcessStream._snap_increment).zfill(MultiProcessStream._snap_pad) + '.jpg'
        path_ = _path.normpath(MultiProcessStream._snap_path)
        fullname = _path.normpath(_path.join(MultiProcessStream._snap_path, fname))
        _cv2.imwrite(fullname, img)
        MultiProcessStream._snap_increment += 1
        if not silent:
            s = 'snapshot taken folder:%s name:%s' % (fullname, fname)
            print(s)
        return fname, path_




class _StatusInfo():
    '''handle FPS
    '''
    def __init__(self, cap):
        '''(cv2.VideoCapture) -> void
        '''
        self._total_frames = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT))
        self._fps_native = cap.get(_cv2.CAP_PROP_FPS)
        self._length_seconds = self._total_frames/self._fps_native
        self._native_x = int(cap.get(_cv2.CAP_PROP_FRAME_WIDTH))
        self._native_y = int(cap.get(_cv2.CAP_PROP_FRAME_HEIGHT))
        self._target_fps = self._fps_native
        self.VideoCapture = cap


    @property
    def frame_current(self):
        '''current frame nr,
        or the last frame nr read'''
        return int(self.VideoCapture.get(_cv2.CAP_PROP_POS_FRAMES) - 1)

    @property
    def frame_next(self):
        '''next frame nr to be read'''
        return int(self.VideoCapture.get(_cv2.CAP_PROP_POS_FRAMES))

    @property
    def position_as_ratio(self):
        '''how far through as a ratio 0 - 1'''
        if self.total_frames != 0:
            return self.frame_current/self.total_frames
        return 0

    @property
    def position_milliseconds(self):
        '''how far through in milliseconds'''
        return self.VideoCapture.get(_cv2.CAP_PROP_POS_MSEC)

    @property
    def position_seconds(self):
        '''how far through in seconds'''
        return self.VideoCapture.get(_cv2.CAP_PROP_POS_MSEC/1000)

    @property
    def target_fps(self):
        '''target_fps getter'''
        return self._target_fps
    @target_fps.setter
    def target_fps(self, target_fps):
        '''target_fps setter'''
        self._target_fps = target_fps

    @property
    def total_frames(self):
        '''total_frames getter'''
        return self._total_frames

    @property
    def fps_native(self):
        '''fps_native getter'''
        return self._fps_native

    @property
    def length_seconds(self):
        '''length_seconds getter'''
        return self._length_seconds




if __name__ == '__main__':
    print(__doc__)
