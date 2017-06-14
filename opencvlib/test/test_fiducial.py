
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
import opencvlib.fiducial as fid
from opencvlib.view import show

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)



    #@unittest.skip("Temporaily disabled while debugging")
    def test_getmarker(self):
        '''test'''
        for n in range(50):
            s = _path.join('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/fudicial', '%s.jpg' % n)
            m = fid.getmarker(n,200,20,saveas=s)
            print('Saved marker as %s' % s)



if __name__ == '__main__':
    unittest.main(verbosity=2)
    
