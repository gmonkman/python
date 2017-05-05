# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''edge detection and skeletonization
'''
import cv2 as _cv2
import numpy as _np


def skeletonize(image, size, structuring=_cv2.MORPH_RECT):
    '''determine the area (i.e.  total number of pixels in the image),
    initialize the output skeletonized image, and construct the
    morphological structuring element
    '''
    area = image.shape[0] * image.shape[1]
    skeleton = _np.zeros(image.shape, dtype="uint8")
    elem = _cv2.getStructuringElement(structuring, size)

    # keep looping until the erosions remove all pixels from the
    # image
    while True:
        # erode and dilate the image using the structuring element
        eroded = _cv2.erode(image, elem)
        temp = _cv2.dilate(eroded, elem)

        # subtract the temporary image from the original, eroded
        # image, then take the bitwise 'or' between the skeleton
        # and the temporary image
        temp = _cv2.subtract(image, temp)
        skeleton = _cv2.bitwise_or(skeleton, temp)
        image = eroded.copy()

        # if there are no more 'white' pixels in the image, then
        # break from the loop
        if area == area - _cv2.countNonZero(image):
            break

    # return the skeletonized image
    return skeleton
