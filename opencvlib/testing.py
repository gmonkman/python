#pylint: skip-file

import sys
import cv2
import opencvlib.digikamlib as digikamlib
import opencvlib.vgg as vgg
import opencvlib.common as common

def test_imagesbytags():
    image_paths = digikamlib.ImagePaths('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
    lst = image_paths.ImagesByTags(filename='10150756_851703354845619_1559938228217274444_n.jpg', album_label='images', relative_path='bass/angler', species='bass')
    print(str(len(lst)))
    pass

def test_vgg():
    vgg.load_json('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json')
    img = vgg.Image('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/10150756_851703354845619_1559938228217274444_n.jpg')
    assert isinstance(img, vgg.Image)
    for subject in img.subjects_generator('bass'):
        assert isinstance(subject, vgg._Subject)
        for region in subject.regions_generator():
            assert isinstance(region, vgg._Region)
            print(region.species, region.part, region.shape)

def test_roi():
    image_paths = digikamlib.ImagePaths('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db')
    img_path = image_paths.ImagesByTags(filename='10150756_851703354845619_1559938228217274444_n.jpg', album_label='images', relative_path='bass/angler', species='bass')[0]
    vgg.load_json('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json', False)
    img = vgg.Image(img_path)
    for subject in img.subjects_generator('bass'):
        assert isinstance(subject, vgg._Subject)
        for region in subject.regions_generator('whole'):
            assert isinstance(region, vgg._Region)
            mask = common.roi_polygons_get(img_path, region.all_points)
            cv2.imshow('preview', mask)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

def main():
    test_roi()
    #test_imagesbytags()
    #test_vgg()

if __name__ == "__main__":
    main()
    sys.exit(int(main() or 0))
