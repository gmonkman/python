# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''test effects with sliders

def equalize_adapthist(img, kernel_size=None, clip_limit=0.01, nbins=256):
    (ndarray|str, int|listlike, float, int) -> BGR-ndarray
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Supports color.

    kernel_size: integer or list-like, optional
        Defines the shape of contextual regions used in the algorithm.
        If iterable is passed, it must have the same number
        of elements as image.ndim (without color channel).
        If integer, it is broadcasted to each image dimension.
        By default, kernel_size is 1/8 of image height by 1/8 of its width.
    clip_limit : float, optional
        Clipping limit, normalized between 0 and 1 (higher values give more contrast).

    nbins : int, optional
        Number of gray bins for histogram (“data range”).

'''
from inspect import getsourcefile
import sys
import os.path as path

import cv2
import numpy as np

import opencvlib.display_utils as display_utils
import opencvlib.transforms as t
import funclib.iolib as iolib
from opencvlib.common import draw_str

THIS_FILE_PATH = path.normpath(iolib.get_file_parts2(path.abspath(getsourcefile(lambda: 0)))[0]) #root of the executing py (ie this)

try:
    img_path = path.normpath(sys.argv[1])
except Exception:
    img_path = path.normpath(path.join(THIS_FILE_PATH, 'img/lena.jpg'))

print('\n**Press Escape to Quit**\n')


orig_image = cv2.imread(img_path)
Keys = display_utils.KeyBoardInput()
functions = {'escape':'exit'}
tb_ticks = 100 #tool bars have 100 ticks set in createTrackbar and used in set_params, which calls the getval lambda below
getval = lambda tb_val, min, max, tb_max: tb_val*(max - min)*(1/tb_max) + min #given the state of the slider, get the value variable

cv2.namedWindow('original')
cv2.namedWindow('ctrls', cv2.WINDOW_NORMAL)
cv2.createTrackbar('kernel', 'ctrls', 10, tb_ticks, lambda x: x)
cv2.createTrackbar('clip', 'ctrls', 10, tb_ticks, lambda x: x)
cv2.createTrackbar('nbins', 'ctrls', 50, tb_ticks, lambda x: x)
dummy_img = np.zeros((2, 300), np.uint8)
cv2.imshow('ctrls', dummy_img)

KERNEL_SIZE = None
CLIP = None
NBINS = None


def set_params():
    '''set params'''
    global KERNEL_SIZE
    KERNEL_SIZE = getval(cv2.getTrackbarPos('kernel', 'ctrls'), 3, 50, tb_ticks) #proportion of image size
    global CLIP
    CLIP = getval(cv2.getTrackbarPos('clip', 'ctrls'), 0, 1, tb_ticks)
    global NBINS
    NBINS = int(getval(cv2.getTrackbarPos('nbins', 'ctrls'), 2, 512, tb_ticks))


set_params()


def write_text(image):
    '''(byref:ndarray)->ndarray
    write status text to image
    '''
    s = []
    s.append('kern: {!s}'.format(KERNEL_SIZE))
    s.append('clip: {0:.3f}'.format(CLIP))
    s.append('bins: {!s}'.format(NBINS))
    txt = ' '.join(s)
    draw_str(image, 4, 4, txt, color=(0, 0, 0), scale=0.5, box_background=255, box_pad=2)


cv2.imshow('original', orig_image)

while True:
    img = np.copy(orig_image)
    if KERNEL_SIZE > 0 and CLIP > 0 and NBINS > 0:
        set_params()
        with iolib.quite(stdout=True, stderr=True):
            img = t.equalize_adapthist(orig_image, kernel_size=KERNEL_SIZE, clip_limit=CLIP, nbins=NBINS)

    write_text(img)
    cv2.imshow('image', img)
    key = Keys.get_pressed_key(cv2.waitKey(1))
    if functions.get(key, '') == 'exit':
        break


cv2.destroyAllWindows()
