# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''test effects with sliders
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
cv2.createTrackbar('gamma', 'ctrls', int(getval(1, 0, 100, 5)), tb_ticks, lambda x: x) #getval(1, 0, 100, 5),  ie set the gamma to 1 - no change
cv2.createTrackbar('brightness', 'ctrls', int(tb_ticks/2), tb_ticks, lambda x: x)
cv2.createTrackbar('intensity', 'ctrls', int(tb_ticks/2), tb_ticks, lambda x: x)
dummy_img = np.zeros((2, 300), np.uint8)
cv2.imshow('ctrls', dummy_img)

gamma = None
brightness = None
intensity = None


def set_params():
    '''set params'''
    global gamma
    gamma = getval(cv2.getTrackbarPos('gamma', 'ctrls'), 0.0001, 5, tb_ticks) #proportion of image size
    global brightness
    brightness = getval(cv2.getTrackbarPos('brightness', 'ctrls'), -50, 50, tb_ticks)
    global intensity
    intensity = getval(cv2.getTrackbarPos('intensity', 'ctrls'), -1, 1, tb_ticks)


set_params()


def write_text(image):
    '''(byref:ndarray)->ndarray
    write status text to image
    '''
    s = []
    s.append('gamma: {0:.1f}'.format(gamma))
    s.append('brightness: {0:.1f}'.format(brightness))
    s.append('intensity: {0:.1f}'.format(intensity))
    txt = ' '.join(s)
    draw_str(image, 4, 4, txt, color=(0, 0, 0), scale=0.5, box_background=255, box_pad=2)


cv2.imshow('original', orig_image)

while True:
    img = np.copy(orig_image)
    set_params()
    with iolib.quite(stdout=True, stderr=True):
        img = t.gamma(img, gamma_=gamma)
        img = t.brightness(img, value=brightness)
        img = t.intensity_wrapper(img, intensity_=intensity)
    write_text(img)
    cv2.imshow('image', img)
    key = Keys.get_pressed_key(cv2.waitKey(1))
    if functions.get(key, '') == 'exit':
        break


cv2.destroyAllWindows()
