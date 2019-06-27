# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable, unused-import, missing-docstring
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import nlp
import nlp.clean as clean

class Test(unittest.TestCase):
    '''unittest for keypoints'''


    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(nlp.__path__[0]) #root of opencvlib




    #@unittest.skip("Temporaily disabled while debugging")
    def test_clean(self):
        '''test'''
        s = clean.clean("this weren't right good at st. albans <>\next\next\n", tolower=True)
        print(s)


if __name__ == '__main__':
    unittest.main(verbosity=2)
