# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument, dangerous-default-value
'''simple image file generators'''
import cv2

from funclib.iolib import file_list_generator1


__all__ = ['image_generator', 'IMAGE_EXTENSIONS',
           'IMAGE_EXTENSIONS_AS_WILDCARDS']


# region module consts and variables
IMAGE_EXTENSIONS = ('.bmp',
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.tif',
                    '.tiff',
                    '.pbm',
                    '.pgm',
                    '.ppm')

IMAGE_EXTENSIONS_AS_WILDCARDS = ('*.bmp',
                                 '*.jpg',
                                 '*.jpeg',
                                 '*.png',
                                 '*.tif',
                                 '*.tiff',
                                 '*.pbm',
                                 '*.pgm',
                                 '*.ppm')


def image_generator(paths, wildcards=IMAGE_EXTENSIONS_AS_WILDCARDS, flags=-1):
    '''(iterable, iterable)->ndarray (an image)
    Globs through every file in paths matching wildcards returning
    the image as an ndarray

    paths: List of paths
    wildcards: List of wildcards. eg ['*.bmp', '*.gif']

    Flags:
    <0 - Loads as is, with alpha channel if present)
    0 - Force grayscale
    >0 - 3 channel color iage (stripping alpha if present
    http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html#Mat%20imread(const%20String&%20filename,%20int%20flags)
    '''

    for images in file_list_generator1(paths, wildcards):
        if flags is None:
            yield cv2.imread(images)
        else:
            yield cv2.imread(images, flags)
