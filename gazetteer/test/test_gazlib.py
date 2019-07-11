
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import gazetteer
import gazetteer.gazlib as gazlib
import gazetteerdb.model as _model


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(gazetteer.__path__[0]) #root of opencvlib





    #@unittest.skip("Temporaily disabled while debugging")
    def test_lookup_geograph(self):
        '''test'''
        #rows = gazlib.lookup(_model.t_v_LK, 'safadadasd')
        #self.assertEqual(rows.count(), 0)
        #rows = gazlib.lookup(_model.t_v_LK, 'Bottom of the Stairs')
        pass



if __name__ == '__main__':
    unittest.main(verbosity=2)
