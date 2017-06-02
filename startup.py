# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
import math

import importlib.util as _util
from importlib import reload

from cv2 import imread
import cv2
import numpy as np

from matplotlib import pyplot

from skimage import exposure
from skimage.io import imshow as skimshow
from skimage.io import imread as skimread
from scipy import signal

from opencvlib import show, mosaic, CVColors, showarray
from opencvlib.transforms import to8bpp
from opencvlib.keypoints import printkp


testimg = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/pollock/angler/1238342_855950924420862_2220743491253041339_n.jpg'
I = cv2.imread(testimg, -1)
Ibw = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY,0) #blackwhite version
Isk = skimread(testimg)

PATCH = np.array([[0,0,0,0,0],[0,255,255,255,0],[0,255,255,255,0],[0,255,255,255,0],[0,0,0,0,0]])
PATCH = PATCH.astype('uint8')

MG = np.meshgrid(list(range(0,250,10)),list(range(0,250,10)))
Gradient = np.stack([MG[0],MG[0],MG[0]],2).astype('uint8') #3channel greyscale
Gradient = Gradient[:,:,0] #ok back to 1channel

hogx_kern = np.array([[0,0,0],[-1,0,1],[0,0,0]])
hogy_kern = np.array([[0,-1,0],[0,0,0],[0,1,0]])
Gx = abs(signal.convolve2d(Gradient, hogx_kern, mode='valid'))
Gy = abs(signal.convolve2d(Gradient, hogy_kern,mode='valid'))
Theta = np.arctan(Gy/Gx) #Gradient direction
g = np.sqrt(Gx**2 + Gy**2) #gradient magnitude


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