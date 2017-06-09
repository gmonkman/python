# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Multithreaded video processing
'''
from multiprocessing.pool import ThreadPool as _ThreadPool
from collections import deque as _deque

import os.path as _path

import cv2 as _cv2

from common import draw_str as _draw_str
from opencvlib import transforms as _transforms



class MultiProcessStream():
    '''
    Open a movie

    Optionally provide a transformation
    queue (Class:Transforms) to apply
    per frame.
    '''

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
        self._source = source
        self._open_source()


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
        self._open_source()


    def _open_source(self):
        if not self.source in '0123456789':
            self.source = _path.normpath(self.source)
        self.VideoCapture = _cv2.VideoCapture(self.source)


    def _transform(self, frame):
        '''(ndarray, int) -> ndarray, int
        Pass in image and result and
        return them after applying
        queued transforms in self.Transforms
        '''
        assert isinstance(self.Transforms, _transforms.Transforms)
        frame = self.Transforms.executeQueue(frame)
        return frame


    def read(self):
        '''READ'''
        threadn = _cv2.getNumberOfCPUs()
        pool = _ThreadPool(processes=threadn)
        pending = _deque()


        while True:

            #something is queued in pending and if pending
            #is it ready
            while pending and pending[0].ready():
                frame = pending.popleft()
                _cv2.imshow('threaded video', frame)        #show the image

            if len(pending) < threadn:
                dummy, frame = self.VideoCapture.read() #get frame
                task = pool.apply_async(self._transform, (frame.copy())) #pass frame and time
                pending.append(task)

            ch = _cv2.waitKey(1)
            if ch == 27: break

        _cv2.destroyAllWindows()





#class _Widget():
#    '''widgets'''


#class HSV():


#class Histogram()

#class RegionSelector


if __name__ == '__main__':
    print(__doc__)
