
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import text2digits
from text2digits import text2digits as t2d

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(text2digits.__path__[0]) #root of text2digits
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))




    #@unittest.skip("Temporaily disabled while debugging")
    def test_convert(self):
        T = t2d.Text2Digits()
        T.convert('IV')





if __name__ == '__main__':
    unittest.main(verbosity=2)

