
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import opencvlib.transforms as transforms
import cv2
import funclib.iolib as iolib
import textract
import textract.tesseractlib as tesslib

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(textract.__path__[0]) #root of opencvlib, uses the package name, not a module
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))
        self.img_mag = _path.normpath(_path.join(self.test_images_path, 'sa0006.jpg'))
        self.img_clean = _path.normpath(_path.join(self.test_images_path, 'clean_text.jpg'))

    #@unittest.skip("Temporaily disabled while debugging")
    def test_to_paragraphs(self):
        '''test'''

        im = cv2.imread('C:/temp/sa6dpi300.jpg')
        im = transforms.resize(im,width=3000)
        cv2.imwrite('C:/temp/sa6big.jpg', im)
        d = tesslib.to_paragraphs(self.img_clean)
        print(d)




if __name__ == '__main__':
    unittest.main(verbosity=2)
