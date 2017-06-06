
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib

import opencvlib.display_utils as du
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
    def test_KeyBoardInput(self):
        '''test'''
        KBI = du.KeyBoardInput()
        key, dummy = show(self.I)
        print(KBI.check_pressed_key(du.eSpecialKeys.backspace, key))
        print(KBI.check_pressed_key(du.eSpecialKeys.escape, key))
        print(KBI.check_pressed_key(du.eSpecialKeys.return_, key))
        print(KBI.check_pressed_key(du.eSpecialKeys.space, key))
        print(KBI.check_pressed_key(du.eSpecialKeys.tab, key))
        print(KBI.check_pressed_key(du.eSpecialKeys.unknowable, key))
        print(KBI.check_pressed_key('a', key))
        print(KBI.check_pressed_key('A', key))

        key, dummy = show(self.I, waitsecs=1)
        print('showing waitsecs=1')
        self.assertTrue(KBI.check_pressed_key(du.eSpecialKeys.none, key))

        key, dummy = show(self.I)
        print(KBI.get_pressed_key(key))
        pass



if __name__ == '__main__':
    unittest.main()
    
