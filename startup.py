# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
import importlib.util as _util
from importlib import reload

from cv2 import imread
import cv2
import numpy as np

from opencvlib import show, mosaic, to8bpp


from matplotlib import pyplot

from skimage import exposure
from skimage.io import imshow as skimshow
from skimage.io import imread as skimread


testimg = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/pollock/angler/1238342_855950924420862_2220743491253041339_n.jpg'
I = cv2.imread(testimg, -1)

#Doesnt really work
def ddir():
    d = [[name, type(name)] for name in globals() if not '__' in name]
    s = ''
    for d in d:
        print('%s [%s]' % (d[0], d[1]))


def pimport(script_path, modulename=''):
    '''(str,str)->module
    modulename = package.module, e.g. opencvlib.faces
    script_path: path to py
    '''
    spec = _util.spec_from_file_location(modulename, script_path)
    f = _util.module_from_spec(spec)
    spec.loader.exec_module(f)

    return f


def skshow(img):
    skimshow(img)
    pyplot.show()