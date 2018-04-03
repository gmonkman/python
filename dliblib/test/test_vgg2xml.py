
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import dliblib
from dliblib import vgg2xml

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(dliblib.__path__[0]) #root of opencvlib
        self.xmlout = _path.normpath(_path.join(self.module_root, 'test/bin/w300/vgg_landmarks.xml'))
        self.imagepath = _path.normpath(_path.join(self.module_root, 'test/bin/images'))
        self.vggin = _path.normpath(_path.join(self.module_root, 'test/bin/images/vgg_pts.json'))


    #@unittest.skip("Temporaily disabled while debugging")
    def test_vgg2xml(self):
        '''test'''
        iolib.files_delete2(self.xmlout)
        vgg2xml.create_xml(self.xmlout)
        self.assertTrue(iolib.file_exists(self.xmlout))
        iolib.files_delete2(self.xmlout)

        vgg2xml.vgg2xml(self.vggin, self.xmlout)




if __name__ == '__main__':
    unittest.main(verbosity=2)
