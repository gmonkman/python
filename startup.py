# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
import math

import importlib.util as _util
from importlib import reload

from cv2 import imread
import cv2
import numpy as np

#from matplotlib import pyplot

#from skimage import exposure
#from skimage.io import imshow as skimshow
#from skimage.io import imread as skimread
#from scipy import signal

#import tensorflow as tf
#from tensorflow.contrib import eager as tfe
#tfe.enable_eager_execution()

from opencvlib.view import show, mosaic, showarray
from opencvlib.color import CVColors
from opencvlib.transforms import to8bpp
from opencvlib.keypoints import printkp

from plotlib.qplot import histo, scatter
from funclib.arraylib import shape

testimg = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/pollock/angler/1238342_855950924420862_2220743491253041339_n.jpg'
#testimg = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/bass/mbiusmchfu_r358_UND.jpg'
testmovie = 'C:/development/python/opencvlib/test/bin/movie/test-mpeg_512kb.mp4'


I = cv2.imread(testimg, -1)
Ibw = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY,0) #blackwhite version
#Isk = skimread(testimg)
Ihsv = cv2.cvtColor(I, cv2.COLOR_BGR2HSV)

PATCH = np.array([[0,0,0,0,0],[0,255,255,255,0],[0,255,255,255,0],[0,255,255,255,0],[0,0,0,0,0]])
PATCH = PATCH.astype('uint8')

MG = np.meshgrid(list(range(0,250,10)),list(range(0,250,10)))
Gradient = np.stack([MG[0],MG[0],MG[0]],2).astype('uint8') #3channel greyscale
Gradient = Gradient[:,:,0] #ok back to 1channel


#region HOG bits
#hogx_kern = np.array([[0,0,0],[-1,0,1],[0,0,0]])
#hogy_kern = np.array([[0,-1,0],[0,0,0],[0,1,0]])
#Gx = abs(signal.convolve2d(Gradient, hogx_kern, mode='valid'))
#Gy = abs(signal.convolve2d(Gradient, hogy_kern,mode='valid'))
#Theta = np.arctan(Gy/Gx) #Gradient direction
#g = np.sqrt(Gx**2 + Gy**2) #gradient magnitude
#endregion


BLUE_PATCH = np.zeros((100,100,3)).astype('uint8')
BLUE_PATCH[:,:,0:1] = 255
BLUE_PATCH_HSV = cv2.cvtColor(BLUE_PATCH, cv2.COLOR_BGR2HSV)

RED_PATCH = np.zeros((100,100,3)).astype('uint8')
RED_PATCH[:,:,2:3] = 255
RED_PATCH_HSV = cv2.cvtColor(RED_PATCH, cv2.COLOR_BGR2HSV)

GREEN_PATCH = np.zeros((100,100,3)).astype('uint8')
GREEN_PATCH[:,:,1:2] = 255
GREEN_PATCH_HSV = cv2.cvtColor(GREEN_PATCH, cv2.COLOR_BGR2HSV)

YELLOW_PATCH = np.zeros((100,100,3)).astype('uint8')
YELLOW_PATCH[:,:,1:2] = 255
YELLOW_PATCH[:,:,2:3] = 255
YELLOW_PATCH_HSV = cv2.cvtColor(YELLOW_PATCH, cv2.COLOR_BGR2HSV)

BLACK_PATCH = np.zeros((100,100,3)).astype('uint8')
BLACK_PATCH_HSV = cv2.cvtColor(BLACK_PATCH, cv2.COLOR_BGR2HSV)

WHITE_PATCH = np.ones((100,100,3))*255
WHITE_PATCH = WHITE_PATCH.astype('uint8')
WHITE_PATCH_HSV = cv2.cvtColor(WHITE_PATCH, cv2.COLOR_BGR2HSV)

MOSAIC = np.vstack([np.hstack([BLUE_PATCH, RED_PATCH]), np.hstack([GREEN_PATCH, YELLOW_PATCH]),  np.hstack([BLACK_PATCH, WHITE_PATCH])])
MOSAIC_HSV = cv2.cvtColor(MOSAIC, cv2.COLOR_BGR2HSV)

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


#def skshow(img):
 #   skimshow(img)
  #  pyplot.show()