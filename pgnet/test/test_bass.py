#pylint: skip-file
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path


import tensorflow as tf
import tensorflow.contrib.eager as tfe
tfe.enable_eager_execution()


import funclib.iolib as iolib
import opencvlib

import pgnet.inputs.bass as bass


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(opencvlib.__path__[0]) #root of opencvlib
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))
        self.csv_path = _path.normpath("C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi")



    #@unittest.skip("Temporaily disabled while debugging")
    def test_bass(self):
        bass.init_()
        lbls = bass.BassTrain.Tlabels
        imgs = bass.BassTrain.Timages
        iolib.wait_key('\nPress any key to stop.')


if __name__ == '__main__':
    unittest.main(verbosity=2)

