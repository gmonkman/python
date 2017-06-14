
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
import opencvlib.histo as histo

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        self.grasspath = _path.normpath(_path.join(self.modpath, 'bin/images/grass.jpg'))
        self.Grass = cv2.imread(self.grasspath)

    #@unittest.skip("Temporaily disabled while debugging")
    def test_VisualColorHisto(self):
        '''test'''

        H = histo.VisualColorHisto(self.Grass)
        cv2.waitKey(0)
        H(cv2.cvtColor(self.Grass, cv2.COLOR_BGR2GRAY))


if __name__ == '__main__':
    unittest.main(verbosity=2)
    
