# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, no-self-use

'''unit tests for the VGG module, used to read VGG json files'''

import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

from funclib import iolib

import opencvlib.imgpipes.vgg as vgg
import opencvlib as _opencvlib


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.this_file_path)

        self.module_root = _path.normpath(_opencvlib.__path__[0]) #root of opencvlib



    #@unittest.skip("Temporaily disabled while debugging")
    def test_vgg(self):
        '''test_vgg'''
        vgg.load_json(
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json')

        img = vgg.Image(
            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass' \
            '/angler/10150756_851703354845619_1559938228217274444_n.jpg'
            )
        assert isinstance(img, vgg.Image)
        for subject in img.subjects_generator('bass'):
            assert isinstance(subject, vgg.Subject)
            for region in subject.regions_generator():
                assert isinstance(region, vgg.Region)
                print(region.species, region.part, region.shape)



if __name__ == '__main__':
    unittest.main()
