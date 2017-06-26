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


    #DEBUG Double check test_image_pipeline
    #@unittest.skip("Temporaily disabled while debugging")
    def test_RegionPosRandomNeg(self):
        '''test_RegionPosRandomNeg'''
        #Get training region
        vgg_sp = gnr.VGGSearchParams('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler', 'whole', 'bass')
        dk_sp = gnr.DigikamSearchParams(search_type=gnr.eDigiKamSearchType.innerOr_outerAnd, is_train='whole', fins='dorsal_spiny')
        dk_sample = gnr.DigikamSearchParams(search_type=gnr.eDigiKamSearchType.innerOr_outerAnd, species=['bullhuss', 'dab', 'flatfish', 'cod', 'plaice', 'dogfish', 'mini species', 'smoothhound', 'tope', 'whiting', 'pollock'])

        T = None
        F = None

        #bw =  transforms.Transform(transforms.togreyscale)
        #eq = transforms.Transform(transforms.equalize_hist)
        #T = transforms.Transforms(None, bw, eq)

        f1 = filters.Filter(filters.is_higher_res, w=100, h=100)
        f2 = filters.Filter(filters.is_lower_res, w=10000, h=10000)
        F = filters.Filters(None, f1, f2)

        Gen = gnr.RegionPosRandomNeg(vgg_sp, dk_sp, dk_sample, F=F, T=T)
        for train, test, dict_out in Gen.generate():
            pos_path = dict_out['imgpath']
            neg_path = dict_out['region_img_path']
            show([train, test])


    @unittest.skip("Temporaily disabled while debugging")
    def test_VGGRegions(self):
        '''test vggregions'''
        #Get training region
        vgg_sp = gnr.VGGSearchParams('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler', 'whole', 'bass')
        #TODO Double check boolean handling
        dk_sp = gnr.DigikamSearchParams(search_type=gnr.eDigiKamSearchType.innerOr_outerAnd, pitch='0', yaw='180', roll='0')

        #t1 = transforms.Transform(transforms.togreyscale)
        #t2 = transforms.Transform(transforms.equalize_adapthist)
        #T = transforms.Transforms(None, t1, t2)

        #f1 = filters.Filter(filters.is_higher_res, w=100, h=100)
        #f2 = filters.Filter(filters.is_lower_res, w=10000, h=10000)
        #F = filters.Filters(None, f1, f2)

        Gen = gnr.VGGRegions(dk_sp, vgg_sp, transforms=None, filters=None)
        for img, dummy, dummy1 in Gen.generate():
            show(img)




if __name__ == '__main__':
    unittest.main()
    
