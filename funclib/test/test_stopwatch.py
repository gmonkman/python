# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''unit tests for features'''
import unittest
import time

from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib


import funclib.stopwatch as stopwatch


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)



    @unittest.skip("Temporaily disabled while debugging")
    def test_func(self):
        '''testfunc'''
        SW = stopwatch.StopWatch(event_name='test')
        time.sleep(3)
        SW.lap(3)
        print(SW)
        self.assertAlmostEqual(SW.event_rate_last, 1, places=2)
        print(SW.remaining(10))
        self.assertAlmostEqual(SW.remaining(10), SW.event_rate_last*10, places=2)
        print(SW)
        print(SW.Times[-1])
        time.sleep(7)
        SW.lap(97) #time 10secs, ticks 100
        self.assertAlmostEqual(SW.event_rate_last, 7/97, places=2)
        self.assertAlmostEqual(SW.event_rate_global, 10/100, places=2)
        for dummy in range(10):
            SW.lap(10)
            time.sleep(0.5)
            print(SW.Times[-1])
        print('Event rate global:', SW.event_rate_global)

    #@unittest.skip("Temporaily disabled while debugging")
    def test_func1(self):
        '''testfunc'''
        SW = stopwatch.StopWatch(event_name='test')
        for dummy in range(6):
            time.sleep(dummy)
            time.sleep(1)
            SW.lap()
            print(SW.Times[-1])

        print('Event rate global:', SW.event_rate_global)
        print('Event rate smoothed:', SW.event_rate_last_smoothed)
        print('Event rate:', SW.event_rate_last)

        print('Pretty remaining (100) smoothed', SW.pretty_remaining(100))
        print('Pretty remaining (100) unsmoothed', SW.pretty_remaining(100, use_smoothed=False))

        print('Pretty remaining (1) smoothed', SW.pretty_remaining(1))
        print('Pretty remaining (1) unsmoothed', SW.pretty_remaining(1))


if __name__ == '__main__':
    unittest.main(verbosity=2)
