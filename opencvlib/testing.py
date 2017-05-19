# pylint: skip-file
from functools import wraps  # decorator for decorator funcs

import sys
import cv2
from numpy import ndarray
import numpy as np

import opencvlib.imgpipes.digikamlib as digikamlib
import opencvlib.imgpipes.vgg as vgg
import opencvlib.common as common
import opencvlib
from opencvlib.decs import decgetimg
from opencvlib import show
from opencvlib import ImageInfo
import opencvlib.transforms as transforms
from opencvlib.imgpipes import filters

import opencvlib.imgpipes.generators as gnr

from funclib.iolib import get_file_parts2
from funclib.iolib import write_to_file

def test_vgg_fix():
    vgg.load_json(
        'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/test_write.json')
    vgg.write_region_attributes('bass')


def test_imagesbytags():
    image_paths = digikamlib.ImagePaths(
        'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
    lst = image_paths.images_by_tags(
        filename='10150756_851703354845619_1559938228217274444_n.jpg',
        album_label='images',
        relative_path='bass/angler',
        species='bass')
    print(str(len(lst)))
    pass


def test_vgg():
    vgg.load_json(
        'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json')
    img = vgg.Image(
        'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/10150756_851703354845619_1559938228217274444_n.jpg')
    assert isinstance(img, vgg.Image)
    for subject in img.subjects_generator('bass'):
        assert isinstance(subject, vgg.Subject)
        for region in subject.regions_generator():
            assert isinstance(region, vgg.Region)
            print(region.species, region.part, region.shape)


def test_roi():
    image_paths = digikamlib.ImagePaths(
        'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
    img_path = image_paths.images_by_tags(
        filename='10150756_851703354845619_1559938228217274444_n.jpg',
        album_label='images',
        relative_path='bass/angler',
        species='bass')[0]
    vgg.load_json(
        'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json',
        False)
    vgg_img = vgg.Image(img_path)
    for subject in vgg_img.subjects_generator('bass'):
        assert isinstance(subject, vgg.Subject)
        for region in subject.regions_generator('whole'):
            assert isinstance(region, vgg.Region)
            white, ma, cropped_image = common.roi_polygons_get(
                img_path, region.all_points)
            cv2.imshow('preview', white)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

@decgetimg
def test_decgetimg(img):
    print(type(img))
    show(img)
    pass


def test_padimg():
    imlist = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/scraped/1d/1d2ada5bf427c8e02ec0368ae9ad159781447574.jpg', 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/scraped/1d/1d2b0381c6046005ce24d8b3de75d8a07844b882.jpg', 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/scraped/1d/1d2d6745aa0a0bb2292d9ab59b49bb5708a29b31.jpg', 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/scraped/1d/1d4aa79954da8c09cb60431e8b5dd1300bb2bc8a.jpg']
    #I = processing.pad_images(imlist)
    out = processing.mosaic(imlist,2)
    show(out)


#DEBUG Double check test_image_pipeline
def test_image_pipeline():
    #Get training region
    vgg_sp = gnr.VGGSearchParams('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler', 'whole','bass')
    dk_sp = gnr.DigikamSearchParams(key_value_bool_type='OR', is_train=['head','whole'])
    dk_sample = gnr.DigikamSearchParams(key_value_bool_type='OR', species=['bullhuss','dab','flatfish','cod','plaice','dogfish','mini species','smoothhound','tope','whiting','pollock'])

    t1 = transforms.Transform(transforms.togreyscale)
    t2 = transforms.Transform(transforms.equalize_adapthist)
    T = transforms.Transforms(None, t1, t2)

    f1 = filters.Filter(filters.is_higher_res, w=100, h=100)
    f2 = filters.Filter(filters.is_lower_res, w=10000, h=10000)
    F = filters.Filters(None, f1, f2)

    Gen = gnr.RegionPosRandomNeg(vgg_sp, dk_sp, dk_sample, F=F, T=None)
    for train, test, dummy in Gen.generate():
        show([train, test])


def main():
    # test_roi()
    # test_imagesbytags()
    # test_vgg()
    #test_vgg_fix()
    #test_decgetimg('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/smoothhound/angler/DSCF0907.JPG')
    #test_padimg()
    test_image_pipeline()


if __name__ == "__main__":
    main()
    sys.exit(int(main() or 0))
