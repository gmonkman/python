# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import funclib.iolib as iolib
import opencvlib.imgpipes.vgg as vgg

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)


    #@unittest.skip("Temporaily disabled while debugging")
    def test_points(self):
        '''test points generated for images
        '''
        vgg_path = r'C:\development\python\opencvlib\test\bin\images\vgg_rotations.json'
        vgg.load_json(vgg_path)
        allpts = []
        for img in vgg.imagesGenerator():
            pts = img.image_points
            allpts.append(pts)  #making a 3-deep list
        self.assertListEqual(allpts[0], [[856, 410]])


if __name__ == '__main__':
    unittest.main(verbosity=2)

