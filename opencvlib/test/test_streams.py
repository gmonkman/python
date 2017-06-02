'''unit tests for streas.py'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import time
import cv2
#import numpy as np


import opencvlib.streams as streams
import funclib.iolib as _iolib


class Test(unittest.TestCase):
    '''unittest for streams'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.streampath = _path.normpath(_path.join(self.modpath, 'movie/test-mpeg_512kb.mp4'))
        self.output_folder = _path.normpath(_path.join(self.modpath, 'output'))


    def test_BufferedFrameGenerator(self):
        '''test'''
        BFG = streams.BufferedFrameGenerator(self.streampath)
        BFG.start()
        
        start_time = time.time
        while True:
            img = BFG.read()
            cv2.putText(img, "Queue Size: {}".format(BFG.Q.qsize()),
		        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	

            if img is None:
                break
            cv2.imshow('Frame', img)
            cv2.waitKey(1)



        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

if __name__ == '__main__':
    unittest.main()
