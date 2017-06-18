# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2

import funclib.iolib as iolib
import opencvlib.imgpipes.generators as Gen
import opencvlib.features as features
import opencvlib.matcher as matcher
import opencvlib.view as view
import opencvlib.transforms as _transforms


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        
        
        self.box_path = _path.normpath(_path.join(self.modpath, 'bin/images/box.png'))
        self.box_fld, dummy1, dummy2 = iolib.get_file_parts2(self.box_path)

        self.boxinscene_path = _path.normpath(_path.join(self.modpath, 'bin/images/box_in_scene.png'))
        self.boxinscene_fld, dummy1, dummy2 = iolib.get_file_parts2(self.boxinscene_path)
           


    #@unittest.skip("Temporaily disabled while debugging")
    def test_with_vggdigi_generator(self):
        '''test with vgg generator'''
        first_feat = features.OpenCV_ORB()

        vgg_param = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['head'], species=['bass'])
        dk_param = Gen.DigikamSearchParams(search_type=Gen.eDigiKamSearchType.innerOr_outerAnd, roll='0', pitch='0', yaw=['0', '180'])

        VGG = Gen.VGGRegions(dk_param, vgg_param)

        Ts = _transforms.Transforms()
        T = _transforms.Transform(cv2.medianBlur,ksize=5)

        #get first image as ref
        for img, imgpath, dummy in VGG.generate():
            ref_img = img
            break
        
        first_feat(ref_img, imgpath, extract_now=True)

        matcher.BruteForceMatcher.filter_match_ratio = 0.9

        for img, imgpath, dummy in VGG.generate():
            test_feat = features.OpenCV_ORB()
            test_feat(img, imgpath, extract_now=True)

            M = matcher.BruteForceMatcher(first_feat, test_feat)
            resI = M.get_match_viz()
            view.show(resI)           


    @unittest.skip("Temporaily disabled while debugging")
    def test_Base(self):
        '''test'''
        firstSIFT = features.OpenCV_SIFT()      
        firstSIFT(self.box_path, self.box_fld, extract_now=True)

        curSIFT = features.OpenCV_SIFT()
        curSIFT(self.boxinscene_path, self.boxinscene_fld, extract_now=True)

        M = matcher.BruteForceMatcher(firstSIFT, curSIFT)
        resI = M.get_match_viz()
        view.show(resI)            


if __name__ == '__main__':
    unittest.main(verbosity=2)
    
