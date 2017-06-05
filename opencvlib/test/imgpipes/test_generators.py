# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''unit tests for imgpipes.generators'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path


from opencvlib.view import show
import opencvlib.imgpipes.generators as gnr
import opencvlib.transforms as transforms
from opencvlib.imgpipes import filters
import funclib.iolib as iolib

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        pass


    #@unittest.skip("Temporaily disabled while debugging")
    #DEBUG Double check test_image_pipeline
    def test_RegionPosRandomNeg(self):
        '''test_RegionPosRandomNeg'''
        #Get training region
        vgg_sp = gnr.VGGSearchParams('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler', 'whole', 'bass')
        dk_sp = gnr.DigikamSearchParams(key_value_bool_type='OR', is_train=['head', 'whole'])
        dk_sample = gnr.DigikamSearchParams(key_value_bool_type='OR', species=['bullhuss', 'dab', 'flatfish', 'cod', 'plaice', 'dogfish', 'mini species', 'smoothhound', 'tope', 'whiting', 'pollock'])

        t1 = transforms.Transform(transforms.togreyscale)
        t2 = transforms.Transform(transforms.equalize_adapthist)
        T = transforms.Transforms(None, t1, t2)

        f1 = filters.Filter(filters.is_higher_res, w=100, h=100)
        f2 = filters.Filter(filters.is_lower_res, w=10000, h=10000)
        F = filters.Filters(None, f1, f2)

        Gen = gnr.RegionPosRandomNeg(vgg_sp, dk_sp, dk_sample, F=F, T=T)
        for train, test, dummy in Gen.generate():
            show([train, test])



if __name__ == '__main__':
    unittest.main()
    
