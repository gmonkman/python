
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for voc_utils'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
import opencvlib.imgpipes.voc_utils as voc

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
    def test_funcs(self):
        '''test functions'''
        #voc.list_image_sets()
        l = voc.get_image_url_list('cat', 'train')
        print(l)
        #voc.imgs_from_category('cat','train')




if __name__ == '__main__':
    unittest.main(verbosity=2)
