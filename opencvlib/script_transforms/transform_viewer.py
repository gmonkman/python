# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''test effects with sliders

'''
import sys
import os.path as path

import cv2
import numpy as np

import opencvlib.display_utils as display_utils
import opencvlib.transforms as t

try:
    img_path = path.normpath(sys.argv[1])
except Exception:
    img_path = r'..\test\bin\images\lena.jpg'

orig_image = cv2.imread(img_path)


Keys = display_utils.KeyBoardInput()
functions = {'escape':'exit'}




def nothing(x):
    '''dummy callback'''
    pass


cv2.namedWindow('original')


cv2.namedWindow('ctrls')
cv2.createTrackbar('gkernel', 'ctrls', 5, 100, nothing)
cv2.createTrackbar('sigma', 'ctrls', 10, 50, nothing)
cv2.createTrackbar('thresh', 'ctrls', 0, 100, nothing)
cv2.createTrackbar('weight', 'ctrls', 20, 100, nothing)
dummy_img = np.zeros((1, 300, 3), np.uint8)
cv2.imshow('ctrls', dummy_img)

getval = lambda tb_val, min, max: tb_val*(max - min)*0.01 + min #given the state of the slider, get the value variable

while True:
    gauss_kernel_size = (cv2.getTrackbarPos('kernel', 'ctrls'), cv2.getTrackbarPos('gauss_kernel_size', 'ctrls'))
    gauss_sigma = cv2.getTrackbarPos('sigma', 'ctrls')
    threshhold = getval(cv2.getTrackbarPos('thresh', 'ctrls'),0 ,1)
    weight = getval(cv2.getTrackbarPos('weight', 'ctrls'), 0, 10)

    img = t.sharpen_unsharpmask(orig_image, gauss_kernel_size, threshhold, weight, gauss_sigma)

    cv2.imshow('image', img)
    cv2.imshow('original', orig_image)
    key = Keys.get_pressed_key(cv2.waitKey(1))
    if functions.get(key, '') == 'exit':
        break


cv2.destroyAllWindows()



def write_text(i):
    '''(ndarray)->ndarray
    write status text to image
    '''
    return cv2.putText(i, 'weight: {!s}'.format(getval(cv2.getTrackbarPos('weight', 'image'), 0, 10)), (5, 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, bottomLeftOrigin=True)
