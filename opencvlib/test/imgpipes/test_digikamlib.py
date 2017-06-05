# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''unit tests for digikamlib which
is used to interact with the digikam
sqlite database'''

import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path


import opencvlib.imgpipes.digikamlib as digikamlib
import funclib.iolib as iolib

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)


    #@unittest.skip("Temporaily disabled while debugging")
    def test_imagesbytags(self):
        '''test_imagesbytags'''
        image_paths = digikamlib.ImagePaths(
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
        lst = image_paths.images_by_tags(
            filename='10150756_851703354845619_1559938228217274444_n.jpg',
            album_label='images',
            relative_path='bass/angler',
            species='bass')
        print(str(len(lst)))



if __name__ == '__main__':
    unittest.main()
    
