# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''dealing with image streams, ie movies!'''
from threading import Thread as _Thr
#import sys as _sys

from queue import Queue as _Queue

import cv2 as _cv2

#from opencvlib import Log as _Log

class _Frame():
    '''class representing a frame in the buffer'''
    def __init__(self, Frame, frame_nr):
        self.img = Frame
        self.frame_nr = frame_nr


class BufferedFrameGenerator():
    '''yeild frames
    '''
    def __init__(self, filepath, queue_size=128):
        '''(str) -> void
        '''
        self.filepath = filepath
        self.queue_size = queue_size

        self.position_in_ms = 0
        self.position_in_secs = 0
        self.current_frame = 0
        self.position_ratio = 0


        #queue stuff
        self.stopped = False
        self.Q = _Queue(maxsize=queue_size)
        self.V = _cv2.VideoCapture(filepath)
        self.fps = self.V.get(_cv2.CAP_PROP_FPS)
        self.frames_total = int(self.V.get(_cv2.CAP_PROP_FRAME_COUNT))
        self.height = self.V.get(_cv2.CAP_PROP_FRAME_HEIGHT)
        self.width = self.V.get(_cv2.CAP_PROP_FRAME_WIDTH)



    def __repr__(self):
        '''__repr__
        '''
        s = 'filepath: {0!s}\n' \
        'fps: {1!s}\n' \
        'res: {2!s}x{3}\n' \
        'current_frame: {4!s}\n' \
        'position(secs): {5!s}' \
        .format(self.filepath, self.fps, self.width, self.height, self.current_frame, self.position_ratio)
        return s


    def start(self):
        '''start a thread seperate from the main thread'''
        t = _Thr(target=self._update, args=())
        t.daemon = False
        t.start()
        return self


    def _update(self):
        '''populate the queue'''
        while True:
            #_time.sleep(0.0005)

            if self.Q.full():
                break
            else:
                ret, frame = self.V.read()
                if ret:
                    self.current_frame = self.V.get(_cv2.CAP_PROP_POS_FRAMES) - 1
                    f = _Frame(frame, self.current_frame)
                    self.Q.put(f)
                else:
                    self._stop()
                    return


    def read(self):
        '''get next frame'''
        if self.Q.empty():
            return
        else:
            F = self.Q.get()
            assert isinstance(F, _Frame)
            self.current_frame = F.frame_nr
            return F.img


    def queued(self):
        '''return true if still more to read'''
        return not self.stopped


    def _stop(self):
        '''stop reading on the queue thread'''
        self.stopped = True
        self.V.release()


    def _set_stats(self, F):
        '''(class:_Frame)
        Calculate states based on a frame
        '''
        assert isinstance(F, _Frame)
        self.position_ratio = F.frame_nr/self.frame_count if self.frame_count > 0 else 0
        self.position_in_ms = F.frame_nr/(self.fps*1000) if self.fps > 0 else 0
        self.position_in_secs = self.position_in_ms/1000




    def getframe(self, setpos=True, **kwargs):
        '''(bool, kwargs) -> ndarray
        Get a frame using the frame number, or
        milliseconds

        setpos:
            leaves the position at the requested frame,
            otherwise returns to the current position
        frame=<int>
            
        ms=<int>
        
        '''
        pass
        #if setpos:
         #   self.V
        #else:
         #   self.current_frame = self.V.get(_cv2.CAP_PROP_POS_FRAMES) - 1
        


    def setframe(self, **kwargs):
        '''
        Get a frame using the frame number, or
        milliseconds

        frame=<int>
            
        ms=<int>
        '''
        pass


    def reset(self):
        '''reset stats'''
        self.filepath = None
        self.fps = None
        self.width = None
        self.height = None
        self.position_in_ms = None
        self.position_in_secs = None
        self.current_frame = None
