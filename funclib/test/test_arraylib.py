
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import funclib.arraylib as arraylib
import numpy as np
import funclib

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(funclib.__path__[0]) #root of opencvlib
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))




    #@unittest.skip("Temporaily disabled while debugging")
    def test_vstackt_hstackt(self):
        a = [np.ones((100, 100, 3)), np.ones((200, 200, 3)), np.ones((300, 300, 3))]

        m = arraylib.hstackt(a)
        self.assertTupleEqual(m.shape, (100, 600, 3))

        m = arraylib.vstackt(a)
        self.assertTupleEqual(m.shape, (600, 100, 3))




if __name__ == '__main__':
    unittest.main(verbosity=2)

