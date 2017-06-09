# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Multithreaded video processing
'''
from multiprocessing.pool import ThreadPool as _ThreadPool
from collections import deque as _deque

import os.path as _path

import cv2 as _cv2

#from common import draw_str as _draw_str
from opencvlib import transforms as _transforms
from opencvlib import stopwatch as _stopwatch
import opencvlib.display_utils as _display_utils
import funclib.iolib as _iolib
from funclib.baselib import isempty as _isempty

_Keys = _display_utils.KeyBoardInput()

_FUNCTIONS = {'t':'forward/back', 'l':'loop', 's':'snapshot', 'escape':'exit', 'r':'restart'}



class MultiProcessStream():
    '''
    Open a movie

    Optionally provide a transformation
    queue (Class:Transforms) to apply
    per frame.
    '''
    
    
    snap_path = _iolib.temp_folder()
    snap_increment = 0
    snap_pad = 6
    

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
        self.Transforms = Transforms
        self._at_end = False
        self._selected_function = ''
        self._loop = False
        self._reverse = False #play direction
        self.frame_out = None
        self._initialise()
        self.Status = _StatusInfo(self.VideoCapture)


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
        self.Transforms = Transforms
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
        assert isinstance(self.Transforms, _transforms.Transforms)
        frame = self.Transforms.executeQueue(frame)
        return frame



            

    #Main play loop
    def play(self):
        '''READ'''
        threadn = _cv2.getNumberOfCPUs()
        pool = _ThreadPool(processes=threadn)
        pending = _deque()
        wk_time = 1

        self.FrameSpeed.reset()
        while True:
            #something is queued in pending and if pending
            #is it ready
            while pending and pending[0].ready():
                frame = pending.popleft()
                self.frame_out = frame
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
                    self.VideoCapture.set(self.Status.frame_current - 2)
                ret, raw_frame = self.VideoCapture.read() 
                if not ret:
                    self._at_end = True
                else:
                    task = pool.apply_async(self._transform, (raw_frame.copy()))
                    pending.append(task)
            
            ch = _cv2.waitKey(wk_time)

            #persistent single status changes
            if _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'loop':
                self._loop = not self._loop
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'snap':
                fname, fpath = self.snap(self.frame_out)
                s = 'snapshot taken folder:%s name:%s' % (fpath, fname)
                print(s)
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'escape':
                break
            elif _FUNCTIONS.get(_Keys.get_pressed_key(ch)) == 'forward/back':
                self._reverse = not self._reverse
                pending = _deque()


        _cv2.destroyAllWindows()



    @staticmethod
    def snap(img):
        '''(ndarray) -> str, str
        Take a snapshot
        img:
            Image as an ndarray

        Returns:
            filename, filepath
        '''
        fname = str(MultiProcessStream.snap_increment).zfill(MultiProcessStream.snap_pad) + '.jpg'
        path_ = _path.normpath(MultiProcessStream.snap_path)
        fullname = _path.normpath(_path.join(MultiProcessStream.snap_path, fname))
        _cv2.imwrite(fname, fullname)
        return fname, path_





class _StatusInfo():
    '''handle FPS
    '''
    def __init__(self, cap):
        '''(cv2.VideoCapture) -> void
        '''
        self._total_frames = cap.get(_cv2.CAP_PROP_FRAME_COUNT)
        self._fps_native = cap.get(_cv2.CAP_PROP_FPS)
        self._length_seconds = self._total_frames/self._fps_native
        self._native_x = int(cap.get(_cv2.CAP_PROP_FRAME_WIDTH))
        self._native_y = int(cap.get(_cv2.CAP_PROP_FRAME_HEIGHT))
        self._target_fps = self._fps_native
        self.VideoCapture = cap


    @property
    def frame_current(self):
        '''current frame nr'''
        return self.VideoCapture.get(_cv2.CAP_PROP_POS_FRAMES)

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
