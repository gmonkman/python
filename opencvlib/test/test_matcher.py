# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable, unused-import, undefined-loop-variable

'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2
import numpy as np


import funclib.iolib as iolib
import funclib.baselib as baselib

import opencvlib.imgpipes.generators as Gen
import opencvlib.features as features
import opencvlib.matcher as matcher
import opencvlib.view as view
import opencvlib.transforms as _transforms
from opencvlib import getimg

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
           


    @unittest.skip("Temporaily disabled while debugging")
    def test_with_vggdigi_generator(self):
        '''test with vgg generator'''
        print('Testing head against random heads')
        features.OpenCV_SIFT.kwargs = {'nfeatures':100, 'nOctaveLayers':3, 'contrastThreshold':0.05, 'edgeThreshold':10, 'sigma':1.0}
        first_feat = features.OpenCV_SIFT()

        vgg_param = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['head'], species=['bass'])
        dk_param = Gen.DigikamSearchParams(search_type=Gen.eDigiKamSearchType.innerOr_outerAnd, roll='0', pitch='0', yaw=['0', '180'])

        VGG = Gen.VGGRegions(dk_param, vgg_param)

        #get first image as ref
        for img, imgpath, dummy in VGG.generate():
            ref_img = img
            break
        
        first_feat(ref_img, imgpath, extract_now=True)

        matcher.BruteForceMatcher.filter_match_ratio = 0.9

        for img, imgpath, dummy in VGG.generate():
            test_feat = features.OpenCV_SIFT()
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


    @unittest.skip("Temporaily disabled while debugging")
    def test_head_body(self):
        '''test with vgg generator'''
        print('Testing Idealised Head-Body Matching')
        #features.OpenCV_SIFT.kwargs = {'nfeatures':500, 'nOctaveLayers':3, 'contrastThreshold':0.05, 'edgeThreshold':10, 'sigma':1.0}
        first_feat = features.OpenCV_SIFT()
        test_feat = features.OpenCV_SIFT()
        matcher.BruteForceMatcher.filter_match_ratio = 0.75
        M = matcher.BruteForceMatcher(first_feat, test_feat)

        vgg_param_part = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['head'], species=['bass'])
        VGG_part = Gen.VGGRegions(None, vgg_param_part)

        for img_part, imgpath, dummy in VGG_part.generate():
            img_whole = getimg(imgpath)
            if not isinstance(img_part, np.ndarray) or not isinstance(img_whole, np.ndarray):
                continue

            first_feat(img_part, imgpath, extract_now=True)
            test_feat(img_whole, imgpath, extract_now=True)
            try:
                M(first_feat, test_feat)
                resI = M.get_match_viz()
                view.show(resI)
            except Exception as _:
                print('Match failed for %s, probably because source or target descriptors were empty.' % test_feat._imgname)


    @unittest.skip("Temporaily disabled while debugging")
    def test_caudal_body(self):
        '''test with vgg generator'''
        print('Testing Idealised Tail-Body Matching')
        features.OpenCV_SIFT.kwargs = {'nfeatures':10000, 'nOctaveLayers':3, 'contrastThreshold':0.05, 'edgeThreshold':10, 'sigma':1.0}
        first_feat = features.OpenCV_SIFT()
        test_feat = features.OpenCV_SIFT()
        matcher.BruteForceMatcher.filter_match_ratio = 0.75
        M = matcher.BruteForceMatcher(first_feat, test_feat)

        vgg_param_part = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['caudal fin'], species=['bass'])
        VGG_part = Gen.VGGRegions(None, vgg_param_part)

        for img_part, imgpath, dummy in VGG_part.generate():
            img_whole = getimg(imgpath)
            if not isinstance(img_part, np.ndarray) or not isinstance(img_whole, np.ndarray):
                continue

            first_feat(img_part, imgpath, extract_now=True)
            test_feat(img_whole, imgpath, extract_now=True)
            
            M(first_feat, test_feat)
            resI = M.get_match_viz()
            view.show(resI) 

    @unittest.skip("Temporaily disabled while debugging")
    def test_opencv_example(self):
        '''matching using idealised opencv images'''
        print('Testing opencv box detection example')
        pth1 = 'C:/Users/Graham Monkman/Downloads/opencv-3.2.0-vc14/opencv/sources/samples/data/box.png'
        pth2 = 'C:/Users/Graham Monkman/Downloads/opencv-3.2.0-vc14/opencv/sources/samples/data/box_in_scene.png'
        img1 = cv2.imread(pth1)
        img2 = cv2.imread(pth2)
        print('Testing opencv object detector using box.png and box_in_scene.png')
        features.OpenCV_SIFT.kwargs = {'nfeatures':500, 'nOctaveLayers':3, 'contrastThreshold':0.05, 'edgeThreshold':10, 'sigma':1.0}
        first_feat = features.OpenCV_SIFT()
        test_feat = features.OpenCV_SIFT()
        matcher.BruteForceMatcher.filter_match_ratio = 0.75
        M = matcher.BruteForceMatcher(first_feat, test_feat)

        first_feat(img1, pth1, extract_now=True)
        test_feat(img2, pth2, extract_now=True)
        print('img1 - %d features, img2 - %d features' % (len(first_feat.keypoints), len(test_feat.keypoints)))
         
        M(first_feat, test_feat)
        resI = M.get_match_viz()
        view.show(resI) 

    @unittest.skip("Temporaily disabled while debugging")
    def test_fin_generic(self):
        '''this takes a fin and attempts to match against other images'''
        print('Testing general fins')

        features.OpenCV_SIFT.kwargs = {'nfeatures':20000, 'nOctaveLayers':3, 'contrastThreshold':0.04, 'edgeThreshold':10, 'sigma':1.0}
        train_feat = features.OpenCV_SIFT()
        test_feat = features.OpenCV_SIFT()
        matcher.BruteForceMatcher.filter_match_ratio = 0.9
        M = matcher.BruteForceMatcher(train_feat, test_feat)


        #Load a single fin as the train img
        train_img_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/14292366_1279024908815039_4406607645719848778_n.jpg'

        dk_param_part = Gen.DigikamSearchParams('14292366_1279024908815039_4406607645719848778_n.jpg', 'images', '/bass/angler')
        vgg_param_part = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['caudal fin'], species=['bass'])
        VGG_part = Gen.VGGRegions(dk_param_part, vgg_param_part)

        for img_train, imgpath, dummy in VGG_part.generate():
            pass

        train_feat(img_train, imgpath, extract_now=True)



        #loop over all whole fish
        vgg_param_part = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['whole'], species=['bass'])
        #VGG_part = Gen.VGGRegions(None, vgg_param_part)
        VGG_part = Gen.VGGRegions(dk_param_part, vgg_param_part)

        for img_part, imgpath, dummy in VGG_part.generate():
            img_whole = getimg(imgpath)
            if not isinstance(img_part, np.ndarray) or not isinstance(img_whole, np.ndarray):
                continue
          
            test_feat(img_whole, imgpath, extract_now=True)
            
            M(train_feat, test_feat)
            resI = M.get_match_viz()
            view.show(resI) 

    #@unittest.skip("Temporaily disabled while debugging")
    def test_whole_generic(self):
        '''this takes a whole fish and attempts to match against other images'''
        print('Testing general whole')

        features.OpenCV_SIFT.kwargs = {'nfeatures':10000, 'nOctaveLayers':3, 'contrastThreshold':0.04, 'edgeThreshold':10, 'sigma':1}
        train_feat = features.OpenCV_SIFT()
        test_feat = features.OpenCV_SIFT()
        matcher.BruteForceMatcher.filter_match_ratio = 0.8
        M = matcher.BruteForceMatcher(train_feat, test_feat)

        #Load a single fin as the train img
        dk_param_part = Gen.DigikamSearchParams('DSCF8225.JPG', 'images', '/bass/angler')
        vgg_param_part = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['whole'], species=['bass'])

        t1 = _transforms.Transform(_transforms.histeq_adapt)
        T = _transforms.Transforms(None, t1)
        VGG_part = Gen.VGGRegions(dk_param_part, vgg_param_part, transforms=T)

        for img_train, imgpath, dummy in VGG_part.generate():
            if not img_train is None: #we're only getting a single image
                continue
        img_train = _transforms.resize(img_train, width=200)
        train_feat(img_train, imgpath, extract_now=True)

        #loop over all whole fish
        vgg_param_part = Gen.VGGSearchParams(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json'], parts=['whole'], species=['bass'])
        VGG_part = Gen.VGGRegions(None, vgg_param_part, transforms=T)

        for img_part, imgpath, dummy in VGG_part.generate():
            img_whole = getimg(imgpath)
            img_whole = _transforms.resize(img_whole, width=200)
            if not isinstance(img_part, np.ndarray) or not isinstance(img_whole, np.ndarray):
                continue


            try:
                test_feat(img_whole, imgpath, extract_now=True)
                M(train_feat, test_feat)
                resI = M.get_match_viz()
                view.show(resI, waitsecs=0)
            except cv2.error as e:
                print('\nMatching failed, most likely error is caused by memory overflow with large images. Error was ' + str(e))
            finally:
                pass
    



if __name__ == '__main__':
    unittest.main(verbosity=2)
    
