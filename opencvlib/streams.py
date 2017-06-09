# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''dealing with image streams, ie movies!'''
from threading import Thread as _Thr
from queue import Queue as _Queue

import cv2 as _cv2
import numpy as _np
#from opencvlib import Log as _Log

class _Frame():
    '''class representing a frame in the buffer'''
    def __init__(self, Frame, frame_nr):
        self.img = Frame
        self.frame_nr = frame_nr


class BufferedFrameGenerator():
    '''yield frames using a buffer
    and threading
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


def play(moviefile, title='movie'):
    '''(str, str, int|None) -> void
    Play a movie without buffering
    
    title:
        window title
    '''
    cap = _cv2.VideoCapture(moviefile)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _cv2.namedWindow(title, _cv2.WINDOW_NORMAL)
        #_cv2.resizeWindow(title, new_w, new_h)
        _cv2.imshow(title, frame)

        if _cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    _cv2.destroyAllWindows()



def playb(moviefile, title='movie', buffer=128):
    '''(str, str, int|None) -> void
    Play a movie with buffering
    
    title:
        window title
    buffer:
        Number of frames to buffer, if
        None, no buffer is used
    '''
    #https://github.com/maximus009/VideoPlayer/blob/master/new_test_3.py


    _cv2.namedWindow(title)
    _cv2.moveWindow(title, 250, 150)
    _cv2.namedWindow('controls')
    _cv2.moveWindow('controls', 250, 50)

    controls = _np.zeros((50, 750), _np.uint8)
    _cv2.putText(controls, 'W/w: Play, S/s: Stay, A/a: Prev, D/d: Next, E/e: Fast, Q/q: Slow, Esc: Exit', (40, 20), _cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)

    BFG = BufferedFrameGenerator(moviefile)
    BFG.start()
        

    while True:
        img = BFG.read()
        _cv2.putText(img, "Queue Size: {}".format(BFG.Q.qsize()),
		    (10, 30), _cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	

        if img is None:
            break
        _cv2.imshow(title, img)
        _cv2.waitKey(1)
