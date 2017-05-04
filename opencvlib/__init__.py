# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument,wildcard-import

'''opencvlib'''
from opencvlib.common import getimg, show, checkwaitkey, getwaitkey
from opencvlib.common import ImageInfo, Info

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

__all__ = ['common', 'distance', 'edges', 'faces',
           'perspective', 'processing', 'roi', 'winpyr']
