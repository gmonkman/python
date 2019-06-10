
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import gazetteerdb.gaz as gaz
import gazetteerdb.model as _model
import gazetteerdb

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(gazetteerdb.__path__[0]) #root of opencvlib





    #@unittest.skip("Temporaily disabled while debugging")
    def test_(self):
        '''test'''
        s = 'Southern'
        gaz.get_by_ifca(s)
        print(len(s))
        



if __name__ == '__main__':
    unittest.main(verbosity=2)

