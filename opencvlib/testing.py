# pylint: skip-file
from functools import wraps  # decorator for decorator funcs

import sys
import cv2
from numpy import ndarray

import opencvlib.imgpipes.digikamlib as digikamlib
import opencvlib.imgpipes.vgg as vgg
import opencvlib.common as common
import opencvlib
from opencvlib.decs import decgetimg
from opencvlib import show
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

def test_image_pipeline():
    vgg_sp = gnr.VGGSearchParams('whole','bass')
    vgg_folders = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler']
    dk_sp = gnr.DigikamSearchParams(key_value_bool_type='OR', is_train=['head','whole'])
    #dk_sp = None
    pipe = gnr.Images(vgg_folders, dk_sp, vgg_sp)
    res = []
    for img, spp, part, img_path in pipe.generate_regions():
        i, title = show(img, title=get_file_parts2(img_path)[1], waitsecs=10)
        if opencvlib.checkwaitkey('n', i): #pressed n
            res.append([opencvlib.getwaitkey(i), title])
    if res: write_to_file(res)


def main():
    # test_roi()
    # test_imagesbytags()
    # test_vgg()
    #test_vgg_fix()
    #test_decgetimg('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/smoothhound/angler/DSCF0907.JPG')
    test_image_pipeline()

if __name__ == "__main__":
    main()
    sys.exit(int(main() or 0))
