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
    def test_images_by_tags_or(self):
        '''test_imagesbytags'''
        ImgP = digikamlib.ImagePaths('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
        lst = ImgP.images_by_tags_or(
            album_label='images',
            relative_path='bass/angler',
            species=['bass', 'pollock'])
        print(str(len(lst)))


    #@unittest.skip("Temporaily disabled while debugging")
    def test_images_by_tags_outer_and_inner_or(self):
        '''test_imagesbytags'''
        ImgP = digikamlib.ImagePaths('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
        lst = ImgP.images_by_tags_outerAnd_innerOr(
            album_label='images',
            relative_path='bass/angler',
            species=['bass', 'pollock'], pitch=['0', '45', '180'], roll='0', yaw=['0', '180'])
        print(str(len(lst)))


    #@unittest.skip("Temporaily disabled while debugging")
    def test_images_by_tags_outer_and(self):
        '''test_imagesbytags'''
        ImgP = digikamlib.ImagePaths('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
        lst = ImgP.images_by_tags_outerAnd_innerOr(
            album_label='images',
            relative_path='bass/angler',
            species='bass', pitch='0')
        print(str(len(lst)))

if __name__ == '__main__':
    unittest.main()
    