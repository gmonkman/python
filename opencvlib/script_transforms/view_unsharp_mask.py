# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''test effects with sliders
'''
import sys
import os.path as path

import cv2
import numpy as np

import opencvlib.display_utils as display_utils
import opencvlib.transforms as t
import funclib.iolib as iolib
from opencvlib.common import draw_str

try:
    img_path = path.normpath(sys.argv[1])
except Exception:
    img_path = r'..\test\bin\images\lena.jpg'

print('\n**Press Escape to Quit**\n')

orig_image = cv2.imread(img_path)
Keys = display_utils.KeyBoardInput()
functions = {'escape':'exit'}
tb_ticks = 100 #tool bars have 100 ticks set in createTrackbar and used in set_params, which calls the getval lambda below
getval = lambda tb_val, min, max, tb_max: tb_val*(max - min)*(1/tb_max) + min #given the state of the slider, get the value variable

cv2.namedWindow('original')
cv2.namedWindow('ctrls', cv2.WINDOW_NORMAL)
cv2.createTrackbar('gkernel', 'ctrls', 5, tb_ticks, lambda x: x)
cv2.createTrackbar('sigma', 'ctrls', 10, tb_ticks, lambda x: x)
cv2.createTrackbar('thresh', 'ctrls', 0, tb_ticks, lambda x: x)
cv2.createTrackbar('weight', 'ctrls', 20, tb_ticks, lambda x: x)
dummy_img = np.zeros((2, 300), np.uint8)
cv2.imshow('ctrls', dummy_img)

GAUSS_KERNEL_SIZE = None
GAUSS_SIGMA = None
THRESHHOLD = None
WEIGHT = None


def set_params():
    '''set params'''
    sz = getval(cv2.getTrackbarPos('gkernel', 'ctrls'), 1, 100, tb_ticks)
    sz = 1 if int(sz) < 1 else int(sz)
    #kernel size must be odd
    if sz%2 == 0:
        sz += 1
    global GAUSS_KERNEL_SIZE
    GAUSS_KERNEL_SIZE = (sz, sz)
    global GAUSS_SIGMA
    GAUSS_SIGMA = getval(cv2.getTrackbarPos('sigma', 'ctrls'), 0.01, 50, tb_ticks)
    global THRESHHOLD
    THRESHHOLD = getval(cv2.getTrackbarPos('thresh', 'ctrls'), 0, 1, tb_ticks)
    global WEIGHT
    WEIGHT = getval(cv2.getTrackbarPos('weight', 'ctrls'), 0, 10, tb_ticks)

set_params()


def write_text(image):
    '''(byref:ndarray)->ndarray
    write status text to image
    '''
    thresh_as_uint8 = int(255*THRESHHOLD)
    s = []
    s.append('kern: {!s}'.format(GAUSS_KERNEL_SIZE))
    s.append('sigma: {0:.1f}'.format(GAUSS_SIGMA))
    s.append('thresh: {0:.2f} [uint:{1:d}]'.format(THRESHHOLD, thresh_as_uint8))
    s.append('weight: {0:.2f}'.format(WEIGHT))
    txt = ' '.join(s)
    draw_str(image, 4, 4, txt, color=(0, 0, 0), scale=0.5, box_background=255, box_pad=2)


cv2.imshow('original', orig_image)

while True:
    img = np.copy(orig_image)
    if GAUSS_KERNEL_SIZE[0] >= 1 and GAUSS_SIGMA > 0 and THRESHHOLD >= 0 and WEIGHT >= 0:
        set_params()
        with iolib.quite(stdout=True, stderr=True):
            img = t.sharpen_unsharpmask(orig_image, GAUSS_KERNEL_SIZE, THRESHHOLD, WEIGHT, GAUSS_SIGMA)

    write_text(img)
    cv2.imshow('image', img)
    key = Keys.get_pressed_key(cv2.waitKey(1))
    if functions.get(key, '') == 'exit':
        break


cv2.destroyAllWindows()
