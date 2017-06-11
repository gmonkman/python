# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Multithreaded video processing
'''
from multiprocessing.pool import ThreadPool as _ThreadPool
from collections import deque as _deque
from time import sleep as _sleep
import os.path as _path

import cv2 as _cv2
import numpy as _np

#from common import draw_str as _draw_str
from opencvlib import transforms as _transforms
from opencvlib import stopwatch as _stopwatch
import opencvlib.display_utils as _display_utils
import funclib.iolib as _iolib
from funclib.baselib import isempty as _isempty

_Keys = _display_utils.KeyBoardInput()

_FUNCTIONS = {'t':'forward/back', 'l':'loop', 's':'snapshot', 'escape':'exit', 'r':'restart', 'p':'pause'}



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
    

#        def draw(self, img, x=20, y=20):
 #               img = _draw_str(img, (x, y), "latency        :  %.1f ms" %
          #              (fps.latency.value * 1000))

#_draw_str(frame, (20, 60), "frame interval :  %.1f ms" %
            #  (fps.frame_interval.value * 1000))

    def __init__(self, source=None, Transforms=None):
        '''(int|str|None, Class:Transforms)
        
        source:
            capture device number, or filepath to movie
        Transforms:
            Class of Transforms, representing queued transforms
            to be applied per frame.
        '''
        self._source = source
        self.VideoCapture = None
        self._at_end = False
        self._selected_function = ''
        self._loop = False
        self._reverse = False #play direction
        self._frame_out = None #holds the movie frame
        self.Transforms = Transforms if isinstance(Transforms, _transforms.Transforms) else _transforms.Transforms()
        self._initialise()
        self._Status = _StatusInfo(self.VideoCapture)
        self.wk_time = 1 #waitkey time

        #mouse selection stuff
        self._region_img = None
        self._region_selection = 0, 0, 0, 0
        self._drag_start = None


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


    def _transform(self, frame):
        '''(ndarray, int) -> ndarray, int
        Pass in image and result and
        return them after applying
        queued transforms in self.Transforms
        '''
        frame = self.Transforms.executeQueue(frame)
        return frame


    @staticmethod
    def testprocess(frame):
        return frame
            

    #Main play loop
    def play(self):
        '''READ'''
        threadn = _cv2.getNumberOfCPUs()
        pool = _ThreadPool(processes=threadn)
        pending = _deque()
        is_start = True
        self.FrameSpeed.reset()
        _cv2.namedWindow(self._source, _cv2.WINDOW_NORMAL)
        _cv2.namedWindow('region', _cv2.WINDOW_NORMAL)

        _cv2.createTrackbar('Frames', self._source, 0, 
                            int(self._Status.total_frames), 
                            lambda v: self.tbProgressCallback(v, self))

        cv2.setMouseCallback(self._source, onmouse, self)


        while True:

            assert isinstance(self._region_img, _np.ndarray)

            if self._region_img.size:
                _cv2.imshow('region', self_region_img)


            #something is queued in pending and if pending
            #is it ready
            while pending and pending[0].ready():
                frame = pending.popleft().get()
                self._frame_out = frame.copy()
                _cv2.imshow(self._source, frame)        #show the image
                self.FrameSpeed.lap(1)
                if self._at_end:
                    if not self._loop:
                        break
                    else:
                        self.set_frame('restart')

            #process and add to display queue
            if len(pending) < threadn:
                if self._reverse:
                    self.set_frame(self._Status.frame_current - 2)
                ret, raw_frame = self.VideoCapture.read() 
                if not ret:
                    self._at_end = True
                    if not pending: #nothing buffered to show
                        if self._loop and self._reverse:
                            self.set_frame('end')
                        elif self._loop and not self._reverse:
                            self.set_frame('start')
                        else:
                            break
                    else:
                        break
                else:
                    raw_frame_copy = raw_frame.copy()
                    task = pool.apply_async(self.Transforms.executeQueue, (raw_frame_copy,))
                    pending.append(task)
                    if is_start:
                        _sleep(0.1)
                        is_start=False

            ch = _cv2.waitKey(self.wk_time)
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
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'forward/back':
                self._reverse = not self._reverse
                pending = _deque()
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'restart':
                self.set_frame(0)
                pending = _deque()
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'pause':
                self.wk_time = 1 if self.wk_time == 0 else 0


        _cv2.destroyAllWindows()



#handle region selection
def onmouse(event, x, y, flags, param, self):
    self.wk_time = 0 #pause
    if event == _cv2.EVENT_LBUTTONDOWN:  #click
        drag_start = x, y
        self._sel = 0, 0, 0, 0
    elif event == _cv2.EVENT_LBUTTONUP:  #mb release
        if self._region_selection[2] > self._region_selection[0] and self._region_selection[3] > self._region_selection[1]:
            self._region_img = self.frame_out[self._region_selection[1]:self._region_selection[3], self._region_selection[0]:self._region_selection[2]]
            #result = _cv2.matchTemplate(gray, patch, _cv2.TM_CCOEFF_NORMED)
            #result = np.abs(result)**3
            #val, result = _cv2.threshold(result, 0.01, 0, _cv2.THRESH_TOZERO)
            #result8 = _cv2.normalize(
             #   result, None, 0, 255, _cv2.NORM_MINMAX, _cv2.CV_8U)
        self._drag_start = None
    elif drag_start:                    #drag
        # print flags
        if flags & _cv2.EVENT_FLAG_LBUTTON:
            minpos = min(drag_start[0], x), min(drag_start[1], y)
            maxpos = max(drag_start[0], x), max(drag_start[1], y)
            self._region_selection = minpos[0], minpos[1], maxpos[0], maxpos[1]
            img = _cv2.cvtColor(gray, _cv2.COLOR_GRAY2BGR)
            _cv2.rectangle(img, (self._region_selection[0], self._region_selection[1]),
                          (self._region_selection[2], self._region_selection[3]), (0, 255, 255), 1)
            _cv2.imshow("gray", img)
        else:
            print("selection is complete")
            drag_start = None

    
    @staticmethod
    def tbProgressCallback(frame_nr, self):
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
        if frame_nr == 1 or frame_nr == 0:
            frame_nr = int(frame_nr)

        if isinstance(frame_nr, str):
            if frame_nr in ('end', 'finish'):
                assert isinstance(self._Status, _StatusInfo)
                f_nr = self._Status.total_frames - 1
                self._at_end = not self._reverse
            elif frame_nr in ('start', 'begin', 'begining'):
                f_nr = 0
                self._at_end = self._reverse
        elif isinstance(frame_nr, int):
            f_nr = frame_nr
            self._at_end = (frame_nr == self._Status.total_frames - 1) 
        elif isinstance(frame_nr, float):
            self._at_end = (frame_nr == 1) and not self._reverse
            if 0 <= frame_nr <= 1:
                f_nr = (self._Status.total_frames - 1) * frame_nr

        self.VideoCapture.set(_cv2.CAP_PROP_POS_FRAMES, f_nr)



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
        if frame_nr == 1 or frame_nr == 0:
            frame_nr = int(frame_nr)

        if isinstance(frame_nr, str):
            if frame_nr in ('end', 'finish'):
                assert isinstance(self._Status, _StatusInfo)
                f_nr = self._Status.total_frames - 1
                self._at_end = not self._reverse
            elif frame_nr in ('start', 'begin', 'begining'):
                f_nr = 0
                self._at_end = self._reverse
        elif isinstance(frame_nr, int):
            f_nr = frame_nr
            self._at_end = (frame_nr == self._Status.total_frames - 1) 
        elif isinstance(frame_nr, float):
            self._at_end = (frame_nr == 1) and not self._reverse
            if 0 <= frame_nr <= 1:
                f_nr = (self._Status.total_frames - 1) * frame_nr

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
        '''current frame nr'''
        return self.VideoCapture.get(_cv2.CAP_PROP_POS_FRAMES) - 1

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
