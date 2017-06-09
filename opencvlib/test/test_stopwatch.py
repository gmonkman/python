# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''unit tests for features'''
import unittest
import time

from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib


import opencvlib.stopwatch as stopwatch


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)

   

    #@unittest.skip("Temporaily disabled while debugging")
    def test_func(self):
        '''testfunc'''
        SW = stopwatch.StopWatch(event_name='test')
        time.sleep(0.5)    
        for dummy in range(10):
            SW.lap(10)
            time.sleep(0.5)
            print(SW.Times[-1])
        print('Event rate global:', SW.event_rate_global)

        
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
    
