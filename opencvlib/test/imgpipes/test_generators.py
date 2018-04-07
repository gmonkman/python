# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''unit tests for imgpipes.generators'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path


import numpy as np

from opencvlib.view import show
import opencvlib.imgpipes.generators as gnr
import opencvlib.transforms as transforms
from opencvlib.imgpipes import filters
import opencvlib.roi as roi
import funclib.iolib as iolib
import opencvlib.common as common
import opencvlib

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(opencvlib.__path__[0]) #root of opencvlib
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))

    #DEBUG Double check test_image_pipeline
    @unittest.skip("Temporaily disabled while debugging")
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
        dk_sp = gnr.DigikamSearchParams(search_type=gnr.eDigiKamSearchType.innerOr_outerAnd, pitch='0', yaw='180', roll='0')

        #t1 = transforms.Transform(transforms.togreyscale)
        #t2 = transforms.Transform(transforms.equalize_adapthist)
        #T = transforms.Transforms(None, t1, t2)

        #f1 = filters.Filter(filters.is_higher_res, w=100, h=100)
        #f2 = filters.Filter(filters.is_lower_res, w=10000, h=10000)
        #F = filters.Filters(None, f1, f2)

        Gen = gnr.VGGDigiKam(dk_sp, vgg_sp, transforms=None, filters=None)
        for img, dummy, dummy1 in Gen.generate():
            show(img)


    @unittest.skip("Temporaily disabled while debugging")
    def test_frompaths(self):
        '''test frompaths image generator
        '''
        FP = gnr.FromPaths(self.test_images_path, ['*.jpg'])

        for img, imgpath, dic  in FP.generate():
            self.assertIsInstance(img, np.ndarray)
            self.assertIsInstance(imgpath, str)
            self.assertIsInstance(dic, dict)


    @unittest.skip("Temporaily disabled while debugging")
    def test_voc(self):
        '''test the pascal voc generator
        '''
        VOC = gnr.VOC('cat', 'train')
        for img, pth, regions in VOC.generate():
            assert isinstance(regions, dict)
            lbls = regions['categories']
            rects = regions['rects']

            for i, lbl in enumerate(lbls):
                pts = rects[i]
                img = common.draw_points(pts, img)
                common.draw_str(img, pts[0][0], pts[0][1], lbl, box_background=(0))
            show(img)


    @unittest.skip("Temporaily disabled while debugging")
    def test_VGGROI(self):
        '''test the VGG ROI generator, which generates
        generic regions of interest from the VGG file,
        with an option to filter by a partial dictionary
        match on a regions attributes (region_attributes in the json file)
        '''
        fp = _path.normpath(_path.join(self.test_images_path, 'vgg_regions.json'))
        VGGROI = gnr.VGGROI(fp)
        for img, pth, dic in VGGROI.generate():
            pass
            #show(img)

        attrs = {'shape': 'rect', 'id': '1'}
        VGGROI = gnr.VGGROI(fp, region_attrs=attrs)
        for img, pth, dic in VGGROI.generate():
            pass
            #show(img)

        for img, pth, dic in VGGROI.generate(grow_roi_proportion=2):
            show(img)

        for img, pth, dic in VGGROI.generate(grow_roi_proportion=0.5):
            show(img)


    #@unittest.skip("Temporaily disabled while debugging")
    def test_VGGImages(self):
        '''test the VGGImages generator, which is a
        simple generator for all images in a set of
        VGG file.
        '''
        fp = _path.normpath(_path.join(self.test_images_path, 'vgg_regions.json'))
        VGGImages = gnr.VGGImages(fp)
        for img, pth, dic in VGGImages.generate(file_attr_match={'is_train':'1'}):
            print(pth)
            self.assertIs(isinstance(img, np.ndarray) and isinstance(pth, str) and isinstance(dic, dict), True)


if __name__ == '__main__':
    unittest.main()
